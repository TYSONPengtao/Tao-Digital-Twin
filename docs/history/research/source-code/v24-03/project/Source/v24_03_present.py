import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V24_03');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_03.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene
for n,pos,tar,lens in [('V24_03_Saved_Gate_Overview',(7.1,-16.,4.8),(6.6,-11.9,2.2),24),('V24_03_Saved_Kitchen_Review',(4.7,-1.2,2.4),(8.7,-6.6,1.4),32)]:
 ob=bpy.data.objects.get(n)
 if not ob:ob=bpy.data.objects.new(n,bpy.data.cameras.new(n));sc.collection.objects.link(ob)
 ob.location=pos;ob.rotation_euler=(Vector(tar)-ob.location).to_track_quat('-Z','Y').to_euler();ob.data.lens=lens
sc.camera=bpy.data.objects['V24_03_Saved_Gate_Overview'];sc.frame_set(40)
guide='''V24.03：歇山门楼与厨房实景修正

主模型：Blender/Architecture_Complete_V24_03.blend；完整基地，LOCAL 米，保留实景材质。
门楼：上部两主坡、两端山花、四面下披檐和九脊结构，五层连续承接、封闭檐底；根据参考2号模型的配准剖面加深屋顶并恢复高度，保持收敛的檐口宽度。
厨房：后墙和屋顶下三角区域封齐；旧重复独立柱列与柱础移除，改为一根中部檐廊柱，配柱头承托和斜撑；补后部墙脚、落水管与排水沟收口。
交接：左围墙连续回接石柱侧后；厨房、木构与新门楼屋顶作有厚度的裁切收口，逐组检查三角交叉，结果见Junction报告。
原有15块灰度参考实体浮雕、107个材质和74张图像（含灰度源图）、26扇内开/推拉门动画保留。默认40帧完全开启；1–40帧可检视门扇动作。
灰度图为Non-Color高度参考，基础网格已有位移；禁用的Displace仅保留源图索引。浮雕及四角雕刻可用Multires继续编辑。
尺寸对照：参考 E:/jz/实景三维场景模型2.3dm，已核实为同院落，进行了全场参考配准。其影像重建坐标/高程与当前版本不同；配准约0.32米残差，适用于体量、屋顶剖面复核，细部接头依照照片和实际网格连接。报告保留矩阵和误差，未声称逐毫米测绘。
相机：V24_03_Saved_Gate_Overview、V24_03_Saved_Kitchen_Review。Source含脚本与灰度提示词，References含实景对照。
未在真实UE项目中运行验证。
'''
(O/'README_V24_03.txt').write_text(guide,encoding='utf-8-sig');tx=bpy.data.texts.get('V24_使用说明') or bpy.data.texts.new('V24_使用说明');tx.clear();tx.write(guide)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
build=json.loads((R/'V24_03_Build.json').read_text(encoding='utf8'))
with P.open('rb') as f:build['model_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(R/'V24_03_Build.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf8');print('V24.03 PRESENTATION SAVED',flush=True)
