from pathlib import Path
import sys
W=Path(__file__).parent;sys.path.insert(0,str(W/'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id('D:/AJAVIS01/RHINO8/RUNING/System').load(rhinoinside.__parse_framework_id('net48'))
import clr
clr.AddReference('RhinoCommon');clr.AddReference('System.Drawing');clr.AddReference('Microsoft.CSharp')
import Rhino,System
from Microsoft.CSharp import CSharpCodeProvider
from System.CodeDom.Compiler import CompilerParameters
def start():
 return Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
def bridge():
 p=CompilerParameters();p.GenerateExecutable=False;p.GenerateInMemory=True
 for n in ['System.dll','System.Core.dll','System.Drawing.dll','D:/AJAVIS01/RHINO8/RUNING/System/RhinoCommon.dll']:p.ReferencedAssemblies.Add(n)
 result=CSharpCodeProvider().CompileAssemblyFromSource(p,(W/'v25_mesh_bridge.cs').read_text('utf8'))
 errors=[str(e)for e in result.Errors if not e.IsWarning]
 if errors:raise RuntimeError('\n'.join(errors))
 return result.CompiledAssembly.GetType('V25MeshBridge')
def call(bridge,name,*args):return bridge.GetMethod(name).Invoke(None,System.Array[System.Object](args))
