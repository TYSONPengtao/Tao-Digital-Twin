import sys,types,importlib,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'np1'));import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid');D=Path(__file__).resolve().parent
I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));byname={x['name']:x for x in I}
pkg=types.ModuleType('readonly_fbx_patch');pkg.__path__=[r'D:\AJAVIS01\RHINO7.12\PLUGINS\BLENDER\RUNING\5.1\scripts\addons_core\io_scene_fbx'];sys.modules['readonly_fbx_patch']=pkg
parser=importlib.import_module('readonly_fbx_patch.parse_fbx');root,_=parser.parse(str(O/'05_Export/Reality_Hybrid_V6_LOCAL.fbx'))
def child(n,name):return next((x for x in n.elems if x.id==name),None)
def text(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else x
objs=child(root,b'Objects').elems;byid={x.props[0]:x for x in objs};con=child(root,b'Connections').elems;checks=[];unknown=[]
for n in objs:
 if n.id!=b'Geometry':continue
 modelids=[x.props[2] for x in con if x.props[0]==b'OO' and x.props[1]==n.props[0] and x.props[2] in byid and byid[x.props[2]].id==b'Model'];label=None
 for mi in modelids:
  p=child(byid[mi],b'Properties70')
  if p:
   e=next((x for x in p.elems if x.id==b'P' and x.props[0]==b'Element'),None)
   if e:label=text(e.props[-1])
 if not label:continue
 if label not in byname:unknown.append(label);continue
 row=byname[label];npz=np.load(O/'02_Data'/row['file']);uvn=child(n,b'LayerElementUV');direct=np.asarray(child(uvn,b'UV').props[0],float).reshape(-1,2);uvix=np.asarray(child(uvn,b'UVIndex').props[0],int);pi=np.asarray(child(n,b'PolygonVertexIndex').props[0],int);fi=np.where(pi<0,-pi-1,pi);actual=direct[uvix];wanted=npz['uv'][fi];diff=float(np.max(np.abs(actual-wanted)));checks.append(dict(name=label,faces=int(np.sum(pi<0)),expected_faces=row['triangles'],max_uv_difference=diff,passed=bool(diff<2e-6 and np.sum(pi<0)==row['triangles'])))
res=dict(expected_patch_nodes=len(I),checked_patch_nodes=len(checks),unknown_labels=unknown,max_uv_difference=max(x['max_uv_difference'] for x in checks),all_passed=all(x['passed'] for x in checks),passed=len(checks)==len(I) and not unknown and all(x['passed'] for x in checks),checks=checks)
(D/'FBX_Patch_UV_Readback.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in res.items() if k!='checks'}),flush=True)
