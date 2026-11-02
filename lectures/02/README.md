# 第2回・発展課題の実行記録

提出本文は [answer.md](answer.md)。実行ノートブックは [Google Colab](https://colab.research.google.com/drive/1iVyUkVQ8SVEUyMEhP50k9AZ3aCr7mW1R?usp=sharing)。元の架空FAQ演習の結果とは区別している。

- `data/`：実験時の用語集、公式生成器の116件の出力、JSON回答に変換した学習116件、検証58件、評価30問と正解。
- `results/`：添付ZIPから取り出した原始JSON、当時の実行コード `experiment_executed.py`、追加のAI内容照合・整合性監査。原始JSONの数値は変更していない。
- `../../scripts/lec02_experiment.py`：パスと系列長監査を修正した再実行用コード。出力先を `lectures/02/reproduction_results/` に分離し、提出済み結果とanswer.mdを上書きしない。修正後のGPU学習は再実行していない。

## 学習なしの再評価

リポジトリのルートで次を実行する（標準ライブラリのみ）。

```bash
python scripts/lec02_experiment.py
```

この処理はデータと検索評価を再生成する。学習は実行しない。`preparation.json` のtraining_executed=falseはこの段階の状態を表す。

## GPUでの再実行

実行済みColabは上のリンクを参照。コードの修正版を再実行する場合は、GPU環境で講義の依存版を導入し、ルートで次を実行する。

```bash
python -m pip uninstall -y torchao
python -m pip install transformers==5.18.0 peft==0.21.1 trl==1.14.2 accelerate==1.15.0 datasets==5.1.0
python scripts/lec02_experiment.py --train
```

torchは実行時と同じ2.11.0+cu130を前提とする。既存の環境に重ねて学習せず、新しいセッションで行う。

`lengths.json` のmax=2は、元の系列長監査の実装不備による値で、実トークン数ではない。修正版では `return_dict=False` を明示し、512超なら停止する。停止した場合は系列長や設定を再検討し、条件変更後の結果として別途記録する。

## 記録の扱い

自動採点はキーワードを含むかを調べるため、意味上の誤回答にも合格を付ける場合がある。元の16/30と、AIによる厳しい事後照合の11/30を区別した。後者は独立した人間の判定ではない。

共有Colabのコードには当時の未実行草稿が埋め込まれている。最終的な実行状況と考察は本PRのanswer.md、実測値はresults/result.jsonを参照する。
