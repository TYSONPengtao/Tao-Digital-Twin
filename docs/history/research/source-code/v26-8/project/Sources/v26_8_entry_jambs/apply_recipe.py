"""Use with a current tracked combined house manifold. Does not read or save Blender."""
from pathlib import Path
import json
from v26_2_common import np,solid,finish

def apply_front_entry_jamb_recipe(house,proof=None):
    d=Path(__file__).resolve().parent
    a=np.load(d/'Entry_Jamb_Cutters.npz')
    cutter=solid(a['v'],a['f'],'V26.8 user actual photo narrow entry jamb cutters')
    result=house-finish(cutter,'M_Wall_Interior','Narrow actual entry jambs and oblique frame terminal planes')
    if proof is not None:
        rows=json.loads((d/'Prepared_Geometry.json').read_text('utf8'))['proof']
        proof.append({'repair':'Front door to polygonal bay narrow white jambs','source_recipe':'v26_8_entry_jambs/Entry_Jamb_Cutters.npz','removed_m3':(house-result).volume(),'no_added_volume':True,'joints':rows})
    return result
