"""演習追加ツールのデータ整合性とエージェント接続を確認する。API不要。"""
import json

from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app import tools
from app.agent import agent


def test_quiz_answer_comes_from_requested_lecture():
    result = json.loads(tools.make_quiz(2))
    entries = tools.load_glossary()
    entry = next(t for t in entries if t['lecture'] == 2)
    assert result['lecture'] == 2
    assert result['term'] == entry['term']
    assert result['answer'] == entry['definition']
    assert entry['term'] in result['question']


def test_quiz_invalid_and_missing_lecture():
    for lecture in (0, -1, True, '2'):
        assert '1以上の整数' in tools.make_quiz(lecture)
    assert '用語集にありません' in tools.make_quiz(999)


def test_quiz_is_registered_and_result_returns_to_agent():
    model = TestModel(call_tools=['make_quiz'])
    result = agent.run_sync('第2回の確認問題', model=model)
    parts = [p for m in result.all_messages() for p in m.parts]
    assert any(isinstance(p, ToolCallPart) and p.tool_name == 'make_quiz' for p in parts)
    assert any(isinstance(p, ToolReturnPart) and p.tool_name == 'make_quiz' for p in parts)
    offered = {t.name: t for t in model.last_model_request_parameters.function_tools}
    assert '確認問題' in offered['make_quiz'].description
