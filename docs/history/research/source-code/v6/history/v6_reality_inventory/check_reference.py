import sys,json,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'libs'));import rhino3dm as r
O=Path(__file__).resolve().parent
P=Path(r'E:\jz\JIA\Rebuild_V5\04_ContextCapture\Production_1QK_Local_REFERENCE.3dm');f=r.File3dm.Read(str(P))
result=dict(path=str(P),units=str(f.Settings.ModelUnitSystem),objects=len(f.Objects),geometry=[],materials=[])
for o in f.Objects:
 g=o.Geometry
 if isinstance(g,r.Mesh):
  b=g.GetBoundingBox();result['geometry'].append(dict(vertices=len(g.Vertices),faces=len(g.Faces),uv=len(g.TextureCoordinates),material_index=o.Attributes.MaterialIndex,material_source=str(o.Attributes.MaterialSource),bbox=[[b.Min.X,b.Min.Y,b.Min.Z],[b.Max.X,b.Max.Y,b.Max.Z]]))
for m in f.Materials:
 t=m.GetBitmapTexture();result['materials'].append(dict(name=m.Name,texture=t.FileName if t else None,exists=Path(t.FileName).is_file() if t else False))
(O/'Local_Reference_Summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result),flush=True)
