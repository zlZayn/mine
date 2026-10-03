"""标题前缀强制的测试。

这里的**每一个**用例都对应一次真实故障：
前缀逻辑最初用「裸标题是否为空」判断有无前缀，
而「【R Language】」这种只有前缀没内容的标题剥完也是空串，
两种含义撞车后真正的标题被当成前缀丢掉，卡片上只剩下 【R Language】。
"""

from __future__ import annotations

import pytest

from rlang_pipeline.normalize import (
    PREFIX_EN,
    PREFIX_ZH,
    enforce_title_prefix,
    strip_title_prefix,
)


class TestStrip:
    @pytest.mark.parametrize(
        "raw, expect_bare, expect_prefix, expect_had",
        [
            ("【R Language】Anonymous Functions", "Anonymous Functions", PREFIX_EN, True),
            ("【R语言】匿名函数", "匿名函数", PREFIX_ZH, True),
            ("【R 语言】匿名函数", "匿名函数", PREFIX_ZH, True),
            ("[R 语言] 洛伦兹曲线", "洛伦兹曲线", PREFIX_ZH, True),
            ("R Language: Something", "Something", PREFIX_EN, True),
            # 无关标题：必须原样保留，且 had_prefix=False
            ("broom Package for Tidy Modeling", "broom Package for Tidy Modeling", "", False),
            ("", "", "", False),
        ],
    )
    def test_strip(self, raw, expect_bare, expect_prefix, expect_had):
        bare, prefix, had = strip_title_prefix(raw)
        assert (bare, prefix, had) == (expect_bare, expect_prefix, expect_had)

    def test_only_prefix_yields_empty_bare_but_still_had_prefix(self):
        """只有前缀、没有正文：裸标题是空串，但 had_prefix 必须为 True。

        这是那个事故的核心 —— 两种情况必须以第三个返回值区分。
        """
        bare, prefix, had = strip_title_prefix("【R Language】")
        assert bare == ""
        assert prefix == PREFIX_EN
        assert had is True


class TestEnforce:
    @pytest.mark.parametrize(
        "raw, lang, expected",
        [
            # 没有前缀 → 补上
            ("broom Package for Tidy Modeling", "en",
             "【R Language】broom Package for Tidy Modeling"),
            ("匿名函数", "zh", "【R 语言】匿名函数"),
            # 已有标准前缀 → 原样
            ("【R Language】Anonymous Functions", "en",
             "【R Language】Anonymous Functions"),
            ("【R 语言】匿名函数", "zh", "【R 语言】匿名函数"),
            # 别名写法 → 收敛到标准写法
            ("【R语言】匿名函数", "zh", "【R 语言】匿名函数"),
            ("[R 语言] 洛伦兹曲线", "zh", "【R 语言】洛伦兹曲线"),
            ("R Language: Something", "en", "【R Language】Something"),
            # 前缀内多余空格
            ("  【R  Language】  多余空格  ", "en", "【R Language】多余空格"),
            # "r language" 后面没有冒号或括号，不算前缀 → 整串保留并补前缀。
            # 这是有意行为：宁可多补一个前缀，也不能把标题切断。
            ("r language - lowercase", "en",
             "【R Language】r language - lowercase"),
        ],
    )
    def test_enforce(self, raw, lang, expected):
        out, _changed = enforce_title_prefix(raw, lang)
        assert out == expected

    def test_bare_title_is_never_lost(self):
        """回归守卫：无关标题绝不能被吃成只剩前缀。

        这条断言直接对应那次事故的现场。
        """
        out, changed = enforce_title_prefix("broom Package for Tidy Modeling", "en")
        assert out.endswith("broom Package for Tidy Modeling")
        assert out != PREFIX_EN
        assert changed is True

    def test_only_prefix_is_left_alone(self):
        """只有前缀时保留原样，不造出一个空标题。"""
        out, changed = enforce_title_prefix("【R Language】", "en")
        assert out == "【R Language】"
        assert changed is False

    def test_empty_is_empty(self):
        assert enforce_title_prefix("", "zh") == ("", False)
        assert enforce_title_prefix("   ", "zh") == ("", False)

    def test_idempotent(self):
        """反复施加不应继续变化。"""
        for raw, lang in [
            ("broom Package", "en"),
            ("【R语言】匿名函数", "zh"),
            ("[R 语言] 标题", "zh"),
        ]:
            once, _ = enforce_title_prefix(raw, lang)
            twice, changed = enforce_title_prefix(once, lang)
            assert twice == once
            assert changed is False
