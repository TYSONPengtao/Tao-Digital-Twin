"""V24.02: local Blender roof and kitchen-gable refinement, incrementally from V24."""
import bpy,json,sys,hashlib,shutil,time
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_roof_detail_blender import apply_v24_roof_detail
from v24_kitchen_junction_blender import apply_v24_kitchen_junction
from v24_qa_blender import _mesh_hash
O=Path('E:/jz/JIA/Rebuild_V24');P=O/'Blender/Architecture_Complete_V24_02.blend'
B=O/'Blender/Architecture_Complete_V24.blend'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
source_sha=sha(B);original_names=set(bpy.data.objects.keys());print('V24.02 BASE LOADED',source_sha,flush=True)
roof=apply_v24_roof_detail(bpy,O/'Reports');print('ROOF UPDATE COMPLETE',flush=True)
junction=apply_v24_kitchen_junction(bpy,O/'Reports');print('KITCHEN JUNCTION UPDATE COMPLETE',flush=True)
collection=bpy.data.collections.get('V24_内大门_雕刻编辑')
if collection:
 for ob in bpy.data.objects:
  if ob.name.startswith(('V24_Gate_','V24_Kitchen_')) and ob.name not in collection.objects:collection.objects.link(ob)
sc['Version']='V24_02_BLENDER_NATIVE';sc['V24_02_Source_Blend_SHA256']=source_sha
sc['V24_02_Roof_Report']='Reports/V24_Roof_Detail_Report.json';sc['V24_02_Kitchen_Report']='Reports/V24_Kitchen_Junction_QA.json'
guide='''V24.02 内大门顶部及厨房山墙收口（Blender）

主模型：Blender/Architecture_Complete_V24_02.blend。完整基地和实景材质保留。
依据本轮 DJI_0097–0103 航拍、124233/124258 实景图及 download.jpg，细化内大门顶部与厨房交接；形状由照片拟合，非毫米级测绘。
内大门筒瓦搭接消除重面，增加细薄接缝、正脊透空菱花带、脊座及侧边收口；保持已收短的屋檐宽度，正脊因补入缺失花带适量抬高。
厨房端部补曲线山墙压顶和短竖脊头，修正瓦面/封檐与山墙的前后位置及门楼交接，详见独立检查报告。
V24 的 15 块灰度图实体浮雕及 4 处翼角雕刻保留；新增复杂图案以灰度图生成实际网格，独立 Multires 可继续雕刻。禁用的 Displace 仅留源图索引，基础网格已带位移，不要重复启用。
保留原有 107 个材质、73 张图像及 26 扇门的动画；灰度图仅作 Non-Color 高度参考。默认 40 帧完全开启，1–40 帧可查看内开/推拉动作。
所有预览采用原材质，不设白模材质覆盖。未在真实 UE 项目内运行验证。
本轮仅交付 Blender；灰度源图、提示词、建模脚本、检查报告及实景参考随完整包提供。
'''
(O/'README_V24.txt').write_text(guide,encoding='utf-8-sig')
t=bpy.data.texts.get('V24_使用说明') or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide)
sc.frame_set(40);bpy.context.view_layer.update()
if bpy.data.objects.get('V23_Gate_Roof_Oblique'):sc.camera=bpy.data.objects['V23_Gate_Roof_Oblique']
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_perspective='CAMERA'
for layer in sc.view_layers:assert layer.material_override is None
from v24_kitchen_junction_blender import ROOF_NODES
changed=['SITE_V21_GATE_REFERENCE_LAYER_10_Geometry','SITE_V21_GATE_REFERENCE_LAYER_14_Geometry']+[n+'_Geometry' for n in ROOF_NODES]
expected={n:_mesh_hash(bpy.data.objects[n].data) for n in (set(bpy.data.objects.keys())-original_names)|set(changed) if n in bpy.data.objects and bpy.data.objects[n].type=='MESH'}
(O/'Reports/V24_02_Expected_Mesh_Readback.json').write_text(json.dumps({'changed_old_objects':changed,'new_objects':sorted(set(bpy.data.objects.keys())-original_names),'expected_meshes':expected},ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
report={'version':'V24.02','model':str(P),'model_sha256':sha(P),'source':str(B),'source_sha256':source_sha,'blender_version':bpy.app.version_string,'roof':roof,'junction':junction,'real_materials_retained':True,'rhino_exported':False,'glb_exported':False}
(O/'Reports/V24_02_Build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('V24.02 SAVED',P.stat().st_size,flush=True)
