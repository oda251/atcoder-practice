---
name: stats
description: 練習の進捗（出題数 / 正答率 / 最終出題日）を表示する。
argument-hint: "[--tech typical90-NNN] [--kind card|impl|advanced]"
allowed-tools: Bash(sqlite3 *)
---

## 現在のサマリ

```!
sqlite3 -box data/practice.db "SELECT kind, COUNT(*) AS n, SUM(correct) AS ok, ROUND(AVG(correct)*100, 1) AS acc, MAX(asked_at) AS last_at FROM attempts GROUP BY kind ORDER BY kind;"
```

## ユーザ入力

`$ARGUMENTS`（フィルタ。省略可）

## 詳細

引数があれば、`stats` ビューから該当行のみ抽出する。Bash ツールで以下のような SELECT を実行する（WHERE 句を引数に応じて構築）。

```bash
# 例: --tech typical90-005 のみ
sqlite3 -box data/practice.db "SELECT technique_id, kind, n, ok, acc, last_at FROM stats WHERE technique_id = 'typical90-005' ORDER BY kind;"

# 例: --kind impl のみ
sqlite3 -box data/practice.db "SELECT technique_id, name, n, ok, acc, last_at FROM stats WHERE kind = 'impl' ORDER BY acc, last_at;"

# 例: 引数なし → 上のサマリだけで足りるが、もう少し詳しく出すなら:
sqlite3 -box data/practice.db "SELECT technique_id, name, kind, n, ok, acc, last_at FROM stats ORDER BY technique_id, kind;"
```

## 出力方針

- まずサマリ（kind ごとの集計）を見せる
- 引数で絞り込みがあれば、その範囲の明細を続けて表示
- 引数なしでも明細が欲しそうな場合は「全 270 (= 90 × 3) ペアのうち着手済みは N 件」のような俯瞰を 1 行添える
- 出題ゼロのペアは `stats` ビューには出ない（JOIN なので）。これを含めたい時は LEFT JOIN で別途出す
