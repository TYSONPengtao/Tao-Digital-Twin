import Rhino,scriptcontext as sc,json,traceback
try:
 doc=Rhino.RhinoDoc.ActiveDoc
 assert not doc.Modified,'Do not discard edits made in the preview'
 assert not doc.Path or doc.Path.replace('\\','/').lower()=='e:/jz/jia/rebuild_v25/rhino/architecture_complete_v25.3dm'
 result=Rhino.RhinoDoc.Open('E:/jz/JIA/Rebuild_V25/Rhino/Architecture_Complete_V25.3dm')
 # On Windows the script's original document is closed by Open. Verify the
 # new active native document rather than the closed document return wrapper.
 opened=Rhino.RhinoDoc.ActiveDoc
 assert opened is not None and opened.Path.replace('\\','/').lower()=='e:/jz/jia/rebuild_v25/rhino/architecture_complete_v25.3dm'
 sc.doc=Rhino.RhinoDoc.ActiveDoc
 execfile('C:/Users/PENG/Documents/Codex/2026-10-07/files-pasted-by-the-user-rhino/work/v25_viewport.py')
except Exception:
 with open('E:/jz/JIA/Rebuild_V25/Reports/V25_Rhino_Desktop_Error.json','w') as f:json.dump({'error':traceback.format_exc()},f)
