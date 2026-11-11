from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_35';D.mkdir(exist_ok=True);sys.path.insert(0,str(W));from v24_06_common import snapshot
P=Path('E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();before=snapshot(bpy);(D/'Before_Snapshot.json').write_text(json.dumps(before,ensure_ascii=False),encoding='utf8')
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Source.json').write_text(json.dumps({'model':str(P),'sha256':h}),encoding='utf8');rows=[]
for o in bpy.data.objects:
 if o.type!='MESH'or o.hide_render:continue
 me=o.data;v=np.empty(len(me.vertices)*3,dtype=np.float64);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);M=np.array(o.matrix_world);v=v@M[:3,:3].T+M[:3,3]
 if not len(v):continue
 lo=v.min(0);hi=v.max(0);photo='ORIGINAL_EXTERIOR_'in o.name or o.name.startswith('V24_34_MB7_')
 hit=all(hi>np.array([7.,-18.,.1]))and all(lo<np.array([23.,0.,6.]))
 native=any(k in o.name.upper()for k in ['KITCHEN','CONNECTED_KITCHEN_STORAGE_MASONRY','STORAGE_STONE_BASE'])
 if not hit or not(photo or native):continue
 me.calc_loop_triangles();f=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',f);f=f.reshape(-1,3);mi=np.array([t.material_index for t in me.loop_triangles],np.int32);uv=None
 if me.uv_layers.active:
  u=np.empty(len(me.loops)*2,dtype=np.float64);me.uv_layers.active.data.foreach_get('uv',u);u=u.reshape(-1,2);uv=u[np.array([t.loops for t in me.loop_triangles])]
 fn='SRC_'+str(len(rows))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv if uv is not None else np.zeros((len(f),3,2)));rows.append({'name':o.name,'photo':photo,'file':fn,'bounds':[lo.tolist(),hi.tolist()],'vertices':len(v),'triangles':len(f),'materials':[m.name if m else None for m in me.materials]})
(D/'Region_Index.json').write_text(json.dumps(rows,indent=2));print('PROBE',len(rows),'photo',sum(x['photo']for x in rows),flush=True)
sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=True;sc.render.resolution_x=1500;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.exposure=-.5
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
views=[('01_Kitchen_East',(26.,-13.5,4.4),(13.8,-7.5,1.5),35),('02_Kitchen_East_Close',(23.,-9.,3.2),(14.,-7.,1.5),32),('03_Kitchen_South_Join',(23.,-19.,5.),(14.5,-10.,1.6),32)]
for name,pos,aim,lens in views:
 c=bpy.data.objects.new('PROBE_'+name,bpy.data.cameras.new('PROBE_'+name));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300.;sc.camera=c;sc.render.filepath=str(D/('Before_'+name+'.png'));bpy.ops.render.render(write_still=True);print('PROBE_VIEW',name,flush=True)
(D/'Views.json').write_text(json.dumps(views),encoding='utf8')
