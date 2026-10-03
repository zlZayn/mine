"""命令行入口。

    uv run python -m rlang_pipeline <子命令>

子命令：
    import    把 Obsidian 里的中文 Markdown 导入仓库（归一化 + 图片落盘）
    build     重新生成 index.html 与英文文章阅读页
    check     完整性体检（缺字段/缺文件/图缺失/index 过期）
    manifest  输出站点清单 JSON（调试用）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import __version__, normalize
from .articles import (
    EN_KEY_ORDER,
    EN_REQUIRED,
    ZH_KEY_ORDER,
    ZH_REQUIRED,
    encode_repo_path,
    english_pages_url,
    english_repo_url,
    load_articles,
)
from .build import BuildError, build_all, build_index, site_manifest
from .config import ConfigError, load_site_config
from .paths import get_paths
from .slug import slugify

# ---------------------------------------------------------------------------
# 输出小工具
# ---------------------------------------------------------------------------

_USE_COLOR = sys.stdout.isatty()


def _paint(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def ok(msg: str) -> None:
    print(f"{_paint('  OK  ', '32')} {msg}")


def warn(msg: str) -> None:
    print(f"{_paint(' WARN ', '33')} {msg}")


def bad(msg: str) -> None:
    print(f"{_paint(' FAIL ', '31')} {msg}")


def info(msg: str) -> None:
    print(f"       {msg}")


def head(msg: str) -> None:
    print()
    print(_paint(msg, '1'))
    print(_paint("─" * max(20, len(msg)), '2'))


# ---------------------------------------------------------------------------
# 仓库根标记：让图片解析知道"库根"在哪
# ---------------------------------------------------------------------------

VAULT_MARKER = ".rlang-vault-root"


def _vault_root_for(source_file: Path) -> Path | None:
    """推断 Obsidian 库根，用于解析 ![[R/xxx/aaa.png]] 这类库内相对路径。

    优先用同目录或上层的 .rlang-vault-root 标记文件，
    其次向上找 .obsidian / AGENTS.md，最后退化为源文件所在目录。
    """
    for parent in [source_file.parent, *source_file.parents]:
        if (parent / VAULT_MARKER).is_file():
            return parent

    for parent in [source_file.parent, *source_file.parents]:
        if (parent / ".obsidian").is_dir() or (parent / "AGENTS.md").is_file():
            return parent

    return source_file.parent


# ---------------------------------------------------------------------------
# import
# ---------------------------------------------------------------------------


def _resolve_source(path_str: str) -> Path:
    source = Path(path_str).expanduser()
    if not source.is_absolute():
        source = (Path.cwd() / source).resolve()
    if not source.is_file():
        raise SystemExit(f"找不到源文件：{source}")
    return source


def _title_from_source(text: str, source: Path) -> str:
    """从文件内容或文件名推断中文标题。"""
    parsed = normalize.fm.parse(text)
    title = str(parsed.data.get("zhihu-title", "")).strip()
    if title:
        return title

    # 正文里第一个 ## 标题
    match = re.search(r"(?m)^#{1,3}\s+(.+?)\s*$", parsed.body)
    if match:
        return match.group(1).strip()

    # 文件名：去掉知乎导出的后缀
    stem = source.stem
    for suffix in ("-落日阳红的文章", "-知乎", "_知乎"):
        stem = stem.replace(suffix, "")
    return stem.strip()


def cmd_import(args: argparse.Namespace) -> int:
    paths = get_paths()
    config = load_site_config(paths.site_config)

    source = _resolve_source(args.file)
    text = source.read_text(encoding="utf-8")

    title = _title_from_source(text, source)
    # 强制补齐中文标题前缀，约定不靠人记
    title, prefixed = normalize.enforce_title_prefix(title, "zh")
    if prefixed:
        warn(f"标题已规范为 {title!r}")
    slug = args.slug or slugify(title)

    zh_dir = paths.article_dir("zh", slug)
    zh_md = paths.article_markdown("zh", slug)
    assets = paths.article_assets("zh", slug)

    if zh_md.exists() and not args.force:
        bad(f"目标已存在：{zh_md.relative_to(paths.repo_root)}")
        info("要覆盖请加 --force")
        return 1

    vault_root = _vault_root_for(source)

    # 补齐知乎导出件缺失的字段
    parsed = normalize.fm.parse(text)
    extra: dict[str, str] = {"zhihu-title": title}
    link = str(parsed.data.get("zhihu-link", "")).strip()
    if link:
        extra["zhihu-link"] = link
    if not str(parsed.data.get("zhihu-topics", "")).strip():
        extra["zhihu-topics"] = args.topic
    if not str(parsed.data.get("zhihu-created-at", "")).strip():
        extra["zhihu-created-at"] = args.created_at

    new_text, report = normalize.normalize_markdown(
        text,
        md_dir=source.parent,
        assets_dir=assets,
        lang="zh",
        vault_root=vault_root,
        copy_images=True,
        extra_frontmatter=extra,
    )

    zh_dir.mkdir(parents=True, exist_ok=True)
    zh_md.write_text(new_text, encoding="utf-8", newline="\n")

    head("导入完成")
    ok(f"slug      {slug}")
    ok(f"中文标题  {title}")
    ok(f"落盘      {zh_md.relative_to(paths.repo_root)}")
    info(f"库根推断  {vault_root}")
    if report.images_rewritten:
        ok(f"图片落盘  {report.images_rewritten} 张 → assets/")
    if report.fences_fixed:
        ok(f"代码块语言修正 {report.fences_fixed} 处")
    for fieldname in report.frontmatter_filled:
        warn(f"frontmatter 补写了 {fieldname}（请核对）")
    for missing in sorted(set(report.images_missing)):
        bad(f"找不到图片：{missing}")

    # 同步生成英文侧骨架，避免忘记建目录
    en_dir = paths.article_dir("en", slug)
    en_md = paths.article_markdown("en", slug)
    if not en_md.exists() and not args.no_en_stub:
        en_dir.mkdir(parents=True, exist_ok=True)
        stub_fm = {
            "en-title": args.en_title or "",
            "slug": slug,
        }
        if link:
            stub_fm["zhihu-link"] = link
        if str(parsed.data.get("zhihu-created-at", "")).strip():
            stub_fm["zhihu-created-at"] = str(parsed.data["zhihu-created-at"])
        en_md.write_text(
            normalize.fm.dump(stub_fm, "", key_order=EN_KEY_ORDER),
            encoding="utf-8",
            newline="\n",
        )
        warn(f"已建英文骨架（待翻译）：{en_md.relative_to(paths.repo_root)}")

    return 1 if report.images_missing else 0


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


def cmd_build(args: argparse.Namespace) -> int:
    paths = get_paths()
    config = load_site_config(paths.site_config)

    # 先算一遍但不写盘，好报告"是否有变化"
    before = paths.site_output.read_text(encoding="utf-8") if paths.site_output.exists() else None
    html, count, articles = build_index(paths, config, dry_run=True)
    changed = before != html

    result = build_all(paths, config, dry_run=args.dry_run)

    head("构建完成" if not args.dry_run else "构建预估（--dry-run，未写盘）")
    ok(f"文章数      共 {count} 篇")
    ok(f"index.html  {'有变化，已写入' if changed else '内容无变化'}")
    if not args.dry_run:
        ok(f"英文阅读页  {len(result.article_pages)} 个")
    info(f"输出        {paths.site_output.relative_to(paths.repo_root)}")

    ready = [a for a in articles if a.has_english]
    pending = [a for a in articles if not a.has_english]
    print()
    info(f"已双语（{len(ready)}）：")
    for article in ready:
        info(f"    {article.slug}")
    if pending:
        info(f"待翻译（{len(pending)}）：")
        for article in pending:
            info(f"    {article.slug}")
    return 0


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------


def cmd_check(args: argparse.Namespace) -> int:
    paths = get_paths()
    config = load_site_config(paths.site_config)
    articles = load_articles(paths, config)

    problems: list[str] = []
    warnings: list[str] = []

    head(f"体检：{len(articles)} 篇文章")

    if not articles:
        bad(f"{paths.en_dir} / {paths.zh_dir} 下没有找到任何文章")
        return 1

    seen_slugs: set[str] = set()

    for article in articles:
        tag = article.slug
        if article.slug in seen_slugs:
            problems.append(f"{tag}: slug 重复")
        seen_slugs.add(article.slug)

        # --- 两侧是否存在 ---
        if not article.en.exists:
            problems.append(f"{tag}: 缺英文 index.md（en/{tag}/index.md）")
        if not article.zh.exists:
            warnings.append(f"{tag}: 缺中文 index.md（zh/{tag}/index.md），中文标题与知乎链接将缺失")

        # --- frontmatter 必填字段 ---
        for side in (article.zh, article.en):
            if not side.exists:
                continue
            missing = side.missing_required()
            if missing:
                problems.append(f"{tag} [{side.lang}]: frontmatter 缺 {', '.join(missing)}")

        # --- 标题前缀约定 ---
        #   en 侧必须以 【R Language】 开头，zh 侧必须以 【R 语言】 开头。
        #   这是 index.html 卡片版式的一部分，不允许个别文章例外。
        for side in (article.zh, article.en):
            if not side.exists or not side.title:
                continue
            expected = normalize.PREFIX_EN if side.lang == "en" else normalize.PREFIX_ZH
            if not side.title.startswith(expected):
                problems.append(
                    f"{tag} [{side.lang}]: 标题缺少 {expected} 前缀 → {side.title!r}"
                )

        # --- 两侧标题前缀不应互换（英文标题写成【R 语言】是常见笔误）---
        if article.en.exists and article.en.title.startswith(normalize.PREFIX_ZH):
            problems.append(f"{tag} [en]: 英文标题误用了中文前缀 → {article.en.title!r}")
        if article.zh.exists and article.zh.title.startswith(normalize.PREFIX_EN):
            problems.append(f"{tag} [zh]: 中文标题误用了英文前缀 → {article.zh.title!r}")

        # --- 知乎链接形态 ---
        link = article.zh.zhihu_link
        if link and not re.match(r"^https://zhuanlan\.zhihu\.com/p/\d+$", link):
            warnings.append(f"{tag}: 知乎链接形态可疑 → {link}")

        # --- 日期 ---
        if article.zh.exists and article.zh.sort_key[0] == 1:
            warnings.append(f"{tag}: zhihu-created-at 无法解析 → {article.zh.created_at!r}")

        # --- 本地图片是否存在 ---
        for side in (article.zh, article.en):
            if not side.exists:
                continue
            for ref in side.local_asset_refs:
                target = (side.dir / ref).resolve()
                if not target.is_file():
                    problems.append(
                        f"{tag} [{side.lang}]: 图片引用指向不存在的文件 → {ref}"
                    )

        # --- 远程图片统计（不算错误，只提示）---
        remote = len(article.en.remote_image_refs) + len(article.zh.remote_image_refs)
        if remote:
            warnings.append(
                f"{tag}: 有 {remote} 张图仍指向外部图床（zhimg.com 允许热链，可用）"
            )

    # --- index.html 是否与当前内容一致 ---
    expected, _, _ = build_index(paths, config, dry_run=True)
    actual = paths.site_output.read_text(encoding="utf-8") if paths.site_output.exists() else None
    if actual is None:
        problems.append("index.html 不存在，请运行 build")
    elif actual != expected:
        problems.append("index.html 与当前内容不一致（已过期），请运行 build")

    # --- 产物隔离：中文绝不能进 Pages ---
    leaked = list(paths.content_dir.glob("zh/**/*.html"))
    if leaked:
        problems.append(
            f"zh/ 下出现了 {len(leaked)} 个 html 文件，中文有泄漏进 Pages 的风险"
        )

    # --- 输出 ---
    print()
    if warnings:
        for w in warnings:
            warn(w)
    if problems:
        print()
        for p in problems:
            bad(p)
        print()
        print(_paint(f"{len(problems)} 个问题需要处理", '31'))
        return 1

    print()
    ok("全部检查通过" + (f"（{len(warnings)} 条提示）" if warnings else ""))
    return 0


# ---------------------------------------------------------------------------
# manifest
# ---------------------------------------------------------------------------


def cmd_manifest(args: argparse.Namespace) -> int:
    paths = get_paths()
    config = load_site_config(paths.site_config)
    data = site_manifest(paths, config)
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8", newline="\n")
        ok(f"已写入 {args.out}")
    else:
        print(text)
    return 0


def cmd_paths(args: argparse.Namespace) -> int:
    paths = get_paths()
    head("路径解析")
    ok(f"仓库根     {paths.repo_root}")
    ok(f"专栏目录   {paths.content_dir}")
    ok(f"英文目录   {paths.en_dir}")
    ok(f"中文目录   {paths.zh_dir}")
    ok(f"流水线     {paths.pipeline_dir}")
    ok(f"站点配置   {paths.site_config}")
    ok(f"index 输出 {paths.site_output}")
    return 0


def cmd_slug(args: argparse.Namespace) -> int:
    print(slugify(args.text))
    return 0


# ---------------------------------------------------------------------------
# 参数解析
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rlang-pipeline",
        description="R Language 专栏发布流水线",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_import = sub.add_parser(
        "import",
        help="把 Obsidian 里的中文 Markdown 导入仓库",
        description="归一化中文 Markdown（图片落盘、代码块语言修正、frontmatter 补全）并写入 zh/<slug>/index.md",
    )
    p_import.add_argument("file", help="源 Markdown 路径（知乎导出件或 Obsidian 笔记）")
    p_import.add_argument("--slug", help="指定 slug（默认由标题推导）")
    p_import.add_argument("--topic", default="R", help="zhihu-topics 的值（默认 R）")
    p_import.add_argument("--created-at", default="", help="zhihu-created-at，格式 2025-01-01 12:00")
    p_import.add_argument("--en-title", default="", help="英文标题（可稍后补）")
    p_import.add_argument("--force", action="store_true", help="目标已存在时覆盖")
    p_import.add_argument("--no-en-stub", action="store_true", help="不生成英文骨架")
    p_import.set_defaults(func=cmd_import)

    p_build = sub.add_parser("build", help="重新生成 index.html 与英文阅读页")
    p_build.add_argument("--dry-run", action="store_true", help="只报告不写盘")
    p_build.set_defaults(func=cmd_build)

    p_check = sub.add_parser("check", help="完整性体检")
    p_check.set_defaults(func=cmd_check)

    p_manifest = sub.add_parser("manifest", help="输出站点清单 JSON")
    p_manifest.add_argument("--out", help="写入文件而不是打印")
    p_manifest.set_defaults(func=cmd_manifest)

    p_paths = sub.add_parser("paths", help="打印各目录的解析结果")
    p_paths.set_defaults(func=cmd_paths)

    p_slug = sub.add_parser("slug", help="由标题推算 slug（调试用）")
    p_slug.add_argument("text")
    p_slug.set_defaults(func=cmd_slug)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except (BuildError, ConfigError, normalize.fm.FrontmatterError) as exc:
        print()
        bad(str(exc))
        return 2
    except KeyboardInterrupt:
        print()
        warn("已中断")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
