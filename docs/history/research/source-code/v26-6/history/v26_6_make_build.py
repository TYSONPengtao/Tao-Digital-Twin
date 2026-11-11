from pathlib import Path
W=Path(__file__).parent
code=(W/'v26_5_build.py').read_text('utf8').replace('v26_5','v26_6').replace('V26_5','V26_6').replace('V26_4','V26_5')
code=code.replace('c5f5465eea815fa3c3545855b25036629ed2a5ceda091ac6f2c6850fd4b81663','202625cfe023a542ce75b7cbee3e05f0dee1767543a4ac7633b401d796e6c51a')
start=code.index("sc['Version']=");end=code.index("write('V26_6_Changes.json'",start)
extra="""
# Preserve every original material. The packed studio environment is converted
# to luminance in the WORLD graph so white paint is not tinted by forest soil.
source_light=next(s for s in bpy.context.preferences.studio_lights if s.name=='studio.exr' and s.type=='WORLD')
env=bpy.data.images.load(source_light.path,check_existing=False);env.name='V26_6_Packed_Studio_Inspection_Environment';env.pack()
world=bpy.data.worlds.new('V26_6_Neutral_Colour_Inspection_World');world.use_nodes=True;ns=world.node_tree.nodes;ns.clear();lk=world.node_tree.links
tex=ns.new('ShaderNodeTexEnvironment');tex.image=env;bw=ns.new('ShaderNodeRGBToBW');background=ns.new('ShaderNodeBackground');background.inputs['Strength'].default_value=1.;output=ns.new('ShaderNodeOutputWorld');lk.new(tex.outputs['Color'],bw.inputs['Color']);lk.new(bw.outputs['Val'],background.inputs['Color']);lk.new(background.outputs['Background'],output.inputs['Surface']);sc.world=world
spaces=0
for work in bpy.data.workspaces:
 for screen in work.screens:
  for area in screen.areas:
   if area.type!='VIEW_3D':continue
   shade=area.spaces.active.shading;shade.type='MATERIAL';shade.studio_light='studio.exr';shade.use_scene_world=True;shade.use_scene_lights=False;spaces+=1
write('V26_6_Neutral_Preview_Setup.json',{'method':'Unchanged white paint; packed studio environment through RGB to luminance in scene world','source_light':source_light.path,'source_sha256':sha(source_light.path),'image':env.name,'packed':bool(env.packed_file),'material_preview_uses_scene_world':True,'configured_3d_spaces':spaces,'site_illumination_not_claimed_measured':True})
sc['Version']='V26_6_Photo_Referenced_Stair_Fronts_F3_Open_Terrace_Neutral_White_Preview';sc['V26_6_Source_SHA256']=sha(SRC)
text=bpy.data.texts.new('V26_6_实景依据与本次修正');text.write('以V26.5另存：按原INSV115、125、140、150秒楼梯实景，只将两个中平台和两个楼层到达前缘竖面改为现有灰色石纹，保留白色梯底梁底和全部原踏步高程、木扶手。按170、175、180、200、205秒三楼露台实景，去除误补的西侧窗角前填充墙，保留顶部横梁与两侧柱，下层隔墙不动；双窗头整理为白色连续收口。白色天花原材质不改，将森林环境偏色替换为内嵌灰度工作室核对光，仅用于材质颜色核对，不宣称复原现场实测照明。次照壁、普通墙厚上限240mm、原窗门玻璃、入口坡保留。')
"""
code=code[:start]+extra+code[end:]
(W/'v26_6_build.py').write_text(code,encoding='utf8')
for suffix in ['readback','protection_qa','geometry_qa','physics_qa','overlap_after','overlap_gate']:
 code=(W/f'v26_5_{suffix}.py').read_text('utf8').replace('v26_5','v26_6').replace('V26_5','V26_6')
 if suffix=='readback':code=code.replace('V26.4 source remains byte identical','V26.5 source remains byte identical')
 (W/f'v26_6_{suffix}.py').write_text(code,encoding='utf8')
print('V26_6_BUILD_AND_CHECKS_READY')
