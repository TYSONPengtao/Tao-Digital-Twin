from pathlib import Path
import bpy,sys,json,hashlib
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_3_views import VIEWS
after='--after'in sys.argv;cycles='--material-preview'in sys.argv;args=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[]
P=Path('E:/jz/JIA/Rebuild_V26_3/Blender/Architecture_Complete_V26_3.blend')if after else Path('E:/jz/JIA/Rebuild_V26_2/Blender/Architecture_Complete_V26_2.blend');R=W/'v26_3'/'Review';R.mkdir(parents=True,exist_ok=True)
original='--original-secondary'in sys.argv
if original:P=Path('E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='CYCLES'if cycles else'BLENDER_WORKBENCH';sc.render.resolution_x=1200;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard'
probe='--no-bump-probe'in sys.argv
emission_probe='--emission-probe'in sys.argv
photo_probe='--brick-photo-probe'in sys.argv
group_probe='--brick-group-probe'in sys.argv
if group_probe:
 nt=bpy.data.materials['M_V26_3_Secondary_Original_Brick_Explicit_UV'].node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');g=nt.nodes.new('ShaderNodeGroup');g.node_tree=bpy.data.node_groups['V26_2_Arc_Blue_Brick_Photo'];nt.links.new(g.outputs['Shader'],out.inputs['Surface'])
if photo_probe:
 me=bpy.data.objects['V26_2_Continuous_Ground_And_Perimeter_Shell'].data
 for k,mat in enumerate(me.materials):
  if mat.name=='M_V26_3_Secondary_Original_Brick_Explicit_UV':me.materials[k]=bpy.data.materials['M_V24_20_Shared_AsBuilt_Perimeter_Brick']
if emission_probe:
 nt=bpy.data.materials['M_V26_3_Secondary_Original_Brick_Explicit_UV'].node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(1.,1.,1.,1.);em.inputs['Strength'].default_value=1.;nt.links.new(em.outputs[0],out.inputs['Surface'])
if probe:
 mat=bpy.data.materials['M_V26_3_Secondary_Original_Brick_Explicit_UV'];nt=mat.node_tree
 for nd in nt.nodes:
  if nd.type=='BSDF_PRINCIPLED':
   for link in list(nd.inputs['Normal'].links):nt.links.remove(link)
with P.open('rb')as fp:modelhash=hashlib.file_digest(fp,'sha256').hexdigest()
if not cycles:
 sh=sc.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=False;sh.show_specular_highlight=True;sh.background_type='WORLD';sc.world.color=(.12,.12,.12);sc.display.render_aa='16'
else:
 sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.view_settings.view_transform='AgX'
 try:
  p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
  for d in p.devices:d.use=d.type=='OPTIX'
  sc.cycles.device='GPU'
 except Exception:pass
for tag,pos,aim,lens in VIEWS:
 if args and tag not in args:continue
 c=bpy.data.objects.new('Review_'+tag,bpy.data.cameras.new('Review_'+tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=600;sc.camera=c
 light=None
 if cycles and not tag.startswith('08_'):
  ld=bpy.data.lights.new('Temporary_Review_Fill','AREA');ld.energy=75;ld.shape='DISK';ld.size=2.;light=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(light);light.location=c.location;light.rotation_euler=c.rotation_euler
 fn=('Probe_Group_'if group_probe else'Probe_Photo_'if photo_probe else'Probe_Emission_'if emission_probe else'Probe_NoBump_'if probe else'')+('Original_'if original else'After_'if after else'Before_')+tag+('_Cycles'if cycles else'_Solid')+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True)
 ray=[];frame=c.data.view_frame(scene=sc);xmin=min(p.x for p in frame);xmax=max(p.x for p in frame);ymin=min(p.y for p in frame);ymax=max(p.y for p in frame)
 for u,v in[(.5,.2),(.3,.4),(.5,.5),(.7,.5),(.5,.8)]:
  direction=c.matrix_world.to_3x3()@Vector((xmin+u*(xmax-xmin),ymax-v*(ymax-ymin),frame[0].z));direction.normalize();hit,point,normal,face,o,mat=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,direction)
  if hit:
   p=o.data.polygons[face];ma=o.data.materials[p.material_index];ray.append({'uv':[u,v],'object':o.name,'face':face,'p':list(point),'n':list(normal),'material':ma.name,'diffuse':list(ma.diffuse_color)})
 (R/(fn[:-4]+'.json')).write_text(json.dumps({'model':str(P),'model_sha256':modelhash,'camera':[pos,aim,lens],'hits':ray,'temporary_review_fill_W':75 if light else 0,'saved_file_unchanged':True},ensure_ascii=False,indent=2),encoding='utf8');print('REVIEW_DONE',fn,ray,flush=True)
 if light:bpy.data.objects.remove(light,do_unlink=True)
 bpy.data.objects.remove(c,do_unlink=True)
