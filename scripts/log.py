#!/usr/bin/env python3
"""Record an attempt: insert into attempts."""
from __future__ import annotations

import argparse
import datetime as dt
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "practice.db"
KINDS = ("card", "impl", "advanced")
RESULTS = {"o": 1, "x": 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("technique_id")
    parser.add_argument("kind", choices=KINDS)
    parser.add_argument("result", choices=RESULTS.keys(), help="o=correct, x=wrong")
    parser.add_argument("--uri", help="problem URI (typically for advanced)")
    parser.add_argument("--note")
    parser.add_argument("--db", default=str(DB_PATH))
    args = parser.parse_args()

    correct = RESULTS[args.result]
    asked_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    conn = sqlite3.connect(args.db)
    try:
        exists = conn.execute(
            "SELECT 1 FROM techniques WHERE id = ?", (args.technique_id,)
        ).fetchone()
        if not exists:
            print(f"unknown technique_id: {args.technique_id}", file=sys.stderr)
            return 1
        cur = conn.execute(
            "INSERT INTO attempts (technique_id, kind, problem_uri, correct, asked_at, note) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (args.technique_id, args.kind, args.uri, correct, asked_at, args.note),
        )
        conn.commit()
        print(f"#{cur.lastrowid} {args.technique_id} {args.kind} {args.result} {asked_at}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
