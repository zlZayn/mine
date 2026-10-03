"""路径解析。

所有路径都从本文件位置反推，禁止在任何地方写绝对路径。
包结构:  <repo>/R Language/pipeline/src/rlang_pipeline/paths.py
             ↑3      ↑4       ↑5        ↑6      ↑7
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def _find_repo_root() -> Path:
    """从本文件向上找到含 .git 的目录；找不到就退化为包目录上溯 7 层。"""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            return parent
    return here.parents[6]


@dataclass(frozen=True)
class Paths:
    repo_root: Path
    pipeline_dir: Path
    templates_dir: Path
    src_dir: Path
    site_config: Path

    @property
    def content_dir(self) -> Path:
        """R Language/ ——单个专栏的根。"""
        return self.pipeline_dir.parent

    @property
    def en_dir(self) -> Path:
        return self.content_dir / "en"

    @property
    def zh_dir(self) -> Path:
        return self.content_dir / "zh"

    @property
    def site_output(self) -> Path:
        """index.html 落地位置（仓库根，GitHub Pages 入口）。"""
        return self.repo_root / "index.html"

    def article_dir(self, lang: str, slug: str) -> Path:
        base = self.en_dir if lang == "en" else self.zh_dir
        return base / slug

    def article_markdown(self, lang: str, slug: str) -> Path:
        return self.article_dir(lang, slug) / "index.md"

    def article_assets(self, lang: str, slug: str) -> Path:
        return self.article_dir(lang, slug) / "assets"


def get_paths() -> Paths:
    pipeline_dir = Path(__file__).resolve().parents[2]
    return Paths(
        repo_root=_find_repo_root(),
        pipeline_dir=pipeline_dir,
        templates_dir=pipeline_dir / "templates",
        src_dir=pipeline_dir / "src",
        site_config=pipeline_dir / "site.toml",
    )
