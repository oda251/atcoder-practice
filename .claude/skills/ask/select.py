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
PREREQ = {"card": None, "impl": "card", "advanced": "impl"}


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

    # Fetch all attempts once and group; avoids N+1 across techniques × kinds.
    attempts: dict[tuple[str, str], list[sqlite3.Row]] = {}
    for r in conn.execute(
        "SELECT technique, kind, correct, asked_at FROM attempts "
        "ORDER BY technique, kind, asked_at DESC"
    ):
        attempts.setdefault((r["technique"], r["kind"]), []).append(r)

    # Gate kind progression: impl needs prior card, advanced needs prior impl.
    # Only explicit --kind bypasses the gate (--tech still respects progression).
    explicit = bool(args.kind)

    now = dt.datetime.now(dt.timezone.utc)
    unseen, due, fresh = [], [], []
    for t in techniques:
        for kind in kinds:
            if not explicit:
                prereq = PREREQ[kind]
                if prereq is not None and not attempts.get((t["name"], prereq)):
                    continue
            rows = attempts.get((t["name"], kind), [])
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
            # SQLite `datetime('now')` returns naive UTC; tag as UTC for compare.
            last_at = dt.datetime.fromisoformat(rows[0]["asked_at"].replace(" ", "T"))
            if last_at.tzinfo is None:
                last_at = last_at.replace(tzinfo=dt.timezone.utc)
            entry["reps"] = reps
            entry["last_at"] = rows[0]["asked_at"]
            if last_at + dt.timedelta(days=2 ** min(reps, 7)) < now:
                entry["bucket"] = "due"
                due.append(entry)
            else:
                entry["bucket"] = "fresh"
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
