"""内容归一化：把原始 Markdown 整理成入库标准形态。

处理三类历史遗留问题：
  1. Obsidian 的 ![[图片.png]] 引用 → 标准 Markdown ![](assets/xxx.png)，图片落盘到 assets/
  2. 知乎导出的代码块语言标注错误（R 代码被标成 ```ada，Rust 代码被标成 ```text）
  3. frontmatter 缺失或字段不全
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from . import frontmatter as fm
from .slug import slugify

# ---- 图片引用 ----
_WIKI_IMG_RE = re.compile(r"!\[\[([^\]|]+?)(?:\|[^\]]*)?\]\]")
# 目标里可以含空格，也可以含一层配对括号（"unnest().png"）。
# 两种情况都真实存在于本仓库，不能用 [^)\s]+ 粗暴截断。
# 路径可含空格（"assets/Lorenz Curve.png"）与配对括号（"assets/unnest().png"）。
# 见 articles.py 的同类正则说明：允许一层配对括号，且不能排除空格。
_MD_IMG_DEST = r"(?:<([^>]+)>|((?:[^()]|\([^()]*\))+))"
_MD_IMG_RE = re.compile(r"(!\[[^\[\]]*\]\()" + _MD_IMG_DEST + r"(\))")

# ---- 代码块语言 ----
_ZHIHU_WRONG_LANGS = {"ada", "text", "plain", "plaintext", ""}

# 语言嗅探规则，按顺序匹配，先命中先用
_LANG_RULES: list[tuple[str, list[re.Pattern]]] = [
    (
        "rust",
        [
            re.compile(r"^\s*(use|pub use)\s+\w+::"),
            re.compile(r"#\[extendr\]"),
            re.compile(r"\bfn\s+\w+\s*\([^)]*\)\s*->"),
            re.compile(r"\bextendr_module!\s*\{"),
            re.compile(r"\bimpl\s+\w+\s*\{"),
        ],
    ),
    (
        "r",
        [
            re.compile(r"^\s*library\("),
            re.compile(r"^\s*require\("),
            re.compile(r"<-\s*(function|tibble|ggplot|lm|read|data\.frame)"),
            # R 的管道符可以出现在行中，不能锚定行尾：
            # "models |> map(glance)" 就是单行写法。
            re.compile(r"\|\>"),
            re.compile(r"^\s*(mutate|summarise|summarize|select|filter|arrange|pivot_|unnest|map|ggplot|aes)\("),
        ],
    ),
    (
        "toml",
        [
            re.compile(r"^\s*\[(dependencies|package|lib|features|\[)"),
            re.compile(r"^\s*\w+\s*=\s*\{.*\}\s*$"),
        ],
    ),
    (
        "bash",
        [
            re.compile(r"^\s*(rustup|cargo|git|cd|ls|mkdir|python|pip|uv)\s"),
        ],
    ),
]

# ``` 之后直接被识别为"这是 R 代码"的强信号
_STRONG_R = [
    re.compile(r"^\s*library\((tidyverse|dplyr|ggplot2|broom|mice|tidymodels|rextendr)\b"),
    re.compile(r"\|\>"),
    re.compile(r"<-\s*function\s*\("),
]

# R 的弱信号。单行 `devtools::document()` 这种既不命中强信号、也没有函数定义，
# 只能靠这些：包内函数调用、R 的注释输出标记、字符串赋值、独占一行的函数调用。
_R_HINTS = [
    re.compile(r"^\s*[a-zA-Z][\w.]*::[\w.]+\(", re.MULTILINE),   # pkg::fun(
    re.compile(r"(?m)^\s*#\s*\[1\]"),                            # R 控制台输出
    re.compile(r"^\s*\w+\s*<-\s*[\"']", re.MULTILINE),           # x <- "字符串"
    re.compile(r"^\s*\w+\s*<-\s*\w+\(", re.MULTILINE),           # x <- fun(
    # 独占一行的「标识符(...)」语句。
    #
    # 不做括号平衡校验 —— 正则表达不了嵌套（`ma_rust(c(1,2,3), 3)` 就配不上），
    # 而这里也不需要严格：目录树已在上一步被排除，散文里出现
    # 「行首标识符紧跟左括号」的概率极低。宁可多标一个高亮，也不要漏标。
    re.compile(r"^\s*[a-zA-Z_][\w.]*\(", re.MULTILINE),
    re.compile(r"\bn\s*\(\s*\)"),                                # n() 计数
]

# 明显是目录树 / 文件清单的块：保留无高亮，标了反而难看
_TREE_HINT = re.compile(r"[├└]──|^[A-Za-z0-9_.\-]+/$", re.MULTILINE)

_STRONG_RUST = [
    re.compile(r"#\[extendr\]"),
    re.compile(r"\bextendr_module!\s*\{"),
    re.compile(r"^\s*use\s+extendr_api"),
]


@dataclass
class NormalizeReport:
    changed: bool = False
    images_rewritten: int = 0
    images_missing: list[str] = field(default_factory=list)
    fences_fixed: int = 0
    frontmatter_filled: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def detect_language(code: str, current: str) -> str:
    """判断一个代码块应该标什么语言。

    current 是原标记；只有原标记明显是错的（知乎的 ada / text）才会去猜，
    已经标成 r / rust / bash 等的一律尊重原样。
    """
    current = current.strip().lower()
    if current not in _ZHIHU_WRONG_LANGS:
        return current

    for pattern in _STRONG_RUST:
        if pattern.search(code):
            return "rust"
    for pattern in _STRONG_R:
        if pattern.search(code):
            return "r"

    for lang, patterns in _LANG_RULES:
        hits = sum(1 for p in patterns if p.search(code))
        if hits >= 1:
            return lang

    # 目录树 / 文件清单：不要标语言，标了反而难看
    if _TREE_HINT.search(code):
        return ""

    # R 的弱信号：单行的 `devtools::document()`、`add_one(5)` 这类
    # 既不命中强信号、也不是别的语言，靠这些兜住。
    if any(p.search(code) for p in _R_HINTS):
        return "r"

    # 猜不出来就留空（渲染成无高亮的代码块，好过标错）
    return ""


def fix_code_fences(body: str, report: NormalizeReport) -> str:
    """修正围栏代码块的语言标注。

    逐行扫描，遇到 ``` 就向后找配对的结束行，把中间内容交给 detect_language 嗅探。
    """
    lines = body.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            info = stripped[3:].strip()
            # 找到配对的结束行
            j = i + 1
            while j < len(lines):
                if lines[j].lstrip().startswith(marker):
                    break
                j += 1
            code = "\n".join(lines[i + 1: j])
            new_lang = detect_language(code, info)
            if new_lang != info.strip():
                report.fences_fixed += 1
            result.append(f"{marker}{new_lang}" if new_lang else marker)
            result.extend(lines[i + 1: j])
            if j < len(lines):
                result.append(lines[j])
                i = j + 1
            else:
                i = j
            continue
        result.append(line)
        i += 1

    return "\n".join(result)


def resolve_obsidian_image(ref: str, md_dir: Path, vault_root: Path | None) -> Path | None:
    """按 Obsidian 的查找顺序解析 ![[...]] 里的图片。

    Obsidian 实际是按文件名索引整个库来找的，这里用有限但可预测的顺序：
      1. 相对于 md 所在目录
      2. 相对于库根
      3. md 同目录 + 仅文件名
      4. 库内按文件名递归查找（慢，但只在前面都失败时才做）
    """
    ref = ref.strip().lstrip("/")
    if not ref:
        return None

    candidates = [md_dir / ref]
    if vault_root is not None:
        candidates.append(vault_root / ref)
    candidates.append(md_dir / Path(ref).name)

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    # 最后一招：按文件名在库内递归找
    if vault_root is not None:
        name = Path(ref).name
        matches = list(vault_root.rglob(name))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            # 有歧义就返回 md 同目录的那个（如果有），否则返回 None 让人工决定
            for m in matches:
                if m.parent == md_dir:
                    return m
            return None
    return None


def localize_images(
    body: str,
    md_dir: Path,
    assets_dir: Path,
    vault_root: Path | None,
    report: NormalizeReport,
    *,
    copy: bool,
    existing_assets_dir: Path | None = None,
) -> str:
    """把图片引用统一成 Markdown 相对路径，并把文件落到 assets/。

    md_dir               源 md 所在目录（用来解析相对引用）
    assets_dir           归一化后 assets/ 的位置
    existing_assets_dir  归一化后的 md 所在目录；若引用已经是 assets/xxx
                         就到这里去找，而不是去源目录找。
                         （重跑归一化时源 md 可能已被改写过，这一步是必需的）
    """
    resolved: dict[str, Path | None] = {}

    def handle_wiki(match: re.Match) -> str:
        ref = match.group(1).strip()
        if ref.startswith(("http://", "https://")):
            return f"![]({ref})"

        if ref not in resolved:
            resolved[ref] = resolve_obsidian_image(ref, md_dir, vault_root)
        source = resolved[ref]

        if source is None:
            report.images_missing.append(ref)
            return f"![]({ref})"

        target_name = source.name
        if copy:
            assets_dir.mkdir(parents=True, exist_ok=True)
            dest = assets_dir / target_name
            if source.resolve() != dest.resolve():
                shutil.copy2(source, dest)
        report.images_rewritten += 1
        return f"![](assets/{target_name})"

    body = _WIKI_IMG_RE.sub(handle_wiki, body)

    # 已经是 Markdown 形式的本地相对引用：能落盘就统一收进 assets/
    def handle_md(match: re.Match) -> str:
        prefix, bracketed, balanced, suffix = match.groups()
        target = (bracketed or balanced or "").strip()
        if not target or target.startswith(("http://", "https://", "data:")):
            return match.group(0)

        # 已经指向 assets/ 的：在「归一化后的 md 目录」里确认，
        # 而不是源目录 —— 源 md 可能早被改写过。
        if target.startswith("assets/"):
            probe_dirs = [d for d in (existing_assets_dir, md_dir) if d is not None]
            if not any((d / target).is_file() for d in probe_dirs):
                report.images_missing.append(target)
            return match.group(0)

        # 指向 plots/ 之类的其他相对路径：把文件收进 assets/ 并改写引用
        source = md_dir / target
        if not source.is_file():
            alt = md_dir / Path(target).name
            if alt.is_file():
                source = alt
            elif existing_assets_dir is not None and (
                existing_assets_dir / "assets" / Path(target).name
            ).is_file():
                # 上一轮已经收进 assets/ 了，无需重复搬运
                return f"{prefix}assets/{Path(target).name}{suffix}"
            else:
                report.images_missing.append(target)
                return match.group(0)

        name = source.name
        if copy:
            assets_dir.mkdir(parents=True, exist_ok=True)
            dest = assets_dir / name
            if source.resolve() != dest.resolve():
                shutil.copy2(source, dest)
        report.images_rewritten += 1
        return f"{prefix}assets/{name}{suffix}"

    return _MD_IMG_RE.sub(handle_md, body)


def normalize_markdown(
    text: str,
    *,
    md_dir: Path,
    assets_dir: Path,
    lang: str,
    vault_root: Path | None = None,
    copy_images: bool = True,
    extra_frontmatter: dict | None = None,
    existing_assets_dir: Path | None = None,
) -> tuple[str, NormalizeReport]:
    """归一化一篇 Markdown，返回 (新内容, 报告)。"""
    report = NormalizeReport()
    parsed = fm.parse(text)

    if not parsed.had_block:
        report.frontmatter_filled.append("(整个 frontmatter 缺失)")

    data = dict(parsed.data)
    if extra_frontmatter:
        for key, value in extra_frontmatter.items():
            if value and not str(data.get(key, "")).strip():
                data[key] = value
                report.frontmatter_filled.append(key)

    body = localize_images(
        parsed.body,
        md_dir,
        assets_dir,
        vault_root,
        report,
        copy=copy_images,
        existing_assets_dir=existing_assets_dir,
    )
    body = fix_code_fences(body, report)

    if data != parsed.data:
        report.changed = True
    if report.images_rewritten or report.fences_fixed:
        report.changed = True

    if not parsed.had_block and not data:
        # 完全没有 frontmatter 也没有补充信息，保持原样，不要凭空造一个空块
        return body, report

    key_order = (
        ["zhihu-title", "zhihu-topics", "zhihu-link", "zhihu-created-at"]
        if lang == "zh"
        else ["en-title", "slug", "zhihu-link", "zhihu-created-at"]
    )
    return fm.dump(data, body, key_order=key_order), report


def suggest_slug(title: str) -> str:
    return slugify(title)


# ---------------------------------------------------------------------------
# 标题前缀约定
#
#   英文侧标题一律以 【R Language】 开头
#   中文侧标题一律以 【R 语言】   开头
#
# index.html 上的每张卡片都是「【R Language】… / 【R 语言】…」两行，
# 这个前缀是版式的一部分，不是可选装饰。
# 因此在这里强制收口：任何进入流水线的标题都会被补齐前缀，
# 而不是靠人每次记得写。
# ---------------------------------------------------------------------------

PREFIX_EN = "【R Language】"
PREFIX_ZH = "【R 语言】"

# 所有被认为"等价于标准前缀"的写法，统一收敛到标准形式。
# 用 fullmatch 语义匹配「前缀 + 任意剩余内容」，因此这里不带 ^，
# 并且开启 IGNORECASE —— 否则 "r language" 这类写法会漏掉。
_PREFIX_ALIASES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\s*【\s*R\s+Language\s*】\s*", re.IGNORECASE), PREFIX_EN),
    (re.compile(r"\s*\[\s*R\s+Language\s*\]\s*", re.IGNORECASE), PREFIX_EN),
    (re.compile(r"\s*R\s+Language\s*[:：]\s*", re.IGNORECASE), PREFIX_EN),
    (re.compile(r"\s*【\s*R\s*语言\s*】\s*"), PREFIX_ZH),
    (re.compile(r"\s*\[\s*R\s*语言\s*\]\s*"), PREFIX_ZH),
    (re.compile(r"\s*【\s*R\s*語言\s*】\s*"), PREFIX_ZH),
    (re.compile(r"\s*R\s*语言\s*[:：]\s*"), PREFIX_ZH),
]

# 前缀识别用：在标题开头处匹配「前缀 + 其余全部内容」
_PREFIX_PROBE = re.compile(
    r"(?P<prefix>"
    r"【\s*R\s+Language\s*】|\[\s*R\s+Language\s*\]|R\s+Language\s*[:：]"
    r"|【\s*R\s*语言\s*】|\[\s*R\s*语言\s*\]|【\s*R\s*語言\s*】|R\s*语言\s*[:：]"
    r")(?P<rest>.*)$",
    re.IGNORECASE | re.DOTALL,
)

_PREFIX_CANONICAL = {
    "language": PREFIX_EN,
    "语言": PREFIX_ZH,
    "語言": PREFIX_ZH,
}


def strip_title_prefix(title: str) -> tuple[str, str, bool]:
    """剥掉标题上的语言前缀。

    返回 (裸标题, 标准前缀, 是否本来就有前缀)。

    **第三个返回值是必需的**：不能用"裸标题是空串"来表示"没有前缀"，
    因为「【R Language】」这种只有前缀没有内容的标题，剥完裸标题也是空串，
    两者会混淆，结果就是把真正的标题当成前缀丢掉。

    >>> strip_title_prefix("【R Language】Anonymous Functions")
    ('Anonymous Functions', '【R Language】', True)
    >>> strip_title_prefix("【R语言】匿名函数")
    ('匿名函数', '【R 语言】', True)
    >>> strip_title_prefix("broom Package for Tidy Modeling")
    ('broom Package for Tidy Modeling', '', False)
    """
    text = (title or "").strip()
    match = _PREFIX_PROBE.match(text)
    if not match:
        return text, "", False

    prefix = match.group("prefix")
    rest = match.group("rest").strip()

    is_en = bool(re.search(r"language", prefix, re.IGNORECASE))
    canonical = PREFIX_EN if is_en else PREFIX_ZH

    return rest, canonical, True


def enforce_title_prefix(title: str, lang: str) -> tuple[str, bool]:
    """把标题规范成带标准前缀的形式。

    返回 (规范后的标题, 是否发生了改动)。

    >>> enforce_title_prefix("broom Package for Tidy Modeling", "en")
    ('【R Language】broom Package for Tidy Modeling', True)
    >>> enforce_title_prefix("【R语言】匿名函数", "zh")
    ('【R 语言】匿名函数', True)
    >>> enforce_title_prefix("【R Language】Anonymous Functions", "en")
    ('【R Language】Anonymous Functions', False)
    """
    title = (title or "").strip()
    canonical = PREFIX_EN if lang == "en" else PREFIX_ZH

    if not title:
        return "", False

    bare, existing, had_prefix = strip_title_prefix(title)

    if not had_prefix:
        # 完全没有前缀 → 补上
        return f"{canonical}{title}", True

    if not bare:
        # 只有前缀、没有正文：保留原标题，不要造出一个空标题
        return title, False

    # 已有前缀（可能是别名写法）→ 收敛到标准写法
    normalized = f"{canonical}{bare}"
    return normalized, normalized != title
