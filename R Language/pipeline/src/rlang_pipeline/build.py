"""构建 index.html 与英文文章阅读页。

设计约束（都是为了"可复现"）：
  - 不访问网络
  - 不读系统时间
  - 不用 random
  - 不读环境变量
同样的输入必定产出逐字节相同的输出，因此可以直接用 git diff 判断有没有变化。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import render
from .articles import (
    Article,
    encode_repo_path,
    english_pages_url,
    english_repo_url,
    load_articles,
)
from .config import SiteConfig
from .paths import Paths


class BuildError(RuntimeError):
    pass


@dataclass
class BuildResult:
    index_path: Path
    article_pages: list[Path]
    article_count: int
    written: bool


def _require_jinja():
    try:
        import jinja2
    except ImportError as exc:  # pragma: no cover
        raise BuildError(
            "渲染需要 Jinja2。请安装：\n"
            "    uv sync            （在本目录运行）\n"
            "或  pip install jinja2"
        ) from exc
    return jinja2


def _make_env(templates_dir: Path):
    jinja2 = _require_jinja()
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(templates_dir)),
        autoescape=jinja2.select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    # 模板里用到的自定义过滤器
    env.filters["urlpath"] = encode_repo_path
    return env


def _card_context(article: Article, config: SiteConfig) -> dict:
    """把一篇文章整理成模板需要的扁平结构。

    链接缺失时给 None，模板会渲染成不可点的占位按钮 ——
    绝不用空字符串拼出一个 href="" 的死链。
    """
    return {
        "slug": article.slug,
        "en_title": article.display_en_title,
        "zh_title": article.display_zh_title,
        "en_url": english_repo_url(config, article.slug) if article.has_english else None,
        "zh_url": article.zh.zhihu_link or None,
        "color_classes": article.color(config).tailwind_classes,
    }


def build_index(
    paths: Paths, config: SiteConfig, *, dry_run: bool = False
) -> tuple[str, int, list[Article]]:
    """渲染 index.html，返回 (内容, 文章数, 文章列表)。"""
    articles = load_articles(paths, config)
    if not articles:
        raise BuildError(
            f"在 {paths.en_dir} 和 {paths.zh_dir} 下都没有找到任何文章。\n"
            "每篇文章应位于 <lang>/<slug>/index.md。"
        )

    env = _make_env(paths.templates_dir)
    template = env.get_template("index.html.j2")

    card_css = (paths.templates_dir / "card.css").read_text(encoding="utf-8")

    html = template.render(
        site=config,
        articles=[_card_context(a, config) for a in articles],
        card_css=card_css,
        pending_label=config.pending_label,
    )

    if not dry_run:
        paths.site_output.write_text(html, encoding="utf-8", newline="\n")

    return html, len(articles), articles


def build_article_pages(
    paths: Paths,
    config: SiteConfig,
    articles: list[Article],
    *,
    dry_run: bool = False,
) -> list[Path]:
    """把每篇英文 Markdown 渲染成 en/<slug>/index.html。

    中文不参与这一步 —— 它不进 Pages 产物。
    """
    env = _make_env(paths.templates_dir)
    template = env.get_template("article.html.j2")
    article_css = (paths.templates_dir / "article.css").read_text(encoding="utf-8")
    pyg_css = render.pygments_css()

    written: list[Path] = []
    for article in articles:
        if not article.en.exists:
            continue

        body = render.clean_body(article.en.body)
        content = render.render_markdown(body)

        # 返回站点首页的相对前缀。
        # 不能按 "slug 里有几段" 算 —— 文章页实际位于
        #     <content_dir>/en/<slug>/index.html
        # 相对仓库根（= Pages 根）要回退「目录段数 + 1」层。
        depth = len(paths.article_dir("en", article.slug).relative_to(paths.repo_root).parts)
        root_prefix = "../" * depth

        html = template.render(
            title=article.display_en_title,
            content=content,
            article_css=article_css,
            pygments_css=pyg_css,
            has_math=render.has_math(body),
            root_prefix=root_prefix,
            home_label=config.title,
            footer_left=article.zh.title or "",
            source_url=english_repo_url(config, article.slug),
            source_label="View source on GitHub",
        )

        out = paths.article_dir("en", article.slug) / "index.html"
        if not dry_run:
            out.write_text(html, encoding="utf-8", newline="\n")
        written.append(out)

    return written


def build_all(paths: Paths, config: SiteConfig, *, dry_run: bool = False) -> BuildResult:
    html, count, articles = build_index(paths, config, dry_run=dry_run)
    pages = build_article_pages(paths, config, articles, dry_run=dry_run)
    return BuildResult(
        index_path=paths.site_output,
        article_pages=pages,
        article_count=count,
        written=not dry_run,
    )


def site_manifest(paths: Paths, config: SiteConfig) -> dict:
    """给调试用的站点清单。不写盘，由 CLI 决定要不要输出。"""
    articles = load_articles(paths, config)
    return {
        "site_title": config.title,
        "repo": config.repo_base_url,
        "article_count": len(articles),
        "articles": [
            {
                "slug": a.slug,
                "en_title": a.display_en_title,
                "zh_title": a.display_zh_title,
                "zhihu_link": a.zh.zhihu_link,
                "github_url": english_repo_url(config, a.slug),
                "pages_url": english_pages_url(a.slug),
                "color": a.color(config).tailwind_classes,
                "created_at": a.zh.created_at,
                "en_exists": a.en.exists,
                "zh_exists": a.zh.exists,
                "remote_images": len(a.en.remote_image_refs) + len(a.zh.remote_image_refs),
                "local_assets": len(a.en.local_asset_refs) + len(a.zh.local_asset_refs),
            }
            for a in articles
        ],
    }
