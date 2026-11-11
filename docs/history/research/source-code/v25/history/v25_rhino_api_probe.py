from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'netlibs')]
import rhinoinside
rhinoinside.__parse_rhino_id('D:/AJAVIS01/RHINO8/RUNING/System').load(rhinoinside.__parse_framework_id('net48'))
import clr
clr.AddReference('RhinoCommon')
import Rhino,System
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
try:
 f=Rhino.FileIO.File3dm();m=Rhino.DocObjects.Material();m.ToPhysicallyBased();pbr=m.PhysicallyBased;mesh=Rhino.Geometry.Mesh();result={'version':Rhino.RhinoApp.Version.ToString(),'File3dm':[s for s in dir(f)if not s.startswith('_')],'Material':[s for s in dir(m)if not s.startswith('_')],'PBR':[s for s in dir(pbr)if not s.startswith('_')],'MeshVertices':[s for s in dir(mesh.Vertices)if not s.startswith('_')],'MeshTexcoords':[s for s in dir(mesh.TextureCoordinates)if not s.startswith('_')],'Embedded':[s for s in dir(getattr(f,'AllEmbeddedFiles',None))if not s.startswith('_')],'TextureType':[s for s in dir(Rhino.DocObjects.TextureType)if not s.startswith('_')]};(W/'v25/Rhino_API_Probe.json').write_text(json.dumps(result,indent=2));print('RHINO_RUNTIME',result['version'],flush=True)
except Exception:
 import traceback;traceback.print_exc()
finally:core.Dispose()
