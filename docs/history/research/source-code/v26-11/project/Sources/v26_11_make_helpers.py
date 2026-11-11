from pathlib import Path
W=Path(__file__).parent
for name in['readback','protection_qa','geometry_qa','physics_qa','build_fast','verify_fast']:
 s=(W/f'v26_10_{name}.py').read_text('utf8').replace('v26_10','v26_11').replace('V26_10','V26_11').replace('V26.10','V26.11')
 if name=='readback':s=s.replace('V26.9 source remains byte identical','V26.10 source remains byte identical')
 (W/f'v26_11_{name}.py').write_text(s,'utf8')
D=W/'v26_11_perf';D.mkdir(exist_ok=True);(D/'roam_controller_fast.py').write_text((W/'v26_10_perf/roam_controller_fast.py').read_text('utf8').replace('Rebuild_V26_10','Rebuild_V26_11').replace('Architecture_Complete_V26_10','Architecture_Complete_V26_11'),'utf8')
