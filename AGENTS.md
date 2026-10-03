# Mine — 维护索引

> 本文件是**规则与仪表盘**，会在会话启动时自动注入。
> 内容与用法不放这里 —— 那是 [README.md](README.md) 的职责；设计理由见 [ARCHITECTURE.md](ARCHITECTURE.md)。

---

## 全局规则

- **中文不发布**：`R Language/zh/` 只归档，绝不进 Pages 产物、绝不出现在 `index.html`
- **标题前缀强制**：英文 `【R Language】`、中文 `【R 语言】`，由 `enforce_title_prefix()` 兜底，不靠人记
- **不手改生成物**：`index.html` 与 `en/<slug>/index.html` 都是产物，改模板/数据后重新构建
- **frontmatter 是唯一数据源**：文章的标题与链接只从 `index.md` 的 YAML 读，任何地方不许再写一份
- **禁止绝对路径**：路径一律从 [paths.py](R%20Language/pipeline/src/rlang_pipeline/paths.py) 反推
- **禁止 `random` 与系统时间**：构建必须可复现，`git diff index.html` 要能精确反映内容变化

---

## 常用命令

在 `R Language/pipeline/` 下执行：

```bash
uv sync                                       # 准备环境（首次）
uv run python -m rlang_pipeline build         # 重新生成 index.html 与英文阅读页
uv run python -m rlang_pipeline check         # 完整性体检（语义层）
uv run python -m rlang_pipeline import <md>   # 导入新文章中文源
uv run pytest -q                              # 单元测试
```

在仓库根执行：

```bash
npx markdownlint-cli2          # 检查文章格式
npx markdownlint-cli2 --fix    # 自动修（空行、列表标记）
```

排版规则的分层见 [RULES.md](R%20Language/pipeline/RULES.md)。

---

## 验证快照

- 部署：[Deploy R Language column to Pages](https://github.com/zlZayn/mine/actions/workflows/static.yml)（徽章见 [README.md](README.md)）
- 线上站点：<https://zlzayn.github.io/mine/> —— 11 张卡片，与本地生成物逐字节一致
- `check` 0 FAIL；`pytest` 99 passed；`markdownlint` 14 项（均为严格规则提示，非阻断）

---

## 待办

- [ ] `markdownlint` 剩余 14 项：多为 MD025（多一级标题）与 MD040（无语言围栏），
      目录树那处**有意留空**，不必强行满足

---

## 仓库外的东西

以下**刻意不入库**，放在仓库外按需查阅。理由见 [.gitignore](.gitignore)。

| 位置 | 内容 |
| --- | --- |
| `D:\PythonDirectory\_archive_mine\` | 旧流程源码（两代）、知乎导出原件 |
| `D:\PythonDirectory\_知乎_legacy_backup_20261003\` | 第一代流程的采集残留（另存的网页 HTML） |

早期曾在仓库内建 `_archive/`，后按要求移除，`.gitignore` 已兜底。

---

## 活跃坑

按踩过的时间顺序，每条都对应一次真实故障：

- **图片文件名含空格与括号**（`Lorenz Curve.png`、`unnest().png`）
  正则必须允许一层配对括号**且不排除空格**：
  `(?:<([^>]+)>|((?:[^()]|\([^()]*\))+))`。
  试过三种错法：`[^)\s]+` 截断空格名；`(?:[^()\s]|\([^()]*\))+` 同样排除空格；
  `[^)]+` 贪婪停在第一个 `)` 把 `unnest(` 截断。
- **知乎导出把 R 代码标成 `ada`**，Rust 代码标成 `text`
  归一化按内容嗅探修正；`|>` 可在行中，不能锚定行尾
- **frontmatter 与实际发布标题会漂移**（`mice`、`broom`）
  以 [vault-map.toml](R%20Language/pipeline/vault-map.toml) 的 `canonical_zh_titles` 为准
- **`enforce_title_prefix` 不能用"裸标题是否为空"判断有无前缀**
  只有前缀没内容时裸标题也是空串，两种含义撞车会把标题丢掉。
  函数因此返回三元组 `(裸标题, 标准前缀, 是否本来就有前缀)`。
- **Tailwind CDN 的 JIT 按字面量扫类名**
  色板在 `site.toml` 里存成完整的 `from-red-300 to-red-600`，模板不许插值拼类名
- **markdownlint 的默认规则会改坏东西**
  MD029 默认 lazy 编号会把 `1. 2. 3.` 改成 `1. 1. 1.`（须设 `"style": "ordered"`）；
  MD026 会去掉标题末尾句号。作用范围已收窄到 `R Language/{en,zh}`，
  不含根文档（有作者语气）
- **迁移的备份机制不能改名文章目录**
  曾用 `<slug>.__stash__` 做备份，异常时不还原导致文章消失、
  且残留目录被当成一篇文章混进产物。现改为目录内的 `.assets-backup/`。
- **卡片悬浮不能改变任何尺寸**
  曾用 `:hover { height: .75rem }` 让色条变高：卡片被撑高 → Grid 行高重算 →
  下方所有卡片一起下移。悬浮反馈只能用 `transform` 与 `box-shadow`，它们不参与布局。
- **卡片高度不能用固定 `height`**
  固定高度在标题换行时不报错，只是把内容挤变形 —— `margin-top: auto`
  推不动按钮，于是长标题卡片的按钮紧贴标题、短标题的沉底。
  用 `min-height`，长标题自然撑高，Grid 行内自动等高。

---

## 文档地图

- 站点用途与入口 → [README.md](README.md)
- 设计决策与不可破坏约束 → [ARCHITECTURE.md](ARCHITECTURE.md)
- 流水线用法 → [R Language/pipeline/README.md](R%20Language/pipeline/README.md)
- 规则分层：什么写死、什么配置 → [R Language/pipeline/RULES.md](R%20Language/pipeline/RULES.md)
- 站点与构建配置 → [R Language/pipeline/site.toml](R%20Language/pipeline/site.toml)
- 文章来源映射 → [R Language/pipeline/vault-map.toml](R%20Language/pipeline/vault-map.toml)
