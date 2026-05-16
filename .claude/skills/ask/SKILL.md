---
name: ask
description: 典型解法の練習を1件提示する。次に解くべき (technique, kind) を SRS で選び、その場でカード / 実装課題 / 応用問題を生成する。
argument-hint: "[--kind card|impl|advanced] [--tech typical90-NNN]"
allowed-tools: Bash(python3 *), Bash(sqlite3 *), Read, Grep, Glob, WebFetch
---

## 選定結果

```!
python3 "${CLAUDE_SKILL_DIR}/select.py" $ARGUMENTS
```

## 出題

上の選定結果の `kind` に応じて出題する。

### kind = card

Claude が作った小問題に対して **解答方針** を答える形式。

- 該当 technique を典型的に使う小問題を Claude が **その場で生成** する
  - 問題文、入力形式・制約・小さなサンプル1つ を含める
  - 設定は毎回変えて、同じ言い回しの繰り返しを避ける
  - 典型90 の本問は流用しない（impl で扱うため温存）
- ユーザには **方針だけ** を答えてもらう
  - 使う典型解法名（例: 「累積和」「二分探索」「桁DP」）
  - 解法のアイデアの要点 1-3 行
- ユーザ回答後、模範方針と照合し、合致点 / 抜けを 3-5 行で指摘
- 「方針が立てば card は ○」を判定基準とする（実装はしない）
- 結果確定後 `/log <technique_id> card <o|x> [--note "..."]` を案内

### kind = impl

基礎実装。**典型90 本問そのもの** を提示する。

- 該当 `technique_id`（例 `typical90-034`）が指す典型90 本問の問題文 / 入力形式 / 制約 / サンプル を提示する
- 本問が思い出せない場合は WebFetch で `https://atcoder.jp/contests/typical90/tasks/...` を確認
- ユーザがコードを書いたらレビューし、テストケースで合うか確認
- 結果確定後 `/log <technique_id> impl <o|x> [--uri ...] [--note ...]` を案内

### kind = advanced

応用。**典型90 以外の AtCoder 本問**（同じ technique を使う別問題）を提示する。

- AtCoder で同じ technique を使う1問を提案する（abc/arc の D・E・F が目安）
- 候補が思い当たらない場合は WebFetch で AtCoder Problems や atcoder-tags を確認
- 問題URLを示し、`/log <technique_id> advanced <o|x> --uri <URL>` を案内
- 解いた後の感想 / 詰まりポイントは `--note` で残すよう促す

## 共通方針

- 出題はこの会話の中で完結させる。問題ファイルや一時データを書き出す必要はない
- 問題本文・解説は記録しない（DB に残るのは結果のみ）
