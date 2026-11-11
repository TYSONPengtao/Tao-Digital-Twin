from v26_2_common import *
import v26_2_common as C
FD=W/'v26_6/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
D=W/'v26_7_gate_audit/Prepared';D.mkdir(exist_ok=True);C.D=D;rows=[];proof=[]
def native(n,need_solid=True):
 r=J[n];a=np.load(FD/r['file']);return r,a,tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],n)if need_solid else None
n='SITE_V21_GATE_REFERENCE_LAYER_01_Geometry';r,a,m=native(n)
v=a['v'].copy();v[:,2]-=.15
shifted=tracked(v,a['f'],r['materials'],a['mi'],a['uv'],'Inherited stone threshold reset relative to lowered court')
# Unite the original overlapping threshold boxes into one actual stone body.
stone=union(shifted.decompose())
# Seat the original carved jamb bases onto the lowered foundation continuously.
for x0,x1 in[(4.9333,5.4562),(7.7438,8.2667)]:
 stone+=finish(cube([x0,-11.87,-.70],[x1,-11.294,-.60769]),r['materials'][0],'Stone bearing below inherited carved jamb')
rr,stone=export(n,stone,'Photo referenced low single stone threshold at100mm above registered court; remove accumulated250mm-high plinth after court datum lowered')
rows.append(rr);proof.append({'repair':'Low gate stone threshold relative to current court','top_m':-.5,'adjacent_court_m':-.6,'nominal_rise_m':.1,'prior_top_m':-.35,'vertical_adjustment_m':-.15,'metric_status':'Fitted to current model datum and actual low threshold relationship; not field-measured','evidence':[[655,0],[655,1],[650,0]]})
newsolids={n:stone}
for n in ['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_03_Geometry','V24_07_Gate_Moulded_Timber_Jambs','GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS_Geometry','SITE_V20_INNER_GATE__LEAF_L_Geometry','SITE_V20_INNER_GATE__LEAF_R_Geometry']:
 isleaf=n.startswith('SITE_V20_INNER_GATE__LEAF_')
 r,a,m=native(n,not isleaf);v=a['v'].copy();factor=np.clip((.4-v[:,2])/.75,0,1);v[:,2]-=.15*factor
 fn=n+'.npz';np.savez_compressed(D/fn,v=v,f=a['f'],mi=a['mi'],uv=a['uv'])
 rr=dict(r,file=fn,reason='Fit lower gate jamb/leaf edge to photographed low stone threshold; all upper geometry above0.4m, original plan, UVs and hinge transforms retained')
 rr.pop('bounds',None);rows.append(rr)
 if not isleaf:newsolids[n]=solid(v,a['f'],n)
 proof.append({'repair':'Lower gate foot fit','object':n,'maximum_low_vertex_extension_m':.15,'unchanged_above_z_m':.4,'original_xy_uv_faces_unchanged':True})
# Fill only the missing rear-side porch return between the gate and existing
# kitchen entrance. Exclude every existing opaque volume, so no display skin
# is overlaid on the current ground and its protected source attributes.
_,ga,ground=native('V26_2_Continuous_Ground_And_Perimeter_Shell')
_,ma,masonry=native('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry')
gap=cube([8.02856,-11.382,-.66],[9.50,-11.0999,-.40002])-ground-masonry
for m in newsolids.values():gap=gap-m
assert gap.volume()>1e-6
new='V26_7_Inner_Gate_Rear_Return_Closure'
rr,gap=export(new,finish(gap,'M_Floor','Existing porch return completed only in the missing corner'),'Complete missing inner gate rear-side floor/base return to existing kitchen porch level; exclude original ground and jamb solids',new=True)
rows.append(rr);proof.append({'repair':'Gate rear-side low return closure','requested_crop_m':[[8.02856,-11.382,-.66],[9.50,-11.0999,-.40002]],'new_volume_m3':gap.volume(),'existing_ground_vertices_and_height_attributes_unchanged':True,'door_swing_not_filled':True,'metric_status':'Existing registered porch level retained; relationship matched to actual650/655s view'})
(D/'Prepared_Geometry.json').write_text(json.dumps({'source':'E:/jz/JIA/Rebuild_V26_6/Blender/Architecture_Complete_V26_6.blend','source_sha256':'ea7cd20cb3c30cf2b5984c1e262ca182fa3c168a8a16fd7201ef428267bf05b7','objects':rows,'proof':proof,'archive':[]},ensure_ascii=False,indent=2),'utf8')
print('GATE_PREPARED',len(rows),'RETURN_VOLUME',gap.volume(),flush=True)
