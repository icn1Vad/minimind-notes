# Windows 本地学习环境

工作目录：`F:\minimind-notes`。对应[教程路线图](https://www.minimind.wiki/ROADMAP)的基础实验、数据准备和后续单卡训练。

## 日常运行

在 PowerShell 中进入项目后，用 `learn.cmd` 运行 Python；它始终使用项目的 `venv`，不需要先激活虚拟环境。

```powershell
Set-Location F:\minimind-notes
.\learn.cmd scripts/check_learning_env.py --require-cuda
.\learn.cmd modules/01-foundation/01-normalization/experiments/exp1_gradient_vanishing.py
.\learn.cmd modules/01-foundation/02-position-encoding/experiments/exp1_rope_basics.py
.\learn.cmd modules/01-foundation/03-attention/experiments/exp1_attention_basics.py
```

归一化实验会弹出图片窗口，关闭窗口后脚本结束；结果保存在对应实验目录的 `results/` 中。RoPE 和 Attention 的入门实验直接在终端显示结果。

## 重建或修复环境

推荐 Python 3.11。当前机器为 RTX 5070 Ti Laptop GPU，使用官方 CUDA 12.8 版 PyTorch 2.9.1；它支持 Blackwell 显卡。安装包含较大的 GPU 运行库，请预留约 10GB 磁盘空间。

```powershell
Set-Location F:\minimind-notes
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
```

`Bypass` 仅对这次 PowerShell 子进程有效，不修改系统执行策略。脚本先安装匹配的 PyTorch，再安装 `requirements-windows.txt` 并检查依赖、GPU 及 MiniMind 的一次前向传播、反向传播和优化器更新。无需另装完整 CUDA Toolkit。

无 NVIDIA 显卡的机器可在安装命令末尾加 `-Compute cpu`，验证时省略 `--require-cuda`。

**不要再次使用原始 `requirements.txt` 覆盖本环境**：它锁定旧版 `ujson==5.1.0` 和 `torch==2.6.0`。Windows 配置保留其余教程依赖，并替换这两个兼容性问题相关的版本、匹配 torchvision，再补上通用可视化工具需要的 seaborn。上游文件保持原样。

另外固定 `pyarrow==19.0.1`，避免自动安装要求 NumPy 2 的新版本，与教程锁定的 `numpy==1.26.4` 冲突。环境检查会实际导入 `datasets`，而不只检查包版本声明。

## 本地阅读教程

部署时已安装前端依赖并构建文档，本地预览地址为 [学习路线图](http://127.0.0.1:4173/ROADMAP)。重启电脑后，可在仓库根目录重新启动：

```powershell
pnpm run docs:preview --host 127.0.0.1 --port 4173 --strictPort
```

修改 Markdown 后，先运行 `pnpm run docs:build` 更新预览内容；需要边改边预览时使用 `pnpm run docs:dev`。

站点配置已排除 `venv/` 等虚拟环境目录，避免将第三方包的 Markdown 模板作为教程页面构建。

## 数据和后续训练

1. 前三个入门实验不需要下载数据。
2. TinyShakespeare 缓存在 `modules/common/data/tinyshakespeare.txt`，可用下面命令检查或下载：

   ```powershell
   .\learn.cmd modules/common/data_sources.py --dataset shakespeare
   ```

3. TinyStories 按需下载；教程的 `--download-all` 还会取 10MB 和 50MB 子集，需要访问 Hugging Face。
4. 正式预训练前另行准备 `dataset/pretrain_hq.jsonl`，SFT 和 LoRA 也需要各自的数据与前一阶段权重。环境检查中的小模型更新只验证运行链路，不会启动正式训练或产生可用的预训练权重。
5. 教程的 `bash run_all.sh` 面向 Bash。Windows PowerShell 可分别执行其中的 Python 命令；训练脚本按教程要求从 `trainer` 目录运行，单卡训练可先使用 `--num_workers 0` 排查数据加载问题。

在 `trainer` 目录使用同一环境：

```powershell
Set-Location F:\minimind-notes\trainer
..\learn.cmd train_pretrain.py --help
```

本地数据、虚拟环境和训练权重不应提交到 Git。`origin` 指向自己的 `icn1Vad/minimind-notes`，`upstream` 保留教程原仓库。

参考：[PyTorch 官方版本安装命令](https://pytorch.org/get-started/previous-versions/)、[Blackwell 支持说明](https://pytorch.org/blog/pytorch-2-7/)。
