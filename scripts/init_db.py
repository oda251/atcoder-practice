#!/usr/bin/env python3
"""Initialize practice.db: schema + technique catalog seed.

Catalog uses Japanese names as natural keys; variation_of expresses
the parent technique when this entry is a true variant of another
(NOT a category grouping).
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "practice.db"

SCHEMA = """
CREATE TABLE techniques (
  name         TEXT PRIMARY KEY,
  variation_of TEXT REFERENCES techniques(name)
);

CREATE INDEX idx_techniques_variation ON techniques(variation_of);

CREATE TABLE attempts (
  id          INTEGER PRIMARY KEY,
  technique   TEXT NOT NULL REFERENCES techniques(name),
  kind        TEXT NOT NULL CHECK (kind IN ('card','impl','advanced')),
  problem_uri TEXT,
  correct     INTEGER NOT NULL CHECK (correct IN (0,1)),
  asked_at    TEXT NOT NULL,
  note        TEXT
);

CREATE INDEX idx_attempts_tk ON attempts(technique, kind);

CREATE VIEW stats AS
SELECT t.name         AS technique,
       t.variation_of AS variation_of,
       a.kind         AS kind,
       COUNT(*)       AS n,
       SUM(a.correct) AS ok,
       ROUND(AVG(a.correct) * 100.0, 1) AS acc,
       MAX(a.asked_at) AS last_at
FROM techniques t
JOIN attempts a ON a.technique = t.name
GROUP BY t.name, a.kind;
"""

# (name, variation_of). Parents listed before children where possible;
# SQLite FK enforcement is off by default so absolute order is not required.
TECHNIQUES: list[tuple[str, str | None]] = [
    # ===== DP =====
    ("1次元DP",                       None),
    ("漸化式DP",                      "1次元DP"),
    ("in-placeローリングDP",          "1次元DP"),
    ("ナップサックDP",                None),
    ("LIS",                           None),
    ("LCS",                           None),
    ("編集距離",                      "LCS"),
    ("区間DP",                        None),
    ("bitDP",                         None),
    ("部分和bitDP",                   "bitDP"),
    ("集合分割bitDP",                 "bitDP"),
    ("TSPbitDP",                      "bitDP"),
    ("Sum over Subsets DP",           "bitDP"),
    ("木DP",                          None),
    ("全方位木DP",                    "木DP"),
    ("桁DP",                          None),
    ("k進数DP",                       "桁DP"),
    ("mod DP",                        None),
    ("確率DP",                        None),
    ("期待値DP",                      "確率DP"),
    ("部分文字列DP",                  None),
    ("スケジューリングDP",            None),
    ("グリッドDP",                    None),
    ("行列累乗DP",                    None),
    ("セグメント木DP高速化",          None),
    ("スライド最小値DP高速化",        None),
    ("Convex Hull Trick",             None),
    ("分割統治DP高速化",              None),
    ("Monge最適化",                   None),

    # ===== グラフ探索 =====
    ("BFS",                           None),
    ("01-BFS",                        "BFS"),
    ("多点スタートBFS",               "BFS"),
    ("ハイパーグラフBFS",             "BFS"),
    ("DFS",                           None),
    ("DFSサイクル検出",               "DFS"),
    ("再帰DFS全列挙",                 "DFS"),

    # ===== 最短経路 =====
    ("ダイクストラ",                  None),
    ("ベルマン–フォード",             None),
    ("SPFA",                          "ベルマン–フォード"),
    ("ワーシャル–フロイド",           None),

    # ===== 最小全域木 =====
    ("最小全域木",                    None),
    ("Kruskal",                       "最小全域木"),
    ("Prim",                          "最小全域木"),

    # ===== トポロジカル =====
    ("トポロジカルソート",            None),
    ("トポロジカル順序の列挙",        "トポロジカルソート"),
    ("逆辺トポロジカルソート",        "トポロジカルソート"),

    # ===== 連結成分・低リンク =====
    ("強連結成分分解",                None),
    ("2-SAT",                         "強連結成分分解"),
    ("橋・関節点",                    None),
    ("二重連結成分分解",              "橋・関節点"),

    # ===== 二部グラフ =====
    ("二部グラフ判定",                None),
    ("木の二部塗り分け",              "二部グラフ判定"),
    ("二部マッチング",                None),

    # ===== ダブリング（先に親） =====
    ("ダブリング",                    None),

    # ===== 木 =====
    ("木の直径",                      None),
    ("LCA",                           None),
    ("仮想木",                        "LCA"),
    ("オイラーツアー",                None),
    ("Heavy-Light分解",               None),
    ("重心分解",                      None),
    ("ファンクショナルグラフ",        None),
    ("ダブリング（木のk個上）",       "ダブリング"),

    # ===== フロー =====
    ("最大流",                        None),
    ("最小カット",                    "最大流"),
    ("最小費用流",                    "最大流"),

    # ===== グラフ・その他 =====
    ("次数集計・握手補題",            None),

    # ===== 文字列 =====
    ("Z-algorithm",                   None),
    ("KMP",                           None),
    ("ローリングハッシュ",            None),
    ("Suffix Array",                  None),
    ("LCP配列",                       "Suffix Array"),
    ("Aho-Corasick",                  None),
    ("Trie木",                        None),
    ("Manacher",                      None),
    ("辞書順最小構成",                None),
    ("ランレングス圧縮",              None),

    # ===== 整数論 =====
    ("GCD / LCM",                     None),
    ("拡張ユークリッド互除法",        "GCD / LCM"),
    ("中国剰余定理",                  "拡張ユークリッド互除法"),
    ("繰り返し二乗法",                None),
    ("modの逆元",                     "繰り返し二乗法"),
    ("mod二項係数",                   "modの逆元"),
    ("篩",                            None),
    ("エラトステネスの篩",            "篩"),
    ("線形篩",                        "篩"),
    ("素因数分解",                    None),
    ("約数列挙",                      None),
    ("Miller–Rabin / Pollard's rho",  "素因数分解"),
    ("オイラーのトーシェント関数",    None),
    ("メビウス関数",                  None),
    ("進数変換",                      None),
    ("桁和・桁ごと寄与計算",          None),

    # ===== 幾何 =====
    ("三角関数の基本",                None),
    ("ベクトル外積・内積",            None),
    ("CCW",                           "ベクトル外積・内積"),
    ("線分交差判定",                  "CCW"),
    ("凸包",                          None),
    ("45度回転",                      None),
    ("偏角ソート",                    None),
    ("最近点対",                      None),
    ("浮動小数の罠",                  None),

    # ===== データ構造（線形） =====
    ("スタック",                      None),
    ("キュー",                        None),
    ("deque",                         "キュー"),
    ("優先度付きキュー",              None),
    ("中央値管理（2-heap）",          "優先度付きキュー"),
    ("set / map",                     None),
    ("multiset",                      "set / map"),

    # ===== データ構造（Union-Find） =====
    ("Union-Find",                    None),
    ("重み付きUnion-Find",            "Union-Find"),

    # ===== データ構造（区間） =====
    ("BIT",                           None),
    ("セグメント木",                  None),
    ("遅延セグメント木",              "セグメント木"),
    ("平面走査 + BIT/セグ木",         None),
    ("平方分割",                      None),
    ("Mo's algorithm",                "平方分割"),
    ("Sparse Table",                  None),
    ("bitset高速化",                  None),

    # ===== 累積和・差分 =====
    ("累積和",                        None),
    ("二次元累積和",                  "累積和"),
    ("いもす法",                      None),
    ("二次元いもす法",                "いもす法"),
    ("階差・差分配列",                None),
    ("座標圧縮",                      None),

    # ===== 全探索 =====
    ("多重ループ全探索",              None),
    ("bit全探索",                     None),
    ("部分集合の部分集合列挙",        "bit全探索"),
    ("順列全探索",                    None),
    ("半分全列挙",                    None),

    # ===== 二分探索・尺取り =====
    ("二分探索",                      None),
    ("答えで二分探索",                "二分探索"),
    ("インタラクティブ二分探索",      "二分探索"),
    ("三分探索",                      None),
    ("尺取り法",                      None),
    ("循環シフト探索",                None),

    # ===== 貪欲・構築 =====
    ("ソート + 貪欲",                 None),
    ("交換論法",                      "ソート + 貪欲"),
    ("貪欲シミュレーション",          None),
    ("パリティ",                      None),
    ("不変量",                        None),
    ("鳩の巣原理",                    None),
    ("構築",                          None),
    ("メタ的考察",                    None),
    ("bitごと独立に計算",             None),
    ("Grundy数 / Nim",                None),
    ("XOR連立方程式",                 None),

    # ===== 数え上げ・確率 =====
    ("組合せ・順列の基本",            None),
    ("包除原理",                      None),
    ("期待値の線形性",                None),
    ("期待値の計算",                  None),
    ("mod数え上げ",                   None),
    ("累乗数え上げ",                  None),
    ("単純数え上げ・寄与計算",        None),
    ("中央値の最適性",                None),
    ("集合・重複検出",                None),

    # ===== 数学・その他 =====
    ("FFT / NTT",                     None),
    ("行列演算の基本",                None),
    ("LCM・桁数評価",                 None),
]

# Typical 90 -> technique names. Reference for Claude when impl picks
# a real problem to present. Not stored in DB.
TYPICAL90_MAP: dict[int, list[str]] = {
    1:  ["答えで二分探索"],
    2:  ["bit全探索"],
    3:  ["木の直径"],
    4:  ["累積和"],
    5:  ["行列累乗DP"],
    6:  ["辞書順最小構成", "Sparse Table"],
    7:  ["二分探索"],
    8:  ["部分文字列DP"],
    9:  ["偏角ソート"],
    10: ["累積和"],
    11: ["スケジューリングDP"],
    12: ["Union-Find"],
    13: ["ダイクストラ"],
    14: ["ソート + 貪欲"],
    15: ["約数列挙"],
    16: ["多重ループ全探索"],
    17: ["平面走査 + BIT/セグ木", "BIT"],
    18: ["三角関数の基本"],
    19: ["区間DP"],
    20: ["浮動小数の罠"],
    21: ["強連結成分分解"],
    22: ["GCD / LCM"],
    23: ["bitDP"],
    24: ["パリティ"],
    25: ["メタ的考察"],
    26: ["木の二部塗り分け"],
    27: ["集合・重複検出"],
    28: ["二次元いもす法"],
    29: ["遅延セグメント木"],
    30: ["エラトステネスの篩"],
    31: ["Grundy数 / Nim"],
    32: ["順列全探索"],
    33: ["単純数え上げ・寄与計算"],
    34: ["尺取り法"],
    35: ["仮想木", "LCA"],
    36: ["45度回転"],
    37: ["Convex Hull Trick"],
    38: ["LCM・桁数評価"],
    39: ["全方位木DP"],
    40: ["最小カット"],
    41: ["凸包"],
    42: ["mod DP"],
    43: ["01-BFS"],
    44: ["循環シフト探索"],
    45: ["集合分割bitDP"],
    46: ["mod数え上げ"],
    47: ["Z-algorithm"],
    48: ["ソート + 貪欲"],
    49: ["平方分割"],
    50: ["漸化式DP"],
    51: ["半分全列挙"],
    52: ["期待値の計算"],
    53: ["インタラクティブ二分探索"],
    54: ["ハイパーグラフBFS"],
    55: ["多重ループ全探索"],
    56: ["部分和bitDP"],
    57: ["XOR連立方程式"],
    58: ["ダブリング"],
    59: ["bitset高速化"],
    60: ["LIS"],
    61: ["deque"],
    62: ["逆辺トポロジカルソート"],
    63: ["bit全探索", "単純数え上げ・寄与計算"],
    64: ["階差・差分配列"],
    65: ["包除原理"],
    66: ["期待値の線形性"],
    67: ["進数変換"],
    68: ["重み付きUnion-Find"],
    69: ["累乗数え上げ"],
    70: ["中央値の最適性"],
    71: ["トポロジカル順序の列挙"],
    72: ["DFSサイクル検出"],
    73: ["木DP"],
    74: ["k進数DP"],
    75: ["素因数分解"],
    76: ["尺取り法"],
    77: ["二部マッチング"],
    78: ["次数集計・握手補題"],
    79: ["貪欲シミュレーション"],
    80: ["包除原理", "bitDP"],
    81: ["二次元いもす法"],
    82: ["桁和・桁ごと寄与計算"],
    83: ["平方分割"],
    84: ["尺取り法"],
    85: ["約数列挙"],
    86: ["bitごと独立に計算"],
    87: ["二分探索"],
    88: ["鳩の巣原理"],
    89: ["セグメント木DP高速化"],
    90: ["包除原理", "mod数え上げ"],
}

assert len({n for n, _ in TECHNIQUES}) == len(TECHNIQUES), "duplicate technique name"


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
            "INSERT INTO techniques (name, variation_of) VALUES (?, ?)",
            TECHNIQUES,
        )
        conn.commit()
        # verify variation_of references resolve
        names = {n for n, _ in TECHNIQUES}
        bad = [(n, v) for n, v in TECHNIQUES if v is not None and v not in names]
        if bad:
            print(f"WARNING: dangling variation_of references: {bad}", file=sys.stderr)
            return 1
    finally:
        conn.close()

    print(f"Initialized {db} with {len(TECHNIQUES)} techniques.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
