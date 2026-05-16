---
name: ask
description: 典型解法の練習を1件提示する。次に解くべき (technique, kind) を SRS で選び、その場でカード / 実装課題 / 応用問題を生成する。
argument-hint: "[--kind card|impl|advanced] [--tech <技法名>] [--variation-of <親技法>]"
allowed-tools: Bash(python3 *), Bash(sqlite3 *), Read, Grep, Glob, WebFetch
---

## 選定結果

```!
python3 "${CLAUDE_SKILL_DIR}/select.py" $ARGUMENTS
```

## 出題

上の選定結果の `technique` (日本語名) / `variation_of` / `kind` を見て出題する。

### kind = card

Claude が作った小問題に対して **解答方針** を答える形式。

- 該当 technique を典型的に使う小問題を Claude が **その場で生成** する
  - 問題文、入力形式・制約・小さなサンプル1つ を含める
  - 設定は毎回変えて、同じ言い回しの繰り返しを避ける
- ユーザには **方針だけ** を答えてもらう
- ユーザ回答後、模範方針と照合し、合致点 / 抜けを指摘
- 「方針が立てば card は ○」を判定基準とする
- 結果確定後は下記「記録」を **自動で実行**（実装はしないので `--uri` は付けない）

### kind = impl

基礎実装。コードを書いてもらう。

- 該当 technique を典型的に使う問題を Claude が提示する
  - **基本は Claude がその場で生成**（短めで解法本質に集中する設計）
  - その technique を扱う **典型90 の本問が思い当たれば** 優先的に流用してよい（マッピングは `scripts/init_db.py` の `TYPICAL90_MAP` を参照）
- 問題文 / 入力形式 / 制約 / サンプル1-2個 を提示
- ユーザがコードを書いたらレビューし、テストケースで合うか確認
- 結果確定後は下記「記録」を **自動で実行**（実問題流用時は `--uri` 相当の URL も埋める）

### kind = advanced

応用。実問題（AtCoder/yukicoder 本問）でもう一段難度を上げる。

- **基本は Claude がその場で発展問題を生成**（同 technique + 追加考察 1 段）
- AtCoder/yukicoder で **既知の良問が思い当たれば** それを優先（abc/arc の D・E・F が目安）
  - 候補が薄ければ WebFetch で AtCoder Problems や atcoder-tags を確認
- 結果確定後は下記「記録」を **自動で実行**（実問題なら URL を埋める）
- 詰まりポイントがあれば note に短く残す

## 記録（自動）

判定が ○/× で確定したら、ユーザに `/log` を促さず、Claude が即 `attempts` に INSERT する。

```bash
sqlite3 data/practice.db <<'SQL'
INSERT INTO attempts (technique, kind, problem_uri, correct, asked_at, note)
VALUES ('<TECH>', '<KIND>', <URI_OR_NULL>, <0|1>, datetime('now'), <NOTE_OR_NULL>);
SELECT 'recorded #' || last_insert_rowid() || ' ' || datetime('now');
SQL
```

- 値はシングルクオートで囲み、シングルクオートのエスケープは `''` 重ね
- `problem_uri` `note` が無い場合はクオート無しの `NULL`
- 記録結果（行 ID と時刻）を 1 行報告して終了
- INSERT 失敗時は原因（未知の technique、kind スペルミス等）を 1 行で伝える

## 共通方針

- `variation_of` が出ていれば「これは <親技法> の一バリエーション」と意識して出題（親と違いが出るような設定にする）
- 出題はこの会話の中で完結させる。問題ファイルや一時データを書き出す必要はない
- 問題本文・解説は記録しない（DB に残るのは結果のみ）
