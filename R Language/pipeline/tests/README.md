# tests/ — what is covered

The point of this suite is **failures that actually happened**, not a coverage number.
Each test traces back to a real breakage.

## Files and their coverage

| File | Covers | Traces back to |
| --- | --- | --- |
| `test_slug.py` | Slug generation, export-suffix stripping | Zhihu export filenames carrying `-落日阳红的文章` |
| `test_frontmatter.py` | The YAML subset reader/writer | A leading newline in the body silently breaking every `body.startswith(...)` check |
| `test_title_prefix.py` | Prefix enforcement | A bare title being eaten because "empty bare title" was used to mean "no prefix" |
| `test_normalize.py` | Image references, code-fence language sniffing | Filenames containing spaces and parentheses being truncated; Zhihu labelling R code as `ada` |
| `test_build.py` | Artifact consistency, `index.html` regression guard | Colors drifting, Chinese leaking into the index, pipeline files appearing under `en/` |
| `test_palette.py` | Color allocation | New articles hashing onto the same color as a neighbour while other colors went unused |

## Running

```bash
cd "R Language/pipeline"
uv run pytest -q
```

## What these tests deliberately do not do

- No coverage padding: a test that cannot fail for a meaningful reason is not added
- No implementation-detail assertions: they test the behaviour that broke, not internals
- No network: the whole suite runs offline, like the build
