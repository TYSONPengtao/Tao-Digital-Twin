"""Photo-map corrugated tile sides from the measured roof envelope.
Normals on modeled small tile sides differ from the scan's large roof faces;
choose one original atlas per triangle rather than treating those as no photo.
"""
import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v6_reality_inventory')]
import numpy as np
from nearest_photo_projection import PhotoProjector
O=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid');I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf-8'));a=math.radians(C['rotation_deg']);c=math.cos(a);s=math.sin(a);T=np.eye(4);T[:3,:3]=[[c,-s,0],[s,c,0],[0,0,1]];T[:3,3]=C['origin']
P=PhotoProjector.from_objs(sorted(Path(r'E:\jz\JIA\Productions\Production_OBJ (2)\Data').rglob('*.obj')),np.linalg.inv(T))
sub={k:PhotoProjector(P.triangles[P.material_ids==k],P.uv[P.material_ids==k],P.material_ids[P.material_ids==k],P.materials) for k in P.materials}
report=[]
for row in I:
 if 'ROOF' not in row['name'] or 'M_Roof' not in row['materials']:continue
 d=np.load(O/'02_Data'/row['file']);v=d['vertices'];f=d['faces'];uv=d['uv'].copy();mid=d['material_ids'].copy();t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-30)
 sel=np.flatnonzero((mid==row['materials'].index('M_Roof'))&(n[:,2]>-.3))
 if not len(sel):continue
 q=P.query(t[sel].mean(axis=1),max_distance=.5,k=32);assigned=0;distances=[]
 for mi,projector in sub.items():
  j=np.flatnonzero(q['matched']&(q['material_id']==mi));ids=sel[j]
  if not len(ids):continue
  r=projector.query(t[ids].reshape(-1,3),max_distance=.5,k=48);quv=r['uv'].reshape(-1,3,2);good=r['matched'].reshape(-1,3).all(axis=1)&(np.ptp(np.nan_to_num(quv,nan=1e20),axis=1).max(axis=1)<.12)
  label='PATCH_PHOTO_'+str(mi)
  if label not in row['materials']:row['materials'].append(label)
  for k in np.flatnonzero(good):
   uv[f[ids[k]]]=quv[k];mid[ids[k]]=row['materials'].index(label)
  assigned+=int(good.sum());distances.extend(r['distance'].reshape(-1,3)[good].ravel().tolist())
 np.savez_compressed(O/'02_Data'/row['file'],vertices=v,faces=f,uv=uv,material_ids=mid)
 row['photo_triangles']=int(sum(mid==i for i,label in enumerate(row['materials']) if label.startswith(('PATCH_PHOTO_','BASE_PHOTO_'))).sum())
 report.append({'node':row['name'],'eligible_unmapped_tile_faces':len(sel),'additional_photo_faces':assigned,'total_faces':len(f),'photo_faces_after':row['photo_triangles'],'max_distance_m':max(distances) if distances else None})
 print(report[-1],flush=True)
(O/'02_Data/Patch_Index.json').write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'06_Report/Roof_Photo_Repair.json').write_text(json.dumps({'method':'One original atlas per modeled tile triangle, determined by nearest original measured roof envelope at centroid; sides do not use roof-plane normal rejection; vertices must match same atlas within0.5m and UV span<0.12','geometry_changed':False,'source_photos_changed':False,'added_photo_triangles':sum(r['additional_photo_faces'] for r in report),'rows':report,'unmatched':'Original modeled tile material retained; photo position gate is not surveying accuracy'},ensure_ascii=False,indent=2),encoding='utf-8')
q=json.loads((O/'06_Report/Patch_Clip_And_Photo_QA.json').read_text(encoding='utf-8'));q['counts']['photo_projected_triangles']=sum(r.get('photo_triangles',0) for r in I);q['roof_photo_repair']='Roof_Photo_Repair.json';(O/'06_Report/Patch_Clip_And_Photo_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
