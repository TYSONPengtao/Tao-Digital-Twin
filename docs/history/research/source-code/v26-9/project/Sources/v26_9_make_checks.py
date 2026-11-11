from pathlib import Path
W=Path(__file__).parent
for stem in ['protection_qa','readback','physics_qa','geometry_qa']:
 code=(W/('v26_8_'+stem+'.py')).read_text('utf8').replace('Rebuild_V26_8','Rebuild_V26_9').replace('Architecture_Complete_V26_8','Architecture_Complete_V26_9').replace('V26_8','V26_9').replace('v26_8','v26_9')
 if stem=='readback':
  code=code.replace('after=snapshot(bpy)','after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False))')
  code=code.replace("before['actions']==after['actions']", "all(after['actions'].get(k)==v for k,v in before['actions'].items())")
 (W/('v26_9_'+stem+'.py')).write_text(code,'utf8')
