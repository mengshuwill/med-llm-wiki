#!/usr/bin/env python3
"""
Read Zotero local SQLite database directly.
Usage:
  python zotero_reader.py list                              # list all collections
  python zotero_reader.py list --collection "GPT"          # list items in a collection
  python zotero_reader.py export --collection "GPT" --limit 10  # export items to raw/papers/
  python zotero_reader.py export --collection "GPT" --output /path/to/raw/papers/
"""

import argparse
import glob
import os
import re
import sqlite3
import sys


def find_zotero_db():
    candidates = [
        os.path.expanduser("~/Zotero/zotero.sqlite"),
        os.path.expanduser("~/Library/Application Support/Zotero/Profiles/*/zotero.sqlite"),
    ]
    for c in candidates:
        for path in sorted(glob.glob(c) if "*" in c else [c]):
            if os.path.exists(path):
                return path
    return None


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# Field IDs for common Zotero fields (stable across Zotero versions)
FIELDS = {
    1: "title",
    2: "abstractNote",
    6: "date",
    8: "shortTitle",
    13: "url",
    14: "accessDate",
    16: "extra",
    19: "volume",
    32: "pages",
    38: "publicationTitle",
    59: "DOI",
    76: "issue",
    78: "journalAbbreviation",
}

ITEM_TYPES = {
    8: "bookSection",
    11: "conferencePaper",
    22: "journalArticle",
    31: "preprint",
    34: "report",
    40: "webpage",
}


def parse_authors_from_creators_text(creator_summary):
    """Parse 'LastName, FirstName; LastName, FirstName' into formatted author list."""
    if not creator_summary:
        return []
    authors = []
    for c in creator_summary.split("\n"):
        c = c.strip()
        if not c:
            continue
        if "," in c:
            last, first = c.split(",", 1)
            authors.append(f"{first.strip()} {last.strip()}")
        else:
            authors.append(c)
    return authors


def get_collections(conn):
    rows = conn.execute("""
        SELECT c.collectionID, c.collectionName, c.parentCollectionID,
               COUNT(ci.itemID) AS item_count
        FROM collections c
        LEFT JOIN collectionItems ci ON c.collectionID = ci.collectionID
        WHERE c.collectionID > 1
        GROUP BY c.collectionID
        ORDER BY item_count DESC
    """).fetchall()
    return rows


def get_items_in_collection(conn, collection_name):
    rows = conn.execute("""
        SELECT i.itemID, i.key, it.typeName,
               GROUP_CONCAT(cr.lastName || ', ' || cr.firstName, '; ') AS authors,
               idv_title.value AS title,
               idv_date.value AS date,
               idv_pub.value AS journal,
               idv_doi.value AS doi,
               idv_abstract.value AS abstract,
               idv_extra.value AS extra,
               idv_url.value AS url,
               i.dateModified
        FROM items i
        JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
        JOIN collectionItems ci ON i.itemID = ci.itemID
        JOIN collections c ON ci.collectionID = c.collectionID
        LEFT JOIN itemCreators ic ON i.itemID = ic.itemID
        LEFT JOIN creators cr ON ic.creatorID = cr.creatorID AND ic.creatorTypeID = 8
        LEFT JOIN itemData id_title ON i.itemID = id_title.itemID AND id_title.fieldID = 1
        LEFT JOIN itemDataValues idv_title ON id_title.valueID = idv_title.valueID
        LEFT JOIN itemData id_date ON i.itemID = id_date.itemID AND id_date.fieldID = 6
        LEFT JOIN itemDataValues idv_date ON id_date.valueID = idv_date.valueID
        LEFT JOIN itemData id_pub ON i.itemID = id_pub.itemID AND id_pub.fieldID = 38
        LEFT JOIN itemDataValues idv_pub ON id_pub.valueID = idv_pub.valueID
        LEFT JOIN itemData id_doi ON i.itemID = id_doi.itemID AND id_doi.fieldID = 59
        LEFT JOIN itemDataValues idv_doi ON id_doi.valueID = idv_doi.valueID
        LEFT JOIN itemData id_abstract ON i.itemID = id_abstract.itemID AND id_abstract.fieldID = 2
        LEFT JOIN itemDataValues idv_abstract ON id_abstract.valueID = idv_abstract.valueID
        LEFT JOIN itemData id_extra ON i.itemID = id_extra.itemID AND id_extra.fieldID = 16
        LEFT JOIN itemDataValues idv_extra ON id_extra.valueID = idv_extra.valueID
        LEFT JOIN itemData id_url ON i.itemID = id_url.itemID AND id_url.fieldID = 13
        LEFT JOIN itemDataValues idv_url ON id_url.valueID = idv_url.valueID
        WHERE c.collectionName = ?
          AND i.itemTypeID IN (22, 31, 11, 8, 34)
        GROUP BY i.itemID
        ORDER BY i.dateModified DESC
    """, (collection_name,)).fetchall()
    return rows


def get_item_attachments(conn, item_id):
    rows = conn.execute("""
        SELECT ia.path, ia.contentType
        FROM itemAttachments ia
        WHERE ia.parentItemID = ? AND ia.linkMode IN (0, 2)
    """, (item_id,)).fetchall()
    return rows


def get_item_notes(conn, item_id):
    rows = conn.execute("""
        SELECT note, title FROM itemNotes WHERE parentItemID = ?
    """, (item_id,)).fetchall()
    return rows


def get_item_tags(conn, item_id):
    rows = conn.execute("""
        SELECT t.name FROM tags t
        JOIN itemTags it ON t.tagID = it.tagID
        WHERE it.itemID = ?
    """, (item_id,)).fetchall()
    return [r["name"] for r in rows]


def extract_pmid(extra):
    if not extra:
        return None
    m = re.search(r'PMID:\s*(\d+)', extra)
    if m:
        return m.group(1)
    return None


def format_markdown(item, conn):
    """Format a single Zotero item as a markdown file for the wiki's raw/papers/."""
    pmid = extract_pmid(item["extra"] or "")
    doi = item["doi"] or ""
    title = item["title"] or "Untitled"
    journal = item["journal"] or ""
    date_str = item["date"] or ""
    year = date_str[:4] if len(date_str) >= 4 else date_str

    authors_raw = parse_authors_from_creators_text(item["authors"])
    first_author = authors_raw[0].split()[-1] if authors_raw else "Unknown"

    # Build PMID-based filename
    if pmid:
        filename = f"PMID{pmid}_{first_author}_{year}.md"
    elif doi:
        doi_slug = doi.split("/")[-1].replace("/", "_")
        filename = f"DOI{doi_slug}_{first_author}_{year}.md"
    else:
        title_slug = re.sub(r'[^a-zA-Z0-9]+', '_', title[:60]).strip('_')
        filename = f"{first_author}_{year}_{title_slug}.md"

    # Get attachments
    attachments = get_item_attachments(conn, item["itemID"])
    attachment_paths = [a["path"] for a in attachments if a["path"]]

    # Get notes
    notes = get_item_notes(conn, item["itemID"])

    # Get tags
    tags = get_item_tags(conn, item["itemID"])

    lines = []
    lines.append("---")
    lines.append(f"zotero_key: {item['key']}")
    lines.append(f"title: \"{title}\"")
    lines.append(f"authors: \"{item['authors'] or ''}\"")
    if journal:
        lines.append(f"journal: \"{journal}\"")
    if year:
        lines.append(f"year: {year}")
    if doi:
        lines.append(f"doi: {doi}")
    if pmid:
        lines.append(f"pmid: {pmid}")
    if attachment_paths:
        lines.append(f"attachments:")
        for p in attachment_paths:
            lines.append(f"  - {p}")
    if tags:
        lines.append(f"tags: [{', '.join(tags)}]")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Authors:** {item['authors'] or 'N/A'}")
    lines.append("")
    lines.append(f"**Journal:** {journal or 'N/A'}")
    if year:
        lines.append(f"**Year:** {year}")
    if doi:
        lines.append(f"**DOI:** [{doi}](https://doi.org/{doi})")
    if pmid:
        lines.append(f"**PMID:** [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
    lines.append("")
    lines.append("## Abstract")
    lines.append("")
    if item["abstract"]:
        lines.append(item["abstract"].strip())
    else:
        lines.append("_No abstract available._")
    lines.append("")

    if notes:
        lines.append("## Zotero Notes")
        lines.append("")
        for n in notes:
            lines.append(f"- {n['title'] or 'Note'}: {n['note'] or ''}")
        lines.append("")

    if tags:
        lines.append(f"**Tags:** {', '.join(tags)}")
        lines.append("")

    return filename, "\n".join(lines)


def cmd_list(args, conn):
    if args.collection:
        items = get_items_in_collection(conn, args.collection)
        print(f"\nCollection: {args.collection} ({len(items)} items)")
        print("-" * 80)
        for i, item in enumerate(items, 1):
            title = (item["title"] or "Untitled")[:80]
            authors_raw = item["authors"] or ""
            first_author = authors_raw.split(";")[0].strip() if authors_raw else "N/A"
            date_str = (item["date"] or "....")[:4]
            doi = item["doi"] or ""
            print(f"  [{i}] {first_author} ({date_str}) {title}")
            if doi:
                print(f"      DOI: {doi}")
        print()
    else:
        rows = get_collections(conn)
        print(f"\nZotero Collections ({len(rows)} total)")
        print("-" * 60)
        for r in rows:
            print(f"  [{r['item_count']:>4}] {r['collectionName']}")
        print()


def cmd_export(args, conn):
    items = get_items_in_collection(conn, args.collection)
    if args.limit and args.limit > 0:
        items = items[:args.limit]

    outdir = args.output or os.path.join(os.getcwd(), "raw", "papers")
    os.makedirs(outdir, exist_ok=True)

    print(f"\nExporting {len(items)} items from '{args.collection}' to {outdir}/")
    print("-" * 60)

    exported = 0
    for item in items:
        filename, content = format_markdown(item, conn)
        filepath = os.path.join(outdir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        exported += 1
        title_short = (item["title"] or "Untitled")[:60]
        print(f"  [{exported}] {filename}")
        print(f"       {title_short}")

    print(f"\nExported {exported} files.\n")
    print(f"Next: run /med-llm-wiki ingest on each file, or batch ingest:")
    print(f"  for f in {outdir}/*.md; do /med-llm-wiki ingest \"$f\"; done")


def main():
    parser = argparse.ArgumentParser(description="Read Zotero SQLite and export papers for Med LLM Wiki")
    sub = parser.add_subparsers(dest="command")

    list_p = sub.add_parser("list", help="List collections or items in a collection")
    list_p.add_argument("--collection", "-c", help="Filter to items in a specific collection")

    export_p = sub.add_parser("export", help="Export items as markdown to raw/papers/")
    export_p.add_argument("--collection", "-c", required=True, help="Zotero collection name")
    export_p.add_argument("--output", "-o", help="Output directory (default: raw/papers/)")
    export_p.add_argument("--limit", "-n", type=int, help="Max items to export")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    db_path = find_zotero_db()
    if not db_path:
        print("Error: Zotero database not found at ~/Zotero/zotero.sqlite", file=sys.stderr)
        sys.exit(1)

    conn = connect(db_path)
    try:
        if args.command == "list":
            cmd_list(args, conn)
        elif args.command == "export":
            cmd_export(args, conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
