from pathlib import Path
import shutil,json
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V5')
for name in ['export','geometry_qa','rhino_validate','default_site_view','repair_exchange','check_exchange']:
 s=(W/f'{name}_v4.py').read_text(encoding='utf-8').replace('Rebuild_V4','Rebuild_V5').replace('export_v4','export_v5').replace('Geometry_QA_V4','Geometry_QA_V5')
 if name=='repair_exchange':s=s.replace('bake_anim=False,','bake_anim=False,use_custom_props=True,').replace("export_cameras=True)","export_cameras=True,export_extras=True)")
 (W/f'{name}_v5.py').write_text(s,encoding='utf-8')
s=(W/'blender_v4.py').read_text(encoding='utf-8').replace('Rebuild_V4','Rebuild_V5')
s=s.replace("e=elem.get(fields[1]) if len(fields)>2 else None", "e=elem.get('__'.join(fields[1:-1])) if len(fields)>2 else None")
s=s.replace("group[k]=str(e.get(k,''))", "group[k]=str(e.get(k,''))\n    for k in ['door_id','role','parent_id','interaction','swing_status']:group[k]=str(e.get(k,''))\n    group['Parameters']=json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False)")
s=s.replace('bake_anim=False,','bake_anim=False,use_custom_props=True,').replace('export_cameras=True)','export_cameras=True,export_extras=True)')
# Only changed interiors and one whole-site preview need re-rendering.
a=s.index(' for camera_name in (');b=s.index(' bpy.ops.wm.save_as_mainfile',a)
s=s[:a]+''' for camera_name in (['CAM_02_Front'] if mode=='ARCH' else ['CAM_06_Whole_Site']):
  bpy.context.scene.camera=bpy.data.objects[camera_name];bpy.context.scene.render.filepath=str(OUT/'09_Report'/f'{mode}_{camera_name}.png');bpy.ops.render.render(write_still=True)
 bpy.context.scene.camera=bpy.data.objects['CAM_06_Whole_Site']
'''+s[b:]
s=s.replace('cycles.samples=24','cycles.samples=16').replace('resolution_x=1600','resolution_x=1400').replace('resolution_y=1000','resolution_y=900')
(W/'blender_v5.py').write_text(s,encoding='utf-8')
shutil.copytree(W/'v5_video_plan',O/'12_Video_Layout_Evidence',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.py'))
sd=O/'05_Intermediate/Scripts';sd.mkdir(exist_ok=True)
for n in ['build_scene_v5','export_v5','geometry_qa_v5','rhino_validate_v5','blender_v5','default_site_view_v5','repair_exchange_v5','check_exchange_v5']:
 shutil.copy2(W/(n+'.py'),sd/(n+'.py'))
print('V5 export scripts and visual evidence prepared')
