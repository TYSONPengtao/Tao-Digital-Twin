import bpy, json, numpy as np, sys, hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent
D=W/'v26_12';D.mkdir(exist_ok=True)
paths=[('V24',Path('E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24.blend')),
       ('V26_11',Path('E:/jz/JIA/Rebuild_V26_11/Blender/Architecture_Complete_V26_11.blend')),
       ('V26_11_Fast',Path('E:/jz/JIA/Rebuild_V26_11/Blender/Architecture_Complete_V26_11_Fast.blend'))]
out={}
for version,p in paths:
 bpy.ops.wm.open_mainfile(filepath=str(p));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
 rows=[]
 for o in sc.objects:
  if not(o.name.startswith(('V24_Gate_','V26_10_Gate_','V26_11_Gate_'))or o.name in ['V26_10_Inner_Gate_Rectangular_Stone_Piers','SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_05_Geometry']):continue
  r={'name':o.name,'type':o.type,'hide_viewport':o.hide_viewport,'hide_render':o.hide_render,'hide_get':o.hide_get(),'visible_get':o.visible_get(),'display_type':o.display_type,'collections':[c.name for c in o.users_collection],'parent':o.parent.name if o.parent else None,'matrix':np.asarray(o.matrix_world).tolist(),'modifiers':[{'name':m.name,'type':m.type,'viewport':m.show_viewport,'render':m.show_render}for m in o.modifiers]}
  if o.type=='MESH':
   a=np.asarray([o.matrix_world@v.co for v in o.data.vertices]);r.update(vertices=len(a),faces=len(o.data.polygons),bounds=[a.min(0).tolist(),a.max(0).tolist()] if len(a)else None,materials=[m.name for m in o.data.materials])
  rows.append(r)
 report={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':rows,'view_layers':[l.name for l in sc.view_layers],'screens':[{'name':s.name,'shading':[a.spaces.active.shading.type for a in s.areas if a.type=='VIEW_3D']}for s in bpy.data.screens],'settings':{'engine':sc.render.engine,'simplify':sc.render.use_simplify,'simplify_subdivision':sc.render.simplify_subdivision}}
 out[version]=report
 (D/(version+'_Probe.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
 print('PROBED',version,[(o['name'],o.get('visible_get'),o.get('hide_render'))for o in rows],flush=True)
(D/'All_Probes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
