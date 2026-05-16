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

知識想起のフラッシュカード。`name` の解法について 1 問だけ Q を提示する。

- 問いの粒度: 「この典型解法を一言で言うと？」「どんな問題条件のときに使う？」「主な計算量は？」「実装の核となるアイデアは？」のいずれか1つ
- 答えは伏せて、ユーザの回答を待つ
- ユーザ回答後、模範解答と照合し、合致点 / 補足 / 抜けを 3-5 行で指摘
- 結果（○/×）が確定したら `/log <technique_id> card <o|x> [--note "..."]` を案内する

### kind = impl

基礎実装。**典型90 本問またはその類題** を提示する。

- まず `name` の解法（典型90 の番号で示された解法）の本問または難易度を上げすぎない類題 1 問を選び、問題文 / 入力形式 / 制約 / サンプル を提示する
- ★3 以下なら本問、★4 以上なら易しい類題から始めると良い
- ユーザがコードを書いたらレビューし、テストケースで合うか確認
- 結果確定後 `/log <technique_id> impl <o|x> [--uri ...] [--note ...]` を案内

### kind = advanced

応用。**実問題（本問相当）** を提示する。

- `stars` を参考に同等以上の難易度の AtCoder 本問 を提案する（typical90 既出回避）
- 候補が思い当たらない場合は WebFetch で AtCoder Problems や atcoder-tags を確認
- 問題URLを示し、`/log <technique_id> advanced <o|x> --uri <URL>` を案内
- 解いた後の感想 / 詰まりポイントは `--note` で残すよう促す

## 共通方針

- 出題はこの会話の中で完結させる。問題ファイルや一時データを書き出す必要はない
- 問題本文・解説は記録しない（DB に残るのは結果のみ）
