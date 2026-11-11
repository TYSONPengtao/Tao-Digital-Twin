from pathlib import Path
import subprocess,sys,json,time
W=Path(__file__).parent;B='D:/AJAVIS01/RHINO7.12/PLUGINS/BLENDER/RUNING/blender.exe';PY=sys.executable;O=Path('E:/jz/JIA/Rebuild_V26_14');jobs=[('prepare',[],None,'python'),('build',[],None,'blender'),('native_qa',[],'Native_QA','blender'),('geometry_qa',[],'Geometry_QA','python'),('build_fast',[],None,'blender'),('verify_fast',[],'Fast_Display_QA','blender'),('physics_qa',[],'Interior_Physics_QA','blender'),('render',[],None,'blender'),('render',['--version','V26_13'],None,'blender')]
if '--from-native'in sys.argv:jobs=jobs[2:]
for k,(tag,args,report,runtime)in enumerate(jobs):
 log=W/('v26_14_check_'+str(k+1)+'_'+tag+'.log');script=str(W/('v26_14_'+tag+'.py'));cmd=[PY,script,*args]if runtime=='python'else[B,'--factory-startup','-b','-t','2','--python',script,'--',*args]
 print('START',tag,args,flush=True);t=time.monotonic()
 with log.open('wb')as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,cwd=str(W.parent))
 if p.returncode:raise RuntimeError(str(log)+' failed')
 if tag=='build':assert(O/'Blender/Architecture_Complete_V26_14.blend').exists()and'V26_14_SAVED'in log.read_text('utf8',errors='replace')
 if report:
  q=json.loads((O/'Reports'/('V26_14_'+report+'.json')).read_text('utf8'))
  if not q['status'].startswith('PASS')or q['failures']:raise AssertionError(str(log)+' '+str(q['failures'])[:1400])
 print('DONE',tag,round(time.monotonic()-t,1),'seconds',flush=True)
print('BATCH_COMPLETE',flush=True)
