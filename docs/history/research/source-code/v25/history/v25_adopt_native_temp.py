from pathlib import Path
import os,stat
O=Path('E:/jz/JIA/Rebuild_V25/Rhino');p=O/'Architecture_Complete_V25.3dm';temp=O/'_Building_LOCAL.3dm';assert temp.stat().st_size>700000000
os.chmod(p,stat.S_IWRITE|stat.S_IREAD);os.replace(temp,p);print('ADOPTED_FINAL_NATIVE_LOCAL',p.stat().st_size,flush=True)
