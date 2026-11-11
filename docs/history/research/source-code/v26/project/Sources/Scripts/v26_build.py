from pathlib import Path
import bpy,bmesh,numpy as np,json,sys,hashlib,shutil,time
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;D=W/'v26';O=Path('E:/jz/JIA/Rebuild_V26');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26.blend';SRC=Path('E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend')
for p in [O/'Blender',R,O/'Roam',O/'Sources'] :p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
BASE_SHA=sha(SRC)
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
col=bpy.data.collections.new('V26_原坡面与三层构件连接修正');sc.collection.children.link(col);changed=[];added=[]
struct=json.loads((D/'Prepared_Structure.json').read_text('utf8'));ramp=json.loads((D/'Prepared_Ramp.json').read_text('utf8'))

def transfer(old,v,f):
 me=old.data;me.calc_loop_triangles();ov=np.array([old.matrix_world@p.co for p in me.vertices]);of=np.array([t.vertices[:]for t in me.loop_triangles]);ot=ov[of];om=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv0=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles])if me.uv_layers.active else None
 tree=BVHTree.FromPolygons(ov,of,all_triangles=True);mi=[];uv=[]
 for tri in v[f]:
  q,no,k,dist=tree.find_nearest(Vector(tri.mean(0)))
  mi.append(int(om[k]));t=ot[k];A=t[1]-t[0];B=t[2]-t[0];d00=A@A;d01=A@B;d11=B@B;det=d00*d11-d01*d01
  if uv0 is not None and abs(det)>1e-15:
   Q=tri-t[0];d20=Q@A;d21=Q@B;a=(d11*d20-d01*d21)/det;b=(d00*d21-d01*d20)/det;uv.append(uv0[k,0]+a[:,None]*(uv0[k,1]-uv0[k,0])+b[:,None]*(uv0[k,2]-uv0[k,0]))
  else:uv.append(tri[:,:2])
 return np.array(mi,np.int32),np.array(uv,np.float32)

for row in struct['objects']+ramp['objects']:
 n=row['name'];a=np.load(D/row['file']);v=a['v'];f=a['f'];old=bpy.data.objects.get(n);mats=[bpy.data.materials[m]for m in row['materials']]
 if 'uv'in a:mi=a['mi']if'mi'in a else np.zeros(len(f),np.int32);uv=a['uv']
 elif old is not None and len(mats)>1:mi,uv=transfer(old,v,f)
 else:mi=np.zeros(len(f),np.int32);uv=v[f][:,:,:2].astype(np.float32)
 me=bpy.data.meshes.new('V26_'+n);inv=old.matrix_world.inverted()if old is not None else None;local=[inv@Vector(p)for p in v]if inv else v;me.from_pydata(local,[],f)
 for m in mats:me.materials.append(m)
 me.polygons.foreach_set('material_index',mi);layer=me.uv_layers.new(name='Original_Photo_UV'if'Original_Site_Entrance_Ramp'in n else'V26_Preserved_Metre_UV');layer.data.foreach_set('uv',uv.ravel());me.update()
 if old is None:
  o=bpy.data.objects.new(n,me);col.objects.link(o);added.append(n)
 else:o=old;o.data=me;changed.append(n)
 o['V26_Repair']=row.get('reason',row.get('photo_geometry','Finite solid bearing geometry'));o['V26_Source_Model_SHA256']=BASE_SHA
 if'Original_Site_Entrance_Ramp'in n:
  o['Source_3dm']=ramp['proof']['original_source'];o['Source_3dm_SHA256']=ramp['proof']['original_source_sha256'];o['Original_Source_Object_ID']=row['source_id'];o['Original_Photo_Bytes_SHA256']=row['source_texture_sha256'];o['Original_Geometry_Height_Unchanged']=True
 if n.startswith('KZ_') and o.parent and 'Parameters'in o.parent:
  params=json.loads(o.parent['Parameters']);params['V26_actual_core_section_m']=[.4,.4];params['V26_frame_joint_continuity']='core retained through slab; original grid and 400mm section restored';o.parent['Parameters']=json.dumps(params,ensure_ascii=False);changed.append(o.parent.name)
 print('INSTALLED',n,len(f),flush=True)

# Repaint the actual inward faces. Do not add a second coplanar surface and
# do not modify the material shared by outward blue-brick faces.
segs=json.loads((W/'v16/Drain_Segments.json').read_text('utf8'));rs=[r for r in segs if not(r['ci']==0 and r['j']in[60,61])];a=np.array([r['a']for r in rs]);d=np.array([r['b']for r in rs])-a;ll=np.einsum('ij,ij->i',d,d);tangent=d/np.sqrt(ll)[:,None];norm=np.c_[tangent[:,1],-tangent[:,0]];hint=np.array([r['outer_a']for r in rs])-a;norm*=np.where(np.einsum('ij,ij->i',norm,hint)>0,1,-1)[:,None]
white=bpy.data.materials['M_V24_11_Plain_White_Limewash'];paint=[]
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_1_Geometry','SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry','V24_28_Continuous_White_Courtyard_Wall_Face']:
 o=bpy.data.objects[n];me=o.data.copy();o.data=me;idx=next((i for i,m in enumerate(me.materials)if m==white),len(me.materials))
 if idx==len(me.materials):me.materials.append(white)
 count=0;area=0.
 for p in me.polygons:
  c=o.matrix_world@p.center;no=(o.matrix_world.to_3x3()@p.normal).normalized();tt=np.clip(np.einsum('ij,ij->i',np.array(c[:2])-a,d)/ll,0,1);j=int(np.argmin(np.linalg.norm(a+d*tt[:,None]-np.array(c[:2]),axis=1)))
  if abs(no.z)<.4 and np.dot(np.array(no[:2]),norm[j])<-.15:
   p.material_index=idx;count+=1;area+=p.area
 me.update();paint.append({'object':n,'inward_white_faces':count,'inward_white_face_area_m2':area,'outside_material_unchanged':True});changed.append(n);o['V26_Inner_Courtyard_White_Limewash']=True
write('V26_White_Inside_Faces.json',paint)

# Rebuild collision from the saved architectural source list and the actual
# repaired meshes. Preserve the existing exterior coverage and safe walker.
native_index=json.loads(Path('E:/jz/JIA/Rebuild_V24_33/Reports/V24_33_Collision_Index.json').read_text('utf8'))['objects'];names={r['name']for r in native_index};names.update(added);names.discard('V26_Original_Ramp_Concrete_Back_And_Sides');vv=[];ff=[];ci=[]
def append_mesh(o,me=None):
 me=me or o.data;me.calc_loop_triangles();start=len(vv);vv.extend(tuple(o.matrix_world@p.co)for p in me.vertices);ff.extend(tuple(start+i for i in t.vertices)for t in me.loop_triangles);ci.append({'name':o.name,'triangles':len(me.loop_triangles),'first_triangle':len(ff)-len(me.loop_triangles)})
for n in sorted(names):
 o=bpy.data.objects.get(n)
 if o is None or o.type!='MESH' or o.hide_render:continue
 append_mesh(o)
architecture_faces=len(ff)
external=[o for o in bpy.data.objects if o.type=='MESH'and not o.hide_render and ('ORIGINAL_EXTERIOR_'in o.name or o.name.startswith('V24_34_MB7_'))]
deps=bpy.context.evaluated_depsgraph_get()
for j,o in enumerate(external):
 if o.name in names:continue
 me=o.data.copy();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005);bm.to_mesh(me);bm.free();temp=bpy.data.objects.new('TEMP_V26_COLLISION',me);sc.collection.objects.link(temp);temp.matrix_world=o.matrix_world.copy()
 if len(me.polygons)>600:
  mod=temp.modifiers.new('Real_Surface_Proxy','DECIMATE');mod.ratio=.28;mod.use_collapse_triangulate=True
 deps.update();ev=temp.evaluated_get(deps);proxy=bpy.data.meshes.new_from_object(ev);append_mesh(o,proxy);bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(proxy);bpy.data.meshes.remove(me)
 if j%30==0:print('EXTERIOR_COLLISION',j,len(external),flush=True)
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=bpy.data.meshes.new('V26_Repaired_Architecture_And_Source_Exterior_Collision');me.from_pydata(vv,[],ff);me.update();cache.data=me;cache.matrix_world.identity();cache['V26_Current_Geometry_Collision']=True;changed.append(cache.name);write('V26_Collision_Index.json',{'architectural_triangles':architecture_faces,'triangles':len(ff),'objects':ci,'frame':40,'no_infinite_plane':True})
for text,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[text].as_string().replace('Rebuild_V24_34','Rebuild_V26').replace('V24.34','V26');bpy.data.texts[text].clear();bpy.data.texts[text].write(code);(O/'Roam'/fn).write_text(code,encoding='utf8')
for n in ['打开修正版模型.cmd','启动漫游.cmd']:(O/n).write_text((SRC.parents[1]/n).read_text('utf8').replace('Rebuild_V24_34','Rebuild_V26').replace('Architecture_Complete_V24_34','Architecture_Complete_V26'),encoding='utf8')
views=[('01_White_Courtyard_Inside',(-5,-6,3.1),(-17,5,1.0),23),('02_Original_Site_Entrance_Ramp',(-20.5,-16.5,4.3),(-13.9,-10.55,-.3),35),('03_Stair_Landing_Lower',(7.45,9.15,2.75),(4.45,8.6,1.55),20),('04_Stair_Landing_Upper',(7.45,9.15,6.5),(4.45,8.6,5.3),20),('05_Stair_Wall_Corner',(6.3,8.7,5.8),(4.1,9.72,6.7),24),('06_Whole_Building',(24,-22,17),(6,4,4.5),36),('07_Structure_Cutaway',(19,-12,17),(6.5,6.,4.5),40),('08_Stair_Bearings_Cutaway',(11.5,13.4,10.2),(5.9,8.6,3.5),40)]
for tag,pos,aim,lens in views:
 name='V26_'+tag;o=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(o);o.location=pos;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_start=.025;o.data.clip_end=500;added.append(name)
(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8');sc.camera=bpy.data.objects['V26_01_White_Courtyard_Inside'];sc['Version']='V26_WHITE_COURTYARD_ORIGINAL_RAMP_CONNECTED_STAIR_FRAME';sc['V26_Base_SHA256']=sha(SRC);sc['V26_Structural_Status']='Geometric connection repaired; not a structural capacity or reinforcement verification'
note=bpy.data.texts.new('V26_修正范围与结构检查边界');note.write('底稿为V24.34。外院墙朝院内的实际网格面改白，外侧青砖保持。入口恢复纯场地版本.3dm原坡面和照片UV，仅在现有建模道路0.85米范围内调整接缝。楼梯外侧与墙形成120mm几何搭接，平台增设埋入式支承梁；恢复原400x400柱截面、梁端和楼层节点。各层楼板标高、门窗位置与动作保持。此为建筑模型几何纠错；结构体系、配筋、材料强度、荷载、地基及抗震验算不在现有资料中，不能据此宣称完成结构安全或全部规范认证。')
sc.frame_set(40);bpy.context.view_layer.update()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
write('V26_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(set(changed)),'added':added,'removed':[],'structure':struct['proof'],'ramp':ramp['proof'],'white_inner_faces':paint,'capacity_analysis':False})
for n in ['Prepared_Structure.json','Prepared_Ramp.json','Original_Source_Index.json','Base.json']:shutil.copy2(D/n,O/'Sources'/n)
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_Build.json',{'source':str(SRC),'source_sha256':sha(SRC),'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'date':'2026-10-23'});print('V26_SAVED',str(P),sha(P),flush=True)
