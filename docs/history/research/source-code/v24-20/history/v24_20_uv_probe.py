import bpy,numpy as np
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_20/Blender/Architecture_Complete_V24_20.blend');o=bpy.data.objects['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry'];v=np.array([o.matrix_world@p.co for p in o.data.vertices],dtype=np.float64);uv=o.data.uv_layers.active;bad=[]
for f in o.data.polygons:
 t=v[list(f.vertices)];nn=np.cross(t[1]-t[0],t[2]-t[0]);ll=np.linalg.norm(nn)
 if ll<1e-10 or abs(nn[2])/ll>.85:continue
 q=np.array([uv.data[li].uv[:]for li in f.loop_indices]);e=abs(q[:,1]-t[:,2]).max()
 if e>.001:bad.append({'i':f.index,'error':float(e),'area':ll/2,'normal':(nn/ll).tolist(),'xyz':t.tolist(),'uv':q.tolist()})
print('BAD_UV',len(bad),sum(r['area']for r in bad),sorted(bad,key=lambda r:-r['area'])[:8],flush=True)
