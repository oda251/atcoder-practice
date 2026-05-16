---
name: log
description: 練習結果を attempts テーブルに記録する。
argument-hint: "<technique_id> <kind> <o|x> [--uri ...] [--note ...]"
allowed-tools: Bash(sqlite3 *)
---

## 引数

ユーザ入力: `$ARGUMENTS`

形式: `<technique_id> <kind> <o|x> [--uri <URI>] [--note "<text>"]`

- `technique_id`: 例 `typical90-005`
- `kind`: `card` / `impl` / `advanced`
- `o` = 正解（correct=1）/ `x` = 不正解（correct=0）
- `--uri`: 任意。問題URL（`advanced` で推奨、AtCoder/yukicoder/file:// 何でも可）
- `--note`: 任意。一言メモ

## 実行

引数をパースし、Bash ツールで以下を実行する。値は SQL リテラルとして安全にエスケープすること（シングルクオートは `''` で重ね、NULL の場合はクオート無し）。

```bash
sqlite3 data/practice.db <<'SQL'
INSERT INTO attempts (technique_id, kind, problem_uri, correct, asked_at, note)
VALUES ('<TECH>', '<KIND>', <URI_OR_NULL>, <0|1>, datetime('now'), <NOTE_OR_NULL>);
SELECT 'recorded #' || last_insert_rowid() || ' ' || datetime('now');
SQL
```

例:
- `/log typical90-005 card o` → URI/NOTE は NULL
- `/log typical90-005 advanced x --uri https://atcoder.jp/contests/abc123/tasks/abc123_d --note "桁DPが書けなかった"`

## 事後アクション

- 記録結果（行 ID と時刻）を 1 行で報告するだけで良い
- 失敗時は原因を伝える（未知の technique_id、kind のスペルミスなど）
- 次の出題が欲しそうなら `/ask` を案内
