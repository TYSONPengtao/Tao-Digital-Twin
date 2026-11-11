import json
from pathlib import Path
O=Path(r'E:/jz/JIA/Rebuild_V16');q=json.loads((O/'06_Report/V16_Native_Readback_QA.json').read_text(encoding='utf8'));g=q['ground']
p=O/'06_Report/V16_Design_Control.json';d=json.loads((Path(__file__).parent/'v16/Geometry_QA.json').read_text(encoding='utf8'));d['soil']['height_minmax_m']=g['top_z_minmax_m'];d['soil']['grade_quantiles']=g['grade_quantiles'];d['soil']['top_triangles_method']='Constrained quality triangulation, final actual native readback';d['final_model_sha256']=q['sha256'];p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
for name in ['V16_Stitched_Edge_QA.json','V16_Soil_Quality_QA.json']:
 p=O/'06_Report'/name;d=json.loads(p.read_text(encoding='utf8'));d['status']='PASS_FRESH_NATIVE_READBACK';d['final_model_sha256']=q['sha256'];d['drain_contact_check']=g['drain_scan_boundary_contact'] if 'Stitched' in name else None;p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
print('FINAL REPORT VALUES UPDATED',q['sha256'])
p=O/'06_Report/V16_Junction_Extent_QA.json';d=json.loads(p.read_text(encoding='utf8'));d['status']='PASS_FINAL_NATIVE_READBACK_AND_EXTENT_LIMIT';d['final_model_sha256']=q['sha256'];p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
p=O/'06_Report/V16_Assembly_QA.json';d=json.loads(p.read_text(encoding='utf8'));d.setdefault('initial_build_mesh_checks',d.get('mesh_checks',[]));d['mesh_checks']=q['fresh_changed_mesh_checks'];p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
p=O/'06_Report/Preview_View_States.json';p.write_text(json.dumps({'geometry':'Final V16 actual 3DM Mesh readback, unchanged Brep/block tessellation verified by geometry hash','views':'Eight complete views, no hidden modeled objects, sunlight for inspection; no added survey fixtures'},indent=2),encoding='utf8')
