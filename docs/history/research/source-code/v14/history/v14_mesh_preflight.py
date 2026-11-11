import sys,json,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V13/08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));ex.SCENE=S
tree=ast.parse((W/'v14_assemble.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='mesh'],type_ignores=[]),'mesh','exec'))
Q=json.loads((W/'v14/Building_Mutation.json').read_text(encoding='utf8'));fail=[]
for e in Q['replace']+Q['add']:
 for i,p in enumerate(e['parts']):
  if p['geometry']['type'] in ['box','prism_holes','cylinder']:continue
  try:mesh(p['geometry'])
  except AssertionError as err:fail.append([e['name'],i,str(err)]);print('FAIL',fail[-1],flush=True)
print('TOTAL',len(fail),flush=True)
