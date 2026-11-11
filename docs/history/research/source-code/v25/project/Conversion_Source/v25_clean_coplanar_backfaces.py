from pathlib import Path
import sys,json,struct,hashlib
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
D=W/'v25';O=Path('E:/jz/JIA/Rebuild_V25');idx=json.loads((D/'Export_Index.json').read_text('utf8'));name='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';parts=[];target=None
assert not (D/'Coplanar_Cleanup.json').exists(),'Cleanup already applied'
(D/'Before_Coplanar_Cleanup_Export_Index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf8')
for row in idx:
 if row['source_object']!=name:continue
 data=Path(row['file']).read_bytes();_,nv,nf=struct.unpack_from('<III',data,4);offset=16+nv*44;v=np.frombuffer(data,'<f8',nv*3,16).reshape(-1,3);f=np.frombuffer(data,'<i4',nf*3,offset).reshape(-1,3);tri=v[f];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(n,axis=1)/2;n/=np.linalg.norm(n,axis=1)[:,None];parts.append((row,data,nv,nf,offset,v,f,tri,n,area))
 if row['material'].endswith('::M_V24_11_Plain_White_Limewash'):target=parts[-1]
assert target
row,data,nv,nf,offset,v,f,tri,n,area=target;alltri=np.concatenate([p[7] for p in parts]);allnorm=np.concatenate([p[8] for p in parts]);remove=[];proof=[]
for i in np.flatnonzero((n[:,0]<-.8)&(tri[:,:,2].max(1)<-.34)&(tri[:,:,0].min(1)>12)&(tri[:,:,0].max(1)<14.3)):
 t=tri[i];normal=n[i];same=(allnorm@normal)<-.999999;distance=np.abs(np.einsum('fvi,i->fv',alltri-t[0],normal)).max(1);same&=distance<2e-6;axis=int(np.argmax(abs(normal)));use=[a for a in range(3) if a!=axis];p=Polygon(t[:,use]);polys=[]
 for q in alltri[same]:
  z=Polygon(q[:,use])
  if z.intersects(p):polys.append(z)
 if not polys:continue
 u=unary_union(polys);uncovered=p.difference(u).area
 if uncovered<=max(1e-10,p.area*1e-5):remove.append(int(i));proof.append({'face':int(i),'area_m2':float(area[i]),'normal':normal.tolist(),'uncovered_fraction':float(uncovered/max(p.area,1e-20)),'coplanarity_tolerance_m':2e-6})
assert remove,'No fully covered reverse interior faces found'
keep=np.ones(nf,bool);keep[remove]=False;faces=f[keep].astype('<i4');p=Path(row['file']);new=b'R25M'+struct.pack('<III',1,nv,len(faces))+data[16:offset]+faces.tobytes();oldhash=row['sha256'];p.write_bytes(new);row['sha256']=hashlib.sha256(new).hexdigest();row['triangles']=len(faces);row['area_m2']=float(area[keep].sum());row['geometry_method']+='; removed fully covered reverse internal wall-foot faces (2 micrometre coplanarity tolerance, complete coverage proof). No retained positions, normals or UV changed.'
report={'status':'PASS_COPLANAR_INTERNAL_BACKFACE_CLEANUP','source_object':name,'material_key':row['material'],'faces_removed':len(remove),'surface_information_preserved':True,'coverage_proof':proof,'original_geometry_sha256':oldhash,'clean_geometry_sha256':row['sha256'],'retained_positions_normals_uv_unchanged':True,'original_source_blend_unchanged':True};(D/'Coplanar_Cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');(O/'Reports/V25_Coplanar_Cleanup_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
(D/'Export_Index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf8');r=json.loads((D/'Export_Report.json').read_text('utf8'));r['export_triangles']=sum(x['triangles']for x in idx);r['coplanar_internal_backfaces_removed']=len(remove)
for p in [D/'Export_Report.json',O/'Reports/V25_Blender_Export_QA.json']:p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print('COPLANAR_BACKFACE_CLEANUP_OK',len(remove),'retained triangles',r['export_triangles'],flush=True)
