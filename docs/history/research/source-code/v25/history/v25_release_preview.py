import Rhino,json,scriptcontext as sc
d=sc.doc
report={'file':d.Path,'modified':d.Modified,'objects':d.Objects.Count}
assert d.Path.replace('\\','/').lower()=='e:/jz/jia/rebuild_v25/rhino/architecture_complete_v25.3dm'
assert not d.Modified,'Preview was edited; do not discard user changes'
# Revertible preview created by this task. Close only its unedited document so
# the native writer can replace the file without Rhino's .rhl lock.
report['release_result']=Rhino.RhinoApp.RunScript('_-New _None _Enter',False)
with open('E:/jz/JIA/Rebuild_V25/Reports/V25_Desktop_Preview_Release.json','w') as f:json.dump(report,f)
