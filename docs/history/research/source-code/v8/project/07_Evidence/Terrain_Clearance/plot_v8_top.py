import sys,json,math
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
from PIL import Image,ImageDraw
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');out=W/'v8_terrain_clear';B=json.loads((O/'02_Data/Base_Index.json').read_text());I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));M=json.loads((O/'02_Data/Materials.json').read_text(encoding='utf-8'));C=json.loads((O/'02_Data/Coordinate.json').read_text());R=np.array(C['local_to_survey'])[:3,:3];org=np.array(C['origin']);cache={}
def texture(p):
 if p not in cache:cache[p]=np.array(Image.open(p).convert('RGB'))
 return cache[p]
man=json.loads((out/'Merge_Manifest.json').read_text(encoding='utf-8'));M.update(man['material_additions']);delete=set(man['delete_names']);replace={r['name']:r for r in man['replacement_patch_rows']};I=[replace.get(r['name'],r) for r in I if r['name'] not in delete]+man['new_patch_rows'];tr=[];co=[]
for b in B:
 file=('Base_'+str(b['index'])+'.npz');d=np.load(out/'data'/file if (out/'data'/file).exists() else O/'02_Data'/file);v=(d['vertices']-org)@R;f=d['faces'];f=np.concatenate([f[:,:3],f[f[:,2]!=f[:,3]][:,[0,2,3]]]);t=v[f];uv=d['uv'][f].mean(1);ar=np.abs(np.cross(t[:,1,:2]-t[:,0,:2],t[:,2,:2]-t[:,0,:2]));take=ar>.0005;t=t[take];uv=uv[take];tex=texture(b['texture']);u=(uv[:,0]*(tex.shape[1]-1)).astype(int).clip(0,tex.shape[1]-1);vv=((1-uv[:,1])*(tex.shape[0]-1)).astype(int).clip(0,tex.shape[0]-1);tr.append(t);co.append(tex[vv,u]);print(b['name'],len(t),flush=True)
for row in I:
 if 'TILE_ROWS' in row['name'] or row['name']=='ANNEX_EXPOSED_GREY_BRICK_UNITS':continue
 d=np.load(out/'data'/row['file'] if (out/'data'/row['file']).exists() else O/'02_Data'/row['file']);t=d['vertices'][d['faces']];uv=d['uv'][d['faces']].mean(1);ar=np.abs(np.cross(t[:,1,:2]-t[:,0,:2],t[:,2,:2]-t[:,0,:2]));take=ar>.0005;t=t[take];uv=uv[take];mid=d['material_ids'][take];cols=np.zeros((len(t),3),np.uint8)
 for mi,m in enumerate(row['materials']):
  idx=mid==mi;mat=M[m]
  if mat.get('texture'):
   tex=texture(mat['texture']);u=(uv[idx,0]*(tex.shape[1]-1)).astype(int).clip(0,tex.shape[1]-1);vv=((1-uv[idx,1])*(tex.shape[0]-1)).astype(int).clip(0,tex.shape[0]-1);cols[idx]=tex[vv,u]
  else:cols[idx]=mat['color']
 tr.append(t);co.append(cols)
tr=np.concatenate(tr);co=np.concatenate(co);sort=np.argsort(tr[:,:,2].mean(1));im=Image.new('RGB',(1534,1180),(245,245,245));dr=ImageDraw.Draw(im)
# Local plan mapping approximate screenshot axes; original scan and retained site landmarks used for alignment.
A=np.array([[25.05,-.20],[.20,-25.05]]);o=np.array([774.,600.]);xy=tr[:,:,:2]@A.T+o
for k in sort:
 if xy[k,:,0].max()<0 or xy[k,:,0].min()>1534 or xy[k,:,1].max()<0 or xy[k,:,1].min()>1180:continue
 dr.polygon([tuple(x) for x in xy[k]],fill=tuple(co[k]))
im.save(out/'V8_West_Terrain_Only_Plan.png')
(out/'Plan_Map_Initial.json').write_text(json.dumps({'A':A.tolist(),'offset':o.tolist()},indent=2))
print('saved',len(tr),flush=True)
