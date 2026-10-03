"""YAML frontmatter 的读写。

刻意只用极简子集（`key: value` 一行一条），因为实际数据就是这样的，
没必要为此引入 PyYAML 依赖。

frontmatter 是整条流水线的唯一数据源：
  - 中文侧提供 zhihu-title / zhihu-link，index.html 的中文标题与知乎链接由此而来
  - 英文侧提供 en-title，卡片的英文标题由此而来
  - slug 两侧一致，就是配对键
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

_FM_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n)?", re.DOTALL)


class FrontmatterError(RuntimeError):
    pass


@dataclass
class Frontmatter:
    data: dict[str, Any]
    body: str
    had_block: bool
    raw_block: str = ""


def _coerce(value: str) -> Any:
    """把标量字符串转成合适的 Python 类型。"""
    v = value.strip()
    if v == "":
        return ""
    # 不去引号化数字/布尔以外的内容，避免破坏 URL
    if v.startswith(("'", '"')) and v.endswith(("'", '"')) and len(v) >= 2:
        return v[1:-1]
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    return v


def parse(text: str) -> Frontmatter:
    """拆出 frontmatter 与正文。没有 frontmatter 时 data 为空字典。

    正文一律以第一个非空行开头（去掉分隔线之后的多余空行）。
    这一点影响很大：调用方普遍用 `body.startswith(...)` 判断内容，
    若正文带前导换行，这类判断会静默失效。
    """
    match = _FM_RE.match(text)
    if not match:
        # 统一换行，保证后续处理一致
        return Frontmatter(data={}, body=text.lstrip("\ufeff"), had_block=False)

    block = match.group(1)
    body = text[match.end():].lstrip("\r\n")
    data: dict[str, Any] = {}

    for line_no, line in enumerate(block.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t", "-")):
            raise FrontmatterError(
                f"frontmatter 第 {line_no} 行不是受支持的 `key: value` 形式：{line!r}\n"
                "本流水线只支持扁平的单层键值对（不支持列表与嵌套）。"
            )
        if ":" not in line:
            raise FrontmatterError(
                f"frontmatter 第 {line_no} 行缺少冒号：{line!r}"
            )
        key, value = line.split(":", 1)
        data[key.strip()] = _coerce(value)

    return Frontmatter(data=data, body=body, had_block=True, raw_block=block)


def dump(data: dict[str, Any], body: str, *, key_order: list[str] | None = None) -> str:
    """把 frontmatter 与正文合成一个文件内容。

    key_order 中列出的键按该顺序排在最前，其余键按原顺序跟在后面，
    保证写回文件时 diff 最小。
    """
    keys: list[str] = []
    if key_order:
        keys.extend(k for k in key_order if k in data)
    keys.extend(k for k in data if k not in keys)

    lines = ["---"]
    for key in keys:
        value = data[key]
        if value is None:
            continue
        lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")

    header = "\n".join(lines)
    return header + body.lstrip("\n")
