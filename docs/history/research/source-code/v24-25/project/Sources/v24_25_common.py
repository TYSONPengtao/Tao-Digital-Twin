from pathlib import Path
import json
import v24_16_common as base
base.D=Path(__file__).parent/'v24_25'
base.INDEX={r['name']:r for r in json.loads((base.D/'Inventory.json').read_text(encoding='utf8'))}
base.OUT={'objects':[],'proof':{},'remove':[],'material_edits':[]}
from v24_16_common import *
def profile_y(poly,lo,hi):return section(poly,hi-lo).transform(np.array([[1,0,0,0],[0,0,1,lo],[0,1,0,0]],float))
def compose(ms):return mf.Manifold.compose(ms)
