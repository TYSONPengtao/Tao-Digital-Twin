import sys,json,math,collections,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]
import numpy as np,rhino3dm as rh
O=W/'v15';O.mkdir(exist_ok=True);B=Path(r'E:/jz/JIA/Rebuild_V14');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V14.json').read_text(encoding='utf8'));I=json.loads((B/'02_Data/Native_Readback_Index_V14.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']}
rows=[]
for row in I:
 d=np.load(B/'02_Data'/row['file']);v=d['vertices'];f=d['faces'];b=np.array([v.min(0),v.max(0)]);n=row['name'];e=E[n];r={'name':n,'bbox':b.tolist(),'layer':e['layer'],'parts':len(e['parts']),'definition':e.get('definition'),'triangles':len(f)};rows.append(r)
 if 'F3' in n or 'ROOF' in n or 'INNER_GATE' in n or 'COURT' in n or 'RAMP' in n:print(json.dumps(r),flush=True)
(O/'Nodes.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V14_ALIGNED_ENU.3dm'));mr=[]
for ob in F.Objects:
 g=ob.Geometry
 if not isinstance(g,rh.Mesh):continue
 v=(np.array([[p.X,p.Y,p.Z] for p in g.Vertices.ToPoint3dArray()])-origin)@R;fs=[]
 for f in g.Faces:
  fs.append(f[:3])
  if f[2]!=f[3]:fs.append([f[0],f[2],f[3]])
 t=v[np.array(fs)];nor=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);vol=float(np.einsum('ij,ij->i',t[:,0]-v.mean(0),nor).sum()/6);nn=np.array([[p.X,p.Y,p.Z] for p in g.Normals])@R;lens=np.linalg.norm(nn,axis=1);bounds=np.array([v.min(0),v.max(0)])
 r={'name':ob.Attributes.Name,'id':str(ob.Attributes.Id),'closed':g.IsClosed,'valid':g.IsValid,'volume_signed_m3':vol,'triangles':len(t),'normal_count':len(nn),'normal_len_min':float(lens.min()) if len(nn) else None,'normal_len_max':float(lens.max()) if len(nn) else None,'bbox':bounds.tolist(),'material':F.Materials[ob.Attributes.MaterialIndex].Name if ob.Attributes.MaterialIndex>=0 else None};mr.append(r)
 if g.IsClosed and vol<0:print('INWARD',json.dumps(r),flush=True)
(O/'Native_Mesh_Audit.json').write_text(json.dumps(mr,indent=2),encoding='utf8')
q={'total_meshes':len(mr),'closed_inward':sum(r['closed'] and r['volume_signed_m3']<0 for r in mr),'zero_normals':sum(r['normal_len_min']==0 for r in mr),'negative_names':dict(collections.Counter(r['name'].rsplit('__',1)[0] for r in mr if r['closed'] and r['volume_signed_m3']<0))};(O/'Probe_Summary.json').write_text(json.dumps(q,indent=2),encoding='utf8');print('SUMMARY',json.dumps(q),flush=True)
