"""Package only the final Blender file, current reports, sources and references."""
import json,hashlib,shutil,zipfile
from pathlib import Path
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V24');R=O/'Reports'
P=O/'Blender/Architecture_Complete_V24_02.blend'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
model_sha=sha(P);build=json.loads((R/'V24_02_Build.json').read_text(encoding='utf8'));qa=json.loads((R/'V24_02_Fresh_Blend_QA.json').read_text(encoding='utf8'));views=json.loads((R/'V24_02_Preview_States.json').read_text(encoding='utf8'))
assert build['model_sha256']==qa['model_sha256']==views['model_sha256']==model_sha
assert qa['status'].startswith('PASS') and not qa['failures']
assert qa['existing_materials_checked']==107 and qa['existing_images_checked']==73 and qa['door_roots_checked']==26
files=[P,O/'README_V24.txt']
reports=['Baseline_V23_Snapshot.json','V24_02_Build.json','V24_02_Expected_Mesh_Readback.json','V24_02_Fresh_Blend_QA.json','V24_02_Preview_States.json','V24_Gate_Relief_Geometry_QA.json','V24_Wing_Sculpt_Report.json','V24_Roof_Detail_Report.json','V24_Kitchen_Junction_Module_QA.json']
for name in reports:assert (R/name).is_file(),name;files.append(R/name)
for v in views['views']:
 p=R/v['file'];assert p.stat().st_size>10000;files.append(p)
source=O/'Source';source.mkdir(exist_ok=True)
for name in ['v24_relief_blender.py','v24_sculpt_blender.py','v24_roof_detail_blender.py','v24_kitchen_junction_blender.py','v24_qa_blender.py','v24_build_blender.py','v24_update_top.py','v24_02_verify_render.py','v24_package.py']:
 shutil.copy2(W/name,source/name)
for name in ['Reference_Review.md','Coordinate_Inventory.json']:
 src=W/'v24_junction_reference_review'/name;dest=R/('V24_02_'+name);shutil.copy2(src,dest);files.append(dest)
ref=O/'References';ref.mkdir(exist_ok=True)
for name in ['DJI_0097.JPG','DJI_0098.JPG','DJI_0099.JPG','DJI_0100.JPG','DJI_0101.JPG','DJI_0102.JPG','DJI_0103.JPG']:
 p=Path('D:/DJI/0002/DCIM/101MEDIA')/name;shutil.copy2(p,ref/name)
for original,dest in [('D:/Desktop/download.jpg','V24_02_Aerial_Roof_Context.jpg'),('D:/Desktop/屏幕截图 2026-10-16 124233.jpg','V24_02_Gate_Kitchen_Oblique.jpg'),('D:/Desktop/屏幕截图 2026-10-16 124258.jpg','V24_02_Gate_Exterior.jpg')]:shutil.copy2(original,ref/dest)
for folder in ['Textures','Source','References']:
 files.extend(p for p in (O/folder).rglob('*') if p.is_file() and p.suffix!='.pyc')
files=sorted(set(files));assert all(p.suffix.lower() not in ['.3dm','.glb','.fbx','.blend1'] for p in files)
manifest={'version':'V24.02','model':'Blender/'+P.name,'model_sha256':model_sha,'blender_only':True,'real_materials_retained':True,'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
Z=W.parent/'outputs/Production_1QK_Blender_V24_02_Gate_Top.zip';Z.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for p in files:z.write(p,Path('Rebuild_V24')/p.relative_to(O))
with zipfile.ZipFile(Z) as z:
 bad=z.testzip();assert bad is None,bad
 forbidden=[n for n in z.namelist() if Path(n).suffix.lower() in ['.3dm','.glb','.fbx','.blend1']];assert not forbidden
bundle={'status':'PASS_BLENDER_ONLY_DELIVERY','model_sha256':model_sha,'zip':str(Z),'zip_bytes':Z.stat().st_size,'zip_sha256':sha(Z),'zip_crc_verified':True,'file_count':len(files),'original_materials':107,'original_images':73,'door_roots':26,'qa_checks':len(qa['checks'])+len(qa['top_and_junction_checks'])}
(O/'Bundle_QA.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bundle,ensure_ascii=False,indent=2))
