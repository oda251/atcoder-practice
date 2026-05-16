---
name: ask
description: 典型解法の練習を1件提示する。次に解くべき (technique, kind) を SRS で選び、その場でカード / 実装課題 / 応用問題を生成する。
argument-hint: "[--kind card|impl|advanced] [--tech <id>] [--category <cat>]"
allowed-tools: Bash(python3 *), Bash(sqlite3 *), Read, Grep, Glob, WebFetch
---

## 選定結果

```!
python3 "${CLAUDE_SKILL_DIR}/select.py" $ARGUMENTS
```

## 出題

上の選定結果の `technique_id` / `name` / `category` / `kind` を見て出題する。`technique_id` は `<category>-<slug>` 形式（例: `ds-prefix-sum`, `graph-dijkstra`, `dp-bit`）。

### kind = card

Claude が作った小問題に対して **解答方針** を答える形式。

- 該当 technique を典型的に使う小問題を Claude が **その場で生成** する
  - 問題文、入力形式・制約・小さなサンプル1つ を含める
  - 設定は毎回変えて、同じ言い回しの繰り返しを避ける
- ユーザには **方針だけ** を答えてもらう
  - 使う典型解法名（例: 「累積和」「二分探索」「桁DP」）
  - 解法のアイデアの要点 1-3 行
- ユーザ回答後、模範方針と照合し、合致点 / 抜けを 3-5 行で指摘
- 「方針が立てば card は ○」を判定基準とする（実装はしない）
- 結果確定後 `/log <technique_id> card <o|x> [--note "..."]` を案内

### kind = impl

基礎実装。コードを書いてもらう。

- 該当 technique を典型的に使う問題を Claude が提示する
  - **基本は Claude がその場で生成**（短めで解法本質に集中する設計）
  - その technique を扱う **典型90 の本問が思い当たれば** 優先的に流用してよい（マッピングは `scripts/init_db.py` の `TYPICAL90_MAP` を参照）
- 問題文 / 入力形式 / 制約 / サンプル1-2個 を提示
- ユーザがコードを書いたらレビューし、テストケースで合うか確認
- 結果確定後 `/log <technique_id> impl <o|x> [--uri ...] [--note ...]` を案内（実問題流用時は `--uri` で記録）

### kind = advanced

応用。実問題（AtCoder/yukicoder 本問）でもう一段難度を上げる。

- **基本は Claude がその場で発展問題を生成**（同 technique + 追加考察 1 段）
- AtCoder/yukicoder で **既知の良問が思い当たれば** それを優先（abc/arc の D・E・F が目安）
  - 候補が薄ければ WebFetch で AtCoder Problems や atcoder-tags を確認
- 問題URLがあれば示し、`/log <technique_id> advanced <o|x> --uri <URL>` を案内
- 詰まりポイントは `--note` で残すよう促す

## 共通方針

- 出題はこの会話の中で完結させる。問題ファイルや一時データを書き出す必要はない
- 問題本文・解説は記録しない（DB に残るのは結果のみ）
