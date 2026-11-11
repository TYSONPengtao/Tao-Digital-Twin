from v25_rhino_common import *
core=start()
try:
 for typ in [Rhino.DocObjects.ViewInfo,Rhino.DocObjects.ViewportInfo,Rhino.Display.RhinoViewport]:
  t=clr.GetClrType(typ);print('TYPE',t.FullName,flush=True)
  for c in t.GetConstructors():print(str(c),flush=True)
 print('VIEW_MEMBERS',[(str(m.Name),str(m.MemberType)) for m in clr.GetClrType(Rhino.DocObjects.ViewInfo).GetMembers()],flush=True)
finally:core.Dispose()
