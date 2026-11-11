"""Keep source stair flights exactly while installing only the new rear guard."""
from v26_2_common import *
import v26_2_common as C
D=W/'v26_10_railing';C.D=D;prep=json.loads((D/'Prepared_Railing.json').read_text('utf8'));n='V26_1_Photo_Referenced_Continuous_Wood_Railing';r=prep['objects'][0];a=np.load(D/r['file']);new=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],'New F3 level rear guard')
BD=W/'v26_9/Final';J={q['name']:q for q in json.loads((BD/'Geometry_Index.json').read_text('utf8'))};b=np.load(BD/J[n]['file']);old=tracked(b['v'],b['f'],J[n]['materials'],b['mi'],b['uv'],'Unchanged V26.9 sloping flights, turns and front guard')
mask=cube([7.76,8.59,7.03],[8.,9.59,8.61]);m=(old-mask)+(new^mask);rr,m=export(n,m,r['reason'],smooth_wood=True);assert len(m.decompose())==2
prep['objects']=[rr];prep['proof']['source_mesh_preserved_outside_rear_guard_mask']=True;prep['proof']['rear_guard_mask_bounds_m']=[[7.76,8.59,7.03],[8.,9.59,8.61]];(D/'Prepared_Railing.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2),'utf8');print('PRESERVED_RAIL',len(m.decompose()),m.num_tri(),flush=True)
