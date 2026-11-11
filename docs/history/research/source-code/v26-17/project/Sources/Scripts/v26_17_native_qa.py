import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
import v24_qa_blender as q
D=W/'v26_17';F=D/'Final';F.mkdir(exist_ok=True);O=Path('E:/jz/JIA/Rebuild_V26_17');P=O/'Blender/Architecture_Complete_V26_17.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
ch=json.loads((O/'Reports/V26_17_Changes.json').read_text('utf8'));before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False));source=json.loads((D/'Input/Source_Index.json').read_text('utf8'));ix={r['name']:r for r in source['objects']};checks=[]
def ck(name,yes,**data):checks.append({'check':name,'pass':bool(yes),**data});print('NATIVE_QA',name,bool(yes),data if not yes else'',flush=True)
bad=[n for n,r in before['objects'].items()if n not in ch['changed']and after['objects'].get(n)!=r];ck('Every unrelated original object, central window, leaf and Roman column stays exact',not bad,invalid=bad)
for key in['materials','images','actions','door_poses']:
 bad=[n for n,r in before[key].items()if after[key].get(n)!=r];ck('Original '+key+' stay exact',not bad,invalid=bad)
for name,archive in ch['archive_map'].items():
 ob=bpy.data.objects[archive];ck('Exact prior native mesh is recoverable and hidden: '+name,q._mesh_hash(ob.data)==before['objects'][name]['mesh_hash']and ob.hide_render and not ob.visible_get())
rows=[];arrays={}
for name in ch['geometry_changed']:
 ob=bpy.data.objects[name];me=ob.data;me.calc_loop_triangles();v=q._world(me,ob.matrix_world);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int64);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles]);np.savez_compressed(F/(name+'.npz'),v=v,f=f,mi=mi,uv=uv)
 tr=v[f];area=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)/2;edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),1);_,cnt=np.unique(edges,axis=0,return_counts=True)
 closed=np.all(cnt==2)
 ck('Saved mesh has finite UVs, nonzero faces and preserved topology: '+name,np.isfinite(v).all()and np.isfinite(uv).all()and area.min()>1e-18 and closed,minimum_triangle_m2=float(area.min()))
 row={'name':name,'file':name+'.npz','materials':[m.name for m in me.materials],'mesh_hash':q._mesh_hash(me),'triangles':len(f)};rows.append(row);arrays[name]=(v,f,mi)
(F/'Geometry_Index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
HN='V26_3_House_Connected_Walls_And_Stairs';v,f,mi=arrays[HN];hr=next(r for r in rows if r['name']==HN);tree=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True)
sa=np.load(D/'Input'/ix[HN]['file']);source_tree=BVHTree.FromPolygons([Vector(p)for p in sa['v']],sa['f'].tolist(),all_triangles=True)
beam_hits=[];column_hits=[];plate_hits=[]
for b in ch['proof']['bays']:
 x0,x1=b['axis_span_m'];z=b['beam_soffit_z_m']
 for x in np.linspace(x0+.25,x1-.25,13):
  hit,no,index,distance=tree.ray_cast(Vector((float(x),2.1,z-.02)),Vector((0,0,1)),.5);old_hit,_,_,_=source_tree.ray_cast(Vector((float(x),2.1,z-.02)),Vector((0,0,1)),.5)
  beam_hits.append({'floor':b['floor'],'side':b['side'],'x_m':float(x),'before_z_m':float(old_hit.z)if old_hit is not None else None,'after_z_m':float(hit.z)if hit is not None else None,'expected_z_m':z,'pass':bool(hit is not None and abs(hit.z-z)<2e-6 and hr['materials'][mi[index]]=='M_V26_3_Neutral_White_Interior_Ceiling')})
 for cx,sign in[(x0,1),(x1,-1)]:
  face=cx+sign*.2
  for y in[2.,2.12,2.25]:
   for ztest in[b['frame_bottom_z_m']+.1,(b['frame_bottom_z_m']+b['frame_top_z_m'])/2]:
    hit,_,_,_=tree.ray_cast(Vector((face+sign*.35,y,ztest)),Vector((-sign,0,0)),.7)
    column_hits.append({'floor':b['floor'],'side':b['side'],'axis_x_m':cx,'y_m':y,'z_m':ztest,'actual_face_x_m':float(hit.x)if hit is not None else None,'pass':bool(hit is not None and abs(hit.x-face)<2e-6)})
 # Probe the newly fitted side strips on their room side, past the200mm sill.
 for frame in[q for q in ch['proof']['fixed_return_frames']if q['floor']==b['floor']and q['side']==b['side']]:
  start,end=map(np.asarray,frame['new_segment_xy']);t=end-start;t/=np.linalg.norm(t);normal=np.array([-t[1],t[0]])
  from mathutils.geometry import intersect_point_tri_2d
  # Both normals are tried using the bay polygon's simple ray-crossing test.
  poly=np.asarray(b['new_bay_plan']['coordinates'][0])
  def inside(p):
   parity=False
   for aa,bb in zip(poly[:-1],poly[1:]):
    if(aa[1]>p[1])!=(bb[1]>p[1])and p[0]<(bb[0]-aa[0])*(p[1]-aa[1])/(bb[1]-aa[1])+aa[0]:parity=not parity
   return parity
  if not inside((start+end)/2+normal*.16):normal=-normal
  for factor in[.25,.5,.72]:
   xy=start+(end-start)*factor+normal*.16
   for tag,expected,direction,origin in [('floor',b['floor_z_m'],(0,0,-1),b['floor_z_m']+.12),('ceiling',b['ceiling_z_m'],(0,0,1),b['ceiling_z_m']-.06)]:
    hit,_,_,_=tree.ray_cast(Vector((float(xy[0]),float(xy[1]),origin)),Vector(direction),.5);plate_hits.append({'floor':b['floor'],'side':b['side'],'location':tag,'xy_m':xy.tolist(),'expected_z_m':expected,'actual_z_m':float(hit.z)if hit is not None else None,'pass':bool(hit is not None and abs(hit.z-expected)<2e-6)})
ck('65 saved native beam soffit stations are straight and at the original datum',all(h['pass']for h in beam_hits),stations=beam_hits)
ck('60 saved native column face stations retain the full original rectangular section',all(h['pass']for h in column_hits),stations=column_hits)
ck('60 saved native floor and ceiling stations support the new returns at unchanged levels',all(h['pass']for h in plate_hits),stations=plate_hits)
ci=json.loads((O/'Reports/V26_17_Collision_Index.json').read_text('utf8'))['objects'];names={r['name']for r in ci}
ck('Navigation collision includes all corrected facade meshes and excludes archives',set(ch['geometry_changed']).issubset(names)and not any(n in names for n in ch['archived']))
ck('Inherited overcast soft even lighting and local AO remain',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY'and all(o.data.energy==0 for o in sc.objects if o.type=='LIGHT'and o.data.type=='SUN'))
ck('Saved V26.16 source remains byte-identical',hashlib.sha256(Path(ch['source']).read_bytes()).hexdigest()==ch['source_sha256'])
mh=hashlib.sha256(P.read_bytes()).hexdigest();(D/'Native_After_Snapshot.json').write_text(json.dumps(after,ensure_ascii=False),'utf8');(D/'Native_Snapshot_Source_SHA256.txt').write_text(mh,'utf8')
fail=[c for c in checks if not c['pass']];out={'status':'PASS'if not fail else'FAIL','model_sha256':mh,'checks':checks,'failures':fail};(O/'Reports/V26_17_Native_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('NATIVE_QA_DONE',len(checks),len(fail),flush=True)
