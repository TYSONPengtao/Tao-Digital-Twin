from pathlib import Path
import bpy,numpy as np,json,sys,hashlib,shutil
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_2';O=Path('E:/jz/JIA/Rebuild_V26_2');R=O/'Reports';BASE=Path('E:/jz/JIA/Rebuild_V26_1');SRC=BASE/'Blender/Architecture_Complete_V26_1.blend';P=O/'Blender/Architecture_Complete_V26_2.blend'
for p in [P.parent,R,O/'Roam',O/'Sources',O/'References']:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(W));from v26_2_views import VIEWS
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
col=bpy.data.collections.new('V26_2_连续墙面门洞及外墙贴图修正');sc.collection.children.link(col);ar=bpy.data.collections.new('V26_2_上版构件备份_隐藏且排除碰撞');sc.collection.children.link(ar);ar.hide_render=True;ar.hide_viewport=True
changed=[];added=[]
# New shader groups reference the existing packed photographs. Original shared
# material graphs and packed photo bytes are not edited.
def photograph_group(source,name,width,height,offset=0.,wrap_v=True):
 g=bpy.data.node_groups[source].copy();g.name=name;ns=g.nodes;ls=g.links
 uv=ns.new('ShaderNodeTexCoord');uv.name='Metre_Arc_Length';uvs=ns.new('ShaderNodeSeparateXYZ');ls.new(uv.outputs['UV'],uvs.inputs[0]);geo=ns.new('ShaderNodeNewGeometry');z=ns.new('ShaderNodeSeparateXYZ');ls.new(geo.outputs['Position'],z.inputs[0]);comb=ns.new('ShaderNodeCombineXYZ')
 for axis,socket,scale,off in [('X',uvs.outputs['X'],width,0),('Y',z.outputs['Z'],height,offset)]:
  n=ns.new('ShaderNodeMath');n.operation='ADD';n.inputs[1].default_value=off;ls.new(socket,n.inputs[0]);d=ns.new('ShaderNodeMath');d.operation='DIVIDE';d.inputs[1].default_value=scale;ls.new(n.outputs[0],d.inputs[0]);value=d.outputs[0]
  if axis=='X'or wrap_v:
   pp=ns.new('ShaderNodeMath');pp.operation='PINGPONG';pp.inputs[1].default_value=1.;ls.new(value,pp.inputs[0]);value=pp.outputs[0]
  ls.new(value,comb.inputs[axis])
 for nd in list(ns):
  if nd.type=='TEX_IMAGE':nd.extension='EXTEND';ls.new(comb.outputs[0],nd.inputs['Vector'])
 g['V26_2_Photo_Width_Metres']=width;g['V26_2_Photo_Height_Metres']=height;g['V26_2_Continuous_Arc_Length']=True;return g
rubble=photograph_group('V26_1_Source_M_V24_18_Continuous_Rubble','V26_2_Arc_Rubble_Photo',3.2,2.3)
stone=photograph_group('V26_1_Source_M_V19_Perimeter_Dark_Stone','V26_2_Arc_Dressed_Stone_Photo',3.6,.48,.68,False)
gallery_stone=photograph_group('V26_1_Source_M_V19_Perimeter_Dark_Stone','V26_2_Arc_Gallery_Stone_Photo',3.6,.67,1.05,False)
brick=photograph_group('V26_1_Source_M_V24_20_Shared_AsBuilt_Perimeter_Brick','V26_2_Arc_Blue_Brick_Photo',1.6,.9)
white=bpy.data.node_groups['V26_1_Source_M_V19_Limewash_Band'].copy();white.name='V26_2_Limewash_Band'
def group(nt,g):
 n=nt.nodes.new('ShaderNodeGroup');n.node_tree=g;return n.outputs['Shader']
def less(nt,value,threshold):
 n=nt.nodes.new('ShaderNodeMath');n.operation='LESS_THAN';n.inputs[1].default_value=threshold;nt.links.new(value,n.inputs[0]);return n.outputs[0]
def mix(nt,factor,a,b):
 n=nt.nodes.new('ShaderNodeMixShader');nt.links.new(factor,n.inputs[0]);nt.links.new(a,n.inputs[1]);nt.links.new(b,n.inputs[2]);return n.outputs[0]
for name,outer in [('M_V26_2_Continuous_Exterior_Strata',True),('M_V26_2_Continuous_Gallery_Base',False)]:
 ma=bpy.data.materials.new(name);ma.use_nodes=True;ma.use_fake_user=True;nt=ma.node_tree;nt.nodes.clear();geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],xyz.inputs[0]);rr=group(nt,rubble);gg=group(nt,gallery_stone);gallery=mix(nt,less(nt,xyz.outputs['Z'],-1.05),gg,rr)
 if outer:
  bb=group(nt,brick);ss=group(nt,stone);ww=group(nt,white);cur=bb
  for threshold,shader in [(.04,ww),(-.20,ss),(-.68,rr)]:cur=mix(nt,less(nt,xyz.outputs['Z'],threshold),cur,shader)
  x=nt.nodes.new('ShaderNodeMath');x.operation='GREATER_THAN';x.inputs[1].default_value=13.0;nt.links.new(xyz.outputs['X'],x.inputs[0]);y=less(nt,xyz.outputs['Y'],-8.2);z=less(nt,xyz.outputs['Z'],-.375);xy=nt.nodes.new('ShaderNodeMath');xy.operation='MULTIPLY';nt.links.new(x.outputs[0],xy.inputs[0]);nt.links.new(y,xy.inputs[1]);test=nt.nodes.new('ShaderNodeMath');test.operation='MULTIPLY';nt.links.new(xy.outputs[0],test.inputs[0]);nt.links.new(z,test.inputs[1]);cur=mix(nt,test.outputs[0],cur,gallery)
 else:cur=gallery
 out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(cur,out.inputs['Surface']);ma['V26_2_No_Overlay_Faces']=True;ma['V26_2_Basis']='Existing packed site photo textures; common registered finish datums'
preps=[json.loads((D/f'Prepared_{tag}.json').read_text('utf8'))for tag in ['House','Site']];archive=set(n for pp in preps for n in pp.get('archive',[]));rows=[r for pp in preps for r in pp['objects']]
for n in archive:
 o=bpy.data.objects[n]
 for c in list(o.users_collection):c.objects.unlink(o)
 ar.objects.link(o);o.hide_render=True;o.hide_set(True);o['V26_2_Previous_Component_Retained']=True;changed.append(n)
for r in rows:
 n=r['name'];a=np.load(D/r['file']);o=bpy.data.objects.get(n);me=bpy.data.meshes.new(n+'_V26_2');iv=o.matrix_world.inverted()if o else None;me.from_pydata([iv@Vector(v)for v in a['v']]if o else a['v'],[],a['f'])
 for mat in r['materials']:me.materials.append(bpy.data.materials[mat])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_2_Continuous_Source_Photo_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True;me.update()
 if o:o.data=me;changed.append(n)
 else:o=bpy.data.objects.new(n,me);col.objects.link(o);added.append(n)
 o['V26_2_Repair']=r['reason'];print('INSTALLED',n,len(a['f']),flush=True)
# Isolate the 450mm datum correction from the original animated hinge curves.
leaf=bpy.data.objects['DOOR_BATH_F1_R__LEAF'];parent=leaf.parent;cor=bpy.data.objects.new('V26_2_F1_Right_Glazed_Door_Datum_Correction',None);col.objects.link(cor);cor.parent=parent;cor.location.z=-.45;leaf.parent=cor;changed.extend([leaf.name,'DOOR_BATH_F1_R__LEAF_Geometry']);added.append(cor.name);cor['V26_2_Datum_Correction_Metres']=-.45;leaf['V26_2_Floor_Datum_Corrected']=True;sc.frame_set(40);bpy.context.view_layer.update()
# Rebuild only the affected ranges of the actual static open-door roam mesh.
# Untouched context scan proxies retain the previous verified surface ranges.
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();cv=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in old.loop_triangles],np.int32);index=json.loads((BASE/'Reports/V26_1_Collision_Index.json').read_text('utf8'))['objects'];edited=set(changed)|set(added);vv=[];ff=[];ci=[];offset=0;first=0
def append(v,f,name,kind):
 global offset,first
 v=np.asarray(v);f=np.asarray(f);vv.append(v);ff.append(f+offset);ci.append({'name':name,'first_triangle':first,'triangles':len(f),'source':kind});offset+=len(v);first+=len(f)
for r in index:
 n=r['name']
 if n in edited or n in archive:continue
 fs=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,ix=np.unique(fs.ravel(),return_inverse=True);append(cv[used],ix.reshape(-1,3),n,'Unchanged V26.1 verified surface proxy')
need={r['name']for r in rows}|{'DOOR_BATH_F1_R__LEAF_Geometry'}
for n in sorted(need):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);append(v,f,n,'Current saved V26.2 native geometry');print('COLLISION_REPLACED',n,len(f),flush=True)
me=bpy.data.meshes.new('V26_2_Actual_Continuous_Surface_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);write('V26_2_Collision_Index.json',{'objects':ci,'triangles':first,'frame':40,'archived_components_excluded':True,'no_infinite_ground':True})
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string().replace('Rebuild_V26_1','Rebuild_V26_2').replace('Architecture_Complete_V26_1.blend','Architecture_Complete_V26_2.blend');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code);(O/'Roam'/fn).write_text(code,encoding='utf8')
for n in ['启动漫游.cmd','打开修正版模型.cmd']:(O/n).write_text((BASE/n).read_text('utf8').replace('Rebuild_V26_1','Rebuild_V26_2').replace('Architecture_Complete_V26_1.blend','Architecture_Complete_V26_2.blend'),encoding='utf8')
for tag,pos,aim,lens in VIEWS:
 c=bpy.data.objects.new('V26_2_'+tag,bpy.data.cameras.new('V26_2_'+tag));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=600;added.append(c.name)
sc.camera=bpy.data.objects['V26_2_08_House_Overview'];sc['Version']='V26_2_Continuous_Finished_Walls_And_Exterior_Photo_Strata';sc['V26_2_Source_SHA256']=sha(SRC)
text=bpy.data.texts.new('V26_2_结构与贴图修正说明');text.write('以V26.1另存。三层楼各房间柱边、梁侧、窗下墙面统一到连续完成面，保留梁柱核心和原门窗洞口。门框补足墙厚；一层右侧玻璃门原来高出门洞450mm，使用独立标高校正父级下移，保留原动画和开启方向。院墙外侧毛石、灰石、白灰腰线沿整段统一，内侧白墙保留。廊下旧白色装饰和青砖错贴清理，与毛石及条石基座衔接。实际地面和围墙交接归并，漫游碰撞同步。原入口实景坡和外景扫描保留。外观和几何接合校正不等于现场测量或结构承载验算。')
for time in ['072718','072826','072901','072943','073017','073142','073314','073539']:
 p=Path('D:/Desktop/屏幕截图 2026-10-23 '+time+'.jpg')
 if p.exists():shutil.copy2(p,O/'References'/p.name)
write('V26_2_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(set(changed)),'added':sorted(set(added)),'archived':sorted(archive),'removed':[],'house_proof':preps[0]['proof'],'site_proof':preps[1]['proof'],'door_pose_expected_change':['DOOR_BATH_F1_R__FRAME_Geometry','DOOR_BATH_F1_R__LEAF_Geometry'],'no_rhino_export':True})
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_2_Build.json',{'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'source':str(SRC),'source_sha256':sha(SRC),'blender':bpy.app.version_string});print('V26_2_SAVED',str(P),sha(P),flush=True)
