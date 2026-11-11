import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _mesh
from v24_18_finish import ArcMap
D=W/'v24_20';O=Path('E:/jz/JIA/Rebuild_V24_20');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True)
P=O/'Blender/Architecture_Complete_V24_20.blend';src=json.loads((D/'Source.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text())}
prep['proof']['f1_wc_space']['door_location_basis']='User confirmed moving left along the same wall. The 1.20m distance is fitted to photo 230016 and the existing room, not a new survey measurement.'
bpy.ops.wm.open_mainfile(filepath=src['model']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_20_实景围墙厨房与瓦作纠正');sc.collection.children.link(col)
changed=[];added=[];removed=[];finishes=[];wallreports=[]
for ma in bpy.data.materials:ma.use_fake_user=True
for a in bpy.data.actions:a.use_fake_user=True

def photo_material(name,oldname,scale):
 m=bpy.data.materials[oldname].copy();m.name=name;m.use_fake_user=True;ns=m.node_tree.nodes;ls=m.node_tree.links;uv=ns.new('ShaderNodeTexCoord');mul=ns.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=scale;ls.new(uv.outputs['UV'],mul.inputs[0]);sep=ns.new('ShaderNodeSeparateXYZ');ls.new(mul.outputs[0],sep.inputs[0]);comb=ns.new('ShaderNodeCombineXYZ')
 for ax in ['X','Y']:
  pp=ns.new('ShaderNodeMath');pp.operation='PINGPONG';pp.inputs[1].default_value=1;ls.new(sep.outputs[ax],pp.inputs[0]);ls.new(pp.outputs[0],comb.inputs[ax])
 for nd in ns:
  if nd.type=='TEX_IMAGE':nd.extension='EXTEND';ls.new(comb.outputs[0],nd.inputs['Vector'])
 for nd in ns:
  if nd.type=='BSDF_PRINCIPLED':nd.inputs['Roughness'].default_value=.93;nd.inputs['Specular IOR Level'].default_value=.18
 return m
brick=photo_material('M_V24_20_Shared_AsBuilt_Perimeter_Brick','M_V19_Perimeter_Brick',(.625,1/.9,1));stone=photo_material('M_V24_20_Low_AsBuilt_Stone_Base','M_V19_Perimeter_Rubble',(.5,1.,1))
perimeter=bpy.data.materials.new('M_V24_20_Continuous_AsBuilt_Perimeter');perimeter.use_nodes=True;perimeter.use_fake_user=True;ns=perimeter.node_tree.nodes;ls=perimeter.node_tree.links;ns.clear();out=ns.new('ShaderNodeOutputMaterial');mix=ns.new('ShaderNodeMixShader');ls.new(mix.outputs[0],out.inputs['Surface'])
def branch(oldname,scale):
 images=[n.image for n in bpy.data.materials[oldname].node_tree.nodes if n.type=='TEX_IMAGE'and n.image];uv=ns.new('ShaderNodeTexCoord');mul=ns.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=scale;ls.new(uv.outputs['UV'],mul.inputs[0]);sep=ns.new('ShaderNodeSeparateXYZ');ls.new(mul.outputs[0],sep.inputs[0]);comb=ns.new('ShaderNodeCombineXYZ')
 for axis in ['X','Y']:
  pp=ns.new('ShaderNodeMath');pp.operation='PINGPONG';pp.inputs[1].default_value=1;ls.new(sep.outputs[axis],pp.inputs[0]);ls.new(pp.outputs[0],comb.inputs[axis])
 color=ns.new('ShaderNodeTexImage');color.image=images[0];color.extension='EXTEND';ls.new(comb.outputs[0],color.inputs['Vector']);bs=ns.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.93;bs.inputs['Specular IOR Level'].default_value=.18;ls.new(color.outputs['Color'],bs.inputs['Base Color'])
 if len(images)>1:
  height=ns.new('ShaderNodeTexImage');height.image=images[1];height.extension='EXTEND';ls.new(comb.outputs[0],height.inputs['Vector']);bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.0015;ls.new(height.outputs['Color'],bump.inputs['Height']);ls.new(bump.outputs[0],bs.inputs['Normal'])
 return bs.outputs['BSDF']
ls.new(branch('M_V19_Perimeter_Rubble',(.5,1,1)),mix.inputs[1]);ls.new(branch('M_V19_Perimeter_Brick',(.625,1/.9,1)),mix.inputs[2]);attr=ns.new('ShaderNodeAttribute');attr.attribute_name='V24_20_Height_Above_Finish_Division';gate=ns.new('ShaderNodeMath');gate.operation='GREATER_THAN';gate.inputs[1].default_value=0;ls.new(attr.outputs['Fac'],gate.inputs[0]);ls.new(gate.outputs[0],mix.inputs[0])
clay=bpy.data.materials.new('M_V24_20_Unified_Weathered_Gray_Clay');clay.use_nodes=True;clay.use_fake_user=True;ns=clay.node_tree.nodes;ls=clay.node_tree.links;ns.clear();out=ns.new('ShaderNodeOutputMaterial');bs=ns.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.9;bs.inputs['Specular IOR Level'].default_value=.18;ls.new(bs.outputs[0],out.inputs[0]);uv=ns.new('ShaderNodeTexCoord');im=ns.new('ShaderNodeTexImage');im.image=bpy.data.images['Weathered_Wall_Tile.png'];im.extension='REPEAT';ls.new(uv.outputs['UV'],im.inputs['Vector']);bw=ns.new('ShaderNodeRGBToBW');ls.new(im.outputs['Color'],bw.inputs[0]);mult=ns.new('ShaderNodeMath');mult.operation='MULTIPLY_ADD';mult.inputs[1].default_value=.28;mult.inputs[2].default_value=.10;ls.new(bw.outputs[0],mult.inputs[0]);rgb=ns.new('ShaderNodeCombineXYZ')
for ax in ['X','Y','Z']:ls.new(mult.outputs[0],rgb.inputs[ax])
ls.new(rgb.outputs[0],bs.inputs['Base Color']);height=ns.new('ShaderNodeTexImage');height.image=bpy.data.images['Weathered_Wall_Tile_Height.png'];ls.new(uv.outputs['UV'],height.inputs['Vector']);bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.0006;ls.new(height.outputs['Color'],bump.inputs['Height']);ls.new(bump.outputs[0],bs.inputs['Normal'])

for n in prep['remove']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True);removed.append(n)

def replace(n,v,f):
 o=bpy.data.objects[n];old=o.data;iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V24_20');me.from_pydata([iv@Vector(p)for p in v],[],f);me.update();o.data=me
 for m in old.materials:me.materials.append(m)
 if not old.users:bpy.data.meshes.remove(old)
 changed.append(n);return o

def add_mesh(n,v,f,ma):
 # Preserve oriented cavity shells supplied by the solid modeller.
 me=bpy.data.meshes.new(n+'_Mesh');me.from_pydata(v,[],f);me.materials.append(ma);me.update();o=bpy.data.objects.new(n,me);col.objects.link(o);return o

def uv_metres(o):
 me=o.data;uv=me.uv_layers.active or me.uv_layers.new(name='V24_20_Metres')
 for f in me.polygons:
  pts=np.array([o.matrix_world@me.vertices[j].co for j in f.vertices]);normal=o.matrix_world.to_3x3()@f.normal;coords=pts[:,[1,2]]if abs(normal.x)>abs(normal.y)else pts[:,[0,2]]
  if abs(normal.z)>.65:coords=pts[:,:2]
  for li,q in zip(f.loop_indices,coords):uv.data[li].uv=q

def transfer(o,datafile):
 d=np.load(datafile);v=d['v'];f=d['f'];mi=d['mi'];t=v[f];tr=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);uv=o.data.uv_layers.active or o.data.uv_layers.new(name='Source_Affine_Metre_UV')
 for face in o.data.polygons:
  pts=np.array([o.matrix_world@o.data.vertices[i].co for i in face.vertices]);hit=tr.find_nearest(Vector(pts.mean(0)));j=hit[2];face.material_index=int(mi[j]);p=t[j];A=np.c_[p[1]-p[0],p[2]-p[0]];bc=np.linalg.lstsq(A,(pts-p[0]).T,rcond=None)[0].T;q=d['uv'][j];coords=q[0]+bc[:,0,None]*(q[1]-q[0])+bc[:,1,None]*(q[2]-q[0])
  for li,q in zip(face.loop_indices,coords):uv.data[li].uv=q

for row in prep['objects']:
 ma=bpy.data.materials[row['material']]
 if row['new']:o=add_mesh(row['name'],row['v'],row['f'],ma);added.append(o.name)
 else:o=replace(row['name'],row['v'],row['f'])
 if row.get('transfer'):
  transfer(o,row.get('transfer_file',str(D/idx[o.name]['file'])))
  if row.get('frame_base_material_by_z'):
   for face in o.data.polygons:face.material_index=1 if (o.matrix_world@face.center).z<-.19998 else 0
 else:
  o.data.materials.clear();o.data.materials.append(ma);uv_metres(o)
 if 'Unified_Pan_Barrel'in o.name or o.name=='SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry':
  for face in o.data.polygons:face.use_smooth=True

# Apply white finish to the actual inner wall faces, avoiding overlay skins.
white=bpy.data.materials['M_V24_11_Plain_White_Limewash']
for row in prep['material_edits']:
 o=bpy.data.objects[row['name']];o.data=o.data.copy();me=o.data;j=len(me.materials);me.materials.append(white);count=0
 for face in me.polygons:
  pts=np.array([o.matrix_world@me.vertices[i].co for i in face.vertices]);c=pts.mean(0);normal=o.matrix_world.to_3x3()@face.normal
  yes=(-11.96<c[1]<-2.49 and c[0]>12.7 and normal.x<-.25)or(-4.0<c[1]<-2.49 and 8.05<c[0]<14.3 and normal.y<-.35)or(-11.96<c[1]<-10.6 and 8.05<c[0]<13.43 and normal.y>.35)
  inner_x=13.10 if c[1]<-8.6 else 13.245+(c[1]+8.276)*(.714/4.994)
  if -11.96<c[1]<-2.49 and 12.7<c[0]<inner_x+.028 and c[2]<-.10 and normal.z>.35:yes=True
  if row['kind']=='kitchen_floor_toe':
   yes=-11.96<c[1]<-2.9 and 12.65<c[0]<inner_x+.03 and c[2]>-.435 and normal.z>.35
   if yes:
    concrete=bpy.data.materials['M_Concrete']
    if concrete.name not in me.materials:me.materials.append(concrete)
    face.material_index=me.materials.find(concrete.name);count+=1
   continue
  if yes:face.material_index=j;count+=1
 changed.append(o.name);finishes.append({'object':o.name,'white_inner_faces':count})

# One continuous scalar field controls the finish; it introduces no mesh cuts.
rr=prep['wall_grade_segments'];a=np.array([r['a']for r in rr]);d=np.array([r['b']for r in rr])-a;ll=np.einsum('ij,ij->i',d,d);za=np.array([r['za']for r in rr]);zb=np.array([r['zb']for r in rr])
def grade_z(v):
 zz=[]
 for p in v:
  tt=np.clip(np.einsum('ij,ij->i',p[:2]-a,d)/ll,0,1);dist=np.linalg.norm(a+d*tt[:,None]-p[:2],axis=1);i=int(np.argmin(dist));zz.append(za[i]+tt[i]*(zb[i]-za[i]))
 return np.array(zz)
mapper=ArcMap(prep['wall_uv_route'])
for n in prep['proof']['perimeter_finish']['walls']+[prep['proof']['perimeter_finish']['toe']]:
 o=bpy.data.objects[n];o.data=o.data.copy();me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64);field=v[:,2]-grade_z(v)-.2;me.materials.clear();me.materials.append(perimeter);att=me.attributes.new('V24_20_Height_Above_Finish_Division','FLOAT','POINT');att.data.foreach_set('value',field.astype(np.float32))
 while me.uv_layers:me.uv_layers.remove(me.uv_layers[0])
 uv=me.uv_layers.new(name='Shared_Perimeter_ArcLength_Metres');uv.active_render=True;area=0
 for face in me.polygons:
  face.material_index=0;pts=v[list(face.vertices)];q=mapper.triangle(pts)
  for li,qq in zip(face.loop_indices,q):uv.data[li].uv=qq
  for j in range(1,len(pts)-1):area+=np.linalg.norm(np.cross(pts[j]-pts[0],pts[j+1]-pts[0]))/2
 changed.append(n);wallreports.append({'object':n,'surface_area_m2':float(area),'division_height_above_road_grade_m':.2,'shared_material':perimeter.name,'image_physical_width_height_m':[1.6,.9],'finish_does_not_subdivide_geometry':True})

# All fired clay roof surfaces share the same material; sheet roofs retain theirs.
ceramic_names={'M_Roof','M_V19_Weathered_Wall_Tile','M_V24_17_Stable_Gray_Ceramic'}|{f'M_V23_Gate_Tile_{i:02d}'for i in range(5)}|{f'M_V24_09_Screenwall_Ceramic_{i}'for i in range(5)}
for o in bpy.data.objects:
 if o.type!='MESH'or 'ASPHALT'in o.name or 'FOLDED_RIDGE_CAPS'in o.name:continue
 slots=[i for i,m in enumerate(o.data.materials)if m and m.name in ceramic_names]
 if not slots:continue
 o.data=o.data.copy()
 for i in slots:o.data.materials[i]=clay
 changed.append(o.name)

for change in prep.get('door_changes',[]):
 offset=bpy.data.objects.new('V24_20_WC_Entry_Position',None);col.objects.link(offset);offset.location=change['translation'];added.append(offset.name)
 for n in change['objects']:
  o=bpy.data.objects[n];o.parent=offset;o.matrix_parent_inverse=Matrix.Identity(4);changed.append(n)
  changed.extend(c.name for c in o.children_recursive)

views=[('Perimeter',(-39,-13,8),(-14,1,.4),42),('Perimeter_Corner',(-31,2,3.8),(-23.6,4.7,.7),32),('Kitchen_Interior',(9.95,-7.25,1.5),(13.55,-7.0,1.05),17),('Kitchen_Floor',(11.9,-8.0,.65),(13.65,-5.7,-.2),25),('Kitchen_Roof',(18,-1.2,10),(11.6,-7.5,3.3),50),('Roof_Units',(20,-17,7.8),(15.7,-12.7,3.8),50),('House_Front',(20,-18,12.8),(6.8,2.,5.5),48),('WC_Entrance',(11.2,4.8,1.45),(11.2,7.4,1.1),26),('WC_Interior',(9.65,7.8,1.6),(12.5,9.2,1.3),22),('Whole_Site',(28,-32,18),(5,-7,1.3),47)]
for n,pos,target,lens in views:
 name='V24_20_'+n;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.035;c.data.clip_end=300;added.append(name)
for n,pos,target,lens in [('Roof_Junction',(17,-4,12.5),(13.3,-10.7,3.6),52),('WC_Stair_Entry',(8.0,8.95,1.45),(10.1,8.95,1.1),22)]:
 name='V24_20_'+n;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.035;c.data.clip_end=300;added.append(name)
o=bpy.data.objects['V24_20_WC_Interior'];o.location=(11.05,7.75,1.5);o.rotation_euler=(Vector((12.4,9.3,1.1))-o.location).to_track_quat('-Z','Y').to_euler()
sc.camera=bpy.data.objects['V24_20_House_Front'];sc.frame_set(40);bpy.context.view_layer.update();sc['Version']='V24_20_PHOTO_CORRECTED_PERIMETER_WC_KITCHEN_UNIFIED_CLAY_NO_DRAINS'
text=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');text.clear();text.write('V24.20：外院围墙采用用户指定侧墙的实景青砖照片，两面共用连续米制UV与同一材质；砖石分界按225227红线拟合为墙脚路面上方约0.20m，随路面高差衔接，低位墙脚同样连续。原墙体闭合块重新合并，材质分界不另切网格。厨房恢复被1.8m裁切误删的柱身和柱础，按002312实景让柱列随外墙内侧转折布置，梁架同步接续；内墙白色，弯墙脚的地面缺口补齐。雨水管、檐沟及落水口移除，原沟槽封平；烟囱、排烟弯头与真实金属雨棚保留。三层楼、厨房、储藏房统一灰色筒板瓦材质，瓦垄约158mm。两房交接按DJI_0598和DJI_0525修成斜向内凹交线、连续瓦面及砖封收口，保留镬耳和外挑瓦檐。首层按downa77d蓝线加隔墙分成两区，楼梯对面的原卫生间门保留，楼梯通道保留；右侧入口仍沿原墙左移1.20m，旧洞封好。26扇原门动作保留。窗动画第1帧关闭、第20帧半开、第40帧全开。尺寸为照片与既有模型拟合。')
def write(n,a):(R/n).write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
write('V24_20_Changes.json',{'changed':sorted(set(changed)),'added':sorted(set(added)),'removed':sorted(set(removed))});write('V24_20_Corrections.json',prep['proof']);write('V24_20_Finishes.json',{'perimeter':wallreports,'kitchen':finishes});bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
write('V24_20_Build.json',{'source':src['model'],'source_sha256':src['sha256'],'model':str(P),'sha256':h});print('V20_SAVED',h,flush=True)
