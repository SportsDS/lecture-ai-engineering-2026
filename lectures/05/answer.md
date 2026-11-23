# 第5回 解答

## 演習

- `--list-tools` の結果：関数を直接登録する場合は `search_glossary`、`get_lecture_summary`、`make_quiz` の3個。MCP経由では設定上のサーバー名 `glossary` が付き、`glossary_search_glossary`、`glossary_get_lecture_summary`、`glossary_make_quiz` の3個になった。名前以外の説明と引数は、元の関数のdocstringと型ヒントに基づく。
- `--mcp --trace` の実モデル実行：この作業環境には `GEMINI_API_KEY` が設定されていないため未実施。したがって実モデルのツール選択、最終回答、`requests` 回数は記録していない。代わりにTestModelを使ったテストで、`glossary_make_quiz(lecture=2)` の呼び出しとMCPから返る結果を確認した。
- MCPサーバーに公開したツール：`get_lecture_summary` と `make_quiz`。説明は各関数のdocstringをそのまま利用する。`--mcp --list-tools` で `glossary_get_lecture_summary` と `glossary_make_quiz` が表示されることを確認した。
- fetchサーバー：未追加。外部MCPサーバーを含む実モデルでの呼び分けは確認していない。

## 宿題

- 取り組んだレベル：**実装**
- やったこと：第3回で作成済みの `make_quiz(lecture: int)` を `app/mcp_server.py` からMCPツールとして公開した。TestModelを使った配線テストを `tests/test_mcp_server.py` に追加し、通常の回の問題・模範解答が返ることと、不正な回 `0` に対する説明がMCPのツール戻り値として返ることを確認した。
- 結果：`uv run python -m app.agent --mcp --list-tools` でMCPツール3個を確認。`uv run pytest -q tests/test_mcp_server.py` は **4 passed**、全テスト `uv run pytest -q` は **22 passed**。
- 気づき・疑問：MCPクライアント側からはサーバー名付きのツール名で見えるが、関数の説明・引数・処理は既存のPython関数を再利用できた。TestModelの配線テストで、入力引数を固定しないとテスト用データ生成に任されてしまうため、今回のテストでは `gen_tool_args` を上書きして講義回を明示した。実モデルでの `--trace` はAPIキーがないため未確認であり、TestModelでの結果を実モデルの選択傾向としては解釈していない。
