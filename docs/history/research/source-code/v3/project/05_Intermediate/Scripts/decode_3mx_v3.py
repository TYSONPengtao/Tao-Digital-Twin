import sys,json,struct,collections,shutil,ctypes
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'ctmlibs'),str(W/'libs')]
import numpy as np
from openctm import load_ctm
from openctm.binding import _ctm_lib
_ctm_lib.ctmGetNamedUVMap.argtypes=[ctypes.c_void_p,ctypes.c_char_p];_ctm_lib.ctmGetNamedUVMap.restype=ctypes.c_uint32
def load_with_uv(path):
 # Standard OpenCTM API: preserve source texture coordinates.
 with path.open('rb') as f:r=load_ctm(f)
 lib=_ctm_lib;lib.ctmNewContext.restype=ctypes.c_void_p;lib.ctmNewContext.argtypes=[ctypes.c_uint32];lib.ctmLoad.argtypes=[ctypes.c_void_p,ctypes.c_char_p];lib.ctmFreeContext.argtypes=[ctypes.c_void_p];lib.ctmGetFloatArray.argtypes=[ctypes.c_void_p,ctypes.c_uint32];lib.ctmGetFloatArray.restype=ctypes.POINTER(ctypes.c_float)
 ctx=lib.ctmNewContext(0x0101);lib.ctmLoad(ctx,str(path).encode())
 try:
  uv=lib.ctmGetFloatArray(ctx,0x0700)
  if uv:r['uv']=np.ctypeslib.as_array(uv,shape=(len(r['vertices'])*2,)).copy().reshape(-1,2)
 finally:lib.ctmFreeContext(ctx)
 return r
sources=json.loads((W/'3MX_Roots_V3.json').read_text(encoding='utf-8'));out=W/'decoded_cases_v3';out.mkdir(exist_ok=True)
for row in sources:
 if row['case'] not in ['ui','ZZCLDQ','新建工程']:continue
 root=Path(row['root']);dest=out/(row['case']+'_'+root.stem);dest.mkdir(exist_ok=True);queue=[(root,0)];chosen=[];missing=[]
 while queue:
  p,depth=queue.pop(0)
  if not p.exists():missing.append(str(p));continue
  with p.open('rb') as f:prefix=f.read(9);n=struct.unpack('<I',prefix[5:])[0];h=json.loads(f.read(n));buffers={}
  children=[p.parent/child for node in h['nodes'] for child in node.get('children',[])]
  if children and depth<5:
   queue.extend((child,depth+1) for child in children);continue
  if not h.get('resources'):continue
  with p.open('rb') as f:
   f.seek(9+n)
   for i,res in enumerate(h['resources']):
    if 'size' not in res:continue
    data=f.read(res['size']);fn=p.stem+'_'+res['id']+'.'+res['format'];target=dest/fn;target.write_bytes(data);buffers[res['id']]=target
  for res in h['resources']:
   if res['type']!='geometryBuffer':continue
   ctm=buffers[res['id']];chosen.append({'ctm':str(ctm),'texture':str(buffers.get(res.get('texture'),'')),'bbox':[res.get('bbMin'),res.get('bbMax')]})
 (dest/'index.json').write_text(json.dumps({'source':row,'meshes':chosen,'missing_children':missing},ensure_ascii=False,indent=2),encoding='utf-8')
 print(row['case'],'CTM',len(chosen),'missing',len(missing),flush=True)
 for mesh in chosen:
  ctm_path=Path(mesh['ctm']);ascii_path=W/'ctm_read_temp.ctm';shutil.copyfile(ctm_path,ascii_path)
  result=load_with_uv(ascii_path)
  print({k:v.shape for k,v in result.items()},flush=True)
  np.savez_compressed(Path(mesh['ctm']).with_suffix('.npz'),**result)
 print('decoded',row['case'],flush=True)
