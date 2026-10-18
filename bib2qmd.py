#!/usr/bin/env python3
"""
bib2qmd.py — 从 refs.bib 生成首页的论文区块

用法:
    python bib2qmd.py                 # 读取 refs.bib，更新 page.html
    python bib2qmd.py --bib my.bib    # 指定其他 bib 文件
    python bib2qmd.py --dry-run       # 只打印统计，不写文件

脚本会替换 page.html 中两段被注释标记包裹的区块：
    <!-- BEGIN:SELECTED --> ... <!-- END:SELECTED -->   精选论文
    <!-- BEGIN:ALL -->      ... <!-- END:ALL -->        按年份分组的完整列表
并同步更新标题旁的篇数徽章。

依赖: pip install bibtexparser
"""
import argparse
import html
import re
import sys

try:
    import bibtexparser
except ImportError:
    print("错误: 缺少依赖 bibtexparser，请先执行:")
    print("  pip install bibtexparser")
    sys.exit(1)

ARROW = '<span aria-hidden="true">↗</span>'

SECTION_TITLES = {
    "article": "Journal Articles",
    "inproceedings": "Conference Papers",
    "incollection": "Book Chapters",
    "phdthesis": "Theses",
    "mastersthesis": "Theses",
    "techreport": "Technical Reports",
    "unpublished": "Preprints",
    "misc": "Preprints",
}


# --------------------------------------------------------------------------- #
# 字段处理
# --------------------------------------------------------------------------- #
def clean_field(value: str) -> str:
    """去除 BibTeX 花括号，压缩空白，并把 -- 转成 en dash"""
    if not value:
        return ""
    value = re.sub(r"[{}]", "", str(value))
    value = re.sub(r"\s+", " ", value).strip()
    return value.replace("--", "–")


def esc(value: str) -> str:
    return html.escape(clean_field(value), quote=True)


def is_true(value: str) -> bool:
    return clean_field(value).lower() in {"true", "yes", "1", "y"}


def load_bib(path: str) -> list:
    """读入 BibTeX，统一成 [{'ID':..., 'ENTRYTYPE':..., 字段: 值(str)}]

    兼容 bibtexparser 2.x（parse_file）与 1.x（load）。
    """
    try:  # bibtexparser >= 2
        library = bibtexparser.parse_file(path)
        entries = []
        for e in library.entries:
            record = {"ID": e.key, "ENTRYTYPE": (e.entry_type or "misc").lower()}
            fields = e.fields or []
            pairs = fields.items() if hasattr(fields, "items") else (
                (getattr(f, "key", ""), f) for f in fields
            )
            for name, field in pairs:
                if name:
                    record[name.lower()] = getattr(field, "value", str(field))
            entries.append(record)
        return entries
    except AttributeError:  # bibtexparser 1.x
        with open(path, "r", encoding="utf-8") as f:
            return bibtexparser.load(f).entries


def format_authors(author_str: str, me_lastnames=("hu",)) -> str:
    """'Hu, Mingwang and Tu, Yi' -> 'Mingwang Hu, Yi Tu'，本人姓名加粗"""
    names = [n.strip() for n in author_str.split(" and ") if n.strip()]
    out = []
    for name in names:
        if "," in name:
            last, first = name.split(",", 1)
            last, first = last.strip(), first.strip()
            display = f"{first} {last}".strip() if first else last
        else:
            display = name
            last = name.split()[-1] if name.split() else ""
        display = esc(display)
        if last.lower() in me_lastnames:
            display = f"<strong>{display}</strong>"
        out.append(display)
    return ", ".join(out)


def entry_get(entry, key: str, default: str = "") -> str:
    if isinstance(entry, dict):
        return entry.get(key, default) or default
    return getattr(entry, key, default) or default


def entry_type(entry) -> str:
    if isinstance(entry, dict):
        return (entry.get("ENTRYTYPE") or "misc").lower()
    return (getattr(entry, "entry_type", "misc") or "misc").lower()


def venue_label(entry) -> str:
    """卡片上显示的会议/期刊简称"""
    short = clean_field(entry_get(entry, "shortvenue"))
    if short:
        return short
    etype = entry_type(entry)
    if etype == "article":
        return clean_field(entry_get(entry, "journal"))
    if etype == "inproceedings":
        return clean_field(entry_get(entry, "booktitle"))
    return clean_field(entry_get(entry, "howpublished"))


def links_for(entry):
    """返回 [(url, label), ...]"""
    links = []
    doi = clean_field(entry_get(entry, "doi"))
    url = clean_field(entry_get(entry, "url"))
    pdf = clean_field(entry_get(entry, "pdf"))
    if doi:
        links.append((f"https://doi.org/{doi}", "Paper"))
    if url:
        label = "Code" if "github.com" in url.lower() else "Link"
        links.append((url, label))
    if pdf:
        links.append((pdf, "PDF"))
    return links


def anchor(url: str, inner: str, aria: str = "") -> str:
    aria_attr = f' aria-label="{html.escape(aria, quote=True)}"' if aria else ""
    return (
        f'<a href="{html.escape(url, quote=True)}" target="_blank" '
        f'rel="noopener noreferrer"{aria_attr}>{inner}</a>'
    )


# --------------------------------------------------------------------------- #
# HTML 片段
# --------------------------------------------------------------------------- #
def article_html(entry, *, selected: bool) -> str:
    key = clean_field(entry_get(entry, "ID"))
    title = esc(entry_get(entry, "title", "Untitled"))
    authors = format_authors(clean_field(entry_get(entry, "author")))
    venue = esc(venue_label(entry))
    role = esc(entry_get(entry, "role"))
    summary = esc(entry_get(entry, "summary"))
    year = clean_field(entry_get(entry, "year"))
    links = links_for(entry)

    prefix = "selected" if selected else "paper"
    dom_id = f"{prefix}-{key}" if key else ""

    title_inner = html.escape(title, quote=False)
    if links:
        title_html = anchor(links[0][0], title_inner)
    else:
        title_html = title_inner

    meta = []
    if venue:
        meta.append(f'<span class="venue">{venue}</span>')
    elif year:
        meta.append(f'<span class="venue">{year}</span>')
    if role:
        meta.append(f'<span class="author-role">{role}</span>')

    open_tag = '<article class="publication"' + (f' id="{dom_id}"' if dom_id else "") + ">"

    parts = [
        open_tag,
        '<div class="publication-content">',
        f'<div class="publication-meta">{"".join(meta)}</div>' if meta else "",
        f"<h3>{title_html}</h3>",
        f'<p class="authors">{authors}</p>' if authors else "",
    ]
    if selected and summary:
        parts.append(f'<p class="paper-summary">{summary}</p>')
    if links:
        items = "".join(
            anchor(u, f"{lbl} {ARROW}", aria=f"{lbl}: {title}") for u, lbl in links
        )
        parts.append(f'<div class="paper-links">{items}</div>')
    parts.append("</div></article>")
    return "".join(p for p in parts if p)


def build_selected(entries) -> str:
    picked = [e for e in entries if is_true(entry_get(e, "selected"))]
    if not picked:
        return '<p class="empty-state">No selected publications yet.</p>'
    return "\n".join(article_html(e, selected=True) for e in picked)


def build_all(entries) -> str:
    if not entries:
        return '<p class="empty-state">No publications yet.</p>'
    by_year = {}
    for e in entries:
        by_year.setdefault(clean_field(entry_get(e, "year")) or "—", []).append(e)

    blocks = []
    for year in sorted(by_year, key=lambda y: (y == "—", y), reverse=True):
        articles = "\n".join(article_html(e, selected=False) for e in by_year[year])
        blocks.append(
            '<div class="publication-year" data-year-group="">'
            f'<h3 class="year-heading">{html.escape(year)}</h3>'
            f"<div>\n{articles}\n</div></div>"
        )
    return "\n".join(blocks)


# --------------------------------------------------------------------------- #
# 写回页面文件
# --------------------------------------------------------------------------- #
def replace_block(text: str, marker: str, payload: str, page_name: str = "") -> str:
    pattern = re.compile(
        rf"(<!-- BEGIN:{marker} -->)(.*?)(<!-- END:{marker} -->)", re.S
    )
    if not pattern.search(text):
        raise SystemExit(
            f"错误: {page_name or '页面文件'} 中找不到 {marker} 标记区块\n"
            f"  需要存在 <!-- BEGIN:{marker} --> 与 <!-- END:{marker} -->"
        )
    return pattern.sub(lambda m: f"{m.group(1)}\n{payload}\n{m.group(3)}", text)


def replace_count(text: str, which: str, count: int) -> str:
    pattern = re.compile(
        rf'(<span class="section-count" data-count="{which}">)\d+(</span>)'
    )
    return pattern.sub(lambda m: f"{m.group(1)}{count}{m.group(2)}", text)


def main():
    parser = argparse.ArgumentParser(description="BibTeX -> homepage publication blocks")
    parser.add_argument("--bib", default="refs.bib", help="BibTeX 文件 (默认 refs.bib)")
    parser.add_argument("--page", default="page.html", help="目标页面 (默认 page.html)")
    parser.add_argument("--dry-run", action="store_true", help="只统计，不写文件")
    args = parser.parse_args()

    try:
        entries_raw = load_bib(args.bib)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.bib}")
        sys.exit(1)

    entries = sorted(
        entries_raw,
        key=lambda e: (clean_field(entry_get(e, "year", "0")), clean_field(entry_get(e, "title"))),
        reverse=True,
    )
    for e in entries:
        if not entry_get(e, "ID") and isinstance(e, dict):
            e["ID"] = re.sub(r"\W+", "-", clean_field(entry_get(e, "title"))[:40]).strip("-").lower()

    selected_html = build_selected(entries)
    all_html = build_all(entries)
    selected_count = sum(1 for e in entries if is_true(entry_get(e, "selected")))

    print(f"共 {len(entries)} 篇文献，其中精选 {selected_count} 篇")
    for e in entries:
        flag = "★" if is_true(entry_get(e, "selected")) else " "
        print(f"  {flag} {clean_field(entry_get(e, 'year'))}  {clean_field(entry_get(e, 'title'))[:70]}")

    if args.dry_run:
        print("\n(--dry-run，未写入文件)")
        return

    try:
        with open(args.page, "r", encoding="utf-8") as f:
            page = f.read()
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.page}")
        sys.exit(1)

    page = replace_block(page, "SELECTED", selected_html, args.page)
    page = replace_block(page, "ALL", all_html, args.page)
    page = replace_count(page, "selected", selected_count)
    page = replace_count(page, "all", len(entries))

    with open(args.page, "w", encoding="utf-8") as f:
        f.write(page)

    print(f"\n✅ 已更新 {args.page}")


if __name__ == "__main__":
    main()
