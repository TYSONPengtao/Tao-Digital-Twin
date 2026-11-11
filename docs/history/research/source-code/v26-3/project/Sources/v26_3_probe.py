from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_3';D.mkdir(exist_ok=True);sys.path.insert(0,str(W))
from v24_06_common import snapshot
P=Path('E:/jz/JIA/Rebuild_V26_2/Blender/Architecture_Complete_V26_2.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update()
def sha(p):
 with Path(p).open('rb')as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
def dump(o,fn):
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32)
 uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2))
 np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
 return {'name':o.name,'file':fn,'materials':[m.name if m else None for m in me.materials],'bounds':[v.min(0).tolist(),v.max(0).tolist()],'triangles':len(f),'hidden':o.hide_get(),'hide_render':o.hide_render,'collections':[c.name for c in o.users_collection],'matrix':[list(p)for p in o.matrix_world]}
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH'and(o.name.startswith(('KZ_','BEAM_','FACADE_CONTINUOUS','PARTITIONS_JOINED','SLAB_JOINED','ROOF_','STAIR_F','STAIR_LANDING','UTILITY_FLAT'))or'Secondary'in o.name or 'TRANSOM'in o.name or o.name=='V26_2_House_Flush_Continuous_Finished_Shell'):
  rows.append(dump(o,'PROBE_'+str(len(rows))+'.npz'))
(D/'Components.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8')
materials={}
for m in bpy.data.materials:
 if m.name in ['M_Concrete','M_Wall_Interior','M_Floor','M_V24_31_White_Painted_Ceiling']:
  materials[m.name]={'diffuse':list(m.diffuse_color),'nodes':[(n.type,n.inputs['Base Color'].default_value[:])for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED']if m.use_nodes else[]}
(D/'Material_Diagnostics.json').write_text(json.dumps(materials,ensure_ascii=False,indent=2),encoding='utf8')
(D/'Base.json').write_text(json.dumps({'model':str(P),'sha256':sha(P),'blender':bpy.app.version_string}),encoding='utf8')
print('CURRENT_COMPONENTS',len(rows),'MATERIALS',materials,flush=True)
orig=Path('E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend');bpy.ops.wm.open_mainfile(filepath=str(orig));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();old=[]
for o in bpy.data.objects:
 if o.type=='MESH'and'Secondary_Screenwall'in o.name:
  old.append(dump(o,'ORIGINAL_SECONDARY_'+str(len(old))+'.npz'))
(D/'Original_Secondary.json').write_text(json.dumps({'source':str(orig),'sha256':sha(orig),'objects':old},ensure_ascii=False,indent=2),encoding='utf8')
print('ORIGINAL_SECONDARY',len(old),[(r['name'],r['hidden'],r['hide_render'])for r in old],flush=True)
