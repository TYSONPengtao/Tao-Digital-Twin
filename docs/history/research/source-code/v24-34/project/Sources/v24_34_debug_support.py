import bpy,types,json,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_34';P='E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend';bpy.ops.wm.open_mainfile(filepath=P);m=types.ModuleType('physics');exec(bpy.data.texts['V24_21_碰撞控制.py'].as_string(),m.__dict__);a=np.load(D/'Final_Collision.npz');world=m.World(a['v'].tolist(),a['f'].tolist());r=json.loads(Path('E:/jz/JIA/Rebuild_V24_34/Reports/V24_34_Exterior_Physics_QA.json').read_text())
for row in r['checks']:
 if not row.get('blocked'):continue
 b=row['blocked'];p=Vector(b['at']);d=Vector(b['target'])-p;d.z=0;d.normalize();trial=p+d*.015;z=world.ground(trial)
 if z is not None:trial.z=z
 print('DEBUG',row['check'],list(p),'trial',list(trial),'g',z,'clear',world.clear(trial),flush=True)
 for i in range(7):
  h=m.RADIUS+(m.HEIGHT-2*m.RADIUS)*i/6;c=trial+Vector((0,0,h))
  for loc,no,idx,dist in world.bvh.find_nearest_range(c,m.RADIUS-m.SKIN):
   if no.z>=m.WALKABLE and loc.z<=trial.z+.008:continue
   print(' HIT',i,'loc',list(loc),'normal',list(no),'dist',dist,'height',loc.z-trial.z,'tri',idx,flush=True)
