"""API不要の検証。結果は偽モデルによる回答比較ではない。"""
import importlib.metadata
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from google.adk.tools import FunctionTool
from pydantic_ai.models.test import TestModel
from adk_agent.glossary_agent.agent import root_agent
from app.agent import INSTRUCTIONS, agent
from app.config import MODEL
from app import tools

print('API不要の静的・関数検証（実モデルの回答比較ではない）')
for name in ('google-adk', 'google-genai', 'pydantic-ai-slim'):
    print(name, importlib.metadata.version(name))
assert root_agent.instruction == INSTRUCTIONS
assert root_agent.tools == [tools.search_glossary, tools.get_lecture_summary]
assert root_agent.model == MODEL
print('指示文字列の一致: PASS')
print('ツール関数オブジェクトの同一性: PASS (2関数)')
print('モデル名の一致: PASS', MODEL)
model = TestModel(call_tools=[])
agent.run_sync('登録情報の確認', model=model)
pydantic = {t.name: t for t in model.last_model_request_parameters.function_tools}
for fn, argument, kind in ((tools.search_glossary, 'query', 'string'),
                           (tools.get_lecture_summary, 'lecture', 'integer')):
    adk = FunctionTool(fn)._get_declaration().model_dump(exclude_none=True)
    pa_schema = pydantic[fn.__name__].parameters_json_schema
    adk_schema = adk['parameters_json_schema']
    assert pa_schema['properties'][argument]['type'] == kind
    assert adk_schema['properties'][argument]['type'] == kind
    assert argument in pa_schema['required'] and argument in adk_schema['required']
    print('両SDKの必須引数・型: PASS', fn.__name__, argument, kind)
for query in ('LoRA', 'QLoRA', 'AIE未登録検証語98765'):
    result = tools.search_glossary(query)
    if query in ('LoRA', 'QLoRA'):
        assert json.loads(result)[0]['term'] == query
    else:
        assert '見つかりませんでした' in result
    print('search_glossary', query, '=>', result)
summary = tools.get_lecture_summary(3)
assert summary and 'エージェント' in summary
print('get_lecture_summary(3): PASS /', summary.splitlines()[0])
print('TestModelは登録情報の確認だけに使用。生成したダミー回答は比較結果に使っていない。')
