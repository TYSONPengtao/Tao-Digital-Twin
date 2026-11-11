import bpy,sys,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_09_common import *
from v24_09_roof import build_roof
from v24_09_facade import materials,deform_crown,clear_screen_frames,panels,inner_plaster
for n in['Blender','Reports','Source','References']:(O/n).mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;base=snapshot(bpy);write('V24_09_Before_Snapshot.json',base);sc.frame_set(40);bpy.context.view_layer.update()
col=bpy.data.collections.new('V24_09_照壁分叉瓦顶与曲面叠涩');sc.collection.children.link(col);palette,trim,lime,field=materials();roof=build_roof(col,palette,trim,W);write('V24_09_Forked_Roof.json',roof);print('FORK ROOF BUILT',roof['wing_terminal_count'],roof['hip_fan_cover_tile_units'],flush=True)
crown=deform_crown();clear=clear_screen_frames();facade=panels(col,trim,field,W);plaster=inner_plaster(lime);write('V24_09_Facade_and_Soffit.json',{'crown':crown,'retired_frames':clear,'facade':facade,'plaster':plaster});print('CURVED SOFFIT AND PANELS BUILT',flush=True)
for n,pos,tar,lens,ortho in [('V24_09_Outside',(7.025,-29,3.3),(7.025,-17.05,2.7),42,10.3),('V24_09_Inside',(7.025,-12.8,2.0),(7.025,-16.9,2.7),14,None),('V24_09_Fork_Plan',(7.025,-16.9,14),(7.025,-16.9,3.9),45,10),('V24_09_Fork_Oblique',(13.5,-24.2,8.3),(7.025,-16.9,3.65),42,None),('V24_09_Underside',(14.8,-19.2,3.15),(10.25,-16.9,4.0),38,None),('V24_09_Whole_Site',(28,-32,18),(5,-7,1.3),47,None)]:
 c=bpy.data.objects.new(n,bpy.data.cameras.new(n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
sc.camera=bpy.data.objects['V24_09_Fork_Oblique'];sc.frame_set(40);sc['Version']='V24_09_SCREENWALL_FORKED_HIPS_AND_CURVED_SOFFIT'
guide='V24.09照壁：按135801俯视图明确长脊两端各分叉成前后两条斜脊，共四条分叉脊、四个翘角，撤去原端部中央直立锥形脊饰。端部补横向扇铺瓦面，长坡密排筒板瓦、通透菱格及圆环脊带、莲花瓦当。仰视底部为连续闭合曲面承托、三道薄叠涩与封檐，端面有白色框内芯；内外各七组长短框，内面白灰墙作适度风化。原墙平面、场地边界、下部基础不变，只在照壁两端上部墙冠随屋底收口。厨房0.45m退让、门楼3.10m檐底和26扇门动画保留。照片拟合的瓦件、脊饰和线脚尺寸不作为现场实测值。默认40帧开门，1帧关闭、20帧半开。'
(O/'README_V24_09.txt').write_text(guide,encoding='utf-8-sig');t=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide)
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.overlay.show_overlays=False;a.spaces.active.shading.type='MATERIAL';a.spaces.active.region_3d.view_perspective='CAMERA'
after=snapshot(bpy);changed=[n for n,r in base['objects'].items()if n in after['objects']and r!=after['objects'][n]];added=sorted(set(after['objects'])-set(base['objects']));removed=sorted(set(base['objects'])-set(after['objects']));allowed=set(roof['changed_objects']+[r['name']for r in crown]+[clear['name']]);assert set(changed)<=allowed,sorted(set(changed)-allowed)
write('V24_09_Changes.json',{'changed_objects':changed,'added_objects':added,'removed_objects':removed,'allowed_objects':sorted(allowed),'expected_mesh_hashes':{n:after['objects'][n]['mesh_hash']for n in changed+added if after['objects'][n]['mesh_hash']},'roof':roof,'crown':crown,'facade':facade,'plaster':plaster});bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_09_Build.json',{'status':'SAVED','model':str(P),'sha256':sha(P),'source_sha256':sha(B),'changed_count':len(changed),'added_count':len(added)});print('V24.09 SAVED',len(changed),len(added),flush=True)
