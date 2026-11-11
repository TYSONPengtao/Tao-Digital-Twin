import bpy,json,math
from pathlib import Path
OUT=Path(r'E:\jz\JIA\Rebuild_V4');results={}
for mode in ['ARCH','VIS']:
 results[mode]={}
 for ext in ['obj','fbx','glb']:
  bpy.ops.wm.read_factory_settings(use_empty=True);p=OUT/'08_Export'/f'Production_1QK_{mode}.{ext}'
  if ext=='obj':bpy.ops.wm.obj_import(filepath=str(p),forward_axis='Y',up_axis='Z')
  elif ext=='fbx':bpy.ops.import_scene.fbx(filepath=str(p))
  else:bpy.ops.import_scene.gltf(filepath=str(p))
  bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];doors=[o for o in meshes if 'DOOR_BED_F1_X3.9' in o.name]
  assert doors,'Known door parts were lost';points=[o.matrix_world@v.co for o in doors for v in o.data.vertices];axis=1 if ext=='fbx' else 2;width=max(p[axis] for p in points)-min(p[axis] for p in points)
  # glTF is Y-up. Blender imports it back into Z-up, so the known door is again along local Y.
  if ext in ['glb','obj']:width=max(p[1] for p in points)-min(p[1] for p in points)
  assert abs(width-.9)<1e-5,(ext,width)
  invalid=[];degenerate=0
  for o in meshes:
   if any(not all(math.isfinite(z) for z in v.co) for v in o.data.vertices):invalid.append(o.name)
   degenerate+=sum(p.area<1e-10 for p in o.data.polygons)
  results[mode][ext]={'file':str(p),'import_success':True,'mesh_objects':len(meshes),'unique_meshes':len(set(o.data.name for o in meshes)),'empty_hierarchy_nodes':sum(o.type=='EMPTY' for o in bpy.context.scene.objects),'cameras':sum(o.type=='CAMERA' for o in bpy.context.scene.objects),'known_door_width_m':float(width),'invalid_coordinates':invalid,'degenerate_faces':degenerate,'uv_missing_objects':sum(not len(o.data.uv_layers) for o in meshes),'material_slot_missing_objects':sum(not len(o.data.materials) for o in meshes),'complete_site_present':all(any(key in o.name for o in meshes) for key in ['SITE_MAIN_COURTYARD_PAVING','SITE_KITCHEN','SITE_PERIMETER_JOINED_RETAINING_WALL','SITE_CURVED_PUBLIC_ROAD'])}
  results[mode][ext]['photo_corrected_site_present']=all(any(key in o.name for o in meshes) for key in ['SITE_SW_METAL_ENTRY_GATE','SITE_SOUTH_SCREENWALL_RAISED_BODY','SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS','SITE_INNER_STONE_GATEHOUSE'])
  results[mode][ext]['obsolete_false_gate_absent']=not any('SITE_OUTER_ENTRY_PORTAL' in o.name or 'SITE_ENTRY_RAMP' in o.name for o in meshes)
  print('READBACK',mode,ext,results[mode][ext],flush=True)
(OUT/'09_Report/Exchange_Readback_QA.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
