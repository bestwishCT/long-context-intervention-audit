"""Fresh request; writes new evidence and never edits saved responses."""
import argparse,subprocess,os,json,uuid,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--bohr',required=True);p.add_argument('--condition',choices=['baseline','workflow'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
R=Path(__file__).resolve().parent
if a.out.exists():raise SystemExit('Use new out directory')
a.out.mkdir(parents=True)
prompt='独立记录号 '+str(uuid.uuid4())+'（不含任务语义）\n'+((R/'workflow.txt').read_text(encoding='utf8')+'\n' if a.condition=='workflow' else '')+(R/'task.txt').read_text(encoding='utf8')+'\n'+(R/'numbered.txt').read_text(encoding='utf8')
(a.out/'request.txt').write_text(prompt,encoding='utf8');env=os.environ.copy()
for k in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']:env.pop(k,None)
cmd=[a.bohr,'chat',prompt,'--model','gpt-5-mini','--payment-source','photon','--output','json'];started=time.monotonic()
pre=subprocess.run(cmd+['--dry-run'],env=env,capture_output=True,encoding='utf8',timeout=20);planned=json.loads(pre.stdout)
assert planned['data']['operations'][0]['body']['message']==prompt
(a.out/'preflight.json').write_text(json.dumps(planned,ensure_ascii=False,indent=2),encoding='utf8')
r=subprocess.run(cmd,env=env,capture_output=True,encoding='utf8',timeout=180)
(a.out/'stderr.txt').write_text(r.stderr or '(empty)',encoding='utf8')
payload=json.loads(r.stdout);bill=payload.get('notice',{}).get('billing',{})
if 'balance' in bill:bill['balance']={'redacted':'private account balance'}
(a.out/'response.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
data=payload['data'];(a.out/'output.json').write_text(data['choices'][0]['message']['content'],encoding='utf8')
(a.out/'metadata.json').write_text(json.dumps({'seconds':round(time.monotonic()-started,3),'model':data['model'],'usage':data['usage'],'completion_id':data['id'],'cost':None},ensure_ascii=False,indent=2),encoding='utf8')
print('Saved raw new response',a.out)
