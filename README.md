# literature-manager（ymeng）

一个轻量级文献管理原型工具：
- 手动扫描文献目录（支持 PDF/BIB/TXT/MD/DOC/DOCX），并可选开启持续监控。
- 自动生成可搜索、可排序、可按列筛选的动态 HTML 表格。
- 附带内容摘要列，便于快速建立阅读笔记视图。

## 快速开始

### 方式 1：直接运行脚本

```bash
python3 literature_manager.py /path/to/your/papers
```

默认即手动扫描一次并退出。

### 方式 2：安装为命令行工具（推荐发布后使用）

```bash
pip install .
literature-manager /path/to/your/papers
```

默认输出到：

```text
output/literature_table.html
```

### 监控模式（可选）

```bash
literature-manager /path/to/your/papers --watch --interval 60
```

### 指定输出路径

```bash
literature-manager /path/to/your/papers --output output/my_table.html
```

## 从 GitHub 直接安装（本地用户最方便）

如果你已经把仓库发布到 GitHub，用户可以不下载源码，直接安装：

### HTTPS 安装

```bash
pip install "git+https://github.com/<你的GitHub用户名>/<你的仓库名>.git"
```

### 指定分支/标签安装（推荐发布版本时使用 tag）

```bash
pip install "git+https://github.com/<你的GitHub用户名>/<你的仓库名>.git@v0.1.0"
```

### SSH 安装（适合私有仓库或已配置 SSH Key）

```bash
pip install "git+ssh://git@github.com/<你的GitHub用户名>/<你的仓库名>.git"
```

安装后可直接运行：

```bash
literature-manager /path/to/your/papers
```

## Windows 一键安装（EXE 安装包）

可以。项目已提供 Windows 打包脚本与安装器脚本：
- `scripts/windows/build_windows_exe.ps1`（用 PyInstaller 生成 exe）
- `scripts/windows/literature-manager.iss`（用 Inno Setup 生成一键安装包）

### 在 Windows 上构建步骤

1. 安装依赖：
   - Python 3.9+
   - Inno Setup 6（安装后包含 `ISCC.exe`）

2. 在 PowerShell 进入项目目录后执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\build_windows_exe.ps1
```

产物目录：

```text
dist\literature-manager\literature-manager.exe
```

3. 生成一键安装程序（Setup.exe）：

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" .\scripts\windows\literature-manager.iss
```

安装包输出：

```text
dist\literature-manager-setup-0.1.0.exe
```

用户双击该安装包即可完成安装（可选桌面快捷方式）。

## 交互能力

1. 点击表头进行升序/降序排序。
2. 顶部全局搜索。
3. 每一列下方独立筛选输入框。

## 提取字段

- 标题、作者、年份、类型、大小、更新时间、文件名
- 研究目的
- 关键词
- 研究方法概述
- 主要结果与结论
- 创新点与不足

提取策略：
- `.bib`：提取 `title/author/year`，并尝试提取 `abstract/keywords`。
- `.txt/.md`：通过常见章节名（研究目的/关键词/方法/结论/创新点与不足）进行轻量抽取。
- 其他类型（如 PDF/DOCX）目前内容列为“未知”，后续可接入专用解析器。

## 发布（PyPI）

1. 安装打包工具：

```bash
python3 -m pip install --upgrade build twine
```

2. 构建发布包：

```bash
python3 -m build
```

3. 检查包：

```bash
python3 -m twine check dist/*
```

4. 上传到 PyPI：

```bash
python3 -m twine upload dist/*
```

## 适合下一步扩展

- 接入 PDF 元数据解析（DOI、期刊、摘要）。
- 接入 LLM 自动摘要能力。
- 支持 Zotero / EndNote 导入与标签管理。
