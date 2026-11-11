"""Read actual GLB buffers, hierarchy, textures and transformed geometry bounds."""
import sys,json,struct,hashlib,math,collections
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'np1'));import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V12');P=O/'05_Export/Complete_Site_V12_LOCAL.glb';raw=P.read_bytes();magic,version,n=struct.unpack_from('<4sII',raw,0);assert magic==b'glTF' and version==2 and n==len(raw)
chunks=[];offset=12
while offset<n:
 size,typ=struct.unpack_from('<I4s',raw,offset);chunks.append((typ,raw[offset+8:offset+8+size]));offset+=8+size
D=json.loads(next(v for k,v in chunks if k==b'JSON'));binary=next(v for k,v in chunks if k==b'BIN\0');assert D['buffers'][0]['byteLength']<=len(binary)
def accessor(i):
 a=D['accessors'][i];assert 'sparse' not in a;b=D['bufferViews'][a['bufferView']];dt={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}[a['componentType']];cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];off=b.get('byteOffset',0)+a.get('byteOffset',0);size=np.dtype(dt).itemsize;arr=np.ndarray((a['count'],cols),dt,buffer=binary,offset=off,strides=(b.get('byteStride',size*cols),size));assert np.all(np.isfinite(arr));return arr
parents={c:i for i,o in enumerate(D['nodes']) for c in o.get('children',[])}
def local(o):
 if 'matrix' in o:return np.array(o['matrix']).reshape(4,4).T
 x,y,z,w=o.get('rotation',[0,0,0,1]);r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]);a=np.eye(4);a[:3,:3]=r@np.diag(o.get('scale',[1,1,1]));a[:3,3]=o.get('translation',[0,0,0]);return a
world={}
def matrix(i):
 if i not in world:world[i]=(matrix(parents[i]) if i in parents else np.eye(4))@local(D['nodes'][i])
 return world[i]
triangles=0;mesh_nodes=[];points=[];material_refs=[];node_bounds={}
for i,node in enumerate(D['nodes']):
 if 'mesh' not in node:continue
 mesh_nodes.append(node['name']);T=matrix(i);localbounds=[]
 for prim in D['meshes'][node['mesh']]['primitives']:
  assert prim.get('mode',4)==4;v=accessor(prim['attributes']['POSITION']);uv=accessor(prim['attributes']['TEXCOORD_0']);assert len(uv)==len(v)
  normal=accessor(prim['attributes']['NORMAL']);assert len(normal)==len(v);length=np.linalg.norm(normal,axis=1);assert np.all((length>.95)&(length<1.05)),node['name']
  if 'indices' in prim:ids=accessor(prim['indices']);assert int(ids.max())<len(v);triangles+=len(ids)//3
  else:triangles+=len(v)//3
  q=v@T[:3,:3].T+T[:3,3];q=q[:,[0,2,1]]*np.array([1,-1,1]);localbounds.append([q.min(0),q.max(0)]);points.append([q.min(0),q.max(0)]);material_refs.append(prim['material'])
 node_bounds[node['name']]=[np.array(localbounds)[:,0].min(0),np.array(localbounds)[:,1].max(0)]
I=json.loads((O/'02_Data/Modeled_Index_V12.json').read_text(encoding='utf8'));assert len(mesh_nodes)==len(I);assert triangles==sum(r['triangles'] for r in I)
expected=[];node_errors=[]
for row in I:
 v=np.load(O/'02_Data'/row['file'])['vertices'];bounds=[v.min(0),v.max(0)];expected.append(bounds);node_error=float(np.max(abs(np.array(node_bounds[row['name']+'_Geometry'])-bounds)));assert node_error<.0002,(row['name'],node_error);node_errors.append(node_error)
bbox=[np.array(points)[:,0].min(0),np.array(points)[:,1].max(0)];eb=[np.array(expected)[:,0].min(0),np.array(expected)[:,1].max(0)];error=float(np.max(abs(np.array(bbox)-eb)));assert error<.0002,error
textures=[]
for im in D.get('images',[]):
 assert 'bufferView' in im and 'uri' not in im;bv=D['bufferViews'][im['bufferView']];v=binary[bv.get('byteOffset',0):bv.get('byteOffset',0)+bv['byteLength']];assert len(v)>100 and (v.startswith(b'\x89PNG\r\n\x1a\n') or v.startswith(b'\xff\xd8'));textures.append({'name':im.get('name',''),'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()})
assert textures,'Expected embedded modeled PBR textures'
nodes={o['name']:i for i,o in enumerate(D['nodes'])};door_checks=[]
for row in I:
 e=row['element']
 if e.get('role')=='LEAF' and e.get('door_id'):
  ni=nodes[row['name']];node=D['nodes'][ni];assert node.get('extras',{}).get('door_id')==e['door_id'];pivot=e.get('hinge_origin_local_m',e.get('origin',[0,0,0]));q=matrix(ni)[:3,3];q=q[[0,2,1]]*np.array([1,-1,1]);assert np.max(abs(q-pivot))<.0002,(e['door_id'],q,pivot);door_checks.append(e['door_id'])
p=O/'06_Report/Modeled_Exchange_QA.json';report=json.loads(p.read_text());report.update(status='PASS_GLB_READBACK',glb_sha256=hashlib.sha256(raw).hexdigest(),mesh_nodes=len(mesh_nodes),triangles_readback=triangles,bbox_LOCAL=[q.tolist() for q in bbox],bbox_max_error_m=error,all_nodes_bbox_max_error_m=max(node_errors),embedded_images=len(textures),images=textures,retained_door_leaf_pivots=len(door_checks),no_external_image_dependencies=True,fbx_readback='Pending companion Blender import verification');p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('GLB readback PASS',len(mesh_nodes),triangles,'triangles;',len(textures),'embedded textures; bbox error',error,flush=True)
