import Rhino,json
with open('E:/jz/JIA/Rebuild_V25/Reports/V25_Desktop_Attachment.json','w') as f:json.dump({'file':Rhino.RhinoDoc.ActiveDoc.Path,'objects':Rhino.RhinoDoc.ActiveDoc.Objects.Count,'rhino_version':str(Rhino.RhinoApp.Version)},f)
