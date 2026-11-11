# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh
O=Path(__file__).parent
F=rh.File3dm.Read(r'E:\jz\纯场地版本.3dm')
a=math.radians(19.65);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array([-3.45191261,-3.90043098,TAO_PRIVATE_SITE_002])
rows=[]
for i,o in enumerate(F.Objects):
 g=o.Geometry;b=g.GetBoundingBox();r=dict(index=i,name=o.Attributes.Name,type=str(type(g)),layer=o.Attributes.LayerIndex,bbmin=[b.Min.X,b.Min.Y,b.Min.Z],bbmax=[b.Max.X,b.Max.Y,b.Max.Z])
 if isinstance(g,rh.Mesh):
  v=np.array([[p.X,p.Y,p.Z] for p in g.Vertices]);f=np.array([list(p) for p in g.Faces],np.int32);uv=np.array([[p.X,p.Y] for p in g.TextureCoordinates]);loc=(v-origin)@R
  r.update(vertices=len(v),faces=len(f),uv=len(uv),localmin=loc.min(0).tolist(),localmax=loc.max(0).tolist());np.savez_compressed(O/('source_'+str(i)+'.npz'),vertices=v,local=loc,faces=f,uv=uv)
 rows.append(r)
print('units',F.Settings.ModelUnitSystem,'materials',len(F.Materials),'objects',len(rows));print(json.dumps(rows,ensure_ascii=False,indent=2));(O/'Source_Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
