import sys,json,collections
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'libs'));from PIL import Image
O=Path(__file__).resolve().parent
B=Path(r'E:\jz\JIA\Productions\Production_OBJ (2)\Data');rows=[]
for p in B.rglob('*.obj'):
 stat=dict(obj=str(p),obj_bytes=p.stat().st_size,vertices=0,uv=0,faces=0,mtllib=[],materials=[],bbox=[[float('inf')]*3,[float('-inf')]*3])
 with p.open('r',encoding='utf-8',errors='replace') as f:
  for line in f:
   if line.startswith('v '):
    a=list(map(float,line.split()[1:4]));stat['vertices']+=1
    for k in range(3):stat['bbox'][0][k]=min(stat['bbox'][0][k],a[k]);stat['bbox'][1][k]=max(stat['bbox'][1][k],a[k])
   elif line.startswith('vt '):stat['uv']+=1
   elif line.startswith('f '):stat['faces']+=1
   elif line.startswith('mtllib '):stat['mtllib'].append(line[7:].strip())
   elif line.startswith('usemtl '):stat['materials'].append(line[7:].strip())
 stat['materials']=sorted(set(stat['materials']));stat['textures']=[]
 for mn in stat['mtllib']:
  mtl=p.parent/mn
  with mtl.open('r',encoding='utf-8',errors='replace') as f:
   current=''
   for line in f:
    if line.startswith('newmtl '):current=line[7:].strip()
    if line.startswith('map_Kd '):
     ip=mtl.parent/line[7:].strip();im=Image.open(ip);stat['textures'].append(dict(material=current,path=str(ip),bytes=ip.stat().st_size,width=im.width,height=im.height))
 rows.append(stat);print(json.dumps(stat),flush=True)
(O/'Old_JIA_Texture_Source.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
