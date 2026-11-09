# 第3回の再現手順

提出本文は [answer.md](answer.md)。演習の追加ツールは `app/tools.py` の `make_quiz` で、Pydantic AI版・ADK版に同じ3関数を登録している。

## 演習：素のLLMとエージェント、trace、小テスト

APIキー設定済みのCodespacesで、リポジトリ直下から実行する。

```bash
uv run --with google-adk==2.14.0 python scripts/run_lecture03_exercise.py
```

第1回の既定質問（宿題の3レベル）と第3回資料の開始タグの質問について、素のLLMとエージェントを同じ質問で比較する。さらにLoRA・QLoRAと確認問題の質問を `--trace` 付きで実行する。各実行は新規プロセスで、質問間は15秒空ける。

結果は `lectures/03/results/exercise_実行日時/` の `exercise.json`・`exercise.md`・各標準出力/標準エラーログに保存する。pytestと3ツールの共有確認も記録する。APIエラー時は成功したとの記録を作らず停止する。

## 発展(a)：Google ADKとの比較

```bash
uv run --with google-adk==2.14.0 python scripts/compare_adk.py
```

用語・講義内容・未登録語・追加した小テストの5問を両方式で実行する。全問成功時にだけ `answer.md` の実回答欄を更新する。生ログは `lectures/03/results/実行日時/` に保存する。

コードの書き方と同じ質問への回答を比較し、添付の課題資料に従って `adk run` を使う。`adk web` 画面の比較は行っていない。

## API不要の検証

```bash
uv run pytest -q
uv run --with google-adk==2.14.0 python scripts/verify_adk_offline.py
```

TestModelは接続・登録情報の確認に用い、ダミーの回答を実モデル比較の結果として扱わない。

## 変更後の保存

実回答と考察を確認し、必要な変更だけをcommit・pushする。自分のfork内の `lec03-adk` → `main` のPRが提出先である。mainへのマージは行わない。

APIキーは環境変数 `GEMINI_API_KEY` から読み、コード・ログ・コミットに記録しない。
