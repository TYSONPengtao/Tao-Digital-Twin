from pathlib import Path
import subprocess,json,sys,time
W=Path(__file__).parent;B='D:/AJAVIS01/RHINO7.12/PLUGINS/BLENDER/RUNING/blender.exe'
O=Path('E:/jz/JIA/Rebuild_V26_13')
assert json.loads((O/'Reports/V26_13_Native_QA.json').read_text('utf8'))['status']=='PASS'
jobs=[('build_fast',[],'Fast_Build'),('verify_fast',[],'Fast_Display_QA'),('gate_clearance_qa',[],'Gate_Clearance_QA'),('physics_qa',[],'Interior_Physics_QA'),('render',['--only','01_Gate_Whole','03_Right_Three_Faces','05_Faceted_Carving_Close'],None),('render',['--version','V26_12','--only','01_Gate_Whole','02_Left_Three_Faces','03_Right_Three_Faces','04_Low_Plinth_And_Sill'],None)]
if '--from-physics'in sys.argv:jobs=jobs[3:]
for i,(tag,args,report)in enumerate(jobs):
 log=W/('v26_13_job_'+str(i+1)+'_'+tag+'.log');print('START',tag,args,flush=True);t=time.monotonic()
 with log.open('wb')as f:r=subprocess.run([B,'--factory-startup','-b','-t','2','--python',str(W/('v26_13_'+tag+'.py')),'--',*args],stdout=f,stderr=subprocess.STDOUT,cwd=str(W.parent))
 if r.returncode:raise RuntimeError(str(log)+' exit '+str(r.returncode))
 if report and report!='Fast_Build':
  q=json.loads((O/'Reports'/('V26_13_'+report+'.json')).read_text('utf8'))
  if not q['status'].startswith('PASS')or q['failures']:raise AssertionError(str(log)+' '+str(q['failures'])[:1400])
 print('DONE',tag,round(time.monotonic()-t,1),'seconds',flush=True)
print('ALL_BATCH_CHECKS_AND_VIEWS_COMPLETE',flush=True)
