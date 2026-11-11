"""Read-only V24 preservation and geometry QA; safe after fresh .blend readback."""
import hashlib,json,math
from pathlib import Path
import numpy as np

ALLOWED={'SITE_V21_GATE_REFERENCE_LAYER_04_Geometry','SITE_V21_GATE_REFERENCE_LAYER_05_Geometry','SITE_V21_GATE_REFERENCE_LAYER_14_Geometry'}

def _plain(v):
 if v is None or isinstance(v,(str,bool,int,float)):return v
 if hasattr(v,'name_full'):return {'id_type':type(v).__name__,'name':v.name_full}
 try:return [_plain(x) for x in v]
 except TypeError:return str(v)

def _jsonhash(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def _bulk(seq,key,n,dtype=np.float32):
 a=np.empty(len(seq)*n,dtype=dtype);seq.foreach_get(key,a);return a
def _matrix(m):return np.asarray(m,dtype=np.float64).round(10).tolist()

def _mesh_hash(me):
 h=hashlib.sha256()
 for seq,key,n,dt in [(me.vertices,'co',3,np.float32),(me.loops,'vertex_index',1,np.int32),(me.polygons,'loop_start',1,np.int32),(me.polygons,'loop_total',1,np.int32),(me.polygons,'material_index',1,np.int32),(me.polygons,'use_smooth',1,np.bool_)]:h.update(_bulk(seq,key,n,dt).tobytes())
 for uv in me.uv_layers:h.update(uv.name.encode());h.update(_bulk(uv.data,'uv',2).tobytes())
 h.update(json.dumps([m.name if m else None for m in me.materials]).encode());return h.hexdigest()

def _material(m):
 d={'name':m.name,'use_nodes':m.use_nodes,'diffuse_color':list(m.diffuse_color),'metallic':m.metallic,'roughness':m.roughness}
 if m.use_nodes:
  nodes=[]
  for n in m.node_tree.nodes:
   p={'name':n.name,'type':n.bl_idname,'inputs':[(s.identifier,_plain(s.default_value)) for s in n.inputs if hasattr(s,'default_value')]}
   for a in ['image','uv_map','operation','blend_type','extension','projection','interpolation','vector_type','distribution','is_active_output']:
    if hasattr(n,a):p[a]=_plain(getattr(n,a))
   nodes.append(p)
  d.update(nodes=sorted(nodes,key=lambda r:r['name']),links=sorted([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links]))
 return {'hash':_jsonhash(d),'shader':d}

def _image(im):
 packed=[]
 for p in getattr(im,'packed_files',[]):packed.append(hashlib.sha256(bytes(p.packed_file.data)).hexdigest())
 if not packed and im.packed_file:packed=[hashlib.sha256(bytes(im.packed_file.data)).hexdigest()]
 return {'name':im.name,'source':im.source,'size':list(im.size),'channels':im.channels,'colorspace':im.colorspace_settings.name,'alpha_mode':im.alpha_mode,'packed_hashes':packed}

def _curves(act):
 try:return list(act.fcurves)
 except AttributeError:
  out=[]
  for layer in act.layers:
   for strip in layer.strips:
    for bag in getattr(strip,'channelbags',[]):out.extend(bag.fcurves)
  return out

def _action(act):
 r=[]
 for f in _curves(act):r.append({'path':f.data_path,'index':f.array_index,'keys':[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.easing) for k in f.keyframe_points]})
 return _jsonhash(sorted(r,key=lambda x:(x['path'],x['index'])))

def _animation(ob):
 a=ob.animation_data
 if not a:return None
 return {'action':a.action.name if a.action else None,'nla':[[t.name,t.mute,[[s.name,s.action.name if s.action else None,s.frame_start,s.frame_end,s.action_frame_start,s.action_frame_end,s.scale,s.repeat,s.blend_type,s.extrapolation,s.influence,s.mute] for s in t.strips]] for t in a.nla_tracks]}

def _world(me,matrix):
 p=_bulk(me.vertices,'co',3,np.float64).reshape(-1,3);m=np.asarray(matrix);return p@m[:3,:3].T+m[:3,3]

def _wing_weight(p):
 x,y,z=p;t=min(1.,abs(x-6.6)/(.87*2.6547619));carrier=2.8093+.37*(.077*t*t+.638*t**7)
 inner=min(1.,max(0.,(abs(x-6.6)-1.86)/.30));upper=min(1.,max(0.,(z-carrier-.035)/.055));outer=min(1.,max(0.,(abs(x-6.6)-2.29)/.15));w=inner*max(upper,outer);return w*w*(3-2*w)

def _wing_reference(bpy):
 import bmesh
 ob=bpy.data.objects['SITE_V21_GATE_REFERENCE_LAYER_14_Geometry'];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.verts.ensure_lookup_table()
 remain=set(bm.verts);wings=[];anchors=[];allpts=[]
 while remain:
  r=remain.pop();stack=[r];comp={r}
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    other=e.other_vert(v)
    if other in remain:remain.remove(other);comp.add(other);stack.append(other)
  pts=np.array([tuple(ob.matrix_world@v.co)for v in comp]);cen=pts.mean(0)
  if cen[1]<-12.05 and abs(cen[0]-6.6)>1.8:
   wings.append({'vertices':len(comp),'bbox':[pts.min(0).tolist(),pts.max(0).tolist()]});allpts.extend(pts.tolist());anchors.extend(p.tolist() for p in pts if _wing_weight(p)<1e-12)
 bm.free();a=np.array(allpts);return {'components':wings,'anchor_points':anchors,'bbox':[a.min(0).tolist(),a.max(0).tolist()]}

def baseline_snapshot(bpy):
 """Capture before modification; JSON-serializable, includes all original assets."""
 sc=bpy.context.scene;frame=sc.frame_current;obs={}
 for o in bpy.data.objects:obs[o.name]={'type':o.type,'matrix':_matrix(o.matrix_world),'parent':o.parent.name if o.parent else None,'mesh_hash':_mesh_hash(o.data)if o.type=='MESH' else None,'animation':_animation(o)}
 doors=sorted(o.name for o in bpy.data.objects if o.get('UE_Interaction')in ['HINGED_INWARD','SLIDING']);poses={}
 for f in [1,20,40]:
  sc.frame_set(f);bpy.context.view_layer.update();poses[str(f)]={n:_matrix(bpy.data.objects[n].matrix_world)for n in doors}
 sc.frame_set(frame);bpy.context.view_layer.update()
 return {'frame':frame,'objects':obs,'materials':{m.name:_material(m)for m in bpy.data.materials},'images':{im.name:_image(im)for im in bpy.data.images if im.source!='VIEWER'and im.type not in ['RENDER_RESULT','COMPOSITING']},'actions':{a.name:_action(a)for a in bpy.data.actions},'doors':doors,'door_poses':poses,'wings':_wing_reference(bpy)}

def _stats(me):
 counts=np.bincount(_bulk(me.loops,'edge_index',1,np.int32),minlength=len(me.edges));me.calc_loop_triangles();p=_bulk(me.vertices,'co',3,np.float64).reshape(-1,3);f=_bulk(me.loop_triangles,'vertices',3,np.int32).reshape(-1,3);p=p-p.mean(0);t=p[f];vol=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
 return {'vertices':len(me.vertices),'faces':len(me.polygons),'closed':bool(len(counts)>0 and np.all(counts==2)),'signed_volume_m3':vol,'finite':bool(np.isfinite(p).all())}

def _panel_plan(name):
 if 'Header_'in name:
  j=int(name.rsplit('_',1)[1])-1;cx=[5.78,6.60,7.42][j];return np.array([cx-.340,-11.811]),np.array([cx+.340,-11.811]),2.488,2.646
 pi=int(name.split('_P')[1][0])-1;x0,x1=[(4.933333333333334,5.457142857142857),(7.742857142857142,8.266666666666666)][pi];face='left_bevel'if'left_bevel'in name else'right_bevel'if'right_bevel'in name else'front';a,b= {'front':([x0+.09,-11.87],[x1-.09,-11.87]),'left_bevel':([x0,-11.78],[x0+.09,-11.87]),'right_bevel':([x1-.09,-11.87],[x1,-11.78])}[face];a=np.array(a);b=np.array(b);t=(b-a)/np.linalg.norm(b-a);margin=.010 if face=='front'else.008;lo,hi=[(-.305,.575),(.778,2.312)][int(name.rsplit('_',1)[1])-1];return a+t*(margin+.021),b-t*(margin+.021),lo+.022,hi-.022

def validate_v24(bpy,baseline,output_dir):
 """Validate current/fresh-loaded result; write report and raise on real failures."""
 from mathutils import Vector,kdtree
 from mathutils.bvhtree import BVHTree
 checks=[];sc=bpy.context.scene;was=sc.frame_current;sc.frame_set(baseline['frame']);bpy.context.view_layer.update()
 def ck(n,ok,**extra):checks.append({'check':n,'pass':bool(ok),**extra})
 ck('Final scene has no white/clay material override',all(v.material_override is None for v in sc.view_layers),view_layer_overrides={v.name:v.material_override.name if v.material_override else None for v in sc.view_layers})
 for name,r in baseline['materials'].items():ck('Original shader '+name,name in bpy.data.materials and _material(bpy.data.materials[name])['hash']==r['hash'])
 for name,r in baseline['images'].items():ck('Original image/packed bytes '+name,name in bpy.data.images and _image(bpy.data.images[name])==r)
 for name,r in baseline['actions'].items():ck('Original door action '+name,name in bpy.data.actions and _action(bpy.data.actions[name])==r)
 for name,r in baseline['objects'].items():
  if name not in bpy.data.objects:
   ck('Original object retained '+name,name=='SITE_V21_GATE_REFERENCE_LAYER_04_Geometry');continue
  o=bpy.data.objects[name];ck('Original transform/parent/animation '+name,_matrix(o.matrix_world)==r['matrix'] and(o.parent.name if o.parent else None)==r['parent']and _animation(o)==r['animation'])
  if r['mesh_hash'] and name not in ALLOWED:ck('Unmodified site mesh/UV/material slots '+name,o.type=='MESH'and _mesh_hash(o.data)==r['mesh_hash'])
 ck('Exactly 26 original moving door roots',len(baseline['doors'])==26,count=len(baseline['doors']))
 for frame,poses in baseline['door_poses'].items():
  sc.frame_set(int(frame));bpy.context.view_layer.update()
  for name,m in poses.items():ck('Door sampled pose '+name+' frame'+frame,name in bpy.data.objects and _matrix(bpy.data.objects[name].matrix_world)==m)
 sc.frame_set(baseline['frame']);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
 panels=sorted([o for o in bpy.data.objects if o.name.startswith('V24_Gate_Reference_Relief_')],key=lambda o:o.name);ck('Fifteen independent carved fields',len(panels)==15,count=len(panels));panelrows=[];trees={}
 for key in ['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_05_Geometry']:
  support=bpy.data.objects[key];trees[key]=(support,BVHTree.FromObject(support,deps))
 for o in panels:
  st=_stats(o.data);ev=o.evaluated_get(deps);es=_stats(ev.data);depth=float(o.get('V24_Height_Depth_m',0));ck('Closed positive base and evaluated relief '+o.name,st['closed']and es['closed']and st['signed_volume_m3']>0 and es['signed_volume_m3']>0 and st['finite']and es['finite'],base=st,evaluated=es)
  ck('Real stone material retained '+o.name,[m.name for m in o.data.materials]==['M_V21_GATE_REF_04']);ck('Relief depth bounded '+o.name,0<depth<=.033,nominal_depth_m=depth)
  a,b,z0,z1=_panel_plan(o.name);t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]]);v=_world(o.data,o.matrix_world);u=(v[:,:2]-a)@t;d=(v[:,:2]-a)@n;w=np.linalg.norm(b-a)
  ck('Registered frame opening '+o.name,u.min()>-2e-5 and u.max()<w+2e-5 and v[:,2].min()>z0-2e-5 and v[:,2].max()<z1+2e-5 and d.min()>=-.001-depth-.0001 and d.max()<=.0091,bbox=[v.min(0).tolist(),v.max(0).tolist()],normal_depth_range_m=[float(d.min()),float(d.max())])
  key='SITE_V21_GATE_REFERENCE_LAYER_05_Geometry'if'Header_'in o.name else'SITE_V21_GATE_REFERENCE_LAYER_02_Geometry';support,tree=trees[key];back=v[d>d.max()-1e-5];stride=max(1,len(back)//30);dist=[]
  for p in back[::stride]:
   hit=tree.find_nearest(support.matrix_world.inverted()@Vector(p))
   if hit and hit[0]is not None:dist.append(float(hit[3]))
  ck('Backed into original stone recess '+o.name,bool(dist)and min(dist)<=.0015,minimum_back_support_distance_m=min(dist)if dist else None)
  ck('Editable multires and disabled baked source '+o.name,any(m.type=='MULTIRES'and m.total_levels>=1 for m in o.modifiers)and all(not m.show_render and not m.show_viewport and m.strength==0 for m in o.modifiers if m.type=='DISPLACE'))
  ck('Packed atlas reference '+o.name,o.get('V24_Height_Image')in bpy.data.images and bool(bpy.data.images[o['V24_Height_Image']].packed_file));ck('UV map retained '+o.name,bool(o.data.uv_layers));panelrows.append({'name':o.name,'base':st,'evaluated':es,'nominal_depth_m':depth})
 wn='SITE_V21_GATE_REFERENCE_LAYER_14_V24_Sculpted_Wings';wing=bpy.data.objects.get(wn);ck('Independent editable wing sculpture exists',wing is not None)
 if wing:
  v=_world(wing.data,wing.matrix_world);lo,hi=np.array(baseline['wings']['bbox']);st=_stats(wing.data);ck('Four original compact wing solids selected',len(baseline['wings']['components'])==4);ck('Sculpted wing closed positive',st['closed']and st['signed_volume_m3']>0,geometry=st);ck('Original compact wing bounds preserved',np.all(v.min(0)>=lo-2e-6)and np.all(v.max(0)<=hi+2e-6),before=[lo.tolist(),hi.tolist()],after=[v.min(0).tolist(),v.max(0).tolist()]);kd=kdtree.KDTree(len(v))
  for i,p in enumerate(v):kd.insert(Vector(p),i)
  kd.balance();ds=[kd.find(Vector(p))[2]for p in baseline['wings']['anchor_points']];ck('Original bearing anchors remain unmoved',bool(ds)and max(ds)<=2e-6,anchor_count=len(ds),maximum_distance_m=max(ds)if ds else None);ck('Ceramic material and UV retained',all(m.name in baseline['materials']for m in wing.data.materials)and bool(wing.data.uv_layers))
 sc.frame_set(was);bpy.context.view_layer.update();fail=[c for c in checks if not c['pass']];out={'status':'PASS_V24_FRESH_BLEND_QA'if not fail else'FAIL_V24_FRESH_BLEND_QA','checks':checks,'failures':fail,'panels':panelrows,'existing_materials_checked':len(baseline['materials']),'existing_images_checked':len(baseline['images']),'door_roots_checked':len(baseline['doors']),'allowed_old_geometry_changes':sorted(ALLOWED),'final_material_override_allowed':False};p=Path(output_dir);p.mkdir(parents=True,exist_ok=True);(p/'V24_Fresh_Blend_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],len(checks),len(fail),flush=True)
 if fail:raise AssertionError('V24 QA failed: '+', '.join(r['check']for r in fail[:12]))
 return out
