"""一次性迁移：把旧布局的内容搬进 en/<slug>/index.md 与 zh/<slug>/index.md。

旧的英文文章是平铺的 `R Language/【R Language】X.md`，没有 frontmatter，
中英文靠人工维护的下标顺序配对。这里把它换成显式 slug 配对。

映射数据（哪篇文章对应哪个笔记、知乎链接、发布时间）全部来自
`pipeline/vault-map.toml`，本文件不含任何文章级字面量，也不含绝对路径。

幂等：目标已存在时跳过；`--redo-zh` 可强制重做中文侧。

用法：
    uv run python -m rlang_pipeline.migrate --check
    uv run python -m rlang_pipeline.migrate
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from . import frontmatter as fm
from . import normalize
from .paths import Paths, get_paths
from .slug import strip_export_suffix

MIGRATE_CONFIG = "vault-map.toml"


# ---------------------------------------------------------------------------
# 配置装载
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Pair:
    slug: str
    en_old: str
    zhihu_link: str
    created_at: str
    zh_source: str
    topic: str = "R"
    zh_md: str = ""
    note: str = ""


@dataclass(frozen=True)
class MigrateConfig:
    vault_root: Path
    canonical_zh_titles: dict[str, str]
    pairs: list[Pair]


def _detect_vault_root(start: Path, markers: list[str]) -> Path | None:
    """从 start 逐级向上找含任一 marker 的目录。"""
    for candidate in [start, *start.parents]:
        if any((candidate / m).exists() for m in markers):
            return candidate
    return None


def resolve_vault_root(paths: Paths, raw: dict, cli_value: str | None) -> Path:
    """解析 Obsidian 库根。

    顺序：命令行 → 环境变量 → 配置里的 root → 自动探测。
    绝不把个人机器的绝对路径写进代码。
    """
    for label, value in (
        ("--vault-root", cli_value),
        ("环境变量 RLANG_VAULT_ROOT", os.environ.get("RLANG_VAULT_ROOT")),
        ("vault-map.toml 的 [vault].root", raw.get("root") or None),
    ):
        if value:
            candidate = Path(value).expanduser().resolve()
            if not candidate.is_dir():
                raise SystemExit(f"{label} 指向的目录不存在：{candidate}")
            return candidate

    markers = raw.get("markers", [".obsidian", ".rlang-vault-root"])
    probe_bases = raw.get("probe_from", ["."])
    for rel in probe_bases:
        base = (paths.repo_root / rel).resolve()
        if not base.is_dir():
            continue
        found = _detect_vault_root(base, markers)
        if found is not None:
            return found

    raise SystemExit(
        "无法自动定位 Obsidian 库根。请任选一种方式指定：\n"
        "  1) 命令行：uv run python -m rlang_pipeline.migrate --vault-root <路径>\n"
        "  2) 环境变量：$env:RLANG_VAULT_ROOT = '<路径>'\n"
        f"  3) 在 {MIGRATE_CONFIG} 的 [vault].root 里填写"
    )


def load_migrate_config(paths: Paths, cli_vault_root: str | None) -> MigrateConfig:
    config_path = paths.pipeline_dir / MIGRATE_CONFIG
    if not config_path.exists():
        raise SystemExit(f"找不到迁移配置：{config_path}")

    with config_path.open("rb") as fh:
        raw = tomllib.load(fh)

    vault_root = resolve_vault_root(paths, raw.get("vault", {}), cli_vault_root)

    pairs = [
        Pair(
            slug=item["slug"],
            en_old=item.get("en_old", ""),
            zhihu_link=item.get("zhihu_link", ""),
            created_at=item.get("created_at", ""),
            zh_source=item["zh_source"],
            topic=item.get("topic", "R"),
            zh_md=item.get("zh_md", ""),
            note=item.get("note", ""),
        )
        for item in raw.get("article", [])
    ]

    if not pairs:
        raise SystemExit(f"{config_path} 里没有任何 [[article]] 条目")

    return MigrateConfig(
        vault_root=vault_root,
        canonical_zh_titles=raw.get("canonical_zh_titles", {}),
        pairs=pairs,
    )


# ---------------------------------------------------------------------------
# 迁移
# ---------------------------------------------------------------------------


@dataclass
class MigrateReport:
    migrated_en: list[str] = field(default_factory=list)
    migrated_zh: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    images: int = 0
    fences: int = 0


def _strip_leading_heading(body: str, candidates: list[str]) -> str:
    """去掉正文开头那个与标题重复的一级/二级标题。"""
    lines = body.split("\n")
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx >= len(lines):
        return body
    match = re.match(r"^#{1,3}\s+(.*?)\s*$", lines[idx])
    if not match:
        return body
    heading = re.sub(r"\s+", " ", match.group(1)).strip()
    for candidate in candidates:
        if candidate and re.sub(r"\s+", " ", candidate).strip() == heading:
            return "\n".join(lines[idx + 1:]).lstrip("\n")
    return body


def _title_from_source(parsed: fm.Frontmatter, source_file: Path) -> tuple[str, str]:
    """推断中文标题，返回 (标题, 来源说明)。

    优先级（重要）：
      1. frontmatter 的 zhihu-title —— 权威值
      2. 文件名 —— Obsidian 的笔记名就是发布标题（"【R 语言】匿名函数.md"）
      3. 正文第一个标题 —— 最后手段，很可能抓到的是小节标题而不是文章标题

    第 2 条排在第 3 条前面是有意的：这个库里正文的第一个标题经常是
    「定义函数」这种小节名，直接拿来当文章标题会错得很难看。
    """
    title = str(parsed.data.get("zhihu-title", "")).strip()
    if title:
        return title, "frontmatter"

    return strip_export_suffix(source_file.stem), "文件名"


def _resolve_zh_source(vault_root: Path, pair: Pair) -> tuple[Path, Path] | None:
    """定位中文源，返回 (md 文件, 所在目录)。"""
    raw = vault_root / pair.zh_source
    if raw.is_file():
        return raw, raw.parent
    if raw.is_dir():
        md_name = pair.zh_md or f"{raw.name}.md"
        candidate = raw / md_name
        if candidate.is_file():
            return candidate, raw
    return None


def migrate_en(paths: Paths, pair: Pair, *, dry_run: bool, report: MigrateReport) -> None:
    target_dir = paths.article_dir("en", pair.slug)
    target_md = paths.article_markdown("en", pair.slug)

    if target_md.exists():
        report.skipped.append(f"en/{pair.slug}（已存在）")
        return

    if not pair.en_old:
        report.skipped.append(f"en/{pair.slug}（无英文源，待翻译）")
        return

    source = paths.content_dir / pair.en_old
    if not source.is_file():
        report.warnings.append(f"英文源缺失：{pair.en_old}")
        return

    parsed = fm.parse(source.read_text(encoding="utf-8"))
    en_title = Path(pair.en_old).stem.strip()
    body = _strip_leading_heading(parsed.body, [en_title])

    data = {"slug": pair.slug, "zhihu-link": pair.zhihu_link}
    if en_title:
        data["en-title"] = en_title
    if pair.created_at:
        data["zhihu-created-at"] = pair.created_at

    text = fm.dump(data, body, key_order=["en-title", "slug", "zhihu-link", "zhihu-created-at"])

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        target_md.write_text(text, encoding="utf-8", newline="\n")
    report.migrated_en.append(pair.slug)


def migrate_zh(
    paths: Paths,
    pair: Pair,
    config: MigrateConfig,
    *,
    dry_run: bool,
    redo: bool,
    report: MigrateReport,
) -> None:
    target_dir = paths.article_dir("zh", pair.slug)
    target_md = paths.article_markdown("zh", pair.slug)

    # 重做时不再"把文章目录改名藏起来"做备份 ——
    # 那样一旦中途异常，文章就从目录里消失、被当成已删除，
    # 而且改名后的目录会被当成一篇文章混进产物。
    #
    # 改成：把已有 assets/ 复制到一个点开头的隐藏目录做备份。
    #   1. 点开头 → articles._slugs_in 本就跳过它，不会被误当成文章
    #   2. 不移动正文 → 异常时正文仍在原位
    #   3. 重做成功后删除备份
    backup_dir: Path | None = None
    if redo and not dry_run and (target_dir / "assets").is_dir():
        backup_dir = target_dir / ".assets-backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(target_dir / "assets", backup_dir)

    if target_md.exists() and not redo:
        report.skipped.append(f"zh/{pair.slug}（已存在）")
        return

    located = _resolve_zh_source(config.vault_root, pair)
    if located is None:
        report.warnings.append(f"中文源缺失：{config.vault_root / pair.zh_source}")
        return
    source_file, source_dir = located

    parsed = fm.parse(source_file.read_text(encoding="utf-8"))
    title, how = _title_from_source(parsed, source_file)

    # 权威覆盖表优先于源码 frontmatter
    override = config.canonical_zh_titles.get(pair.slug)
    if override:
        if override != title:
            report.warnings.append(
                f"zh/{pair.slug}: 源码标题 {title!r} 与线上不一致，改用线上标题 {override!r}"
            )
        title, how = override, "线上标题覆盖表"

    # 强制补齐语言前缀（【R 语言】/【R Language】），不依赖人工每次记得写
    title, prefixed = normalize.enforce_title_prefix(title, "zh")
    if prefixed:
        report.warnings.append(f"zh/{pair.slug}: 标题已规范为 {title!r}")

    if how != "线上标题覆盖表":
        report.warnings.append(f"zh/{pair.slug}: 中文标题取自{how} → {title!r}")

    if not pair.created_at:
        report.warnings.append(
            f"zh/{pair.slug}: zhihu-created-at 未知，已留空，"
            f"请在 {MIGRATE_CONFIG} 的 created_at 里补（格式 2025-10-14 15:11）"
        )

    body = _strip_leading_heading(parsed.body, [title])
    assets = paths.article_assets("zh", pair.slug)

    # 先落标题，再走归一化。
    # normalize_markdown 的 extra_frontmatter 只在原值为空时才填充，
    # 所以覆盖权威标题必须发生在它之前，否则会被源码 frontmatter 里的旧值挡住。
    seed_data = dict(parsed.data)
    seed_data["zhihu-title"] = title
    seed_data["zhihu-link"] = pair.zhihu_link

    new_text, sub_report = normalize.normalize_markdown(
        fm.dump(seed_data, body, key_order=[]),
        md_dir=source_dir,
        assets_dir=assets,
        lang="zh",
        vault_root=config.vault_root,
        copy_images=not dry_run,
        extra_frontmatter={"zhihu-topics": pair.topic, "zhihu-created-at": pair.created_at},
        existing_assets_dir=backup_dir if backup_dir is not None else target_dir,
    )

    report.images += sub_report.images_rewritten
    report.fences += sub_report.fences_fixed
    for missing in sorted(set(sub_report.images_missing)):
        report.warnings.append(f"zh/{pair.slug}: 找不到图片 {missing}")

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        target_md.write_text(new_text, encoding="utf-8", newline="\n")

        # 从备份里补回本轮没能重新搬运的图片（仅当目标缺失时）
        if backup_dir is not None and backup_dir.is_dir():
            new_assets = target_dir / "assets"
            for src in backup_dir.iterdir():
                if not src.is_file():
                    continue
                new_assets.mkdir(parents=True, exist_ok=True)
                dst = new_assets / src.name
                if not dst.exists():
                    shutil.copy2(src, dst)
            shutil.rmtree(backup_dir, ignore_errors=True)

    report.migrated_zh.append(pair.slug)


def run(
    paths: Paths,
    config: MigrateConfig,
    *,
    dry_run: bool = False,
    redo: bool = False,
) -> MigrateReport:
    report = MigrateReport()
    for pair in config.pairs:
        migrate_en(paths, pair, dry_run=dry_run, report=report)
        migrate_zh(paths, pair, config, dry_run=dry_run, redo=redo, report=report)
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="把旧布局内容迁移到 en/<slug>/ 与 zh/<slug>/",
        epilog="库根解析顺序：--vault-root → 环境变量 RLANG_VAULT_ROOT "
               "→ vault-map.toml 的 [vault].root → 自动探测",
    )
    parser.add_argument("--vault-root", default=None,
                        help="Obsidian 库根；不传则自动探测")
    parser.add_argument("--check", action="store_true", help="只报告，不写盘")
    parser.add_argument("--redo-zh", action="store_true",
                        help="删掉 zh/<slug>/ 重新生成（用于修正标题等推断错误）")
    parser.add_argument("--cleanup-old", action="store_true",
                        help="迁移完成后删除 R Language/ 下旧的平铺英文 md")
    args = parser.parse_args(argv)

    paths = get_paths()
    config = load_migrate_config(paths, args.vault_root)
    report = run(paths, config, dry_run=args.check, redo=args.redo_zh)

    print()
    print(f"{'（推演）' if args.check else ''}迁移结果")
    print("─" * 40)
    print(f"  库根       {config.vault_root}")
    print(f"  英文迁入   {len(report.migrated_en)}")
    for slug in report.migrated_en:
        print(f"      en/{slug}")
    print(f"  中文迁入   {len(report.migrated_zh)}")
    for slug in report.migrated_zh:
        print(f"      zh/{slug}")
    if report.skipped:
        print(f"  跳过       {len(report.skipped)}")
        for item in report.skipped:
            print(f"      {item}")
    print(f"  图片落盘   {report.images}")
    print(f"  代码块修正 {report.fences}")
    if report.warnings:
        print(f"  警告       {len(report.warnings)}")
        for item in report.warnings:
            print(f"      ! {item}")

    if args.cleanup_old and not args.check:
        removed = 0
        for pair in config.pairs:
            if not pair.en_old:
                continue
            old = paths.content_dir / pair.en_old
            if old.is_file():
                old.unlink()
                removed += 1
        print(f"  已删除旧平铺英文 md {removed} 个")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
