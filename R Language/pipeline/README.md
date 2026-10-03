# R Language 专栏发布流水线

把 Markdown 的 YAML frontmatter 当作唯一数据源，生成 `index.html`。

**一句话职责划分：**
> `R Language/en/` 与 `R Language/zh/` 是内容，`R Language/pipeline/` 是机器，`index.html` 是产物。

---

## 一、目录结构

```
mine/
├── index.html                      ← 生成物，唯一入口页，不要手改
├── _archive/legacy-pipeline/       ← 第一代抓取式流程的源码存档（已废弃）
└── R Language/                     ← 一个"专栏"块，自包含
    ├── en/<slug>/                  ← 英文原文（GitHub 上是源文件，Pages 上是渲染页）
    │   ├── index.md
    │   ├── assets/                 ← 本地图片（若有）
    │   └── index.html              ← 生成物：渲染后的阅读页
    ├── zh/<slug>/                  ← 中文归档（只在仓库里，绝不进 Pages）
    │   ├── index.md
    │   └── assets/
    └── pipeline/                   ← 流水线本体
        ├── site.toml               ← 唯一允许写站点事实的地方
        ├── pyproject.toml
        ├── templates/
        │   ├── index.html.j2       ← 首页模板
        │   ├── article.html.j2     ← 英文阅读页模板
        │   ├── card.css
        │   └── article.css
        └── src/rlang_pipeline/
            ├── paths.py            ← 路径解析（从文件位置反推，无绝对路径）
            ├── config.py           ← site.toml 读取与校验
            ├── frontmatter.py      ← YAML frontmatter 读写
            ├── slug.py             ← slug 生成 + 稳定哈希取色
            ├── articles.py         ← 文章模型与配对
            ├── normalize.py        ← 内容归一化（图片、代码块、frontmatter）
            ├── render.py           ← Markdown → HTML
            ├── build.py            ← 生成 index.html 与阅读页
            ├── migrate.py          ← 一次性迁移脚本（跑完即可不用）
            └── cli.py              ← 命令行入口
```

---

## 二、数据源：frontmatter

### 中文侧 `zh/<slug>/index.md`

```yaml
---
zhihu-title: 【R 语言】broom 包进行整洁建模    # index.html 上显示的中文标题
zhihu-topics: R
zhihu-link: https://zhuanlan.zhihu.com/p/1949603330578953873   # 卡片上的"中文-知乎"按钮
zhihu-created-at: 2025-09-11 22:51            # 排序依据
---
```

### 英文侧 `en/<slug>/index.md`

```yaml
---
en-title: 【R Language】broom Package for Tidy Modeling   # 卡片上的英文标题
slug: broom-package-for-tidy-modeling
zhihu-link: https://zhuanlan.zhihu.com/p/1949603330578953873
zhihu-created-at: 2025-09-11 22:51
---
```

### 配对规则

**`slug` 就是配对键**，两侧目录同名即视为同一篇。

这取代了旧流程"靠 `_1` 对 `_1` 的下标顺序配对"——那种做法在知乎列表顺序与
GitHub 文件名顺序不一致时会静默错位。

---

## 三、日常操作

所有命令在 `R Language/pipeline/` 下执行。

```bash
# 首次准备环境
uv sync

# 1) 导入一篇新文章的中文源
#    源可以是知乎导出件（带 -落日阳红的文章 后缀），也可以是 Obsidian 笔记
uv run python -m rlang_pipeline import "D:\ObsidianDirectory\zhihu\某篇新文章-落日阳红的文章.md"

#    它会：归一化 frontmatter、把图片落盘到 zh/<slug>/assets/、
#          修正代码块语言、并建好 en/<slug>/index.md 骨架待翻译

# 2) 写完英文译文后，重新构建
uv run python -m rlang_pipeline build

# 3) 体检（缺字段、缺图、index 过期、中文泄漏到 Pages 都会被拦下）
uv run python -m rlang_pipeline check
```

调试用：

```bash
uv run python -m rlang_pipeline paths       # 各目录解析结果
uv run python -m rlang_pipeline manifest    # 站点清单 JSON
uv run python -m rlang_pipeline slug "某标题"  # 看会生成什么 slug
```

---

## 四、设计约束（为什么这么写）

| 约束 | 原因 |
| --- | --- |
| **构建过程零网络** | 不抓知乎、不抓 GitHub。数据只来自仓库内的 Markdown。 |
| **不使用 `random`** | 颜色由 `site.toml` 的固定分配表决定，未登记的用 slug 稳定哈希。同一篇文章的颜色永远不变。 |
| **不读系统时间** | 输出不含时间戳，因此 `git diff index.html` 能精确反映内容变化。 |
| **无绝对路径** | 所有路径从 `paths.py` 反推。换机器、换用户名、换盘符都能跑。 |
| **爬虫式正则一律不写** | 旧流程靠 `data-za-detail-view_element_name="Title"` 这种外部站点类名取数，改版即失效。 |
| **缺数据要报错不要兜底** | 旧的 `link_extractor_*.py` 匹配到 0 条也打印"成功"。现在缺什么就 `check` 失败并说明缺什么。 |
| **Tailwind 类名必须是字面量** | `cdn.tailwindcss.com` 的 JIT 按字面量扫源码。模板里写 `from-{{ color }}-300` 会扫不到，颜色失效。所以色板在配置里存成完整的 `from-red-300 to-red-600`。 |

---

## 五、内容约定

### 图片

- 归一化后统一是 `![](assets/文件名.png)`，文件在同目录的 `assets/`
- 带空格（`Lorenz Curve.png`）和带括号（`unnest().png`）的文件名都支持
- 指向知乎图床的 `https://pic*.zhimg.com/...` 会**保留为远程链接**
  （已实测 zhimg 允许跨站热链，从 GitHub 与 Pages 都能正常加载）

### 代码块语言

知乎导出会把 R 代码标成 ` ```ada `、把 Rust 代码标成 ` ```text `。
归一化时按内容嗅探修正为 `r` / `rust` / `toml` / `bash`，嗅探不出来就留空
（渲染成无高亮的代码块，好过标错语言）。

### 中文不发布

- `zh/` 里的 Markdown 永远不参与 Pages 构建
- `build_article_pages()` 只处理英文侧
- `.github/workflows/static.yml` 只上传白名单路径，不是整个仓库
- `check` 会检查 `zh/` 下有没有混入 html

仓库本身是 public，所以 `zh/` 的**源码**在 GitHub 网页上仍可看到——
"不发布"指的是不进入 Pages 产物、不在 `index.html` 上出现。
