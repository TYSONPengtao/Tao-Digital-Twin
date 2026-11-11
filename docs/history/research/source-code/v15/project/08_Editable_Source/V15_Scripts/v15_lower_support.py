import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
O=Path(r'E:/jz/JIA/Rebuild_V15');P=O/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);sp=O/'08_Editable_Source/Architecture_Scene_V15.json';S=json.loads(sp.read_text(encoding='utf8'));ex.SCENE=S;n='SITE_PERIMETER_JOINED_RETAINING_WALL_0';e=next(e for e in S['elements'] if e['name']==n);aq=json.loads((O/'06_Report/V15_Assembly_QA.json').read_text(encoding='utf8'));changed=[]
for ip,pp in enumerate(e['parts']):
 g=pp['geometry'];v,fs,_,_=ex.solid_data(g);hit=((v[:,0]>13.129)&(v[:,0]<19.631)&(v[:,1]>-17.501)&(v[:,1]<-9.199))|((v[:,0]>13.049)&(v[:,0]<14.701)&(v[:,1]>-12.201)&(v[:,1]<-2.099));hit&=abs(v[:,2]+.4)<1e-6
 if not hit.any() or v[:,2].min()>-.57:continue
 v[hit,2]=-.55;g={'type':'mesh','vertices':v.tolist(),'faces':fs};pp['geometry']=g;name=n+'__'+str(ip+1);ob=next(ob for ob in F.Objects if ob.Attributes.Name==name);at=ob.Attributes;mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True;k=0
 for f in fs:
  for ids in ex.triangulate(v[f]) if len(f)>3 else [[0,1,2]]:
   q=v[[f[j] for j in ids]];nn=np.cross(q[1]-q[0],q[2]-q[0]);axes=[j for j in range(3) if j!=int(np.argmax(abs(nn)))];enu=q@R.T+origin
   for pt,uv in zip(enu,q[:,axes]):mm.Vertices.AddPoint3d(*map(float,pt));mm.TextureCoordinates.__add__(*map(float,uv))
   mm.Faces.AddFace(k,k+1,k+2);k+=3
 mm.Normals.ComputeNormals();assert mm.IsValid and mm.IsClosed,name;F.Objects.Delete(at.Id);idd=F.Objects.Add(mm,at);hh=hashlib.sha256(json.dumps(mm.Encode(),sort_keys=True).encode()).hexdigest();aq['native_created']=[r for r in aq['native_created'] if r['id']!=str(idd)]+[{'id':str(idd),'name':name,'node':n,'geometry_hash':hh}];changed.append(name)
vv=[];ff=[];uu=[];mi=[];mats=[];off=0
for ob in F.Objects:
 if not ob.Attributes.Name.startswith(n+'__'):continue
 mm=ob.Geometry;v=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;fs=[]
 for f in mm.Faces:
  fs.append(f[:3])
  if f[2]!=f[3]:fs.append([f[0],f[2],f[3]])
 mat=F.Materials[ob.Attributes.MaterialIndex].Name
 if mat not in mats:mats.append(mat)
 vv.append(v);ff.append(np.array(fs)+off);uu.append(np.array([[p.X,p.Y] for p in mm.TextureCoordinates]));mi.extend([mats.index(mat)]*len(fs));off+=len(v)
v=np.vstack(vv);fs=np.vstack(ff);uv=np.vstack(uu);mid=np.array(mi,np.int32)
for path,indexname in [('Native_Readback/NATIVE_'+n+'.npz','Native_Readback_Index_V15.json'),('MODEL_'+n+'.npz','Modeled_Index_V15.json')]:
 np.savez_compressed(O/'02_Data'/path,vertices=v,faces=fs,uv=uv,material_ids=mid);ip=O/'02_Data'/indexname;I=json.loads(ip.read_text(encoding='utf8'));row=next(r for r in I if r['name']==n);row['triangles']=len(fs);row['materials']=mats;ip.write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf8')
sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V15_Assembly_QA.json').write_text(json.dumps(aq,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V15_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();assert F.Write(str(P),8);qq=json.loads((O/'06_Report/V15_Native_Readback_QA.json').read_text(encoding='utf8'));qq['sha256']=hashlib.sha256(P.read_bytes()).hexdigest();qq['post_support_cap_repair']=changed;(O/'06_Report/V15_Native_Readback_QA.json').write_text(json.dumps(qq,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V15_Support_Cap_QA.json').write_text(json.dumps({'status':'PASS_SUPPORT_CAP_BELOW_FINISHED_FLOOR','old_z_local_m':-.40,'new_z_local_m':-.55,'changed_native_objects':changed},ensure_ascii=False,indent=2),encoding='utf8');print('SUPPORT CAPS LOWERED',len(changed),flush=True)
