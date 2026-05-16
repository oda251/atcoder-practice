---
name: stats
description: 練習の進捗（出題数 / 正答率 / 最終出題日）を表示する。
argument-hint: "[--tech <技法名>] [--variation-of <親>] [--kind card|impl|advanced]"
allowed-tools: Bash(sqlite3 *)
---

## 現在のサマリ（kind 別）

```!
sqlite3 -box "${CLAUDE_SKILL_DIR}/../../../data/practice.db" "SELECT kind, SUM(n) AS n, SUM(ok) AS ok, ROUND(100.0 * SUM(ok) / SUM(n), 1) AS acc, MAX(last_at) AS last_at FROM stats GROUP BY kind ORDER BY kind;"
```

## ユーザ入力

`$ARGUMENTS`（追加フィルタ。省略可）

## 詳細

引数があれば `stats` ビューから該当行を抽出する。Bash で sqlite3 を叩く。DB パスは `${CLAUDE_SKILL_DIR}/../../../data/practice.db` を使う（または相対 `data/practice.db` でもリポジトリルートなら可）。

`stats` ビューの列: `technique, variation_of, kind, n, ok, acc, last_at`。

引数の組み立て例:

- `--tech "<name>"` → `WHERE technique = '<name>'`
- `--variation-of "<parent>"` → `WHERE variation_of = '<parent>'`
- `--kind <kind>` → `WHERE kind = '<kind>'`

例:

```bash
sqlite3 -box "${CLAUDE_SKILL_DIR}/../../../data/practice.db" \
  "SELECT * FROM stats WHERE technique = '累積和' ORDER BY kind;"
```

## 出力方針

- まず kind 別サマリを見せる
- 引数で絞り込みがあれば、その範囲の明細を続けて表示
- 全体把握として「着手済 N pair / 全 M pair」を 1 行添えると良い
  - 全体 = `SELECT COUNT(*) * 3 FROM techniques`
  - 着手済 = `SELECT COUNT(DISTINCT technique || ':' || kind) FROM attempts`
- 未着手は `stats` ビューには出ない（INNER JOIN なので）
