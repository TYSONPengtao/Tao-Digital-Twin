from pathlib import Path
import shutil
W=Path(__file__).parent
O=Path('E:/jz/JIA/Rebuild_V26_13')
D=W/'v26_13_perf';D.mkdir(exist_ok=True)
shutil.copy2(O/'Roam/roam_controller_fast.py',D/'roam_controller_fast.py')
for tag in ['fast_display','build_fast','verify_fast','physics_qa','gate_clearance_qa']:
 s=(W/('v26_12_'+tag+'.py')).read_text('utf8').replace('V26_12','V26_13').replace('v26_12','v26_13').replace('V26.12','V26.13')
 if tag=='verify_fast':s=s.replace('for V26.11.','for V26.13.')
 if tag=='gate_clearance_qa':
  s=s.replace("[q['name']for q in ch['restored']]","[q['name']for q in ch['panels']]+[n for n in ch['retained_headers']if n!='SITE_V21_GATE_REFERENCE_LAYER_05_Geometry']+[ch['waist']]")
  s=s.replace("if other.startswith('V26_13_Restored_'):continue","if other.startswith(('V26_13_Photo_Fit_','V26_12_Restored_'))or other==ch['waist']:continue")
  s=s.replace('new piers,21 signed-relief inserts, header and platform','new faceted piers,21 signed-relief inserts, waist, header and narrow platform')
 if tag=='physics_qa':
  s=s.replace('# Actual MB7 ground, outside',"""# Trace the newly exposed ground alongside the reduced step footprint.
for label,a,b in [('left_apron',(4.40,-12.30),(5.20,-12.30)),('right_apron',(8.80,-12.30),(8.00,-12.30))]:
 w=Walker(world,(*a,-.50));rec=w.recoveries;ok,tr=go(w,b,limit=6.);traces['gate_'+label]=tr
 ck('Ground beside reduced gate apron remains continuously supported '+label,ok and w.grounded and w.recoveries==rec and all(p[2]>-.72 for p in tr),position=list(w.p),recoveries=w.recoveries)
# Actual MB7 ground, outside""")
 (W/('v26_13_'+tag+'.py')).write_text(s,'utf8')
print('V26_13_CHECKS_ADAPTED')
