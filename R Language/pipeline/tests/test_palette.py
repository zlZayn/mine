"""色板分配的测试。

对应一次真实问题：新文章走纯哈希兜底，与邻近卡片撞成同一个绿色
（tidymodels 与 ggplot2 都是 emerald，而 yellow 一次没用上）。
"""

from __future__ import annotations

import pytest

from rlang_pipeline.config import ConfigError, PaletteStop, allocate_palette

PALETTE = [
    PaletteStop(light="red-300", dark="red-600"),
    PaletteStop(light="orange-300", dark="orange-600"),
    PaletteStop(light="amber-300", dark="amber-600"),
    PaletteStop(light="yellow-300", dark="yellow-600"),
    PaletteStop(light="emerald-300", dark="emerald-600"),
    PaletteStop(light="teal-300", dark="teal-600"),
]


class TestPaletteStop:
    def test_name(self):
        assert PaletteStop(light="red-300", dark="red-600").name == "red"

    def test_tailwind_classes_are_literal(self):
        """必须产出完整字面量类名 —— 模板插值拼出来的类名 Tailwind JIT 扫不到。"""
        assert PaletteStop("red-300", "red-600").tailwind_classes == (
            "from-red-300 to-red-600"
        )


class TestAllocate:
    def test_pinned_colors_are_respected(self):
        slugs = ["a", "b", "c"]
        pinned = {"a": "red", "c": "teal"}
        got = allocate_palette(slugs, PALETTE, pinned)
        assert PALETTE[got["a"]].name == "red"
        assert PALETTE[got["c"]].name == "teal"

    def test_pinned_colors_never_change_with_more_articles(self):
        """回归基线：新增文章不得改动已发布文章的颜色。"""
        base = ["a", "b"]
        pinned = {"a": "red", "b": "teal"}
        before = allocate_palette(base, PALETTE, pinned)

        grown = ["new1", "a", "new2", "b", "new3"]
        after = allocate_palette(grown, PALETTE, pinned)

        assert after["a"] == before["a"]
        assert after["b"] == before["b"]

    def test_unpinned_fills_a_free_colour(self):
        """未登记的必须拿到一个没被固定色占用的颜色。"""
        slugs = ["a", "new", "b"]
        pinned = {"a": "red", "b": "teal"}
        got = allocate_palette(slugs, PALETTE, pinned)
        assert PALETTE[got["new"]].name not in {"red", "teal"}

    def test_no_adjacent_duplicates(self):
        slugs = [f"s{i}" for i in range(6)]
        got = allocate_palette(slugs, PALETTE, {})
        names = [PALETTE[got[s]].name for s in slugs]
        assert all(names[i] != names[i + 1] for i in range(len(names) - 1))

    def test_deterministic(self):
        slugs = ["a", "b", "c", "d"]
        pinned = {"a": "red"}
        assert allocate_palette(slugs, PALETTE, pinned) == allocate_palette(
            slugs, PALETTE, pinned
        )

    def test_unknown_pinned_colour_is_an_error(self):
        """色名写错要立刻报错，不能静默忽略。"""
        with pytest.raises(ConfigError, match="不在"):
            allocate_palette(["a"], PALETTE, {"a": "chartreuse"})

    def test_degenerate_when_all_pinned(self):
        """固定色占满色板时不能崩，且结果仍然确定。"""
        slugs = [f"s{i}" for i in range(len(PALETTE) + 2)]
        pinned = {slug: PALETTE[i % len(PALETTE)].name for i, slug in enumerate(slugs)}
        got = allocate_palette(slugs, PALETTE, pinned)
        assert len(got) == len(slugs)
        assert got == allocate_palette(slugs, PALETTE, pinned)

    def test_in_range(self):
        slugs = [f"s{i}" for i in range(20)]
        got = allocate_palette(slugs, PALETTE, {})
        assert all(0 <= v < len(PALETTE) for v in got.values())

    def test_every_slug_gets_a_colour(self):
        slugs = ["a", "b", "c"]
        got = allocate_palette(slugs, PALETTE, {"b": "amber"})
        assert set(got) == set(slugs)
