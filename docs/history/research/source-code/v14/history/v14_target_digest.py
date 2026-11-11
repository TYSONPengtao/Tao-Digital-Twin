import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import rhino3dm as rh
f=rh.File3dm.Read(r'E:\jz\纯场地版本.3dm');print('embed methods', [n for n in dir(f) if 'mbed' in n or 'itmap' in n]);print('embedded paths',f.EmbeddedFilePaths if hasattr(f,'EmbeddedFilePaths') else '')
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V13\08_Editable_Source\Architecture_Scene_V13.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']}
I=json.loads(Path(r'E:\jz\JIA\Rebuild_V13\02_Data\Modeled_Index_V13.json').read_text(encoding='utf8'))
print('all site names', [e['name'] for e in S['elements'] if e['name'].startswith('SITE_') and not any(t in e['name'] for t in ['V12_','V11_','V10_','TILE_ROWS','KITCHEN','PAVILION'])])
for n in ['SLAB_JOINED_F3','PARTITIONS_JOINED_F3','FACADE_CONTINUOUS_F3','STAIR_F2_FLIGHT1','STAIR_F2_FLIGHT2','STAIR_LANDING_F2','DOOR_LAUNDRY_F3__FRAME','DOOR_STUDY_F3__FRAME','DOOR_BATH_F3_R__FRAME','SITE_KITCHEN_STONE_FLOOR','SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES','SITE_KITCHEN_CHINESE_TILE_ROOF']:
 print(n,json.dumps(E[n],ensure_ascii=False))
(W/'v14/All_Node_Names.txt').write_text('\n'.join(e['name'] for e in S['elements']),encoding='utf8')
