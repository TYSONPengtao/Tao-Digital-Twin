"""Last visible ideal/site corrections: continuous balcony edge and gate step."""
from v22_common import *
def find(Q,n):return next(e for e in Q['replace']+Q['add'] if e['name']==n)
def rewrite(Q,n,ps,**meta):
 try:e=find(Q,n);e.update(parts=ps,**meta)
 except StopIteration:put(Q,n,ps,**meta)
# The native columns end at3.77/start at3.90, outside the narrow balcony slab.
# A continuous concrete edge closes that13cm gap and supports the guard feet.
D=W/'v22_house';Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'))
edge=cube([3.68,-.22,3.768],[5.64,.48,.137])-cyl(8.82,.13,3.76,.063,.20,32)
rewrite(Q,'HOUSE_V22_CONTINUOUS_BALCONY_EDGE',[pp(edge,'M_Wall_Exterior')],classification='CONTINUOUS_BALCONY_FASCIA_CLOSING_NATIVE_COLUMN_JUNCTION_GAP',existing_rainwater_pipe_opening_preserved=True)
n='BALCONY_F2_PHOTO_OPEN_STONE_RAIL';ps=[]
for mat in I[n]['materials']:
 m=raw(n,mat);q=m.to_mesh64();v=np.asarray(q.vert_properties)[:,:3].copy();v[v[:,2]<4.0,2]-=.080
 ps.append(pp(manifold({'type':'polyhedron','vertices':v.tolist(),'faces':np.asarray(q.tri_verts).tolist()}),mat))
rewrite(Q,n,ps,classification='ORIGINAL_GUARD_WITH_BASES_EXTENDED_TO_FLOOR')
Q['change_notes']=[s for s in Q['change_notes'] if not s.startswith('补齐阳台前沿连续边梁')]
note='补齐阳台前沿连续边梁，消除原上下柱之间130mm断缝；石栏底脚下延80mm与原坡面/边梁相接，边梁预留原排水管孔。'
if note not in Q['change_notes']:Q['change_notes'].append(note)
save(Q,D,[{'check':'Continuous balcony edge bridges native3.77..3.90 column gap','pass':True,'concealed_end_bearing_m':.002}])
D=W/'v22_gate';Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'));n='SITE_V21_GATE_REFERENCE_LAYER_01';ps=[]
for p in E[n]['parts']:
 g=copy.deepcopy(p['geometry']);v=np.asarray(g['vertices']);name=p.get('reference_object_name','')
 if name in ['门外台阶','门槛石']:
  top=float(v[:,2].max());v[abs(v[:,2]-top)<1e-7,2]=-.360 if name=='门外台阶' else -.350
 p=copy.deepcopy(p);p['geometry']={'type':'polyhedron','vertices':v.tolist(),'faces':g['faces']};ps.append(p)
rewrite(Q,n,ps,classification='ONE_VISIBLE_STONE_GATE_STEP_FITTED_TO_CURRENT_ADJACENT_GRADE')
for n in ['SITE_V20_INNER_GATE__LEAF_L','SITE_V20_INNER_GATE__LEAF_R']:
 e=find(Q,n);lo=min(np.asarray(p['geometry']['vertices'])[:,2].min() for p in e['parts']);hi=max(np.asarray(p['geometry']['vertices'])[:,2].max() for p in e['parts']);ps=[]
 for p in e['parts']:
  m=manifold(p['geometry']);q=m.to_mesh64();v=np.asarray(q.vert_properties)[:,:3].copy();v[:,2]=-.337+(v[:,2]-lo)*(hi+.337)/(hi-lo)
  ps.append(pp(manifold({'type':'polyhedron','vertices':v.tolist(),'faces':np.asarray(q.tri_verts).tolist()}),p['material']))
 rewrite(Q,n,ps,v22_final_threshold_clearance_m=.013)
n='GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS';e=find(Q,n);clip=cube([4,-12,-.337],[5,2,4]);ps=[]
for p in e['parts']:
 m=manifold(p['geometry'])^clip
 if not m.is_empty():ps.append(pp(m,p['material']))
rewrite(Q,n,ps)
note='按理想图/实景显出一道石阶，门槛比相邻现状铺地高约100mm；门叶仅重配底端高度，保留顶部、门轴和内开方向，门下留13mm。'
if note not in Q['change_notes']:Q['change_notes'].append(note)
save(Q,D,[{'check':'Visible one-step threshold and reprofiled leaves','step_rise_above_adjacent_pavement_m':.100,'door_bottom_clearance_m':.013,'dimension_status':'Photo/ideal fit, not field measurement','pass':True}])
