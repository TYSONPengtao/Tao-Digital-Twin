from pathlib import Path
import json
import v24_16_common as base
base.D=Path(__file__).parent/'v24_20'
base.INDEX={r['name']:r for r in json.loads((base.D/'Inventory.json').read_text())}
base.OUT={'objects':[],'raw_objects':[],'proof':{},'remove':[],'material_edits':[],'door_changes':[]}
from v24_16_common import *
def compose(ms):return mf.Manifold.compose(ms)
def profile_solid(points,lo,hi,axis='X'):
 m=section(points,hi-lo)
 return m.transform(np.array([[0,0,1,lo],[1,0,0,0],[0,1,0,0]],float))if axis=='X'else m.transform(np.array([[1,0,0,0],[0,0,1,lo],[0,1,0,0]],float))
