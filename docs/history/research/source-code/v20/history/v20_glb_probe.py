import sys,json,struct,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1')]
import numpy as np
O=Path('E:/jz/JIA/Rebuild_V20');GP=O/'05_Export/Complete_Site_V20_LOCAL.glb'
with GP.open('rb') as f:
 f.read(12);n,typ=struct.unpack('<II',f.read(8));g=json.loads(f.read(n));n,typ=struct.unpack('<II',f.read(8));binary=f.read(n)
I=json.loads((O/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'));idx={r['name']:r for r in I};nodes={n.get('name'):j for j,n in enumerate(g['nodes'])};parents={c:j for j,n in enumerate(g['nodes']) for c in n.get('children',[])}
tree=ast.parse((W/'v20_package.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['quatmat','matworld','acc']],type_ignores=[]),'<gltf_geometry>','exec'))
DM=json.loads((O/'02_Data/Door_Manifest_V20.json').read_text(encoding='utf8'));errs=[]
for r in DM['doors']:
 n=r['name'];j=nodes[n+'_Geometry'];m=matworld(j);vv=np.vstack([acc(p['attributes']['POSITION']) for p in g['meshes'][g['nodes'][j]['mesh']]['primitives']]);vv=np.c_[vv,np.ones(len(vv))]@m.T;local=vv[:,[0,2,1]];local[:,1]*=-1;v=np.load(O/'02_Data'/idx[n]['file'])['vertices'];err=float(np.max(abs(np.array([local.min(0),local.max(0)])-np.array([v.min(0),v.max(0)]))));errs.append([n,err]);assert err<1e-5,(n,err)
print('GLB',len(g['meshes']),len(g.get('animations',[])),len(g['cameras']),len(g['images']),'DOOR PARITY MAX',max(r[1] for r in errs))
