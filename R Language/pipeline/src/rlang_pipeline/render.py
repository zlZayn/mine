"""Markdown → HTML 渲染。

只用于**英文**文章（中文不进 Pages 产物）。
用 python-markdown + Pygments；若二者缺失，由调用方给出可执行的修复提示。
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, unquote, urlparse

_ZHIHU_REDIRECT_RE = re.compile(
    r"https?://link\.zhihu\.com/\?target=([^)\s\"']+)"
)

# 需要数学公式时才注入 MathJax，避免每篇文章都多两个网络请求
_MATH_HINT_RE = re.compile(r"\$\$?[^$\n]+\$\$?|\\\(|\\\[|\\begin\{")


class RenderError(RuntimeError):
    pass


def _require_markdown():
    try:
        import markdown  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise RenderError(
            "渲染英文文章需要 python-markdown。请安装：\n"
            "    uv sync            （在本目录运行）\n"
            "或  pip install markdown pygments"
        ) from exc
    return markdown


def decode_zhihu_redirect(url: str) -> str:
    """把知乎的外链跳转还原成真实地址。

    https://link.zhihu.com/?target=https%3A//broom.tidymodels.org/
        → https://broom.tidymodels.org/
    """
    parsed = urlparse(url)
    if parsed.netloc.endswith("link.zhihu.com"):
        params = parse_qs(parsed.query)
        target = params.get("target", [None])[0]
        if target:
            return unquote(target)
    return url


def clean_body(body: str) -> str:
    """正文预处理。

    1. 去掉 Obsidian 的图片尺寸后缀（![[a.png|300]] → ![[a.png]]）
    2. 还原知乎外链跳转
    3. 顺手清掉知乎粘贴时留下的零宽字符
    """
    # 1) Obsidian wiki 图片的 |尺寸 后缀
    body = re.sub(r"!\[\[([^\]|]+)\|[^\]]*\]\]", r"![[\1]]", body)

    # 2) 知乎跳转链接
    body = _ZHIHU_REDIRECT_RE.sub(
        lambda m: decode_zhihu_redirect(f"https://link.zhihu.com/?target={m.group(1)}"),
        body,
    )

    # 3) 零宽字符
    for ch in ("\u200b", "\u200c", "\u200d", "\ufeff"):
        body = body.replace(ch, "")

    return body


def has_math(body: str) -> bool:
    return bool(_MATH_HINT_RE.search(body))


def render_markdown(body: str) -> str:
    markdown = _require_markdown()

    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "attr_list",
            "sane_lists",
            "codehilite",
            "md_in_html",
        ],
        extension_configs={
            "codehilite": {
                "guess_lang": False,
                "css_class": "highlight",
                "linenums": False,
            }
        },
        output_format="html5",
    )
    return md.convert(body)


def pygments_css() -> str:
    """Pygments 的代码高亮样式。取不到就返回空串（页面仍可读）。"""
    try:
        from pygments.formatters import HtmlFormatter

        return HtmlFormatter(style="friendly").get_style_defs(".highlight")
    except Exception:
        return ""
