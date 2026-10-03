"""`pipeline` 对应测试。

覆盖重点是**踩过的坑**，不是覆盖率数字。每个测试对应一次真实故障。

- `test_slug.py`：slug 生成与稳定取色
- `test_frontmatter.py`：YAML 子集读写
- `test_title_prefix.py`：标题前缀强制（含"裸标题为空"撞车事故）
- `test_normalize.py`：图片引用与代码块语言
- `test_build.py`：产物一致性（index.html 回归守卫）

运行：

```bash
cd "R Language/pipeline"
uv run pytest -q
```
