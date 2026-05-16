#!/usr/bin/env python3
"""Pick the next (technique, kind) to practice.

Priority:
  1. Never-attempted (technique, kind) pairs.
  2. SRS-due pairs (derived from attempts).
  3. Everything else.
Ties are broken randomly.

SRS rule (derived, no state table):
  Count `reps` = current streak of consecutive correct attempts (newest first).
  interval_days = 2 ** min(reps, 7)
  Due if last_at + interval_days < now.
"""
from __future__ import annotations

import argparse
import datetime as dt
import random
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "practice.db"
KINDS = ("card", "impl", "advanced")


def streak(rows: list[tuple[int, str]]) -> int:
    """Count current correct streak (rows are newest-first)."""
    n = 0
    for correct, _ in rows:
        if correct:
            n += 1
        else:
            break
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tech", help="restrict to a single technique id")
    parser.add_argument("--kind", choices=KINDS, help="restrict to a single kind")
    parser.add_argument("--db", default=str(DB_PATH))
    parser.add_argument("--seed", type=int, help="random seed for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    where_t = "WHERE id = ?" if args.tech else ""
    params_t: tuple = (args.tech,) if args.tech else ()
    techniques = conn.execute(
        f"SELECT id, name FROM techniques {where_t} ORDER BY id", params_t
    ).fetchall()
    if not techniques:
        print("no techniques found", file=sys.stderr)
        return 1

    kinds = (args.kind,) if args.kind else KINDS

    now = dt.datetime.now(dt.timezone.utc)
    unseen: list[tuple[str, str, str]] = []
    due: list[tuple[str, str, str]] = []
    other: list[tuple[str, str, str]] = []

    for t in techniques:
        for kind in kinds:
            rows = conn.execute(
                "SELECT correct, asked_at FROM attempts "
                "WHERE technique_id = ? AND kind = ? "
                "ORDER BY asked_at DESC",
                (t["id"], kind),
            ).fetchall()
            entry = (t["id"], t["name"], kind)
            if not rows:
                unseen.append(entry)
                continue
            reps = streak([(r["correct"], r["asked_at"]) for r in rows])
            last_at = dt.datetime.fromisoformat(rows[0]["asked_at"])
            interval = dt.timedelta(days=2 ** min(reps, 7))
            if last_at + interval < now:
                due.append(entry)
            else:
                other.append(entry)

    bucket = unseen or due or other
    if not bucket:
        print("nothing to ask", file=sys.stderr)
        return 1

    tech_id, name, kind = random.choice(bucket)
    bucket_label = (
        "unseen" if bucket is unseen else "due" if bucket is due else "fresh"
    )
    print(f"{tech_id}\t{kind}\t{name}\t[{bucket_label}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
