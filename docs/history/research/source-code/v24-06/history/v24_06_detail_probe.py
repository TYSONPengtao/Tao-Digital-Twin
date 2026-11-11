import bpy,json,sys,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _bounds,_tree
R=W/'v24_06_probe';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_05/Blender/Architecture_Complete_V24_05.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
def clip(poly,axis,bound,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[axis]>=bound if greater else a[axis]<=bound;ib=b[axis]>=bound if greater else b[axis]<=bound
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*((bound-a[axis])/(b[axis]-a[axis])))
 return out
rows=[]
for o in bpy.data.objects:
 n=o.name
 if o.type!='MESH'or not(n.startswith('SITE_KITCHEN_')and any(k in n for k in ['ROOF','FASCIA','FLASHING','SHEATHING'])or n in ['V24_Kitchen_Curved_Gable_Coping','V24_Kitchen_Thin_Dark_Coping_Edge']):continue
 o.data.calc_loop_triangles();top=[]
 for tri in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in tri.vertices]
  for ax,b,g in [(0,6.95,True),(0,9.0,False),(1,-12.66,True),(1,-10.50,False)]:
   if p:p=clip(p,ax,b,g)
  if p:top.extend(p)
 if top:rows.append({'name':n,'highest_z':max(p.z for p in top)})
print('KITCHEN CONTACT HEIGHTS',json.dumps(rows),flush=True);(R/'Kitchen_Contact_Heights.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
o=bpy.data.objects['SITE_V12_REBUILT_COURT_0_-20_0_Geometry'];uv=o.data.uv_layers.active;data=[]
for f in o.data.polygons:
 if f.normal.z<.5:continue
 for li in f.loop_indices:
  p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;u=uv.data[li].uv;data.append([p.x,p.y,u.x,u.y])
d=np.array(data);A=np.column_stack([d[:,:2],np.ones(len(d))]);fit=np.linalg.lstsq(A,d[:,2:],rcond=None)[0];err=np.sqrt(np.mean((A@fit-d[:,2:])**2));print('PAVING UV FIT',fit.tolist(),err,flush=True)
floor=[]
for o in bpy.data.objects:
 if o.type!='MESH'or not any(m and m.name in ['M_V12_Terrain_Earth','M_V12_Court_Stone']for m in o.data.materials):continue
 lo,hi=_bounds(o)
 if hi[0]<-15 or lo[0]>8 or hi[1]<-18 or lo[1]>-10:continue
 floor.append((o,_tree(o)))
samples=[]
for x in [-13,-10,-6,-4,0,3,6]:
 for y in [-17,-16,-15,-14,-13,-12]:
  hits=[]
  for o,t in floor:
   h=t.ray_cast(Vector((x,y,5)),Vector((0,0,-1)),12)
   if h[0]is not None:hits.append({'object':o.name,'z':h[0].z,'material':o.data.materials[o.data.polygons[h[2]].material_index].name})
  if hits:samples.append({'x':x,'y':y,'hits':sorted(hits,key=lambda a:-a['z'])[:2]})
(R/'Floor_Samples.json').write_text(json.dumps({'samples':samples,'paving_uv_fit':fit.tolist(),'rms':err},indent=2),encoding='utf8')
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1600;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';ds=sc.display.shading;ds.light='STUDIO';ds.color_type='MATERIAL';ds.show_cavity=True;ds.cavity_type='BOTH';ds.show_shadows=True
c=bpy.data.objects.new('Front_Site_Plan',bpy.data.cameras.new('Front_Site_Plan'));sc.collection.objects.link(c);c.location=(-1,-12.5,25);c.rotation_euler=(Vector((-1,-12.5,0))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=32;sc.camera=c;sc.render.filepath=str(R/'Before_Front_Plan.png');bpy.ops.render.render(write_still=True);print('DETAIL PROBE COMPLETE',flush=True)
