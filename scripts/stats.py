#!/usr/bin/env python3
"""Show practice stats from the `stats` view."""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "practice.db"
KINDS = ("card", "impl", "advanced")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tech", help="filter by technique id")
    parser.add_argument("--kind", choices=KINDS, help="filter by kind")
    parser.add_argument("--db", default=str(DB_PATH))
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    sql = "SELECT technique_id, name, kind, n, ok, acc, last_at FROM stats"
    conds, params = [], []
    if args.tech:
        conds.append("technique_id = ?")
        params.append(args.tech)
    if args.kind:
        conds.append("kind = ?")
        params.append(args.kind)
    if conds:
        sql += " WHERE " + " AND ".join(conds)
    sql += " ORDER BY technique_id, kind"

    rows = conn.execute(sql, params).fetchall()

    if not rows:
        print("no attempts recorded yet")
        return 0

    print(f"{'technique':<22}{'kind':<10}{'n':>4}{'ok':>4}{'acc%':>7}  last_at")
    print("-" * 72)
    for r in rows:
        print(
            f"{r['technique_id']:<22}{r['kind']:<10}{r['n']:>4}{r['ok']:>4}"
            f"{(r['acc'] or 0):>7.1f}  {r['last_at']}"
        )

    # overall summary per kind
    summary_sql = (
        "SELECT a.kind, COUNT(*) AS n, SUM(a.correct) AS ok, "
        "ROUND(AVG(a.correct) * 100.0, 1) AS acc, MAX(a.asked_at) AS last_at "
        "FROM attempts a"
    )
    sconds, sparams = [], []
    if args.tech:
        sconds.append("a.technique_id = ?")
        sparams.append(args.tech)
    if args.kind:
        sconds.append("a.kind = ?")
        sparams.append(args.kind)
    if sconds:
        summary_sql += " WHERE " + " AND ".join(sconds)
    summary_sql += " GROUP BY a.kind ORDER BY a.kind"

    print()
    print("== summary by kind ==")
    print(f"{'kind':<10}{'n':>4}{'ok':>4}{'acc%':>7}  last_at")
    print("-" * 50)
    for r in conn.execute(summary_sql, sparams).fetchall():
        print(
            f"{r['kind']:<10}{r['n']:>4}{r['ok']:>4}"
            f"{(r['acc'] or 0):>7.1f}  {r['last_at']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
