"""Read a non-overlapping OSGB hierarchy frontier through the installed OSG tool.
Embedded JPEGs are byte-extracted, avoiding the converter's JPEG recompression.
"""
from pathlib import Path
import sys,json,re,subprocess,hashlib,io,concurrent.futures,time
import numpy as np
from PIL import Image
W=Path(__file__).parent;D=W/'v24_34';SRC=Path('D:/AJAVIS01/ContextCapture/CASES/MB501/Productions/MB7/Data/Model');EXE=Path('D:/AJAVIS01/ContextCapture/PLUGINS/AutoCAD2023/PLUGINS/CASS/CASS-RUNING/CASS11 For AutoCAD 2023/bin/osgconv.exe');level=int(sys.argv[1]) if len(sys.argv)>1 else 21;names=json.loads((D/f'Frontier_{level}.json').read_text('utf8'));O=D/'Decode'/f'L{level}';O.mkdir(exist_ok=True);start=time.perf_counter()
def decode(n):
 p=SRC/n;stem=p.stem;obj=O/(stem+'.obj');dest=O/(stem+'.npz');meta=O/(stem+'.json');source=p.read_bytes();h=hashlib.sha256(source).hexdigest()
 if dest.exists() and meta.exists():
  r=json.loads(meta.read_text('utf8'))
  if r.get('source_sha256')==h:return r
 if not obj.exists():
  r=subprocess.run([str(EXE),'-O','noRotation precision=10',str(p),str(obj)],cwd=str(O),capture_output=True,text=True,errors='replace',timeout=90)
  if r.returncode or not obj.exists():raise RuntimeError((n,r.returncode,r.stdout[-500:],r.stderr[-500:]))
 # Serializer stores each image filename followed by its encoded file bytes.
 image_names=list(dict.fromkeys(x.decode('ascii') for x in re.findall(rb'[A-Za-z0-9_]+\.jpe?g',source)));jpgs=[];pos=0
 while True:
  a=source.find(b'\xff\xd8\xff',pos)
  if a<0:break
  b=source.find(b'\xff\xd9',a+3)
  if b<0:break
  encoded=source[a:b+2]
  try:
   im=Image.open(io.BytesIO(encoded));im.verify();jpgs.append(encoded)
  except Exception:pass
  pos=b+2
 if len(jpgs)!=len(image_names):raise RuntimeError(('Image count mismatch',n,image_names,len(jpgs)))
 for fn,b in zip(image_names,jpgs):(O/fn).write_bytes(b)
 materials={};current=None
 for line in obj.with_suffix('.mtl').read_text('utf8').splitlines():
  t=line.split()
  if not t:continue
  if t[0]=='newmtl':current=t[1];materials[current]=None
  elif t[0]=='map_Kd':materials[current]=Path(t[-1]).name
 textures=list(dict.fromkeys(materials.values()));assert None not in textures,(n,materials)
 v=[];vt=[];f=[];fu=[];mi=[];mat=0
 for line in obj.open(encoding='utf8'):
  if line.startswith('v '):v.append([float(x)for x in line.split()[1:4]])
  elif line.startswith('vt '):vt.append([float(x)for x in line.split()[1:3]])
  elif line.startswith('usemtl '):mat=textures.index(materials[line.split()[1]])
  elif line.startswith('f '):
   ids=[q.split('/') for q in line.split()[1:]]
   for k in range(1,len(ids)-1):
    ff=[ids[0],ids[k],ids[k+1]];f.append([int(t[0])-1 if int(t[0])>0 else len(v)+int(t[0])for t in ff]);fu.append([int(t[1])-1 if int(t[1])>0 else len(vt)+int(t[1])for t in ff]);mi.append(mat)
 v=np.array(v,dtype=np.float64).reshape(-1,3);f=np.array(f,dtype=np.int32).reshape(-1,3);uv=np.array(vt,dtype=np.float64).reshape(-1,2)[np.array(fu,dtype=np.int32).reshape(-1,3)];mi=np.array(mi,dtype=np.int32);np.savez_compressed(dest,v=v,f=f,uv=uv,mi=mi)
 row={'node':n,'file':str(dest.relative_to(D)),'source_sha256':h,'vertices':len(v),'triangles':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()] if len(v) else None,'textures':[{'file':str((O/t).relative_to(D)),'sha256':hashlib.sha256((O/t).read_bytes()).hexdigest(),'size':list(Image.open(O/t).size)}for t in textures]};meta.write_text(json.dumps(row),encoding='utf8');return row
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8)as pool:
 for i,r in enumerate(pool.map(decode,names)):
  rows.append(r)
  if i%20==0:print('DECODE',level,i+1,'/',len(names),flush=True)
(D/f'Decoded_L{level}_Index.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print('DECODE_DONE',level,len(rows),'triangles',sum(r['triangles']for r in rows),'seconds',time.perf_counter()-start,flush=True)
