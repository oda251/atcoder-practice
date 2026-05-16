#!/usr/bin/env python3
"""Initialize practice.db: create schema and seed typical90 techniques."""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "practice.db"

SCHEMA = """
CREATE TABLE techniques (
  id   TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE attempts (
  id            INTEGER PRIMARY KEY,
  technique_id  TEXT NOT NULL REFERENCES techniques(id),
  kind          TEXT NOT NULL CHECK (kind IN ('card','impl','advanced')),
  problem_uri   TEXT,
  correct       INTEGER NOT NULL CHECK (correct IN (0,1)),
  asked_at      TEXT NOT NULL,
  note          TEXT
);

CREATE INDEX idx_attempts_tk ON attempts(technique_id, kind);

CREATE VIEW stats AS
SELECT t.id           AS technique_id,
       t.name         AS name,
       a.kind         AS kind,
       COUNT(*)       AS n,
       SUM(a.correct) AS ok,
       ROUND(AVG(a.correct) * 100.0, 1) AS acc,
       MAX(a.asked_at) AS last_at
FROM techniques t
JOIN attempts a ON a.technique_id = t.id
GROUP BY t.id, a.kind;
"""

TYPICAL90 = [
    "Yokan Party（★4）",
    "Encyclopedia of Parentheses（★3）",
    "Longest Circular Road（★4）",
    "Cross Sum（★2）",
    "Restricted Digits（★7）",
    "Smallest Subsequence（★5）",
    "CP Classes（★3）",
    "AtCounter（★4）",
    "Three Point Angle（★6）",
    "Score Sum Queries（★2）",
    "Gravy Jobs（★6）",
    "Red Painting（★4）",
    "Passing（★5）",
    "We Used to Sing a Song Together（★3）",
    "Don't be too close（★6）",
    "Minimum Coins（★3）",
    "Crossing Segments（★7）",
    "Statue of Chokudai（★3）",
    "Pick Two（★6）",
    "Log Inequality（★3）",
    "Come Back in One Piece（★5）",
    "Cubic Cake（★2）",
    "Avoid War（★7）",
    "Select +／- One（★2）",
    "Digit Product Equation（★7）",
    "Independent Set on a Tree（★4）",
    "Sign Up Requests（★2）",
    "Cluttered Paper（★4）",
    "Long Bricks（★5）",
    "K Factors（★5）",
    "VS AtCoder（★6）",
    "AtCoder Ekiden（★3）",
    "Not Too Bright（★2）",
    "There are few types of elements（★4）",
    "Preserve Connectivity（★7）",
    "Max Manhattan Distance（★5）",
    "Don't Leave the Spice（★5）",
    "Large LCM（★3）",
    "Tree Distance（★5）",
    "Get More Money（★7）",
    "Piles in AtCoder Farm（★7）",
    "Multiple of 9（★4）",
    "Maze Challenge with Lack of Sleep（★4）",
    "Shift and Swapping（★3）",
    "Simple Grouping（★6）",
    "I Love 46（★3）",
    "Monochromatic Diagonal（★7）",
    "I will not drop out（★3）",
    "Flip Digits 2（★6）",
    "Stair Jump（★3）",
    "Typical Shop（★5）",
    "Dice Product（★3）",
    "Discrete Dowsing（★7）",
    "Takahashi Number（★6）",
    "Select 5（★2）",
    "Lucky Bag（★5）",
    "Flip Flap（★6）",
    "Original Calculator（★4）",
    "Many Graph Queries（★7）",
    "Chimera（★5）",
    "Deck（★2）",
    "Paint All（★6）",
    "Monochromatic Subgrid（★4）",
    "Uplift（★3）",
    "RGB Balls 2（★7）",
    "Various Arrays（★5）",
    "Base 8 to 9（★2）",
    "Paired Information（★5）",
    "Colorful Blocks 2（★3）",
    "Plant Planning（★4）",
    "Fuzzy Priority（★7）",
    "Loop Railway Plan（★4）",
    "We Need Both a and b（★5）",
    "ABC String 2（★6）",
    "Magic For Balls（★3）",
    "Cake Cut（★3）",
    "Planes on a 2D Plane（★7）",
    "Easy Graph Problem（★2）",
    "Two by Two（★3）",
    "Let's Share Bit（★6）",
    "Friendly Group（★5）",
    "Counting Numbers（★3）",
    "Colorful Graph（★6）",
    "There are two types of characters（★3）",
    "Multiplication 085（★4）",
    "Snuke's Favorite Arrays（★5）",
    "Chokudai's Demand（★5）",
    "Similar but Different Ways（★6）",
    "Partitions and Inversions（★7）",
    "Tenkei90's Last Problem（★7）",
]

assert len(TYPICAL90) == 90, f"expected 90 titles, got {len(TYPICAL90)}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="recreate the DB if it exists")
    parser.add_argument("--db", default=str(DB_PATH), help="path to SQLite DB")
    args = parser.parse_args()

    db = Path(args.db)
    if db.exists():
        if not args.force:
            print(f"{db} already exists. Use --force to recreate.", file=sys.stderr)
            return 1
        db.unlink()

    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    try:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO techniques (id, name) VALUES (?, ?)",
            [(f"typical90-{i:03d}", name) for i, name in enumerate(TYPICAL90, start=1)],
        )
        conn.commit()
    finally:
        conn.close()

    print(f"Initialized {db} with {len(TYPICAL90)} techniques.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
