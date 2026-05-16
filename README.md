# atcoder-practice

典型解法の習得を目的とした AtCoder 練習ログ。典型90 の各解法について、3 種類の練習（`card` / `impl` / `advanced`）の出題数と正答率を SQLite に蓄積する。

Claude Code から `/ask` `/log` `/stats` の project skill で操作する前提。

## 練習の種類

| kind | 内容 |
|---|---|
| `card` | フラッシュカード（知識想起 Q&A）。Claude が都度生成 |
| `impl` | 基礎実装。典型90 本問またはその類題を Claude が都度提示 |
| `advanced` | 応用。AtCoder/yukicoder の本問（URI を `--uri` で記録） |

問題自体はマスタを持たない。Claude が会話で出題し、結果のみ DB に記録する。

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
├── scripts/init_db.py     # 初期セットアップ
└── README.md
```

## 初回セットアップ

```sh
python3 scripts/init_db.py
```

`data/practice.db` を作成し、`techniques` に typical90 を 90 件投入する。再作成したい場合は `--force`。

## 使い方（Claude Code）

このリポジトリのルートで `claude` を起動すると、project skill が自動で読み込まれる。

```text
/ask
/ask --kind card
/ask --tech typical90-005

/log typical90-005 card o
/log typical90-005 impl x --note "全探索で TLE"
/log typical90-005 advanced o --uri https://atcoder.jp/contests/...

/stats
/stats --tech typical90-005
/stats --kind impl
```

`/ask` は SRS で次の `(technique, kind)` を選び、Claude が `kind` に応じて以下を行う:

- `card`: 解法の知識を問うフラッシュカードを生成 → ユーザ回答を採点
- `impl`: 典型90 本問または易しい類題を提示 → コードレビュー
- `advanced`: 同等以上の難易度の AtCoder 本問を提案 → URI で記録

## SQLite スキーマ

```sql
CREATE TABLE techniques (
  id   TEXT PRIMARY KEY,    -- 'typical90-NNN'
  name TEXT NOT NULL        -- 例: 'Yokan Party（★4）'
);

CREATE TABLE attempts (
  id            INTEGER PRIMARY KEY,
  technique_id  TEXT NOT NULL REFERENCES techniques(id),
  kind          TEXT NOT NULL CHECK (kind IN ('card','impl','advanced')),
  problem_uri   TEXT,
  correct       INTEGER NOT NULL CHECK (correct IN (0,1)),
  asked_at      TEXT NOT NULL,    -- ISO8601 UTC
  note          TEXT
);

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
```

## SRS

`(technique, kind)` ごとに attempts から派生計算（状態テーブルなし、1ソース原則）。

- `reps` = 直近の連続正解数（新しい方から、`x` が出るまで）
- `interval_days = 2 ** min(reps, 7)` = `1, 2, 4, 8, 16, 32, 64, 128`
- `last_at + interval_days < now` なら due

`/ask` は **unseen → due → fresh** の順に優先し、同点ランダム。
