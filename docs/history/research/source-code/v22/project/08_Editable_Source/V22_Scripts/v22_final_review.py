from v22_common import *
import hashlib
O=Path('E:/jz/JIA/Rebuild_V22');R=O/'06_Report'
N=json.loads((R/'V22_Native_Readback_QA.json').read_text(encoding='utf8'));Door=json.loads((R/'Final_Native_Door_QA.json').read_text(encoding='utf8'))
assert N['status'].startswith('PASS') and Door['status'].startswith('PASS')
nativehash=hashlib.file_digest((O/'04_Rhino/Architecture_Complete_V22_ALIGNED_ENU.3dm').open('rb'),'sha256').hexdigest();assert nativehash==N['sha256']
J={r['name']:r for r in json.loads((O/'02_Data/Native_Readback_Index_V22.json').read_text(encoding='utf8'))}
Q=json.loads((W/'v22/Mutation.json').read_text(encoding='utf8'));new={e['name']:e for e in Q['replace']+Q['add']}
checks=[]
def test(name,ok,**data):
 checks.append({'check':name,'pass':bool(ok),**data});assert ok,(name,data)
def data(n):return np.load(O/'02_Data'/J[n]['file'])
def solid(n):
 d=data(n);v=d['vertices'];f=d['faces']
 for dec in [9,8,7,6]:
  vv,iv=np.unique(np.round(v,dec),axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(vv,iv[f].astype(np.uint64)))
  if m.status()==mf.Error.NoError:return m
 if n in new:return uni([manifold(p['geometry']) for p in new[n]['parts']])
 return raw(n)
edge=solid('HOUSE_V22_CONTINUOUS_BALCONY_EDGE')
for n in ['ROMAN_COLUMN_X3.9_Z0','ROMAN_COLUMN_X9.1_Z0','ROMAN_COLUMN_X3.9_Z3.9','ROMAN_COLUMN_X9.1_Z3.9']:
 vol=(edge^solid(n)).volume();test(n+' bears on continuous edge',vol>1e-7,intersection_m3=vol)
vol=(edge^solid('BALCONY_F2_PHOTO_OPEN_STONE_RAIL')).volume();test('Balcony guard feet connected',vol>1e-7,contact_m3=vol)
vol=(edge^solid('CONSTRUCTION_BALCONY_RAINWATER_BRANCH')).volume();test('Original rainwater pipe not blocked by new edge',vol<1e-7,overlap_m3=vol)
threshold=float(data('SITE_V21_GATE_REFERENCE_LAYER_01')['vertices'][:,2].max())
test('Gate visible one-step threshold',abs(threshold+.35)<1e-7,threshold_top_m=threshold)
for n in ['SITE_V20_INNER_GATE__LEAF_L','SITE_V20_INNER_GATE__LEAF_R']:
 lo=float(data(n)['vertices'][:,2].min());test(n+' bottom clears new threshold',lo-threshold>.012,clearance_m=lo-threshold)
deck=data('SITE_V20_PAVILION_RAISED_WOOD_SLATS')['vertices'];test('Pavilion 50mm underside clearance retained',abs(float(deck[:,2].min())+.43038-.05)<1e-7)
test('Pavilion principal-axis retreat retained',abs(float(deck[:,0].max())-3.96)<1e-7)
brick=solid('SITE_COURTYARD_WEST_TILE_WALL_V10_STAGGERED_GRAY_PLINTH_BRICKS')
for n in ['SITE_COURTYARD_WEST_TILE_WALL','SITE_COURTYARD_WEST_TILE_WALL_V10_PLINTH_MORTAR_BACKING']:
 # Same1mL overlap tolerance as the native door audit. Boolean cleanup and
 # metre/ENU round-trips leave sub-mL tessellation slivers in long masonry.
 vol=(solid(n)^brick).volume();test(n+' material partition',vol<1e-6,overlap_m3=vol,volumetric_tolerance_m3=1e-6)
DM=json.loads((O/'02_Data/Door_Manifest_V22.json').read_text(encoding='utf8'))
test('House entry operation remains sliding',sum(r.get('operation')=='SLIDING' for r in DM['doors'])==4)
result={'status':'PASS_FINAL_DETAIL_AND_INTERFACE_QA','native_model_sha256':nativehash,'checks':checks,'changed_native_parts':N['changed_objects'],'retained_native_objects':N['retained_objects'],'model_nodes':N['nodes'],'door_default_checks':len(Door['doors']),'door_unresolved_collisions':len(Door['unresolved_collisions']),'door_boolean_test_exceptions':Door['not_boolean_testable'],'dimension_status':'Ideal/photo fitting; not measured stone carving or a field dimensional survey','ue_import_runtime_tested':False}
(R/'Final_Detail_Review_V22.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(result['status'],len(checks),flush=True)
