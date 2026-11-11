from pathlib import Path
import sys,json,struct,hashlib,ctypes,concurrent.futures,time
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'ctmlibs'),str(W/'libs')]
import numpy as np
from PIL import Image
from openctm.binding import _ctm_lib as lib
D=W/'v24_36';level=int(sys.argv[1])if len(sys.argv)>1 else 99;names=json.loads((D/f'Frontier_{level}.json').read_text());O=D/'Decode'/f'L{level}';O.mkdir(parents=True,exist_ok=True);SRC=Path('D:/AJAVIS01/ContextCapture/CASES/新建工程/Productions/Production_PTJIA6/Scene/Data/Model');start=time.perf_counter()
lib.ctmNewContext.argtypes=[ctypes.c_uint32];lib.ctmNewContext.restype=ctypes.c_void_p;lib.ctmFreeContext.argtypes=[ctypes.c_void_p];lib.ctmLoad.argtypes=[ctypes.c_void_p,ctypes.c_char_p];lib.ctmGetInteger.argtypes=[ctypes.c_void_p,ctypes.c_uint32];lib.ctmGetInteger.restype=ctypes.c_uint32;lib.ctmGetFloatArray.argtypes=[ctypes.c_void_p,ctypes.c_uint32];lib.ctmGetFloatArray.restype=ctypes.POINTER(ctypes.c_float);lib.ctmGetIntegerArray.argtypes=[ctypes.c_void_p,ctypes.c_uint32];lib.ctmGetIntegerArray.restype=ctypes.POINTER(ctypes.c_uint32);lib.ctmGetError.argtypes=[ctypes.c_void_p];lib.ctmGetError.restype=ctypes.c_uint32
def readctm(p):
 ctx=lib.ctmNewContext(0x0101);lib.ctmLoad(ctx,str(p).encode('ascii'))
 try:
  err=lib.ctmGetError(ctx)
  if err:raise RuntimeError((p.name,err))
  n=lib.ctmGetInteger(ctx,0x0301);nf=lib.ctmGetInteger(ctx,0x0302);v=np.ctypeslib.as_array(lib.ctmGetFloatArray(ctx,0x0602),shape=(n*3,)).copy().reshape(-1,3).astype(float);f=np.ctypeslib.as_array(lib.ctmGetIntegerArray(ctx,0x0601),shape=(nf*3,)).copy().reshape(-1,3).astype(np.int32);ptr=lib.ctmGetFloatArray(ctx,0x0700);assert ptr,(p,'No source UV');uv=np.ctypeslib.as_array(ptr,shape=(n*2,)).copy().reshape(-1,2).astype(float);return v,f,uv
 finally:lib.ctmFreeContext(ctx)
def decode(name):
 source=(SRC/name).read_bytes();h=hashlib.sha256(source).hexdigest();n=struct.unpack('<I',source[5:9])[0];header=json.loads(source[9:9+n]);offset=9+n;buffers={};rows=[]
 for r in header.get('resources',[]):
  if'size'not in r:continue
  b=source[offset:offset+r['size']];offset+=r['size'];p=O/(Path(name).stem+'_'+r['id']+'.'+r['format']);buffers[r['id']]=p
  if not p.exists()or hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(b).digest():p.write_bytes(b)
 assert offset==len(source),(name,offset,len(source))
 for r in header.get('resources',[]):
  if r['type']!='geometryBuffer':continue
  p=buffers[r['id']];out=p.with_suffix('.npz');meta=p.with_suffix('.json')
  if out.exists()and meta.exists():
   row=json.loads(meta.read_text())
   if row['source_sha256']==h:rows.append(row);continue
  v,f,uv=readctm(p);assert np.isfinite(v).all()and np.isfinite(uv).all();tex=buffers[r['texture']];tx={'file':str(tex.relative_to(D)),'sha256':hashlib.sha256(tex.read_bytes()).hexdigest(),'size':list(Image.open(tex).size)};np.savez_compressed(out,v=v,f=f,uv=uv[f],mi=np.zeros(len(f),np.int32));row={'node':name,'part':r['id'],'file':str(out.relative_to(D)),'source_sha256':h,'vertices':len(v),'triangles':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'textures':[tx]};meta.write_text(json.dumps(row),encoding='utf8');rows.append(row)
 return rows
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
 for i,rr in enumerate(pool.map(decode,names)):
  rows.extend(rr)
  if i%100==0:print('DECODE',level,i+1,'/',len(names),flush=True)
(D/f'Decoded_L{level}_Index.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print('PTJIA6_DECODE_DONE',level,'meshes',len(rows),'triangles',sum(r['triangles']for r in rows),'seconds',time.perf_counter()-start,flush=True)
