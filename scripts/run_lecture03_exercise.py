"""第3回演習の素のLLM比較・trace・小テストを実モデルで記録する。"""
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.compare_adk import run


def main():
    if not os.getenv('GEMINI_API_KEY'):
        raise SystemExit('GEMINI_API_KEYがありません。')
    from app.config import MODEL
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder = ROOT / 'lectures/03/results' / ('exercise_' + stamp)
    folder.mkdir(parents=True)
    env = dict(os.environ, PYTHONPATH=str(ROOT), PYDANTIC_AI_NO_BANNER='1')
    tag = 'AIE2026の講座で使う「lecNN-start タグ」とは何ですか？'
    levels = 'AIE2026の講座の宿題にある「3レベル」とは何ですか？'
    cases = [('bare_tag', 'app.ask', tag), ('agent_tag', 'app.agent', tag),
             ('bare_levels', 'app.ask', levels), ('agent_levels', 'app.agent', levels),
             ('agent_lora', 'app.agent', 'LoRAとQLoRAの違いは？'),
             ('agent_quiz', 'app.agent', '第2回の内容から確認問題を1問出して')]
    rows = []
    for i, (name, module, question) in enumerate(cases, 1):
        command = [sys.executable, '-m', module]
        if module == 'app.agent':
            command.append('--trace')
        command.append(question)
        print(f'[{i}/{len(cases)}] {name}', flush=True)
        stdout = run(command, env, folder / name)
        rows.append({'name': name, 'question': question, 'command': command, 'stdout': stdout})
        if i < len(cases):
            time.sleep(15)
    tests = run([sys.executable, '-m', 'pytest', '-q'], env, folder / 'pytest')
    verification = run([sys.executable, 'scripts/verify_adk_offline.py'], env, folder / 'offline')
    data = {'model': MODEL, 'started_at_utc': stamp,
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'versions': {k: importlib.metadata.version(k) for k in ('google-genai', 'pydantic-ai-slim', 'google-adk')},
            'cases': rows, 'tests': tests, 'offline': verification}
    (folder / 'exercise.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 第3回 演習の実行ログ', '', f'共通モデル: `{MODEL}`。各条件1回、新規プロセスで実行。', '']
    for row in rows:
        lines.extend([f"## {row['name']}", '', row['question'], '', '````````text', row['stdout'], '````````', ''])
    lines.extend(['## テスト', '', '```text', tests, '```', ''])
    (folder / 'exercise.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'演習完了: {folder.relative_to(ROOT)}', flush=True)


if __name__ == '__main__':
    main()
