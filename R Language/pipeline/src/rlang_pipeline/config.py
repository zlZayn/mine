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
    def tailwind_classes(self) -> str:
        """拼成完整的 Tailwind 类名。

        必须产出字面量类名（如 "from-red-300 to-red-600"），
        不能让模板去做 "from-{{ color }}-300" 这种变量插值 ——
        Tailwind CDN 的 JIT 是按字面量扫描源码的，插值出来的类名扫不到。
        """
        l_name, l_shade = self.light.rsplit("-", 1)
        d_name, d_shade = self.dark.rsplit("-", 1)
        return f"from-{l_name}-{l_shade} to-{d_name}-{d_shade}"


@dataclass(frozen=True)
class HeaderLink:
    label: str
    href: str
    style: str  # "github" | "zhihu"


@dataclass(frozen=True)
class SiteConfig:
    raw: dict[str, Any]
    palette: list[PaletteStop] = field(default_factory=list)
    palette_assign: dict[str, int] = field(default_factory=dict)
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

    assign = {str(k): int(v) for k, v in raw.get("palette", {}).get("assign", {}).items()}

    # ---- 页头按钮 ----
    links = [
        HeaderLink(label=item["label"], href=item["href"], style=item.get("style", ""))
        for item in raw.get("header", {}).get("links", [])
    ]

    return SiteConfig(
        raw=raw, palette=stops, palette_assign=assign, header_links=links
    )
