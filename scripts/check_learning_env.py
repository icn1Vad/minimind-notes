"""Check tutorial dependencies, local tokenizer, and a MiniMind optimizer step."""

import argparse
import importlib
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-cuda', action='store_true')
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))

    import torch
    from transformers import AutoTokenizer
    from model.model_minimind import MiniMindConfig, MiniMindForCausalLM

    for name in ('numpy', 'matplotlib', 'seaborn', 'requests', 'datasets',
                 'transformers', 'tokenizers', 'peft', 'trl', 'ujson',
                 'dataset.lm_dataset', 'modules.common.visualization'):
        importlib.import_module(name)

    print(f'Python: {sys.executable}')
    print(f'PyTorch: {torch.__version__}; CUDA runtime: {torch.version.cuda}')
    if args.require_cuda and not torch.cuda.is_available():
        raise RuntimeError('CUDA is required but unavailable.')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if device.type == 'cuda':
        print(f'GPU: {torch.cuda.get_device_name(0)}')
        print(f'Compute capability: {torch.cuda.get_device_capability(0)}')

    torch.manual_seed(42)
    tokenizer = AutoTokenizer.from_pretrained(
        str(project_root / 'model'), local_files_only=True
    )
    config = MiniMindConfig(
        hidden_size=64, num_hidden_layers=1, num_attention_heads=4,
        num_key_value_heads=2, max_position_embeddings=64,
        vocab_size=len(tokenizer), flash_attn=False,
    )
    model = MiniMindForCausalLM(config).to(device)
    model.train()
    batch = tokenizer('MiniMind learning environment check.', return_tensors='pt')
    input_ids = batch.input_ids[:, :32].to(device)
    targets = input_ids[:, 1:]
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    outputs = model(input_ids[:, :-1])
    loss = torch.nn.functional.cross_entropy(
        outputs.logits.reshape(-1, config.vocab_size), targets.reshape(-1)
    )
    if not torch.isfinite(loss):
        raise RuntimeError('Non-finite loss in MiniMind forward pass.')
    loss.backward()
    gradients = [p.grad for p in model.parameters() if p.grad is not None]
    if not gradients or any(not torch.isfinite(g).all() for g in gradients):
        raise RuntimeError('Missing or non-finite gradients.')
    optimizer.step()
    if device.type == 'cuda':
        torch.cuda.synchronize()
    print(f'MiniMind forward/backward/optimizer step passed on {device}; loss={loss.item():.4f}')
    print('Learning environment ready.')


if __name__ == '__main__':
    main()
