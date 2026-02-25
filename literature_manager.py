#!/usr/bin/env python3
"""Literature folder watcher and interactive HTML table generator."""

from __future__ import annotations

import argparse
import html
import json
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

SUPPORTED_EXTENSIONS = {".pdf", ".bib", ".txt", ".md", ".doc", ".docx"}
UNKNOWN = "未知"


@dataclass
class LiteratureItem:
    file_name: str
    title: str
    authors: str
    year: str
    file_type: str
    size_kb: str
    modified_time: str
    absolute_path: str
    objective: str
    keywords: str
    methods: str
    results_conclusion: str
    innovation_limitations: str


def parse_bibtex_text(content: str) -> dict[str, str]:
    """Extract common bibtex fields with a lightweight regex strategy."""

    def get_field(name: str) -> str:
        pattern = rf"{name}\s*=\s*[{{\"]([^}}\"]+)[}}\"]"
        match = re.search(pattern, content, flags=re.IGNORECASE | re.DOTALL)
        return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""

    return {
        "title": get_field("title"),
        "authors": get_field("author"),
        "year": get_field("year"),
        "objective": get_field("abstract"),
        "keywords": get_field("keywords"),
        "methods": "",
        "results_conclusion": "",
        "innovation_limitations": "",
    }


def infer_from_filename(stem: str) -> tuple[str, str, str]:
    """Best-effort parser for file names like 2021_Smith_Transformer Survey."""
    year_match = re.search(r"(19|20)\d{2}", stem)
    year = year_match.group(0) if year_match else ""

    parts = re.split(r"[_\-]+", stem)
    author = ""
    title_parts: list[str] = []
    for part in parts:
        cleaned = part.strip()
        if not cleaned:
            continue
        if not author and cleaned.istitle() and cleaned.isalpha() and len(cleaned) > 2:
            author = cleaned
            continue
        title_parts.append(cleaned)

    title = " ".join(title_parts) if title_parts else stem
    title = title.replace(year, "").strip(" _-") if year else title
    return title or stem, author, year


def extract_structured_sections(text: str) -> dict[str, str]:
    """Extract objective/keywords/methods/results/innovation from txt/md text."""
    cleaned = re.sub(r"\r\n?", "\n", text)

    def section(patterns: list[str]) -> str:
        for p in patterns:
            match = re.search(p, cleaned, flags=re.IGNORECASE | re.DOTALL)
            if match:
                value = re.sub(r"\s+", " ", match.group(1)).strip(" :：;；\n")
                if value:
                    return value[:240]
        return ""

    return {
        "objective": section([
            r"(?:研究目的|目的|objective)\s*[:：]\s*(.+?)(?:\n\s*\n|\n[A-Z\u4e00-\u9fff].{0,20}[:：]|$)",
            r"(?:摘要|abstract)\s*[:：]\s*(.+?)(?:\n\s*\n|\n[A-Z\u4e00-\u9fff].{0,20}[:：]|$)",
        ]),
        "keywords": section([
            r"(?:关键词|关键字|keywords?)\s*[:：]\s*(.+?)(?:\n|$)",
        ]),
        "methods": section([
            r"(?:研究方法|方法|methods?)\s*[:：]\s*(.+?)(?:\n\s*\n|\n[A-Z\u4e00-\u9fff].{0,20}[:：]|$)",
        ]),
        "results_conclusion": section([
            r"(?:主要结果|结论|results?|conclusion)\s*[:：]\s*(.+?)(?:\n\s*\n|\n[A-Z\u4e00-\u9fff].{0,20}[:：]|$)",
        ]),
        "innovation_limitations": section([
            r"(?:创新点与不足|创新点|不足|limitations?)\s*[:：]\s*(.+?)(?:\n\s*\n|\n[A-Z\u4e00-\u9fff].{0,20}[:：]|$)",
        ]),
    }


def parse_content_fields(path: Path) -> dict[str, str]:
    suffix = path.suffix.lower()
    default = {
        "objective": "",
        "keywords": "",
        "methods": "",
        "results_conclusion": "",
        "innovation_limitations": "",
    }

    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return extract_structured_sections(text)

    return default


def _iter_files(folder: Path) -> Iterable[Path]:
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def collect_literature_items(folder: Path) -> list[LiteratureItem]:
    items: list[LiteratureItem] = []

    for path in sorted(_iter_files(folder), key=lambda p: p.name.lower()):
        stat = path.stat()
        title, authors, year = "", "", ""
        content_fields = {
            "objective": "",
            "keywords": "",
            "methods": "",
            "results_conclusion": "",
            "innovation_limitations": "",
        }

        if path.suffix.lower() == ".bib":
            bib_fields = parse_bibtex_text(path.read_text(encoding="utf-8", errors="ignore"))
            title, authors, year = bib_fields["title"], bib_fields["authors"], bib_fields["year"]
            content_fields.update({k: v for k, v in bib_fields.items() if k in content_fields})

        if not title:
            title, authors, year = infer_from_filename(path.stem)

        if path.suffix.lower() in {".txt", ".md"}:
            content_fields.update(parse_content_fields(path))

        items.append(
            LiteratureItem(
                file_name=path.name,
                title=title,
                authors=authors or UNKNOWN,
                year=year or UNKNOWN,
                file_type=path.suffix.lower().lstrip("."),
                size_kb=f"{stat.st_size / 1024:.1f}",
                modified_time=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                absolute_path=str(path.resolve()),
                objective=content_fields["objective"] or UNKNOWN,
                keywords=content_fields["keywords"] or UNKNOWN,
                methods=content_fields["methods"] or UNKNOWN,
                results_conclusion=content_fields["results_conclusion"] or UNKNOWN,
                innovation_limitations=content_fields["innovation_limitations"] or UNKNOWN,
            )
        )

    return items


def render_html(items: list[LiteratureItem], source_dir: Path) -> str:
    data_json = html.escape(json.dumps([asdict(item) for item in items], ensure_ascii=False))

    return f"""<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>文献动态表格</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    .meta {{ color: #555; margin-bottom: 12px; }}
    .global-search {{ width: 360px; padding: 8px; margin-bottom: 12px; }}
    .table-wrap {{ overflow-x: auto; border: 1px solid #ddd; }}
    table {{ border-collapse: collapse; min-width: 1800px; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f5f5f5; cursor: pointer; position: sticky; top: 0; z-index: 1; }}
    .filter-row input {{ width: 100%; box-sizing: border-box; padding: 4px; }}
    tr:nth-child(even) {{ background: #fafafa; }}
    tr:hover {{ background: #eef6ff; }}
    .wrap {{ max-width: 360px; white-space: normal; line-height: 1.4; }}
  </style>
</head>
<body>
  <h1>文献动态表格</h1>
  <div class=\"meta\">来源目录: {html.escape(str(source_dir.resolve()))} | 当前显示: <span id=\"count\">{len(items)}</span> 篇</div>
  <input id=\"globalSearch\" class=\"global-search\" placeholder=\"全局搜索（标题/作者/年份/关键词等）...\" />

  <div class=\"table-wrap\">
    <table id=\"literatureTable\">
      <thead>
        <tr>
          <th data-key=\"idx\">#</th>
          <th data-key=\"title\">标题</th>
          <th data-key=\"authors\">作者</th>
          <th data-key=\"year\">年份</th>
          <th data-key=\"file_type\">类型</th>
          <th data-key=\"size_kb\">大小(KB)</th>
          <th data-key=\"modified_time\">更新时间</th>
          <th data-key=\"objective\">研究目的</th>
          <th data-key=\"keywords\">关键词</th>
          <th data-key=\"methods\">研究方法概述</th>
          <th data-key=\"results_conclusion\">主要结果与结论</th>
          <th data-key=\"innovation_limitations\">创新点与不足</th>
          <th data-key=\"file_name\">文件名</th>
        </tr>
        <tr class=\"filter-row\">
          <th></th>
          <th><input data-filter=\"title\" placeholder=\"筛选标题\" /></th>
          <th><input data-filter=\"authors\" placeholder=\"筛选作者\" /></th>
          <th><input data-filter=\"year\" placeholder=\"筛选年份\" /></th>
          <th><input data-filter=\"file_type\" placeholder=\"筛选类型\" /></th>
          <th><input data-filter=\"size_kb\" placeholder=\"筛选大小\" /></th>
          <th><input data-filter=\"modified_time\" placeholder=\"筛选更新时间\" /></th>
          <th><input data-filter=\"objective\" placeholder=\"筛选研究目的\" /></th>
          <th><input data-filter=\"keywords\" placeholder=\"筛选关键词\" /></th>
          <th><input data-filter=\"methods\" placeholder=\"筛选研究方法\" /></th>
          <th><input data-filter=\"results_conclusion\" placeholder=\"筛选结果结论\" /></th>
          <th><input data-filter=\"innovation_limitations\" placeholder=\"筛选创新不足\" /></th>
          <th><input data-filter=\"file_name\" placeholder=\"筛选文件名\" /></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>

<script>
const data = JSON.parse(`{data_json}`);
const tbody = document.querySelector('#literatureTable tbody');
const globalSearch = document.getElementById('globalSearch');
const countNode = document.getElementById('count');
const filterInputs = Array.from(document.querySelectorAll('[data-filter]'));
let sortKey = null;
let sortAsc = true;

function esc(text) {{
  return String(text ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
}}

function rowHtml(item, idx) {{
  return `
    <tr>
      <td>${{idx + 1}}</td>
      <td class="wrap">${{esc(item.title)}}</td>
      <td>${{esc(item.authors)}}</td>
      <td>${{esc(item.year)}}</td>
      <td>${{esc(item.file_type)}}</td>
      <td>${{esc(item.size_kb)}}</td>
      <td>${{esc(item.modified_time)}}</td>
      <td class="wrap">${{esc(item.objective)}}</td>
      <td class="wrap">${{esc(item.keywords)}}</td>
      <td class="wrap">${{esc(item.methods)}}</td>
      <td class="wrap">${{esc(item.results_conclusion)}}</td>
      <td class="wrap">${{esc(item.innovation_limitations)}}</td>
      <td title="${{esc(item.absolute_path)}}">${{esc(item.file_name)}}</td>
    </tr>`;
}}

function applyFilters() {{
  const globalKeyword = globalSearch.value.trim().toLowerCase();
  const columnFilters = Object.fromEntries(filterInputs.map(i => [i.dataset.filter, i.value.trim().toLowerCase()]));

  let rows = data.filter(item => {{
    const values = [
      item.title, item.authors, item.year, item.file_type, item.size_kb, item.modified_time,
      item.objective, item.keywords, item.methods, item.results_conclusion, item.innovation_limitations, item.file_name
    ].join(' ').toLowerCase();

    const passGlobal = !globalKeyword || values.includes(globalKeyword);
    const passColumns = Object.entries(columnFilters).every(([k, v]) => !v || String(item[k] ?? '').toLowerCase().includes(v));
    return passGlobal && passColumns;
  }});

  if (sortKey) {{
    rows.sort((a, b) => {{
      const av = String(a[sortKey] ?? '').toLowerCase();
      const bv = String(b[sortKey] ?? '').toLowerCase();
      if (av === bv) return 0;
      return (av > bv ? 1 : -1) * (sortAsc ? 1 : -1);
    }});
  }}

  tbody.innerHTML = rows.map(rowHtml).join('');
  countNode.textContent = rows.length;
}}

globalSearch.addEventListener('input', applyFilters);
filterInputs.forEach(input => input.addEventListener('input', applyFilters));

document.querySelectorAll('th[data-key]').forEach(th => {{
  th.addEventListener('click', () => {{
    const key = th.dataset.key;
    if (key === 'idx') return;
    if (sortKey === key) sortAsc = !sortAsc;
    else {{ sortKey = key; sortAsc = true; }}
    applyFilters();
  }});
}});

applyFilters();
</script>
</body>
</html>"""


def scan_and_render(source_dir: Path, output_file: Path) -> int:
    items = collect_literature_items(source_dir)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(render_html(items, source_dir), encoding="utf-8")
    return len(items)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="监控文献目录并生成动态交互表格")
    parser.add_argument("source_dir", type=Path, help="文献文件夹路径")
    parser.add_argument("--output", type=Path, default=Path("output/literature_table.html"), help="输出 HTML 文件")
    parser.add_argument("--interval", type=int, default=30, help="轮询间隔（秒）")
    parser.add_argument("--once", action="store_true", help="仅扫描一次并退出")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_dir: Path = args.source_dir
    output_file: Path = args.output

    if not source_dir.exists() or not source_dir.is_dir():
        raise SystemExit(f"目录不存在或不是文件夹: {source_dir}")

    print(f"开始监控目录: {source_dir.resolve()}")
    print(f"输出文件: {output_file.resolve()}")

    previous_snapshot: dict[str, float] = {}

    while True:
        current_snapshot = {str(path): path.stat().st_mtime for path in _iter_files(source_dir)}

        should_render = current_snapshot != previous_snapshot or (args.once and not previous_snapshot)

        if should_render:
            total = scan_and_render(source_dir, output_file)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 已更新表格，文献数: {total}")
            previous_snapshot = current_snapshot
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 无变化")

        if args.once:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
