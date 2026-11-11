"""Surface-picked metric measurements for the native architectural tour."""
import bpy,blf,gpu,json,math,time,csv,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils
from bpy_extras.io_utils import ExportHelper

KEY='V24_25_Measurements_JSON'
def distance(points,scale=1.):
 if len(points)!=2:raise ValueError('长度需要两个端点')
 return(Vector(points[1])-Vector(points[0])).length*scale

def polygon_metrics(points,scale=1.):
 ps=[Vector(p)for p in points]
 if len(ps)>2 and(ps[-1]-ps[0]).length<1e-6:ps.pop()
 if len(ps)<3:raise ValueError('面积至少需要三个边界点')
 if any((a-b).length<1e-6 for i,a in enumerate(ps)for b in ps[i+1:]):raise ValueError('边界点重复，请撤销后重新点选')
 normal=Vector((0.,0.,0.))
 for a,b in zip(ps,ps[1:]+ps[:1]):normal+=a.cross(b)
 if normal.length<1e-9:raise ValueError('边界不能共线或交叉')
 normal.normalize();u=(ps[1]-ps[0]);u-=normal*u.dot(normal);u.normalize();v=normal.cross(u)
 xy=[((p-ps[0]).dot(u),(p-ps[0]).dot(v))for p in ps]
 def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 def touch(a,b,c,d):
  aa,bb,cc,dd=cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)
  if aa*bb<-1e-14 and cc*dd<-1e-14:return True
  for z,p,q,t in [(aa,a,b,c),(bb,a,b,d),(cc,c,d,a),(dd,c,d,b)]:
   if abs(z)<1e-9 and min(p[0],q[0])-1e-9<=t[0]<=max(p[0],q[0])+1e-9 and min(p[1],q[1])-1e-9<=t[1]<=max(p[1],q[1])+1e-9:return True
  return False
 N=len(ps)
 for i in range(N):
  for j in range(i+1,N):
   if j==i+1 or(i==0 and j==N-1):continue
   if touch(xy[i],xy[(i+1)%N],xy[j],xy[(j+1)%N]):raise ValueError('边界相交，请沿轮廓依次点选')
 projected=[Vector((q[0],q[1],0.))for q in xy];triangles=tessellate_polygon([projected]);area=0.
 for t in triangles:
  ids=[int(p)if isinstance(p,int)else min(range(N),key=lambda i:(projected[i]-p).length_squared)for p in t];a,b,c=[ps[i]for i in ids];area+=(b-a).cross(c-a).length/2
 if area<1e-8:raise ValueError('面积太小，请重新点选')
 horizontal=abs(sum(a.x*b.y-b.x*a.y for a,b in zip(ps,ps[1:]+ps[:1])))/2
 perimeter=sum((a-b).length for a,b in zip(ps,ps[1:]+ps[:1]))
 return{'area_m2':area*scale*scale,'horizontal_area_m2':horizontal*scale*scale,'perimeter_m':perimeter*scale,'max_plane_deviation_m':max(abs((p-ps[0]).dot(normal))for p in ps)*scale}

def read_records(scene):
 try:
  a=json.loads(scene.get(KEY,'[]'));return[r for r in a if r.get('type')in ['LENGTH','AREA']and isinstance(r.get('points'),list)]
 except(ValueError,TypeError,AttributeError):return[]

def export_records(records,path):
 with Path(path).open('w',encoding='utf-8-sig',newline='')as f:
  w=csv.writer(f);w.writerow(['序号','类型','长度_m','面内面积_m2','水平投影面积_m2','周长_m','最大离面偏差_m','模型坐标点'])
  for i,r in enumerate(records,1):w.writerow([i,'长度'if r['type']=='LENGTH'else'面积',r.get('length_m',''),r.get('area_m2',''),r.get('horizontal_area_m2',''),r.get('perimeter_m',''),r.get('max_plane_deviation_m',''),json.dumps(r['points'],ensure_ascii=False)])

def live():return getattr(sys.modules.get('architecture_roam_controller'),'_running',None)

class SurfacePicker:
 def __init__(self,context):
  self.dg=context.evaluated_depsgraph_get();self.objects=[]
  for o in context.scene.objects:
   if o.type!='MESH'or o.hide_render or not o.visible_get(view_layer=context.view_layer)or o.name.startswith('V24_21_')or any(k in o.name.upper()for k in ['OLD_REFERENCE','ORIGINAL_EXTERIOR','NAVIGATION_COLLISION']):continue
   e=o.evaluated_get(self.dg);bb=[Vector(p)for p in e.bound_box];lo=Vector(tuple(min(p[i]for p in bb)for i in range(3)));hi=Vector(tuple(max(p[i]for p in bb)for i in range(3)));self.objects.append((e,e.matrix_world.copy(),e.matrix_world.inverted_safe(),lo,hi))
 def pick(self,region,rv3d,xy,snap=False):
  origin=view3d_utils.region_2d_to_origin_3d(region,rv3d,xy);direction=view3d_utils.region_2d_to_vector_3d(region,rv3d,xy).normalized();best=1000.;chosen=None
  for o,m,iv,lo,hi in self.objects:
   a=iv@origin;d=iv.to_3x3()@direction;t0=0.;t1=best
   for i in range(3):
    if abs(d[i])<1e-12:
     if a[i]<lo[i]or a[i]>hi[i]:t1=-1.;break
    else:
     aa=(lo[i]-a[i])/d[i];bb=(hi[i]-a[i])/d[i];t0=max(t0,min(aa,bb));t1=min(t1,max(aa,bb))
   if t0>t1 or t1<0:continue
   hit,p,no,face=o.ray_cast(a,d.normalized(),distance=best*d.length)
   if not hit:continue
   p=m@p;length=(p-origin).dot(direction)
   if 0<=length<best:best=length;chosen=(p,o,m,face)
  if chosen is None:return None
  p,o,m,face=chosen
  if snap and 0<=face<len(o.data.polygons):
   candidates=[]
   for j in o.data.polygons[face].vertices:
    q=m@o.data.vertices[j].co;s=view3d_utils.location_3d_to_region_2d(region,rv3d,q)
    if s is not None:candidates.append(((s-Vector(xy)).length,q))
   if candidates:
    error,q=min(candidates,key=lambda a:a[0])
    if error<18:p=q
  return p

class MeasureSession:
 def __init__(self,owner):
  self.owner=owner;self.scene=owner.scene;self.mode='OFF';self.points=[];self.records=read_records(self.scene);self.hover=None;self.picker=None;self.last_pick=0.;self.message='';self.shader=None
 def save(self):self.scene[KEY]=json.dumps(self.records,ensure_ascii=False)
 def begin(self,mode,context):
  if mode==self.mode or mode=='OFF':self.stop();return
  self.mode=mode;self.points=[];self.hover=None;self.message='';self.owner.keys.clear();self.owner.jump=False;self.picker=SurfacePicker(context);self.owner.area.tag_redraw()
 def stop(self):self.mode='OFF';self.points=[];self.hover=None;self.message='';self.owner.keys.clear();self.owner.area.tag_redraw()
 def add(self,p):
  if self.points and(Vector(p)-Vector(self.points[-1])).length<1e-5:return
  self.points.append(list(p));self.message=''
  if self.mode=='LENGTH'and len(self.points)==2:self.commit()
 def commit(self):
  scale=self.scene.unit_settings.scale_length or 1.
  try:
   r={'type':self.mode,'points':[list(p)for p in self.points]}
   if self.mode=='LENGTH':r['length_m']=distance(self.points,scale)
   else:r.update(polygon_metrics(self.points,scale))
   self.records.append(r);self.save();self.points=[];self.message='已记录：'+self.label(r);self.owner.area.tag_redraw();return True
  except ValueError as e:self.message=str(e);return False
 def undo(self):
  if self.points:self.points.pop()
  elif self.records:self.records.pop();self.save()
  self.message='';self.owner.area.tag_redraw()
 def label(self,r):return f"长度 {r['length_m']:.3f} m"if r['type']=='LENGTH'else f"面内面积 {r['area_m2']:.3f} m²  |  水平面积 {r['horizontal_area_m2']:.3f} m²  |  周长 {r['perimeter_m']:.3f} m"
 def handle(self,context,event):
  if event.value=='PRESS'and event.type in {'L','P'}:self.begin('LENGTH'if event.type=='L'else'AREA',context);return True
  if self.mode=='OFF':return False
  if event.type=='ESC'and event.value=='PRESS':self.stop();return True
  if event.type=='BACK_SPACE'and event.value=='PRESS':self.undo();return True
  if event.type in {'RET','NUMPAD_ENTER'}and event.value=='PRESS':
   if self.mode=='AREA':self.commit()
   return True
  region=next((r for r in self.owner.area.regions if r.type=='WINDOW'),None)
  if region is None:return False
  xy=(event.mouse_x-region.x,event.mouse_y-region.y);inside=0<=xy[0]<region.width and 0<=xy[1]<region.height
  if event.type=='LEFTMOUSE'and inside:
   if event.value=='DOUBLE_CLICK'and self.mode=='AREA':self.commit()
   elif event.value=='PRESS':
    p=self.picker.pick(region,self.owner.region3d,xy,event.ctrl)
    if p is None:self.message='请点选模型表面'
    else:self.add(p)
   return True
  if event.type=='MOUSEMOVE'and inside and not self.owner.orbit and time.perf_counter()-self.last_pick>.09:
   self.last_pick=time.perf_counter();self.hover=self.picker.pick(region,self.owner.region3d,xy,event.ctrl);self.owner.area.tag_redraw()
  if event.type=='SPACE':return True
  return False
 def draw3d(self):
  try:
   if self.shader is None:self.shader=gpu.shader.from_builtin('UNIFORM_COLOR')
   gpu.state.blend_set('ALPHA');gpu.state.depth_test_set('NONE');gpu.state.line_width_set(2.);gpu.state.point_size_set(7.)
   for r in self.records[-40:]:self.draw_line(r['points'],r['type']=='AREA',(1.,.65,.12,1.)if r['type']=='AREA'else(.15,.86,1.,1.))
   pending=self.points+([list(self.hover)]if self.hover is not None else[])
   if pending:self.draw_line(pending,False,(.95,1.,.25,1.))
  except(ReferenceError,RuntimeError,ValueError):pass
  finally:gpu.state.line_width_set(1.);gpu.state.point_size_set(1.);gpu.state.blend_set('NONE');gpu.state.depth_test_set('NONE')
 def draw_line(self,points,closed,color):
  if not points:return
  self.shader.bind();self.shader.uniform_float('color',color);batch_for_shader(self.shader,'POINTS',{'pos':points}).draw(self.shader)
  if len(points)>1:
   seq=points+[points[0]]if closed else points;batch_for_shader(self.shader,'LINE_STRIP',{'pos':seq}).draw(self.shader)
 def draw_hud(self,font):
  try:
   blf.enable(font,blf.SHADOW);blf.shadow(font,3,0,0,0,.95);blf.color(font,1.,.92,.55,1.);blf.size(font,15)
   if self.mode!='OFF':
    lines=['测长度：点选两个端点'if self.mode=='LENGTH'else'测面积：沿边界依次点选，Enter 完成','Ctrl 吸附顶点  |  Backspace 撤销  |  Esc 返回漫游']
    if self.message:lines.append(self.message)
    elif self.points:lines.append('已选 '+str(len(self.points))+' 个点')
   else:lines=['L 测长度  |  P 测面积  |  顶栏可导出测量结果']
   for i,s in enumerate(lines):blf.position(font,24,160+i*24,0);blf.draw(font,s)
   if self.records:blf.position(font,24,116,0);blf.draw(font,'最近结果：'+self.label(self.records[-1]))
   region=next((r for r in self.owner.area.regions if r.type=='WINDOW'),None)
   if region:
    for r in self.records[-12:]:
     pts=[Vector(p)for p in r['points']];center=sum(pts,Vector())/len(pts);screen=view3d_utils.location_3d_to_region_2d(region,self.owner.region3d,center)
     if screen is not None:blf.position(font,screen.x+8,screen.y+8,0);blf.draw(font,f"{r['length_m']:.3f} m"if r['type']=='LENGTH'else f"{r['area_m2']:.3f} m²")
   blf.disable(font,blf.SHADOW)
  except(ReferenceError,RuntimeError,ValueError):pass

class ARCHMEASURE_OT_mode(bpy.types.Operator):
 bl_idname='arch_roam.measure_mode';bl_label='模型测量';bl_description='在模型表面点选端点或面积边界'
 mode:bpy.props.EnumProperty(items=[('LENGTH','长度',''),('AREA','面积',''),('OFF','结束','')],default='LENGTH')
 def execute(self,context):
  op=live()
  if op is None:
   bpy.ops.arch_roam.resume('INVOKE_DEFAULT');op=live()
  if op is None:return{'CANCELLED'}
  op.measure.begin(self.mode,context);return{'FINISHED'}

class ARCHMEASURE_OT_undo(bpy.types.Operator):
 bl_idname='arch_roam.measure_undo';bl_label='撤销测量';bl_description='撤销一个边界点，或删除最近一条测量'
 def execute(self,context):
  op=live()
  if op:op.measure.undo()
  else:
   r=read_records(context.scene)
   if r:r.pop();context.scene[KEY]=json.dumps(r,ensure_ascii=False)
  return{'FINISHED'}

class ARCHMEASURE_OT_export(bpy.types.Operator,ExportHelper):
 bl_idname='arch_roam.measure_export';bl_label='导出测量CSV';filename_ext='.csv'
 filter_glob:bpy.props.StringProperty(default='*.csv',options={'HIDDEN'})
 def invoke(self,context,event):
  self.filepath=bpy.path.abspath('//测量结果.csv');context.window_manager.fileselect_add(self);return{'RUNNING_MODAL'}
 def execute(self,context):
  r=read_records(context.scene)
  if not r:self.report({'WARNING'},'尚无测量结果');return{'CANCELLED'}
  try:export_records(r,bpy.path.abspath(self.filepath))
  except OSError as e:self.report({'ERROR'},str(e));return{'CANCELLED'}
  self.report({'INFO'},'已导出 '+str(len(r))+' 条测量');return{'FINISHED'}

classes=[ARCHMEASURE_OT_mode,ARCHMEASURE_OT_undo,ARCHMEASURE_OT_export]
def register():
 for c in classes:bpy.utils.register_class(c)
def unregister():
 for c in classes[::-1]:bpy.utils.unregister_class(c)
