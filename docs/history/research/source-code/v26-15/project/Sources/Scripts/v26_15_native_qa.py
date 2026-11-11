import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
import v24_qa_blender as q
O=Path('E:/jz/JIA/Rebuild_V26_15');D=W/'v26_15';F=D/'Final';F.mkdir(exist_ok=True);P=O/'Blender/Architecture_Complete_V26_15.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();ch=json.loads((O/'Reports/V26_15_Changes.json').read_text('utf8'));before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False));checks=[];rows=[];trees={}
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('NATIVE_QA',n,bool(p),kw if not p else'',flush=True)
bad=[n for n,r in before['objects'].items()if n not in ch['changed']and after['objects'].get(n)!=r];ck('Every unrelated original object stays exact in geometry UV transform and visibility',not bad,invalid=bad)
for key in ['materials','images','actions','door_poses']:
 bad=[n for n,r in before[key].items()if after[key].get(n)!=r];ck('Original '+key+' remain exact',not bad,invalid=bad)
for n,an in ch['archive_map'].items():
 a=bpy.data.objects[an];ck('Editable exact original archived '+n,q._mesh_hash(a.data)==before['objects'][n]['mesh_hash']and a.hide_render and not a.visible_get())
for name in ch['geometry_changed']:
 o=bpy.data.objects[name];me=o.data;me.calc_loop_triangles();v=q._world(me,o.matrix_world);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int64);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);np.savez_compressed(F/(name+'.npz'),v=v,f=f,uv=uv,mi=mi);trees[name]=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);tr=v[f];area=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)/2;edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),1);_,cnt=np.unique(edges,axis=0,return_counts=True);ck('Saved native indexed mesh finite closed and nondegenerate '+name,np.isfinite(v).all()and np.isfinite(uv).all()and area.min()>1e-18 and np.all(cnt==2),minimum_triangle_area_m2=float(area.min()),nonmanifold_edges=int((cnt!=2).sum()));rows.append({'name':name,'file':name+'.npz','materials':[m.name for m in me.materials],'triangles':len(f),'mesh_hash':q._mesh_hash(me)})
(F/'Geometry_Index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
HN='V26_3_House_Connected_Walls_And_Stairs';GN='V26_2_Continuous_Ground_And_Perimeter_Shell';tree=trees[HN];wall=[]
for z in[2.0,3.34,3.38,3.43,4.3,6.94,6.98,7.03,8.4]:
 for label,org,direction,ax,target in [('west',(4.5,7.52,z),(-1,0,0),0,4.02),('front',(4.12,7.9,z),(0,-1,0),1,7.42)]:
  if label=='front' and z==8.4:continue # Preserved F3 terrace door aperture is intentionally open here.
  hit,no,idx,dist=tree.ray_cast(Vector(org),Vector(direction),.7);wall.append({'label':label,'z_m':z,'target':target,'actual':float(hit[ax])if hit is not None else None,'pass':bool(hit is not None and abs(hit[ax]-target)<2e-6)})
ck('Stair corner is flush across both formerly protruding slab seals',all(r['pass']for r in wall),samples=wall)
floor=[]
for x in np.linspace(8.4,9.4,11):
 for y in np.linspace(-11.59,-11.12,12):
  hit,no,idx,dist=trees[GN].ray_cast(Vector((x,y,0.1)),Vector((0,0,-1)),1.);floor.append({'xy_m':[float(x),float(y)],'z_m':float(hit.z)if hit is not None else None,'pass':bool(hit is not None and abs(hit.z+.4000244140625)<3e-6 and no.z>.999)})
ck('Gate rear wall-side floor is level and continuously supported at132 native stations',all(r['pass']for r in floor),samples=floor)
cn={r['name']for r in json.loads((O/'Reports/V26_15_Collision_Index.json').read_text('utf8'))['objects']};ck('Collision owns corrected floor and house and excludes all archives',HN in cn and GN in cn and not any(n in cn for n in ch['archived']))
ck('Overcast soft even world with local AO retained',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and sc.eevee.use_fast_gi and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY'and all(o.data.energy==0 for o in sc.objects if o.type=='LIGHT'and o.data.type=='SUN'))
ck('Source V26.14 stays byte-identical',hashlib.sha256(Path(ch['source']).read_bytes()).hexdigest()==ch['source_sha256'])
fail=[r for r in checks if not r['pass']];out={'status':'PASS'if not fail else'FAIL','model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':checks,'failures':fail};(O/'Reports/V26_15_Native_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('NATIVE_QA_DONE',len(checks),len(fail),flush=True)
