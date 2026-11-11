"""V24 Blender-native gate refinement; retain all real materials and site."""
import bpy,json,sys,hashlib,shutil,faulthandler
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_relief_blender import apply_v24_relief
from v24_sculpt_blender import apply_v24_sculpt
from v24_qa_blender import baseline_snapshot
faulthandler.enable();faulthandler.dump_traceback_later(60,repeat=True)
O=Path('E:/jz/JIA/Rebuild_V24');B=Path('E:/jz/JIA/Rebuild_V23/05_Export/Actual_Rhino_V23_Readback_LOCAL.blend');P=O/'Blender/Architecture_Complete_V24.blend'
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
base=baseline_snapshot(bpy);(O/'Reports/Baseline_V23_Snapshot.json').write_text(json.dumps(base,ensure_ascii=False,indent=2),encoding='utf8');print('BASELINE CAPTURED',len(base['objects']),flush=True)
for material in bpy.data.materials:material.use_fake_user=True
for image in bpy.data.images:
 if image.source!='VIEWER' and image.type not in ['RENDER_RESULT','COMPOSITING']:image.use_fake_user=True
for action in bpy.data.actions:action.use_fake_user=True
relief=apply_v24_relief(bpy,O/'Textures/Gate_Carving_HeightAtlas.png',O/'Reports')
sculpt=apply_v24_sculpt(bpy,O/'Reports');print('SCULPT COMPLETE',sculpt['base_sculpt_vertices'],flush=True)
edit=bpy.data.collections.new('V24_内大门_雕刻编辑');sc.collection.children.link(edit)
for ob in bpy.data.objects:
 if ob.name.startswith(('SITE_V21_GATE_REFERENCE','SITE_V20_INNER_GATE','SITE_V15_INNER_GATE_HANGING','GATE_V22_','GATE_V23_','V24_Gate_')):
  if ob.name not in edit.objects:edit.objects.link(ob)
old=bpy.data.collections.get('ACTUAL_RHINO_V23_READBACK')
if old:old.name='V24_现场建筑_完整基地'
source=bpy.data.objects['V23_Inner_Gate_Ideal_Compare'];cam=source.copy();cam.data=source.data.copy();cam.name='V24_Inner_Gate_Real_Materials';sc.collection.objects.link(cam);sc.camera=cam
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.region_3d.view_perspective='CAMERA'
guide='''V24：Blender 内大门灰度浮雕与局部雕刻

从 V24 起只制作和交付 Blender 模型。完整基地沿用 V23 紧凑屋檐版本，原有实景材质、纹理、门轴和动画保持。
内大门新增12块柱面/折角面、3块门楣实体浮雕。灰度图以实际顶点位移实现，非仅凹凸着色；源图已打包。
选择 V24_内大门_雕刻编辑 集合中的 V24_Gate_Reference_Relief_* 可继续在 Sculpt 模式雕刻。Multires 1级可编辑；禁用的 Displace 仅保存源图索引，基础网格已带浮雕，直接再启用会叠加位移。
四处翼角采用焊接、局部倒角、密集细分、平滑/微膨胀雕刻核，承托锚点保持，轮廓未扩大。不是人工逐笔雕刻或实物扫描。
原有107个材质和73张图像保持；灰度图为独立 Non-Color 高度参考，不替换石材颜色。主场景保持真实配色，未用白模材质覆盖。
门默认完全打开（40帧）；1到40帧保留原有26扇门的内开/推拉动画。预览采用20帧局部开启以展示门板，文件默认40帧。
灰度纹样由内置 image_gen 参考用户理想图生成，属于图像拟合构图，不是石刻测绘。提示词与布局见 Source 和 Textures。
单位：LOCAL 米，原坐标关系沿用 V23。本轮不生成 Rhino/GLB，不声称已完成 UE 运行验证。
'''
text=bpy.data.texts.new('V24_使用说明');text.write(guide);(O/'README_V24.txt').write_text(guide,encoding='utf-8-sig')
layout=(O/'Textures/Gate_Carving_HeightAtlas_Layout.json').read_text(encoding='utf8');t=bpy.data.texts.new('V24_灰度图UV布局');t.write(layout)
sc['Version']='V24_BLENDER_NATIVE';sc['Delivery']='Blender only, original real materials retained';sc['V24_Baseline_Blend_SHA256']=hashlib.file_digest(B.open('rb'),'sha256').hexdigest();sc['V24_Gray_Reference_Method']='Packed reference atlas -> actual dense relief mesh -> editable Multires';sc['V24_No_Rhino_Export']=True
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
active=bpy.data.objects.get('V24_Gate_Reference_Relief_P1_front_2')
if active:active.select_set(True);bpy.context.view_layer.objects.active=active
for layer in sc.view_layers:assert layer.material_override is None
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
(O/'Reports/V24_Build.json').write_text(json.dumps({'model':str(P),'baseline':str(B),'version':'V24','blender_version':bpy.app.version_string,'relief_panels':relief['panel_count'],'sculpt':sculpt,'original_materials_retained':True,'rhino_exported':False,'glb_exported':False,'model_sha256':hashlib.file_digest(P.open('rb'),'sha256').hexdigest()},ensure_ascii=False,indent=2),encoding='utf8')
print('V24 BLEND SAVED',P.stat().st_size,flush=True)
