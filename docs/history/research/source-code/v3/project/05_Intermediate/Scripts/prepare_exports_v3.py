from pathlib import Path
W=Path(__file__).parent
for a,b in [('export_v2.py','export_v3.py'),('rhino_validate_v2.py','rhino_validate_v3.py'),('blender_v2.py','blender_v3.py'),('geometry_qa_v2.py','geometry_qa_v3.py'),('default_site_view.py','default_site_view_v3.py'),('check_exchange_v2.py','check_exchange_v3.py'),('repair_exchange_v2.py','repair_exchange_v3.py'),('v2_plan_preview.py','v3_plan_preview.py')]:
 s=(W/a).read_text(encoding='utf-8').replace('Rebuild_V2','Rebuild_V3').replace('export_v2','export_v3').replace('Geometry_QA_V2','Geometry_QA_V3').replace('V2_Orthographic','V3_Orthographic')
 if b=='blender_v3.py':s=s.replace("'CAM_08_Junction','CAM_01_Entrance'","'CAM_08_Junction','CAM_01_Entrance','CAM_09_SW_Gate','CAM_10_Screenwall','CAM_11_Chinese_Kitchen','CAM_12_Inner_Gate'")
 if b=='check_exchange_v3.py':s=s.replace("any('SITE_PERIMETER_JOINED_RETAINING_WALL' in n for n in names)","any('SITE_PERIMETER_JOINED_RETAINING_WALL' in n for n in names)")
 (W/b).write_text(s,encoding='utf-8')
print('V3 exporters ready')
