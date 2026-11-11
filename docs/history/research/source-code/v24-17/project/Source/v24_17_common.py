from pathlib import Path
import json
import v24_16_common as base
base.D=Path(__file__).parent/'v24_17'
base.INDEX={r['name']:r for r in json.loads((base.D/'Inventory.json').read_text())}
from v24_16_common import *
def tris(faces):return [[f[0],f[k],f[k+1]]for f in faces for k in range(1,len(f)-1)]
def profile_solid(points,lo,hi,axis='X'):
 m=section(points,hi-lo)
 return m.transform(np.array([[0,0,1,lo],[1,0,0,0],[0,1,0,0]],float))if axis=='X'else m.transform(np.array([[1,0,0,0],[0,0,1,lo],[0,1,0,0]],float))
def variable_prism(poly,top,thick):
 a=section(poly,thick).to_mesh64();v=np.asarray(a.vert_properties[:,:3]).copy();f=np.asarray(a.tri_verts)
 for p in v:p[2]+=top(p[0],p[1])-thick
 return solid(v,f,'variable prism')
def compose(ms):return mf.Manifold.compose(ms)
