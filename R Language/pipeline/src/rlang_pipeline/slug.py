"""slug 生成。

slug 是文章的唯一标识，同时用于：
  - 目录名（en/<slug>/ 与 zh/<slug>/）
  - 配对键（中英两侧同名即视为同一篇）
  - 色号分配表的键

规则刻意保持简单可预测，且**不依赖任何外部库**（不用 unicodedata 的
NFKD 分解，因为那会把中文字符全部丢掉）。
"""

from __future__ import annotations

import hashlib
import re
import unicodedata

# CJK 统一表意文字 + 常用扩展，保留下来不删
_CJK_RANGES = (
    (0x3400, 0x4DBF),    # 扩展 A
    (0x4E00, 0x9FFF),    # 基本区
    (0xF900, 0xFAFF),    # 兼容表意文字
    (0x3040, 0x30FF),    # 日文假名
)

_KEEP_PUNCT = {"-"}

# 知乎「导出文章」时附在文件名尾部的后缀，剥掉才是真标题
_EXPORT_SUFFIXES = ("-落日阳红的文章", "-知乎", "_知乎", "-墨鱼", "-知乎用户")


def strip_export_suffix(name: str) -> str:
    """去掉知乎导出件的文件名后缀。

    >>> strip_export_suffix("用 Rust 给 R 写扩展：完整实践指南-落日阳红的文章")
    '用 Rust 给 R 写扩展：完整实践指南'
    """
    stem = name.strip()
    changed = True
    while changed:
        changed = False
        for suffix in _EXPORT_SUFFIXES:
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)].strip()
                changed = True
    return stem

# 需要整体删除的装饰性括号/书名号等（不是转为连字符，而是直接去掉）
_STRIP_CHARS = "【】《》「」『』〔〕［］"


def _is_cjk(ch: str) -> bool:
    code = ord(ch)
    return any(lo <= code <= hi for lo, hi in _CJK_RANGES)


def slugify(text: str, *, max_len: int = 80) -> str:
    """把任意标题转成 slug。

    >>> slugify("【R Language】broom Package for Tidy Modeling")
    'broom-package-for-tidy-modeling'
    >>> slugify("用 Rust 给 R 写扩展：完整实践指南")
    '用-rust-给-r-写扩展-完整实践指南'
    """
    s = unicodedata.normalize("NFC", text.strip())

    # 1) 去掉装饰性字符
    for ch in _STRIP_CHARS:
        s = s.replace(ch, " ")

    # 2) 去掉常见的标题前缀，例如 "R Language" / "R 语言"
    s = re.sub(r"\bR\s*Language\b", " ", s, flags=re.IGNORECASE)
    s = s.replace("R 语言", " ").replace("R语言", " ")

    out: list[str] = []
    for ch in s:
        if ch.isalnum() or _is_cjk(ch):
            out.append(ch.lower())
        elif ch in _KEEP_PUNCT or ch.isspace():
            out.append("-")
        else:
            # 其余标点（。，：；！？/\\|&%$#@+=~^`'"<>*?()[]{}）一律视为分隔符
            out.append("-")

    slug = "".join(out)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")

    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-")

    if not slug:
        # 极端情况：标题全是标点。用内容哈希兜底，保证仍然稳定。
        slug = "article-" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]

    return slug


def stable_index(slug: str, modulo: int) -> int:
    """由 slug 稳定地映射到 [0, modulo) 的一个下标。

    用途：没在 [palette.assign] 里登记的新文章，自动分配一个固定颜色。
    同一 slug 永远得到同一颜色，不会因为别的文章增删而漂移。
    """
    if modulo <= 0:
        raise ValueError("modulo 必须为正数")
    digest = hashlib.sha1(slug.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % modulo
