import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
B=Path(r'E:/jz/JIA/Rebuild_V14');F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V14_ALIGNED_ENU.3dm'));prefix=['SITE_V12_REBUILT_COURT_0_-20_0','SITE_V14_INNER_STORAGE_MASONRY','SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES','SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_V14_INNER_STORAGE_GABLE_ROOF'];r=[]
for ob in F.Objects:
 if any(ob.Attributes.Name.startswith(n+'__') for n in prefix):
  if sum(q['node']==ob.Attributes.Name.rsplit('__',1)[0] for q in r)>=3:continue
  a=ob.Attributes;g=ob.Geometry;m=F.Materials[a.MaterialIndex] if a.MaterialIndex>=0 else None;mat={'index':a.MaterialIndex,'name':m.Name,'diffuse':list(m.DiffuseColor),'bitmap':m.GetBitmapTexture().FileName if m.GetBitmapTexture() else None,'pbr':str(m.PhysicallyBased.BaseColor)} if m else None
  r.append({'node':a.Name.rsplit('__',1)[0],'name':a.Name,'type':type(g).__name__,'color':list(a.ObjectColor),'color_source':str(a.ColorSource),'layer_color':list(F.Layers[a.LayerIndex].Color),'material_source':str(a.MaterialSource),'material':mat,'meshuv':len(g.TextureCoordinates) if isinstance(g,rh.Mesh) else None,'userdata':dict(a.GetUserStrings())})
(W/'v15/Display_Probe.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps([{k:v for k,v in q.items() if k!='userdata'} for q in r],ensure_ascii=False,indent=2))
