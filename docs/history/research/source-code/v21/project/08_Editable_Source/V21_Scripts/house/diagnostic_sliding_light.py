import bpy,json,math
from pathlib import Path
from mathutils import Vector
D=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V21/05_Export/Actual_Rhino_V21_Readback_LOCAL.blend')
sc=bpy.context.scene;sc.camera=bpy.data.objects['V21_House_Sliding_Entry'];c=sc.camera
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();vf=c.data.view_frame(scene=sc);di=c.matrix_world.to_3x3()@Vector([0,0,vf[0].z]);di.normalize();hit,loc,no,fi,ob,ma=sc.ray_cast(dep,c.location,di)
r={'center_hit':ob.name,'position':list(loc),'normal':list(no),'material':ob.data.materials[ob.data.polygons[fi].material_index].name,'lights':[],'material_nodes':[]}
mat=ob.data.materials[ob.data.polygons[fi].material_index]
for n in mat.node_tree.nodes:
 r['material_nodes'].append({'type':n.type,'name':n.name,'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__iter__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and i.name in ['Base Color','Roughness','Emission Color','Emission Strength']}})
for l in bpy.data.objects:
 if l.type=='LIGHT':
  r['lights'].append({'name':l.name,'energy':l.data.energy,'location':list(l.location),'center_hit_distance':(l.location-loc).length})
  if l.name in ['V20_INSPECTION_F1_Hall','V20_INSPECTION_F1_Rear']:l.data.energy=60
(D/'F1_Light_Diagnosis.json').write_text(json.dumps(r,indent=2))
sc.render.resolution_x=1100;sc.render.resolution_y=760;sc.render.resolution_percentage=100;sc.cycles.samples=10;sc.cycles.use_denoising=True
sc.render.filepath=str(D/'review_sliding_entry_60w.png');bpy.ops.render.render(write_still=True)
