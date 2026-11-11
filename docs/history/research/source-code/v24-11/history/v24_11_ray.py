import bpy,sys,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _bounds
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_11/Blender/Architecture_Complete_V24_11.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();c=bpy.data.objects['V24_11_Kitchen_Continuous_Wall'];sc.camera=c;sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.resolution_percentage=100;view=c.data.view_frame(scene=sc);res=[]
for x,y in [(535,610),(565,624),(530,630),(552,642)]:
 s=x/1200;t=1-y/900;lr=view[0].lerp(view[1],1-t);ll=view[3].lerp(view[2],1-t);v=ll.lerp(lr,s);dr=(c.matrix_world.to_3x3()@v).normalized();ok,loc,no,idx,o,ma=sc.ray_cast(dg,c.matrix_world.translation,dr);r={'pixel':[x,y],'object':o.name if ok else None,'point':list(loc)if ok else None,'normal':list(no)if ok else None,'material':o.data.materials[o.data.polygons[idx].material_index].name if ok else None};res.append(r)
 if ok:print(json.dumps(r),flush=True)
 if ok and o.name=='SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry':
  import mathutils.geometry as gg
  f=o.data.polygons[idx];loop=list(f.loop_indices)[:3];verts=[o.data.vertices[o.data.loops[i].vertex_index].co for i in loop];uvs=[Vector((*o.data.uv_layers.active.data[i].uv,0))for i in loop];p=gg.barycentric_transform(o.matrix_world.inverted()@loc,*verts,*uvs);im=bpy.data.images['Photo_Dark_Stone_Courses.png'];w,h=im.size;ix=int((p.x%1)*(w-1));iy=int((p.y%1)*(h-1));pix=im.pixels[(iy*w+ix)*4:(iy*w+ix)*4+4];print('SURFACE_UV',list(p),'PIXEL',list(pix),'LOOPS',[list(q)for q in uvs],flush=True)
# Direct nearest scene surfaces surrounding the cyan corner.
for p0 in [(13.55,-8.75,-.5),(13.55,-8.69,-.62),(13.55,-8.6,-.55)]:
 for target in [(18,-4,7),(15,-15,10),(20,-8,1),(14,-8.75,0)]:
  p=Vector(p0)+Vector((.001,0,0));u=Vector(target)-p;dist=u.length;ok,loc,no,ix,o,ma=sc.ray_cast(dg,p,u.normalized(),distance=dist);print('SHADOW',p0,target,o.name if ok else None,list(loc)if ok else None,flush=True)
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render:continue
 lo,hi=_bounds(o)
 if hi[0]<13 or lo[0]>14.5 or hi[1]<-9.6 or lo[1]>-3.2:continue
 rows.append({'name':o.name,'bounds':[lo,hi]})
(W/'v24_11/Ray_Probe.json').write_text(json.dumps({'rays':res,'nearby':rows},indent=2),encoding='utf8')
