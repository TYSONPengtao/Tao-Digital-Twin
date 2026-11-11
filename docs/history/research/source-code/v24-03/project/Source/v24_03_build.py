"""Assemble native Blender xieshan roof and measured junction corrections."""
import bpy,json,sys,hashlib,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W))
import v24_qa_blender as q
from v24_xieshan_roof_blender import apply_v24_xieshan_roof
from v24_03_junction_blender import apply_v24_03_junction
from v24_03_kitchen_fix import apply_v24_03_kitchen_fix
O=Path('E:/jz/JIA/Rebuild_V24_03');R=O/'Reports';B=Path('E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend');P=O/'Blender/Architecture_Complete_V24_03.blend'
for n in ['Blender','Reports','Source','Textures','References']:(O/n).mkdir(parents=True,exist_ok=True)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def snapshot():
 obs={}
 for ob in bpy.data.objects:obs[ob.name]={'type':ob.type,'matrix':q._matrix(ob.matrix_world),'parent':ob.parent.name if ob.parent else None,'mesh_hash':q._mesh_hash(ob.data) if ob.type=='MESH' else None,'animation':q._animation(ob),'hide_render':ob.hide_render}
 doors=sorted(ob.name for ob in bpy.data.objects if ob.get('UE_Interaction') in ['HINGED_INWARD','SLIDING']);poses={}
 for f in [1,20,40]:
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update();poses[str(f)]={n:q._matrix(bpy.data.objects[n].matrix_world) for n in doors}
 bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
 return {'objects':obs,'materials':{m.name:q._material(m) for m in bpy.data.materials},'images':{im.name:q._image(im) for im in bpy.data.images if im.source!='VIEWER' and im.type not in ['RENDER_RESULT','COMPOSITING']},'actions':{a.name:q._action(a) for a in bpy.data.actions},'doors':doors,'door_poses':poses}
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
before=snapshot();(R/'V24_03_Before_Snapshot.json').write_text(json.dumps(before,ensure_ascii=False,indent=2),encoding='utf8');print('SOURCE SNAPSHOT',len(before['objects']),flush=True)
kitchen=apply_v24_03_kitchen_fix(bpy,R);print('KITCHEN REAR AND SINGLE POST COMPLETE',flush=True)
roof=apply_v24_xieshan_roof(bpy,R);print('XIESHAN MODULE COMPLETE',flush=True)
junction=apply_v24_03_junction(bpy,R);print('JUNCTION MODULE COMPLETE',flush=True)
after=snapshot();changes=[];removed=[]
for n,old in before['objects'].items():
 if n not in after['objects']:removed.append(n)
 elif after['objects'][n]!=old:changes.append(n)
added=sorted(set(after['objects'])-set(before['objects']))
expected={n:q._mesh_hash(bpy.data.objects[n].data) for n in sorted(set(changes+added)) if n in bpy.data.objects and bpy.data.objects[n].type=='MESH'}
(R/'V24_03_Changes.json').write_text(json.dumps({'changed_old_objects':changes,'removed_objects':removed,'added_objects':added,'expected_mesh_hashes':expected,'module_reports':{'roof':roof,'junction':junction,'kitchen':kitchen}},ensure_ascii=False,indent=2),encoding='utf8')
for m in bpy.data.materials:m.use_fake_user=True
for im in bpy.data.images:
 if im.source!='VIEWER' and im.type not in ['RENDER_RESULT','COMPOSITING']:im.use_fake_user=True
sc['Version']='V24_03_BLENDER_XIESHAN';sc['Source_SHA256']=sha(B);sc['Delivery']='Blender; retained real materials; gate hip-and-gable roof'
guide='''V24.03：内大门歇山屋顶及两侧交接修正

主模型：Blender/Architecture_Complete_V24_03.blend，完整基地，LOCAL 米。
内大门屋顶重做为歇山结构：上部主坡、端部山花、下部四面披檐及转角脊，檐下按照片补连续层叠承接。厨房与内院围墙端部按新屋顶修正收口，保留石柱斜面及雕花。
保留实景材质、灰度源图形成的15块实体浮雕、26扇门的内开/推拉动画。默认40帧完全开启，1–40帧可查看门扇动作。
尺寸参考及配准结论见 Reports/V24_03_Dimension_Audit.md；造型细节按照片拟合。
灰度图为独立Non-Color高度参考；基础网格已有位移，禁用的Displace仅保存源图索引。浮雕可在Multires上继续雕刻。
Source包含本轮建模与校验脚本，Textures包含灰度源图，References包含用户实景图。未在UE项目内运行验证。
'''
(O/'README_V24_03.txt').write_text(guide,encoding='utf-8-sig');t=bpy.data.texts.get('V24_使用说明') or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide)
sc.frame_set(40);bpy.context.view_layer.update()
if bpy.data.objects.get('V23_Gate_Roof_Oblique'):sc.camera=bpy.data.objects['V23_Gate_Roof_Oblique']
for layer in sc.view_layers:assert layer.material_override is None
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
(R/'V24_03_Build.json').write_text(json.dumps({'status':'SAVED_V24_03','model':str(P),'model_sha256':sha(P),'source':str(B),'source_sha256':sha(B),'roof':roof,'junction':junction,'blender_version':bpy.app.version_string},ensure_ascii=False,indent=2),encoding='utf8');print('V24.03 SAVED',P.stat().st_size,flush=True)
