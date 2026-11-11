"""Import from root preparation script; does not export or save anything.

house=apply_window_sills(house)
Load ordinary objects/remove separately from Prepared_Geometry.json.
"""
from pathlib import Path
import json
import v26_2_common as C

def apply_window_sills(house,prepared_base=None):
 base=Path(prepared_base)if prepared_base else Path(__file__).resolve().parent
 d=base/'Prepared';prep=json.loads((base/'Prepared_Geometry.json').read_text('utf8'))
 def m(row):
  a=C.np.load(d/row['file'])
  return C.tracked(a['v'],a['f'],row['materials'],a['mi'],a['uv'],row['name'])
 for q in prep['house_recipe']:house=(house-m(q['cut']))+m(q['add'])
 for q in prep['glazing_clearance_recipe']:house-=m(q['cut'])
 return house
