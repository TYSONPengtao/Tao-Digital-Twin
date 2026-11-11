import json,copy
from pathlib import Path
W=Path(__file__).parent;D=W/'v20';O=Path('E:/jz/JIA/Rebuild_V20')
paths=[W/'v20_house/House_Mutation.json',W/'v20_gate_pavilion/Mutation.json',W/'v20_storage/Mutation.json',D/'Door_Mutation.json']
Q={'replace':[],'add':[],'remove':[],'materials':{}};seen=set()
for p in paths:
 a=json.loads(p.read_text(encoding='utf8'))
 for k in ['replace','add']:
  for e in a[k]:
   assert e['name'] not in seen,('Conflicting patches',e['name']);seen.add(e['name']);Q[k].append(e)
 Q['remove']+=a['remove'];Q['materials'].update(a.get('materials',{}))
Q['remove']=list(dict.fromkeys(Q['remove']));assert not seen.intersection(Q['remove'])
for pp in [W/'v20_house/Outer_Gate_Bottom_Mutation.json',W/'v20_storage/Seam_Correction.json']:
 if not pp.exists():continue
 aq=json.loads(pp.read_text(encoding='utf8'))
 for e in aq['replace']:
  for k in ['replace','add']:Q[k]=[x for x in Q[k] if x['name']!=e['name']]
  Q['replace'].append(e)
 Q['materials'].update(aq.get('materials',{}))
Q['change_notes']=['Photo-correlated ground-floor stair enclosure and missing partition walls','One solid entrance step with seamless nearby courtyard grading and closed porch base','Recessed pavilion with 5cm raised slatted timber deck','Closed smooth inner-gate soffit with real narrow external trim','Wrong storage-room middle portals sealed, eave-end portal restored','Stone guard aligned with screenwall, with extended gallery floor and stone base, clear west entry','Original INSV whitewashed storage interior and red wood finish in verified F3 bedroom','Independently hinged inward-open leaves, actual default open geometry and GLB pivot metadata']
Q['cameras']=[
 ['V20_House_Stair_Enclosure',[6.4,4.5,1.55],[6.4,7.35,1.4],84],
 ['V20_House_Rear_Partition',[10.0,4.8,1.55],[9.8,7.35,1.3],78],
 ['V20_House_Entry_One_Solid_Step',[11.0,-3.0,1.2],[6.5,.25,-.05],74],
 ['V20_Pavilion_Wood_Deck',[6.0,-5.0,.25],[2.3,-5,-.28],73],
 ['V20_Pavilion_Main_Axis',[6.5,-10.6,1.35],[6.5,.5,1.0],85],
 ['V20_Inner_Gate_Closed_Soffit',[6.6,-13.3,1.8],[6.6,-11.55,3.30],92],
 ['V20_Storage_Aligned_Gallery',[13.65,-16.0,1.1],[18.85,-15.62,1.0],88],
 ['V20_Storage_Correct_End_Portal',[20.5,-15.5,.95],[18.2,-15.5,.8],86],
 ['V20_Storage_Exterior',[23,-22.0,1.8],[17.5,-16.5,.2],65],
 ['V20_Storage_Interior',[16.1,-13.0,1.0],[18.5,-12.0,1.0],92],
 ['V20_F3_Bedroom_Inward_Door',[11.6,4.1,8.8],[9.08,7.95,8.6],86],
 ['V20_Outer_Gate_Inward_Pairs',[-17.8,-13.5,.6],[-12.9,-9.9,.6],82]]
DM=json.loads((D/'Door_Manifest.json').read_text(encoding='utf8'))
for e in Q['replace']+Q['add']:
 if e['name'].startswith('DOOR_STORAGE_V20'):
  e['v20_door']=True;e['current_pose']='OPEN_90_DEG_INWARD';e['inward_normal_local_xy']=[0,1]
  if 'pivot_world_m' not in e:e['pivot_world_m']=e.get('hinge_world_m',e.get('hinge_origin_local_m'))
  assert e['pivot_world_m'],e
  e['orientation_angle_degrees']=90;e['open_angle_degrees']=-90 if '_R__' in e['name'] else 90
  DM['doors'].append({'name':e['name'],'hinge_local_m':e['pivot_world_m'],'inward_normal_local_xy':[0,1],'open_angle_deg':e['open_angle_degrees'],'parent_door_id':None,'reference':'Original INSV 710/715s storage timber front'})
DM['doors']=list({r['name']:r for r in DM['doors']}.values())
(D/'Door_Manifest.json').write_text(json.dumps(DM,ensure_ascii=False,indent=2),encoding='utf8');(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
for p in paths:
 print(p.name,len(json.loads(p.read_text(encoding='utf8'))['replace']),len(json.loads(p.read_text(encoding='utf8'))['add']))
print('TOTAL',len(Q['replace']),len(Q['add']),len(Q['remove']),len(DM['doors']),Q['materials'].keys())
