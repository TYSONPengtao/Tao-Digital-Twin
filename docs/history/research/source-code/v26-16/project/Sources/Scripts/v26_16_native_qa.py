import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
import v24_qa_blender as q
O=Path('E:/jz/JIA/Rebuild_V26_16');D=W/'v26_16';F=D/'Final';F.mkdir(exist_ok=True);P=O/'Blender/Architecture_Complete_V26_16.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();ch=json.loads((O/'Reports/V26_16_Changes.json').read_text('utf8'));before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False));checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('NATIVE_QA',n,bool(p),kw if not p else'',flush=True)
bad=[n for n,r in before['objects'].items()if n not in ch['changed']and after['objects'].get(n)!=r];ck('All unrelated original objects stay exact',not bad,invalid=bad)
for key in['materials','images','actions','door_poses']:
 bad=[n for n,r in before[key].items()if after[key].get(n)!=r];ck('Original '+key+' remain exact',not bad,invalid=bad)
for n,an in ch['archive_map'].items():
 a=bpy.data.objects[an];ck('Exact editable original archived '+n,q._mesh_hash(a.data)==before['objects'][n]['mesh_hash']and a.hide_render and not a.visible_get())
HN='V26_3_House_Connected_Walls_And_Stairs';EN='HOUSE_V22_CONTINUOUS_BALCONY_EDGE_Geometry';rows=[];arrays={}
for name in ch['geometry_changed']:
 o=bpy.data.objects[name];me=o.data;me.calc_loop_triangles();v=q._world(me,o.matrix_world);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int64);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);np.savez_compressed(F/(name+'.npz'),v=v,f=f,uv=uv,mi=mi)
 tr=v[f];normals=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);area=np.linalg.norm(normals,axis=1)/2;normals/=np.maximum(2*area[:,None],1e-30);centres=tr.mean(1);edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),1);_,cnt=np.unique(edges,axis=0,return_counts=True)
 ck('Saved corrected mesh has finite UVs and closed nondegenerate indexed topology: '+name,np.isfinite(v).all()and np.isfinite(uv).all()and area.min()>1e-18 and np.all(cnt==2),minimum_area_m2=float(area.min()),nonmanifold_edges=int((cnt!=2).sum()))
 rows.append({'name':name,'file':name+'.npz','materials':[m.name for m in me.materials],'triangles':len(f),'mesh_hash':q._mesh_hash(me)});arrays[name]=(v,f,mi,normals,centres)
(F/'Geometry_Index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8');v,f,mi,n,c=arrays[HN];r=next(r for r in rows if r['name']==HN);tree=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True)
ceiling=[];wall=[]
for nd in ch['proof']['nodes']:
 lo,hi=map(np.asarray,nd['scope_bounds_m']);head=np.all(c>=lo-1e-6,1)&np.all(c<=hi+1e-6,1)&(c[:,2]>=nd['beam_soffit_z_m']-1e-6);sel=head&(n[:,2]<-.99);wrong=[int(i)for i in np.flatnonzero(sel)if r['materials'][mi[i]]!='M_V26_3_Neutral_White_Interior_Ceiling'];sides=head&(abs(n[:,2])<.01);side_wrong=[int(i)for i in np.flatnonzero(sides)if r['materials'][mi[i]]!='M_Wall_Interior'];ceiling.append({'floor':nd['floor'],'side':nd['side'],'down_faces':int(sel.sum()),'wrong_material_faces':wrong,'wrong_vertical_material_faces':side_wrong})
 x=3.78 if nd['side']=='L'else 9.22;sign=1 if nd['side']=='L'else-1
 for y in[2.22,2.30,2.38]:
  for z in[nd['frame_bottom_z_m']+.07,(nd['frame_bottom_z_m']+nd['frame_top_z_m'])/2,nd['beam_soffit_z_m']-.04]:
   hit,no,idx,dist=tree.ray_cast(Vector((x-sign*.35,y,z)),Vector((sign,0,0)),.7);wall.append({'floor':nd['floor'],'side':nd['side'],'y':y,'z':z,'actual_x':float(hit.x)if hit is not None else None,'pass':bool(hit is not None and abs(hit.x-x)<2e-6)})
ck('All five head nodes have consistent ceiling and vertical painted finishes',all(not q['wrong_material_faces']and not q['wrong_vertical_material_faces']and q['down_faces']for q in ceiling),nodes=ceiling)
ck('Five inner window wall returns are continuous at45 saved native stations',all(q['pass']for q in wall),stations=wall)
ceiling_hits=[]
for x,y in[(9.24748039,2.17781115),(9.26412487,2.21126842),(3.75251961,2.17781115),(3.73587513,2.21126842)]:
 hit,normal,idx,dist=tree.ray_cast(Vector((x,y,3.2)),Vector((0,0,1)),.2)
 ceiling_hits.append({'xy_m':[x,y],'z_m':float(hit.z)if hit is not None else None,'pass':bool(hit is not None and abs(hit.z-3.319999933242798)<2e-6 and r['materials'][mi[idx]]=='M_V26_3_Neutral_White_Interior_Ceiling')})
ck('Previously exposed balcony-edge pixels now meet the true finished indoor ceiling',all(h['pass']for h in ceiling_hits),stations=ceiling_hits)
bay_hits=[]
for x,y in[(9.95,1.35),(10.3,1.3),(11.,1.5),(12.,1.4),(12.3,1.5)]:
 hit,normal,idx,dist=tree.ray_cast(Vector((x,y,10.1)),Vector((0,0,1)),.4)
 bay_hits.append({'xy_m':[x,y],'z_m':float(hit.z)if hit is not None else None,'pass':bool(hit is not None and abs(hit.z-10.220000267028809)<2e-6 and r['materials'][mi[idx]]=='M_V26_3_Neutral_White_Interior_Ceiling')})
ck('Third-floor right bay has a continuous flat soffit hiding roof-cut wall slivers',all(h['pass']for h in bay_hits),stations=bay_hits)
ci=json.loads((O/'Reports/V26_16_Collision_Index.json').read_text('utf8'))['objects'];ck('Collision uses both corrected meshes and excludes archive',{HN,EN}.issubset({q['name']for q in ci})and not any(n in{q['name']for q in ci}for n in ch['archived']))
ck('Overcast soft even world and local AO retained',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY'and all(o.data.energy==0 for o in sc.objects if o.type=='LIGHT'and o.data.type=='SUN'))
ck('Saved V26.15 source remains byte-identical',hashlib.sha256(Path(ch['source']).read_bytes()).hexdigest()==ch['source_sha256'])
fail=[q for q in checks if not q['pass']];out={'status':'PASS'if not fail else'FAIL','model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':checks,'failures':fail};(O/'Reports/V26_16_Native_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('NATIVE_QA_DONE',len(checks),len(fail),flush=True)
