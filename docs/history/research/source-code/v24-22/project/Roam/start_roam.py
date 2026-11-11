"""Explicit entry to a dedicated tour viewport; no saved script trust required."""
import bpy,sys,types,traceback

_prepared=False

class ARCHROAM_OT_resume(bpy.types.Operator):
 bl_idname='arch_roam.resume';bl_label='进入人物漫游';bl_description='开始或恢复1.65米人物漫游'
 def invoke(self,context,event):
  win=context.window
  areas=[a for a in win.screen.areas if a.type=='VIEW_3D']
  if not areas:self.report({'ERROR'},'当前窗口没有三维画面');return {'CANCELLED'}
  area=max(areas,key=lambda a:a.width*a.height)
  region=next(r for r in area.regions if r.type=='WINDOW')
  with context.temp_override(window=win,area=area,region=region):
   return bpy.ops.arch_roam.start('INVOKE_DEFAULT')

def draw_entry(self,context):
 self.layout.separator()
 self.layout.operator('arch_roam.resume',text='进入人物漫游 / F8',icon='PLAY')

def install_entry():
 if hasattr(bpy.types,'ARCHROAM_OT_resume'):return
 bpy.utils.register_class(ARCHROAM_OT_resume)
 bpy.types.VIEW3D_HT_header.append(draw_entry)
 wm=bpy.context.window_manager
 kc=wm.keyconfigs.addon if wm.keyconfigs.addon is not None else wm.keyconfigs.user
 km=kc.keymaps.new(name='Window',space_type='EMPTY')
 km.keymap_items.new('arch_roam.resume','F8','PRESS')

def load_embedded():
 if 'architecture_roam_controller'not in sys.modules:
  for name,text in [('architecture_roam_physics','V24_21_碰撞控制.py'),('architecture_roam_controller','V24_21_漫游控制器.py')]:
   m=types.ModuleType(name);m.__file__='<Blender text: '+text+'>';sys.modules[name]=m;exec(compile(bpy.data.texts[text].as_string(),m.__file__,'exec'),m.__dict__)
  sys.modules['architecture_roam_controller'].register()
 install_entry()

def begin():
 global _prepared
 if bpy.app.background:load_embedded();return None
 for win in bpy.context.window_manager.windows:
  areas=[a for a in win.screen.areas if a.type=='VIEW_3D']
  if not areas:continue
  area=max(areas,key=lambda a:a.width*a.height);region=next((r for r in area.regions if r.type=='WINDOW'),None)
  if region is None:continue
  if not _prepared:
   _prepared=True
   if len(win.screen.areas)>1:
    with bpy.context.temp_override(window=win,area=area,region=region):
     bpy.ops.screen.screen_full_area(use_hide_panels=False)
    print('ARCH_ROAM_VIEWPORT_PREPARED',flush=True)
    return .5
  try:
   with bpy.context.temp_override(window=win,area=area,region=region):
    load_embedded()
    control=sys.modules['architecture_roam_controller']
    if control._running is None:
     result=bpy.ops.arch_roam.start('INVOKE_DEFAULT')
     if 'RUNNING_MODAL'not in result:raise RuntimeError('Tour operator did not start: '+str(result))
    print('ARCH_ROAM_LAUNCHER_READY: arrows move; Space jumps; V switches eye view.',flush=True)
  except Exception:
   traceback.print_exc()
   print('ARCH_ROAM_LAUNCHER_FAILED',flush=True)
  return None
 return .5

if bpy.app.background:load_embedded()
else:bpy.app.timers.register(begin,first_interval=1.0)
