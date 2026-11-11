from pathlib import Path
import ast

W = Path(__file__).parent
D = W / 'v26_8_perf'
D.mkdir(exist_ok=True)
source = Path('E:/jz/JIA/Rebuild_V26_8/Roam/roam_controller.py').read_text('utf8')

old = "  self.measure=MeasureSession(self)"
new = """  self._avatar_objects=[o for o in bpy.data.objects[ROOT].children_recursive if o.type=='MESH']
  self._avatar_shown=None;self._last_pose=None;self._input_dirty=True;self._focus_active=True;self._camera_settling=True
  self.perf_counts={'timer_events':0,'simulation_updates':0,'idle_skips':0,'focus_skips':0}
  self.measure=MeasureSession(self)"""
assert old in source
source=source.replace(old,new,1)
old="""  root=bpy.data.objects[ROOT]
  for o in root.children_recursive:
   if o.type=='MESH':o.hide_set(not show)"""
new="""  if self._avatar_shown is show:return
  for o in self._avatar_objects:o.hide_set(not show)
  self._avatar_shown=show"""
assert old in source
source=source.replace(old,new,1)
old="  pose_character(p,self.heading,self.phase,moving,not self.walker.grounded)"
new="""  pose=(*p,self.heading,self.phase if moving else 0.,moving,not self.walker.grounded)
  if pose!=self._last_pose:
   pose_character(p,self.heading,self.phase,moving,not self.walker.grounded);self._last_pose=pose"""
assert old in source
source=source.replace(old,new,1)
old="   target=p+Vector((0,0,1.53));look="
new="   self._camera_settling=False\n   target=p+Vector((0,0,1.53));look="
assert old in source
source=source.replace(old,new,1)
old="   alpha=1-math.exp(-settings.smooth*dt);self.camera_pos=self.world.camera(target,self.camera_pos.lerp(desired,alpha));aim=target;self.visible_avatar((self.camera_pos-target).length>.65)"
new="""   alpha=1-math.exp(-settings.smooth*dt);self.camera_pos=self.world.camera(target,self.camera_pos.lerp(desired,alpha));aim=target;self.visible_avatar((self.camera_pos-target).length>.65)
   self._camera_settling=(self.camera_pos-desired).length>.001"""
assert old in source
source=source.replace(old,new,1)
old=" def modal(self,context,event):\n  if event.ctrl"
new=""" def modal(self,context,event):
  if event.type not in {'TIMER','WINDOW_DEACTIVATE','WINDEACTIVATE','INBETWEEN_MOUSEMOVE'}:
   self._focus_active=True
   if event.type in {'LEFTMOUSE','RIGHTMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE','V','HOME','F8'}or(event.type=='MOUSEMOVE'and self.orbit):self._input_dirty=True
  if event.ctrl"""
assert old in source
source=source.replace(old,new,1)
old="  if event.type in {'WINDOW_DEACTIVATE','WINDEACTIVATE'}:self.keys.clear();self.orbit=False;return {'PASS_THROUGH'}"
new="  if event.type in {'WINDOW_DEACTIVATE','WINDEACTIVATE'}:self.keys.clear();self.orbit=False;self._focus_active=False;return {'PASS_THROUGH'}"
assert old in source
source=source.replace(old,new,1)
old="""  if event.type=='TIMER':
   now=time.perf_counter();dt=min(.10,now-self.last);self.last=now
   try:self.update(context,dt)"""
new="""  if event.type=='TIMER':
   if hasattr(event,'timer')and event.timer!=self.timer:return {'PASS_THROUGH'}
   self.perf_counts['timer_events']+=1
   now=time.perf_counter();dt=min(.10,now-self.last);self.last=now
   if not self._focus_active:
    self.perf_counts['focus_skips']+=1;return {'RUNNING_MODAL'}
   needs_update=bool(self.keys)or self.jump or not self.walker.grounded or self._input_dirty or self._camera_settling
   if not needs_update:
    self.perf_counts['idle_skips']+=1;return {'RUNNING_MODAL'}
   self._input_dirty=False;self.perf_counts['simulation_updates']+=1
   try:self.update(context,dt)"""
assert old in source
source=source.replace(old,new,1)
old="  if _running is not None:_running.walker.place(p);_running.camera_pos=None"
new="  if _running is not None:_running.walker.place(p);_running.camera_pos=None;_running._input_dirty=True"
assert old in source
source=source.replace(old,new,1)
source=source.replace('M：材质/流畅','M：纹理/极速')
ast.parse(source)
(D/'roam_controller_fast.py').write_text(source,'utf8')
print('FAST_CONTROLLER_CREATED',len(source))
