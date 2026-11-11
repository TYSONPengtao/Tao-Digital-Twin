import sys,json,collections,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
O=W/'v14';O.mkdir(exist_ok=True)
P=Path(r'E:\jz\纯场地版本.3dm');f=rh.File3dm.Read(str(P))
rows=[]
for ob in f.Objects:
 g=ob.Geometry;a=ob.Attributes;b=g.GetBoundingBox()
 rows.append(dict(id=str(a.Id),name=a.Name,type=type(g).__name__,layer=f.Layers[a.LayerIndex].Name,material=a.MaterialIndex,bbox=[[b.Min.X,b.Min.Y,b.Min.Z],[b.Max.X,b.Max.Y,b.Max.Z]],vertices=len(g.Vertices) if isinstance(g,rh.Mesh) else None,faces=len(g.Faces) if isinstance(g,rh.Mesh) else None,uv=len(g.TextureCoordinates) if isinstance(g,rh.Mesh) else None,hidden=a.Visible==False,userdata=dict(a.GetUserStrings())))
rep={'source':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'units':str(f.Settings.ModelUnitSystem),'objects':rows,'materials':[{'name':m.Name,'diffuse':list(m.DiffuseColor),'textures':str(m.GetBitmapTexture().FileName) if m.GetBitmapTexture() else None} for m in f.Materials],'strings':list(f.Strings),'layers':[{'name':l.Name,'visible':l.Visible} for l in f.Layers]}
(O/'Source_Site_Inventory.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(rep,ensure_ascii=False)[:16000])
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V13\08_Editable_Source\Architecture_Scene_V13.json').read_text(encoding='utf8'))
out={e['name']:e for e in S['elements'] if any(t in e['name'] for t in ['F3','STOR','KITCHEN','TERRACE','SLAB','STAIR']) and not e['name'].startswith('KITCHEN_V12_DETAIL')}
(O/'Target_Elements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('target nodes',list(out))
