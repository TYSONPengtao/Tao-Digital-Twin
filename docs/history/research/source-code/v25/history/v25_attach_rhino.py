import win32com.client,sys
from pathlib import Path
a=win32com.client.Dispatch('Rhino.Interface.8');a.ReleaseWithoutClosing=1
print('INITIALIZED',a.IsInitialized,flush=True)
p=Path(sys.argv[1]).resolve();print('SCRIPT_RESULT',a.RunScript('-_RunPythonScript ('+p.as_posix()+')',0),flush=True)
