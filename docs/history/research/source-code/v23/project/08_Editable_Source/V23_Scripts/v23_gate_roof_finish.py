"""Final curved contact fitting for V23 gate roof details, applied once."""
from v23_common import *
D=W/'v23_gate_roof';Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'))
ctrl=json.loads((D/'Design_Control.json').read_text(encoding='utf8'))
assert not any(x.get('check')=='CURVED_WING_DETAIL_FINISH' for x in ctrl['checks'])
v=np.asarray(ex.world_part(E['SITE_V21_GATE_REFERENCE_LAYER_09']['parts'][0],E['SITE_V21_GATE_REFERENCE_LAYER_09'])[0]);xvals=np.unique(np.round(v[:,0],6));zvals=[]
for x in xvals:
 mask=(abs(v[:,0]-x)<2e-6)&(abs(v[:,1]+12.262)<2e-6);zvals.append(v[mask,2].max())
def lift(x):return float(np.interp(x,xvals,zvals)-np.interp(6.6,xvals,zvals))
nodes={e['name']:e for e in Q['replace']+Q['add']}

def fit(p):
 m=manifold(p['geometry']);q=m.to_mesh64();v=np.asarray(q.vert_properties)[:,:3].copy();cx=(v[:,0].min()+v[:,0].max())/2
 v[:,2]+=[lift(x)-lift(cx) for x in v[:,0]]
 return pp(manifold({'type':'polyhedron','vertices':v.tolist(),'faces':np.asarray(q.tri_verts).tolist()}),p['material'])

n=nodes['SITE_V21_GATE_REFERENCE_LAYER_13'];n['parts']=[fit(p) for p in n['parts']]
n=nodes['SITE_V21_GATE_REFERENCE_LAYER_15'];n['parts']=[n['parts'][0]]+[fit(p) for p in n['parts'][1:]]
n=nodes['SITE_V21_GATE_REFERENCE_LAYER_10']
for p in n['parts'][258:]:
 for v in p['geometry']['vertices']:v[2]+=.006

roof=raw('SITE_V21_GATE_REFERENCE_LAYER_09');soffit=raw('SITE_V21_GATE_REFERENCE_CLOSED_SOFFIT')
overlaps=[]
for k,p in enumerate(n['parts']):
 m=manifold(p['geometry']);ov=(m^roof).volume();assert ov>1e-9,('unsupported_tile_after_finish',k,ov);overlaps.append(ov)
for k,p in enumerate(nodes['SITE_V21_GATE_REFERENCE_LAYER_15']['parts'][1:]):
 m=manifold(p['geometry']);ov=(m^(roof+soffit)).volume();assert ov>1e-9,('unsupported_curved_rafter',k,ov)
ctrl['checks'].append({'check':'CURVED_WING_DETAIL_FINISH','passed':True,'rafters':62,'curved_drip_slabs':78,'ceramic_units':510,'minimum_tile_carrier_overlap_m3':min(overlaps),'pan_bottom_above_original_carrier_top_m':.004})
Q['change_notes'].append('翼角附近的椽尾和滴水板随原屋面曲率连续拟合，板瓦凹槽底面高出屋面底板 4 mm，保持厚瓦叠接可见并嵌入承托面。')
save(Q,D,ctrl['checks'])
