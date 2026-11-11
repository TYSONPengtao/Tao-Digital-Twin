import sys,json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','libs']]
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));M=json.loads((O/'02_Data/Materials.json').read_text(encoding='utf-8'))
src=Path(r'D:\DJI\0002\DCIM\101MEDIA\DJI_0429.JPG');dest=O/'03_Textures/Patch/DJI_0002_0429_GABLE_ORIGINAL.JPG';shutil.copy2(src,dest)
M['DJI_GABLE_0429']={'color':[255,255,255],'roughness':.85,'texture':str(dest),'source_texture':str(src),'role':'Original unaltered DJI photo, manual three-control-point affine front gable UV; visual alignment, not calibrated camera projection'}
r=next(r for r in I if r['name']=='CANOPY_FRONT_CLOSED_GABLE');d=np.load(O/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];uv=d['uv'].copy();mid=d['material_ids'].copy();tri=v[f];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
if 'M_Wall_Exterior' not in r['materials']:r['materials'].append('M_Wall_Exterior')
if 'DJI_GABLE_0429' not in r['materials']:r['materials'].append('DJI_GABLE_0429')
mid[:]=r['materials'].index('M_Wall_Exterior')
# Pixel controls from inspected original 4000x2250 photograph. Interior blank
# gable face, exclude the carved roof fascia. Original pixels are not edited.
model=np.array([[3.0,7.37,1],[6.5,8.297,1],[10.0,7.37,1]])
pixels=np.array([[615,1818],[2127,1396],[3715,1778]],float)
target=np.column_stack((pixels[:,0]/4000,1-pixels[:,1]/2250));coeff=np.linalg.solve(model,target)
sel=np.flatnonzero((np.max(np.abs(tri[:,:,1]+.218),axis=1)<1e-6)&(n[:,1]<-.9))
for k in sel:
 q=np.column_stack((tri[k,:,0],tri[k,:,2],np.ones(3)));uv[f[k]]=q@coeff;mid[k]=r['materials'].index('DJI_GABLE_0429')
np.savez_compressed(O/'02_Data'/r['file'],vertices=v,faces=f,uv=uv,material_ids=mid)
r['photo_triangles']=len(sel);r['photo_mapping']='DJI 0002 0429, manually inspected three control points on front gable; back faces retain clean wall material'
(O/'02_Data/Patch_Index.json').write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf-8');(O/'02_Data/Materials.json').write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf-8')
report={'source':str(src),'texture':str(dest),'source_copy_sha256_equal':hashlib.sha256(src.read_bytes()).hexdigest()==hashlib.sha256(dest.read_bytes()).hexdigest(),'source_image_pixels_changed':False,'front_faces_mapped':len(sel),'controls_model_xz':model[:,:2].tolist(),'controls_original_pixels':pixels.tolist(),'metric_status':'VISUAL_ALIGNMENT_NOT_CALIBRATED_PHOTOGRAMMETRY'}
(O/'06_Report/Gable_DJI_Texture_QA.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(report,flush=True)
