# 第一代发布流程（2025-09 ~ 2025-10）—— 已废弃

这里保存了这个站点最早那套生成 `index.html` 的源码。

**保留原因：** 记录站点最初是怎么做出来的，以及当时踩了哪些坑。
**状态：** 只读存档，不会运行、不会维护、新流程不引用它。

> 脚本里的绝对路径（`d:\PythonDirectory\知乎\...`）原样保留，作为"当时就是这样写的"的证据。

---

## 一、它当时怎么工作

```
浏览器「另存为网页」
      │
      ├─ 知乎专栏页      →  R 语言 - 知乎.txt              (~250 KB 整页 HTML)
      └─ GitHub 目录页   →  mine_R Language at main….txt   (~282 KB 整页 HTML)
              │
              ▼
      link_extractor_*.py            正则从整页 HTML 里抠链接
              ▼
      html_card_generator_*.py       正则抠「标题 + 链接」，产出单语卡片页
              ▼
      generate_dynamic_template.py   随机挑一个卡片页，提取渐变色，产出模板
              ▼
      generate_combined_cards.py     把 36 条硬编码字面量填进模板
              ▼
      combined_article_cards.html    → 人工改名 index.html 后提交
```

入口 `scripts/workflow.py` 按顺序调上面 4 个脚本，最后用浏览器打开结果。

---

## 二、为什么整条链路要废弃

| # | 问题 | 具体表现 |
| --- | --- | --- |
| 1 | **数据源错位** | 从「浏览器另存的网页」取数据，而不是从 Markdown 源文件取。等于在扒自己的下游产物。 |
| 2 | **绑死外部 HTML 结构** | 依赖 `data-za-detail-view_element_name="Title"`、`href=".../blob/main/R%20Language/..."` 这类类名与属性正则。知乎或 GitHub 任何一次改版，全线失效。 |
| 3 | **硬编码** | 文章数量 9 写死；每篇文章的标题与中英链接以字面量写在 `generate_combined_cards.py` 里；4 处 `d:\PythonDirectory\知乎\` 绝对路径。 |
| 4 | **构建不可复现** | `generate_dynamic_template.py` 用 `random.choice` 随机挑文件取渐变色，同样输入两次运行可能得到不同结果。 |
| 5 | **静默失败** | 正则匹配到 0 条时仍打印「成功提取了 0 个链接」，然后照常产出一个空页面，没有任何非零退出码。 |
| 6 | **生成物当输入** | `dynamic_article_card_template.txt` 由脚本产出，又被另一个脚本读取，无法人工维护、无法 review、无法 diff。 |
| 7 | **靠下标顺序配对** | 中英文靠 `_1` 对 `_1` 的下标对齐。知乎列表顺序与 GitHub 文件名顺序毫无关系，当时的正确纯属偶然。 |
| 8 | **实际早已失效** | 最终上线的 `index.html` 是**手工编辑**的（双语标题 + 双链接 + GitHub 角标 + R logo），脚本产物里没有这些。经逐字节比对，`combined_article_cards.html` 与线上 `index.html` 完全一致——也就是说，脚本早已不再参与产出，只是留在硬盘上。 |

---

## 三、本目录收录范围

**只收录源码**（8 个 `.py`），因为它们承载了"当时怎么想的"这一信息。

**主动排除**以下文件，理由是没有历史信息量、纯占体积：

| 排除项 | 大小 | 理由 |
| --- | --- | --- |
| `R 语言 - 知乎.txt` | 250 KB | 浏览器另存的知乎整页 HTML，是采集残留而非源码 |
| `mine_R Language at main….txt` | 282 KB | 同上，GitHub 目录页残留 |
| `article_cards_*.html` | 13 KB | 脚本产出物，可由源码复现 |
| `combined_article_cards.html` | 12 KB | 脚本产出物；其内容与线上 `index.html` 等同，已在 git 历史中 |
| `dynamic_article_card_template.txt` | 12 KB | 生成物充当输入的证据，已在本文档第 6 条说明 |

需要这些原始文件时，它们保存在仓库外的本地备份：
`D:\PythonDirectory\_知乎_legacy_backup_20261003\`

---

## 四、被什么取代

见 [`R Language/pipeline/`](../../R%20Language/pipeline/)：

- **数据源**：Markdown 的 YAML frontmatter（`zhihu-title` / `zhihu-link` / `zhihu-topics` / `zhihu-created-at`），而不是抓来的 HTML
- **配对方式**：显式 article id（slug），而不是下标顺序
- **渲染**：Jinja2 模板，模板是唯一 HTML 出处
- **颜色**：由 article id 稳定哈希得出，不使用 `random`
- **零硬编码**：站名、仓库地址、专栏地址、颜色表全部在 `pipeline/templates/site.toml`
- **零网络**：构建过程不访问任何外部站点
- **可校验**：`check` 子命令做完整性体检，缺字段/图缺失/链接失效一律报错并非零退出
