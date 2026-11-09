# 第3回 解答

## 演習

今回の変更は宿題の発展(a)に限定した。演習の実モデル実行・`make_quiz` の追加はこの変更には含めていない。

## 宿題

- 取り組んだレベル：**発展(a)：Google ADKへの移植**
- やったこと：`adk_agent/glossary_agent/agent.py` と `__init__.py` を追加した。`app.agent.INSTRUCTIONS`、`app.tools.search_glossary`、`app.tools.get_lecture_summary` を直接インポートし、同じ指示と同じ関数をADKの `Agent` に渡した。モデルも `app.config.MODEL` を共有した。`app/` と講座の `pyproject.toml`・`uv.lock` は変更していない。
- 結果：下記の静的比較とAPI不要の検証を実施した。実モデルによる回答比較の実行状況・結果は末尾の「実モデル比較結果」に示す。実行時に実回答と呼び出し記録を追記するスクリプトを用意し、未実行の回答・回数は作成しない。
- 気づき・疑問：指示文と検索関数を分離しておくと、エージェント構築部分の変更でフレームワークを置き換えられる。ただし、同じ関数・指示でもモデルに送るリクエストの構成や既定の生成設定まで同じとは限らない。回答差が出たとき、それがSDK・生成の確率的変動・会話履歴のどれに由来するかは、単発実行だけでは分離できない。

### 書き方の比較

| 比較項目 | Pydantic AI（演習） | Google ADK（今回） |
|---|---|---|
| エージェント | `pydantic_ai.Agent` | `google.adk.agents.Agent` |
| 指示の渡し方 | `Agent(instructions=INSTRUCTIONS)` | `Agent(instruction=INSTRUCTIONS, ...)` |
| ツール登録 | `agent.tool_plain(tools.search_glossary)` など | `tools=[tools.search_glossary, tools.get_lecture_summary]` |
| モデル指定 | 実行時に `GoogleModel` を渡す | 構築時に `model=MODEL` を渡す |
| 通常の実行 | `uv run python -m app.agent --trace "質問"` | `PYTHONPATH=. uv run --with google-adk==2.14.0 adk run adk_agent/glossary_agent` |
| 直接共有したもの | 元の指示文字列・Python関数 | 同じ文字列・同じ関数オブジェクト |

`instructions`（複数形）と `instruction`（単数形）が異なる。ツール名・docstring・型ヒントは関数の再利用により維持される。一方、SDKが生成するスキーマやモデルへの要求全体の完全一致は、このことだけでは保証できない。

### 検証と再現手順

API不要の検証結果は [offline_verification.txt](offline_verification.txt) に記録する。
この検証は指示・関数の共有、ツールの実出力、SDKへの登録を確かめるもので、実モデルの回答品質の評価ではない。

Gemini APIキーが登録済みのCodespacesで次を実行する。

```bash
uv run --with google-adk==2.14.0 python scripts/compare_adk.py
```

比較する質問は、演習と同じ開始タグの質問、LoRAとQLoRAの違い、第3回の内容、未登録語の4件。
各条件を新規プロセスで実行する。Pydantic AIの結果・ツール名・引数・戻り値・requestsと、`adk run --jsonl` のイベント・実回答を `lectures/03/results/` に保存する。
4件すべて成功した場合に限り、末尾の結果欄を更新する。レート制限・認証・タイムアウトなどの失敗時は、成功済み結果を上書きせず未完了で停止する。APIキーは保存しない。

### 制約・AI利用

- この提出文とコードの作成・API不要の検証にはAIを利用した。実モデル未実行の段階を完了とは扱わない。
- 発展(a)は添付の宿題資料に従い `adk run` で比較する。リポジトリの `problem.md` には `adk web` の記載もあるが、今回は添付資料の手順を優先した。Web画面の観察結果は記載しない。
- 実行結果を得た後も、本人が回答・ログを読み、気づきが自分の理解と合うか確認する必要がある。

### 出典

1. 配布資料「第3回宿題資料.pdf」、発展(a)・提出の説明（発行日記載なし）。
2. [講座の課題説明](https://github.com/SportsDS/lecture-ai-engineering-2026/blob/62b03bee1a52fb21bcbe52f7973c26558d0a3a97/lectures/03/problem.md)、2026-11-09確認。
3. [講座の元エージェント](https://github.com/SportsDS/lecture-ai-engineering-2026/blob/62b03bee1a52fb21bcbe52f7973c26558d0a3a97/app/agent.py)、2026-11-09確認。
4. [Google ADK Python Quickstart](https://adk.dev/get-started/python/)、公開日記載なし、2026-11-09確認。`root_agent`・`instruction`・`tools`・`adk run` の使い方を参照。
5. ローカルにインストールした `google-adk==2.14.0` の `adk run --help` と実際の登録結果。

<!-- adk-comparison:start -->

## 実モデル比較結果

**未実行：Gemini APIキーがあるCodespacesで比較を実行する必要がある。現段階では提出完了ではない。**

<!-- adk-comparison:end -->
