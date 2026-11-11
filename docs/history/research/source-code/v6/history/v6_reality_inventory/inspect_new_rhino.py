import sys,json,collections
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'libs'))
import rhino3dm as r
O=Path(__file__).resolve().parent
rows=[]
for p in [Path(r'E:\jz\纯场地版本.3dm'),Path(r'E:\jz\实景三维场景模型.3dm'),Path(r'E:\jz\实景三维场景模型2.3dm')]:
 print('READ',p,flush=True);f=r.File3dm.Read(str(p));rec={'path':str(p),'bytes':p.stat().st_size,'units':str(f.Settings.ModelUnitSystem),'objects':len(f.Objects),'materials':[],'layers':[dict(name=a.Name,index=a.Index) for a in f.Layers],'geometry':[],'embedded_file_api':[x for x in dir(f) if 'embed' in x.lower() or 'bitmap' in x.lower()]}
 for i,m in enumerate(f.Materials):
  mr=dict(index=i,name=m.Name,id=str(m.Id),diffuse=list(m.DiffuseColor),textures=[])
  for method in ['GetBitmapTexture','GetBumpTexture','GetTransparencyTexture','GetEnvironmentTexture']:
   try:
    t=getattr(m,method)()
    if t:mr['textures'].append(dict(kind=method,file=t.FileName,enabled=t.Enabled))
   except Exception as e:mr[method+'_error']=str(e)
  rec['materials'].append(mr)
 for i,a in enumerate(f.Objects):
  g=a.Geometry;at=a.Attributes;gr=dict(index=i,type=str(g.ObjectType),name=at.Name,id=str(at.Id),layer_index=at.LayerIndex,material_index=at.MaterialIndex,material_source=str(at.MaterialSource))
  try:
   b=g.GetBoundingBox();gr['bbox']=[[b.Min.X,b.Min.Y,b.Min.Z],[b.Max.X,b.Max.Y,b.Max.Z]]
  except Exception as e:gr['bbox_error']=str(e)
  if isinstance(g,r.Mesh):
   gr.update(vertices=len(g.Vertices),faces=len(g.Faces),uv=len(g.TextureCoordinates),normals=len(g.Normals),vertex_colors=len(g.VertexColors))
  rec['geometry'].append(gr)
 print(json.dumps({k:v for k,v in rec.items() if k not in ['geometry','materials','layers']},ensure_ascii=False),flush=True)
 print('materials',json.dumps(rec['materials'],ensure_ascii=False)[:2200],flush=True)
 print('geometry',json.dumps(rec['geometry'],ensure_ascii=False)[:2400],flush=True)
 rows.append(rec)
(O/'New_Rhino_Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
