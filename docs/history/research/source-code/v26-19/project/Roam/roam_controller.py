"""Human-scale third-person architectural tour, entirely inside Blender."""
import bpy,math,time,blf
from mathutils import Vector
from architecture_roam_physics import World,Walker,HEIGHT,WALK_SPEED,RUN_SPEED
import architecture_roam_measure as measurements
from architecture_roam_measure import MeasureSession

PRESETS={'INNER_GATE':(6.6,-10.9,-.6),'COURT':(6.5,-4.8,-.411),'F1':(8.5,7.8,0.),'F2':(8.5,7.8,3.900024),'F3':(8.5,7.8,7.5),'EXTERIOR':(-49.,-45.,-11.57),'MB7_FIELD':(28.,-59.,-14.84)}
ROOT='V24_21_Roam_Person_165cm'
CAM='V24_21_Third_Person_Follow_Camera'
COLLISION='V24_21_Navigation_Collision'
_running=None
_font=0

def world_from_scene():
 o=bpy.data.objects[COLLISION];me=o.data;me.calc_loop_triangles()
 return World([o.matrix_world@v.co for v in me.vertices],[t.vertices[:]for t in me.loop_triangles])

def pose_character(position,heading,phase=0.,moving=False,airborne=False):
 root=bpy.data.objects[ROOT];root.location=position;root.rotation_euler.z=heading
 for side,sign in [('L',1),('R',-1)]:
  leg=bpy.data.objects['V24_21_Avatar_'+side+'_Hip'];knee=bpy.data.objects['V24_21_Avatar_'+side+'_Knee'];arm=bpy.data.objects['V24_21_Avatar_'+side+'_Shoulder']
  a=.30*math.sin(phase)*sign if moving else 0.
  leg.rotation_euler.x=a if not airborne else .20*sign
  knee.rotation_euler.x=-max(0.,a)*1.65 if not airborne else -.35
  arm.rotation_euler.x=-a*.85 if not airborne else -.32
 if moving and not airborne:root.location.z-=.038*abs(math.sin(phase))

class ARCHROAM_Settings(bpy.types.PropertyGroup):
 first_person:bpy.props.BoolProperty(name='人眼视角',default=False)
 distance:bpy.props.FloatProperty(name='跟随距离',default=2.50,min=.45,max=5.5,subtype='DISTANCE')
 smooth:bpy.props.FloatProperty(name='跟随平滑',default=12,min=3,max=30)

class ARCHROAM_OT_start(bpy.types.Operator):
 bl_idname='arch_roam.start';bl_label='开始漫游';bl_description='方向键移动，空格跳跃，鼠标右键转向，Esc退出'
 def invoke(self,context,event):
  global _running
  if _running is not None:self.report({'INFO'},'漫游已经运行');return {'CANCELLED'}
  if context.area is None or context.area.type!='VIEW_3D':self.report({'ERROR'},'请在3D视图中启动漫游');return {'CANCELLED'}
  self.area=context.area;self.space=context.space_data;self.region3d=self.space.region_3d;self.window=context.window;self.scene=context.scene
  self.previous={'camera':self.scene.camera,'perspective':self.region3d.view_perspective,'location':self.region3d.view_location.copy(),'rotation':self.region3d.view_rotation.copy(),'distance':self.region3d.view_distance,'lens':self.space.lens,'clip_start':self.space.clip_start,'clip_end':self.space.clip_end,'overlays':self.space.overlay.show_overlays}
  self.scene.frame_set(40);context.view_layer.update();self.world=world_from_scene();self.walker=Walker(self.world,bpy.data.objects[ROOT].location);self.keys=set();self.jump=False;self.orbit=False;self.yaw=-float(bpy.data.objects[ROOT].rotation_euler.z);self.pitch=math.radians(10);self.phase=0.;self.heading=-self.yaw;self.last=time.perf_counter();self.camera=bpy.data.objects[CAM];self.scene.camera=self.camera;self.camera_pos=None
  self.space.clip_start=.035;self.space.clip_end=300.;self.space.lens=24.;self.space.overlay.show_overlays=False;self.region3d.view_perspective='PERSP'
  self.measure=MeasureSession(self)
  self.draw3d=bpy.types.SpaceView3D.draw_handler_add(self.measure.draw3d,(), 'WINDOW','POST_VIEW')
  self.timer=context.window_manager.event_timer_add(1/60,window=context.window);self.draw=bpy.types.SpaceView3D.draw_handler_add(self.draw_hud,(), 'WINDOW','POST_PIXEL');context.window_manager.modal_handler_add(self);_running=self
  self.area.header_text_set(None)
  self.update(context,1/60);print('ARCH_ROAM_READY',flush=True);return {'RUNNING_MODAL'}
 def draw_hud(self):
  try:
   mode='人眼视角 1.53m'if self.scene.arch_roam.first_person else'第三人称跟随'
   blf.size(_font,16);blf.enable(_font,blf.SHADOW);blf.shadow(_font,3,0.,0.,0.,.9);blf.shadow_offset(_font,1,-1);blf.color(_font,.96,.98,1.,1.);blf.position(_font,24,76,0);blf.draw(_font,'V26.19  ·  1.65m 漫游人物  ·  '+mode)
   blf.size(_font,13);blf.position(_font,24,52,0);blf.draw(_font,'方向键 / WASD：移动    空格：跳跃    Shift：快走    右键拖动：转向')
   blf.position(_font,24,30,0);blf.draw(_font,'滚轮：跟随距离    V：切换视角    Home：回院落    M：材质/流畅    Esc：结束漫游')
   blf.disable(_font,blf.SHADOW)
   self.measure.draw_hud(_font)
  except (ReferenceError,RuntimeError):pass
 def visible_avatar(self,show):
  root=bpy.data.objects[ROOT]
  for o in root.children_recursive:
   if o.type=='MESH':o.hide_set(not show)
 def update(self,context,dt):
  settings=self.scene.arch_roam;fwd=Vector((math.sin(self.yaw),math.cos(self.yaw),0));right=Vector((math.cos(self.yaw),-math.sin(self.yaw),0));up=('UP_ARROW'in self.keys or'W'in self.keys)-('DOWN_ARROW'in self.keys or'S'in self.keys);side=('RIGHT_ARROW'in self.keys or'D'in self.keys)-('LEFT_ARROW'in self.keys or'A'in self.keys);direction=fwd*up+right*side
  if self.measure.mode!='OFF':direction=Vector((0,0,0))
  if direction.length>1:direction.normalize()
  before=self.walker.p.copy();p=self.walker.update(direction,dt,self.jump,'LEFT_SHIFT'in self.keys or'RIGHT_SHIFT'in self.keys);self.jump=False
  if not all(math.isfinite(x)for x in p):self.walker.recover();p=self.walker.p.copy()
  dist=(p-before).length;moving=dist>.0003 and direction.length>.1
  if moving:
   target=-math.atan2(direction.x,direction.y);delta=(target-self.heading+math.pi)%(2*math.pi)-math.pi;self.heading+=delta*min(1,dt*14);self.phase+=dist*7.8
  pose_character(p,self.heading,self.phase,moving,not self.walker.grounded)
  if settings.first_person:
   target=p+Vector((0,0,1.53));look=Vector((math.sin(self.yaw)*math.cos(self.pitch),math.cos(self.yaw)*math.cos(self.pitch),-math.sin(self.pitch)));desired=target;aim=target+look;self.camera_pos=desired.copy();self.visible_avatar(False)
  else:
   target=p+Vector((0,0,1.25));forward=Vector((math.sin(self.yaw)*math.cos(self.pitch),math.cos(self.yaw)*math.cos(self.pitch),-math.sin(self.pitch)));desired=target-forward*settings.distance
   desired=self.world.camera(target,desired)
   if self.camera_pos is None:self.camera_pos=desired.copy()
   alpha=1-math.exp(-settings.smooth*dt);self.camera_pos=self.world.camera(target,self.camera_pos.lerp(desired,alpha));aim=target;self.visible_avatar((self.camera_pos-target).length>.65)
  self.camera.location=self.camera_pos;rotation=(aim-self.camera_pos).to_track_quat('-Z','Y');self.camera.rotation_mode='QUATERNION';self.camera.rotation_quaternion=rotation
  self.region3d.view_rotation=rotation;self.region3d.view_distance=max(.10,(self.camera_pos-aim).length);self.region3d.view_location=aim;self.area.tag_redraw()
 def modal(self,context,event):
  if event.ctrl and event.type=='S':return {'PASS_THROUGH'}
  if self.measure.handle(context,event):return {'RUNNING_MODAL'}
  if event.type in {'ESC','F8'}and event.value=='PRESS':self.finish(context);return {'FINISHED'}
  if event.type in {'UP_ARROW','DOWN_ARROW','LEFT_ARROW','RIGHT_ARROW','W','A','S','D','LEFT_SHIFT','RIGHT_SHIFT'}:
   if event.value=='PRESS':self.keys.add(event.type)
   elif event.value=='RELEASE':self.keys.discard(event.type)
   return {'RUNNING_MODAL'}
  if event.type=='SPACE':
   if event.value=='PRESS':self.jump=True
   return {'RUNNING_MODAL'}
  if event.type=='RIGHTMOUSE':
   self.orbit=event.value=='PRESS';self.mx=event.mouse_x;self.my=event.mouse_y;return {'RUNNING_MODAL'}
  if event.type=='MOUSEMOVE'and self.orbit:
   self.yaw+=(event.mouse_x-self.mx)*.004;self.pitch=max(math.radians(-55),min(math.radians(62),self.pitch-(event.mouse_y-self.my)*.003));self.mx=event.mouse_x;self.my=event.mouse_y;return {'RUNNING_MODAL'}
  if event.type in {'WHEELUPMOUSE','WHEELDOWNMOUSE'}:
   self.scene.arch_roam.distance=max(.45,min(5.5,self.scene.arch_roam.distance+(-.2 if event.type=='WHEELUPMOUSE'else.2)));return {'RUNNING_MODAL'}
  if event.type=='V'and event.value=='PRESS':self.scene.arch_roam.first_person=not self.scene.arch_roam.first_person;self.camera_pos=None;return {'RUNNING_MODAL'}
  if event.type=='HOME'and event.value=='PRESS':self.walker.place(PRESETS['COURT']);self.camera_pos=None;return {'RUNNING_MODAL'}
  if event.type=='M'and event.value=='PRESS':
   shade=self.space.shading
   if shade.type=='SOLID':shade.type='MATERIAL'
   else:shade.type='SOLID';shade.color_type='MATERIAL'
   return {'RUNNING_MODAL'}
  if event.type in {'WINDOW_DEACTIVATE','WINDEACTIVATE'}:self.keys.clear();self.orbit=False;return {'PASS_THROUGH'}
  if event.type=='TIMER':
   now=time.perf_counter();dt=min(.10,now-self.last);self.last=now
   try:self.update(context,dt)
   except Exception as e:
    self.finish(context);self.report({'ERROR'},'漫游停止：'+str(e));raise
   return {'RUNNING_MODAL'}
  return {'PASS_THROUGH'}
 def finish(self,context):
  global _running
  self.measure.stop();bpy.types.SpaceView3D.draw_handler_remove(self.draw3d,'WINDOW')
  context.window_manager.event_timer_remove(self.timer);bpy.types.SpaceView3D.draw_handler_remove(self.draw,'WINDOW');self.area.header_text_set(None);self.visible_avatar(True);self.scene.camera=self.previous['camera'];self.region3d.view_perspective=self.previous['perspective'];self.region3d.view_location=self.previous['location'];self.region3d.view_rotation=self.previous['rotation'];self.region3d.view_distance=self.previous['distance'];self.space.lens=self.previous['lens'];self.space.clip_start=self.previous['clip_start'];self.space.clip_end=self.previous['clip_end'];self.space.overlay.show_overlays=self.previous['overlays'];self.keys.clear();_running=None;self.area.tag_redraw();print('ARCH_ROAM_STOPPED',flush=True)
 def cancel(self,context):
  if _running is self:self.finish(context)

class ARCHROAM_OT_preset(bpy.types.Operator):
 bl_idname='arch_roam.preset';bl_label='切换位置'
 location:bpy.props.StringProperty(default='COURT')
 def execute(self,context):
  p=PRESETS[self.location]
  if _running is not None:_running.walker.place(p);_running.camera_pos=None
  else:bpy.data.objects[ROOT].location=p
  return {'FINISHED'}

class ARCHROAM_PT_panel(bpy.types.Panel):
 bl_label='1.65m 人物漫游';bl_idname='ARCHROAM_PT_panel';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='建筑漫游'
 def draw(self,context):
  L=self.layout;L.operator('arch_roam.start',text='开始漫游 / F8',icon='PLAY');L.prop(context.scene.arch_roam,'first_person');L.prop(context.scene.arch_roam,'distance');row=L.row()
  for key,label in [('COURT','院落'),('F1','一楼'),('F2','二楼'),('F3','三楼')]:row.operator('arch_roam.preset',text=label).location=key
  row=L.row()
  for key,label in [('EXTERIOR','外景道路'),('MB7_FIELD','新增地块')]:row.operator('arch_roam.preset',text=label).location=key
  row=L.row();row.operator('arch_roam.measure_mode',text='测长度 / L').mode='LENGTH';row.operator('arch_roam.measure_mode',text='测面积 / P').mode='AREA'
  row=L.row();row.operator('arch_roam.measure_undo',text='撤销测量');row.operator('arch_roam.measure_export',text='导出 CSV')
  for r in measurements.read_records(context.scene)[-5:]:L.label(text=f"{r['length_m']:.3f} m"if r['type']=='LENGTH'else f"{r['area_m2']:.3f} m²")
  for text in ['↑↓←→ / WASD 移动','空格跳跃，Shift快走','右键拖动转向，滚轮调整距离','V切换人眼/第三人称','Home回院落，Esc退出']:L.label(text=text)

_classes=[ARCHROAM_Settings,ARCHROAM_OT_start,ARCHROAM_OT_preset,ARCHROAM_PT_panel]
_keymaps=[]
def register():
 global _font
 measurements.register()
 for c in _classes:bpy.utils.register_class(c)
 bpy.types.Scene.arch_roam=bpy.props.PointerProperty(type=ARCHROAM_Settings)
 try:_font=blf.load('C:/Windows/Fonts/msyh.ttc')
 except Exception:_font=0
 wm=bpy.context.window_manager
 if wm.keyconfigs.addon:
  km=wm.keyconfigs.addon.keymaps.new(name='3D View',space_type='VIEW_3D');ki=km.keymap_items.new('arch_roam.start','F8','PRESS');_keymaps.append((km,ki))
def unregister():
 for km,ki in _keymaps:km.keymap_items.remove(ki)
 _keymaps.clear()
 if hasattr(bpy.types.Scene,'arch_roam'):del bpy.types.Scene.arch_roam
 for c in _classes[::-1]:bpy.utils.unregister_class(c)
 measurements.unregister()

if __name__=='__main__':register()
