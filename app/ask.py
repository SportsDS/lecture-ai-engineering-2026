"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    uv run python -m app.ask --interactive
    uv run python -m app.ask --temperature 0.8 "LoRAとは何ですか？"

ツールを持たない「素の」呼び出し。--interactive では会話履歴を保つ。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
import time

from google import genai
from google.genai import types
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def print_usage(response: types.GenerateContentResponse, elapsed: float) -> None:
    """応答時間と、モデルが返したトークン使用量を表示する。"""
    usage = response.usage_metadata
    if usage is None:
        print(f"[usage] 応答時間: {elapsed:.2f}秒, トークン数: 取得できません")
        return
    print(
        f"[usage] 応答時間: {elapsed:.2f}秒, "
        f"入力: {usage.prompt_token_count}, 出力: {usage.candidates_token_count}"
    )


def ask(question: str, chat=None, temperature: float | None = None) -> str:
    client = genai.Client(api_key=get_api_key()) if chat is None else None
    if chat is None:
        config = types.GenerateContentConfig(temperature=temperature) if temperature is not None else None
        chat = client.chats.create(model=MODEL, config=config)

    started_at = time.perf_counter()
    response = chat.send_message(question)
    print_usage(response, time.perf_counter() - started_at)
    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument("--interactive", "-i", action="store_true", help="会話履歴を保ったまま続けて質問する")
    parser.add_argument("--temperature", type=float, help="生成温度（基礎の比較用）")
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    try:
        if not args.interactive:
            print(f"[質問] {args.question}\n")
            print(ask(args.question, temperature=args.temperature))
            return

        config = types.GenerateContentConfig(temperature=args.temperature) if args.temperature is not None else None
        client = genai.Client(api_key=get_api_key())
        chat = client.chats.create(model=MODEL, config=config)
        question = args.question
        while True:
            if question:
                print(f"[質問] {question}")
            else:
                question = input("質問（終了するには exit）: ").strip()
            if question.lower() in {"exit", "quit", "終了"}:
                break
            if question:
                print(ask(question, chat=chat))
            question = None
    except (EOFError, KeyboardInterrupt):
        print("\n対話を終了しました。")
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
