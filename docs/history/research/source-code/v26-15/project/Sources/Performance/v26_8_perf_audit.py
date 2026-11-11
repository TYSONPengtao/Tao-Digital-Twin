import bpy, json, time, sys, types
from pathlib import Path
import numpy as np

D = Path(__file__).parent / 'v26_8_perf'
D.mkdir(exist_ok=True)
P = Path('E:/jz/JIA/Rebuild_V26_8/Blender/Architecture_Complete_V26_8.blend')
t = time.perf_counter()
bpy.ops.wm.open_mainfile(filepath=str(P))
sc = bpy.context.scene
load_seconds = time.perf_counter()-t

def props(x, names=None):
    out = {}
    for p in x.bl_rna.properties:
        n=p.identifier
        if n == 'rna_type' or (names and not any(k in n.lower() for k in names)): continue
        try:
            v=getattr(x,n)
            if isinstance(v,(str,int,float,bool)): out[n]=v
            elif p.type=='ENUM': out[n]={'value':str(v),'enum':[q.identifier for q in p.enum_items]}
        except Exception: pass
    return out

meshes=[]
for o in sc.objects:
    if o.type!='MESH': continue
    meshes.append({'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),
                   'visible':o.visible_get(),'hide_render':o.hide_render,
                   'modifiers':[(m.name,m.type,m.show_viewport) for m in o.modifiers]})
images=[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images]
mat_nodes={}
for mat in bpy.data.materials:
    if mat.use_nodes:
        for n in mat.node_tree.nodes: mat_nodes[n.type]=mat_nodes.get(n.type,0)+1
spaces=[]
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            spaces.append({'screen':screen.name,'shade':props(a.spaces.active.shading),
                           'space':props(a.spaces.active,['clip','show','lens'])})
report={'blender':bpy.app.version_string,'load_seconds':load_seconds,'engine':sc.render.engine,
        'render':props(sc.render,['simpl','texture','resolution','stamp']),
        'eevee':props(sc.eevee) if hasattr(sc,'eevee') else {},
        'cycles':props(sc.cycles,['sample','preview','bounc','denois']),
        'system':props(bpy.context.preferences.system,['texture','mem','pixel','gl_','vbo']),
        'spaces':spaces,'mesh_objects':len(meshes),
        'meshes_sorted':sorted(meshes,key=lambda r:r['polygons'],reverse=True),
        'images':images,'material_node_types':mat_nodes,
        'lights':[{'name':o.name,'type':o.data.type,'energy':o.data.energy,'shadow':getattr(o.data,'use_shadow',None)}
                  for o in sc.objects if o.type=='LIGHT']}

sc.frame_set(40); bpy.context.view_layer.update()
o=bpy.data.objects['V24_21_Navigation_Collision']; me=o.data; me.calc_loop_triangles()
t=time.perf_counter()
v=[o.matrix_world@p.co for p in me.vertices]
f=[t.vertices[:] for t in me.loop_triangles]
report['collision_extract_seconds']=time.perf_counter()-t
m=types.ModuleType('architecture_roam_physics'); sys.modules[m.__name__]=m
exec(compile(bpy.data.texts['V24_21_碰撞控制.py'].as_string(),'physics','exec'),m.__dict__)
t=time.perf_counter(); world=m.World(v,f)
report['collision_bvh_build_seconds']=time.perf_counter()-t
timings={}
for label,pos,direction in [('idle',(8.5,7.8,0.),(0,0)),('court',(6.5,-4.8,-.411),(0,1)),('stair',(7.5,9.05,-.45),(-1,0))]:
    walker=m.Walker(world,pos); elapsed=[]
    for _ in range(180):
        t=time.perf_counter(); walker.update(direction,1/60); elapsed.append((time.perf_counter()-t)*1000)
    timings[label]={'median_ms':float(np.median(elapsed)),'p95_ms':float(np.percentile(elapsed,95)), 'max_ms':max(elapsed)}
report['physics_step_ms']=timings
(D/'Audit_Before.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print('PERF_AUDIT',json.dumps({k:report[k] for k in ['load_seconds','mesh_objects','collision_extract_seconds','collision_bvh_build_seconds','physics_step_ms','eevee','render']},ensure_ascii=False),flush=True)
