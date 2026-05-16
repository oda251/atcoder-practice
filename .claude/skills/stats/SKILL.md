---
name: stats
description: 練習の進捗（出題数 / 正答率 / 最終出題日）を表示する。
argument-hint: "[--tech <技法名>] [--variation-of <親>] [--kind card|impl|advanced]"
allowed-tools: Bash(sqlite3 *)
---

## 現在のサマリ（kind 別）

```!
sqlite3 -box data/practice.db "SELECT kind, COUNT(*) AS n, SUM(correct) AS ok, ROUND(AVG(correct)*100, 1) AS acc, MAX(asked_at) AS last_at FROM attempts GROUP BY kind ORDER BY kind;"
```

## ユーザ入力

`$ARGUMENTS`（追加フィルタ。省略可）

## 詳細

引数があれば、`stats` ビューから該当行を抽出する。Bash ツールで以下のような SELECT を実行する（WHERE 句を引数に応じて構築）。

```bash
# --tech <技法名>: 特定 technique
sqlite3 -box data/practice.db "SELECT technique, variation_of, kind, n, ok, acc, last_at FROM stats WHERE technique = '累積和' ORDER BY kind;"

# --variation-of <親>: 親の子（バリエーション）すべて
sqlite3 -box data/practice.db "SELECT technique, kind, n, ok, acc, last_at FROM stats WHERE variation_of = 'bitDP' ORDER BY technique, kind;"

# --kind impl: kind で絞る（正答率の低い順）
sqlite3 -box data/practice.db "SELECT technique, variation_of, n, ok, acc, last_at FROM stats WHERE kind = 'impl' ORDER BY acc, last_at;"

# 引数なし詳細: 着手済みのみ全部
sqlite3 -box data/practice.db "SELECT technique, variation_of, kind, n, ok, acc, last_at FROM stats ORDER BY technique, kind;"
```

## 出力方針

- まず kind 別サマリを見せる
- 引数で絞り込みがあれば、その範囲の明細を続けて表示
- 全体把握として「着手済 N pair / 全 M pair」を 1 行添えると良い
  - 全体 = `SELECT COUNT(*) * 3 FROM techniques`（kind 3 種類分）
  - 着手済 = `SELECT COUNT(DISTINCT technique || ':' || kind) FROM attempts`
- 未着手は `stats` ビューには出ない（INNER JOIN なので）。未着手を含む全 pair が必要なら別途 CROSS JOIN で出す
