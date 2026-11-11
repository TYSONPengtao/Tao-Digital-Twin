# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1')]
import numpy as np
out=W/'evidence_v3';root=W/'decoded_cases_v3'
for folder in root.iterdir():
 if not folder.is_dir():continue
 idx=json.loads((folder/'index.json').read_text(encoding='utf-8'));meta=idx['source'];name=meta['case'];srs=meta['SRS'];bpy.ops.wm.read_factory_settings(use_empty=True);arrays=[]
 for m in idx['meshes']:
  p=Path(m['ctm']).with_suffix('.npz')
  if p.exists():arrays.append((m,np.load(p)))
 if not arrays:continue
 # Geographical horizontal alignment; vertical offsets between free GNSS AT blocks are estimated.
 if name=='ui':offset=Vector((-4.04,-2.22,0));origin=Vector((-3.45191261,-3.90043098,0))
 elif name=='ZZCLDQ':offset=Vector((TAO_PRIVATE_SITE_014-TAO_PRIVATE_SITE_017,TAO_PRIVATE_SITE_011-TAO_PRIVATE_SITE_008,0));origin=Vector((-3.45191261,-3.90043098,0))
 else:offset=Vector((TAO_PRIVATE_SITE_001,5785.0,0));origin=Vector((-3.45191261,-3.90043098,0))
 R=Matrix.Rotation(-math.radians(19.65),4,'Z');meshobs=[]
 for k,(m,a) in enumerate(arrays):
  v=np.array(a['vertices']);f=a['faces'];v[:,:2]+=[offset.x-origin.x,offset.y-origin.y];rr=np.array([[math.cos(math.radians(19.65)),-math.sin(math.radians(19.65))],[math.sin(math.radians(19.65)),math.cos(math.radians(19.65))]]);v[:,:2]=v[:,:2]@rr
  me=bpy.data.meshes.new('Source3MX_'+str(k));me.from_pydata(v.tolist(),[],f.tolist());me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);meshobs.append(ob)
  if 'uv' in a:
   uv=me.uv_layers.new(name='OriginalSourceUV');values=a['uv']
   for loop in me.loops:uv.data[loop.index].uv=values[loop.vertex_index]
  texpath=Path(m['texture']);mat=bpy.data.materials.new('SourceTexture_'+str(k));mat.use_nodes=True;nt=mat.node_tree;em=nt.nodes.new('ShaderNodeEmission');nt.links.new(em.outputs[0],nt.nodes.get('Material Output').inputs[0])
  if texpath.exists():tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texpath));nt.links.new(tex.outputs['Color'],em.inputs[0])
  me.materials.append(mat)
 # Robust high roof percentile avoids treating unrelated elevation datums as house dimensions.
 pts=np.concatenate([np.array([v.co for v in o.data.vertices]) for o in meshobs]);mask=(pts[:,0]>3)&(pts[:,0]<14)&(pts[:,1]>1)&(pts[:,1]<10.6)
 if mask.sum()>30:dz=float(np.quantile(pts[mask,2],.96)-11.8)
 else:dz=float(np.quantile(pts[:,2],.7))
 for ob in meshobs:ob.location.z=-dz
 scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.view_settings.view_transform='Standard';scene.render.resolution_x=1800;scene.render.resolution_y=1800;scene.render.image_settings.file_format='PNG';cd=bpy.data.cameras.new('ReferenceCamera');cam=bpy.data.objects.new('ReferenceCamera',cd);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(-3,-6,300);cd.clip_end=5000;cd.type='ORTHO';cd.ortho_scale=52;scene.render.filepath=str(out/(name+'_3MX_Plan_Approx.png'));bpy.ops.render.render(write_still=True)
 lo=pts.min(axis=0);hi=pts.max(axis=0);cam.location=((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,float(hi[2]-dz+max(hi[0]-lo[0],hi[1]-lo[1])+100));cd.ortho_scale=float(max(hi[0]-lo[0],hi[1]-lo[1])*1.08);scene.render.filepath=str(out/(name+'_3MX_Context_Overview_Approx.png'));bpy.ops.render.render(write_still=True)
 scene.render.resolution_x=1800;scene.render.resolution_y=1200;cd.type='PERSP';cd.lens=32;cam.location=(-35,-35,25);cam.rotation_euler=(Vector((-3,-6,2))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/(name+'_3MX_SW_Approx.png'));bpy.ops.render.render(write_still=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(W/(name+'_3MX_Reference_Approx.blend')))
 print('REFERENCE',name,'meshparts',len(meshobs),'vertical_offset',dz,'HORIZONTAL_APPROXIMATE_NOT_SURVEY_CONTROL',flush=True)
