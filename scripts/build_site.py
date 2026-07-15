#!/usr/bin/env python3
"""
生成 invest-hub 静态站点
- 把 knowledge-base 下的所有 markdown 转成 html
- 复制到 site/knowledge-base/ 下
- 生成 index.html 入口（如果需要覆盖）
"""

import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
KB = ROOT / "knowledge-base"
SITE = ROOT / "site"
SITE_KB = SITE / "knowledge-base"


def md_to_html(md: str) -> str:
    """极简 markdown -> html 转换（足够信息展示用）"""
    lines = md.split("\n")
    out = []
    in_code = False
    in_list = False
    in_table = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def close_table():
        nonlocal in_table
        if in_table:
            out.append("</tbody></table>")
            in_table = False

    for line in lines:
        # code block
        if line.strip().startswith("```"):
            close_list()
            close_table()
            if in_code:
                out.append("</pre>")
                in_code = False
            else:
                out.append('<pre><code>')
                in_code = True
            continue
        if in_code:
            out.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_list()
            close_table()
            level = len(m.group(1))
            text = inline(m.group(2))
            out.append(f"<h{level}>{text}</h{level}>")
            continue

        # hr
        if re.match(r"^---+$", line.strip()):
            close_list()
            close_table()
            out.append("<hr>")
            continue

        # table
        if line.strip().startswith("|") and line.strip().endswith("|"):
            close_list()
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if re.match(r"^[\s\-\|:]+$", line):
                # separator line
                continue
            if not in_table:
                out.append("<table>")
                # check if next is separator
                out.append("<thead><tr>")
                for c in cells:
                    out.append(f"<th>{inline(c)}</th>")
                out.append("</tr></thead><tbody>")
                in_table = True
            else:
                out.append("<tr>")
                for c in cells:
                    out.append(f"<td>{inline(c)}</td>")
                out.append("</tr>")
            continue
        else:
            close_table()

        # list
        m = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if m:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(m.group(2))}</li>")
            continue
        m = re.match(r"^(\s*)\d+\.\s+(.*)$", line)
        if m:
            if not in_list:
                out.append("<ol>")
                in_list = True
            out.append(f"<li>{inline(m.group(2))}</li>")
            continue
        else:
            close_list()

        # empty
        if not line.strip():
            out.append("")
            continue

        # paragraph
        out.append(f"<p>{inline(line)}</p>")

    close_list()
    close_table()
    if in_code:
        out.append("</code></pre>")

    return "\n".join(out)


def inline(text: str) -> str:
    """行内格式"""
    # link [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2" target="_blank">\1</a>',
        text,
    )
    # bold **text**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # italic *text*
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    # inline code `text`
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · 投资信息中心</title>
<link rel="stylesheet" href="{css}">
</head>
<body>
<div class="container">
  <header>
    <h1>📈 投资信息中心</h1>
    <p class="subtitle">Invest Hub · 全球市场每日追踪 + 趋势研报</p>
    <p class="date">2026-07-15 (周三) 收盘后</p>
    <div class="disclaimer">
      ⚠️ 重要声明：纯信息整理，不构成投资建议。投资有风险，决策需谨慎。
    </div>
  </header>
  <nav>
    <a href="{root}index.html">🏠 首页</a>
    <a href="{root}knowledge-base/2026-07-15-今日综合分析.html">综合分析</a>
    <a href="{root}knowledge-base/A股/2026-07-15-A股今日热点.html">A 股</a>
    <a href="{root}knowledge-base/港股/2026-07-15-港股今日热点.html">港股</a>
    <a href="{root}knowledge-base/美股/2026-07-15-美股表现.html">美股</a>
    <a href="{root}knowledge-base/加密货币/2026-07-15-加密货币行情.html">加密</a>
    <a href="{root}knowledge-base/大宗商品/2026-07-15-大宗商品价格.html">大宗</a>
    <a href="{root}knowledge-base/宏观政策/2026-07-15-宏观政策与财经要闻.html">宏观</a>
    <a href="{root}knowledge-base/趋势研报/2026-07-15-未来1-3个月市场展望.html">展望</a>
  </nav>
  <main class="card">
{content}
  </main>
  <footer>
    <p>Invest Hub · 全球投资信息中心</p>
    <p>数据来源：东方财富、新浪财经、腾讯财经、券商研报、机构观点</p>
    <p>⚠️ 纯信息整理，不构成投资建议。投资有风险，决策需谨慎。</p>
    <p>最后更新：2026-07-15</p>
  </footer>
</div>
</body>
</html>
"""


def find_title(md: str, fallback: str) -> str:
    for line in md.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build():
    if SITE_KB.exists():
        shutil.rmtree(SITE_KB)
    SITE_KB.mkdir(parents=True, exist_ok=True)

    md_files = list(KB.rglob("*.md"))
    print(f"找到 {len(md_files)} 个 markdown 文档")

    for md_path in md_files:
        rel = md_path.relative_to(KB)
        out_dir = SITE_KB / rel.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        md = md_path.read_text(encoding="utf-8")
        title = find_title(md, rel.stem)
        body = md_to_html(md)

        # 计算 css 和首页相对路径
        depth = len(rel.parts)
        prefix = "../" * depth
        css = f"{prefix}style.css"
        root = prefix

        html = HTML_TEMPLATE.format(
            title=title,
            css=css,
            root=root,
            content=body,
        )
        out_path = out_dir / (rel.stem + ".html")
        out_path.write_text(html, encoding="utf-8")
        print(f"  ✓ {rel} -> {out_path.relative_to(SITE)}")

    print("\n✅ 站点生成完成")
    print(f"  入口: {(SITE / 'index.html').absolute()}")


if __name__ == "__main__":
    build()
