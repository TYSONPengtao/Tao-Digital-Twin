import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_03_junction_blender import _mesh
from v24_06_common import snapshot
D=W/'v24_16';O=Path('E:/jz/JIA/Rebuild_V24_16');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True)
B=Path('E:/jz/JIA/Rebuild_V24_15/Blender/Architecture_Complete_V24_15.blend');P=O/'Blender/Architecture_Complete_V24_16.blend'
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;write('V24_16_Before_Snapshot.json',snapshot(bpy));sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_16_入口白墙与照壁中线重建');sc.collection.children.link(col)
for m in bpy.data.materials:m.use_fake_user=True
prep=json.loads((D/'Prepared_Geometry.json').read_text());index={r['name']:r for r in json.loads((D/'Inventory.json').read_text())};changes=[];added=[]
def uv(o,axis):
 layer=o.data.uv_layers.active or o.data.uv_layers.new(name='V24_16_Metric_UV')
 for face in o.data.polygons:
  for li in face.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   layer.data[li].uv=((p.y+p.z)*1.6,p.x*.64)if axis=='X'else((p.x+p.z*.4)*1.6,p.y*.64)if axis=='Y'else((p.x+p.y)*1.6,p.z*.64)
def replace(n,v,f):
 o=bpy.data.objects[n];old=o.data;iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V24_16');me.from_pydata([iv@Vector(p)for p in v],[],f);me.update()
 for ma in old.materials:me.materials.append(ma)
 o.data=me
 if not old.users:bpy.data.meshes.remove(old)
 changes.append(n);return o
for row in prep['objects']:
 if row['new']:o=_mesh(bpy,col,row['name'],row['v'],row['f'],bpy.data.materials[row['material']]);added.append(o.name)
 else:o=replace(row['name'],row['v'],row['f'])
 if not row['transfer']:o.data.materials.clear();o.data.materials.append(bpy.data.materials[row['material']])
 uv(o,row['axis'])
 if row['transfer']:
  src=np.load(D/index[row['name']]['file']);v=src['v'];f=src['f'];mi=src['mi'];srcuv=src['uv'];tree=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);layer=o.data.uv_layers.active
  for face in o.data.polygons:
   hit=tree.find_nearest(o.matrix_world@face.center);ti=hit[2]
   if ti is None:continue
   face.material_index=int(mi[ti]);a,b,c=v[f[ti]];u=b-a;vv=c-a;den=(u@u)*(vv@vv)-(u@vv)**2
   if abs(den)<1e-18:continue
   for li in face.loop_indices:
    q=np.array(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co)-a;s=((vv@vv)*(q@u)-(u@vv)*(q@vv))/den;t=((u@u)*(q@vv)-(u@vv)*(q@u))/den;layer.data[li].uv=srcuv[ti,0]*(1-s-t)+srcuv[ti,1]*s+srcuv[ti,2]*t
 if row['material'].startswith('M_V24_09_Screenwall_Ceramic')and 'TILE_ROWS'in o.name:
  for i in range(1,5):o.data.materials.append(bpy.data.materials['M_V24_09_Screenwall_Ceramic_'+str(i)])
  for f in o.data.polygons:f.material_index=int(abs(f.center.x*47+f.center.y*29))%5
 if any(k in o.name for k in ['Column_1','Carved_Scroll','RIDGE_BORDER','LOTUS','FINIALS','End_Disks']):
  for f in o.data.polygons:f.use_smooth=True
 o['V24_16_Corrected']='Entrance white return and post axes / screenwall centred bearing and fork roof'
# Re-seat only the main screen crown. The untouched lower wall and its
# registered XY plan remain the reference; a new central bearing rises above.
crown=[];trace=np.array(prep['proof']['screen']['centerline_xy'])
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry']:
 o=bpy.data.objects[n];old=o.data;o.data=old.copy();T=o.matrix_world;iv=T.inverted();pts=np.array([T@v.co for v in o.data.vertices]);selected=(pts[:,0]>=3.2499)&(pts[:,0]<=10.8001)&(np.abs(pts[:,1]-np.interp(pts[:,0],trace[:,0],trace[:,1]))<.22);maxz={}
 for i in np.where(selected)[0]:key=tuple(np.round(pts[i,:2],5));maxz[key]=max(maxz.get(key,-999),pts[i,2])
 dz={}
 for i in np.where(selected&(pts[:,2]>2.65))[0]:
  p=pts[i].copy();top=maxz[tuple(np.round(p[:2],5))]
  if top<=2.65:continue
  p[2]=2.65+(p[2]-2.65)*(3.10-2.65)/(top-2.65);dz[i]=p[2]-pts[i,2];o.data.vertices[i].co=iv@Vector(p)
 if n.startswith('SITE_PERIMETER_')and o.data.uv_layers:
  layer=o.data.uv_layers.active
  for face in o.data.polygons:
   if o.data.materials[face.material_index].name!='M_V19_Perimeter_Brick':continue
   for li in face.loop_indices:
    i=o.data.loops[li].vertex_index
    if i in dz:layer.data[li].uv.y+=dz[i]/.9
 o.data.update();changes.append(n);crown.append({'name':n,'vertices_changed':len(dz),'only_above_z':2.65,'new_crown_z':3.10,'xy_unchanged':True})
views=[('Entrance_White_Bay',(17.65,-15.67,1.38),(13.52,-14.85,1.50),25,None),('Storage_Front',(24,-29,5.1),(13.7,-13.4,2.3),45,None),('Eave_Underside',(14.5,-15.9,1.20),(16,-15.15,3.00),26,None),('Screen_Outside',(7.025,-29,3.2),(7.025,-17.05,2.6),42,10.0),('Screen_End',(13.7,-17.15,3.60),(10.4,-17.15,3.60),40,3.6),('Screen_Fork',(13.3,-22.9,7.7),(8.5,-17.05,3.55),47,None),('Screen_Plan',(7.025,-17.1,16),(7.025,-17.1,3.7),45,9.7),('Screen_Inside',(7.025,-12.5,2.1),(7.025,-17.1,2.5),18,None),('Whole_Site',(28,-32,18),(5,-7,1.3),47,None)]
for n,pos,tar,lens,ortho in views:
 name='V24_16_'+n;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 added.append(name)
sc.camera=bpy.data.objects['V24_16_Entrance_White_Bay'];sc.frame_set(40);sc['Version']='V24_16_WHITE_ENTRANCE_BAY_AND_CENTRED_SCREENWALL';sc.render.resolution_x=1600;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
guide='V24.16：入口圆柱及柱础向檐廊外侧移0.57m，原两根柱保持竖直、斜向柱列，补齐柱后至退后木门窗之间的白灰侧墙。檐枋、挑梁、雀替和挂落按新柱位连续重接。照壁按原墙身两侧面实际中线重建底座、墙冠、连续窄承托、三层叠涩及瓦顶，分叉斜脊和端部扇铺瓦采用同一中线，四角改为与脊床连体的宽根陶质翘角。檐口两侧等挑，端面白芯居中。保存完整场地、储藏房瓦屋面和后弧墙、厨房及次照壁；26扇门动作保留。构件尺寸按照片近似拟合；承托和中线检查属于模型几何核对，不是工程结构计算。'
t=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide);write('V24_16_Changes.json',{'changed':changes,'added':added,'removed':[],'crown':crown});write('V24_16_Corrections.json',prep['proof']);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_16_Build.json',{'source':str(B),'source_sha256':sha(B),'model':str(P),'sha256':sha(P)});print('SAVED V24.16',str(P),flush=True)
