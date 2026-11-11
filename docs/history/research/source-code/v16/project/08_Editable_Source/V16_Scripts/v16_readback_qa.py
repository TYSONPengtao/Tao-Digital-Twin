import sys,json,math,hashlib,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]
import numpy as np,rhino3dm as rh
from shapely.geometry import shape,Point,Polygon,LineString
from shapely.ops import unary_union
O=Path(r'E:/jz/JIA/Rebuild_V16');B=Path(r'E:/jz/JIA/Rebuild_V15');D=W/'v16';P=O/'04_Rhino/Architecture_Complete_V16_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));AQ=json.loads((O/'06_Report/V16_Assembly_QA.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));ii={r['name']:r for r in I};C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);obs={str(ob.Attributes.Id):ob for ob in F.Objects}
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
bad=[r['name'] for r in AQ['retained'] if r['id'] not in obs or gh(obs[r['id']].Geometry)!=r['geometry_hash']];assert not bad,bad[:10]
newbad=[r['name'] for r in AQ['created'] if r['id'] not in obs or gh(obs[r['id']].Geometry)!=r['geometry_hash']];assert not newbad,newbad
print('NATIVE HASHES PASS',len(AQ['retained']),len(AQ['created']),flush=True)
checks=[]
for rec in AQ['created']:
 g=obs[rec['id']].Geometry;n=rec['node'];v=(np.array([[p.X,p.Y,p.Z] for p in g.Vertices.ToPoint3dArray()])-origin)@R;f=np.array([t[:3] for t in g.Faces],np.int32);uv=np.array([[p.X,p.Y] for p in g.TextureCoordinates]);nn=np.array([[p.X,p.Y,p.Z] for p in g.Normals])@R;length=np.linalg.norm(nn,axis=1);t=v[f];volume=np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6;r=ii[n];old=np.load(O/'02_Data'/r['file']);err=float(abs(v-old['vertices']).max());assert g.IsValid and len(uv)==len(v) and err<1e-7,(n,err);assert length.min()>.9999 and length.max()<1.0001,(n,length.min(),length.max())
 if not n.startswith('SITE_V14_ORIGINAL_EXTERIOR'):assert g.IsClosed and volume>0,(n,g.IsClosed,volume)
 if n in ['SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE','SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE']:assert v[:,0].min()>-28 and v[:,0].max()<25 and v[:,1].min()>-21 and v[:,1].max()<14,(n,'unbounded corner miter',v.min(0).tolist(),v.max(0).tolist())
 np.savez_compressed(O/'02_Data'/r['file'],vertices=v,faces=f,uv=uv,normals=nn,material_ids=np.zeros(len(f),np.int32));checks.append({'node':n,'native_is_valid':g.IsValid,'native_is_closed':g.IsClosed,'full_uv':True,'normals_minmax':[float(length.min()),float(length.max())],'roundtrip_max_coordinate_error_m':err,'signed_volume_m3':float(volume) if g.IsClosed else None})
print('FRESH CHANGED NATIVE MESH READBACK PASS',flush=True)
def load(n):return np.load(O/'02_Data'/ii[n]['file'])
sd=load('SITE_V16_GRADED_INTERIOR_SOIL');st=sd['vertices'][sd['faces']];sn=np.cross(st[:,1]-st[:,0],st[:,2]-st[:,0]);up=sn[:,2]>1e-8;top=st[up];domain=unary_union([Polygon(t[:,:2]) for t in top]).buffer(0);hardnames=[n for n in ii if n.startswith(('SITE_V12_REBUILT_COURT','SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT','SITE_V12_OUTER_GATE_SCORED'))];hard=[]
for n in hardnames:
 d=load(n);t=d['vertices'][d['faces']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);tt=t[no[:,2]>1e-8];hard.append(unary_union([Polygon(q[:,:2]) for q in tt]).buffer(0))
hardunion=unary_union(hard);overlap=domain.intersection(hardunion).area;assert overlap<1e-5,overlap
grade_all=np.linalg.norm(sn[up,:2],axis=1)/sn[up,2];visible=np.ones(len(top),bool);infill_area=0
if 'SITE_V16_COURT_EDGE_INFILL_STEP' in ii:
 import shapely
 dd=load('SITE_V16_COURT_EDGE_INFILL_STEP');tt=dd['vertices'][dd['faces']];nn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);pp=unary_union([Polygon(q[:,:2]) for q in tt[nn[:,2]>1e-10]]).buffer(1e-8);visible=~shapely.covers(pp,shapely.points(top[:,:,:2].mean(1)));infill_area=pp.area
grade=grade_all[visible];ground={'soil_area_m2':domain.area,'top_z_minmax_m':[float(top[:,:,2].min()),float(top[:,:,2].max())],'grade_quantiles':np.quantile(grade,[.1,.5,.9,.99,1]).tolist(),'grade_quantiles_including_buried_step_subgrade':np.quantile(grade_all,[.1,.5,.9,.99,1]).tolist(),'small_supported_hard_level_infill_area_m2':infill_area,'buried_facets_under_hard_infill':int((~visible).sum()),'hard_ground_overlap_m2':overlap,'tree_pit_overlap_m2':domain.intersection(Point(-4,-13.5).buffer(.3999,quad_segs=12)).area};assert ground['tree_pit_overlap_m2']<1e-5;assert np.quantile(grade,.90)<.05 and np.quantile(grade,.99)<.35 and max(grade)<1.1,ground['grade_quantiles']
# Screenwall inner side: dense sampling proves the former multi-metre ditch is now level soil.
probes=[]
def query(x,y,ts):
 q=ts[(ts[:,:,:2].min(1)<=[x+1e-8,y+1e-8]).all(1)&(ts[:,:,:2].max(1)>=[x-1e-8,y-1e-8]).all(1)]
 if not len(q):return None
 a=q[:,0,:2];u=q[:,1,:2]-a;v=q[:,2,:2]-a;w=np.array([x,y])-a;de=u[:,0]*v[:,1]-u[:,1]*v[:,0];aa=(w[:,0]*v[:,1]-w[:,1]*v[:,0])/de;bb=(u[:,0]*w[:,1]-u[:,1]*w[:,0])/de;ok=(aa>=-1e-5)&(bb>=-1e-5)&(aa+bb<=1+1e-5)
 return float(np.max(q[ok,0,2]+aa[ok]*(q[ok,1,2]-q[ok,0,2])+bb[ok]*(q[ok,2,2]-q[ok,0,2]))) if ok.any() else None
for x in np.linspace(3.6,10.3,30):
 z=query(x,-16.2,top);probes.append({'x':float(x),'y':-16.2,'z':z})
valid=[r['z'] for r in probes if r['z'] is not None];assert len(valid)>=25 and max(valid)-min(valid)<.08,(len(valid),valid);ground['screenwall_soil_probes']=probes;ground['screenwall_z_range_m']=max(valid)-min(valid)
# Every cut road edge follows the same gutter outer-edge plane in LOCAL coordinates.
seg=json.loads((D/'Drain_Segments.json').read_text(encoding='utf8'));aa=np.array([r['outer_a'] for r in seg]);bb=np.array([r['outer_b'] for r in seg]);du=bb-aa;ll=(du*du).sum(1);zz=np.array([[r['za'],r['zb']] for r in seg]);contact=[]
for n in ii:
 if not n.startswith('SITE_V14_ORIGINAL_EXTERIOR'):continue
 d=load(n);v=d['vertices'];count=0;errs=[]
 for k in range(0,len(v),4096):
  p=v[k:k+4096];s=np.clip(((p[:,None,:2]-aa)*du).sum(2)/ll,0,1);dist=np.linalg.norm(aa+du*s[:,:,None]-p[:,None,:2],axis=2);idx=np.argmin(dist,axis=1);rr=np.arange(len(p));expected=zz[idx,0]+s[rr,idx]*(zz[idx,1]-zz[idx,0]);error=abs(p[:,2]-expected);ok=(dist[rr,idx]<1e-6)&(error<.7);errs.extend(error[ok].tolist());count+=int(ok.sum())
 if errs:contact.append({'node':n,'matching_boundary_vertices':count,'max_boundary_height_error_m':float(max(errs))})
assert sum(r['matching_boundary_vertices'] for r in contact)>300
assert max(r['max_boundary_height_error_m'] for r in contact)<.002,contact
ground['drain_scan_boundary_contact']=contact
paths=[]
for m in F.Materials:
 for get in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,get)()
  if tx:assert Path(tx.FileName).exists(),tx.FileName;paths.append(tx.FileName)
qa={'status':'PASS_NATIVE_READBACK_AND_GROUND_DRAIN_CONTACT','model':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'native_objects':len(F.Objects),'nodes':len(I),'retained_geometry_hash_checks':len(AQ['retained']),'unchanged_architecture_ramp_steps_roofs':not bad,'fresh_changed_mesh_checks':checks,'ground':ground,'material_path_count':len(paths),'method':'New meshes read directly from saved 3DM; unchanged Breps/blocks reuse V15 verified native tessellation after geometry-hash equality','field_elevation_independently_measured':False}
AQ['status']=qa['status'];AQ['sha256']=qa['sha256'];(O/'06_Report/V16_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V16_Native_Readback_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V16_Ground_Drain_QA.json').write_text(json.dumps({'status':qa['status'],**ground},ensure_ascii=False,indent=2),encoding='utf8');print('V16 GROUND AND DRAIN QA PASS',ground['top_z_minmax_m'],ground['grade_quantiles'],contact,flush=True)
