from pathlib import Path
p=Path(r'work\blender_v4.py');t=p.read_text(encoding='utf-8');a=t.index(' for camera_name in ');b=t.index('  hidden=[]',a)
t=t[:a]+" for camera_name in ([] if mode=='ARCH' else ['CAM_13_Stair_Coordination']):\n"+t[b:]
Path(r'work\blender_v4_stair_fix.py').write_text(t,encoding='utf-8')
