from pathlib import Path
import bpy,numpy as np,json,sys,hashlib,shutil
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_3';BASE=Path('E:/jz/JIA/Rebuild_V26_2');SRC=BASE/'Blender/Architecture_Complete_V26_2.blend';O=Path('E:/jz/JIA/Rebuild_V26_3');P=O/'Blender/Architecture_Complete_V26_3.blend';R=O/'Reports'
for p in [P.parent,R,O/'Roam',O/'Sources',O/'References']:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(W));from v26_3_views import VIEWS
def sha(p):
 with Path(p).open('rb')as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
col=bpy.data.collections.new('V26_3_隔墙上亮玻璃墙顶收口_次照壁原版恢复');sc.collection.children.link(col);ar=bpy.data.collections.new('V26_3_上版误改备份_隐藏排除碰撞');sc.collection.children.link(ar);ar.hide_render=True;ar.hide_viewport=True;changed=[];added=[]
archive={'V26_2_House_Flush_Continuous_Finished_Shell'}|{o.name for o in bpy.data.objects if o.name.startswith('V26_1_Secondary_Wall_')}
for n in archive:
 o=bpy.data.objects[n]
 for c in list(o.users_collection):c.objects.unlink(o)
 ar.objects.link(o);o.hide_set(True);o.hide_render=True;changed.append(n)
orig=json.loads((D/'Original_Secondary.json').read_text('utf8'));restored=[]
for r in orig['objects']:
 o=bpy.data.objects[r['name']];a=np.load(D/r['file']);actual=np.array([o.matrix_world@p.co for p in o.data.vertices]);assert actual.shape==a['v'].shape and np.max(abs(actual-a['v']))<1e-7,(o.name,'Original secondary geometry changed')
 assert np.max(abs(np.array([list(p)for p in o.matrix_world])-np.array(r['matrix'])))<1e-8,(o.name,'Original screenwall transform changed')
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.hide_render=r['hide_render'];o.hide_viewport=False;o.hide_set(r['hidden']);restored.append(o.name);changed.append(o.name);o['V26_3_Original_V24_34_Restored']=True
# Independent white material avoids changing shared original shaders.
white=bpy.data.materials['M_V24_31_White_Painted_Ceiling'].copy();white.name='M_V26_3_Neutral_White_Interior_Ceiling';white.diffuse_color=(.98,.98,.98,1)
for n in white.node_tree.nodes:
 if n.type=='BSDF_PRINCIPLED':n.inputs['Base Color'].default_value=(.98,.98,.98,1);n.inputs['Roughness'].default_value=.85
house=json.loads((D/'Prepared_House.json').read_text('utf8'));fixtures=json.loads((D/'Prepared_Fixtures.json').read_text('utf8'));deco=json.loads((D/'Prepared_Secondary_Deco.json').read_text('utf8'));rows=house['objects']+fixtures['objects']+deco['objects']
for r in rows:
 n=r['name'];a=np.load(D/r['file']);o=bpy.data.objects.get(n);me=bpy.data.meshes.new(n+'_V26_3');iv=o.matrix_world.inverted()if o else None;me.from_pydata([iv@Vector(v)for v in a['v']]if o else a['v'],[],a['f'])
 for mat in r['materials']:
  if n.startswith('V26_3_House')and mat=='M_V24_31_White_Painted_Ceiling':mat=white.name
  me.materials.append(bpy.data.materials[mat])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_3_Source_Photo_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True;me.update()
 if o:o.data=me;changed.append(n)
 else:o=bpy.data.objects.new(n,me);col.objects.link(o);added.append(n)
 o['V26_3_Repair']=r['reason'];print('INSTALLED',n,len(a['f']),flush=True)
# The original wall shader is driven by a source point attribute. Restore its
# interpolated values on the recovered branch, instead of leaving missing
# attribute defaults to create diagonal rubble / brick patches.
from mathutils.bvhtree import BVHTree
sr=json.loads((D/'Original_Secondary_Surfaces.json').read_text('utf8'))['objects'][0];sa=np.load(D/sr['file']);sv=sa['v'];sf=sa['f'];bvh=BVHTree.FromPolygons([Vector(v)for v in sv],sf.tolist(),all_triangles=True);gn=bpy.data.objects['V26_2_Continuous_Ground_And_Perimeter_Shell'];me=gn.data;ids=fixtures['proof']['secondary_wall_base']['restored_triangle_indices'];used=np.unique(np.array([me.polygons[i].vertices[:]for i in ids]).ravel());values=np.zeros(len(me.vertices),np.float32);distances=[]
for i in used:
 point=gn.matrix_world@me.vertices[int(i)].co;near,normal,face,dist=bvh.find_nearest(point);tr=sv[sf[face]];aa=tr[1]-tr[0];bb=tr[2]-tr[0];qq=np.array(near)-tr[0];ab=aa@bb;det=(aa@aa)*(bb@bb)-ab*ab;s=((bb@bb)*(aa@qq)-ab*(bb@qq))/det;t=((aa@aa)*(bb@qq)-ab*(aa@qq))/det;values[int(i)]=(1-s-t)*sa['height_attribute'][sf[face,0]]+s*sa['height_attribute'][sf[face,1]]+t*sa['height_attribute'][sf[face,2]];distances.append(float(dist))
attr=me.attributes.new('V24_20_Height_Above_Finish_Division','FLOAT','POINT');attr.data.foreach_set('value',values);me.update();np.savez_compressed(D/'Secondary_Restored_Point_Field.npz',ids=used,values=values[used]);write('V26_3_Secondary_Original_Attribute_Restoration.json',{'source':sr['file'],'attribute':attr.name,'points_restored':len(used),'maximum_source_surface_distance_m':max(distances),'restored_point_indices':used.tolist(),'original_profile_ornament_surfaces':deco['proof']})
# Reproduce the original UV interpolation as an affine world-space field on
# each recovered triangle. This retains the original photograph coordinates
# while avoiding a UV interpolation fallback in the combined native mesh.
assert float(values[used].min())>0.,('Secondary branch crosses original brick division',float(values[used].min()))
original=bpy.data.materials['M_V24_20_Continuous_AsBuilt_Perimeter'];mapping=[];sourcephoto=np.load(D/'Secondary_Original_Base_Finish.npz')
for i in ids:
 face=me.polygons[i]
 if me.materials[face.material_index].name!=original.name:continue
 v=np.array([gn.matrix_world@me.vertices[j].co for j in face.vertices]);_,_,sourceface,_=bvh.find_nearest(Vector(v.mean(0)));reference=sv[sf[sourceface]];reference_uv=sa['uv'][sourceface].astype(float);E=reference[1:]-reference[0];delta=reference_uv[1:]-reference_uv[0];gradients=E.T@np.linalg.solve(E@E.T,delta);offsets=reference_uv[0]-reference[0]@gradients;error=float(np.max(abs(reference@gradients+offsets-reference_uv)));assert error<1e-5,(i,sourceface,error)
 uv=v@gradients+offsets
 for j,coord in zip(face.loop_indices,uv):me.uv_layers.active.data[j].uv=coord
 g=bpy.data.node_groups['V26_2_Arc_Blue_Brick_Photo'].copy();g.name='V26_3_Original_Secondary_Affine_'+str(i);ns=g.nodes;lk=g.links;oldgeos=[n for n in ns if n.type=='NEW_GEOMETRY'];geo=ns.new('ShaderNodeNewGeometry');coords=[]
 for axis in range(2):
  dot=ns.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=gradients[:,axis];lk.new(geo.outputs['Position'],dot.inputs[0]);add=ns.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=float(offsets[axis]);lk.new(dot.outputs['Value'],add.inputs[0]);coords.append(add.outputs[0])
 co=ns.new('ShaderNodeCombineXYZ');lk.new(coords[0],co.inputs['X']);cv=ns.new('ShaderNodeCombineXYZ');lk.new(coords[1],cv.inputs['Z'])
 olduv=ns.get('Metre_Arc_Length')
 for link in list(olduv.outputs['UV'].links):target=link.to_socket;lk.remove(link);lk.new(co.outputs[0],target)
 for og in oldgeos:
  for link in list(og.outputs['Position'].links):target=link.to_socket;lk.remove(link);lk.new(cv.outputs[0],target)
 mat=bpy.data.materials.new('M_V26_3_Secondary_Original_Photo_'+str(i));mat.use_nodes=True;mat.diffuse_color=original.diffuse_color;nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');node=nt.nodes.new('ShaderNodeGroup');node.node_tree=g;nt.links.new(node.outputs['Shader'],out.inputs['Surface']);ix=len(me.materials);me.materials.append(mat);me.polygons[i].material_index=ix;mapping.append({'triangle':int(i),'original_source_triangle':int(sourceface),'gradients_world':gradients.tolist(),'offsets_m':offsets.tolist(),'maximum_source_uv_vertex_error_m':error})
me.update();write('V26_3_Secondary_Original_Photo_Mapping.json',{'basis':'Exact affine interpolation of original source U and V coordinates on the unchanged saved triangles','source_uv_preserved':True,'source_brick_photo_width_height_m':[1.6,.9],'source_height_field_minimum':float(values[used].min()),'triangles':mapping})
# Keep untouched context proxy ranges, and replace only changed geometric
# objects. Source ramp and exterior scan proxies are preserved byte for byte.
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();cv=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in old.loop_triangles],np.int32);index=json.loads((BASE/'Reports/V26_2_Collision_Index.json').read_text('utf8'))['objects'];need={r['name']for r in rows if r['name']!='V26_2_Continuous_Ground_And_Perimeter_Shell'}|set(restored);edited=archive|need;vv=[];ff=[];ci=[];off=0;first=0
def append(v,f,n,kind):
 global off,first
 vv.append(v);ff.append(f+off);ci.append({'name':n,'first_triangle':first,'triangles':len(f),'source':kind});off+=len(v);first+=len(f)
for r in index:
 if r['name']in edited:continue
 fs=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,ix=np.unique(fs.ravel(),return_inverse=True);append(cv[used],ix.reshape(-1,3),r['name'],'Unchanged V26.2 verified proxy')
for n in sorted(need):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();append(np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles],np.int32),n,'Current V26.3 native geometry')
me=bpy.data.meshes.new('V26_3_Current_Geometry_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);write('V26_3_Collision_Index.json',{'objects':ci,'triangles':first,'frame':40,'archived_components_excluded':True,'no_infinite_ground':True})
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string().replace('Rebuild_V26_2','Rebuild_V26_3').replace('Architecture_Complete_V26_2.blend','Architecture_Complete_V26_3.blend');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code);(O/'Roam'/fn).write_text(code,encoding='utf8')
for n in ['启动漫游.cmd']:(O/n).write_text((BASE/n).read_text('utf8').replace('Rebuild_V26_2','Rebuild_V26_3').replace('Architecture_Complete_V26_2.blend','Architecture_Complete_V26_3.blend'),encoding='utf8')
for tag,pos,aim,lens in VIEWS:
 c=bpy.data.objects.new('V26_3_'+tag,bpy.data.cameras.new('V26_3_'+tag));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=600;added.append(c.name)
sc.camera=bpy.data.objects['V26_2_08_House_Overview'];sc['Version']='V26_3_Partition_Transom_Roof_Junction_Original_Secondary_Screenwall';sc['V26_3_Source_SHA256']=sha(SRC)
txt=bpy.data.texts.new('V26_3_本次修正及次照壁原版恢复');txt.write('以 V26.2 为基准另存。次照壁恢复 V24.34 的11个原始构件、原坐标、原尺寸和材质，撤回 V26.1 的5个替代构件。一层右侧补回卧室与楼梯间对面卫生间之间的隔墙，保留100mm内部隔墙，两个卫生间门框深度由452mm恢复为220mm并保留原门扇动画。隔墙后端与后窗侧墙收口，后窗右端按现有隔墙位置收回110mm，左端与高程保留；110mm为模型调整量。一二层中心滑动门及上亮重新贯通墙洞，上亮上边接到原结构梁底，保留原玻璃与红色边框。高窗和楼梯墙头接到上层板底，三楼墙顶随原斜屋顶封合，不改变外部屋顶轮廓；内侧顶面改中性白色。保留原楼梯踏步、扶手、入口实景坡、外景扫描。碰撞使用本次保存的实际模型。')
for time in ['093856','094118','094232','094354','094441','094558','094659','094734','020444']:
 p=Path('D:/Desktop/屏幕截图 2026-10-23 '+time+'.jpg')
 if p.exists():shutil.copy2(p,O/'References'/p.name)
write('V26_3_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(set(changed)),'added':sorted(set(added)),'archived':sorted(archive),'restored_secondary':restored,'secondary_source':orig['source'],'secondary_source_sha256':orig['sha256'],'restored_secondary_ornaments':deco['proof'],'house_proof':house['proof'],'fixtures':fixtures['proof'],'removed':[],'no_rhino_export':True})
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_3_Build.json',{'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'source':str(SRC),'source_sha256':sha(SRC),'blender':bpy.app.version_string});print('V26_3_SAVED',sha(P),flush=True)
