"""构建产物的一致性测试。

这是**回归守卫**：`index.html` 是产物，任何非预期的变化都应当被这里拦下。

守卫方式：重新构建一次（不写盘）并与已提交的 `index.html` 逐字符比对。
失败时说明「内容变了但 index.html 没重建」，或者「构建不再可复现」。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from rlang_pipeline.articles import english_pages_url, english_repo_url, load_articles
from rlang_pipeline.build import build_index
from rlang_pipeline.config import load_site_config
from rlang_pipeline.paths import get_paths

PATHS = get_paths()
CONFIG = load_site_config(PATHS.site_config)


def test_repo_root_discovered():
    """路径解析必须从文件位置反推，不能依赖当前工作目录。"""
    assert (PATHS.repo_root / ".git").exists()
    assert PATHS.site_config.is_file()
    assert PATHS.templates_dir.is_dir()


def test_articles_load():
    articles = load_articles(PATHS, CONFIG)
    assert len(articles) >= 11
    for article in articles:
        assert article.slug
        assert not article.slug.startswith(".")


def test_index_matches_content():
    """已提交的 index.html 必须与当前内容一致。"""
    expected, count, _ = build_index(PATHS, CONFIG, dry_run=True)
    actual = PATHS.site_output.read_text(encoding="utf-8")
    assert actual == expected, (
        "index.html 与内容不一致。请运行：\n"
        "    uv run python -m rlang_pipeline build"
    )
    assert count >= 11


def test_build_is_deterministic():
    """连续两次构建必须逐字节相同（无 random、无时间戳）。"""
    first, _, _ = build_index(PATHS, CONFIG, dry_run=True)
    second, _, _ = build_index(PATHS, CONFIG, dry_run=True)
    assert first == second


def test_colors_are_literal_tailwind_classes():
    """色板必须产出完整类名，不能让模板插值拼接。

    Tailwind CDN 的 JIT 按字面量扫源码，插值出来的类名扫不到、颜色会失效。
    """
    articles = load_articles(PATHS, CONFIG)
    for article in articles:
        classes = article.color(CONFIG).tailwind_classes
        assert classes.startswith("from-")
        assert " to-" in classes
        assert "{" not in classes and "}" not in classes


def test_color_assignment_is_pinned():
    """已发布文章的配色是回归基线，不得漂移。"""
    pinned = {
        "anonymous-functions": "from-red-300 to-red-600",
        "a-workflow-based-on-nested-data-frames": "from-orange-300 to-orange-600",
        "all-subsets-regression-based-on-broom-package": "from-amber-300 to-amber-600",
        "plotting-known-functions-with-ggplot2": "from-emerald-300 to-emerald-600",
        "mice-package-for-multiple-imputation-and-batch-modeling": "from-teal-300 to-teal-600",
        "nonlinear-least-squares-and-linear-models": "from-blue-300 to-blue-600",
        "chi-square-distribution-and-convolution-effect": "from-violet-300 to-violet-600",
        "lorenz-curve-and-gini-index": "from-purple-300 to-purple-600",
        "broom-package-for-tidy-modeling": "from-pink-300 to-pink-600",
    }
    by_slug = {a.slug: a for a in load_articles(PATHS, CONFIG)}
    for slug, expected in pinned.items():
        assert slug in by_slug, f"文章缺失：{slug}"
        assert by_slug[slug].color(CONFIG).tailwind_classes == expected


class TestUrls:
    def test_english_repo_url_shape(self):
        url = english_repo_url(CONFIG, "broom-package-for-tidy-modeling")
        assert url.startswith("https://github.com/zlZayn/mine/blob/main/")
        assert url.endswith("/index.md")
        # 中文与空格必须被编码
        assert " " not in url

    def test_english_repo_url_encodes_cjk_slug(self):
        url = english_repo_url(CONFIG, "【R 语言】测试")
        assert "【" not in url
        assert "%E3%80%90" in url

    def test_pages_url_shape(self):
        assert english_pages_url("broom-package-for-tidy-modeling") == (
            "broom-package-for-tidy-modeling/index.html"
        )


def test_no_chinese_leaks_into_index():
    """index.html 上只应有中文**标题**，不应有中文正文或 frontmatter 键。"""
    html = PATHS.site_output.read_text(encoding="utf-8")

    # frontmatter 的键名不应出现在产物里。
    # 必须锚定行首：CSS 选择器 ".zhihu-link:hover" 里含 "zhihu-link:" 子串，
    # 用裸子串判断会误报。
    for key in ("zhihu-title", "zhihu-link", "zhihu-created-at", "en-title", "slug"):
        assert not re.search(rf"^{re.escape(key)}:", html, re.MULTILINE), (
            f"产物中检出 frontmatter 键 {key}:"
        )

    # 不应引用任何本地 assets/ 图片（卡片上只有 R logo 一个外链图标）
    assert 'src="assets/' not in html
    assert "](assets/" not in html


def test_chinese_dir_has_no_html():
    """zh/ 下不允许出现 html —— 那是中文泄漏进 Pages 的征兆。"""
    leaked = list(PATHS.zh_dir.rglob("*.html"))
    assert leaked == [], f"zh/ 下出现 html：{leaked}"


def test_english_dir_has_no_pipeline_files():
    """en/ 是发布内容，不许混入流水线源码或配置。"""
    for pattern in ("*.py", "site.toml", "vault-map.toml", "*.j2"):
        stray = list(PATHS.en_dir.rglob(pattern))
        assert stray == [], f"en/ 下混入 {pattern}：{stray}"


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_every_article_dir_has_index_md(lang):
    base = PATHS.en_dir if lang == "en" else PATHS.zh_dir
    if not base.exists():
        pytest.skip(f"{base} 不存在")
    for child in base.iterdir():
        if not child.is_dir() or child.name.startswith((".", "_")):
            continue
        assert (child / "index.md").is_file(), f"{child} 缺 index.md"


def test_index_html_exists():
    assert isinstance(PATHS.site_output, Path)
    assert PATHS.site_output.is_file()
