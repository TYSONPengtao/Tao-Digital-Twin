import bpy,sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _closed_stats
names=['SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry'];out={}
for ver in ['09','10']:
 bpy.ops.wm.open_mainfile(filepath=f'E:/jz/JIA/Rebuild_V24_{ver}/Blender/Architecture_Complete_V24_{ver}.blend');out[ver]={n:_closed_stats(bpy.data.objects[n])for n in names}
(W/'v24_10/Solid_Comparison.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
