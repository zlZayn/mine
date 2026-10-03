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
uv sync                                    # 准备环境（首次）
uv run python -m rlang_pipeline build      # 重新生成 index.html 与英文阅读页
uv run python -m rlang_pipeline check      # 完整性体检
uv run python -m rlang_pipeline import <md>  # 导入新文章中文源
```

日常发布流程见 [pipeline/README.md](R%20Language/pipeline/README.md)。

---

## 验证快照

- 部署：[Deploy R Language column to Pages](https://github.com/zlZayn/mine/actions/workflows/static.yml)（徽章见 [README.md](README.md)）
- 全量体检：`check` 应为 **0 FAIL**（两条待办除外，见下）
- 站点自检：11 张卡片 / 11 个英文阅读页 / 0 断链

---

## 待办

- [ ] 补 `rust-extensions-for-r` 与 `tidymodels-worldview` 的 `zhihu-created-at`
      （写在 [vault-map.toml](R%20Language/pipeline/vault-map.toml) 的 `created_at`）
- [ ] `D:\ObsidianDirectory\zhihu\` 的 `process_files.py` 已被本流水线取代，待清理
- [ ] `mine_R Language at main…txt` 等采集残留只存在于仓库外备份，确认后可弃

---

## 活跃坑

- **图片文件名含空格与括号**（`Lorenz Curve.png`、`unnest().png`）
  正则不能用 `[^)\s]+`，否则名字被截断、体检误报"图片不存在"
- **知乎导出把 R 代码标成 ` ```ada `**，Rust 代码标成 ` ```text `
  归一化时按内容嗅探修正（`normalize.fix_code_fences`）
- **frontmatter 与实际发布标题会漂移**（`mice`、`broom` 两篇历史遗留）
  以 [vault-map.toml](R%20Language/pipeline/vault-map.toml) 的 `canonical_zh_titles` 为准
- **`enforce_title_prefix` 不能用"裸标题是否为空"判断有无前缀**
  只有前缀没内容时裸标题也是空串，两种含义撞车会把标题丢掉
- **Tailwind CDN 的 JIT 按字面量扫类名**
  色板在 `site.toml` 里存成完整的 `from-red-300 to-red-600`，模板不许插值拼类名

---

## 文档地图

- 站点用途与入口 → [README.md](README.md)
- 设计决策与不可破坏约束 → [ARCHITECTURE.md](ARCHITECTURE.md)
- 流水线用法 → [R Language/pipeline/README.md](R%20Language/pipeline/README.md)
- 站点内容与构建配置 → [R Language/pipeline/site.toml](R%20Language/pipeline/site.toml)
- 文章来源映射 → [R Language/pipeline/vault-map.toml](R%20Language/pipeline/vault-map.toml)
- 第一代流程存档（已废弃） → [_archive/legacy-pipeline/README.md](_archive/legacy-pipeline/README.md)
