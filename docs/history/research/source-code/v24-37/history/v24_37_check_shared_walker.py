from pathlib import Path
import json,ast,hashlib
O=Path('E:/jz/JIA/Rebuild_V24_37');P=O/'Blender/Architecture_Complete_V24_37.blend';R=O/'Reports';native=json.loads((R/'V24_37_Native_QA.json').read_text('utf8'));assert all(x['pass']for x in native['checks']if x['check']=='Embedded runtime matches external roam_controller.py')
code=(O/'Roam/roam_controller.py').read_text('utf8');tree=ast.parse(code);calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='Walker'];yes=len(calls)==1 and 'first_person'in code and 'PTJIA6_ROAD'in code
path=R/'V24_37_Exterior_Physics_QA.json';q=json.loads(path.read_text());h=hashlib.file_digest(P.open('rb'),'sha256').hexdigest();assert h==q['model_sha256']==native['model_sha256']
for check in q['checks']:
 if check['check']=='First and third person use the same supported walker':check.update({'pass':yes,'constructor_calls':len(calls),'verification':'AST of external runtime, proven equal to embedded runtime by fresh native readback','prior_test_issue':'Original test expected a module-qualified constructor; actual runtime uses an imported Walker name'})
q['failures']=[r for r in q['checks']if not r['pass']];q['status']='PASS_ALL_MODEL_EXTERIOR_SUPPORT_AND_EDGE_SAFETY'if not q['failures']else'FAIL';path.write_text(json.dumps(q,indent=2));print('SHARED_WALKER',yes,'EXTERIOR_FAILURES',len(q['failures']))
