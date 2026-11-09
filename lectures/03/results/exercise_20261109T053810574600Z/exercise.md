# 第3回 演習の実行ログ

共通モデル: `gemini-3.5-flash-lite`。各条件1回、新規プロセスで実行。

## bare_tag

AIE2026の講座で使う「lecNN-start タグ」とは何ですか？

````````text
[model] gemini-3.5-flash-lite
[質問] AIE2026の講座で使う「lecNN-start タグ」とは何ですか？

[usage] 応答時間: 2.33秒, 入力: 23, 出力: 346
「AIE2026」の具体的な講座のシラバスや教材が手元にないため一般論になりますが、プログラミングやAI開発（Pythonやディープラーニングなど）の講座で使われる場合、**「lecNN-start タグ」**（またはそれに類するカスタムタグ）は、**講義資料（Jupyter Notebookなど）の中で特定のコードブロックやセクションの開始位置を示す目印（マーカー）**である可能性が高いです。

具体的には、以下のような目的で使われていると考えられます。

1. **コードの自動生成・抽出**
   講座の運営側が、Jupyter Notebookなどの教材から「受講生に配布するコード」や「模範解答のコード」を自動的に切り出すために使っているタグ（例: `# [lecNN-start]` のようなコメント形式）。
2. **教材のバージョン管理やセクション分け**
   NN（Neural Networkなどの略称と推測されます）に関する講義モジュールの「Neural Networkの開始（start）」を示すHTMLタグやマークダウンの目印。

もしお使いのテキストやプラットフォーム（Googleコラボレートリ、GitHub、LMSなど）でそのタグを見かけた場合、**「ここからNeural Network（または特定のセクション）の学習やハンズオンが始まりますよ」というプログラム上の、あるいは教材作成上の区切り**を意味しているはずです。

もし可能であれば、そのタグがどのようなファイル（Pythonスクリプト、Jupyter Notebook、HTMLなど）の、どのような文脈で使われているかを追加で教えていただければ、より正確な解説ができるかと思います。

````````

## agent_tag

AIE2026の講座で使う「lecNN-start タグ」とは何ですか？

````````text
[model] gemini-3.5-flash-lite
「lecNN-start タグ」とは、AIE2026の講座リポジトリにおいて、各回の演習開始時点のコードに付けられているGitタグのことです（例: `lec03-start`）。

前の回の演習が終わっていなくても、このタグを指定してブランチを作成すれば、いつでもその回の演習からスムーズに始められるように用意されています。

（関連回：第1回）

--- trace ---
[tool call]   search_glossary({'query': 'lecNN-start タグ'})
[tool return] search_glossary -> [{"term": "lecNN-start タグ", "lecture": 1, "definition": "AIE2026の講座repoで、各回の演習開始時点のコードに付けているGitタグ（例：lec03-start）。前の回が終わっ…
[usage] RunUsage(cost=Decimal('0.0005893'), details={'text_prompt_tokens': 1031}, input_text_tokens=1031, input_tokens=1031, output_tokens=112, requests=2, tool_calls=1)

````````

## bare_levels

AIE2026の講座の宿題にある「3レベル」とは何ですか？

````````text
[model] gemini-3.5-flash-lite
[質問] AIE2026の講座の宿題にある「3レベル」とは何ですか？

[usage] 応答時間: 2.42秒, 入力: 21, 出力: 422
AIE2026（AIエンジニア育成講座などの2026年目標のプログラムを指していると思われます）の宿題における「3レベル」という言葉は、通常、**学習者の理解度や実装の難易度に合わせて課題が3段階に分かれているシステム**を指します。

具体的な内容は講座のカリキュラムによって異なりますが、一般的には以下のような構成になっています。

### 一般的な「3レベル」の構造

1. **レベル1（基礎・ベーシック）**
   * **内容:** 授業で習ったコードをそのまま動かす、穴埋め問題、基本的な用語の確認など。
   * **目的:** 環境構築が正しくできているか、基本の構文を理解しているかを確認する。

2. **レベル2（応用・スタンダード）**
   * **内容:** 少し条件を変えたり、自分でコードを少し書き加えたりして、自力でプログラムを完成させる。
   * **目的:** 知識を定着させ、自力で簡単な課題を解決する力をつける。

3. **レベル3（発展・アドバンス）**
   * **内容:** 応用力を試す問題、エラー処理を追加する、より効率的なコードにリファクタリングする、独自の機能を実装するなど。
   * **目的:** 実務に近いレベルでの問題解決能力や、応用力を養う。

---

### 注意すべきポイント
* **「どこまで提出すべきか？」**
  講座によっては「全員レベル2まで必須、レベル3は挑戦課題」などのルールが定められている場合があります。
* **確認方法:**
  もし正確な定義が分からない場合は、AIE2026の**利用しているプラットフォーム（Slack、Discord、LMSの案内ページなど）の「宿題のルール」や「第〇回課題の概要」**というドキュメントを再度確認するか、講師やTA（ティーチングアシスタント）に質問するのが確実です。

````````

## agent_levels

AIE2026の講座の宿題にある「3レベル」とは何ですか？

````````text
[model] gemini-3.5-flash-lite
用語集によると、AIE2026の宿題における「3レベル」とは、**「基礎」「実装」「発展」**の3段階で構成される宿題の仕組みのことです。

具体的には以下のような内容になっています。

* **基礎**：講義内容の確認
* **実装**：自分でコードを書く
* **発展**：調査や試行

どれか1つに取り組めばその回の宿題は完了となり、原則として採点は行われません。ご自身の理解度や目的に合わせて選んで取り組んでみてくださいね。

第1回

--- trace ---
[tool call]   search_glossary({'query': '3レベル'})
[tool return] search_glossary -> [{"term": "宿題の3レベル", "lecture": 1, "definition": "AIE2026の宿題の構成。「基礎（講義内容の確認）」「実装（自分でコードを書く）」「発展（調査や試行）」の3段階があり、どれか1つに取り組…
[usage] RunUsage(cost=Decimal('0.0006693'), details={'text_prompt_tokens': 1031}, input_text_tokens=1031, input_tokens=1031, output_tokens=144, requests=2, tool_calls=1)

````````

## agent_lora

LoRAとQLoRAの違いは？

````````text
[model] gemini-3.5-flash-lite
LoRAとQLoRAの主な違いは、**ベースモデルの重みの保持方法と量子化の有無**にあります。

* **LoRA（Low-Rank Adaptation）**
  事前学習済みの重みを固定したまま、重みの更新分を小さな低ランク行列（2つの行列の積）で表し、その部分だけを学習するPEFT（Parameter-Efficient Fine-Tuning）手法です。学習パラメータや保存ファイルを大幅に削減できます。

* **QLoRA（Quantized LoRA）**
  LoRAの仕組みをベースにしつつ、**ベースモデルの重みを4ビットなどに量子化してメモリを節約した状態で学習する**手法です。これにより、より大きなモデルを限られたGPUメモリ環境でも効率よく扱えるようになります。

関連する回：第2回

--- trace ---
[tool call]   search_glossary({'query': 'LoRA'})
[tool call]   search_glossary({'query': 'QLoRA'})
[tool return] search_glossary -> [{"term": "LoRA", "lecture": 2, "definition": "事前学習済みの重みは固定したまま、重みの更新分を2つの小さな行列の積（低ランク行列）で表し、その小さな行列だけを学習するPEFT手法。学習するパラ…
[tool return] search_glossary -> [{"term": "QLoRA", "lecture": 2, "definition": "ベースモデルの重みを4ビットなどに量子化してメモリを節約したうえで、LoRAで学習する手法。より大きなモデルを小さなGPUで扱える。本講座の第2…
[usage] RunUsage(cost=Decimal('0.0009682'), details={'text_prompt_tokens': 1444}, input_text_tokens=1444, input_tokens=1444, output_tokens=214, requests=2, tool_calls=2)

````````

## agent_quiz

第2回の内容から確認問題を1問出して

````````text
[model] gemini-3.5-flash-lite
第2回「ファインチューニングとLoRA」から確認問題を出題します。

**【問題】**
「事前学習」とは、どのような学習段階のことですか？講座の用語集の定義に沿って説明してください。

---

**【模範解答のヒント】**
大量のテキストデータを用いて、モデルに**「次のトークンを予測する」**タスクを学習させる、最初の段階のことです。言語の基礎的な知識や常識はこの段階で獲得されます。

（第2回）

--- trace ---
[tool call]   get_lecture_summary({'lecture': 2})
[tool return] get_lecture_summary -> # 第2回 ファインチューニングとLoRA

## この回のねらい

- 事前学習とファインチューニングの違い、ファインチューニングが向く場面と向かない場面を理解する
- LoRAの考え方を理解し、Google Colab上で小さなモデルを…
[tool call]   search_glossary({'query': 'LoRA'})
[tool return] search_glossary -> [{"term": "LoRA", "lecture": 2, "definition": "事前学習済みの重みは固定したまま、重みの更新分を2つの小さな行列の積（低ランク行列）で表し、その小さな行列だけを学習するPEFT手法。学習するパラ…
[tool call]   make_quiz({'lecture': 2})
[tool return] make_quiz -> {"lecture": 2, "term": "事前学習", "question": "「事前学習」とは何ですか？", "answer": "大量の汎用テキストで、次のトークンを予測するようにモデルを学習させる最初の段階。言語の知識や一般的…
[usage] RunUsage(cost=Decimal('0.0016370'), details={'text_prompt_tokens': 4115}, input_text_tokens=4115, input_tokens=4115, output_tokens=161, requests=4, tool_calls=3)

````````

## テスト

```text
....................                                                     [100%]
20 passed in 5.08s

```
