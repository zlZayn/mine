"""frontmatter 子集读写的测试。"""

from __future__ import annotations

import pytest

from rlang_pipeline.frontmatter import FrontmatterError, dump, parse

SAMPLE = """---
zhihu-title: 【R 语言】broom 包进行整洁建模
zhihu-topics: R
zhihu-link: https://zhuanlan.zhihu.com/p/1949603330578953873
zhihu-created-at: 2025-09-11 22:51
---

正文第一段。
"""


class TestParse:
    def test_basic(self):
        fm = parse(SAMPLE)
        assert fm.had_block is True
        assert fm.data["zhihu-title"] == "【R 语言】broom 包进行整洁建模"
        assert fm.data["zhihu-topics"] == "R"
        assert fm.body.startswith("正文第一段。")

    def test_url_not_mangled(self):
        """值里的冒号只能按第一个冒号切分，URL 不能被截断。"""
        fm = parse(SAMPLE)
        assert fm.data["zhihu-link"] == "https://zhuanlan.zhihu.com/p/1949603330578953873"

    def test_datetime_kept_as_string(self):
        """日期时间不能被当成数字或其它类型。"""
        fm = parse(SAMPLE)
        assert fm.data["zhihu-created-at"] == "2025-09-11 22:51"

    def test_empty_value(self):
        fm = parse("---\nzhihu-created-at: \n---\n正文\n")
        assert fm.data["zhihu-created-at"] == ""

    def test_no_frontmatter(self):
        fm = parse("就是一段正文\n")
        assert fm.had_block is False
        assert fm.data == {}
        assert fm.body == "就是一段正文\n"

    def test_bom_stripped_when_no_block(self):
        fm = parse("\ufeff正文\n")
        assert not fm.body.startswith("\ufeff")

    def test_crlf_tolerated(self):
        fm = parse("---\r\nen-title: X\r\n---\r\n正文\r\n")
        assert fm.data["en-title"] == "X"

    def test_comments_skipped(self):
        fm = parse("---\n# 注释\nen-title: X\n---\n正文\n")
        assert fm.data == {"en-title": "X"}

    def test_nested_rejected(self):
        """不支持嵌套 —— 报错而不是静默丢弃。"""
        with pytest.raises(FrontmatterError):
            parse("---\nlist:\n  - a\n---\n正文\n")

    def test_missing_colon_rejected(self):
        with pytest.raises(FrontmatterError):
            parse("---\n没有冒号\n---\n正文\n")


class TestDump:
    def test_roundtrip_stable(self):
        fm = parse(SAMPLE)
        out = dump(fm.data, fm.body, key_order=["zhihu-title", "zhihu-topics",
                                                "zhihu-link", "zhihu-created-at"])
        again = parse(out)
        assert again.data == fm.data
        assert again.body.strip() == fm.body.strip()

    def test_key_order_respected(self):
        fm = parse(SAMPLE)
        out = dump(fm.data, fm.body, key_order=["zhihu-link", "zhihu-title"])
        lines = out.splitlines()
        assert lines[1].startswith("zhihu-link:")
        assert lines[2].startswith("zhihu-title:")

    def test_keys_outside_order_appended(self):
        out = dump({"a": "1", "b": "2", "c": "3"}, "正文", key_order=["b"])
        lines = out.splitlines()
        assert lines[1].startswith("b:")
        assert {line.split(":")[0] for line in lines[1:4]} == {"a", "b", "c"}

    def test_none_values_skipped(self):
        out = dump({"a": "1", "b": None}, "正文")
        assert "b:" not in out

    def test_starts_and_ends_with_fence(self):
        out = dump({"a": "1"}, "正文")
        lines = out.splitlines()
        assert lines[0] == "---"
        assert "---" in lines
