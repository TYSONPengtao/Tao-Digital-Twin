"""Verify saved model solids against the independent original framing definitions."""
from v26_2_common import *
from shapely.geometry import shape,box as box2
from shapely.ops import unary_union
import hashlib
D=W/'v26_17';O=Path('E:/jz/JIA/Rebuild_V26_17');stage='--prepared'in sys.argv;folder=D/('Prepared'if stage else'Final');prep=json.loads((D/'Prepared.json').read_text('utf8'));proof=prep['proof'];source=json.loads((D/'Input/Source_Index.json').read_text('utf8'));ix={r['name']:r for r in source['objects']};rows={r['name']:r for r in(prep['objects']if stage else json.loads((folder/'Geometry_Index.json').read_text('utf8')))};HN='V26_3_House_Connected_Walls_And_Stairs';EN='HOUSE_V22_CONTINUOUS_BALCONY_EDGE_Geometry'
def mesh(name,base=folder,index=rows):
 a=np.load(base/index[name]['file']);return a,solid(a['v'],a['f'])
a,new=mesh(HN);old_a,old=mesh(HN,D/'Input',ix);ea,edge=mesh(EN);_,old_edge=mesh(EN,D/'Input',ix);checks=[]
def ck(name,yes,**data):checks.append({'check':name,'pass':bool(yes),**data});print('GEOMETRY_QA',name,bool(yes),data if not yes else'',flush=True)
mask=union([cube(*b)for b in proof['ownership_scopes_m']]);outside=[((new-old)-mask).volume(),((old-new)-mask).volume()]
ck('Physical changes stay inside the facade and plate bounds within native float tolerance',max(map(abs,outside))<proof['native_float32_volume_tolerance_m3'],outside_added_removed_m3=outside,tolerance_m3=proof['native_float32_volume_tolerance_m3'])
ck('Whole house remains one positive connected closed solid',len(new.decompose())==1 and new.volume()>0,components=len(new.decompose()))
core_checks=[]
for part in[p for p in proof['parts']if p['type']in['column','beam_x','beam_y']]:
 core=cube(*np.asarray(part['bounds_m'],np.float32).astype(float));missing=(core-new).volume();before=(core-old).volume();core_checks.append({'type':part['type'],'floor':part['floor'],'side':part['side'],'bounds_m':part['bounds_m'],'missing_before_m3':before,'missing_after_m3':missing,'pass':abs(missing)<2e-7})
ck('Ten complete400mm column shafts and all specified rectangular beams are present',all(r['pass']for r in core_checks),members=core_checks)
frame_checks=[]
for f in proof['fixed_return_frames']:
 wa,wm=mesh(f['name']);src=np.load(D/'Input'/ix[f['name']]['file']);overlap=(wm^new).volume();unchanged=np.allclose([wa['v'][:,2].min(),wa['v'][:,2].max()],[src['v'][:,2].min(),src['v'][:,2].max()],rtol=0,atol=2e-6)and np.isfinite(wa['uv']).all()and rows[f['name']]['materials']==ix[f['name']]['materials'];frame_checks.append({'frame':f['name'],'intersects_house_m3':overlap,'source_core_overlap_m3':f['old_frame_core_overlap_m3'],'new_max_y_m':float(wa['v'][:,1].max()),'post_front_y_m':f['post_front_y_m'],'glazing_height_and_materials_retained':bool(unchanged),'pass':abs(overlap)<2e-7 and unchanged and wa['v'][:,1].max()<1.89})
ck('All ten fitted fixed returns clear the house while retaining height and original profiles',all(r['pass']for r in frame_checks),frames=frame_checks)
for b in proof['bays']:
 name=f'BAY_WINDOW_F{b["floor"]}_{b["side"]}_1_Geometry';_,wm=mesh(name,D/'Input',ix);ck('Unchanged central glazing clears restored framing '+name,abs((wm^new).volume())<2e-7,overlap_m3=(wm^new).volume())
edge_out=[((edge-old_edge)-mask).volume(),((old_edge-edge)-mask).volume()];owner_overlap=(new^edge^mask).volume()
ck('Balcony stock has one local owner and preserves the exterior beyond the joint',max(map(abs,edge_out))<2e-6 and abs(owner_overlap)<2e-6,outside_added_removed_m3=edge_out,local_shared_volume_m3=owner_overlap)
# The13m drawing establishes the axis spacing. The endpoints were fitted in
# front of those original columns, rather than translating the building grid.
columns=[p for p in proof['parts']if p['type']=='column'];centres=sorted({round((p['bounds_m'][0][0]+p['bounds_m'][1][0])/2,5)for p in columns})
ck('Original0,3.9,9.1,13m column grid is retained',centres==proof['axes_x_m'],native_column_centres_m=centres)
ck('Prior V26.16 source remains byte-identical',hashlib.sha256(Path(source['model']).read_bytes()).hexdigest()==source['sha256'])
fail=[c for c in checks if not c['pass']];report={'status':'PASS'if not fail else'FAIL','phase':'prepared'if stage else'saved_native','checks':checks,'failures':fail}
if not stage:report['model_sha256']=hashlib.sha256((O/'Blender/Architecture_Complete_V26_17.blend').read_bytes()).hexdigest()
out=D/'Prepared_Geometry_QA.json'if stage else O/'Reports/V26_17_Geometry_QA.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda q:q.item()),'utf8');print('GEOMETRY_QA_DONE',len(checks),len(fail),flush=True)
if fail:raise AssertionError(fail)
