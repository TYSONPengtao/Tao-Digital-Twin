"""Read the actual exported FBX, including per-node transforms and hinged leaves."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V12');p=O/'05_Export/Complete_Site_V12_LOCAL.fbx';I=json.loads((O/'02_Data/Modeled_Index_V12.json').read_text(encoding='utf8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(p))
meshes=[o for o in bpy.data.objects if o.type=='MESH'];triangles=sum(len(o.data.polygons) for o in meshes)
assert len(meshes)==len(I) and triangles==sum(r['triangles'] for r in I)
assert all(len(o.data.uv_layers)>0 and o.parent for o in meshes)
actual={json.loads(o.parent['Parameters'])['name']:o for o in meshes};assert len(actual)==len(I);node_errors=[];door_errors=[];points=[];name_aliases=[]
for row in I:
 o=actual[row['name']];co=np.empty(len(o.data.vertices)*3,dtype=np.float64);o.data.vertices.foreach_get('co',co);matrix=np.array(o.matrix_world);world=co.reshape(-1,3)@matrix[:3,:3].T+matrix[:3,3]
 if o.name!=row['name']+'_Geometry':name_aliases.append(dict(source_name=row['name'],imported_mesh_name=o.name,full_name_metadata_preserved=True))
 bounds=np.array([world.min(0),world.max(0)])
 expected=np.load(O/'02_Data'/row['file'])['vertices'];eb=np.array([expected.min(0),expected.max(0)])
 error=float(abs(bounds-eb).max());assert error<.0002,(row['name'],error);node_errors.append(error);points.append(bounds)
 assert len(o.data.uv_layers.active.data)==len(o.data.loops)
 uv=np.empty(len(o.data.loops)*2,dtype=np.float32);o.data.uv_layers.active.data.foreach_get('uv',uv);assert np.isfinite(uv).all()
 assert o.data.materials and all(m is not None for m in o.data.materials)
 e=row['element']
 if e.get('role')=='LEAF' and e.get('door_id'):
  group=o.parent;assert group.get('door_id')==e['door_id']
  pivot=np.array(e.get('hinge_origin_local_m',e.get('origin',[0,0,0])));err=float(abs(np.array(group.matrix_world.translation)-pivot).max());assert err<.0002,(e['door_id'],err);door_errors.append(err)
bounds=np.array([np.array(points)[:,0].min(0),np.array(points)[:,1].max(0)])
r=O/'06_Report/Modeled_Exchange_QA.json';Q=json.loads(r.read_text(encoding='utf8'));assert Q['status']=='PASS_GLB_READBACK'
err=float(abs(bounds-np.array(Q['bbox_LOCAL'])).max());assert err<.0002,err
image_paths=[];packed_images=[];texture_hashes={hashlib.sha256(ip.read_bytes()).hexdigest() for ip in (O/'03_Textures/Modeled_PBR').glob('*.png')}
for im in bpy.data.images:
 if im.source=='FILE':
  if im.packed_file:
   data=im.packed_file.data;digest=hashlib.sha256(data).hexdigest();assert digest in texture_hashes,(im.name,digest);packed_images.append(dict(name=im.name,bytes=len(data),sha256=digest))
  else:
   ip=Path(bpy.path.abspath(im.filepath));assert ip.is_file(),str(ip);image_paths.append(str(ip))
assert packed_images,'Expected actual embedded texture data on FBX readback'
h=hashlib.sha256()
with p.open('rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
Q.update(status='PASS',fbx_readback='PASS actual Blender import, per-node mesh bounds, hinged leaf pivots, finite UVs, material bindings and packed image bytes matching source texture SHA256',fbx_sha256=h.hexdigest(),fbx_meshes=len(meshes),fbx_triangles=triangles,fbx_bbox_error_m=err,fbx_all_nodes_bbox_max_error_m=max(node_errors),fbx_verified_door_pivots=len(door_errors),fbx_external_image_paths=image_paths,fbx_embedded_images=packed_images,fbx_name_aliases=name_aliases,ue5_imported=False)
r.write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');print('FBX readback PASS',len(meshes),triangles,'triangles; node error',max(node_errors),'door pivots',len(door_errors),'packed images',len(packed_images),flush=True)
