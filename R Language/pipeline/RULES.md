# 规则分层：什么该写死、什么该交给工具

> 本文回答一个具体问题：**哪些东西要统一、用什么机制保证。**
>
> 核心判据一条：**能用成熟工具机械保证的，就不要自己写规则；必须靠语义理解才能判断的，才自己写。**

---

## 一、三层分工

| 层 | 机制 | 保证什么 | 为什么放这一层 |
| --- | --- | --- | --- |
| **格式层** | `mdformat` + 插件 | 空行、列表符号、标题间距、行尾、多余空格、表格对齐 | 纯机械、无歧义、有成熟工具，自己写必然漏 |
| **约束层** | `rlang_pipeline` 的 `check` | 标题前缀、frontmatter 字段、图片存在、slug 唯一、产物隔离、index 新鲜度 | 需要理解"这是什么文章"，工具做不了 |
| **命令层** | 运行命令固定 | 命令名、退出码、状态常量 | 是程序契约，改了调用方就崩 |

---

## 二、格式层：交给 mdformat

### 必须装的插件

```bash
mdformat --extensions frontmatter,gfm,tables \
         --wrap=no --end-of-line=lf <paths>
```

| 插件 | 不装会怎样 |
| --- | --- |
| `mdformat-frontmatter` | **frontmatter 被摧毁** —— 已实测：YAML 被折叠成一个 `## en-title: ...` 标题 + 一条分隔线 |
| `mdformat-gfm` | 表格与删除线等 GFM 语法不被识别 |
| `mdformat-tables` | 表格单元格不做对齐规范化 |

### 实测它改了什么

在 `en/broom-package-for-tidy-modeling/index.md` 上实测，只有三类改动：

| 改动 | 判断 |
| --- | --- |
| `-   item` → `- item`（列表缩进规范） | **要**，一致性收益 |
| `* * *` → 下划线分隔线（主题分隔符规范形式） | 可接受，纯外观 |
| frontmatter 与正文之间多余空行收起 | **要**，正是"空行格式化" |

结论：**装齐插件后，它的改动都是我们要的。**

### 边界：只格式化源文件

- 施加对象：`R Language/en/**/index.md`、`R Language/zh/**/index.md`
- **不施加**于：`index.html`、`en/**/index.html`（生成物）、模板、CSS

### 为什么不选 Prettier

- Prettier 需要 Node；本仓流水线已是纯 Python（`uv`）
- mdformat 是纯 Python，与现有工具链同源，无需第二套运行时
- 若将来引入前端工具链，Prettier 可作补充，但 Markdown 仍建议单源（避免两个格式化器互相打架）

---

## 三、约束层：自己写，因为工具做不了

| 规则 | 级别 | 可自动修 |
| --- | --- | --- |
| 英文标题以 `【R Language】` 开头 | error | 是（补前缀） |
| 中文标题以 `【R 语言】` 开头 | error | 是（补前缀） |
| 中英标题前缀不得互换 | error | 是 |
| frontmatter 必填字段齐全 | error | 否（缺日期要人填） |
| `zhihu-link` 形如 `https://zhuanlan.zhihu.com/p/\d+` | error | 否 |
| 本地图片引用必须存在 | error | 否 |
| slug 全局唯一 | error | 否 |
| `index.html` 与内容一致 | error | 是（重新 build） |
| `zh/` 下不得有 `.html` | error | 否 |
| `en/` 下不得有流水线源码 | error | 否 |
| 图片路径必须相对，不得绝对 | error | 否 |
| 日期格式 `YYYY-MM-DD HH:MM` | error | 是（可无歧义解析时） |
| 代码块语言标记正确 | warn | 是 |
| 远程图床引用数量 | info | 否 |

**级别含义**
- `error`：`check` 非零退出，阻断提交
- `warn`：打印但退出码仍为 0
- `info`：仅统计

---

## 四、什么该写死，什么该进配置

这条最容易做错：**写死契约，配置事实。**

| 类别 | 处理 | 例子 |
| --- | --- | --- |
| **程序契约（写死）** | 改了就破坏调用方 | 子命令名 `build`/`check`/`import`；退出码 0/1/2；`PREFIX_EN`/`PREFIX_ZH` 常量；frontmatter 键名 |
| **站点事实（进 `site.toml`）** | 与代码无关，会变 | 色板、仓库地址、专栏链接、按钮文案、排序方向 |
| **文章事实（进 frontmatter）** | 每篇不同 | 标题、知乎链接、发布时间 |
| **来源映射（进 `vault-map.toml`）** | 只迁移时用 | 笔记路径、旧文件名、权威标题覆盖 |

**反例（本仓历史上真实存在过的）**
- 36 条文章标题链接写在 `generate_combined_cards.py` 里 → 应进 frontmatter
- `d:\PythonDirectory\知乎\` 绝对路径 → 应从文件位置反推
- 文章数 `9` 写死 → 应从目录扫描得出
- 色板 12 个色值写在两个生成器里各一份 → 应进 `site.toml` 单源

**正例**
- `PREFIX_EN = "【R Language】"` 写在代码里是对的：它是版式契约，不是文章事实

---

## 五、为什么不用 `random` 也不用系统时间

写进规则是因为它们破坏的是**可复现性**，而可复现性是全部验证手段的地基：

- 有 `random` → 同一输入两次构建结果不同 → `git diff index.html` 失去意义
- 有时间戳 → 每次构建都产生噪声 diff → 无法判断"这次改动影响了什么"

替代做法：
- 需要"随机但有辨识度"的取值（颜色）→ 用 slug 的稳定哈希
- 需要"当前时间"→ 不写进产物；时间属于内容，写在 frontmatter 里

---

## 六、落地位置

| 机制 | 位置 |
| --- | --- |
| mdformat 依赖与插件版本 | `pipeline/pyproject.toml` 的 dev 依赖 |
| 格式检查命令 | `check` 子命令内调用 |
| 语义检查清单 | `cli.py` 的 `cmd_check` |
| 站点事实 | `pipeline/site.toml` |
| 来源映射 | `pipeline/vault-map.toml` |
