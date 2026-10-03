# R Language column — publishing pipeline

Turns the YAML frontmatter of Markdown files into `index.html`.

**Division of responsibility, in one line:**
> `R Language/en/` and `R Language/zh/` are content, `R Language/pipeline/` is the machine, `index.html` is the artifact.

---

## 1. Layout

```
mine/
├── index.html                      ← artifact; the only entry page, never hand-edit
└── R Language/                     ← one self-contained "column" block
    ├── en/<slug>/                  ← English original (source on GitHub, rendered page on Pages)
    │   ├── index.md
    │   ├── assets/                 ← local images, if any
    │   └── index.html              ← artifact: rendered reading page
    ├── zh/<slug>/                  ← Chinese archive (in the repo only, never on Pages)
    │   ├── index.md
    │   └── assets/
    └── pipeline/                   ← the pipeline itself
        ├── site.toml               ← the only place site facts may be written
        ├── vault-map.toml          ← where each article came from
        ├── pyproject.toml
        ├── templates/
        │   ├── index.html.j2       ← index page template
        │   ├── article.html.j2     ← English reading page template
        │   ├── card.css
        │   └── article.css
        └── src/rlang_pipeline/
            ├── paths.py            ← path resolution (derived from file location, no absolute paths)
            ├── config.py           ← site.toml loading, validation, palette allocation
            ├── frontmatter.py      ← YAML frontmatter read/write
            ├── slug.py             ← slug generation
            ├── articles.py         ← article model and pairing
            ├── normalize.py        ← content normalization (images, code fences, frontmatter)
            ├── render.py           ← Markdown → HTML
            ├── build.py            ← produces index.html and reading pages
            ├── migrate.py          ← one-off migration (not needed once it has run)
            └── cli.py              ← command-line entry point
```

---

## 2. Data source: frontmatter

### Chinese side, `zh/<slug>/index.md`

```yaml
---
zhihu-title: 【R 语言】broom 包进行整洁建模    # Chinese title shown on index.html
zhihu-topics: R
zhihu-link: https://zhuanlan.zhihu.com/p/1949603330578953873   # the "中文-知乎" button
zhihu-created-at: 2025-09-11 22:51            # sort key
---
```

### English side, `en/<slug>/index.md`

```yaml
---
en-title: 【R Language】broom Package for Tidy Modeling   # English title on the card
slug: broom-package-for-tidy-modeling
zhihu-link: https://zhuanlan.zhihu.com/p/1949603330578953873
zhihu-created-at: 2025-09-11 22:51
---
```

### Pairing rule

**`slug` is the pairing key.** Two directories with the same name are the same article.

This replaces the old scheme of pairing by position (`_1` with `_1`), which silently
misaligned whenever the Zhihu list order and the GitHub filename order disagreed.

---

## 3. Everyday use

Run everything from `R Language/pipeline/`.

```bash
# First-time setup
uv sync

# 1) Import the Chinese source of a new article.
#    The source may be a Zhihu export (filename ends with -落日阳红的文章) or an Obsidian note.
uv run python -m rlang_pipeline import "D:\ObsidianDirectory\zhihu\some-article-落日阳红的文章.md"

#    It will: normalize the frontmatter, copy images into zh/<slug>/assets/,
#             fix code-fence languages, and scaffold en/<slug>/index.md for translation.

# 2) Once the English translation is written, rebuild.
uv run python -m rlang_pipeline build

# 3) Validate. Missing fields, missing images, a stale index.html, or Chinese
#    leaking onto Pages are all caught here.
uv run python -m rlang_pipeline check
```

Debugging helpers:

```bash
uv run python -m rlang_pipeline paths        # how each directory resolved
uv run python -m rlang_pipeline manifest     # site manifest as JSON
uv run python -m rlang_pipeline slug "Title" # what slug a title would produce
```

---

## 4. Design constraints, and why

| Constraint | Reason |
| --- | --- |
| **No network during build** | Nothing is scraped from Zhihu or GitHub. All data comes from Markdown in the repository. |
| **No `random`** | Colors come from the pinned table in `site.toml`; unregistered articles get one allocated without clashing with their neighbours. An article's color never changes. |
| **No system clock** | The output carries no timestamps, so `git diff index.html` reflects content changes exactly. |
| **No absolute paths** | Every path is derived in `paths.py`. Works on another machine, username, or drive letter. |
| **No scraper-style regex** | The old pipeline read data through external site class names such as `data-za-detail-view_element_name="Title"`, which broke on any redesign. |
| **Missing data must fail, not fall back** | The old `link_extractor_*.py` printed "success" after matching zero links. Now `check` fails and names what is missing. |
| **Tailwind class names must be literal** | The `cdn.tailwindcss.com` JIT scans source text for literal class names. Writing `from-{{ color }}-300` in a template produces classes it never sees, and the color silently disappears. The palette therefore stores complete strings such as `from-red-300 to-red-600`. |

---

## 5. Content conventions

### Images

- After normalization every reference is `![](assets/file.png)`, with the file beside it in `assets/`
- Filenames containing spaces (`Lorenz Curve.png`) and parentheses (`unnest().png`) are both supported
- References to the Zhihu CDN (`https://pic*.zhimg.com/...`) are **kept as remote links** —
  zhimg was measured to allow cross-origin hotlinking, and the images load fine from both
  GitHub and Pages

### Code-fence languages

Zhihu exports label R code as ` ```ada ` and Rust code as ` ```text `.
Normalization sniffs the content and corrects it to `r`, `rust`, `toml`, or `bash`.
When nothing is recognized the tag is left empty — an unhighlighted block is better than a wrong one.

### Chinese is never published

- Markdown under `zh/` never takes part in the Pages build
- `build_article_pages()` only processes the English side
- `.github/workflows/static.yml` uploads a whitelist of paths, not the whole repository
- `check` verifies that no `.html` file has appeared under `zh/`

The repository is public, so the **sources** under `zh/` remain visible on GitHub.
"Not published" means: absent from the Pages artifact, and absent from `index.html`.
