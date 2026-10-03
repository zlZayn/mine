"""site.toml 的读取与访问。

任何"站点事实"（站名、仓库地址、专栏地址、按钮文字、色板）都必须来自这里，
不允许在模板或脚本里再写一份。
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class PaletteStop:
    """一个渐变色档，例如 red-300 : red-600。"""

    light: str  # "red-300"
    dark: str   # "red-600"

    @property
    def name(self) -> str:
        """色名，例如 "red"。

        site.toml 登记固定色时用它而不是下标 ——
        往 stops 里插一个新颜色时下标会整体错位，色名不会。
        """
        return self.light.rsplit("-", 1)[0]

    @property
    def tailwind_classes(self) -> str:
        """拼成完整的 Tailwind 类名。

        必须产出字面量类名（如 "from-red-300 to-red-600"），
        不能让模板去做 "from-{{ color }}-300" 这种变量插值 ——
        Tailwind CDN 的 JIT 是按字面量扫描源码的，插值出来的类名扫不到。
        """
        l_name, l_shade = self.light.rsplit("-", 1)
        d_name, d_shade = self.dark.rsplit("-", 1)
        return f"from-{l_name}-{l_shade} to-{d_name}-{d_shade}"


def allocate_palette(
    slugs: list[str],
    palette: list[PaletteStop],
    pinned: dict[str, str],
    *,
    window: int = 4,
) -> dict[str, int]:
    """给每篇文章分配一个色板下标。

    分两步，而不是"边遍历边挑"：

      第一步  把 `pinned` 登记的固定色钉到各自的槽位上。
      第二步  给剩下的空槽挑颜色：枚举所有候选，取「在 window 范围内
              与已钉住的颜色冲突最少」的那个；并列时取色板顺序最靠前的。

    为什么不做"边遍历边挑第一个可用的"：
      那是先到先得。新文章夹在两篇固定色文章中间时，
      最近处未占用的低位色号会被反复选中，
      结果新文章互相之间、以及与远处的固定色主重复
      （实测 red 与 orange 各出现两次，而 yellow/indigo/rose 一次没用上）。
      先钉住全部固定色、再通盘挑空位，才能让新文章自动落到真正空闲的色上。

    为什么限定 window 而不是要求全页唯一：
      全页唯一在文章数超过色板长度时无解，规则会突然失效。
      限定窗口的规则在任何文章数下都成立，退化是平滑的。

    确定性的保证：
      - 空槽按 `slugs` 顺序逐个填，顺序固定
      - 候选按色板原顺序枚举，并列取最小下标
      - 评分只看已钉住的颜色，不看其它空槽的临时结果
      同一组输入永远得到同一张表。
    """
    by_name = {stop.name: idx for idx, stop in enumerate(palette)}

    for slug, color in pinned.items():
        if color not in by_name:
            raise ConfigError(
                f"[palette.pinned] 里 {slug} 的颜色 {color!r} 不在 [palette].stops 中。\n"
                f"可用色名：{', '.join(by_name)}"
            )

    total = len(palette)
    n = len(slugs)

    # 第一步：钉住固定色
    slots: list[int | None] = [
        by_name[pinned[slug]] if slug in pinned else None for slug in slugs
    ]
    pinned_indices = {idx for idx in slots if idx is not None}

    # 若固定色已占满整个色板，空槽无解，直接按位置取模
    if len(pinned_indices) >= total:
        return {
            slug: (slots[i] if slots[i] is not None else i % total)
            for i, slug in enumerate(slugs)
        }

    def conflicts(candidate: int, position: int) -> tuple[int, int, int]:
        """给候选色打分，越小越好。

        返回 (窗口内冲突次数, 全页冲突次数, 色号)。
        全页冲突是次级判据：窗口内实在挑不出时，也不去加重全局重复。
        """
        lo, hi = max(0, position - window), min(n, position + window + 1)
        near = sum(1 for j in range(lo, hi) if j != position and slots[j] == candidate)
        far = sum(1 for j in range(n) if j != position and slots[j] == candidate)
        return (near, far, candidate)

    # 第二步：逐个填空槽
    for i, slug in enumerate(slugs):
        if slots[i] is not None:
            continue
        slots[i] = min(range(total), key=lambda c: conflicts(c, i))

    return {slug: int(slots[i]) for i, slug in enumerate(slugs)}


@dataclass(frozen=True)
class HeaderLink:
    label: str
    href: str
    style: str  # "github" | "zhihu"


@dataclass(frozen=True)
class SiteConfig:
    raw: dict[str, Any]
    palette: list[PaletteStop] = field(default_factory=list)
    # 已发布文章的固定色：article id -> 色名（如 "red"）
    palette_pinned: dict[str, str] = field(default_factory=dict)
    header_links: list[HeaderLink] = field(default_factory=list)

    # ---- 便捷访问 ----
    @property
    def title(self) -> str:
        return self.raw["site"]["title"]

    @property
    def lang(self) -> str:
        return self.raw["site"].get("lang", "zh-CN")

    @property
    def logo_image(self) -> str:
        return self.raw["header"]["logo_image"]

    @property
    def logo_alt(self) -> str:
        return self.raw["header"]["logo_alt"]

    @property
    def logo_href(self) -> str:
        return self.raw["header"]["logo_href"]

    @property
    def corner_href(self) -> str:
        return self.raw["corner"]["href"]

    @property
    def english_label(self) -> str:
        return self.raw["card"]["english_label"]

    @property
    def chinese_label(self) -> str:
        return self.raw["card"]["chinese_label"]

    @property
    def pending_label(self) -> str:
        """英文尚未翻译时，卡片上半行显示的占位文字。"""
        return self.raw["card"].get("pending_label", "English version pending")

    @property
    def repo_base_url(self) -> str:
        return self.raw["repo"]["base_url"].rstrip("/")

    @property
    def repo_branch(self) -> str:
        return self.raw["repo"]["branch"]

    @property
    def repo_content_dir(self) -> str:
        return self.raw["repo"]["content_dir"]

    @property
    def order_direction(self) -> str:
        return self.raw.get("order", {}).get("direction", "newest-first")


def load_site_config(path: Path) -> SiteConfig:
    if not path.exists():
        raise ConfigError(f"找不到站点配置：{path}")

    with path.open("rb") as fh:
        raw = tomllib.load(fh)

    # ---- 校验必填项，缺了就直接报错，不要静默用默认值 ----
    required_paths = [
        ("site", "title"),
        ("header", "logo_image"),
        ("header", "logo_alt"),
        ("header", "logo_href"),
        ("corner", "href"),
        ("card", "english_label"),
        ("card", "chinese_label"),
        ("repo", "base_url"),
        ("repo", "content_dir"),
    ]
    for section, key in required_paths:
        if key not in raw.get(section, {}):
            raise ConfigError(f"site.toml 缺少必填项 [{section}].{key}")

    # ---- 色板 ----
    stops: list[PaletteStop] = []
    for entry in raw.get("palette", {}).get("stops", []):
        if ":" not in entry:
            raise ConfigError(
                f"色板条目格式应为 'light:dark'（如 red-300:red-600），实际为 {entry!r}"
            )
        light, dark = entry.split(":", 1)
        stops.append(PaletteStop(light=light.strip(), dark=dark.strip()))

    if not stops:
        raise ConfigError("site.toml 的 [palette].stops 不能为空")

    pinned = {
        str(k): str(v) for k, v in raw.get("palette", {}).get("pinned", {}).items()
    }

    # ---- 页头按钮 ----
    links = [
        HeaderLink(label=item["label"], href=item["href"], style=item.get("style", ""))
        for item in raw.get("header", {}).get("links", [])
    ]

    return SiteConfig(
        raw=raw, palette=stops, palette_pinned=pinned, header_links=links
    )
