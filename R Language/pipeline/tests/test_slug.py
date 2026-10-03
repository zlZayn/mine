"""slug 与稳定取色的测试。"""

from __future__ import annotations

import pytest

from rlang_pipeline.slug import slugify, stable_index, strip_export_suffix


class TestSlugify:
    @pytest.mark.parametrize(
        "title, expected",
        [
            ("【R Language】broom Package for Tidy Modeling",
             "broom-package-for-tidy-modeling"),
            ("【R 语言】匿名函数", "匿名函数"),
            ("【R 语言】ggplot2 绘制已知函数图像", "ggplot2-绘制已知函数图像"),
            ("R Language: Something", "something"),
            ("A  B", "a-b"),
            ("  leading and trailing  ", "leading-and-trailing"),
        ],
    )
    def test_basic(self, title, expected):
        assert slugify(title) == expected

    def test_strips_language_prefix(self):
        """前缀不进 slug —— 否则每个 slug 都带 r-language。"""
        assert not slugify("【R Language】X").startswith("r-language")
        assert not slugify("【R 语言】X").startswith("r-语言")

    def test_theoretical_punctuation_falls_back_to_hash(self):
        """标题全是标点时不能产出空 slug。"""
        out = slugify("！！！？？？")
        assert out.startswith("article-")

    def test_deterministic(self):
        title = "【R 语言】卡方分布与卷积效应"
        assert slugify(title) == slugify(title)

    def test_max_len_respected(self):
        assert len(slugify("x" * 200, max_len=40)) <= 40


class TestExportSuffix:
    @pytest.mark.parametrize(
        "name, expected",
        [
            ("用 Rust 给 R 写扩展：完整实践指南-落日阳红的文章",
             "用 Rust 给 R 写扩展：完整实践指南"),
            ("某标题-知乎", "某标题"),
            ("某标题", "某标题"),
            # 连续后缀也要一次剥干净
            ("某标题-知乎-落日阳红的文章", "某标题"),
        ],
    )
    def test_strip(self, name, expected):
        assert strip_export_suffix(name) == expected


class TestStableIndex:
    def test_deterministic(self):
        for slug in ["a", "b", "anonymous-functions", "【R 语言】匿名函数"]:
            assert stable_index(slug, 12) == stable_index(slug, 12)

    def test_in_range(self):
        for slug in ["a", "b", "c", "d", "e", "中文标题"]:
            assert 0 <= stable_index(slug, 12) < 12

    def test_independent_of_other_articles(self):
        """取色只依赖自身 slug —— 加别的文章不会改变已有配色。"""
        before = stable_index("anonymous-functions", 12)
        _ = [stable_index(f"new-article-{i}", 12) for i in range(50)]
        assert stable_index("anonymous-functions", 12) == before

    def test_zero_modulo_rejected(self):
        with pytest.raises(ValueError):
            stable_index("a", 0)
