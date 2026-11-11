from pathlib import Path
W=Path(__file__).parent
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
s=Path('E:/jz/JIA/Rebuild_V24_24/Roam/roam_controller.py').read_text('utf8')
s=once(s,'from architecture_roam_physics import World,Walker,HEIGHT,WALK_SPEED,RUN_SPEED','from architecture_roam_physics import World,Walker,HEIGHT,WALK_SPEED,RUN_SPEED\nimport architecture_roam_measure as measurements\nfrom architecture_roam_measure import MeasureSession')
s=once(s,'  self.timer=context.window_manager.event_timer_add',"  self.measure=MeasureSession(self)\n  self.draw3d=bpy.types.SpaceView3D.draw_handler_add(self.measure.draw3d,(), 'WINDOW','POST_VIEW')\n  self.timer=context.window_manager.event_timer_add")
s=once(s,"  self.area.header_text_set('1.65米漫游  |  ↑↓←→ 移动  空格 跳跃  右键拖动 转向  滚轮 距离  V 人眼/第三人称  Home 回院落  Esc 退出')","  self.area.header_text_set(None)")
s=once(s,'   blf.disable(_font,blf.SHADOW)','   blf.disable(_font,blf.SHADOW)\n   self.measure.draw_hud(_font)')
s=once(s,'direction=fwd*up+right*side','direction=fwd*up+right*side\n  if self.measure.mode!=\'OFF\':direction=Vector((0,0,0))')
s=once(s,' def modal(self,context,event):'," def modal(self,context,event):\n  if event.ctrl and event.type=='S':return {'PASS_THROUGH'}\n  if self.measure.handle(context,event):return {'RUNNING_MODAL'}")
s=once(s,'  context.window_manager.event_timer_remove(self.timer);',"  self.measure.stop();bpy.types.SpaceView3D.draw_handler_remove(self.draw3d,'WINDOW')\n  context.window_manager.event_timer_remove(self.timer);")
s=once(s,'  for text in [\'↑↓←→ / WASD 移动\'',"  row=L.row();row.operator('arch_roam.measure_mode',text='测长度 / L').mode='LENGTH';row.operator('arch_roam.measure_mode',text='测面积 / P').mode='AREA'\n  row=L.row();row.operator('arch_roam.measure_undo',text='撤销测量');row.operator('arch_roam.measure_export',text='导出 CSV')\n  for r in measurements.read_records(context.scene)[-5:]:L.label(text=f\"{r['length_m']:.3f} m\"if r['type']=='LENGTH'else f\"{r['area_m2']:.3f} m²\")\n  for text in ['↑↓←→ / WASD 移动'")
s=once(s,' global _font\n for c in _classes:', ' global _font\n measurements.register()\n for c in _classes:')
s=once(s,' for c in _classes[::-1]:bpy.utils.unregister_class(c)',' for c in _classes[::-1]:bpy.utils.unregister_class(c)\n measurements.unregister()')
(W/'v24_25_roam_controller.py').write_text(s,encoding='utf8')
s=Path('E:/jz/JIA/Rebuild_V24_24/Roam/start_roam.py').read_text('utf8')
s=once(s,"[('architecture_roam_physics','V24_21_碰撞控制.py'),('architecture_roam_controller','V24_21_漫游控制器.py')]","[('architecture_roam_physics','V24_21_碰撞控制.py'),('architecture_roam_measure','V24_25_测量工具.py'),('architecture_roam_controller','V24_21_漫游控制器.py')]")
s=once(s," self.layout.operator('arch_roam.resume',text='进入人物漫游 / F8',icon='PLAY')"," self.layout.operator('arch_roam.resume',text='进入人物漫游 / F8',icon='PLAY')\n self.layout.separator()\n self.layout.operator('arch_roam.measure_mode',text='测长度 L',icon='DRIVER_DISTANCE').mode='LENGTH'\n self.layout.operator('arch_roam.measure_mode',text='测面积 P').mode='AREA'\n self.layout.operator('arch_roam.measure_undo',text='撤销')\n self.layout.operator('arch_roam.measure_export',text='导出 CSV')")
(W/'v24_25_start_roam.py').write_text(s,encoding='utf8')
s=(W/'v24_24_build.py').read_text('utf8').replace('v24_24','v24_25').replace('V24_24','V24_25')
s=s.replace('V24_25_端部封墙门前退墙及院落补铺','V24_25_高窗无缝门墙屋面铺装及测量')
a=s.index(" if row.get('wall_finish'):");b=s.index(" o['V24_25_Reference']",a)
s=s[:a]+''' if row.get('joint_brick_finish'):
  brick=me.materials.find('M_V24_18_Continuous_Blue_Brick')
  for face in me.polygons:
   c=o.matrix_world@face.center;no=o.matrix_world.to_3x3()@face.normal
   if 8.249<c.x<9.55 and abs(c.y+11.73)<.00005 and no.y<-.5:face.material_index=brick
 if row.get('window_panes'):
  mn='M_Glass_Frosted'
  if me.materials.find(mn)<0:me.materials.append(bpy.data.materials[mn])
  for face in me.polygons:
   c=o.matrix_world@face.center
   if abs(c.x-row['window_x'])<.0061 and any(a-1e-5<c.y<b+1e-5 and z0-1e-5<c.z<z1+1e-5 for a,b,z0,z1 in row['window_panes']):face.material_index=me.materials.find(mn)
  parent=o.parent
  if parent:
   params=json.loads(parent.get('Parameters','{}'));params['origin'][2]=min(p[2]for p in row['window_panes'])-.047;params.update(definition='WINDOW_W1200_H800_HIGH_FROSTED_TWO_VERTICAL_LIGHTS',sill_above_floor_m=1.8,height_m=.8,dimension_confidence='PHOTO_FITTED_HIGH_WINDOW');parent['Parameters']=json.dumps(params,ensure_ascii=False);changed.append(parent.name)
'''+s[b:]
s=s.replace("o['V24_25_Reference']='150017 / 150243 / 150306 / 150819'","o['V24_25_Reference']='151458 / 151716 / 175749 / 175946 / 180153 / 180416'")
a=s.index("for txt,fn in [");b=s.index('\nviews=',a)
s=s[:a]+'''for txt,fn in [('V24_25_测量工具.py','v24_25_measure_tools.py'),('V24_21_漫游控制器.py','v24_25_roam_controller.py'),('V24_21_启动漫游.py','v24_25_start_roam.py')]:
 text=bpy.data.texts.get(txt)or bpy.data.texts.new(txt);text.clear();text.write((W/fn).read_text('utf8'))
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 (O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1.;sc.unit_settings.length_unit='METERS';sc['V24_25_Measurements_JSON']='[]'
'''+s[b:]
views=[('WC_Right_F1',(11.45,8.50,1.53),(13.,8.55,2.25),25),('WC_Left_F2',(1.55,8.50,5.43),(0.,8.55,6.10),25),('Gate_Contact',(9.7,-14.2,1.13),(8.2,-11.65,1.65),29),('Gate_Eave',(10.,-15.,4.9),(8.6,-11.65,2.8),35),('Storage_Entrance',(11.7,-14.95,2.6),(13.35,-12.5,-.35),24),('Storage_Approach',(12.4,-13.3,1.3),(13.1,-15.6,-.4),22),('Kitchen_Roof',(3.0,-6.8,10.2),(11.1,-7.2,3.3),32),('Roof_Valley',(15.8,-18.0,11.0),(12.7,-11.3,3.6),34)]
a=s.index('views=');b=s.index('\nfor tag,loc,aim,lens in views:',a);s=s[:a]+'views='+repr(views)+s[b:]
s=s.replace("['150017','150243','150306','150819']","['151458','151716','175749','175827','175910','175946','180153','180416']")
a=s.index("sc.camera=bpy.data.objects['V24_25_");b=s.index('\ndef write',a)
s=s[:a]+"sc.camera=bpy.data.objects['V24_25_Kitchen_Roof'];sc['Version']='V24_25_HIGH_WC_WINDOWS_CLOSED_GATE_JOINT_ORDERED_ROOF_AND_MEASUREMENTS'\nnote=bpy.data.texts.new('V24_25_本次修正说明');note.write('五扇房内卫生间窗改1.8米高窗台、0.8米高磨砂双竖格窗，取消中横档并重切墙洞和窗台。内大门雕花柱后与厨房墙封紧接到檐底，去掉上版前侧平板。厨房瓦面修正为两片平直屋面并统一瓦片起排，保留屋脊镬耳与两房交谷。储藏房入口、过渡地带及檐廊统一现有浅灰地面材质。漫游顶栏新增测长度L、测面积P、撤销及CSV导出；点选模型表面，按Ctrl可吸附顶点，面积Enter完成，Esc回漫游。测量依当前模型米制尺寸；窗位和屋面为照片拟合。')\n"+s[b:]
(W/'v24_25_build.py').write_text(s,encoding='utf8')
s=(W/'v24_24_render.py').read_text('utf8').replace('V24_24','V24_25');a=s.index('for name in [');b=s.index(':\n',a);s=s[:a]+'for name in '+repr([v[0]for v in views])+s[b:];(W/'v24_25_render.py').write_text(s,encoding='utf8')
s=(W/'v24_25_render.py').read_text('utf8');s=s.replace("[('Interior',","[('WC_Right',(11.7,8.2,2.8),(13.,8.55,2.2),12,1.8),('WC_Left',(1.5,8.3,6.6),(0.,8.55,6.1),12,1.8),('Interior',");(W/'v24_25_render.py').write_text(s,encoding='utf8')
s=(W/'v24_24_physics_qa.py').read_text('utf8').replace('V24_24','V24_25');(W/'v24_25_physics_qa.py').write_text(s,encoding='utf8')
print('V25_CONTROLLER_STARTUP_BUILD_READY')
