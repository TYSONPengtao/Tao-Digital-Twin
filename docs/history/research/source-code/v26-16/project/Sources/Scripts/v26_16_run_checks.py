from pathlib import Path
import subprocess,sys,json
W=Path(__file__).parent;B='D:/AJAVIS01/RHINO7.12/PLUGINS/BLENDER/RUNING/blender.exe';PY=sys.executable;tasks=[('build','blender'),('native_qa','blender'),('geometry_qa','python'),('render','blender'),('build_fast','blender'),('verify_fast','blender'),('physics_qa','blender'),('window_motion_qa','blender')];statuses=[]
for name,kind in tasks:
 script=W/('v26_16_'+name+'.py');cmd=[B,'--factory-startup','-b','-t','2','--python',str(script)]if kind=='blender'else[PY,str(script)];log=W/('v26_16_check_'+name+'.log');print('RUN',name,flush=True)
 with log.open('w',encoding='utf8')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 txt=log.read_text('utf8',errors='replace');ok=r.returncode==0 and'Traceback (most recent last)'not in txt and'Traceback (most recent call last)'not in txt
 report_name={'native_qa':'Native_QA','geometry_qa':'Geometry_QA','verify_fast':'Fast_Display_QA','physics_qa':'Interior_Physics_QA','window_motion_qa':'Window_Motion_QA'}.get(name)
 if report_name:
  qa=json.loads((Path('E:/jz/JIA/Rebuild_V26_16/Reports')/('V26_16_'+report_name+'.json')).read_text('utf8'));ok=ok and qa['status'].startswith('PASS')and not qa['failures']
 statuses.append({'step':name,'exit_code':r.returncode,'successful_process':ok,'log':str(log)});print('DONE',name,ok,flush=True)
 if not ok:raise RuntimeError(txt[-6000:])
(W/'v26_16/Check_Run.json').write_text(json.dumps(statuses,indent=2),'utf8');print('ALL_CHECK_PROCESSES_FINISHED',flush=True)
