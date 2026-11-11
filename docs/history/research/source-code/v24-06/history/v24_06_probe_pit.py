import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));from v24_06_common import *
from v24_03_junction_blender import _closed_stats
bpy.ops.wm.open_mainfile(filepath=str(P));out={}
for n in ['SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT_Geometry','SITE_V16_GRADED_INTERIOR_SOIL_Geometry','SITE_COURTYARD_WEST_TILE_WALL_Geometry','SITE_COURTYARD_WEST_TILE_WALL_V10_PLINTH_MORTAR_BACKING_Geometry']:
 o=bpy.data.objects[n];me=o.data;near=[]
 if 'PAVEMENT'in n:
  for v in me.vertices:
   p=o.matrix_world@v.co;r=math.hypot(p.x+4,p.y+13.5)
   if r<.65:near.append({'id':v.index,'xyz':tuple(p),'r':r})
 out[n]={'closed':_closed_stats(o),'near':near,'material_slots':[m.name for m in me.materials]}
 if 'PAVEMENT'in n:
  ids={v['id']for v in near};out[n]['near_faces']=[{'id':f.index,'vertices':list(f.vertices),'normal':tuple(f.normal),'material':f.material_index}for f in me.polygons if ids.intersection(f.vertices)]
write('V24_06_Pit_Probe.json',out);print(json.dumps(out,ensure_ascii=False),flush=True)
bpy.ops.wm.open_mainfile(filepath=str(B));print('BASE WALLS',flush=True)
for n in ['SITE_COURTYARD_WEST_TILE_WALL_Geometry','SITE_COURTYARD_WEST_TILE_WALL_V10_PLINTH_MORTAR_BACKING_Geometry']:print(n,_closed_stats(bpy.data.objects[n]),flush=True)
