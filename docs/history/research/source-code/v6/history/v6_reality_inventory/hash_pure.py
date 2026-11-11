# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys,json,hashlib,struct,csv
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'libs'));import rhino3dm as r
O=Path(__file__).resolve().parent
P=Path(r'E:\jz\纯场地版本.3dm');F=r.File3dm.Read(str(P))
def filehash(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def coordinatehash(items,n):
 h=hashlib.sha256();h.update(struct.pack('<Q',len(items)))
 for a in items:
  vals=[a.X,a.Y] if n==2 else [a.X,a.Y,a.Z]
  h.update(struct.pack('<'+'d'*n,*vals))
 return h.hexdigest()
result=dict(source=str(P),source_sha256=filehash(P),units=str(F.Settings.ModelUnitSystem),coordinate_srs='ENU:TAO_PRIVATE_SITE_003,TAO_PRIVATE_SITE_024',srs_origin=[0,0,0],coordinate_metadata=r'E:\yun\OBJ\metadata.xml',geometry_hash_schema='vertex/uv/normals: item count uint64 LE then original coordinate float64 LE; faces: count uint64 LE then A,B,C,D int32 LE; no vertex welding, face retriangulation or UV regeneration',objects=[],textures=[])
for i,o in enumerate(F.Objects):
 g=o.Geometry;a=o.Attributes;h=hashlib.sha256();h.update(struct.pack('<Q',len(g.Faces)))
 for q in g.Faces:h.update(struct.pack('<iiii',*q))
 mr=F.Materials[a.MaterialIndex];t=mr.GetBitmapTexture()
 rr=dict(index=i,object_id=str(a.Id),vertices=len(g.Vertices),faces=len(g.Faces),uv=len(g.TextureCoordinates),normals=len(g.Normals),vertices_sha256=coordinatehash(g.Vertices,3),faces_sha256=h.hexdigest(),uv_sha256=coordinatehash(g.TextureCoordinates,2),normals_sha256=coordinatehash(g.Normals,3),material_index=a.MaterialIndex,material_source=str(a.MaterialSource),material_id=str(mr.Id),material_name=mr.Name,texture_source=t.FileName,texture_enabled=t.Enabled,layer_index=a.LayerIndex)
 result['objects'].append(rr);print(i,rr['vertices'],rr['faces'],rr['vertices_sha256'],flush=True)
for t in sorted(set(x['texture_source'] for x in result['objects'])):
 p=Path(t);result['textures'].append(dict(source=t,relative_path='textures/'+p.name,exists=p.is_file(),bytes=p.stat().st_size,sha256=filehash(p),also_embedded=t in list(F.EmbeddedFilePaths())))
(O/'Pure_Baseline_Hashes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'Pure_Texture_Map.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=result['textures'][0].keys());wr.writeheader();wr.writerows(result['textures'])
print('wrote',flush=True)
