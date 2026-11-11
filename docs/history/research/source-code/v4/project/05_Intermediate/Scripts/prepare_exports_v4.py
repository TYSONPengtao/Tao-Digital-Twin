from pathlib import Path
W=Path(__file__).parent
for old,new in [('export_v3.py','export_v4.py'),('rhino_validate_v3.py','rhino_validate_v4.py'),('default_site_view_v3.py','default_site_view_v4.py'),('geometry_qa_v3.py','geometry_qa_v4.py'),('blender_v3.py','blender_v4.py'),('repair_exchange_v3.py','repair_exchange_v4.py'),('check_exchange_v3.py','check_exchange_v4.py'),('package_v3.py','package_v4.py')]:
 t=(W/old).read_text(encoding='utf-8-sig').replace('Rebuild_V3','Rebuild_V4').replace('export_v3','export_v4').replace('Geometry_QA_V3','Geometry_QA_V4').replace('Production_1QK_Rebuild_V3','Production_1QK_Rebuild_V4')
 if new=='blender_v4.py':
  a=t.index(' for camera_name in ');b=t.index(' bpy.ops.wm.save_as_mainfile',a)
  t=t[:a]+''' for camera_name in (['CAM_02_Front'] if mode=='ARCH' else ['CAM_02_Front','CAM_06_Whole_Site','CAM_07_Column','CAM_08_Junction','CAM_10_Screenwall','CAM_11_Chinese_Kitchen','CAM_12_Inner_Gate','CAM_13_Stair_Coordination','CAM_14_Roof_Drainage']):
  hidden=[]
  if camera_name=='CAM_13_Stair_Coordination':
   for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and not ob.hide_render and (ob.get('Layer') in ['10_WALL_EXT','11_WALL_INT','20_COLUMN','21_BEAM','50_ROOF','51_CANOPY','31_WINDOW','30_DOOR','41_RAILING'] and not ob.get('Element','').startswith(('STAIR','RAIL_STAIR')) or ob.get('Element','').startswith(('SLAB_JOINED_','CONSTRUCTION_TERRACE','TERRACE','ROOF_'))):
     hidden.append(ob);ob.hide_render=True
  bpy.context.scene.camera=bpy.data.objects[camera_name];bpy.context.scene.render.filepath=str(OUT/'09_Report'/f'{mode}_{camera_name}.png');bpy.ops.render.render(write_still=True)
  for ob in hidden:ob.hide_render=False
''' +t[b:]
 (W/new).write_text(t,encoding='utf-8')
print('Prepared eight V4 export/check scripts')
