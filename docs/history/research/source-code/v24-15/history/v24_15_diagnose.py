import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_15';idx=json.loads((D/'Solid_Export_Index.json').read_text());sol={}
for r in idx['objects']:
 d=np.load(D/r['file']);m=mf.Manifold(mf.Mesh64(np.array(d['v'],dtype=np.float64,order='C'),np.array(d['f'],dtype=np.uint64,order='C')))
 if m.status()==mf.Error.NoError:sol[r['name']]=m
roof=sol['SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry'];glass=sol['V24_15_Storage_Upper_Transom_Amber_Panes']
for n,m in sol.items():
 if not(n.startswith('V24_15_Storage_')or n=='V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails')or 'Amber_Panes'in n:continue
 for label,s in [('ROOF',roof),('GLASS',glass)]:
  mm=m^s
  if mm.volume()>1e-8:print(label,n,mm.volume(),mm.bounding_box(),flush=True)
