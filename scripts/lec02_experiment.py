"""AIE02 advanced: deterministic preparation, retrieval baseline, GPU LoRA run."""
import json, time, re, hashlib, unicodedata
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'lectures/02/data'
OUT = ROOT / 'lectures/02/reproduction_results'
OUT.mkdir(parents=True, exist_ok=True)
TERMS = json.loads((DATA/'glossary_snapshot.json').read_text())['terms']
SYSTEM = 'あなたはAIE講座用語集の回答係です。学習した用語集に基づいて答えてください。必ずJSON 1行で {"answer": 文字列, "needs_review": 真偽値} を返してください。用語集に収録されていない用語は、一般知識で説明せず、answerを「用語集に記載がないため確認が必要です。」、needs_reviewをtrueにしてください。'
UNKNOWN = '用語集に記載がないため確認が必要です。'
# Each inner list is an OR group; all groups are required. No gold is sent to model/retriever.
SPECS = [
 ('lora', '元の重みを固定し、更新分を二つの小さな行列の積で表す追加学習手法を説明して。', [['固定'],['行列'],['学習','更新']]),
 ('qlora', '基盤モデルを4ビットに圧縮し、小さな追加行列だけ学習する手法を説明して。', [['量子化','4ビット','4bit'],['LoRA']]),
 ('sft', '質問と模範回答のペアを教師データにしてモデルを追加学習する方法を説明して。', [['入力','質問'],['出力','回答'],['学習']]),
 ('context-window', 'モデルが一度に扱える入力と出力の合計量の上限を表す概念を説明して。', [['入力'],['出力'],['上限','合計']]),
 ('hallucination', '生成モデルが事実と異なる内容や存在しない情報をもっともらしく出力する現象を説明して。', [['事実','存在しない'],['生成','情報']]),
 ('rate-limit', '429エラーが出るレート制限は何を制限している？', [['時間'],['リクエスト','トークン'],['上限']]),
 ('overfitting', 'overfittingが起きると、学習に使っていない入力の性能はどうなる？', [['学習データ'],['未知','検証'],['落ち','低下']]),
 ('mcp', 'Model Context Protocolは、AIと外部ツールの接続でどんな役割を持つ？', [['ツール','データソース'],['標準','プロトコル','共通']]),
 ('human-in-the-loop', 'HITLでは、人は処理のどのような位置で確認するの？', [['人'],['途中','前'],['確認','承認']]),
 ('default-model', 'AIE2026のデフォルトモデル名と、切替に使う環境変数を教えて。', [['gemini-3.5-flash-lite'],['AIE_MODEL']]),
]
def dump(path, obj):
 path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
def jsonl(path, rows):
 path.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows), encoding='utf-8')
def norm(s):
 return re.sub(r'\s+', '', unicodedata.normalize('NFKC',s).casefold())
def prepare():
 raw=[json.loads(l) for l in (DATA/'glossary_sft.jsonl').read_text().splitlines()]
 train=[]
 for r in raw:
  q,a=r['messages']
  train.append({'messages':[{'role':'system','content':SYSTEM},q,{'role':'assistant','content':json.dumps({'answer':a['content'],'needs_review':False},ensure_ascii=False)}]})
 valid=[{'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':f"講座で使う「{t['term']}」の意味を教えて。"},{'role':'assistant','content':json.dumps({'answer':t['definition'],'needs_review':False},ensure_ascii=False)}]} for t in TERMS]
 byid={t['id']:t for t in TERMS}; tests=[]
 for id,q,groups in SPECS:
  t=byid[id]
  for category,question in [('known',f"{t['term']}の定義は？"),('paraphrase',q)]:
   tests.append({'id':f'{category}-{id}','category':category,'question':question,'term_id':id,'gold':{'needs_review':False,'answer':t['definition'],'groups':groups}})
 for i,word in enumerate(['RAG','DPO','PPO','GRPO','蒸留','RoPE','FlashAttention','MoE','ACTN3 R577X多型','デジタルアスリート']):
  assert all(norm(word)!=norm(n) for t in TERMS for n in [t['term'],t['id']]+t['aliases'])
  tests.append({'id':f'unknown-{i}','category':'unknown','question':f'{word}とは何ですか？','term_id':None,'gold':{'needs_review':True,'answer':UNKNOWN,'groups':[['確認']]}})
 sets=[{r['messages'][-2]['content'] for r in rows} for rows in [train,valid]]
 assert not sets[0]&sets[1]
 assert not (sets[0]|sets[1])&{r['question'] for r in tests}
 assert len(tests)==len({t['question'] for t in tests})==30
 assert len(raw)==len(train)==116 and len(valid)==58
 jsonl(DATA/'train_messages.jsonl',train);jsonl(DATA/'valid_messages.jsonl',valid);jsonl(DATA/'eval.jsonl',tests)
 dump(OUT/'preparation.json',{'terms':len(TERMS),'train':len(train),'valid':len(valid),'test':len(tests),'source_commit':'fae899a409e2c99feee9d44a3789f936f5fc64ee','glossary_sha256':hashlib.sha256((DATA/'glossary_snapshot.json').read_bytes()).hexdigest(),'training_executed':False})
 return train,valid,tests

def retrieval(question):
 # Entire question in, deterministic name/alias matching. No term_id or gold access.
 q=norm(question)
 hits=[]
 for t in TERMS:
  matched=[norm(n) for n in [t['term'],t['id']]+t['aliases'] if len(norm(n))>=3 and norm(n) in q]
  if matched:hits.append((max(map(len,matched)),t))
 if not hits:return json.dumps({'answer':UNKNOWN,'needs_review':True},ensure_ascii=False)
 hits.sort(key=lambda h:(-h[0],h[1]['id']))
 return json.dumps({'answer':hits[0][1]['definition'],'needs_review':False},ensure_ascii=False)
def score(raw,gold):
 try:o=json.loads(raw)
 except (ValueError,TypeError):o=None
 fmt=isinstance(o,dict) and set(o)=={'answer','needs_review'} and type(o['answer']) is str and type(o['needs_review']) is bool
 # Strict booleans prevent 0/1 or string labels receiving credit.
 content=isinstance(o,dict) and type(o.get('needs_review')) is bool and o['needs_review'] is gold['needs_review'] and type(o.get('answer')) is str and all(any(norm(w) in norm(o['answer']) for w in group) for group in gold['groups'])
 return {'format_ok':fmt,'content_ok':content,'both_ok':fmt and content}
def evaluate(tests,fn,label):
 start=time.perf_counter();rows=[]
 for t in tests:
  raw=fn(t['question']); rows.append({**t,'raw':raw,**score(raw,t['gold'])})
 def summary(rs):
  return {'n':len(rs),**{k+'_rate':sum(r[k+'_ok'] for r in rs)/len(rs) for k in ['format','content','both']}}
 result={'label':label,**summary(rows),'by_category':{c:summary([r for r in rows if r['category']==c]) for c in ['known','paraphrase','unknown']},'seconds':time.perf_counter()-start,'rows':rows}
 dump(OUT/f'eval_{label}.json',result)
 return result

def run():
 import torch, transformers, peft, trl, datasets, accelerate
 from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
 from peft import LoraConfig
 from trl import SFTTrainer,SFTConfig
 from datasets import Dataset
 assert torch.cuda.is_available(),'GPUが必要です。ColabでT4 GPUを選んでください。'
 train,valid,tests=prepare()
 cfg={'base_model':'Qwen/Qwen3.5-0.8B','revision':'2fc06364715b967f1860aea9cf38778875588b17','seed':42,'num_train_epochs':20,'lr':2e-4,'lora_r':16,'lora_alpha':32,'max_seq_len':512,'max_new_tokens':256,'warmup_steps':6}
 set_seed(cfg['seed'])
 tok=AutoTokenizer.from_pretrained(cfg['base_model'],revision=cfg['revision'])
 if tok.pad_token is None:tok.pad_token=tok.eos_token
 model=AutoModelForCausalLM.from_pretrained(cfg['base_model'],revision=cfg['revision'],dtype=torch.float32).to('cuda').eval()
 # Avoid silent truncation of long glossary definitions / outputs.
 lengths=[len(tok.apply_chat_template(r['messages'],tokenize=True,return_dict=False,enable_thinking=False)) for r in train+valid]
 dump(OUT/'lengths.json',{'max':max(lengths),'over_512':sum(n>512 for n in lengths)})
 assert max(lengths)<=cfg['max_seq_len'],'512トークン超。切り詰めず、設定と報告を修正してください。'
 def generate(m,q):
  prompt=tok.apply_chat_template([{'role':'system','content':SYSTEM},{'role':'user','content':q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
  inputs=tok(prompt,return_tensors='pt').to(m.device)
  with torch.inference_mode():out=m.generate(**inputs,max_new_tokens=cfg['max_new_tokens'],do_sample=False,pad_token_id=tok.pad_token_id)
  return tok.decode(out[0][inputs['input_ids'].shape[1]:],skip_special_tokens=True).strip()
 before=evaluate(tests,lambda q:generate(model,q),'before')
 baseline=evaluate(tests,retrieval,'retrieval')
 model.config.use_cache=False
 lora=LoraConfig(r=cfg['lora_r'],lora_alpha=cfg['lora_alpha'],lora_dropout=.05,bias='none',task_type='CAUSAL_LM',target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'])
 args=SFTConfig(output_dir=str(OUT/'ckpt'),num_train_epochs=cfg['num_train_epochs'],per_device_train_batch_size=4,gradient_accumulation_steps=2,learning_rate=cfg['lr'],lr_scheduler_type='cosine',warmup_steps=cfg['warmup_steps'],logging_steps=10,save_steps=50,save_total_limit=2,fp16=False,max_length=cfg['max_seq_len'],packing=False,report_to='none',seed=42)
 trainer=SFTTrainer(model=model,args=args,train_dataset=Dataset.from_list(train),eval_dataset=Dataset.from_list(valid),peft_config=lora,processing_class=tok)
 trainer.model.print_trainable_parameters();start=time.perf_counter();training=trainer.train();seconds=time.perf_counter()-start
 tuned=trainer.model;tuned.save_pretrained(OUT/'adapter');tok.save_pretrained(OUT/'adapter')
 tuned.config.use_cache=True;tuned.eval()
 after=evaluate(tests,lambda q:generate(tuned,q),'after')
 regressed=[b['id'] for b,a in zip(before['rows'],after['rows']) if b['both_ok'] and not a['both_ok']]
 result={'config':cfg,'versions':{m.__name__:m.__version__ for m in [torch,transformers,peft,trl,datasets,accelerate]},'gpu':torch.cuda.get_device_name(0),'training_executed':True,'execution_agent':'AI-generated notebook executed by operator','training_seconds':seconds,'training_loss_mean':training.training_loss,'last_logged_loss':next((x['loss'] for x in reversed(trainer.state.log_history) if 'loss'in x),None),'steps':trainer.state.global_step,'train_log':trainer.state.log_history,'regressed':regressed,'summaries':{r['label']:{k:v for k,v in r.items() if k!='rows'} for r in [before,after,baseline]}}
 dump(OUT/'result.json',result)
 report=['# 発展課題・実測結果','', '|条件|形式遵守率|内容正解率|両方|','|---|---:|---:|---:|']
 for r in [before,after,baseline]:report.append(f"|{r['label']}|{r['format_rate']:.1%}|{r['content_rate']:.1%}|{r['both_rate']:.1%}|")
 report+=['',f'学習時間: {seconds:.1f} 秒 / 最終ログloss: {result["last_logged_loss"]} / {result["steps"]} steps',f'退行した質問ID: {regressed}','', '以下の考察は、実測値と全質問の出力を読んで確認すること。','']
 for label in ['before','after','retrieval']:
  for category,s in result['summaries'][label]['by_category'].items():report.append(f'- {label}/{category}: n={s["n"]}, content_rate={s["content_rate"]:.1%}')
 (OUT/'measured_report.md').write_text('\n'.join(report),encoding='utf-8')
 answer=OUT/'answer_reproduction.md'
 if not answer.exists():answer.write_text('# 再実行結果\n',encoding='utf-8')
 text=answer.read_text();marker='<!-- MEASURED -->'
 text=text.split(marker)[0]+marker+'\n\n'+'\n'.join(report)+'\n'
 answer.write_text(text,encoding='utf-8')
 print(json.dumps(result['summaries'],ensure_ascii=False,indent=2))
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--train',action='store_true');a=p.parse_args()
 if a.train:run()
 else:
  _,_,tests=prepare();r=evaluate(tests,retrieval,'retrieval');print({k:v for k,v in r.items() if k!='rows'})
