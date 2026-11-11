# -*- coding: utf-8 -*-
import Rhino,scriptcontext as sc,System,os,json,time,traceback
O='E:/jz/JIA/Rebuild_V25';R=O+'/Reports';t=time.time()
def write(name,value):
 with open(R+'/'+name,'w') as f:json.dump(value,f,ensure_ascii=True,indent=2)
try:
 doc=sc.doc
 write('V25_Rhino_Desktop_Started.json',{'file':doc.Path,'object_count':doc.Objects.Count,'rhino_version':str(Rhino.RhinoApp.Version)})
 with open(O+'/Source_Metadata/Export_Report.json','r') as sf:expected=json.load(sf)
 assert doc.Objects.Count==expected['exported_material_parts'],doc.Objects.Count
 mode=Rhino.Display.DisplayModeDescription.GetDisplayMode(Rhino.Display.DisplayModeDescription.RenderedId)
 view=doc.Views.ActiveView
 if view is None:view=doc.Views.Add('Rebuild V25',Rhino.Display.DefinedViewportProjection.Perspective,System.Drawing.Rectangle(0,0,1600,1000),False)
 vp=view.ActiveViewport;vp.DisplayMode=mode;vp.ConstructionGridVisible=False;vp.ConstructionAxesVisible=False
 # Use the native saved named views, not proxy renders from another program.
 names=[u'01_\u5efa\u7b51\u53ca\u5916\u666f',u'02_\u5b8c\u6574\u5916\u666f\u8303\u56f4',u'03_\u9662\u843d\u9644\u5c5e\u5efa\u7b51',u'04_\u9752\u7816\u5899\u7ec6\u90e8']
 captures=[]
 for i,name in enumerate(names):
  n=next(v for v in doc.NamedViews if v.Name==name);assert vp.SetViewProjection(n.Viewport,True);vp.DisplayMode=mode
  for step in range(3):doc.Views.Redraw();Rhino.RhinoApp.Wait()
  cap=Rhino.Display.ViewCapture();cap.Width=1600;cap.Height=1000;cap.ScaleScreenItems=False;cap.DrawGrid=False;cap.DrawGridAxes=False;cap.DrawAxes=False;cap.TransparentBackground=False
  bitmap=cap.CaptureToBitmap(view);assert bitmap is not None
  p=R+'/V25_Rhino_View_'+str(i+1)+'.png';bitmap.Save(p,System.Drawing.Imaging.ImageFormat.Png);bitmap.Dispose();captures.append({'file':p,'named_view':name,'native_display_mode':mode.EnglishName,'camera':[vp.CameraLocation.X,vp.CameraLocation.Y,vp.CameraLocation.Z]});write('V25_Rhino_Desktop_Progress.json',{'captures':captures,'seconds':time.time()-t})
 n=next(v for v in doc.NamedViews if v.Name==names[0]);vp.SetViewProjection(n.Viewport,True);vp.DisplayMode=mode;doc.Views.Redraw();doc.Modified=False
 mesh_triangles=sum(o.Geometry.Faces.Count for o in doc.Objects if isinstance(o.Geometry,Rhino.Geometry.Mesh));assert mesh_triangles==expected['export_triangles'],mesh_triangles
 write('V25_Rhino_Desktop_QA.json',{'status':'PASS_NATIVE_RHINO_DESKTOP','file':doc.Path,'object_count':doc.Objects.Count,'mesh_triangles':mesh_triangles,'material_count':doc.Materials.Count,'rhino_version':str(Rhino.RhinoApp.Version),'captures':captures,'seconds':time.time()-t,'note':'Actual Rhino Rendered display. Static mesh 3dm; companion Blender carries the walking runtime.'})
except Exception:
 write('V25_Rhino_Desktop_Error.json',{'error':traceback.format_exc()})
