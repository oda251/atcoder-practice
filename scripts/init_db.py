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

# Primary technique per typical90 problem. Approximate — refine as needed.
TYPICAL90 = [
    "二分探索（答え）",                 # 001 Yokan Party
    "bit全探索",                        # 002 Encyclopedia of Parentheses
    "木の直径",                          # 003 Longest Circular Road
    "累積和",                            # 004 Cross Sum
    "行列累乗",                          # 005 Restricted Digits
    "辞書順最小",                        # 006 Smallest Subsequence
    "ソート+二分探索",                  # 007 CP Classes
    "部分文字列DP",                      # 008 AtCounter
    "偏角ソート",                        # 009 Three Point Angle
    "累積和",                            # 010 Score Sum Queries
    "スケジューリングDP",                # 011 Gravy Jobs
    "Union-Find",                       # 012 Red Painting
    "ダイクストラ",                      # 013 Passing
    "ソート貪欲",                        # 014 We Used to Sing a Song Together
    "約数列挙",                          # 015 Don't be too close
    "全探索",                            # 016 Minimum Coins
    "平面走査+BIT",                      # 017 Crossing Segments
    "幾何（三角関数）",                  # 018 Statue of Chokudai
    "区間DP",                            # 019 Pick Two
    "浮動小数の罠",                      # 020 Log Inequality
    "強連結成分分解",                    # 021 Come Back in One Piece
    "GCD",                              # 022 Cubic Cake
    "bitDP",                            # 023 Avoid War
    "パリティ",                          # 024 Select +／- One
    "メタ問題",                          # 025 Digit Product Equation
    "木の二部塗り分け",                  # 026 Independent Set on a Tree
    "集合・重複検出",                    # 027 Sign Up Requests
    "二次元いもす法",                    # 028 Cluttered Paper
    "遅延セグメント木",                  # 029 Long Bricks
    "エラトステネスの篩",                # 030 K Factors
    "Grundy数",                          # 031 VS AtCoder
    "順列全探索",                        # 032 AtCoder Ekiden
    "単純数え上げ",                      # 033 Not Too Bright
    "尺取り法",                          # 034 There are few types of elements
    "仮想木・LCA",                       # 035 Preserve Connectivity
    "45度回転",                          # 036 Max Manhattan Distance
    "Convex Hull Trick",                 # 037 Don't Leave the Spice
    "LCM・桁数",                         # 038 Large LCM
    "全方位木DP",                        # 039 Tree Distance
    "最小カット",                        # 040 Get More Money
    "凸包",                              # 041 Piles in AtCoder Farm
    "mod DP",                           # 042 Multiple of 9
    "01-BFS",                           # 043 Maze Challenge with Lack of Sleep
    "循環シフト",                        # 044 Shift and Swapping
    "bitDP（集合）",                     # 045 Simple Grouping
    "mod 数え上げ",                      # 046 I Love 46
    "Z-algorithm",                       # 047 Monochromatic Diagonal
    "貪欲+ソート",                       # 048 I will not drop out
    "平方分割",                          # 049 Flip Digits 2
    "漸化式DP",                          # 050 Stair Jump
    "半分全列挙",                        # 051 Typical Shop
    "期待値",                            # 052 Dice Product
    "インタラクティブ二分探索",          # 053 Discrete Dowsing
    "ハイパーグラフBFS",                  # 054 Takahashi Number
    "多重ループ全探索",                  # 055 Select 5
    "bitDP（部分和）",                    # 056 Lucky Bag
    "XOR Gauss消去",                     # 057 Flip Flap
    "ダブリング",                        # 058 Original Calculator
    "bitset到達判定",                    # 059 Many Graph Queries
    "LIS",                              # 060 Chimera
    "deque",                             # 061 Deck
    "逆辺トポロジカルソート",            # 062 Paint All
    "bit集合数え上げ",                   # 063 Monochromatic Subgrid
    "階差・差分配列",                    # 064 Uplift
    "包除原理",                          # 065 RGB Balls 2
    "期待値の線形性",                    # 066 Various Arrays
    "進数変換",                          # 067 Base 8 to 9
    "重み付きUnion-Find",                # 068 Paired Information
    "累乗数え上げ",                      # 069 Colorful Blocks 2
    "中央値",                            # 070 Plant Planning
    "トポロジカル順序列挙",              # 071 Fuzzy Priority
    "DFSサイクル検出",                   # 072 Loop Railway Plan
    "木DP",                              # 073 We Need Both a and b
    "三進数DP",                          # 074 ABC String 2
    "素因数分解",                        # 075 Magic For Balls
    "尺取り法",                          # 076 Cake Cut
    "二部マッチング",                    # 077 Planes on a 2D Plane
    "グラフ次数集計",                    # 078 Easy Graph Problem
    "貪欲シミュレーション",              # 079 Two by Two
    "包除+bitDP",                        # 080 Let's Share Bit
    "二次元いもす法（応用）",            # 081 Friendly Group
    "桁数別の和",                        # 082 Counting Numbers
    "平方分割（クエリ）",                # 083 Colorful Graph
    "尺取り法",                          # 084 There are two types of characters
    "約数列挙+探索",                     # 085 Multiplication 085
    "bit独立計算",                       # 086 Snuke's Favorite Arrays
    "二分探索",                          # 087 Chokudai's Demand
    "鳩の巣原理",                        # 088 Similar but Different Ways
    "セグ木DP",                          # 089 Partitions and Inversions
    "数え上げ+包除",                     # 090 Tenkei90's Last Problem
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
