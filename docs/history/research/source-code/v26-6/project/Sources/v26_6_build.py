from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_6';BASE=Path('E:/jz/JIA/Rebuild_V26_5');SRC=BASE/'Blender/Architecture_Complete_V26_5.blend';O=Path('E:/jz/JIA/Rebuild_V26_6');P=O/'Blender/Architecture_Complete_V26_6.blend';R=O/'Reports'
for p in [P.parent,R,O/'Roam',O/'Sources',O/'References']:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(W));from v24_06_common import snapshot
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
assert sha(SRC)=='202625cfe023a542ce75b7cbee3e05f0dee1767543a4ac7633b401d796e6c51a'
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
if not(D/'Before_Snapshot.json').exists():(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8')
sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));rows=prep['objects'];changed=[]
for r in rows:
 n=r['name'];a=np.load(D/r['file']);o=bpy.data.objects[n];iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V26_6');me.from_pydata([iv@Vector(v)for v in a['v']],[],a['f'])
 for m in r['materials']:me.materials.append(bpy.data.materials[m])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_6_Preserved_Source_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True;me.update();o.data=me;o['V26_6_Repair']=r['reason'];changed.append(n);print('INSTALLED',n,len(a['f']),flush=True)
# Rebuild only collision source ranges actually changed by this local repair.
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();cv=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in old.loop_triangles],np.int32);ix=json.loads((BASE/'Reports/V26_5_Collision_Index.json').read_text('utf8'))['objects'];need=set(changed);vv=[];ff=[];ci=[];off=0;first=0
def append(v,f,n,kind):
 global off,first
 vv.append(v);ff.append(f+off);ci.append({'name':n,'first_triangle':first,'triangles':len(f),'source':kind});off+=len(v);first+=len(f)
for r in ix:
 if r['name']in need:continue
 fs=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,rev=np.unique(fs.ravel(),return_inverse=True);append(cv[used],rev.reshape(-1,3),r['name'],'Unchanged V26.4 actual surface')
for n in sorted(need):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();append(np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles],np.int32),n,'V26.5 saved current native surface')
me=bpy.data.meshes.new('V26_6_Current_Geometry_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);write('V26_6_Collision_Index.json',{'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True})
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string().replace('Rebuild_V26_5','Rebuild_V26_6').replace('Architecture_Complete_V26_5.blend','Architecture_Complete_V26_6.blend');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code);(O/'Roam'/fn).write_text(code,encoding='utf8')
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('Rebuild_V26_5','Rebuild_V26_6').replace('Architecture_Complete_V26_5.blend','Architecture_Complete_V26_6.blend'),encoding='utf8')

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
   shade=area.spaces.active.shading;shade.type='MATERIAL';shade.studio_light='studio.exr';shade.use_scene_world=False;shade.use_scene_lights=False;spaces+=1
write('V26_6_Neutral_Preview_Setup.json',{'method':'Unchanged white paint; default Material Preview uses studio.exr instead of forest.exr. Separately packed luminance-only studio scene world supports neutral render inspection.','source_light':source_light.path,'source_sha256':sha(source_light.path),'image':env.name,'packed':bool(env.packed_file),'material_preview_uses_scene_world':False,'default_preview_hdr_is_not_strictly_achromatic':True,'configured_3d_spaces':spaces,'site_illumination_not_claimed_measured':True})
sc['Version']='V26_6_Photo_Referenced_Stair_Fronts_F3_Open_Terrace_Neutral_White_Preview';sc['V26_6_Source_SHA256']=sha(SRC)
text=bpy.data.texts.new('V26_6_实景依据与本次修正');text.write('以V26.5另存：按原INSV115、125、140、150秒楼梯实景，只将两个中平台和两个楼层到达前缘竖面改为现有灰色石纹，保留白色梯底梁底和全部原踏步高程、木扶手。按170、175、180、200、205秒三楼露台实景，去除误补的西侧窗角前填充墙，保留顶部横梁与两侧柱，下层隔墙不动；双窗头整理为白色连续收口。白色天花原材质不改，将森林环境偏色替换为内嵌灰度工作室核对光，仅用于材质颜色核对，不宣称复原现场实测照明。次照壁、普通墙厚上限240mm、原窗门玻璃、入口坡保留。')
write('V26_6_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(changed),'added':[],'archived':[],'wall_limit_m':.24,'wall_corner_exception':True,'specific_repair_proof':prep['proof'],'secondary_screenwall':'All original geometry, placement, photo mapping and source height field untouched','no_rhino_export':True})
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_6_Build.json',{'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string});print('V26_6_SAVED',sha(P),flush=True)
