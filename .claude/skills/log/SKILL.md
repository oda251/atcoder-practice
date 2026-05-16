---
name: log
description: 練習結果を attempts テーブルに記録する。
argument-hint: "<技法名> <kind> <o|x> [--uri ...] [--note ...]"
allowed-tools: Bash(sqlite3 *)
---

## 引数

ユーザ入力: `$ARGUMENTS`

形式: `<技法名> <kind> <o|x> [--uri <URI>] [--note "<text>"]`

- 技法名: `techniques.name` の値（日本語名）。例: `累積和`, `尺取り法`, `bitDP`, `ダイクストラ`
  - スペースや `/` を含む名前は quote する: `"GCD / LCM"`, `"ソート + 貪欲"`
- `kind`: `card` / `impl` / `advanced`
- `o` = 正解（correct=1）/ `x` = 不正解（correct=0）
- `--uri`: 任意。問題URL（`advanced` で推奨、AtCoder/yukicoder/file:// 何でも可）
- `--note`: 任意。一言メモ

## 実行

引数をパースし、Bash ツールで以下を実行する。値は SQL リテラルとして安全にエスケープすること（シングルクオートは `''` で重ね、NULL の場合はクオート無し）。

```bash
sqlite3 data/practice.db <<'SQL'
INSERT INTO attempts (technique, kind, problem_uri, correct, asked_at, note)
VALUES ('<TECH>', '<KIND>', <URI_OR_NULL>, <0|1>, datetime('now'), <NOTE_OR_NULL>);
SELECT 'recorded #' || last_insert_rowid() || ' ' || datetime('now');
SQL
```

例:
- `/log 累積和 card o` → URI/NOTE は NULL
- `/log ダイクストラ advanced x --uri https://atcoder.jp/contests/abc123/tasks/abc123_d --note "ヒープ更新で TLE"`
- `/log "GCD / LCM" impl o`

## 事後アクション

- 記録結果（行 ID と時刻）を 1 行で報告するだけで良い
- 失敗時は原因を伝える（未知の技法名、kind のスペルミスなど）
- 次の出題が欲しそうなら `/ask` を案内
