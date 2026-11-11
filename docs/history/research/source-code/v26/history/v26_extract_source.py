from pathlib import Path
import sys,json,hashlib,numpy as np
W=Path(__file__).parent;D=W/'v26';sys.path[:0]=[str(W/'geomlibs'),str(W/'libs')]
import rhino3dm as rh
P=Path('E:/jz/纯场地版本.3dm');F=rh.File3dm.Read(str(P));C=json.loads(Path('E:/jz/JIA/Rebuild_V23/02_Data/Coordinate.json').read_text('utf8'));T=np.array(C['local_to_survey']);R=T[:3,:3];origin=T[:3,3];rows=[]
for j,o in enumerate(F.Objects):
 g=o.Geometry
 if not isinstance(g,rh.Mesh):continue
 v=np.array([[p.X,p.Y,p.Z] for p in g.Vertices],np.float64); v=(v-origin)@R
 faces=[]
 for a,b,c,d in g.Faces:
  faces.append([a,b,c])
  if c!=d:faces.append([a,c,d])
 f=np.array(faces,np.int32);uv=np.array([[p.X,p.Y] for p in g.TextureCoordinates],np.float64)
 mat=F.Materials[o.Attributes.MaterialIndex];tx=Path(mat.GetBitmapTexture().FileName);txlocal=Path('E:/jz/JIA/Rebuild_V6_Hybrid/03_Textures/Base')/tx.name
 assert txlocal.exists()
 fn=f'ORIGINAL_{j}.npz';np.savez_compressed(D/fn,v=v,f=f,uv=uv[f])
 rows.append({'file':fn,'source_id':str(o.Attributes.Id),'source_material':mat.Name,'texture':str(txlocal),'texture_sha256':hashlib.sha256(txlocal.read_bytes()).hexdigest(),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'triangles':len(f)})
with P.open('rb') as fp:h=hashlib.file_digest(fp,'sha256').hexdigest()
(D/'Original_Source_Index.json').write_text(json.dumps({'source':str(P),'sha256':h,'coordinate':C,'rows':rows},ensure_ascii=False,indent=2),encoding='utf8');print('SOURCE_EXTRACTED',sum(r['triangles'] for r in rows),h,flush=True)
