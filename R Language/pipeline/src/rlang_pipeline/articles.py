"""文章模型与配对加载。

配对键是 slug（目录名），不是顺序。
中文侧提供知乎标题与链接，英文侧提供英文标题；两侧各自可独立缺失，
缺失由 check 子命令报出来，而不是静默生成半张卡片。
"""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from . import frontmatter as fm
from .config import SiteConfig, allocate_palette
from .paths import Paths

# frontmatter 写回时的键顺序，保证 diff 稳定
ZH_KEY_ORDER = ["zhihu-title", "zhihu-topics", "zhihu-link", "zhihu-created-at"]
EN_KEY_ORDER = ["en-title", "slug", "zhihu-link", "zhihu-created-at"]

ZH_REQUIRED = ["zhihu-title", "zhihu-link", "zhihu-topics", "zhihu-created-at"]
EN_REQUIRED = ["en-title"]

# 图片引用。
#
# 路径里可以含空格（"assets/Lorenz Curve.png"），也可以含配对括号
# （"assets/unnest().png"）—— 两种都真实存在于本仓库。
#
# 三种写法都不行，逐一记下来免得再走回头路：
#   [^)\s]+                空格被排除 → "assets/Lorenz" 被截断
#   (?:[^()\s]|\([^()]*\))+  同样排除空格 → 带空格的名字匹配不到
#   [^)]+                  贪婪停在第一个 ')' → "assets/unnest(" 被截断
#
# 正确写法：只排除裸括号，但允许一层配对括号，且**不排除空格**。
# 这样"到目标结束的那个 ')'"才是真正配对的那一个。
_MD_IMG_DEST = r"(?:<([^>]+)>|((?:[^()]|\([^()]*\))+))"
_MD_IMG_RE = re.compile(r"!\[[^\[\]]*\]\(" + _MD_IMG_DEST + r"\)")
_WIKI_IMG_RE = re.compile(r"!\[\[([^\]|]+)")


def encode_repo_path(path: str) -> str:
    """把仓库内路径编码成 URL 片段，逐段编码但保留 / 分隔符。

    中文标题、空格、括号都要编码，否则 GitHub 链接会 404。
    """
    return "/".join(quote(segment, safe="") for segment in path.split("/"))


@dataclass
class Side:
    """一篇文章在某一语言下的全部信息。"""

    lang: str
    slug: str
    dir: Path
    exists: bool
    data: dict = field(default_factory=dict)
    body: str = ""
    raw: str = ""
    local_asset_refs: list[str] = field(default_factory=list)
    remote_image_refs: list[str] = field(default_factory=list)

    @property
    def title(self) -> str:
        if self.lang == "zh":
            return str(self.data.get("zhihu-title", "")).strip()
        return str(self.data.get("en-title", "")).strip()

    @property
    def zhihu_link(self) -> str:
        return str(self.data.get("zhihu-link", "")).strip()

    @property
    def created_at(self) -> str:
        return str(self.data.get("zhihu-created-at", "")).strip()

    @property
    def sort_key(self) -> tuple:
        """排序键。日期解析失败的文章排到最后，而不是让整批排序崩掉。"""
        raw = self.created_at
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                return (0, _dt.datetime.strptime(raw, fmt))
            except ValueError:
                continue
        return (1, _dt.datetime.min)

    def missing_required(self) -> list[str]:
        required = ZH_REQUIRED if self.lang == "zh" else EN_REQUIRED
        return [k for k in required if not str(self.data.get(k, "")).strip()]


@dataclass
class Article:
    slug: str
    zh: Side
    en: Side
    # 色板下标，由 load_articles 在排序后统一分配（见 config.allocate_palette）
    color_index: int = 0

    @property
    def display_en_title(self) -> str:
        """英文标题。

        刻意**不**回退到中文标题：英文尚未翻译时，
        回退会让卡片上下两行显示同一句话，读者会以为英文版就是中文。
        缺就是空，由模板渲染成显式的"pending"占位。
        """
        return self.en.title

    @property
    def has_english(self) -> bool:
        """英文侧是否存在且真的有标题（判断"是否已翻译"）。"""
        return self.en.exists and bool(self.en.title)

    @property
    def display_zh_title(self) -> str:
        return self.zh.title

    def color(self, config: SiteConfig):
        return config.palette[self.color_index]


def english_repo_url(config: SiteConfig, slug: str) -> str:
    """英文原文在 GitHub 上的链接。由配置推导，不写死。"""
    path = f"{config.repo_content_dir}/{slug}/index.md"
    return f"{config.repo_base_url}/blob/{config.repo_branch}/{encode_repo_path(path)}"


def english_pages_url(slug: str) -> str:
    """英文文章在 GitHub Pages 上的渲染页。

    与 en/<slug>/index.md 的目录结构同构，
    只把 index.md 换成 index.html。
    """
    return f"{encode_repo_path(slug)}/index.html"


def _scan_local_assets(body: str) -> tuple[list[str], list[str]]:
    """扫正文里的图片引用，返回 (本地相对路径, 远程 http(s) 图片)。"""
    local: list[str] = []
    remote: list[str] = []

    for match in _MD_IMG_RE.finditer(body):
        target = (match.group(1) or match.group(2) or "").strip()
        if not target:
            continue
        if target.startswith(("http://", "https://", "//")):
            remote.append(target)
        elif target.startswith("data:"):
            continue
        else:
            local.append(target)

    for match in _WIKI_IMG_RE.finditer(body):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://")):
            remote.append(target)
        else:
            local.append(target)

    return local, remote


def _load_side(lang: str, slug: str, paths: Paths) -> Side:
    markdown = paths.article_markdown(lang, slug)
    directory = paths.article_dir(lang, slug)

    if not markdown.exists():
        return Side(lang=lang, slug=slug, dir=directory, exists=False)

    raw = markdown.read_text(encoding="utf-8")
    parsed = fm.parse(raw)
    local, remote = _scan_local_assets(parsed.body)

    return Side(
        lang=lang,
        slug=slug,
        dir=directory,
        exists=True,
        data=parsed.data,
        body=parsed.body,
        raw=raw,
        local_asset_refs=local,
        remote_image_refs=remote,
    )


def _slugs_in(lang_dir: Path) -> set[str]:
    if not lang_dir.exists():
        return set()
    return {
        child.name
        for child in lang_dir.iterdir()
        if child.is_dir()
        and (child / "index.md").exists()
        and not child.name.startswith((".", "_"))
    }


def load_articles(paths: Paths, config: SiteConfig) -> list[Article]:
    """扫描 en/ 与 zh/，按 slug 配对，按配置排序，并分配颜色。

    颜色在排序**之后**分配：卡片在页面上的先后就是颜色的分配依据，
    因此换排序方向时颜色会跟着重排，而不是错位。
    """
    en_slugs = _slugs_in(paths.en_dir)
    zh_slugs = _slugs_in(paths.zh_dir)

    articles = [
        Article(
            slug=slug,
            zh=_load_side("zh", slug, paths),
            en=_load_side("en", slug, paths),
        )
        for slug in sorted(en_slugs | zh_slugs)
    ]

    reverse = config.order_direction == "newest-first"
    articles.sort(key=lambda a: (a.zh.sort_key, a.en.sort_key, a.slug), reverse=reverse)

    assignment = allocate_palette(
        [a.slug for a in articles], config.palette, config.palette_pinned
    )
    for article in articles:
        article.color_index = assignment[article.slug]

    return articles
