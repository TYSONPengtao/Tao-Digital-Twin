from pathlib import Path
import bpy, json, sys, hashlib, numpy as np, re
from mathutils import Vector
W=Path(__file__).parent; D=W/'v26'; D.mkdir(exist_ok=True)
sys.path.insert(0,str(W))
from v24_06_common import snapshot
P=Path('E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend')
bpy.ops.wm.open_mainfile(filepath=str(P)); sc=bpy.context.scene
sc.frame_set(40); bpy.context.view_layer.update()
print('OPEN',bpy.app.version_string,len(bpy.data.objects),flush=True)
baseline=snapshot(bpy); (D/'Before_Snapshot.json').write_text(json.dumps(baseline,ensure_ascii=False),encoding='utf8')
sc.frame_set(40); bpy.context.view_layer.update()
rows=[]; exports=[]
terms=['STAIR','LANDING','KZ_','KL_','LL_','BEAM','COLUMN','SLAB','PARTITIONS_JOINED','FACADE_CONTINUOUS','WALL','GROUND','RAMP','COURTYARD','GATE','PAD','FOUNDATION','FOOTING','PLINTH']
for o in bpy.data.objects:
    pts=[o.matrix_world@Vector(p) for p in o.bound_box] if o.type=='MESH' else []
    row={'name':o.name,'type':o.type,'matrix':[list(r) for r in o.matrix_world], 'parent':o.parent.name if o.parent else None,
         'bounds':[[min(p[k] for p in pts) for k in range(3)],[max(p[k] for p in pts) for k in range(3)]] if pts else None,
         'hidden':o.hide_get(),'hide_render':o.hide_render,'collections':[c.name for c in o.users_collection],
         'props':{k:str(v) for k,v in o.items() if k not in ['_RNA_UI']},
         'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []}
    if o.type=='MESH':
        row.update(vertices=len(o.data.vertices),polygons=len(o.data.polygons),material_faces={str(k):int(v) for k,v in zip(*np.unique(np.array([p.material_index for p in o.data.polygons]),return_counts=True))})
    rows.append(row)
    if o.type!='MESH' or o.hide_render or not any(t in o.name.upper() for t in terms) or any(t in o.name for t in ['Roam','Collision','MEASURE','V24_21_Person','V24_21_Camera']):continue
    me=o.data; me.calc_loop_triangles()
    v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64)
    f=np.array([t.vertices[:] for t in me.loop_triangles],dtype=np.int32)
    mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32)
    uv=np.array([[me.uv_layers.active.data[i].uv[:] for i in t.loops] for t in me.loop_triangles],np.float32) if me.uv_layers.active else np.zeros((len(f),3,2),np.float32)
    fn='GEOM_'+str(len(exports))+'.npz'; np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
    exports.append(dict(row,file=fn,triangles=len(f)))
    print('GEOM',o.name,len(f),np.round(row['bounds'],3).tolist(),flush=True)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8')
(D/'Geometry_Index.json').write_text(json.dumps(exports,ensure_ascii=False),encoding='utf8')
with P.open('rb') as fp: h=hashlib.file_digest(fp,'sha256').hexdigest()
(D/'Base.json').write_text(json.dumps({'source':str(P),'sha256':h,'bytes':P.stat().st_size,'blender':bpy.app.version_string,'units':sc.unit_settings.system,'scale_length':sc.unit_settings.scale_length,'objects':len(rows),'exports':len(exports)},indent=2),encoding='utf8')
print('PROBE_DONE',len(exports),h,flush=True)
