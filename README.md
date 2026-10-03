# Mine

[English](README.md) | [简体中文](README_zh.md)

> A cozy little nook for my content and knowledge.
> May they always stay here where I can see them, and never get lost.

**Browse the site: [zlzayn.github.io/mine](https://zlzayn.github.io/mine/)**

---

## What this is

A personal repository that doubles as a static site.
Articles are written in Chinese on Zhihu first, then translated into English and archived here.

The index page links to both versions:
the English Markdown lives in this repository, the Chinese original lives on Zhihu.

---

## What's inside

### `R Language/` — the column

| Path | Holds |
| --- | --- |
| `en/<slug>/index.md` | English article (source on GitHub, rendered page on the site) |
| `en/<slug>/assets/` | Images for that article |
| `zh/<slug>/index.md` | Chinese article, archived here but **never published** |
| `en/<slug>/index.html` | Generated reading page |
| `pipeline/` | The toolchain that builds the site |

Every article is a directory named by its `slug`.
The same slug on both sides is what pairs the English and Chinese versions.

### `tools/` — browser utilities

Small single-file HTML tools, unrelated to the article pipeline.

---

## How the site is built

`index.html` is a **generated artifact** — never edit it by hand.

```
Markdown frontmatter  ──build──▶  index.html + en/<slug>/index.html
```

The pipeline is pure Python (`uv`-managed) and runs with **no network access**:
everything it needs is in the repository.

```bash
cd "R Language/pipeline"
uv sync                                        # first time only
uv run python -m rlang_pipeline build          # regenerate index.html
uv run python -m rlang_pipeline check          # validate content
uv run python -m rlang_pipeline import <file>  # add a new article
```

Content rules live in [pipeline/RULES.md](R%20Language/pipeline/RULES.md);
design decisions live in [ARCHITECTURE.md](ARCHITECTURE.md).

---

## License and contributions

Personal project — no license granted, no contributions expected.
Feel free to read and learn from the code.

Maintainer notes and the documentation map live in [AGENTS.md](AGENTS.md).
