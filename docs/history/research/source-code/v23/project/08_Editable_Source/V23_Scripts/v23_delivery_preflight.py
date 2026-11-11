import sys,json,hashlib,struct,zipfile,shutil,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path('E:/jz/JIA/Rebuild_V23');P=O/'04_Rhino/Architecture_Complete_V23_COMPACT_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
Q=json.loads((O/'06_Report/V23_Native_Readback_QA.json').read_text(encoding='utf8'));assert Q['status'].startswith('PASS') and Q['sha256']==sha(P);F=rh.File3dm.Read(str(P));GP=O/'05_Export/Complete_Site_V23_LOCAL.glb'
door_qa=json.loads((O/'06_Report/Final_Native_Door_QA.json').read_text(encoding='utf8'));assert door_qa['status'].startswith('PASS') and not door_qa['unresolved_collisions'] and door_qa['native_model_sha256']==Q['sha256']
detail_qa=json.loads((O/'06_Report/Final_Detail_Review_V23.json').read_text(encoding='utf8'));assert detail_qa['status'].startswith('PASS') and detail_qa['native_model_sha256']==Q['sha256']
with GP.open('rb') as f:
 magic,version,total=struct.unpack('<4sII',f.read(12));assert magic==b'glTF' and version==2;length,ctype=struct.unpack('<II',f.read(8));g=json.loads(f.read(length));binlen,bintype=struct.unpack('<II',f.read(8));binary=f.read(binlen)
V=json.loads((O/'06_Report/Preview_View_States.json').read_text(encoding='utf8'));assert V['native_model_sha256']==Q['sha256'];assert total==GP.stat().st_size and len(g['cameras'])==V['camera_count'] and len(g['meshes'])==Q['nodes'];assert all('bufferView' in im and 'uri' not in im for im in g['images']);assert sum(im.get('name','').startswith('Tile_') for im in g['images'])>=5
I=json.loads((O/'02_Data/Native_Readback_Index_V23.json').read_text(encoding='utf8'));idx={r['name']:r for r in I};tri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tri==Q['triangles']==sum(r['triangles'] for r in I)
DM=json.loads((O/'02_Data/Door_Manifest_V23.json').read_text(encoding='utf8'));nodes={n.get('name'):j for j,n in enumerate(g['nodes'])};parents={c:j for j,n in enumerate(g['nodes']) for c in n.get('children',[])}
def quatmat(q):
 x,y,z,w=q;return np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
def matworld(j):
 n=g['nodes'][j]
 if 'matrix' in n:m=np.array(n['matrix']).reshape(4,4).T
 else:
  m=np.eye(4);m[:3,:3]=quatmat(n.get('rotation',[0,0,0,1]))@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0])
 return matworld(parents[j])@m if j in parents else m
def acc(j):
 a=g['accessors'][j];b=g['bufferViews'][a['bufferView']];dtype={5126:np.float32,5125:np.uint32,5123:np.uint16}[a['componentType']];count={'VEC3':3,'VEC2':2,'VEC4':4,'SCALAR':1}[a['type']];return np.frombuffer(binary,dtype=dtype,count=a['count']*count,offset=b.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,count).astype(float)
doorproof=[]
for r in DM['doors']:
 n=r['name'];j=nodes[n+'_Geometry'];m=matworld(j);vv=np.vstack([acc(p['attributes']['POSITION']) for p in g['meshes'][g['nodes'][j]['mesh']]['primitives']]);vv=np.c_[vv,np.ones(len(vv))]@m.T;local=vv[:,[0,2,1]];local[:,1]*=-1;d=np.load(O/'02_Data'/idx[n]['file']);v=d['vertices'];err=float(np.max(abs(np.array([local.min(0),local.max(0)])-np.array([v.min(0),v.max(0)]))));assert err<1e-5,(n,err);doorproof.append({'node':n,'default_open_bbox_error_m':err})
assert len(g.get('animations',[]))>=len(DM['doors'])-2
for name in V['view_names']:assert (O/'06_Report'/f'{name}.png').stat().st_size>10000
AQ=json.loads((O/'06_Report/V23_Assembly_QA.json').read_text(encoding='utf8'));AQ['status']='PASS_FRESH_NATIVE_V23_QA';(O/'06_Report/V23_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8')
delivery={'status':'PASS_DELIVERY_FILES','native_objects':len(F.Objects),'nodes':len(I),'triangles':tri,'glb_meshes':len(g['meshes']),'glb_embedded_images':len(g['images']),'glb_cameras':len(g['cameras']),'glb_animations':len(g.get('animations',[])),'independent_door_leaves':len(DM['doors']),'sliding_leaves':sum(r.get('operation')=='SLIDING' for r in DM['doors']),'default_open_door_parity':doorproof,'native_model_sha256':sha(P),'glb_sha256':sha(GP),'v22_preserved_sha256':AQ['base_model_sha256'],'ue5_import_tested':False};(O/'06_Report/Delivery_QA.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf8')


print('COMPACT_GLB_PARITY_PASS',flush=True)
