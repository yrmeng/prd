# literature-manager（ymeng）

一个轻量级文献管理原型工具：
- 定期扫描文献目录（支持 PDF/BIB/TXT/MD/DOC/DOCX）。
- 自动生成可搜索、可排序、可按列筛选的动态 HTML 表格。
- 附带内容摘要列，便于快速建立阅读笔记视图。

## 快速开始

### 方式 1：直接运行脚本

```bash
python3 literature_manager.py /path/to/your/papers
```

### 方式 2：安装为命令行工具（推荐发布后使用）

```bash
pip install .
literature-manager /path/to/your/papers
```

默认持续监控目录，每 30 秒检查一次，输出到：

```text
output/literature_table.html
```

可选参数：

```bash
literature-manager /path/to/your/papers \
  --output output/my_table.html \
  --interval 60
```

只扫描一次：

```bash
literature-manager /path/to/your/papers --once
```

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
