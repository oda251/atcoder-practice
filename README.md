# atcoder-practice

典型解法の習得を目的とした AtCoder 練習ログ。典型90の各解法について、3 種類の練習（card / impl / advanced）の出題数と正答率を SQLite に蓄積する。

## 練習の種類

| kind | 内容 |
|---|---|
| `card` | フラッシュカード（知識想起 Q&A）。Claude が都度生成 |
| `impl` | 基礎実装。典型90 とその類題を Claude が都度提示 |
| `advanced` | 応用。AtCoder/yukicoder の本問を解く（URI を記録） |

問題自体はマスタを持たない。Claude が対話で出題し、結果のみ SQLite に記録する。

## ファイル

```
atcoder-practice/
├── data/practice.db        # SQLite。init_db.py で生成
└── scripts/
    ├── init_db.py          # スキーマ作成 + typical90 seed
    ├── ask.py              # 次に解くべき (technique, kind) を提示
    ├── log.py              # 結果記録
    └── stats.py            # 集計表示
```

## 使い方

### 初回セットアップ

```sh
python3 scripts/init_db.py
```

`data/practice.db` を作成し、`techniques` に typical90 を 90 件投入する。再作成したい場合は `--force`。

### 出題

```sh
python3 scripts/ask.py                       # 全 kind から1件
python3 scripts/ask.py --kind card           # card に絞る
python3 scripts/ask.py --tech typical90-002  # technique 指定
```

優先度: 未着手 > SRS で due > その他、同点ランダム。実際の問題は Claude が会話で提示する。

### 記録

```sh
python3 scripts/log.py typical90-002 impl o
python3 scripts/log.py typical90-002 advanced x --uri https://atcoder.jp/...
python3 scripts/log.py typical90-002 card o --note "包含排除を忘れていた"
```

3 つ目の引数は `o`（正解）/ `x`（不正解）。

### 集計

```sh
python3 scripts/stats.py                       # 全体
python3 scripts/stats.py --tech typical90-002
python3 scripts/stats.py --kind impl
```

## SRS

`(technique, kind)` ごとに attempts から派生計算する（状態テーブルなし）。直近の連続正解数 `reps` を数え、`interval_days = 2^min(reps, 7)`、`last_at + interval_days < now` なら due 扱い。
