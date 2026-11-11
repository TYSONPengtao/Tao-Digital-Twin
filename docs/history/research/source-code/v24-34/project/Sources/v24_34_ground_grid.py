from pathlib import Path
import bpy,sys,json,types,numpy as np,time
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_34';O=Path('E:/jz/JIA/Rebuild_V24_34');P=O/'Blender/Architecture_Complete_V24_34.blend';bpy.ops.wm.open_mainfile(filepath=str(P));m=types.ModuleType('architecture_roam_physics');exec(bpy.data.texts['V24_21_碰撞控制.py'].as_string(),m.__dict__);a=np.load(D/'Final_Collision.npz');world=m.World(a['v'].tolist(),a['f'].tolist());lo=np.floor(a['v'][:,:2].min(0)).astype(int);hi=np.ceil(a['v'][:,:2].max(0)).astype(int);points=[]
for x in range(lo[0],hi[0]+1):
 for y in range(lo[1],hi[1]+1):
  top=world.top;used=[]
  for _ in range(30):
   z=world.down((x,y),top,world.bottom)
   if z is None:break
   top=z-.30;p=Vector((x,y,z));g=world.ground(p,up=.2,down=.3)
   if g is not None:p.z=g
   if world.clear(p)and all(abs(p.z-a)>.29 for a in used):points.append(list(p));used.append(p.z)
np.savez_compressed(D/'Roam_Ground_Grid.npz',p=np.array(points),bounds=np.array([lo,hi]));print('GROUND_GRID',len(points),lo,hi,flush=True)
