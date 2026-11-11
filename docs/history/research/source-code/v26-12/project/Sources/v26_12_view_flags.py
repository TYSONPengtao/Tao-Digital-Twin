import bpy,json
from pathlib import Path
P=Path('E:/jz/JIA/Rebuild_V26_12/Blender/Architecture_Complete_V26_12_Fast.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();rows=[]
names=['V26_10_Inner_Gate_Rectangular_Stone_Piers','V24_Gate_Waist_Carving_Retained']+[o.name for o in sc.objects if o.name.startswith('V26_12_Restored_')][:4]
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type!='VIEW_3D':continue
   r={'screen':screen.name,'local_view':str(space.local_view),'use_local_collections':space.use_local_collections,'local_collections_uuid':getattr(space,'local_collections_uuid',None),'shading':space.shading.type,'objects':[]}
   for name in names:
    o=bpy.data.objects[name];r['objects'].append({'name':name,'visible':o.visible_get(),'viewport_visible':o.visible_get(viewport=space),'local_view_get':o.local_view_get(space)if space.local_view else None,'display_type':o.display_type,'show_instancer_for_viewport':o.show_instancer_for_viewport,'hide_viewport':o.hide_viewport,'hide_get':o.hide_get()})
   rows.append(r)
report={'screens':rows,'materials':[{a:getattr(m,a,None)for a in['name','use_nodes','use_backface_culling','surface_render_method','diffuse_color']}for m in bpy.data.materials if m.name=='M_V21_GATE_REF_04']}
for r in report['materials']:
 if r['diffuse_color']is not None:r['diffuse_color']=list(r['diffuse_color'])
Path(__file__).with_name('v26_12').joinpath('Viewport_Flags_Diagnosis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=False),flush=True)
