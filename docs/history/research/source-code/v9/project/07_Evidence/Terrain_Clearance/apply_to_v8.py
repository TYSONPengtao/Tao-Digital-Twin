"""Apply isolated west-yard clearance to a V8 copy after other patch rebuilds.
Usage: python apply_to_v8.py E:\jz\JIA\Rebuild_V8_Hybrid
Never writes the V7 source. Other V8 modeled changes are retained.
"""
import json,sys,shutil
from pathlib import Path
D=Path(__file__).parent;dest=Path(sys.argv[1])
assert dest.resolve()!=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid').resolve(),'V7 is immutable source'
m=json.loads((D/'Merge_Manifest.json').read_text(encoding='utf-8'));delete=set(m['delete_names']);repl={r['name']:r for r in m['replacement_patch_rows']};B=json.loads((dest/'02_Data/Base_Index.json').read_text(encoding='utf-8'));I=json.loads((dest/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));M=json.loads((dest/'02_Data/Materials.json').read_text(encoding='utf-8'))
for fn in (D/'data').glob('*.npz'):shutil.copy2(fn,dest/'02_Data'/fn.name)
I=[dict(repl.get(r['name'],r)) for r in I if r['name'] not in delete and not r['name'].startswith('V8_WEST_CLEARED_')]+m['new_patch_rows']
for j,r in enumerate(I):r['index']=j
brepl={r['index']:r for r in m['replacement_base_rows']}
for j,b in enumerate(B):
 if b['index'] in brepl:
  src=brepl[b['index']];r=dict(b);r.update({k:src[k] for k in ['vertices','faces','uv_count','v8_source_edit']});B[j]=r
M.update(m['material_additions'])
for file,value in [('Patch_Index.json',I),('Base_Index.json',B),('Materials.json',M)]: (dest/'02_Data'/file).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
# Delete the same objects from scene for editable geometry rebuilding.
scene=dest/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'
if scene.exists():
 S=json.loads(scene.read_text(encoding='utf-8'));S['elements']=[e for e in S['elements'] if e['name'] not in delete];S['materials'].update(m['material_additions']);S.setdefault('revision_notes',[]).append('V8 west farmyard terrain-only edit: whole intersecting sheds/pergola, internal farm fence and metal entry removed; boundary perimeter masonry remains.');scene.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
(dest/'06_Report').mkdir(exist_ok=True);(dest/'07_Evidence/V8_West_Clearance').mkdir(parents=True,exist_ok=True)
for fn in ['Terrain_Clearance_QA.json','Independent_Terrain_Clearance_QA.json','Terrain_Clearance_Polygon.json','Redline_Calibration.json','Merge_Manifest.json']:shutil.copy2(D/fn,dest/'06_Report'/fn)
for fn in ['Redline_Calibration_Overlay.png','V8_West_Terrain_Only_Plan.png','V8_West_Terrain_Ground_Classification.png']:
 if (D/fn).exists():shutil.copy2(D/fn,dest/'07_Evidence/V8_West_Clearance'/fn)
print('Applied west clearance',len(delete),'deleted names;',len(repl),'patch replacements;',len(m['new_patch_rows']),'new ground nodes;',len(brepl),'modified source derivatives')
