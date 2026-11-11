import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
O=Path(__file__).parent;D=json.loads((O/'Preview_Data.json').read_bytes());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for n,spec in D['materials'].items():
 m=bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=[(c/255/12.92 if c/255<=.04045 else ((c/255+.055)/1.055)**2.4) for c in spec['color']]+[1];p.inputs['Roughness'].default_value=spec.get('roughness',.5)
 if spec.get('alpha',1)<.5:p.inputs['Alpha'].default_value=spec['alpha']
 if 'WOOD' in n.upper() or 'TIMBER' in n.upper():
  t=m.node_tree.nodes.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=3;t.inputs['Detail'].default_value=4
  tc=m.node_tree.nodes.new('ShaderNodeTexCoord');vm=m.node_tree.nodes.new('ShaderNodeVectorMath');vm.operation='MULTIPLY';vm.inputs[1].default_value=(.65,60,60);m.node_tree.links.new(tc.outputs['Generated'],vm.inputs[0]);m.node_tree.links.new(vm.outputs['Vector'],t.inputs['Vector']);bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.012;m.node_tree.links.new(t.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 mats[n]=m
groups={}
for p in D['parts']:
 k=(p['node'],p['material']);v,f=groups.setdefault(k,([],[]));off=len(v);v.extend(p['vertices']);f.extend([[j+off for j in q] for q in p['faces']])
for (n,m),(v,f) in groups.items():
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(v,[],f);mesh.update();ob=bpy.data.objects.new(n,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(mats[m])
bpy.ops.mesh.primitive_plane_add(size=200,location=(10,-7,-.60));floor=bpy.context.object;floor.name='Display_Backdrop';mat=bpy.data.materials.new('BG');mat.diffuse_color=(.46,.46,.43,1);floor.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1400;scene.render.resolution_y=980;scene.render.resolution_percentage=100;scene.world.color=(.55,.55,.55);scene.view_settings.view_transform='AgX'
def light(n,pos,power,size):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;ob=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((10,-7,2))-ob.location).to_track_quat('-Z','Y').to_euler()
light('Main',(2,-16,15),1700,10);light('Fill',(14,-3,13),1100,7);light('Facade',(0,-6,4),750,6)
def camera(loc,target,ortho=None):
 bpy.ops.object.camera_add(location=loc);ob=bpy.context.object;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();ob.data.lens=23
 if ortho:ob.data.type='ORTHO';ob.data.ortho_scale=ortho
 scene.camera=ob
interior_only='interior_only' in sys.argv
if not interior_only:
 camera((-4,-20,8.7),(9.7,-7.1,1.7),15);scene.render.filepath=str(O/'Kitchen_V12_Complete.png');bpy.ops.render.render(write_still=True)
for ob in bpy.data.objects:
 if ob.name.startswith(('SITE_KITCHEN_CHINESE_TILE','SITE_KITCHEN_RIDGE','SITE_KITCHEN_GREY','SITE_KITCHEN_V11_VISIBLE','SITE_KITCHEN_V11_REGISTERED','SITE_KITCHEN_FASCIA','SITE_KITCHEN_VISIBLE_EDGE','SITE_KITCHEN_GATE_UNDERLAP','SITE_KITCHEN_VISIBLE_SHEATHING')):ob.hide_render=True
floor.hide_render=True
if not interior_only:
 camera((4.9,-15,1.10),(10.7,-6.7,3.1),14);scene.render.filepath=str(O/'Kitchen_V12_Exposed_Timber.png');bpy.ops.render.render(write_still=True)
scene.render.resolution_x=1400;scene.render.resolution_y=1100
if not interior_only:
 camera((6.9,-10.74,1.20),(9.01,-10.74,1.20),2.20);scene.render.filepath=str(O/'Kitchen_V12_Double_Octagon_Window_Detail.png');bpy.ops.render.render(write_still=True)
 camera((6.9,-7.10,1.64),(9.06,-7.10,1.64),2.65);scene.render.filepath=str(O/'Kitchen_V12_Door_Pair_Detail.png');bpy.ops.render.render(write_still=True)
light('Interior',(12,-7,3.1),400,5)
for ob in bpy.data.objects:
 if ob.name.startswith(('SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS','SITE_KITCHEN_V12_LONGITUDINAL_ROUND_PURLINS','SITE_KITCHEN_V12_RIDGE_UNDER_TIMBER_BEAM','SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES','SITE_KITCHEN_V12_BEFORE_WOOD_04')):ob.hide_render=True
camera((10.8,-7.65,2.37),(9.06,-7.65,2.37),3.10);scene.render.filepath=str(O/'Kitchen_V12_Two_Fret_Levels_Detail.png');bpy.ops.render.render(write_still=True)
camera((11.1,-7.10,2.06),(9.06,-7.10,2.06),8.80);scene.render.resolution_x=1700;scene.render.resolution_y=980;scene.render.filepath=str(O/'Kitchen_V12_Interior_Facade_Relation.png');bpy.ops.render.render(write_still=True)
for ob in bpy.data.objects:ob.hide_render=False
camera((13.0,-9.70,1.30),(9.06,-7.10,2.55));scene.camera.data.lens=17;scene.render.filepath=str(O/'Kitchen_V12_Interior_Complete.png');bpy.ops.render.render(write_still=True)
print('Kitchen seven previews rendered',flush=True)
