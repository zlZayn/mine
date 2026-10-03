# Mine — architecture

This repository is shaped as *content plus one pipeline*: `index.html` is the artifact,
Markdown is the data source, and `R Language/pipeline/` is the only machine.

---

## 1. Goals

1. Adding an article touches content only, never code.
2. `index.html` can always be rebuilt in full from the content, with no manual patching.
3. Both languages are archived; the Chinese version is never published, it points at Zhihu.
4. Builds are reproducible: identical input produces byte-identical output.

---

## 2. Data flow

```
Obsidian note / Zhihu export
        │  import  (normalize: frontmatter, copy images, code-fence language)
        ▼
R Language/zh/<slug>/index.md ──┐
                                │  paired by slug
English translation (human or AI-assisted)
        ▼                       │
R Language/en/<slug>/index.md ──┴──► build ──► index.html           (index cards)
                                         └───► en/<slug>/index.html (English reading page)
                                                   │
                                                   ▼  workflow whitelist
                                             GitHub Pages (index.html + en/ only)
```

---

## 3. Invariants

Breaching any of these is a bug, not a style choice.

| Invariant | Why | What breaking it causes |
| --- | --- | --- |
| `slug` is the only pairing key | The old pipeline paired by index (`_1` with `_1`), silently misaligning whenever the two sides disagreed on order | English and Chinese titles land on the wrong cards |
| No network during build | Data must come from Markdown inside the repository | CI depends on external sites; their next redesign breaks the build |
| No `random`, no system clock | The output carries no timestamps, so `git diff` reflects content changes exactly | Every build produces a meaningless diff |
| Tailwind class names must be literal | The CDN JIT scans source text; interpolated class names are never seen | Card gradients silently stop rendering |
| Colors come from an allocation over the sorted list, pinned for published articles | Assigning purely by recency makes every later card change color when an article is inserted | Published pages shift color |
| Chinese never enters the Pages artifact | The Chinese version points at Zhihu; Chinese prose should not appear on the site | Conflicts with the publishing policy |
| Title prefixes enforced by code | Relying on memory guarantees omissions | Card layout becomes inconsistent |
| Missing data fails loudly | The old pipeline printed "success" after matching zero items and produced an empty page | Broken pages ship silently |

---

## 4. Key decisions

### 1. Frontmatter as the database

- Chinese side: `zhihu-title`, `zhihu-link`, `zhihu-created-at` drive the card's Chinese
  title, the Zhihu button, and the sort order
- English side: `en-title` drives the card's English title
- There is no "article list" file; the list is the directory scan

**Alternative considered:** maintain an `articles.yml` manifest.
**Rejected because:** the manifest and the frontmatter would drift apart, violating
"one home per fact".

### 2. The directory *is* the identity

`en/<slug>/index.md` and `zh/<slug>/index.md`, with `assets/` beside `index.md` so image
references are relative and resolve in the repository, in Obsidian, and on Pages alike.

**Alternative considered:** `en/<slug>.md` with a global `en/assets/`.
**Rejected because:** a global asset directory collides on duplicate filenames and erases
which images belong to which article.

### 3. The Pages artifact mirrors the repository

`_site/R Language/en/<slug>/index.html` matches the repository path, so the
`../../../index.html` relative link in an article page works both locally and on the live site.

**Alternative considered:** flatten `en/` to the site root.
**Rejected because:** the relative-link depth would then depend on the environment, forcing
the build to branch on it — fragile.

### 4. Whitelist, not whole-repository upload

The old workflow used `path: '.'`, which packed the entire repository — Chinese content,
source code, configuration — into publicly downloadable static files. The workflow now
uploads `index.html` plus `R Language/en/` only, and CI asserts that the artifact contains
no Chinese and no pipeline source.

### 5. Normalization is separate from the build

- `normalize.py` handles dirty source data: Obsidian image syntax, Zhihu's wrong
  code-fence languages, missing frontmatter
- `build.py` only reads structured data and renders; it never touches dirty input

**Reason:** normalization is a one-off chore, while the build runs on every change. Mixing
them lets the dirt leak back into the build path.

---

## 5. Guardrails

- Run `check` after adding an article. A missing translation, a missing publish date,
  a missing image, or a stale `index.html` are all caught.
- `check` validates title prefixes (`【R Language】` / `【R 语言】`) and the shape of the Zhihu link.
- `check` verifies that no `.html` file has appeared under `zh/`.
- Before deploying, the workflow compares `index.html` against the content and fails rather
  than silently publishing a stale page.
- After localizing images, confirm they landed: `assets/` under `zh/` is the single source of truth.

---

## 6. Known boundaries

- The repository is public, so the **sources** under `zh/` remain visible on GitHub.
  "Not published" means precisely: absent from the Pages artifact and from `index.html`.
- Chinese is allowed inside English prose in two cases: identifier names inside inline code,
  and the titles of Chinese-language references. Translating either would make the text
  harder to search, not easier to read.
- Images hosted on the Zhihu CDN stay as remote links (cross-origin hotlinking was measured
  to work); localizing them is not forced.
