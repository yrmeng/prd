import json
import re
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

import literature_manager as lm


class LiteratureManagerTests(unittest.TestCase):
    def test_parse_bibtex_text_extracts_fields(self):
        bib = """
        @article{demo,
          title={A Demo Paper},
          author={Alice and Bob},
          year={2024},
          abstract={A short abstract.},
          keywords={nlp, survey}
        }
        """
        result = lm.parse_bibtex_text(bib)
        self.assertEqual(result["title"], "A Demo Paper")
        self.assertEqual(result["authors"], "Alice and Bob")
        self.assertEqual(result["year"], "2024")
        self.assertEqual(result["objective"], "A short abstract.")
        self.assertEqual(result["keywords"], "nlp, survey")

    def test_extract_structured_sections_from_text(self):
        text = """
        研究目的：验证自动化文献整理流程。
        关键词：文献管理, 自动化
        研究方法：规则提取与文件监控。
        主要结果与结论：可以提升检索和综述效率。
        创新点与不足：轻量易用，但 PDF 深度解析待增强。
        """
        result = lm.extract_structured_sections(text)
        self.assertIn("自动化文献整理", result["objective"])
        self.assertIn("文献管理", result["keywords"])
        self.assertIn("规则提取", result["methods"])
        self.assertIn("检索", result["results_conclusion"])
        self.assertIn("轻量易用", result["innovation_limitations"])

    def test_scan_and_render_creates_html(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "sample.md").write_text(
                "研究目的：验证\n关键词：测试\n研究方法：脚本\n主要结果与结论：可行\n创新点与不足：简单\n",
                encoding="utf-8",
            )
            out = root / "out" / "table.html"
            total = lm.scan_and_render(root, out)
            self.assertEqual(total, 1)
            self.assertTrue(out.exists())
            content = out.read_text(encoding="utf-8")
            self.assertIn("文献动态表格", content)
            self.assertIn("研究方法概述", content)


    def test_render_html_embeds_valid_json_script_payload(self):
        item = lm.LiteratureItem(
            file_name='a.md',
            title='含"引号"标题',
            authors='作者',
            year='2024',
            file_type='md',
            size_kb='1.0',
            modified_time='2024-01-01 00:00:00',
            absolute_path='C:/tmp/a.md',
            objective='目的',
            keywords='关键词',
            methods='方法',
            results_conclusion='结论',
            innovation_limitations='不足',
        )
        html_doc = lm.render_html([item], Path('.'))
        match = re.search(r'<script id="literature-data" type="application/json">(.*?)</script>', html_doc, re.DOTALL)
        self.assertIsNotNone(match)
        payload = match.group(1)
        parsed = json.loads(payload)
        self.assertEqual(parsed[0]['title'], '含"引号"标题')

    def test_cli_default_manual_scan(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "manual.html"
            cmd = [
                "python3",
                "literature_manager.py",
                str(root),
                "--output",
                str(out),
            ]
            completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.assertTrue(out.exists())
            self.assertIn("手动扫描完成", completed.stdout)

    def test_main_works_without_watch_attribute_for_backward_compat(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "manual.html"
            fake_args = SimpleNamespace(source_dir=root, output=out)

            with mock.patch("literature_manager.parse_args", return_value=fake_args), \
                mock.patch("literature_manager.scan_and_render", return_value=0) as scan_mock:
                lm.main()

            scan_mock.assert_called_once_with(root, out)


if __name__ == "__main__":
    unittest.main()
