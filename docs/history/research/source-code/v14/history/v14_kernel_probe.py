import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id(r'D:\AJAVIS01\RHINO8\RUNING\System').load(rhinoinside.__parse_framework_id('net48'))
import clr;clr.AddReference('RhinoCommon');import Rhino,System
try:
 f=Rhino.FileIO.File3dm.Read(r'E:\jz\纯场地版本.3dm');print('file read without core',f is not None,len(list(f.Objects)),flush=True)
 b=Rhino.Geometry.Brep.CreateFromBox(Rhino.Geometry.BoundingBox(0,0,0,1,1,1));m=Rhino.Geometry.Mesh.CreateFromBrep(b,Rhino.Geometry.MeshingParameters.FastRenderMesh);print('MESH WITHOUT CORE',len(m),sum(x.Faces.Count for x in m),flush=True)
except Exception as e:print(type(e).__name__,str(e),flush=True)
