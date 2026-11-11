import Rhino,json,System
d=Rhino.RhinoDoc.ActiveDoc;v=d.Views.ActiveView.ActiveViewport;n=next(x for x in d.NamedViews if x.Name==u'04_\u9752\u7816\u5899\u7ec6\u90e8');v.SetViewProjection(n.Viewport,True);rays=[]
for py in [730,740,750,760,770,780]:
 line=v.ClientToWorld(System.Drawing.Point(int(1050.0/1600*v.Size.Width),int(float(py)/1000*v.Size.Height)))
 rays.append({'py':py,'from':[line.From.X,line.From.Y,line.From.Z],'to':[line.To.X,line.To.Y,line.To.Z]})
with open('C:/Users/PENG/Documents/Codex/2026-10-07/files-pasted-by-the-user-rhino/work/v25/Native_Rays.json','w') as f:json.dump({'rays':rays,'mesh_triangles':sum(o.Geometry.Faces.Count for o in d.Objects if isinstance(o.Geometry,Rhino.Geometry.Mesh))},f)
