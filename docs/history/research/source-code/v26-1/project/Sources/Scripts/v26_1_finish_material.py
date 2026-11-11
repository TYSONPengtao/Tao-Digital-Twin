from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_1';O=Path('E:/jz/JIA/Rebuild_V26_1');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_1.blend';bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.preferences.filepaths.save_version=0
# The source material expects normalized photo UVs; the continuous wall
# carries metre-valued arc-length UVs. Normalize once, wrap horizontally, and
# fit the photographed stone course to its actual 480mm display band.
g=bpy.data.node_groups['V26_1_Source_M_V19_Perimeter_Dark_Stone'];ns=g.nodes;ls=g.links;uv=ns.new('ShaderNodeTexCoord');sep=ns.new('ShaderNodeSeparateXYZ');ls.new(uv.outputs['UV'],sep.inputs[0]);u=ns.new('ShaderNodeMath');u.operation='DIVIDE';u.inputs[1].default_value=3.6;ls.new(sep.outputs['X'],u.inputs[0]);wrap=ns.new('ShaderNodeMath');wrap.operation='PINGPONG';wrap.inputs[1].default_value=1.;ls.new(u.outputs[0],wrap.inputs[0]);geo=ns.new('ShaderNodeNewGeometry');z=ns.new('ShaderNodeSeparateXYZ');ls.new(geo.outputs['Position'],z.inputs[0]);offset=ns.new('ShaderNodeMath');offset.operation='ADD';offset.inputs[1].default_value=.68;ls.new(z.outputs['Z'],offset.inputs[0]);v=ns.new('ShaderNodeMath');v.operation='DIVIDE';v.inputs[1].default_value=.48;ls.new(offset.outputs[0],v.inputs[0]);comb=ns.new('ShaderNodeCombineXYZ');ls.new(wrap.outputs[0],comb.inputs['X']);ls.new(v.outputs[0],comb.inputs['Y'])
for node in list(ns):
 if node.type=='TEX_IMAGE':node.extension='EXTEND';ls.new(comb.outputs[0],node.inputs['Vector'])
g['V26_1_Photo_Repeat_Width_Metres']=3.6;g['V26_1_Fitted_Band_Height_Metres']=.48
views=json.loads((D/'Views.json').read_text('utf8'));row=next(r for r in views if r[0].startswith('09_'));row[1]=[13.45,4.0,.9];row[2]=[14.12,5.,-.35];row[3]=20;c=bpy.data.objects['V26_1_'+row[0]];c.location=row[1];c.rotation_euler=(Vector(row[2])-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=row[3];(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8');bpy.context.scene.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
b=json.loads((R/'V26_1_Build.json').read_text('utf8'));b.update(sha256=h,bytes=P.stat().st_size,wall_photo_uv_normalized=True);(R/'V26_1_Build.json').write_text(json.dumps(b,indent=2),encoding='utf8');ch=json.loads((R/'V26_1_Changes.json').read_text('utf8'));ch['final_visual_repairs'].append('Normalize the dark-stone photo UV to the continuous arc-length wall UV; no material clipping or vertical smear');(R/'V26_1_Changes.json').write_text(json.dumps(ch,ensure_ascii=False,indent=2),encoding='utf8');print('MATERIAL_FINAL_SAVED',h,flush=True)
