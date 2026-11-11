import bpy,json,sys,math,bmesh
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).parent));from v24_06_common import P
from v24_03_junction_blender import _bounds,_closed_stats
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;out={'objects':{},'poses':{}}
names=[o.name for o in bpy.data.objects if o.type=='MESH'and(o.name.startswith('SITE_V20_INNER_GATE')or o.name.startswith('SITE_V21_GATE_REFERENCE')or('GATE_V22_'in o.name and any(w in o.name for w in['WOOD','TIMBER','FIXED'])))];sc.frame_set(1);bpy.context.view_layer.update()
for n in names:
 o=bpy.data.objects[n];r={'bounds':_bounds(o),'matrix':list(map(list,o.matrix_world)),'parent':o.parent.name if o.parent else None,'props':{k:str(o[k])for k in o.keys()},'materials':[m.name for m in o.data.materials]};out['objects'][n]=r
 if n.startswith('SITE_V20_INNER_GATE')or'FIXED_TIMBER_TRANSOM'in n:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);remain=set(bm.verts);parts=[]
  while remain:
   vs={remain.pop()};stack=list(vs)
   while stack:
    for e in stack.pop().link_edges:
     for v in e.verts:
      if v in remain:remain.remove(v);vs.add(v);stack.append(v)
   p=[o.matrix_world@v.co for v in vs];fs={f for v in vs for f in v.link_faces};parts.append({'vertices':len(vs),'faces':len(fs),'bounds':[[min(v[i]for v in p)for i in range(3)],[max(v[i]for v in p)for i in range(3)]],'materials':sorted({f.material_index for f in fs})})
  bm.free();r['parts']=sorted(parts,key=lambda r:-r['vertices'])
for f in[1,20,40]:
 sc.frame_set(f);bpy.context.view_layer.update();out['poses'][str(f)]={n:{'bounds':_bounds(bpy.data.objects[n]),'matrix':list(map(list,bpy.data.objects[n].matrix_world))}for n in names if n.startswith('SITE_V20_INNER_GATE')}
sc.frame_set(40);sc.render.resolution_x=1440;sc.render.resolution_y=1080;sc.render.resolution_percentage=100;c=bpy.data.objects.new('Probe_Camera',bpy.data.cameras.new('Probe_Camera'));sc.collection.objects.link(c);c.location=(10.8,-18.2,7.2);c.rotation_euler=(Vector((6.9,-11.582,3.2))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=45;sc.camera=c;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();frame=c.data.view_frame(scene=sc);out['pixels']=[]
for x,y in [(971,650),(981,641),(951,670),(951,676),(955,662),(967,646)]:
 u=x/1440;v=1-y/1080;ll=Vector((min(p.x for p in frame),min(p.y for p in frame),frame[0].z));rr=Vector((max(p.x for p in frame),max(p.y for p in frame),frame[0].z));loc=Vector((ll.x+u*(rr.x-ll.x),ll.y+v*(rr.y-ll.y),ll.z));direction=(c.matrix_world.to_3x3()@loc).normalized();h=sc.ray_cast(deps,c.location,direction)
 out['pixels'].append({'xy':[x,y],'object':h[4].name if h[0]else None,'location':tuple(h[1])if h[0]else None})
out['coping']=[]
for o in bpy.data.objects:
 if o.name not in ['V24_Kitchen_Curved_Gable_Coping','V24_Kitchen_Thin_Dark_Coping_Edge']:continue
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  if 8.3<p.x<9.3 and -12<p.y<-11:
   uv=world_to_camera_view(sc,c,p);out['coping'].append({'xyz':tuple(p),'screen_xy':[uv.x*1440,(1-uv.y)*1080]})
p=Path(__file__).parent/'v24_07_probe.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('PROBE',p,out['pixels'],flush=True)
