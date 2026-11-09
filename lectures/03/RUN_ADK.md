# 第3回 発展(a) の比較を仕上げる

ADKの実装・API不要の検証は完了。実モデルの回答比較が残っている。
`GEMINI_API_KEY` が設定されている、このリポジトリのCodespacesで実行する。キーをチャットやコードに書かない。

## 1. ブランチを開く

```bash
git fetch origin
git switch lec03-adk
```

すでに同じブランチで作業している場合は、未コミット変更を確認し、必要に応じて `git pull --ff-only` する。

## 2. 比較する

リポジトリ直下で実行する。

```bash
uv run --with google-adk==2.14.0 python scripts/compare_adk.py
```

4問×2方式を順に実行する。各エージェントは1問の処理で複数回APIを呼ぶ場合がある。レート制限などで失敗したら、表示されたログを確認してから再実行する。未完了時には `answer.md` の結果欄を更新しない。

モデルが利用できない場合は、利用可能なモデルを `AIE_MODEL` に指定して同じコマンドを実行する。両方式に同じモデル設定が渡る。

## 3. 実回答と提出文を確認してpushする

`lectures/03/answer.md` 末尾に、実回答・ツール呼び出し・Pydantic AIのrequestsが追記される。
rawログと比較し、用語集の参照・関連回の記載・未登録語への応答を確認する。必要なら「気づき・疑問」を自分の理解に合わせて編集する。

```bash
git add lectures/03/answer.md lectures/03/results/
git commit -m "第3回: ADKとPydantic AIの実モデル比較結果を記録"
git push origin lec03-adk
```

GitHubのドラフトPRを開き、実行結果を確認してから「Ready for review」に切り替える。自分のforkの `main` 向けのPRが講座の提出形式で、上流リポジトリへのPRやmainへのマージは必要ない。

## 任意：APIを使わず再検証

```bash
uv run pytest -q
uv run --with google-adk==2.14.0 python scripts/verify_adk_offline.py
```

このチェックは実モデルの回答比較の代用にはならない。
