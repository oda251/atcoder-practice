# atcoder-practice

競プロ典型解法の練習ログ。技法カタログ × 3 種類の練習（`card` / `impl` / `advanced`）の出題数と正答率を SQLite に蓄積する。Claude Code の project skill `/ask` `/log` `/stats` から操作する。

## セットアップ

```sh
python3 scripts/init_db.py
```

## 使い方

```text
/ask [--kind card|impl|advanced] [--tech <技法名>] [--variation-of <親>]
/log  <技法名> <card|impl|advanced> <o|x> [--uri ...] [--note "..."]
/stats [--tech <技法名>] [--variation-of <親>] [--kind ...]
```

技法名にスペースや `/` を含む場合は quote（`"GCD / LCM"` 等）。

## 構成

- `scripts/init_db.py` — スキーマと技法カタログ (158件) の一次ソース
- `.claude/skills/{ask,log,stats}/SKILL.md` — 操作の挙動定義
- `data/practice.db` — SQLite 本体（gitignore）

技法カタログは日本語名を PK にし、`variation_of` で親バリエーションを指す（例: `bitDP` → `部分和bitDP / 集合分割bitDP / ...`）。

SRS は attempts から派生計算: `reps` = 直近の連続正解数、`interval_days = 2 ** min(reps, 7)`、`last_at + interval < now` で due。`/ask` は unseen → due → fresh 優先で 1 件選ぶ。
