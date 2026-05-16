# atcoder-practice

競プロ典型解法の習得を目的とした AtCoder 練習ログ。**技法カタログ**（日本語名 + バリエーション関係）を独立して持ち、各 technique について 3 種類の練習（`card` / `impl` / `advanced`）の出題数と正答率を SQLite に蓄積する。

典型90 はあくまで例題プールとして参照（マスタには持たない）。

Claude Code から `/ask` `/log` `/stats` の project skill で操作する前提。

## 練習の種類

| kind | 内容 |
|---|---|
| `card` | 解答方針カード。該当技法を使う小問題を Claude が生成し、ユーザは方針だけを答える（コード不要） |
| `impl` | 基礎実装。Claude が生成する問題、または該当 technique を扱う典型90 本問でコードを書く |
| `advanced` | 応用。Claude が生成する発展問題、または AtCoder/yukicoder の良問。URI を `--uri` で記録 |

難易度は kind そのものに対応する（`card < impl < advanced`）。

問題自体はマスタを持たない。Claude が会話で出題し、結果のみ DB に記録する。

## 技法カタログ

`scripts/init_db.py` の `TECHNIQUES` が一次ソース（158件）。技法名は日本語（カタカナ・漢字・英略語混在可）。`variation_of` 列で「親技法のバリエーション」関係だけ表現する（カテゴリではない）:

- `二分探索` → `答えで二分探索`, `インタラクティブ二分探索`
- `累積和` → `二次元累積和`
- `bitDP` → `部分和bitDP`, `集合分割bitDP`, `TSPbitDP`, `Sum over Subsets DP`
- `BFS` → `01-BFS`, `多点スタートBFS`, `ハイパーグラフBFS`
- `Union-Find` → `重み付きUnion-Find`
- ほか多数

109親 / 49子。連鎖は最大 3 段（例: `GCD / LCM` → `拡張ユークリッド互除法` → `中国剰余定理`）。

## ファイル構成

```
atcoder-practice/
├── .claude/skills/
│   ├── ask/
│   │   ├── SKILL.md       # 次に解くべき (technique, kind) を提示し問題生成
│   │   └── select.py      # 未着手 > SRS-due > fresh で1件選ぶ
│   ├── log/SKILL.md       # 結果記録
│   └── stats/SKILL.md     # 集計表示
├── data/practice.db       # SQLite (git ignore)
├── scripts/init_db.py     # スキーマ作成 + 技法カタログ seed
└── README.md
```

## 初回セットアップ

```sh
python3 scripts/init_db.py
```

`data/practice.db` を作成し、技法カタログを投入。再作成は `--force`（既存 attempts も消えるので注意）。

## 使い方（Claude Code）

```text
/ask
/ask --kind card
/ask --variation-of 二分探索        # 二分探索系のどれか
/ask --tech 累積和

/log 累積和 card o
/log ダイクストラ impl x --note "ヒープ更新で TLE"
/log "GCD / LCM" advanced o --uri https://atcoder.jp/contests/...

/stats
/stats --tech 累積和
/stats --variation-of bitDP
/stats --kind impl
```

技法名にスペースや `/` などが含まれる場合は引数を quote する（`"GCD / LCM"`, `"ソート + 貪欲"`）。

## SQLite スキーマ

```sql
CREATE TABLE techniques (
  name         TEXT PRIMARY KEY,
  variation_of TEXT REFERENCES techniques(name)
);

CREATE TABLE attempts (
  id          INTEGER PRIMARY KEY,
  technique   TEXT NOT NULL REFERENCES techniques(name),
  kind        TEXT NOT NULL CHECK (kind IN ('card','impl','advanced')),
  problem_uri TEXT,
  correct     INTEGER NOT NULL CHECK (correct IN (0,1)),
  asked_at    TEXT NOT NULL,
  note        TEXT
);

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
```

## SRS

`(technique, kind)` ごとに attempts から派生計算（状態テーブルなし、1ソース原則）。

- `reps` = 直近の連続正解数（新しい方から、`x` が出るまで）
- `interval_days = 2 ** min(reps, 7)` = `1, 2, 4, 8, 16, 32, 64, 128`
- `last_at + interval_days < now` なら due

`/ask` は **unseen → due → fresh** の順に優先し、同点ランダム。
