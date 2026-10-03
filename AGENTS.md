# Mine — maintenance index

> This file is the **rules and dashboard**, injected automatically at session start.
> Usage and overview belong in [README.md](README.md); rationale belongs in [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Global rules

- **Chinese is never published**: `R Language/zh/` is an archive only — it must not enter the
  Pages artifact and must not appear in `index.html`
- **Title prefixes are enforced**: English `【R Language】`, Chinese `【R 语言】`, applied by
  `enforce_title_prefix()`. Do not rely on remembering to type them.
- **Never hand-edit an artifact**: `index.html` and `en/<slug>/index.html` are generated.
  Change the template or the data, then rebuild.
- **Frontmatter is the only data source**: an article's title and links are read from the YAML
  in its `index.md`. Nowhere else may hold a second copy.
- **No absolute paths**: every path is derived in [paths.py](R%20Language/pipeline/src/rlang_pipeline/paths.py)
- **No `random`, no system clock**: builds must be reproducible so `git diff index.html`
  reflects content changes exactly
- **Documentation is English**, with one exception: `README_zh.md` is the Chinese README.
  Both READMEs carry a language switcher directly under the H1.
- **Commit messages are English**

---

## Commands

From `R Language/pipeline/`:

```bash
uv sync                                       # set up the environment (first time only)
uv run python -m rlang_pipeline build         # regenerate index.html and the reading pages
uv run python -m rlang_pipeline check         # semantic validation
uv run python -m rlang_pipeline import <md>   # import a new article's Chinese source
uv run pytest -q                              # unit tests
```

From the repository root:

```bash
npx markdownlint-cli2          # check article formatting
npx markdownlint-cli2 --fix    # fix blank lines and list markers
```

The rule layers are described in [RULES.md](R%20Language/pipeline/RULES.md).

---

## Verification snapshot

- Deployment: [Deploy R Language column to Pages](https://github.com/zlZayn/mine/actions/workflows/static.yml)
  (badge in [README.md](README.md))
- Live site: <https://zlzayn.github.io/mine/> — 11 cards, byte-identical to the local artifact
- `check` 0 FAIL · `pytest` 110 passed · `markdownlint` 14 findings (strict rules, non-blocking)

---

## TODO

- [ ] The remaining 14 markdownlint findings are mostly `MD025` (multiple H1) and `MD040`
      (fence without a language). The directory-tree fence is **intentionally untagged**;
      do not force it.

---

## Deliberately outside the repository

The following are kept **outside** the repository on purpose. See [.gitignore](.gitignore).

| Location | Contents |
| --- | --- |
| `D:\PythonDirectory\_archive_mine\` | Source of both retired pipelines, original Zhihu exports |
| `D:\PythonDirectory\_知乎_legacy_backup_20261003\` | Scrape leftovers from the first pipeline (saved web pages) |

An `_archive/` directory once existed inside the repository; it was removed on request.
`.gitignore` now guards against re-adding it.

---

## Active pitfalls

In the order they were hit. Each one corresponds to a real failure.

- **Image filenames contain spaces and parentheses** (`Lorenz Curve.png`, `unnest().png`).
  The regex must allow one level of balanced parentheses **and must not exclude spaces**:
  `(?:<([^>]+)>|((?:[^()]|\([^()]*\))+))`.
  Three wrong versions were tried: `[^)\s]+` truncates names containing spaces;
  `(?:[^()\s]|\([^()]*\))+` also excludes spaces; `[^)]+` stops at the first `)` and
  truncates `unnest()` to `unnest(`.
- **Zhihu exports label R code as `ada` and Rust code as `text`**.
  Normalization sniffs the content and corrects it. Note that `|>` can appear mid-line,
  so it must not be anchored to end-of-line.
- **The frontmatter title can drift from the published title** (`mice`, `broom`).
  [vault-map.toml](R%20Language/pipeline/vault-map.toml)'s `canonical_zh_titles` is authoritative.
- **`enforce_title_prefix` cannot use "is the bare title empty" to mean "has no prefix"**.
  A title consisting only of a prefix also yields an empty bare title, and the two meanings
  colliding silently ate real titles. The function therefore returns a triple:
  `(bare title, canonical prefix, had_prefix)`.
- **Tailwind's CDN JIT scans for literal class names**.
  The palette stores complete strings such as `from-red-300 to-red-600`; templates must never
  build class names by interpolation.
- **markdownlint's defaults change things they should not**.
  `MD029` defaults to lazy numbering and rewrites `1. 2. 3.` into `1. 1. 1.`
  (set `"style": "ordered"`); `MD026` strips trailing periods from headings.
  Scope was narrowed to `R Language/{en,zh}`, excluding the root documents, which carry the
  author's voice.
- **A migration backup must not rename the article directory**.
  `<slug>.__stash__` was used as a backup; when an error path skipped the restore, the article
  vanished and the leftover directory was picked up as an extra article. It now copies
  `assets/` into `.assets-backup/` inside the article directory instead.
- **Hover must never change any size**.
  `:hover { height: .75rem }` grew the gradient bar, which grew the card, which forced CSS Grid
  to recompute the row and pushed every card below it down. Hover feedback may only use
  `transform` and `box-shadow`, which do not participate in layout.
- **A card must not use a fixed `height`**.
  A fixed height does not error when the title wraps; it silently deforms the content.
  `margin-top: auto` cannot push the buttons down, so on long-title cards the buttons sit flush
  against the title while short-title cards have them at the bottom. Use `min-height`: long
  titles grow the card and Grid equalizes heights within a row.

---

## Documentation map

- What the site is, and how to enter it → [README.md](README.md) · [README_zh.md](README_zh.md)
- Design decisions and invariants → [ARCHITECTURE.md](ARCHITECTURE.md)
- Pipeline usage → [R Language/pipeline/README.md](R%20Language/pipeline/README.md)
- Rule layers: what to hardcode vs configure → [R Language/pipeline/RULES.md](R%20Language/pipeline/RULES.md)
- Test coverage → [R Language/pipeline/tests/README.md](R%20Language/pipeline/tests/README.md)
- Site and build configuration → [R Language/pipeline/site.toml](R%20Language/pipeline/site.toml)
- Article source mapping → [R Language/pipeline/vault-map.toml](R%20Language/pipeline/vault-map.toml)
