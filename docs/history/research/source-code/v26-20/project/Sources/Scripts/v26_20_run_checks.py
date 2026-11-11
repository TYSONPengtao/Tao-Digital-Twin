from pathlib import Path
import subprocess,sys,json
W=Path(__file__).parent;B='D:/AJAVIS01/RHINO7.12/PLUGINS/BLENDER/RUNING/blender.exe';O=Path('E:/jz/JIA/Rebuild_V26_20');statuses=[]
tasks=[('prepared_geometry','geometry_qa','python',['--prepared']),('build','build','blender',[]),('native_qa','native_qa','blender',[]),('geometry_qa','geometry_qa','python',[]),('render','render','blender',[]),('build_fast','build_fast','blender',[]),('verify_fast','verify_fast','blender',[]),('physics_qa','physics_qa','blender',[])]
for label,name,kind,args in tasks:
 script=W/('v26_20_'+name+'.py');cmd=([B,'--factory-startup','-b','-t','2','--python',str(script)]if kind=='blender'else[sys.executable,str(script)])+args;log=W/('v26_20_check_'+label+'.log');print('RUN',label,flush=True)
 with log.open('w',encoding='utf8')as f:result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 txt=log.read_text('utf8',errors='replace');ok=result.returncode==0 and'Traceback (most recent call last)'not in txt;rn={'native_qa':'Native_QA','geometry_qa':'Geometry_QA','verify_fast':'Fast_Display_QA','physics_qa':'Interior_Physics_QA'}.get(label)
 if ok and rn:
  qa=json.loads((O/'Reports'/('V26_20_'+rn+'.json')).read_text('utf8'));ok=qa['status'].startswith('PASS')and not qa['failures']
 statuses.append({'step':label,'exit_code':result.returncode,'successful_process':ok,'log':str(log)});print('DONE',label,ok,flush=True)
 if not ok:raise RuntimeError(txt[-2500:])
(W/'v26_20/Check_Run.json').write_text(json.dumps(statuses,indent=2),'utf8');print('ALL_CHECK_PROCESSES_FINISHED',flush=True)
