from pathlib import Path
import json,shutil
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V25');D=W/'v25';unused=D/'Unused_Bake_Images';unused.mkdir(exist_ok=True);used={Path(t['file']).resolve() for t in json.loads((D/'Texture_Index.json').read_text('utf8'))};moved=[]
for p in (O/'Textures').glob('BAKED_*.png'):
 if p.resolve() not in used:
  assert p.resolve().is_relative_to((O/'Textures').resolve());shutil.move(str(p),str(unused/p.name));moved.append(p.name)
diag=D/'Desktop_Diagnostics';diag.mkdir(exist_ok=True)
for name in ['V25_Desktop_Attachment.json','V25_Desktop_Material_Probe.json','V25_Desktop_Preview_Release.json','V25_Rhino_Desktop_Error.json']:
 p=O/'Reports'/name
 if p.exists():shutil.move(str(p),str(diag/name))
print('TIDIED_OWN_INTERMEDIATE_BAKES',len(moved),flush=True)
