import sys,json,time
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
from nearest_photo_projection import PhotoProjector
import numpy as np
tic=time.time();p=PhotoProjector.from_reference_3dm(Path(r'E:\jz\JIA\Rebuild_V5\04_ContextCapture\Production_1QK_Local_REFERENCE.3dm'))
idx=np.linspace(0,len(p.triangles)-1,512,dtype=int);pts=p.triangles[idx].mean(axis=1);rr=p.query(pts,p.normals[idx],max_distance=.0001,min_normal_dot=.9,k=32)
res=dict(source_triangles=len(p.triangles),source_textures=p.materials,test_points=len(idx),matched=int(rr['matched'].sum()),max_distance=float(np.max(rr['distance'])),max_uv_difference=float(np.nanmax(np.abs(rr['uv']-p.uv[idx].mean(axis=1)))),seconds=time.time()-tic,passed=bool(rr['matched'].all() and np.nanmax(np.abs(rr['uv']-p.uv[idx].mean(axis=1)))<1e-8))
print(json.dumps(res),flush=True);Path(__file__).with_name('Projection_Helper_QA.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
del p
import gc;gc.collect()
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V5\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'));M=np.linalg.inv(np.asarray(S['coordinate']['local_to_survey'],float))
p=PhotoProjector.from_objs(list(Path(r'E:\jz\JIA\Productions\Production_OBJ (2)\Data').rglob('*.obj')),coordinate_transform=M)
idx=np.linspace(0,len(p.triangles)-1,512,dtype=int);pts=p.triangles[idx].mean(axis=1);rr=p.query(pts,p.normals[idx],max_distance=.0001,min_normal_dot=.9,k=32)
res2=dict(source_triangles=len(p.triangles),source_textures=p.materials,test_points=len(idx),matched=int(rr['matched'].sum()),max_distance=float(np.max(rr['distance'])),max_uv_difference=float(np.nanmax(np.abs(rr['uv']-p.uv[idx].mean(axis=1)))),coordinate_transform=M.tolist(),passed=bool(rr['matched'].all() and np.nanmax(np.abs(rr['uv']-p.uv[idx].mean(axis=1)))<1e-8))
print(json.dumps(res2),flush=True);Path(__file__).with_name('Projection_OBJ_Helper_QA.json').write_text(json.dumps(res2,indent=2),encoding='utf-8')
