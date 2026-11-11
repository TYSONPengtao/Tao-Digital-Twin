import bpy,json,numpy as np,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
from v24_06_common import snapshot
O=Path('E:/jz/JIA/Rebuild_V26_13');D=W/'v26_13';P=O/'Blender/Architecture_Complete_V26_13.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();ch=json.loads((O/'Reports/V26_13_Changes.json').read_text('utf8'));before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False));checks=[]
def ck(name,p,**kw):checks.append({'check':name,'pass':bool(p),**kw});print('QA',name,bool(p),kw if not p else'',flush=True)
allowed=set(ch['changed']+ch['archived']);bad=[n for n,r in before['objects'].items()if n not in allowed and after['objects'].get(n)!=r];ck('Every original object outside the stated gate scope is unchanged',not bad,invalid=bad)
for key in['materials','images','actions','door_poses']:
 bad=[n for n,v in before[key].items()if after[key].get(n)!=v];ck('Original '+key+' preserved',not bad,invalid=bad)
def mesh(o):
 me=o.data;me.calc_loop_triangles();v=q._world(me,o.matrix_world);f=np.asarray([t.vertices[:]for t in me.loop_triangles]);return v,f
def tree(o):
 v,f=mesh(o);return BVHTree.FromPolygons([Vector(x)for x in v],f.tolist(),all_triangles=True)
def inside(t,p):
 origin=Vector(p);direction=Vector((.8731,.4517,.1834)).normalized();count=0
 for k in range(64):
  hit,no,index,dist=t.ray_cast(origin,direction,100.)
  if hit is None:return count%2==1
  count+=1;origin=hit+direction*.0001
 raise RuntimeError('Unresolved parity')
body=bpy.data.objects['V26_10_Inner_Gate_Rectangular_Stone_Piers'];bt=tree(body);rows=[]
for x0,x1 in[(4.9333333969,5.4571428571),(7.7428571429,8.2666664124)]:
 for side in['left','right']:
  x=x0 if side=='left'else x1;s=1 if side=='left'else-1
  outside=inside(bt,(x+s*.025,-11.845,1.2));bearing=inside(bt,(x+s*.065,-11.805,1.2));rows.append({'side':side,'x':x,'front_corner_removed':not outside,'bearing_retained':bearing})
ck('Both front corners on each pier form real90mm chamfers rather than12mm corner nicks',all(r['front_corner_removed']and r['bearing_retained']for r in rows),stations=rows)
retained=[]
for name in ch['retained_headers']+[ch['waist']]:
 o=bpy.data.objects[name];v,f=mesh(o)
 source='V24_Gate_Waist_Carving_Retained'if name==ch['waist']else name
 prefix='Input_'if name.startswith('V26_12_Restored_')else'V26_12_'
 a=np.load(D/(prefix+source+'.npz'))
 uv=np.array([[o.data.uv_layers.active.data[l].uv[:]for l in t.loops]for t in o.data.loop_triangles])if o.data.uv_layers.active else np.zeros((len(f),3,2))
 retained.append({'object':name,'pass':bool(np.array_equal(v,a['v'])and np.array_equal(f,a['f'])and np.array_equal(uv,a['uv']))})
ck('Header and original faceted waist preserve their exact shape, pose and UV',all(r['pass']for r in retained),objects=retained)
bad=[];exposed=[];ins=json.loads((D/'Input_Reliefs.json').read_text('utf8'));ix={r['name']:r for r in ins}
for r in ch['panels']:
 o=bpy.data.objects[r['name']];v,f=mesh(o);a=np.load(D/ix[r['source']]['file']);ids=np.asarray(r['front_vertex_ids'],int);n=np.asarray(r['inside']);origin=np.asarray(r['origin']);oldn=np.asarray(ix[r['source']]['inside']);oldo=np.asarray(ix[r['source']]['origin']);olddepth=(a['v']-oldo)@oldn;depth=(v-origin)@n
 if np.max(abs(depth-olddepth))>.000004:bad.append(o.name+' height changed')
 # A vertically fitted n-gon may choose a different triangle diagonal. Compare
 # persistent polygon loops and their UVs against the untouched source instead.
 original=bpy.data.objects[r['source']].data
 uv=np.array([l.uv[:]for l in o.data.uv_layers.active.data]);old_uv=np.array([l.uv[:]for l in original.uv_layers.active.data])
 if not np.array_equal(uv,old_uv):bad.append(o.name+' UV changed')
 if [p.vertices[:]for p in o.data.polygons]!=[p.vertices[:]for p in original.polygons]:bad.append(o.name+' polygon topology changed')
 if len(o.modifiers)or not o.visible_get()or o.hide_render:bad.append(o.name+' not visible baked mesh')
 if r['lower_extended']and(abs(v[:,2].min()+.433)>.00001 or abs(v[:,2].max()-.553)>.00001):bad.append(o.name+' lower extent')
 # The stone-core ray must reach each carved field before entering the backing.
 ft=tree(o);pts=v[ids];h=-depth[ids];tangent=np.cross(n,[0,0,1.]);u=pts@tangent;z=pts[:,2];ok=(u>u.min()+np.ptp(u)*.08)&(u<u.max()-np.ptp(u)*.08)&(z>z.min()+np.ptp(z)*.08)&(z<z.max()-np.ptp(z)*.08);pool=np.flatnonzero(ok)
 for label,k in[('valley',pool[np.argmin(h[pool])]),('peak',pool[np.argmax(h[pool])])]:
  pt=pts[k];near=Vector(pt-n*.03);fh=ft.ray_cast(near,Vector(n),.1);bh=bt.ray_cast(near,Vector(n),.1);yes=fh[0]is not None and np.linalg.norm(np.array(fh[0])-pt)<.0001 and(bh[0]is None or fh[3]<bh[3]-.001);exposed.append({'object':o.name,'sample':label,'pass':bool(yes),'height_m':float(h[k])})
ck('All18 refitted pier fields retain original UV and carving depth with no live subdivision',not bad,invalid=bad)
ck('All36 sampled peaks and valleys remain exposed above actual stone backing',all(r['pass']for r in exposed),samples=exposed)
ck('Six lower pictures extend150mm closer to the doorway floor',sum(r['lower_extended']for r in ch['panels'])==6 and all(abs(r['target_z_m'][0]+.433)<.00001 for r in ch['panels']if r['lower_extended']))
v,f=mesh(body);foot=v[v[:,2]<-.474];ck('Thin chamfered footings replace the former projecting pads',abs(foot[:,1].min()+11.89)<.00001 and abs(foot[:,2].min()+.510)<.00001 and abs(foot[:,0].min()-(4.9333333969-.020))<.00001,bounds=[foot.min(0).tolist(),foot.max(0).tolist()])
pl=bpy.data.objects['SITE_V21_GATE_REFERENCE_LAYER_01_Geometry'];v,f=mesh(pl);ck('One continuous100mm step has the reduced photo-fitted footprint',np.max(abs(v.min(0)[:2]-np.array([4.9033333969,-11.96])))<.00001 and abs(v.max(0)[2]+.5)<.00001,bounds=[v.min(0).tolist(),v.max(0).tolist()])
bad=[]
for name in ch['structural_changed']+[r['name']for r in ch['panels']]:
 v,f=mesh(bpy.data.objects[name]);edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),1);_,cnt=np.unique(edges,axis=0,return_counts=True);vol=np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6
 if not np.isfinite(v).all()or not np.all(cnt==2)or vol<=0:bad.append(name)
ck('Changed native structural meshes and carved inserts are finite closed positive solids',not bad,invalid=bad)
ground=[];deps=bpy.context.evaluated_depsgraph_get()
for x,y in[(4.82,-12.06),(8.36,-12.06),(6.6,-12.08),(4.85,-11.96),(8.34,-11.96)]:
 hit,co,no,fi,o,ma=sc.ray_cast(deps,Vector((x,y,-.3)),Vector((0,0,-1)),distance=2);ground.append({'xy':[x,y],'z':float(co.z)if hit else None,'object':o.name if o else None,'pass':bool(hit and -.72<co.z<-.49)})
ck('Ground is continuous where the oversize apron and pads were removed',all(r['pass']for r in ground),stations=ground)
ck('All superseded gate panels remain archived editably',all(bpy.data.objects[n].hide_render and bpy.data.objects[n].hide_get()for n in ch['archived']))
ck('Overcast lighting and readable local AO retained',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and sc.eevee.use_fast_gi and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY')
ck('V26.12 source file remains byte-identical',hashlib.sha256(Path(ch['source']).read_bytes()).hexdigest()==ch['source_sha256'])
fail=[r for r in checks if not r['pass']];(O/'Reports/V26_13_Native_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
