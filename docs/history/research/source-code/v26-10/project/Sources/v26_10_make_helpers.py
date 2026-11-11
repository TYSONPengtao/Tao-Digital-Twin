from pathlib import Path
W=Path(__file__).parent;(W/'v26_10_perf').mkdir(exist_ok=True)
for stem in ['protection_qa','readback','physics_qa','geometry_qa','render','build_fast','verify_fast']:
 s=(W/('v26_9_'+stem+'.py')).read_text('utf8').replace('Rebuild_V26_9','Rebuild_V26_10').replace('Architecture_Complete_V26_9','Architecture_Complete_V26_10').replace('V26_9','V26_10').replace('v26_9','v26_10')
 # The overcast world and proven fast profile retain their source names.
 if stem=='build_fast':
  s=s.replace('from v26_8_fast_display import apply','from v26_8_fast_display import apply')
 (W/('v26_10_'+stem+'.py')).write_text(s,'utf8')
(W/'v26_10_perf/roam_controller_fast.py').write_text((W/'v26_9_perf/roam_controller_fast.py').read_text('utf8').replace('Rebuild_V26_9','Rebuild_V26_10').replace('Architecture_Complete_V26_9','Architecture_Complete_V26_10'),'utf8')
