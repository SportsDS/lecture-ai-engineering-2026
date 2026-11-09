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

- 実行日時（UTC）: 2026-11-09T05:20:59.765055+00:00
- 共通モデル: `gemini-3.5-flash-lite`
- パッケージ版: `{"google-adk": "2.14.0", "google-genai": "2.31.0", "pydantic-ai-slim": "2.57.0"}`
- 各質問をそれぞれ新規プロセスで実行し、過去の会話履歴は共有しない。
- 指示文・ツール関数・モデル名・APIキーをそろえた。SDK固有の既定生成設定は同一化していない。
- 各条件1回の観測。出力差をフレームワークだけの因果効果とは解釈しない。
- ADKは `adk run --in_memory --jsonl` で実行。Pydantic AIのrequestsと同等のADK指標は集計していない。

| 質問 | Pydantic AIの呼び出し | ADKの呼び出し | Pydantic requests |
|---|---|---|---|
| AIE2026の講座で使う「lecNN-start タグ」とは何ですか？ | search_glossary({"query": "lecNN-start タグ"}) | search_glossary({"query": "lecNN-start タグ"}) | 2 |
| LoRAとQLoRAの違いは？ | search_glossary({"query": "LoRA"}); search_glossary({"query": "QLoRA"}) | search_glossary({"query": "LoRA"}); search_glossary({"query": "QLoRA"}) | 2 |
| 第3回では何を学ぶ？ | get_lecture_summary({"lecture": 3}) | get_lecture_summary({"lecture": 3}) | 2 |
| 用語「AIE未登録検証語98765」の意味は？ | search_glossary({"query": "AIE未登録検証語98765"}) | search_glossary({"query": "AIE未登録検証語98765"}) | 2 |

### Q1: AIE2026の講座で使う「lecNN-start タグ」とは何ですか？

**Pydantic AIの実回答**

````````text
「lecNN-start タグ」とは、AIE2026の講座用リポジトリで、各回の演習を開始するときの基準となるコードに付けられているGitタグのことです（例: `lec03-start`）。

もし前の回の演習が途中であったり終わっていなかったりしても、このタグから新しくブランチを作成すれば、その回の演習をスムーズに始められるようになっています。

関係する回：第1回
````````

**Google ADKの実回答**

````````text
「lecNN-start タグ」とは、AIE2026の講座用リポジトリで、各回の演習開始時点のコードに付けられているGitタグのことです（例: `lec03-start`）。

もし前の回までの内容が完了していなくても、このタグから新しくブランチを作成することで、その回の演習をスムーズに始められるようになっています。

関連する回：第1回（関係用語: branch）
````````

呼び出し列（ツール名・引数・順序）: 一致。

### Q2: LoRAとQLoRAの違いは？

**Pydantic AIの実回答**

````````text
講座の用語集によると、LoRAとQLoRAの違いは以下のとおりです。

* **LoRA**
  事前学習済みの重みを固定したまま、重みの更新分を2つの小さな行列（低ランク行列）の積で表し、その小さな行列だけを学習するPEFT（Parameter-Efficient Fine-Tuning）手法です。学習するパラメータが少なく、学習結果も小さなファイルで保存できます。
* **QLoRA**
  ベースモデルの重みを4ビットなどに**量子化**してメモリを大幅に節約したうえで、LoRAによるファインチューニングを行う手法です。これにより、より大きなモデルを小さなGPU環境でも扱えるようになります。

関係する回：第2回
````````

**Google ADKの実回答**

````````text
LoRAとQLoRAの主な違いは、**ベースモデルの重みの保持方法とメモリ節約のアプローチ**にあります。

* **LoRA**:
  事前学習済みの重みを固定したまま、重みの更新分を表す小さな低ランク行列（アダプタ）を追加し、その部分だけを学習するPEFT（Parameter-Efficient Fine-Tuning）手法です。学習パラメータや保存ファイルを大幅に削減できます。
* **QLoRA**:
  LoRAの仕組みをベースにしつつ、**ベースモデルの重みを4ビットなどに量子化**してメモリをさらに大幅に節約したうえで学習を行う手法です。これにより、より大きなモデルを小さなGPUメモリでも扱えるようになります。

関係する回：第2回
````````

呼び出し列（ツール名・引数・順序）: 一致。

### Q3: 第3回では何を学ぶ？

**Pydantic AIの実回答**

````````text
第3回では「**AIエージェント**」について学びます。

### おもな内容
- **AIエージェントの基本構造**：「モデル ＋ ループ ＋ ツール」の組み合わせにより、自律的にタスクを遂行する仕組みを学びます。
- **ツールとエージェントループ**：LLMが外部ツールを呼び出し、その結果を受け取って次の行動を決める一連の流れや、それに伴うコスト（応答時間や料金）について理解します。
- **フレームワークと演習**：Pydantic AIなどを活用し、実際にツールを使う学習支援エージェントの作成や動作確認を行います。

第3回
````````

**Google ADKの実回答**

````````text
第3回では**「AIエージェント」**について学びます。

主な内容は以下の通りです：
- **AIエージェントの基本構造**：「モデル ＋ ループ ＋ ツール」の組み合わせで自律的に動作する仕組みを理解する。
- **ツールとハーネス**：LLMが外部ツールを呼び出す仕組みや、ツール・ループを包む「ハーネス」の役割を学ぶ。
- **フレームワークの活用**：Pydantic AIやADKを用いたエージェントの実装方法を体験し、TestModelを使ったテストやガードレール（Human-in-the-loopなど）について学ぶ。

関連回：第3回
````````

呼び出し列（ツール名・引数・順序）: 一致。

### Q4: 用語「AIE未登録検証語98765」の意味は？

**Pydantic AIの実回答**

````````text
申し訳ありません。用語集には「AIE未登録検証語98765」という用語は登録されていません。
````````

**Google ADKの実回答**

````````text
用語集には「AIE未登録検証語98765」という用語は見つかりませんでした。そのため、正確な意味については分かりかねます。

関連する回: なし
````````

呼び出し列（ツール名・引数・順序）: 一致。

### 解釈の範囲

関数を共有するとデータ検索処理自体は共通になる。一方、呼び出すツール・引数・順序と回答文はモデルと各SDKの実行処理に依存する。
回答が一致しても全入力での同等性は証明できず、回答が異なっても1回の比較だけではフレームワークの優劣は判断できない。
用語集にない語への応答、講義要約ツールの利用、回答末尾の関連回の記載を実回答で確認する。

<!-- adk-comparison:end -->
