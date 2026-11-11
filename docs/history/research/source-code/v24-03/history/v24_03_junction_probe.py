import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend')
out=Path(__file__).parent/'v24_03_junction_review';rows={}
for o in bpy.data.objects:
 if o.type!='MESH' or not(o.name.startswith('SITE_COURTYARD_WEST') or o.name=='SITE_V21_GATE_REFERENCE_LAYER_02_Geometry'):continue
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 if o.name=='SITE_V21_GATE_REFERENCE_LAYER_02_Geometry':
  q=sorted(set(tuple(round(float(t),5) for t in v) for v in vs if v.x<5.6 and v.z<0))
 else:q=sorted(set(tuple(round(float(t),5) for t in v) for v in vs if v.x>4.65))
 faces=[]
 for p in o.data.polygons:
  co=[vs[j]for j in p.vertices]
  if o.name.startswith('SITE_COURTYARD_WEST_TILE_WALL_Geometry') and all(v.x>4.89 for v in co):faces.append({'v':[tuple(v)for v in co],'material':o.data.materials[p.material_index].name})
 rows[o.name]={'near_end_vertices':q,'end_faces':faces,'parent_props':{k:str(v)[:500]for k,v in o.parent.items()}if o.parent else None}
(out/'End_Profile.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print('END_PROBE_DONE')
