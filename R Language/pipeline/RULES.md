# Rule layers: what to hardcode, what to delegate

> This document answers one question: **which things need to be uniform, and what mechanism enforces them.**
>
> The single criterion: **if a mature tool can guarantee it mechanically, do not write your own rule; write your own only when judging it requires understanding the content.**

---

## 1. Three layers

| Layer | Mechanism | Guarantees | Why here |
| --- | --- | --- | --- |
| **Format** | `markdownlint-cli2` | Blank lines around headings, fences and lists; list-marker spacing; trailing whitespace; hard tabs; repeated blank lines; final newline | Purely mechanical and unambiguous. A hand-written rule set will always miss cases. |
| **Semantic** | `rlang_pipeline check` | Title prefixes, frontmatter fields, image existence, slug uniqueness, artifact isolation, index freshness | Requires knowing *what kind of article this is*. A generic linter cannot decide it. |
| **Interface** | Fixed commands | Subcommand names, exit codes, status constants | These are program contracts. Changing them breaks callers. |

---

## 2. Format layer: delegated to markdownlint

### Configuration

Everything lives in [`.markdownlint-cli2.jsonc`](../../.markdownlint-cli2.jsonc) at the repository root.
One file, used by the CLI, by local runs, and by CI — no second copy.

```bash
npx markdownlint-cli2          # check
npx markdownlint-cli2 --fix    # fix what is fixable
```

### Rules deliberately disabled

| Rule | Why disabled |
| --- | --- |
| `MD013` line length | Conflicts with the existing content style; wrapping prose at 80 columns would churn every article for no gain |
| `MD041`, `MD025` first-line heading | These files start with frontmatter, not a heading |
| `MD033` inline HTML | Occasionally needed |
| `MD036` emphasis as heading | The author uses bold lead-ins deliberately |
| `MD045` image alt text | Low value here; the images are figures already described by surrounding prose |

### Rules deliberately kept

`MD022`, `MD031`, `MD032` (blank lines around headings, fences, lists), `MD012`
(repeated blank lines), `MD030` (list-marker spacing), `MD009` (trailing spaces),
`MD010` (hard tabs), `MD047` (final newline), `MD046`/`MD048` (fence style).

### One rule that had to be changed rather than kept or dropped

`MD029` defaults to lazy numbering, which rewrites an ordered list `1. 2. 3.` into
`1. 1. 1.`. Rendering is equivalent but the source wording is altered for no reason.
It is set to `"style": "ordered"`.

### Scope: article sources only

- Applied to: `R Language/en/**/index.md`, `R Language/zh/**/index.md`
- **Not** applied to: `index.html`, `en/**/index.html` (artifacts), templates, CSS,
  and the root documents (`README.md`, `AGENTS.md`, `ARCHITECTURE.md`), which carry
  the author's voice — `MD026` would strip the trailing periods from their headings

### Why not Prettier

- Prettier needs Node; this pipeline is pure Python managed by `uv`
- markdownlint-cli2 is the tool actually in use, and one linter is enough
- If a frontend toolchain arrives later, Prettier can be added for other languages,
  but Markdown should keep a single source of truth to avoid two tools fighting

---

## 3. Semantic layer: written by hand, because tools cannot do it

| Rule | Level | Auto-fixable |
| --- | --- | --- |
| English title starts with `【R Language】` | error | yes (prepend prefix) |
| Chinese title starts with `【R 语言】` | error | yes (prepend prefix) |
| The two prefixes are not swapped | error | yes |
| Required frontmatter fields present | error | no (a missing date needs a human) |
| `zhihu-link` shaped like `https://zhuanlan.zhihu.com/p/\d+` | error | no |
| Every local image reference resolves | error | no |
| Slugs are globally unique | error | no |
| `index.html` matches the current content | error | yes (run `build`) |
| No `.html` file under `zh/` | error | no |
| No pipeline source under `en/` | error | no |
| Image paths relative, never absolute | error | no |
| Date in `YYYY-MM-DD HH:MM` form | error | yes when unambiguous |
| Code-fence language correct | warn | yes |
| Count of remote image references | info | no |

**Levels**

- `error` — `check` exits non-zero and blocks the commit
- `warn` — printed, exit code stays 0
- `info` — statistics only

---

## 4. What to hardcode, what to move into configuration

The easiest thing to get wrong. The rule is: **hardcode contracts, configure facts.**

| Kind | Treatment | Examples |
| --- | --- | --- |
| **Program contract** (hardcode) | Changing it breaks callers | Subcommand names `build`/`check`/`import`; exit codes 0/1/2; the `PREFIX_EN`/`PREFIX_ZH` constants; frontmatter key names |
| **Site facts** (→ `site.toml`) | Unrelated to code, and they change | Palette, repository URL, column URL, button labels, sort direction |
| **Article facts** (→ frontmatter) | Different per article | Title, Zhihu link, publish time |
| **Source mapping** (→ `vault-map.toml`) | Used only during migration | Note paths, old filenames, canonical title overrides |

**Counter-examples that really existed in this repository**

- 36 article titles and links written into `generate_combined_cards.py` → belong in frontmatter
- The absolute path `d:\PythonDirectory\知乎\` → should be derived from the file location
- The article count `9` hardcoded → should come from scanning directories
- The 12 palette values duplicated in two generators → belong in `site.toml`, one source

**A correct example**

- `PREFIX_EN = "【R Language】"` in code is right: it is a layout contract, not an article fact

---

## 5. Why neither `random` nor the system clock

They are banned because they destroy **reproducibility**, and reproducibility is the
foundation every verification method here rests on:

- With `random`, the same input builds differently twice, so `git diff index.html` means nothing
- With timestamps, every build produces noise, so it is impossible to tell what a change affected

Replacements:

- Need a value that varies but stays recognizable (colors) → allocate it deterministically
  across the sorted article list, pinned for published articles
- Need "the current time" → do not put it in the artifact. Time is content; it belongs in frontmatter

---

## 6. Where each mechanism lives

| Mechanism | Location |
| --- | --- |
| Linter configuration | [`.markdownlint-cli2.jsonc`](../../.markdownlint-cli2.jsonc) |
| Format check | `npx markdownlint-cli2`, also run from the `check` subcommand |
| Semantic checks | `cmd_check` in [`cli.py`](src/rlang_pipeline/cli.py) |
| Palette allocation | `allocate_palette` in [`config.py`](src/rlang_pipeline/config.py) |
| Site facts | [`site.toml`](site.toml) |
| Source mapping | [`vault-map.toml`](vault-map.toml) |
