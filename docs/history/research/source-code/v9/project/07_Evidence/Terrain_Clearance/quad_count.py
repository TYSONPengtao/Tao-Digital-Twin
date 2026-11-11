import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid')
for i in range(5):
 d=np.load(O/'02_Data'/f'Base_{i}.npz');f=d['faces'];print(i,'quads',int((f[:,2]!=f[:,3]).sum()))
