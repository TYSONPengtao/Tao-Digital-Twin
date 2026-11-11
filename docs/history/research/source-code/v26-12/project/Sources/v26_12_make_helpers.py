from pathlib import Path
import shutil
W=Path(__file__).parent
D=W/'v26_12_perf';D.mkdir(exist_ok=True)
for name in ['build_fast','verify_fast','physics_qa']:
 code=(W/f'v26_11_{name}.py').read_text('utf8').replace('v26_11','v26_12').replace('V26_11','V26_12')
 if name=='build_fast':
  code=code.replace('from v26_8_fast_display import apply','from v26_12_fast_display import apply').replace("bpy.data.texts.new('V26_8_流畅显示.py')","bpy.data.texts.new('V26_12_流畅显示.py')").replace("(W/'v26_8_fast_display.py').read_text", "(W/'v26_12_fast_display.py').read_text").replace("bpy.data.texts['V26_8_流畅显示.py']","bpy.data.texts['V26_12_流畅显示.py']")
 if name=='verify_fast':
  code=code.replace("Eevee8samples, half-resolution preview and no ray tracing saved","Eevee8samples, half-resolution preview and local AO saved")
  code=code.replace("and not sc.eevee.use_raytracing","and sc.eevee.use_raytracing and sc.eevee.use_fast_gi and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY'and sc.eevee.fast_gi_resolution=='2'and sc.eevee.ray_tracing_options.trace_max_roughness==0")
 (W/f'v26_12_{name}.py').write_text(code,'utf8')
O=Path('E:/jz/JIA/Rebuild_V26_12')
shutil.copy2(Path('E:/jz/JIA/Rebuild_V26_11/Reports/V26_11_Collision_Index.json'),O/'Reports/V26_12_Collision_Index.json')
(D/'roam_controller_fast.py').write_text((O/'Roam/roam_controller_fast.py').read_text('utf8'),'utf8')
code=(W/'v26_11_gate_clearance_qa.py').read_text('utf8').replace('v26_11','v26_12').replace('V26_11','V26_12')
code=code.replace("ch['proof']['gate']['panels']","ch['restored']").replace("other.startswith('V26_12_Gate_Gray_Relief_')","other.startswith('V26_12_Restored_')")
(W/'v26_12_gate_clearance_qa.py').write_text(code,'utf8')
