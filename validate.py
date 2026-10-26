"""Strict syntax/range validation. Passing never proves semantic support."""
import json,sys
from pathlib import Path
def validate(source_path,answer_path):
 sources={s['id']:s['text'].splitlines() for s in json.loads(Path(source_path).read_text(encoding='utf8'))}
 try:answer=json.loads(Path(answer_path).read_text(encoding='utf8'))
 except json.JSONDecodeError as e:return {'status':'invalid_json','error':str(e),'semantic':'not_evaluated','excerpts':[]}
 errors=[];excerpts=[];rows=answer.get('decisions',[])
 if sorted(x.get('id','') for x in rows)!=['D1','D2','D3','D4']:errors.append('decision_coverage')
 for row in rows:
  if not row.get('answer') or not row.get('limitations') or not row.get('evidence'):errors.append(row.get('id','?')+':missing_field')
  for e in row.get('evidence',[]):
   lines=sources.get(e.get('source_id'));a=e.get('start_line');b=e.get('end_line')
   if lines is None or type(a)!=int or type(b)!=int or not 1<=a<=b<=len(lines):errors.append(row.get('id','?')+':invalid_range');continue
   excerpts.append({'decision':row['id'],**e,'text':'\n'.join(lines[a-1:b])})
 return {'status':'range_errors' if errors else 'ranges_valid','errors':errors,'semantic':'not_evaluated','excerpts':excerpts}
if __name__=='__main__':
 result=validate(*sys.argv[1:3]);print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(result['status']!='ranges_valid')
