"""第3回発展(a)の実モデル比較。repo直下から実行する。

uv run --with google-adk==2.14.0 python scripts/compare_adk.py
API失敗時は未完了を返し、成功済みのanswer.mdは書き換えない。
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = [
    'AIE2026の講座で使う「lecNN-start タグ」とは何ですか？',
    'LoRAとQLoRAの違いは？',
    '第3回では何を学ぶ？',
    '用語「AIE未登録検証語98765」の意味は？',
    '第2回の内容から確認問題を1問出して',
]
START = '<!-- adk-comparison:start -->'
END = '<!-- adk-comparison:end -->'


def pydantic_worker(question: str) -> None:
    from app.agent import agent, build_model
    from pydantic_ai.messages import ToolCallPart, ToolReturnPart

    result = agent.run_sync(question, model=build_model())
    calls, returns = [], []
    for message in result.all_messages():
        for part in message.parts:
            if isinstance(part, ToolCallPart):
                calls.append({'name': part.tool_name, 'args': part.args_as_dict()})
            elif isinstance(part, ToolReturnPart):
                returns.append({'name': part.tool_name, 'result': part.content})
    print(json.dumps({'output': result.output, 'calls': calls, 'returns': returns,
                      'requests': result.usage.requests}, ensure_ascii=False, default=str))


def parse_adk(stdout: str) -> dict:
    events = []
    for line in stdout.splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and (isinstance(obj.get('content'), dict) or obj.get('error_code') or obj.get('errorCode')):
            events.append(obj)
    calls, returns, texts = [], [], []
    for event in events:
        if event.get('error_code') or event.get('errorCode'):
            raise ValueError('ADKがエラーイベントを返しました。rawログを確認してください。')
        event_text = []
        has_call = False
        for part in event['content'].get('parts', []):
            call = part.get('function_call') or part.get('functionCall')
            returned = part.get('function_response') or part.get('functionResponse')
            if call:
                has_call = True
                calls.append({'name': call['name'], 'args': call.get('args', {})})
            if returned:
                returns.append(returned)
            if part.get('text') and not part.get('thought'):
                event_text.append(part['text'])
        if event_text and not has_call and event['content'].get('role') != 'user':
            texts = event_text
    if not texts:
        raise ValueError('ADKの最終回答テキストを取得できませんでした。rawログを確認してください。')
    return {'output': '\n'.join(texts), 'calls': calls, 'returns': returns,
            'requests': None, 'events': events}


def run(command: list[str], env: dict, log: Path) -> str:
    try:
        result = subprocess.run(command, cwd=ROOT, env=env, text=True,
                                capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        raise RuntimeError('180秒でタイムアウト。途中の比較は完了扱いにしません。') from None
    # キーが例外に含まれてもログには残さない。
    def redact(value):
        for name in ('GEMINI_API_KEY', 'GOOGLE_API_KEY'):
            if env.get(name):
                value = value.replace(env[name], '[REDACTED]')
        return value
    stdout, stderr = redact(result.stdout), redact(result.stderr)
    log.with_suffix('.stdout.txt').write_text(stdout, encoding='utf-8')
    log.with_suffix('.stderr.txt').write_text(stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'{command[0]} が終了コード {result.returncode}。{log.parent} のログを確認してください。')
    return stdout


def render(rows: list[dict], model: str, versions: dict, stamp: str) -> str:
    lines = ['## 実モデル比較結果', '', f'- 実行日時（UTC）: {stamp}',
             f'- 共通モデル: `{model}`', f'- パッケージ版: `{json.dumps(versions)}`',
             '- 各質問をそれぞれ新規プロセスで実行し、過去の会話履歴は共有しない。',
             '- 指示文・ツール関数・モデル名・APIキーをそろえた。SDK固有の既定生成設定は同一化していない。',
             '- 各条件1回の観測。出力差をフレームワークだけの因果効果とは解釈しない。',
             '- ADKは `adk run --in_memory --jsonl` で実行。Pydantic AIのrequestsと同等のADK指標は集計していない。', '',
             '| 質問 | Pydantic AIの呼び出し | ADKの呼び出し | Pydantic requests |',
             '|---|---|---|---|']
    for row in rows:
        def calls(kind):
            return '; '.join(c['name'] + '(' + json.dumps(c['args'], ensure_ascii=False) + ')' for c in row[kind]['calls']) or 'なし'
        lines.append(f"| {row['question']} | {calls('pydantic')} | {calls('adk')} | {row['pydantic']['requests']} |")
    for i, row in enumerate(rows, 1):
        lines.extend(['', f"### Q{i}: {row['question']}", ''])
        for name, key in [('Pydantic AI', 'pydantic'), ('Google ADK', 'adk')]:
            lines.extend([f'**{name}の実回答**', '', '````````text', row[key]['output'], '````````', ''])
        left, right = row['pydantic']['calls'], row['adk']['calls']
        lines.append('呼び出し列（ツール名・引数・順序）: ' + ('一致。' if left == right else '異なる。上表・実回答とrawログで確認できる。'))
    lines.extend(['', '### 解釈の範囲', '',
                  '関数を共有するとデータ検索処理自体は共通になる。一方、呼び出すツール・引数・順序と回答文はモデルと各SDKの実行処理に依存する。',
                  '回答が一致しても全入力での同等性は証明できず、回答が異なっても1回の比較だけではフレームワークの優劣は判断できない。',
                  '用語集にない語への応答、講義要約ツールの利用、回答末尾の関連回の記載を実回答で確認する。', ''])
    return '\n'.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', help=argparse.SUPPRESS)
    parser.add_argument('--delay', type=float, default=15, help='質問間の待機秒数（既定15秒）')
    args = parser.parse_args()
    if args.worker is not None:
        pydantic_worker(args.worker)
        return
    if not os.getenv('GEMINI_API_KEY'):
        raise SystemExit('未実行: GEMINI_API_KEYがありません。キーを登録済みのCodespacesで実行してください。キーをチャットに貼る必要はありません。')
    adk = shutil.which('adk')
    if not adk:
        raise SystemExit('adkがありません。uv run --with google-adk==2.14.0 python scripts/compare_adk.py で実行してください。')
    from app.config import MODEL
    stamp = datetime.now(timezone.utc).isoformat()
    output = ROOT / 'lectures/03/results' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output.mkdir(parents=True)
    env = dict(os.environ)
    env['PYTHONPATH'] = str(ROOT)
    env['GOOGLE_API_KEY'] = env['GEMINI_API_KEY']
    env['GOOGLE_GENAI_USE_VERTEXAI'] = 'FALSE'
    env['PYDANTIC_AI_NO_BANNER'] = '1'
    versions = {name: importlib.metadata.version(name) for name in ('google-adk', 'google-genai', 'pydantic-ai-slim')}
    rows = []
    for i, question in enumerate(QUESTIONS, 1):
        print(f'[{i}/{len(QUESTIONS)}] {question}', flush=True)
        pydantic = json.loads(run([sys.executable, str(Path(__file__).resolve()), '--worker', question], env, output / f'q{i}_pydantic'))
        adk_result = parse_adk(run([adk, 'run', '--in_memory', '--jsonl', 'adk_agent/glossary_agent', question], env, output / f'q{i}_adk'))
        rows.append({'question': question, 'pydantic': pydantic, 'adk': adk_result})
        if i < len(QUESTIONS):
            time.sleep(max(0, args.delay))
    (output / 'comparison.json').write_text(json.dumps({'model': MODEL, 'versions': versions, 'rows': rows}, ensure_ascii=False, indent=2), encoding='utf-8')
    report = render(rows, MODEL, versions, stamp)
    (output / 'comparison.md').write_text(report, encoding='utf-8')
    answer_path = ROOT / 'lectures/03/answer.md'
    answer = answer_path.read_text(encoding='utf-8')
    block = START + '\n\n' + report + '\n' + END
    if START not in answer or END not in answer:
        raise SystemExit('結果は保存しましたがanswer.mdの追記位置がありません。comparison.mdを確認してください。')
    answer = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: block, answer, flags=re.S)
    answer_path.write_text(answer, encoding='utf-8')
    print(f'比較完了: {output.relative_to(ROOT)}。実回答と考察を確認し、answer.mdとresultsをcommit/pushしてください。')


if __name__ == '__main__':
    # python scripts/... の実行でも repo の app を読み込めるようにする。
    sys.path.insert(0, str(ROOT))
    try:
        main()
    except (RuntimeError, ValueError) as error:
        raise SystemExit(f'比較未完了: {error}') from None
