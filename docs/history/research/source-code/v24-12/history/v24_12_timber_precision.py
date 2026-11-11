import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_12';idx=json.loads((D/'Solid_Export_Index.json').read_text());row=next(r for r in idx['objects']if r['name']=='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry');d=np.load(D/row['file']);f=np.array(d['f'],dtype=np.uint64,order='C');v=np.ascontiguousarray(d['v']);m=mf.Manifold(mf.Mesh64(v,f));print('SAVED RAW',m.status(),m.volume())
row=next(r for r in json.loads((D/'Prepared_Geometry.json').read_text())['objects']if r['name']=='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry');v=np.array(row['v']);f=np.array(row['f'],dtype=np.uint64,order='C');m=mf.Manifold(mf.Mesh64(np.ascontiguousarray(v),f));print('PREP RAW',m.status(),m.volume(),len(m.decompose()))
for tol in[0,.00005,.0001,.0003]:
 mm=m.simplify(tol)if tol else m;dd=mm.to_mesh64();vv=np.asarray(dd.vert_properties[:,:3],dtype=np.float32).astype(float);ff=np.asarray(dd.tri_verts,dtype=np.uint64,order='C');raw=mf.Manifold(mf.Mesh64(np.ascontiguousarray(vv),ff));print('FLOAT RAW',tol,raw.status(),raw.volume(),flush=True)
