#!/usr/bin/env python3
"""Initialize practice.db: create schema and seed the technique catalog.

The catalog covers typical CP techniques as a self-contained taxonomy
(category -> technique). Typical 90 problems are *examples* of techniques,
not the primary entity. Mapping from typical90 problems to techniques is
documented in TYPICAL90_MAP for Claude's reference (not stored in DB).
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "practice.db"

SCHEMA = """
CREATE TABLE techniques (
  id       TEXT PRIMARY KEY,
  name     TEXT NOT NULL,
  category TEXT NOT NULL
);

CREATE INDEX idx_techniques_category ON techniques(category);

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
       t.category     AS category,
       a.kind         AS kind,
       COUNT(*)       AS n,
       SUM(a.correct) AS ok,
       ROUND(AVG(a.correct) * 100.0, 1) AS acc,
       MAX(a.asked_at) AS last_at
FROM techniques t
JOIN attempts a ON a.technique_id = t.id
GROUP BY t.id, a.kind;
"""

# (id, name, category)
TECHNIQUES: list[tuple[str, str, str]] = [
    # ===== dp =====
    ("dp-basic-1d",                 "1次元DP",                                  "dp"),
    ("dp-knapsack",                 "ナップサックDP",                            "dp"),
    ("dp-lis",                      "LIS（最長増加部分列）",                     "dp"),
    ("dp-lcs",                      "LCS（最長共通部分列）",                     "dp"),
    ("dp-edit-distance",            "編集距離",                                  "dp"),
    ("dp-interval",                 "区間DP",                                    "dp"),
    ("dp-bit",                      "bitDP",                                     "dp"),
    ("dp-bit-subset-sum",           "bitDP（部分和）",                           "dp"),
    ("dp-bit-grouping",             "bitDP（集合分割）",                         "dp"),
    ("dp-bitmask-tsp",              "bitDP（TSP / 巡回）",                        "dp"),
    ("dp-tree",                     "木DP",                                      "dp"),
    ("dp-rerooting",                "全方位木DP",                                "dp"),
    ("dp-digit",                    "桁DP",                                      "dp"),
    ("dp-mod",                      "mod DP",                                    "dp"),
    ("dp-probability",              "確率DP",                                    "dp"),
    ("dp-expectation",              "期待値DP",                                  "dp"),
    ("dp-substring-automaton",      "部分文字列DP（subsequence automaton）",     "dp"),
    ("dp-schedule",                 "スケジューリングDP",                        "dp"),
    ("dp-grid",                     "グリッドDP",                                "dp"),
    ("dp-inline-with-segtree",      "セグメント木DP高速化",                      "dp"),
    ("dp-monotone-queue",           "スライド最小値DP高速化",                    "dp"),
    ("dp-cht",                      "Convex Hull Trick",                         "dp"),
    ("dp-divide-conquer-opt",       "分割統治DP高速化",                          "dp"),
    ("dp-monge",                    "Monge / Knuth 最適化",                       "dp"),
    ("dp-matrix-power",             "行列累乗DP",                                "dp"),
    ("dp-sos",                      "Sum over Subsets DP",                       "dp"),
    ("dp-base-k",                   "k進数DP（三進数等）",                       "dp"),
    ("dp-recurrence",               "漸化式DP",                                  "dp"),
    ("dp-inplace-rolling",          "in-place / ローリングDP",                    "dp"),

    # ===== graph =====
    ("graph-bfs",                   "BFS",                                       "graph"),
    ("graph-dfs",                   "DFS",                                       "graph"),
    ("graph-01-bfs",                "01-BFS",                                    "graph"),
    ("graph-multi-source-bfs",      "多点スタートBFS",                           "graph"),
    ("graph-hypergraph-bfs",        "ハイパーグラフBFS",                         "graph"),
    ("graph-dijkstra",              "ダイクストラ",                              "graph"),
    ("graph-bellman-ford",          "ベルマン–フォード",                         "graph"),
    ("graph-warshall-floyd",        "ワーシャル–フロイド",                       "graph"),
    ("graph-spfa",                  "SPFA / キュー最適化",                        "graph"),
    ("graph-mst-kruskal",           "最小全域木（Kruskal）",                     "graph"),
    ("graph-mst-prim",              "最小全域木（Prim）",                        "graph"),
    ("graph-topological-sort",      "トポロジカルソート",                        "graph"),
    ("graph-topo-enumerate",        "トポロジカル順序の列挙",                    "graph"),
    ("graph-reverse-topo",          "逆辺トポロジカルソート",                    "graph"),
    ("graph-scc",                   "強連結成分分解（SCC）",                     "graph"),
    ("graph-2sat",                  "2-SAT",                                     "graph"),
    ("graph-bridge-articulation",   "橋・関節点（lowlink）",                     "graph"),
    ("graph-bcc",                   "二重連結成分分解",                          "graph"),
    ("graph-cycle-detect",          "DFSサイクル検出",                           "graph"),
    ("graph-bipartite-check",       "二部グラフ判定",                            "graph"),
    ("graph-tree-bipartite-color",  "木の二部塗り分け",                          "graph"),
    ("graph-tree-diameter",         "木の直径",                                  "graph"),
    ("graph-lca",                   "LCA（最小共通祖先）",                       "graph"),
    ("graph-auxiliary-tree",        "仮想木（auxiliary tree）",                  "graph"),
    ("graph-euler-tour",            "オイラーツアー",                            "graph"),
    ("graph-hld",                   "Heavy-Light分解",                           "graph"),
    ("graph-centroid-decomposition","重心分解",                                  "graph"),
    ("graph-functional",            "ファンクショナルグラフ（なもり）",          "graph"),
    ("graph-doubling-on-tree",      "ダブリング（木のk個上）",                   "graph"),
    ("graph-bipartite-matching",    "二部マッチング",                            "graph"),
    ("graph-max-flow",              "最大流（Dinic等）",                         "graph"),
    ("graph-min-cut",               "最小カット",                                "graph"),
    ("graph-min-cost-flow",         "最小費用流",                                "graph"),
    ("graph-degree-aggregation",    "次数集計・握手補題",                        "graph"),

    # ===== string =====
    ("string-z-algorithm",          "Z-algorithm",                               "string"),
    ("string-kmp",                  "KMP / failure function",                    "string"),
    ("string-rolling-hash",         "ローリングハッシュ",                        "string"),
    ("string-suffix-array",         "Suffix Array",                              "string"),
    ("string-lcp-array",            "LCP配列",                                   "string"),
    ("string-aho-corasick",         "Aho-Corasick",                              "string"),
    ("string-trie",                 "Trie木",                                    "string"),
    ("string-manacher",             "Manacher（最長回文）",                      "string"),
    ("string-lex-smallest",         "辞書順最小構成",                            "string"),
    ("string-run-length",           "ランレングス圧縮",                          "string"),

    # ===== number-theory =====
    ("nt-gcd-lcm",                  "GCD / LCM",                                 "number-theory"),
    ("nt-ext-gcd",                  "拡張ユークリッド互除法",                    "number-theory"),
    ("nt-mod-pow",                  "繰り返し二乗法（mod冪）",                   "number-theory"),
    ("nt-mod-inverse",              "modの逆元",                                 "number-theory"),
    ("nt-prime-sieve",              "エラトステネスの篩",                        "number-theory"),
    ("nt-linear-sieve",             "線形篩（最小素因数）",                      "number-theory"),
    ("nt-factorize",                "素因数分解",                                "number-theory"),
    ("nt-divisor-enumerate",        "約数列挙",                                  "number-theory"),
    ("nt-miller-rabin",             "Miller–Rabin / Pollard's rho",              "number-theory"),
    ("nt-crt",                      "中国剰余定理（CRT）",                       "number-theory"),
    ("nt-euler-phi",                "オイラーのトーシェント関数",                "number-theory"),
    ("nt-mobius",                   "メビウス関数",                              "number-theory"),
    ("nt-base-conversion",          "進数変換",                                  "number-theory"),
    ("nt-digit-sum",                "桁和・桁ごと寄与計算",                      "number-theory"),

    # ===== geometry =====
    ("geom-trigonometry",           "三角関数の基本",                            "geometry"),
    ("geom-vector-cross-dot",       "ベクトル外積・内積",                        "geometry"),
    ("geom-ccw",                    "CCW（線分の位置関係）",                     "geometry"),
    ("geom-segment-intersect",      "線分交差判定",                              "geometry"),
    ("geom-convex-hull",            "凸包",                                      "geometry"),
    ("geom-rotation-45",            "45度回転（マンハッタン⇔チェビシェフ）",    "geometry"),
    ("geom-polar-sort",             "偏角ソート",                                "geometry"),
    ("geom-closest-pair",           "最近点対",                                  "geometry"),
    ("geom-float-pitfall",          "浮動小数の罠",                              "geometry"),

    # ===== data-structure =====
    ("ds-stack",                    "スタック",                                  "data-structure"),
    ("ds-queue",                    "キュー",                                    "data-structure"),
    ("ds-deque",                    "deque",                                     "data-structure"),
    ("ds-priority-queue",           "優先度付きキュー",                          "data-structure"),
    ("ds-set-map",                  "set / map",                                  "data-structure"),
    ("ds-multiset",                 "multiset / 中央値管理（2-heap）",            "data-structure"),
    ("ds-union-find",               "Union-Find",                                "data-structure"),
    ("ds-weighted-union-find",      "重み付きUnion-Find",                        "data-structure"),
    ("ds-bit",                      "BIT（Fenwick Tree）",                       "data-structure"),
    ("ds-segtree",                  "セグメント木",                              "data-structure"),
    ("ds-lazy-segtree",             "遅延伝播セグメント木",                      "data-structure"),
    ("ds-segtree-on-index",         "平面走査 + BIT / セグ木",                    "data-structure"),
    ("ds-sqrt-decomposition",       "平方分割",                                  "data-structure"),
    ("ds-mo",                       "Mo's algorithm",                            "data-structure"),
    ("ds-sparse-table",             "Sparse Table（RMQ）",                       "data-structure"),
    ("ds-bitset",                   "bitset高速化",                              "data-structure"),
    ("ds-imos-1d",                  "いもす法（1次元）",                         "data-structure"),
    ("ds-imos-2d",                  "二次元いもす法",                            "data-structure"),
    ("ds-prefix-sum",               "累積和",                                    "data-structure"),
    ("ds-prefix-sum-2d",            "二次元累積和",                              "data-structure"),
    ("ds-diff-array",               "階差・差分配列",                            "data-structure"),
    ("ds-coord-compression",        "座標圧縮",                                  "data-structure"),

    # ===== brute-force =====
    ("bf-loop",                     "多重ループ全探索",                          "brute-force"),
    ("bf-bit",                      "bit全探索（部分集合列挙）",                 "brute-force"),
    ("bf-permutation",              "順列全探索",                                "brute-force"),
    ("bf-subset-of-subset",         "部分集合の部分集合列挙",                    "brute-force"),
    ("bf-recursive-dfs",            "再帰DFSによる全列挙",                       "brute-force"),
    ("bf-meet-in-the-middle",       "半分全列挙",                                "brute-force"),

    # ===== search =====
    ("search-binary-sorted",        "二分探索（ソート済み配列）",                "search"),
    ("search-binary-on-answer",     "答えで二分探索",                            "search"),
    ("search-binary-interactive",   "インタラクティブ二分探索",                  "search"),
    ("search-two-pointers",         "尺取り法",                                  "search"),
    ("search-ternary",              "三分探索",                                  "search"),
    ("search-doubling",             "ダブリング",                                "search"),
    ("search-cyclic-shift",         "循環シフト探索",                            "search"),

    # ===== construction =====
    ("con-greedy-sort",             "ソート + 貪欲",                              "construction"),
    ("con-greedy-exchange",         "交換論法",                                  "construction"),
    ("con-greedy-simulate",         "貪欲シミュレーション",                      "construction"),
    ("con-parity",                  "パリティ（偶奇）",                          "construction"),
    ("con-invariant",               "不変量（XOR和等）",                         "construction"),
    ("con-pigeonhole",              "鳩の巣原理",                                "construction"),
    ("con-construction",            "構築（コンストラクティブ）",                "construction"),
    ("con-meta",                    "メタ的考察",                                "construction"),
    ("con-bit-independent",         "bitごと独立に計算",                         "construction"),
    ("con-game-grundy",             "Grundy数 / Nim",                            "construction"),
    ("con-xor-gauss",               "XOR連立方程式（Gauss消去）",                "construction"),

    # ===== math =====
    ("math-combinatorics",          "組合せ・順列の基本",                        "math"),
    ("math-mod-combination",        "mod 二項係数（階乗 + 逆元）",                "math"),
    ("math-inclusion-exclusion",    "包除原理",                                  "math"),
    ("math-expectation-linearity",  "期待値の線形性",                            "math"),
    ("math-expectation",            "期待値の計算",                              "math"),
    ("math-mod-counting",           "mod 数え上げ",                              "math"),
    ("math-power-counting",         "累乗数え上げ",                              "math"),
    ("math-simple-counting",        "単純数え上げ・寄与計算",                    "math"),
    ("math-median",                 "中央値の最適性",                            "math"),
    ("math-set-dedup",              "集合・重複検出",                            "math"),
    ("math-fft-ntt",                "FFT / NTT（畳み込み）",                      "math"),
    ("math-matrix-basic",           "行列演算の基本",                            "math"),
    ("math-lcm-digits",             "LCM・桁数評価",                             "math"),
]

# Typical90 problem -> representative technique id(s). Reference for Claude
# when impl is asked: "this technique appears in typical90-NNN, optionally
# present that problem". Not stored in DB.
TYPICAL90_MAP: dict[int, list[str]] = {
    1:  ["search-binary-on-answer"],
    2:  ["bf-bit"],
    3:  ["graph-tree-diameter"],
    4:  ["ds-prefix-sum"],
    5:  ["dp-matrix-power"],
    6:  ["string-lex-smallest", "ds-sparse-table"],
    7:  ["search-binary-sorted"],
    8:  ["dp-substring-automaton"],
    9:  ["geom-polar-sort"],
    10: ["ds-prefix-sum"],
    11: ["dp-schedule"],
    12: ["ds-union-find"],
    13: ["graph-dijkstra"],
    14: ["con-greedy-sort"],
    15: ["nt-divisor-enumerate"],
    16: ["bf-loop"],
    17: ["ds-segtree-on-index", "ds-bit"],
    18: ["geom-trigonometry"],
    19: ["dp-interval"],
    20: ["geom-float-pitfall"],
    21: ["graph-scc"],
    22: ["nt-gcd-lcm"],
    23: ["dp-bit"],
    24: ["con-parity"],
    25: ["con-meta"],
    26: ["graph-tree-bipartite-color"],
    27: ["math-set-dedup"],
    28: ["ds-imos-2d"],
    29: ["ds-lazy-segtree"],
    30: ["nt-prime-sieve"],
    31: ["con-game-grundy"],
    32: ["bf-permutation"],
    33: ["math-simple-counting"],
    34: ["search-two-pointers"],
    35: ["graph-auxiliary-tree", "graph-lca"],
    36: ["geom-rotation-45"],
    37: ["dp-cht"],
    38: ["math-lcm-digits"],
    39: ["dp-rerooting"],
    40: ["graph-min-cut"],
    41: ["geom-convex-hull"],
    42: ["dp-mod"],
    43: ["graph-01-bfs"],
    44: ["search-cyclic-shift"],
    45: ["dp-bit-grouping"],
    46: ["math-mod-counting"],
    47: ["string-z-algorithm"],
    48: ["con-greedy-sort"],
    49: ["ds-sqrt-decomposition"],
    50: ["dp-recurrence"],
    51: ["bf-meet-in-the-middle"],
    52: ["math-expectation"],
    53: ["search-binary-interactive"],
    54: ["graph-hypergraph-bfs"],
    55: ["bf-loop"],
    56: ["dp-bit-subset-sum"],
    57: ["con-xor-gauss"],
    58: ["search-doubling"],
    59: ["ds-bitset"],
    60: ["dp-lis"],
    61: ["ds-deque"],
    62: ["graph-reverse-topo"],
    63: ["bf-bit", "math-simple-counting"],
    64: ["ds-diff-array"],
    65: ["math-inclusion-exclusion"],
    66: ["math-expectation-linearity"],
    67: ["nt-base-conversion"],
    68: ["ds-weighted-union-find"],
    69: ["math-power-counting"],
    70: ["math-median"],
    71: ["graph-topo-enumerate"],
    72: ["graph-cycle-detect"],
    73: ["dp-tree"],
    74: ["dp-base-k"],
    75: ["nt-factorize"],
    76: ["search-two-pointers"],
    77: ["graph-bipartite-matching"],
    78: ["graph-degree-aggregation"],
    79: ["con-greedy-simulate"],
    80: ["math-inclusion-exclusion", "dp-bit"],
    81: ["ds-imos-2d"],
    82: ["nt-digit-sum"],
    83: ["ds-sqrt-decomposition"],
    84: ["search-two-pointers"],
    85: ["nt-divisor-enumerate"],
    86: ["con-bit-independent"],
    87: ["search-binary-sorted"],
    88: ["con-pigeonhole"],
    89: ["dp-inline-with-segtree"],
    90: ["math-inclusion-exclusion", "math-mod-counting"],
}

assert len({t[0] for t in TECHNIQUES}) == len(TECHNIQUES), "duplicate technique id"


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
            "INSERT INTO techniques (id, name, category) VALUES (?, ?, ?)",
            TECHNIQUES,
        )
        conn.commit()
    finally:
        conn.close()

    print(f"Initialized {db} with {len(TECHNIQUES)} techniques.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
