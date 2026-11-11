from pathlib import Path
import bpy,numpy as np,json,sys,hashlib,math
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_8';BASE=Path('E:/jz/JIA/Rebuild_V26_7');SRC=BASE/'Blender/Architecture_Complete_V26_7.blend';O=Path('E:/jz/JIA/Rebuild_V26_8');P=O/'Blender/Architecture_Complete_V26_8.blend';R=O/'Reports'
for p in [P.parent,R,O/'Roam',O/'Sources',O/'References']:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(W));from v24_06_common import snapshot
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),'utf8')
assert sha(SRC)=='ae36eb7abde8241465d4d6707fa19c8a9ccd74aaebc025565f2843ee9be5711e'
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
if not(D/'Before_Snapshot.json').exists():(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));changed=[];added=[];geom=[]
for r in prep['objects']:
 n=r['name'];a=np.load(D/r['file']);o=bpy.data.objects.get(n)
 if o is None:
  o=bpy.data.objects.new(n,bpy.data.meshes.new(n));sc.collection.objects.link(o);added.append(n)
 smooth=bool(r.get('smooth_wood'))or any(p.use_smooth for p in o.data.polygons)
 iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V26_8');me.from_pydata([iv@Vector(v)for v in a['v']],[],a['f'])
 for m in r['materials']:me.materials.append(bpy.data.materials[m])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_8_Preserved_Source_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True
 if smooth:
  me.polygons.foreach_set('use_smooth',np.ones(len(me.polygons),bool))
  if r.get('smooth_wood'):me.set_sharp_from_angle(angle=math.radians(38))
 me.update();o.data=me;o['V26_8_Repair']=r['reason'];changed.append(n);geom.append(n);print('INSTALLED',n,len(a['f']),flush=True)
archived=prep.get('remove',[])
for n in archived:
 o=bpy.data.objects[n];o.hide_render=True;o.hide_set(True);changed.append(n)
# Collision cache rebuilt from current visible native changed meshes only.
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();cv=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in old.loop_triangles],np.int32);ix=json.loads((BASE/'Reports/V26_7_Collision_Index.json').read_text('utf8'))['objects'];need=set(geom);vv=[];ff=[];ci=[];off=0;first=0
def append(v,f,n,kind):
 global off,first
 vv.append(v);ff.append(f+off);ci.append({'name':n,'first_triangle':first,'triangles':len(f),'source':kind});off+=len(v);first+=len(f)
for r in ix:
 if r['name']in need or r['name']in archived:continue
 fs=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,rev=np.unique(fs.ravel(),return_inverse=True);append(cv[used],rev.reshape(-1,3),r['name'],'Unchanged V26.6 actual native surface')
for n in sorted(need):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();append(np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles],np.int32),n,'V26.7 saved current native surface')
me=bpy.data.meshes.new('V26_8_Current_Geometry_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);write('V26_8_Collision_Index.json',{'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True})
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string().replace('Rebuild_V26_7','Rebuild_V26_8').replace('Architecture_Complete_V26_7.blend','Architecture_Complete_V26_8.blend');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code);(O/'Roam'/fn).write_text(code,'utf8')
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('Rebuild_V26_7','Rebuild_V26_8').replace('Architecture_Complete_V26_7.blend','Architecture_Complete_V26_8.blend'),'utf8')

# The user asked for overcast, soft and even display lighting.
world=bpy.data.worlds.new('V26_8_Overcast_Soft_Even_Daylight');world.use_nodes=True
ns=world.node_tree.nodes;ns.clear();bg=ns.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.78,.79,.80,1.);bg.inputs['Strength'].default_value=.75;out=ns.new('ShaderNodeOutputWorld');world.node_tree.links.new(bg.outputs['Background'],out.inputs['Surface']);sc.world=world
light_rows=[]
for o in list(sc.objects):
 if o.type!='LIGHT':continue
 changed.append(o.name);prior=o.data.energy
 if o.data.type=='SUN':o.data.energy=0.;o.data.angle=1.2
 elif o.data.type=='POINT':o.data.energy=min(o.data.energy,100.);o.data.shadow_soft_size=1.4
 elif o.data.type=='AREA':o.data.size=max(getattr(o.data,'size',1.),2.5)
 light_rows.append({'object':o.name,'type':o.data.type,'before_energy':prior,'after_energy':o.data.energy})
for fl,z in[(1,-.45),(2,3.45),(3,7.05)]:
 for part,x,y in[('left',2.,5.),('hall',6.5,5.),('right',11.,5.),('stair',6.,8.5)]:
  ld=bpy.data.lights.new(f'V26_8_Overcast_Interior_F{fl}_{part}','AREA');ld.energy=90 if part!='stair'else 55;ld.shape='DISK';ld.size=2.8
  ob=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(ob);ob.location=(x,y,z+2.82);added.append(ob.name);changed.append(ob.name)
sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.preview_samples=16
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium Low Contrast';sc.view_settings.exposure=0.;sc.view_settings.gamma=1.
spaces=0
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type!='VIEW_3D':continue
  shade=ar.spaces.active.shading;shade.type='MATERIAL';shade.use_scene_world=True;shade.use_scene_lights=True;shade.studiolight_background_alpha=1.;shade.studiolight_background_blur=1.;spaces+=1
write('V26_8_Overcast_Lighting_Setup.json',{'world':world.name,'uniform_neutral_ambient_strength':.75,'direct_sun_energy':0,'light_changes':light_rows,'soft_interior_area_lights':12,'area_diameter_m':2.8,'material_preview_scene_world':True,'material_preview_scene_lights':True,'configured_spaces':spaces,'color_transform':'AgX - Medium Low Contrast','lighting_is_user_display_preference_not_measured_site_light':True})

sc['Version']='V26_8_Stair_Well_And_User_Confirmed_Window_Sills_Overcast';sc['V26_8_Source_SHA256']=sha(SRC)
t=bpy.data.texts.new('V26_8_实景与截图修正');t.write('按最新130324实景收窄中央梯井，净宽约100mm为照片与模型关系拟合，非现场测量；四跑接实际墙面，原踏步X/Z及两个平台标高保留。扶手恢复较小回弯、中心转角柱和顺直握柄，去除加宽回弯及额外颈环。一楼湾窗台按用户给定30cm，二三楼湾窗台与原二楼石扶手相对等高；按用户确认移除三层全部15件误加铁栏，35个窗/玻璃/活动扇配合。门边白垛收窄且给原窗框独立收口。普通墙不超过240mm，原后部高窗、门窗开合、次照壁、门槛与入口坡保留。按用户要求保存中性阴天柔光显示设置，关闭直射太阳。')
write('V26_8_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(set(changed)),'geometry_changed':geom,'added':added,'archived':archived,'wall_limit_m':.24,'wall_corner_exception':True,'specific_repair_proof':prep['proof'],'original_secondary_11':'Geometry transforms UVs materials and visibility retained exactly; only explicitly wrong lower site base finish is wrapped to matching strata','no_rhino_export':True})
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_8_Build.json',{'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string});print('V26_8_SAVED',sha(P),flush=True)
