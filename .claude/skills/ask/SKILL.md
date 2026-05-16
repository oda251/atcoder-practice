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
- 「方針が立てば card は ○」を判定基準とする（uri は付けない）

### kind = impl

基礎実装。コードを書いてもらう。

- 該当 technique を典型的に使う問題を Claude が提示する
  - **基本は Claude がその場で生成**（短めで解法本質に集中する設計）
  - その technique を扱う **典型90 の本問が思い当たれば** 優先的に流用してよい（マッピングは `scripts/init_db.py` の `TYPICAL90_MAP` を参照）
- 問題文 / 入力形式 / 制約 / サンプル1-2個 を提示
- ユーザがコードを書いたらレビューし、テストケースで合うか確認（実問題流用時は uri に URL）

### kind = advanced

応用。実問題（AtCoder/yukicoder 本問）でもう一段難度を上げる。

- **基本は Claude がその場で発展問題を生成**（同 technique + 追加考察 1 段）
- AtCoder/yukicoder で **既知の良問が思い当たれば** それを優先（abc/arc の D・E・F が目安）
  - 候補が薄ければ WebFetch で AtCoder Problems や atcoder-tags を確認
- 実問題なら uri に URL、詰まりポイントは note に短く

## 共通方針

- `variation_of` が出ていれば「これは <親技法> の一バリエーション」と意識して出題（親と違いが出るような設定にする）
- 出題はこの会話の中で完結させる。問題ファイルや一時データを書き出す必要はない
- 問題本文・解説は記録しない（DB に残るのは結果のみ）
- **結果確定後、log スキルでログを取る**（uri / note は kind ごとの方針に従う）

## ネタバレ禁止（出題時の厳守事項）

提示してよいのは「題意・入出力形式・制約・サンプル」のみ。問い方は kind ごとに：

- **card**: 「方針を述べてください」だけ。観点の列挙はしない
- **impl**: 「実装してください」だけ。アルゴリズム指定はしない
- **advanced**: 「解いてください（方針 + 実装）」だけ
