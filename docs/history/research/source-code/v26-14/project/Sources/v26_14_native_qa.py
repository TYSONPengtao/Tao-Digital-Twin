import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
import v24_qa_blender as q
O=Path('E:/jz/JIA/Rebuild_V26_14');D=W/'v26_14';P=O/'Blender/Architecture_Complete_V26_14.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();ch=json.loads((O/'Reports/V26_14_Changes.json').read_text('utf8'));before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False));checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('NATIVE_QA',n,bool(p),kw if not p else'',flush=True)
bad=[n for n,r in before['objects'].items()if n not in ch['changed']and after['objects'].get(n)!=r];ck('Every original object outside the house wall and collision cache is unchanged',not bad,invalid=bad)
for key in ['materials','images','actions','door_poses']:
 bad=[n for n,r in before[key].items()if after[key].get(n)!=r];ck('Original '+key+' remain exact',not bad,invalid=bad)
archive=bpy.data.objects[ch['archived'][0]];ck('Original house is archived editably with exact geometry and UV',q._mesh_hash(archive.data)==before['objects']['V26_3_House_Connected_Walls_And_Stairs']['mesh_hash']and archive.hide_render and archive.hide_get())
o=bpy.data.objects['V26_3_House_Connected_Walls_And_Stairs'];me=o.data;me.calc_loop_triangles();v=q._world(me,o.matrix_world);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);np.savez_compressed(D/'Saved_House.npz',v=v,f=f,uv=uv,mi=mi);tree=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True)
tr=v[f];area=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)/2;edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),1);_,cnt=np.unique(edges,axis=0,return_counts=True)
ck('Saved house vertices and UV are finite with no zero faces and every edge used twice',np.isfinite(v).all()and np.isfinite(uv).all()and area.min()>1e-18 and np.all(cnt==2),minimum_triangle_area_m2=float(area.min()),nonmanifold_edges=int((cnt!=2).sum()))
samples=[]
for p in ch['proof']['patches']:
 x=p['adjacent_finished_x_m'];side=p['side'];z0=p['bounds_m'][0][2];sgn=1 if side=='L'else-1
 for y in [7.19,7.25,7.35,7.405,7.45,7.55,7.64]:
  for dz in [.05,1.0,2.5,2.90]:
   origin=Vector((x+sgn*.22,y,z0+dz));hit,no,idx,dist=tree.ray_cast(origin,Vector((-sgn,0,0)),.5);yes=hit is not None and abs(hit.x-x)<.00001 and abs(no.x-sgn)<.00001
   samples.append({'floor':p['floor'],'side':side,'y_m':y,'z_m':z0+dz,'actual_x_m':float(hit.x)if hit else None,'target_x_m':x,'pass':bool(yes)})
ck('Four WC returns are flush from front wall to doorway at112 actual native stations',all(r['pass']for r in samples),samples=samples)
heads=[]
for p in ch['proof']['head_seats']:
 x=p['bounds_m'][1][0]if p['side']=='L'else p['bounds_m'][0][0];sgn=1 if p['side']=='L'else-1
 for y in[7.44,7.48,7.54,7.60]:
  for z in[p['bounds_m'][0][2]+.03,p['bounds_m'][1][2]-.005]:
   hit,no,idx,dist=tree.ray_cast(Vector((x+sgn*.15,y,z)),Vector((-sgn,0,0)),.4);heads.append({'floor':p['floor'],'side':p['side'],'y_m':y,'z_m':z,'actual_x_m':float(hit.x)if hit else None,'pass':bool(hit is not None and abs(hit.x-x)<.00001 and abs(no.x-sgn)<.00001)})
ck('Partition heads are complete behind the beam without a stepped void',all(r['pass']for r in heads),samples=heads)
# The added solids lie completely before the original door apertures. Probe
# actual saved opaque masonry across the centres of all five WC door seats.
door=[]
for n in ['DOOR_BATH_F1_L__FRAME_Geometry','DOOR_BATH_F1_R__FRAME_Geometry','DOOR_BATH_F2_L__FRAME_Geometry','DOOR_BATH_F2_R__FRAME_Geometry','DOOR_BATH_F3_R__FRAME_Geometry']:
 ob=bpy.data.objects[n];pv=np.array([ob.matrix_world@v.co for v in ob.data.vertices]);lo,hi=pv.min(0),pv.max(0);ax=int(np.argmin((hi-lo)[:2]));c=(lo+hi)/2;c[2]=lo[2]+1.;dv=np.eye(3)[ax]*.4;h=tree.ray_cast(Vector(c-dv),Vector(np.eye(3)[ax]),.8);door.append({'door':n,'opaque_hit':h[0]is not None})
ck('All five existing WC door apertures remain open through the wall depth',not any(r['opaque_hit']for r in door),doors=door)
cn={r['name']for r in json.loads((O/'Reports/V26_14_Collision_Index.json').read_text('utf8'))['objects']};ck('Collision uses corrected house and excludes archived original',o.name in cn and archive.name not in cn)
ck('Overcast and local AO settings inherited',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and sc.eevee.use_fast_gi and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY')
ck('V26.13 source model remains byte-identical',hashlib.sha256(Path(ch['source']).read_bytes()).hexdigest()==ch['source_sha256'])
fail=[r for r in checks if not r['pass']];(O/'Reports/V26_14_Native_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('NATIVE_QA_DONE',len(checks),len(fail),flush=True)
