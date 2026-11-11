import sys,json,struct,hashlib,types,importlib,gc,collections
from pathlib import Path
W=Path(__file__).resolve().parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from scipy.spatial import cKDTree
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');E=O/'05_Export';D=O/'06_Report'
B=json.loads((O/'02_Data/Base_Index.json').read_text(encoding='utf-8'));M=json.loads((O/'02_Data/Materials.json').read_text(encoding='utf-8'));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf-8'))
a=np.radians(C['rotation_deg']);R=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
def sha(b):return hashlib.sha256(b).hexdigest()
def jdefault(x):
 if isinstance(x,np.generic):return x.item()
 raise TypeError(type(x).__name__)
def joint_match(source_xyz,source_uv,actual_xyz,actual_uv):
 # Same XYZ can occur at different atlas islands; nearest XYZ alone gives
 # incorrect UV failures on seam duplicates. Match both without welding.
 scale=np.array([2e-5,2e-5,2e-5,2e-6,2e-6]);s=np.column_stack((source_xyz,source_uv));q=np.column_stack((actual_xyz,actual_uv));tree=cKDTree(s/scale);_,idx=tree.query(q/scale)
 return float(np.max(np.linalg.norm(actual_xyz-source_xyz[idx],axis=1))),float(np.max(np.abs(actual_uv-source_uv[idx])))
expected={Path(b['texture']).name:dict(material='BASE_'+b['material_name'],path=b['texture'],sha256=sha(Path(b['texture']).read_bytes()),bytes=Path(b['texture']).stat().st_size) for b in B}
for k,m in M.items():
 if m.get('texture'):expected[Path(m['texture']).name]=dict(material=k,path=m['texture'],sha256=sha(Path(m['texture']).read_bytes()),bytes=Path(m['texture']).stat().st_size)
material_expected={'BASE_'+b['material_name']:dict(material='BASE_'+b['material_name'],path=b['texture'],sha256=sha(Path(b['texture']).read_bytes())) for b in B}
material_expected.update({k:dict(material=k,path=m['texture'],sha256=sha(Path(m['texture']).read_bytes())) for k,m in M.items() if m.get('texture')})
hash_expected={v['sha256']:v for v in expected.values()}
report=dict(expected_images=expected)

# GLB binary readback: embedded images, material-to-image links and base UV.
path=E/'Reality_Hybrid_V8_LOCAL.glb'
with path.open('rb') as f:
 magic,version,total=struct.unpack('<III',f.read(12));jl,jt=struct.unpack('<II',f.read(8));J=json.loads(f.read(jl));bl,bt=struct.unpack('<II',f.read(8));binstart=f.tell()
def segment(v):
 bv=J['bufferViews'][v]
 with path.open('rb') as f:f.seek(binstart+bv.get('byteOffset',0));return f.read(bv['byteLength'])
def accessor(k):
 ac=J['accessors'][k];bv=J['bufferViews'][ac['bufferView']];dt={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[ac['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[ac['type']];b=segment(ac['bufferView']);off=ac.get('byteOffset',0);stride=bv.get('byteStride',np.dtype(dt).itemsize*n)
 if stride==np.dtype(dt).itemsize*n:return np.frombuffer(b,dt,count=ac['count']*n,offset=off).reshape(-1,n).copy()
 return np.ndarray((ac['count'],n),dtype=dt,buffer=b,offset=off,strides=(stride,np.dtype(dt).itemsize)).copy()
g=dict(images=[],photo_material_links=[],base_mesh_uv=[],missing_uv_primitives=[])
for i,im in enumerate(J.get('images',[])):
 blob=segment(im['bufferView']) if 'bufferView' in im else b'';h=sha(blob);g['images'].append(dict(index=i,name=im.get('name'),mime=im.get('mimeType'),bytes=len(blob),sha256=h,original_byte_match=h in hash_expected,expected_material=hash_expected.get(h,{}).get('material')))
for i,m in enumerate(J.get('materials',[])):
 if m.get('name') not in material_expected:continue
 ei=material_expected[m['name']];tt=m.get('pbrMetallicRoughness',{}).get('baseColorTexture',{}).get('index');ii=J['textures'][tt]['source'] if tt is not None else None;image_rec=g['images'][ii] if ii is not None else None
 g['photo_material_links'].append(dict(material=m['name'],material_index=i,image_index=ii,linked_original_bytes=bool(image_rec and image_rec['sha256']==ei['sha256']),emission_texture=m.get('emissiveTexture',{}).get('index')))
for mesh in J.get('meshes',[]):
 for p in mesh['primitives']:
  if 'TEXCOORD_0' not in p['attributes']:g['missing_uv_primitives'].append(mesh.get('name'))
 if not mesh.get('name','').startswith('BASE_REALITY_'):continue
 bi=int(mesh['name'].split('_')[-1]);data=np.load(O/'02_Data'/f'Base_{bi}.npz');loc=(data['vertices']-origin)@R;tree=cKDTree(loc);mf=0;maxdist=0;maxuv=0;num=0
 for p in mesh['primitives']:
  pos=accessor(p['attributes']['POSITION']);pos=pos[:,[0,2,1]]*np.array([1,-1,1]);uv=accessor(p['attributes']['TEXCOORD_0']);uv[:,1]=1-uv[:,1];md,ud=joint_match(loc,data['uv'],pos,uv);maxdist=max(maxdist,md);maxuv=max(maxuv,ud);num+=len(pos);mf+=len(accessor(p['indices']))//3
 g['base_mesh_uv'].append(dict(name=mesh['name'],export_vertices=num,faces=mf,expected_faces=B[bi]['faces'],max_coordinate_difference_m=maxdist,max_uv_difference=maxuv,passed=mf==B[bi]['faces'] and maxdist<2e-5 and maxuv<2e-6))
g['passed']=len(g['photo_material_links'])==len(material_expected) and all(x['linked_original_bytes'] for x in g['photo_material_links']) and len(g['base_mesh_uv'])==5 and all(x['passed'] for x in g['base_mesh_uv']) and not g['missing_uv_primitives']
report['glb']=g;print('GLB',json.dumps(g),flush=True)
del J;gc.collect()

# FBX parse binary without importing or writing any export file.
pkg=types.ModuleType('readonly_fbx');pkg.__path__=[r'D:\AJAVIS01\RHINO7.12\PLUGINS\BLENDER\RUNING\5.1\scripts\addons_core\io_scene_fbx'];sys.modules['readonly_fbx']=pkg
parser=importlib.import_module('readonly_fbx.parse_fbx');root,version=parser.parse(str(E/'Reality_Hybrid_V8_LOCAL.fbx'))
def child(n,name):return next((x for x in n.elems if x.id==name),None)
def sval(v):return v.decode('utf-8',errors='replace') if isinstance(v,bytes) else v
objs=child(root,b'Objects').elems;byid={x.props[0]:x for x in objs};connections=child(root,b'Connections').elems
fc=dict(version=version,videos=[],photo_material_links=[],base_mesh_uv=[],missing_uv_geometry=[])
video_content={}
for n in objs:
 if n.id!=b'Video':continue
 blob=child(n,b'Content');blob=blob.props[0] if blob and blob.props else b'';filename=child(n,b'Filename') or child(n,b'FileName');h=sha(blob);video_content[n.props[0]]=h
 fc['videos'].append(dict(id=n.props[0],name=sval(n.props[1]),filename=sval(filename.props[0]) if filename else '',bytes=len(blob),sha256=h,original_byte_match=h in hash_expected,expected_material=hash_expected.get(h,{}).get('material')))
for n in objs:
 if n.id!=b'Material':continue
 name=sval(n.props[1]).split('\x00')[0]
 if name not in material_expected:continue
 tex_ids=[x.props[1] for x in connections if len(x.props)>=4 and x.props[0]==b'OP' and x.props[2]==n.props[0] and x.props[3]==b'DiffuseColor'];videos=[]
 for ti in tex_ids:videos.extend(x.props[1] for x in connections if x.props[0]==b'OO' and x.props[2]==ti and byid.get(x.props[1]) and byid[x.props[1]].id==b'Video')
 hashes=[video_content.get(vi) for vi in videos];fc['photo_material_links'].append(dict(material=name,texture_ids=tex_ids,video_ids=videos,linked_original_bytes=material_expected[name]['sha256'] in hashes))
for n in objs:
 if n.id!=b'Geometry':continue
 uvn=child(n,b'LayerElementUV')
 if uvn is None:fc['missing_uv_geometry'].append(sval(n.props[1]))
 name=sval(n.props[1]).split('\x00')[0]
 if not name.startswith('BASE_REALITY_'):continue
 bi=int(name.split('_')[-1]);data=np.load(O/'02_Data'/f'Base_{bi}.npz');uv=np.asarray(child(uvn,b'UV').props[0],float).reshape(-1,2);uix=np.asarray(child(uvn,b'UVIndex').props[0],int);pi=np.asarray(child(n,b'PolygonVertexIndex').props[0],int);fi=np.where(pi<0,-pi-1,pi);vi=np.asarray(child(n,b'Vertices').props[0],float).reshape(-1,3);expected_uv=data['uv'][fi];actual_uv=uv[uix];uvdiff=float(np.max(np.abs(expected_uv-actual_uv)));expectedloc=(data['vertices']-origin)@R;vdiff=float(np.max(np.abs(vi-expectedloc))) if vi.shape==expectedloc.shape else None
 fc['base_mesh_uv'].append(dict(name=name,vertices=len(vi),faces=int(np.sum(pi<0)),max_coordinate_difference_m=vdiff,max_uv_difference=uvdiff,passed=bool(uvdiff<2e-6 and vdiff is not None and vdiff<2e-5 and np.sum(pi<0)==B[bi]['faces'])))
fc['passed']=len(fc['photo_material_links'])==len(material_expected) and all(x['linked_original_bytes'] for x in fc['photo_material_links']) and len(fc['base_mesh_uv'])==5 and all(x['passed'] for x in fc['base_mesh_uv']) and not fc['missing_uv_geometry']
report['fbx']=fc;print('FBX',json.dumps(fc),flush=True)
del root,objs,byid,connections;gc.collect()

# OBJ/MTL exact relative photo links; root may be copying absent images now.
oc=dict(photo_material_links=[],base_mesh_uv=[],missing_face_uv=0,faces=0,vertices=0,uv=0)
mtl=E/'Reality_Hybrid_V8_LOCAL.mtl';maps={};cur=None
for line in mtl.read_text(encoding='utf-8').splitlines():
 if line.startswith('newmtl '):cur=line[7:].strip()
 elif line.startswith('map_Kd '):maps[cur]=line[7:].strip()
for name,ei in material_expected.items():
 tx=E/maps[name] if name in maps else None;ok=bool(tx and tx.is_file());oc['photo_material_links'].append(dict(material=name,reference=maps.get(name),exists=ok,bytes=tx.stat().st_size if ok else None,linked_original_bytes=sha(tx.read_bytes())==ei['sha256'] if ok else False))
current='';vv=[];uv=[];bf={};bvu={}
with (E/'Reality_Hybrid_V8_LOCAL.obj').open('r',encoding='utf-8',errors='replace') as f:
 for line in f:
  if line.startswith('o '):current=line[2:].strip()
  elif line.startswith('v '):vv.append(list(map(float,line.split()[1:4])));oc['vertices']+=1
  elif line.startswith('vt '):uv.append(list(map(float,line.split()[1:3])));oc['uv']+=1
  elif line.startswith('f '):
   toks=[q.split('/') for q in line.split()[1:]];oc['faces']+=1
   if not all(len(q)>1 and q[1] for q in toks):oc['missing_face_uv']+=1
   if current.startswith('BASE_REALITY_'):
    bf.setdefault(current,[]).append([int(q[0])-1 for q in toks]);bvu.setdefault(current,[]).append([int(q[1])-1 for q in toks])
vv=np.asarray(vv,float);uv=np.asarray(uv,float)
for name,faces in bf.items():
 bi=int(name.split('_')[-1]);data=np.load(O/'02_Data'/f'Base_{bi}.npz');loc=(data['vertices']-origin)@R;vi=np.array([q for f in faces for q in f]);ui=np.array([q for f in bvu[name] for q in f]);md,uvdiff=joint_match(loc,data['uv'],vv[vi],uv[ui]);oc['base_mesh_uv'].append(dict(name=name,faces=len(faces),max_coordinate_difference_m=md,max_uv_difference=uvdiff,passed=len(faces)==B[bi]['faces'] and md<2e-5 and uvdiff<2e-6))
oc['passed']=len(oc['photo_material_links'])==len(material_expected) and all(x['linked_original_bytes'] for x in oc['photo_material_links']) and len(oc['base_mesh_uv'])==5 and all(x['passed'] for x in oc['base_mesh_uv']) and not oc['missing_face_uv']
report['obj']=oc;print('OBJ',json.dumps(oc),flush=True)
report['passed']=all(report[k]['passed'] for k in ['glb','fbx','obj'])
(D/'V8_Exchange_Photo_Readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('TOTAL',report['passed'],flush=True)

assert report["passed"], "Exchange image/UV readback failed"
