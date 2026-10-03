# Mine

[English](README.md) | [简体中文](README_zh.md)

> 我在给自己搭一个安静的小角落，放我的内容与知识。
> 愿它们一直待在我看得见的地方，永不丢失。

---

## 这是什么

一个既是个人仓库、又是静态站点的东西。
文章先在知乎用中文写，再译成英文归档到这里。

首页同时指向两个版本：英文 Markdown 在本仓库，中文原文在知乎。

---

## 仓库里有什么

### `R Language/` —— 专栏本体

**站点入口：[zlzayn.github.io/mine](https://zlzayn.github.io/mine/)**

| 路径 | 内容 |
| --- | --- |
| `en/<slug>/index.md` | 英文文章（GitHub 上是源文件，站点上是渲染页） |
| `en/<slug>/assets/` | 该文的配图 |
| `zh/<slug>/index.md` | 中文文章，归档在此但**从不发布** |
| `en/<slug>/index.html` | 生成的阅读页 |
| `pipeline/` | 构建站点用的工具链 |

每篇文章是一个以 `slug` 命名的目录。
两侧目录同名，就是中英文配对的依据。

### `tools/` —— 浏览器小工具

单文件 HTML 小工具，与文章流水线无关。

---

## 站点怎么生成

`index.html` 是**生成物**，不要手改。

```
Markdown 的 frontmatter  ──build──▶  index.html + en/<slug>/index.html
```

流水线是纯 Python（用 `uv` 管理），构建过程**不访问网络**：
需要的东西全在仓库里。

```bash
cd "R Language/pipeline"
uv sync                                        # 仅首次
uv run python -m rlang_pipeline build          # 重新生成 index.html
uv run python -m rlang_pipeline check          # 内容体检
uv run python -m rlang_pipeline import <file>  # 导入新文章
```

内容规则见 [pipeline/RULES.md](R%20Language/pipeline/RULES.md)；
设计决策见 [ARCHITECTURE.md](ARCHITECTURE.md)。

---

## 许可与贡献

个人项目——未授予许可，也不需要贡献。
代码可以随便读、随便学。

维护者笔记与文档地图见 [AGENTS.md](AGENTS.md)。
