#!/usr/bin/env python3
"""Pick the next (technique, kind) to practice.

Priority: unseen > SRS-due > fresh. Tie-break: random.
SRS rule (derived from attempts, no state table):
  reps = consecutive correct attempts from the newest backwards.
  interval_days = 2 ** min(reps, 7)
  Due if last_at + interval_days < now.
"""
from __future__ import annotations

import argparse
import datetime as dt
import random
import re
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[3] / "data" / "practice.db"
KINDS = ("card", "impl", "advanced")
STAR_RE = re.compile(r"★(\d+)")


def streak(rows: list[tuple[int, str]]) -> int:
    n = 0
    for correct, _ in rows:
        if correct:
            n += 1
        else:
            break
    return n


def extract_stars(name: str) -> int:
    m = STAR_RE.search(name)
    return int(m.group(1)) if m else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tech", help="restrict to a single technique id")
    parser.add_argument("--kind", choices=KINDS, help="restrict to a single kind")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--seed", type=int, help="random seed (testing)")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    db = Path(args.db)
    if not db.exists():
        print(f"database not found: {db}", file=sys.stderr)
        print("hint: run `python3 scripts/init_db.py` first.", file=sys.stderr)
        return 1

    conn = sqlite3.connect(db)
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
    unseen, due, fresh = [], [], []
    for t in techniques:
        for kind in kinds:
            rows = conn.execute(
                "SELECT correct, asked_at FROM attempts "
                "WHERE technique_id = ? AND kind = ? "
                "ORDER BY asked_at DESC",
                (t["id"], kind),
            ).fetchall()
            entry = {
                "technique_id": t["id"],
                "name": t["name"],
                "stars": extract_stars(t["name"]),
                "kind": kind,
            }
            if not rows:
                entry["bucket"] = "unseen"
                unseen.append(entry)
                continue
            reps = streak([(r["correct"], r["asked_at"]) for r in rows])
            last_at = dt.datetime.fromisoformat(rows[0]["asked_at"])
            interval = dt.timedelta(days=2 ** min(reps, 7))
            if last_at + interval < now:
                entry["bucket"] = "due"
                entry["reps"] = reps
                entry["last_at"] = rows[0]["asked_at"]
                due.append(entry)
            else:
                entry["bucket"] = "fresh"
                entry["reps"] = reps
                entry["last_at"] = rows[0]["asked_at"]
                fresh.append(entry)

    bucket = unseen or due or fresh
    if not bucket:
        print("nothing to pick", file=sys.stderr)
        return 1

    pick = random.choice(bucket)
    print(f"technique_id: {pick['technique_id']}")
    print(f"name:         {pick['name']}")
    print(f"stars:        ★{pick['stars']}" if pick["stars"] else "stars:        (n/a)")
    print(f"kind:         {pick['kind']}")
    print(f"bucket:       {pick['bucket']}")
    if "last_at" in pick:
        print(f"last_at:      {pick['last_at']}")
        print(f"reps:         {pick['reps']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
