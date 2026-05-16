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
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[3] / "data" / "practice.db"
KINDS = ("card", "impl", "advanced")


def streak(rows: list[tuple[int, str]]) -> int:
    n = 0
    for correct, _ in rows:
        if correct:
            n += 1
        else:
            break
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tech", help="restrict to a single technique name")
    parser.add_argument("--variation-of", help="restrict to children of this parent technique")
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

    where, params = [], []
    if args.tech:
        where.append("name = ?")
        params.append(args.tech)
    if args.variation_of:
        where.append("variation_of = ?")
        params.append(args.variation_of)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    techniques = conn.execute(
        f"SELECT name, variation_of FROM techniques {where_sql} ORDER BY name",
        params,
    ).fetchall()
    if not techniques:
        print("no techniques match the filter", file=sys.stderr)
        return 1

    kinds = (args.kind,) if args.kind else KINDS

    now = dt.datetime.now(dt.timezone.utc)
    unseen, due, fresh = [], [], []
    for t in techniques:
        for kind in kinds:
            rows = conn.execute(
                "SELECT correct, asked_at FROM attempts "
                "WHERE technique = ? AND kind = ? "
                "ORDER BY asked_at DESC",
                (t["name"], kind),
            ).fetchall()
            entry = {
                "technique": t["name"],
                "variation_of": t["variation_of"],
                "kind": kind,
            }
            if not rows:
                entry["bucket"] = "unseen"
                unseen.append(entry)
                continue
            reps = streak([(r["correct"], r["asked_at"]) for r in rows])
            last_at = dt.datetime.fromisoformat(rows[0]["asked_at"].replace(" ", "T"))
            if last_at.tzinfo is None:
                last_at = last_at.replace(tzinfo=dt.timezone.utc)
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
    print(f"technique:    {pick['technique']}")
    if pick["variation_of"]:
        print(f"variation_of: {pick['variation_of']}")
    print(f"kind:         {pick['kind']}")
    print(f"bucket:       {pick['bucket']}")
    if "last_at" in pick:
        print(f"last_at:      {pick['last_at']}")
        print(f"reps:         {pick['reps']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
