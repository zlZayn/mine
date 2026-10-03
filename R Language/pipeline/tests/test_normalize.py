"""图片引用解析与代码块语言嗅探的测试。

两个坑各来自一次真实故障：
  1. 图片文件名含空格（`Lorenz Curve.png`）或括号（`unnest().png`）。
     用 `[^)\\s]+` 匹配会把名字截断成 `assets/Lorenz`、`assets/unnest(`，
     于是体检误报「图片不存在」。
  2. 知乎导出把 R 代码标成 ```ada```、Rust 代码标成 ```text```。
"""

from __future__ import annotations

import pytest

from rlang_pipeline.articles import _scan_local_assets
from rlang_pipeline.normalize import NormalizeReport, detect_language, fix_code_fences


class TestImageScan:
    @pytest.mark.parametrize(
        "body, expect_local",
        [
            ("![](assets/3fun.png)", ["assets/3fun.png"]),
            # 空格：必须完整保留
            ("![](assets/Lorenz Curve.png)", ["assets/Lorenz Curve.png"]),
            # 配对括号：必须完整保留
            ("![](assets/unnest().png)", ["assets/unnest().png"]),
            # alt 文本含空格
            ("![alt text](assets/a b (c).png)", ["assets/a b (c).png"]),
            # 尖括号包裹形式
            ("![](<assets/a b.png>)", ["assets/a b.png"]),
            # 中文文件名
            ("![](assets/MICE 示意图.png)", ["assets/MICE 示意图.png"]),
        ],
    )
    def test_local_names_survive(self, body, expect_local):
        local, _remote = _scan_local_assets(body)
        assert local == expect_local

    def test_remote_not_treated_as_local(self):
        local, remote = _scan_local_assets(
            "![](https://pic2.zhimg.com/v2-abc_1440w.jpg)"
        )
        assert local == []
        assert remote == ["https://pic2.zhimg.com/v2-abc_1440w.jpg"]

    def test_mixed(self):
        body = (
            "![](https://pic2.zhimg.com/a.jpg)\n"
            "![](assets/Lorenz Curve.png)\n"
            "![](assets/unnest().png)\n"
        )
        local, remote = _scan_local_assets(body)
        assert local == ["assets/Lorenz Curve.png", "assets/unnest().png"]
        assert remote == ["https://pic2.zhimg.com/a.jpg"]

    def test_obsidian_wiki_form(self):
        local, _remote = _scan_local_assets("![[Lorenz Curve.png]]")
        assert local == ["Lorenz Curve.png"]

    def test_data_uri_ignored(self):
        local, remote = _scan_local_assets("![](data:image/png;base64,AAAA)")
        assert local == []
        assert remote == []


class TestDetectLanguage:
    @pytest.mark.parametrize(
        "code, current, expected",
        [
            # 知乎把 R 标成 ada
            ("library(tidyverse)\ndf <- mtcars", "ada", "r"),
            ("models |> map(glance)", "ada", "r"),
            # 知乎把 Rust 标成 text
            ("use extendr_api::prelude::*;\n#[extendr]\nfn f() {}", "text", "rust"),
            ("extendr_module! {\n    mod mypkg;\n}", "text", "rust"),
            # 已标对的要尊重原样
            ("library(dplyr)", "r", "r"),
            ("fn main() {}", "rust", "rust"),
            ("echo hi", "bash", "bash"),
            # 单行 R 调用：没有 library/管道/函数定义，靠弱信号兜住
            ("rextendr::rust_sitrep()", "text", "r"),
            ("devtools::document()", "ada", "r"),
            ("add_one(5)\n# [1] 6", "text", "r"),
            ('x <- "字符串"', "text", "r"),
            # 目录树：保留无高亮，标语言反而难看
            ("mypkg/\n├── R/\n│   └── extendr-wrappers.R\n└── src/", "text", ""),
        ],
    )
    def test_detect(self, code, current, expected):
        assert detect_language(code, current) == expected

    def test_tree_not_tagged_as_r(self):
        """目录树里出现 `.R` 文件名，不能被误判成 R 代码。"""
        tree = "mypkg/\n├── R/\n│   └── extendr-wrappers.R\n├── tools/\n│   └── config.R\n"
        assert detect_language(tree, "text") == ""


class TestFixCodeFences:
    def test_ada_becomes_r(self):
        body = "```ada\nlibrary(dplyr)\n```\n"
        out = fix_code_fences(body, NormalizeReport())
        assert out.startswith("```r\n")

    def test_text_becomes_rust(self):
        body = "```text\n#[extendr]\nfn f() {}\n```\n"
        out = fix_code_fences(body, NormalizeReport())
        assert out.startswith("```rust\n")

    def test_correct_language_untouched(self):
        body = "```r\nlibrary(dplyr)\n```\n"
        report = NormalizeReport()
        out = fix_code_fences(body, report)
        assert out == body
        assert report.fences_fixed == 0

    def test_content_preserved_exactly(self):
        """只许改语言标记，块内内容一个字符都不能动。"""
        code = "x <- 1\n# 中文注释\nprint(x)"
        body = f"```ada\n{code}\n```\n"
        out = fix_code_fences(body, NormalizeReport())
        assert code in out

    def test_multiple_blocks_independent(self):
        body = "```ada\nlibrary(a)\n```\n\ntext\n\n```text\n#[extendr]\n```\n"
        out = fix_code_fences(body, NormalizeReport())
        assert "```r\n" in out
        assert "```rust\n" in out

    def test_unclosed_fence_does_not_crash(self):
        body = "```ada\nlibrary(a)\n"
        out = fix_code_fences(body, NormalizeReport())
        assert isinstance(out, str)

    def test_tilde_fence(self):
        body = "~~~ada\nlibrary(dplyr)\n~~~\n"
        out = fix_code_fences(body, NormalizeReport())
        assert out.startswith("~~~r")
