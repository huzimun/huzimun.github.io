#!/usr/bin/env python3
"""
bib2qmd.py — BibTeX 批量导入 Quarto 学术主页
用法:
    python bib2qmd.py                 # 读取 refs.bib 生成 publications.qmd
    python bib2qmd.py --bib my.bib    # 指定其他 bib 文件

依赖: pip install bibtexparser
"""
import argparse
import re
import sys

try:
    import bibtexparser
except ImportError:
    print("错误: 缺少依赖 bibtexparser，请先执行:")
    print("  pip install bibtexparser")
    sys.exit(1)


def clean_field(value: str) -> str:
    """去除 BibTeX 字段中的花括号与多余空白"""
    return re.sub(r"\s+", " ", value.replace("{", "").replace("}", "")).strip()


def format_authors(author_str: str) -> str:
    """将 'Lastname, Firstname and ...' 格式化为 'F. Lastname, ...' 并加粗本人姓名"""
    names = [n.strip() for n in author_str.split(" and ") if n.strip()]
    formatted = []
    for name in names:
        if "," in name:
            last, first = name.split(",", 1)
            initials = " ".join(f"{p[0]}." for p in first.strip().split() if p)
            formatted.append(f"{initials} {last.strip()}")
        else:
            formatted.append(name)
    return ", ".join(formatted)


ENTRY_TYPE_MAP = {
    "article": "journal",
    "inproceedings": "conference",
    "incollection": "book chapter",
    "phdthesis": "thesis",
    "mastersthesis": "thesis",
    "techreport": "technical report",
    "unpublished": "preprint",
    "misc": "preprint",
}


def get_entry_type(entry) -> str:
    """兼容 bibtexparser 1.x (dict['ENTRYTYPE']) 与对象属性两种形式"""
    if isinstance(entry, dict):
        return entry.get("ENTRYTYPE", "misc").lower()
    return getattr(entry, "entry_type", "misc").lower()


def entry_to_markdown(entry: dict) -> str:
    title = clean_field(entry.get("title", "Untitled"))
    authors = format_authors(clean_field(entry.get("author", "")))
    etype = ENTRY_TYPE_MAP.get(get_entry_type(entry), "other")

    if etype == "journal":
        venue = clean_field(entry.get("journal", ""))
    elif etype == "conference":
        venue = clean_field(entry.get("booktitle", ""))
    else:
        venue = clean_field(entry.get("howpublished", ""))

    year = clean_field(entry.get("year", ""))
    vol = clean_field(entry.get("volume", ""))
    num = clean_field(entry.get("number", ""))
    pages = clean_field(entry.get("pages", "")).replace("--", "–")
    doi = clean_field(entry.get("doi", ""))
    url = clean_field(entry.get("url", ""))
    pdf = clean_field(entry.get("pdf", ""))  # 支持自定义 pdf 字段

    line = f"- **{title}**  \n  {authors}  \n  "
    venue_parts = [p for p in [f"*{venue}*", vol, f"({num})" if num else "", pages] if p]
    line += ", ".join(venue_parts)
    if year:
        line += f", {year}"
    line += "  \n"

    links = []
    if doi:
        links.append(f"[DOI](https://doi.org/{doi})")
    if url:
        links.append(f"[Link]({url})")
    if pdf:
        links.append(f"[PDF]({pdf})")
    if links:
        line += "  " + " · ".join(links) + "\n"

    return line


def main():
    parser = argparse.ArgumentParser(description="BibTeX -> Quarto publications page")
    parser.add_argument("--bib", default="refs.bib", help="BibTeX 文件路径 (默认 refs.bib)")
    parser.add_argument("--out", default="publications.qmd", help="输出 qmd 文件 (默认 publications.qmd)")
    args = parser.parse_args()

    try:
        with open(args.bib, "r", encoding="utf-8") as f:
            db = bibtexparser.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.bib}")
        sys.exit(1)

    entries = sorted(db.entries, key=lambda e: e.get("year", "0"), reverse=True)

    groups: dict = {}
    for e in entries:
        etype = ENTRY_TYPE_MAP.get(get_entry_type(e), "other")
        groups.setdefault(etype, []).append(e)

    SECTION_TITLES = {
        "journal": "## Journal Articles",
        "conference": "## Conference Papers",
        "book chapter": "## Book Chapters",
        "thesis": "## Theses",
        "preprint": "## Preprints",
        "technical report": "## Technical Reports",
        "other": "## Others",
    }
    ORDER = ["journal", "conference", "preprint", "book chapter", "thesis", "technical report", "other"]

    lines = [
        "---\n",
        'title: "Publications"\n',
        "---\n",
        "\n",
        "# Publications\n",
        "\n",
        f"共 {len(entries)} 篇，按年份倒序排列。由 `{args.bib}` 自动生成（运行 `python bib2qmd.py` 更新）。\n",
        "\n",
    ]

    for key in ORDER:
        if key not in groups:
            continue
        lines.append(SECTION_TITLES[key] + "\n\n")
        for e in groups[key]:
            lines.append(entry_to_markdown(e))
        lines.append("\n")

    with open(args.out, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ 已生成 {args.out}，共 {len(entries)} 条文献")
    for key in ORDER:
        if key in groups:
            print(f"   - {SECTION_TITLES[key].strip('# ')}: {len(groups[key])} 篇")


if __name__ == "__main__":
    main()
