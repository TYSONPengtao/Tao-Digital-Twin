import bpy,numpy as np
from pathlib import Path
D=Path(__file__).parent/'v24_10';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_09/Blender/Architecture_Complete_V24_09.blend');V=[];F=[];off=0
for o in bpy.data.objects:
 if o.type!='MESH'or not(o.name.startswith('SITE_V14_ORIGINAL_EXTERIOR_')or 'REBUILT_ROAD'in o.name or o.name=='SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE_Geometry'):continue
 v=np.array([o.matrix_world@p.co for p in o.data.vertices]);o.data.calc_loop_triangles();f=np.array([p.vertices for p in o.data.loop_triangles]);t=v[f];p=t.mean(1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1),1e-20)[:,None];ok=(p[:,0]>11)&(p[:,0]<25)&(p[:,1]>-21)&(p[:,1]<-7)&(p[:,2]<-1)&(abs(n[:,2])>.35);ff=f[ok];ids,inv=np.unique(ff,return_inverse=True);V.append(v[ids]);F.append(inv.reshape(-1,3)+off);off+=len(ids)
np.savez_compressed(D/'Retained_Ground_Reference.npz',v=np.concatenate(V),f=np.concatenate(F));print('GROUND_REFERENCE',off,flush=True)
