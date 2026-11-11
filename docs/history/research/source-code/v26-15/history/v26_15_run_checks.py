from pathlib import Path
import subprocess,sys,json
W=Path(__file__).parent;B='D:/AJAVIS01/RHINO7.12/PLUGINS/BLENDER/RUNING/blender.exe';PY=sys.executable;tasks=[('build','blender'),('native_qa','blender'),('geometry_qa','python'),('build_fast','blender'),('verify_fast','blender'),('physics_qa','blender'),('door_clearance_qa','blender'),('render','blender')];statuses=[]
for name,kind in tasks:
 script=W/('v26_15_'+name+'.py');cmd=[B,'--factory-startup','-b','-t','2','--python',str(script)]if kind=='blender'else[PY,str(script)]
 if name=='render':cmd+=['--','--only','01_Porch_Right_Z_Fighting','02_Porch_Left','06_Storage_Entry_Reverse','07_Gate_Rear_Floor_Recess','09_Stair_West_Front_Corner']
 log=W/('v26_15_check_'+name+'.log');print('RUN',name,flush=True)
 with log.open('w',encoding='utf8')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 txt=log.read_text('utf8',errors='replace');ok=r.returncode==0 and'Traceback (most recent call last)'not in txt;statuses.append({'step':name,'exit_code':r.returncode,'successful_process':ok,'log':str(log)});print('DONE',name,ok,flush=True)
 if not ok:raise RuntimeError(txt[-6000:])
(W/'v26_15/Check_Run.json').write_text(json.dumps(statuses,indent=2),'utf8');print('ALL_CHECK_PROCESSES_FINISHED',flush=True)
