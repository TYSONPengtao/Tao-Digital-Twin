from pathlib import Path
W=Path(__file__).parent
for name,src in [('interior_physics_qa','v24_36_interior_physics_qa.py'),('measure_math_qa','v24_34_measure_math_qa.py'),('launcher_smoke','v24_34_launcher_smoke.py')]:
 s=(W/src).read_text('utf8').replace('V24_36','V24_37')if src.startswith('v24_36')else(W/src).read_text('utf8').replace('V24_34','V24_37')
 if name=='launcher_smoke':
  s=s.replace("stage=9;finish();return None","stage=90;return .3")
  needle=" except Exception:errors.append(traceback.format_exc());finish();return None"
  extra="""  if stage==90:
   with bpy.context.temp_override(window=win,area=area,region=region):bpy.ops.arch_roam.preset(location='PTJIA6_ROAD')
   op.yaw=math.pi;op.pitch=.12;op.scene.arch_roam.distance=2.5;stage=91;return .5
  if stage==91:
   ck('PTJIA6 road preset seats the same human on the new context',op.walker.grounded and op.walker.p.y>98,position=list(op.walker.p));move_start=op.walker.p.copy();key('UP_ARROW');stage=92;return .7
  if stage==92:
   key('UP_ARROW','RELEASE');ck('Actual keyboard walks in PTJIA6 more than 100m from origin',op.walker.grounded and (op.walker.p-move_start).length>.45 and op.walker.p.length>100,position=list(op.walker.p));stage=93;return 4.
  if stage==93:
   with bpy.context.temp_override(window=win,area=area,region=region):bpy.ops.screen.screenshot(filepath=str(R/'V24_37_PTJIA6_Road_Roam_UI.png'),check_existing=False)
   with bpy.context.temp_override(window=win,area=area,region=region):bpy.ops.arch_roam.preset(location='PTJIA6_FIELD')
   stage=94;return .5
  if stage==94:
   ck('PTJIA6 field preset has real support far beyond the old origin',op.walker.grounded and op.walker.p.x<-380,position=list(op.walker.p));move_start=op.walker.p.copy();tap('SPACE');stage=95;return .3
  if stage==95:
   ck('Real Space jumps on distant PTJIA6 field',not op.walker.grounded and op.walker.vz>0,position=list(op.walker.p));stage=96;return 1.1
  if stage==96:
   ck('Real PTJIA6 field jump lands without origin reset',op.walker.grounded and op.walker.recoveries==0 and op.walker.p.x<-380,position=list(op.walker.p));tap('HOME');stage=97;return .4
  if stage==97:
   ck('Home returns the person to the preserved courtyard',op.walker.grounded and abs(op.walker.p.x-6.5)<.1 and abs(op.walker.p.y+4.8)<.1,position=list(op.walker.p));stage=9;finish();return None
"""
  assert needle in s;s=s.replace(needle,extra+needle)
 compile(s,str(W/('v24_37_'+name+'.py')),'exec');(W/('v24_37_'+name+'.py')).write_text(s,encoding='utf8')
print('QA_SCRIPTS_PREPARED')
