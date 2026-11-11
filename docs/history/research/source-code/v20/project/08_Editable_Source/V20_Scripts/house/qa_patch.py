import json,sys,ast,math
from pathlib import Path
W=Path(__file__).parents[1];D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold']],type_ignores=[]),'old_helpers','exec'))
Q=json.loads((D/'House_Mutation.json').read_text(encoding='utf8'));E={e['name']:e for e in Q['replace']+Q['add']};qa={'status':'PASS_LOCAL_PATCH_QA','closed_positive':[],'probe_tests':[]}
ms={}
for e in E.values():
 mm=[]
 for i,p in enumerate(e['parts']):
  m=manifold(p['geometry']);assert m.status()==mf.Error.NoError and m.volume()>0;mm.append(m)
  qa['closed_positive'].append({'node':e['name'],'part':i,'volume_m3':m.volume(),'triangles':m.num_tri(),'status':str(m.status())})
 ms[e['name']]=mf.Manifold.batch_boolean(mm,mf.OpType.Add)
def test(n,xyz,size,expected_volume,label):
 m=manifold({'type':'box','origin':xyz,'size':size});over=(ms[n]^m).volume();assert abs(over-expected_volume)<1e-5,(label,over,expected_volume)
 qa['probe_tests'].append({'label':label,'overlap_m3':over,'expected_m3':expected_volume})
wn='HOUSE_V20_F1_PHOTO_MISSING_INFILL_WALLS'
test(wn,[5,7.25,.25],[.5,.05,2.0],.05,'Stair front solid')
test(wn,[9.6,7.25,.25],[.5,.05,2.0],.05,'Right rear solid')
test(wn,[8,7.10,0],[.8,.6,2.1],0,'Stair side access remains clear')
test(wn,[11.95,7.15,.1],[.70,.3,1.9],0,'Right bathroom original doorway remains clear')
test(wn,[8.95,8.65,.1],[.30,.7,1.9],0,'Original kitchen side door remains clear')
pn='HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT'
test(pn,[4,-.25,-.14],[.5,.20,.13],.013,'Single tread filled solid')
test(pn,[4.5,.3,-.44],[.5,.5,.28],.07,'Porch underside filled solid')
fn='HOUSE_V20_F3_RIGHT_BEDROOM_RED_BROWN_WOOD_FLOOR'
test(fn,[11.2,8.2,7.5],[.3,.3,.004],0,'Bathroom wood finish excluded')
test(fn,[9.5,3,7.5],[.3,.3,.004],.00036,'Bedroom wood finish present')
def height_at(name,x,y):
 v,ff,_,_=ex.solid_data(E[name]['parts'][0]['geometry']);f=np.array(triangles(v,ff));t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);t=t[no[:,2]>1e-9]
 a=t[:,0,:2];u=t[:,1,:2]-a;v0=t[:,2,:2]-a;w=np.array([x,y])-a;de=u[:,0]*v0[:,1]-u[:,1]*v0[:,0];aa=(w[:,0]*v0[:,1]-w[:,1]*v0[:,0])/de;bb=(u[:,0]*w[:,1]-u[:,1]*w[:,0])/de;good=(aa>=-1e-5)&(bb>=-1e-5)&(aa+bb<=1+1e-5);assert good.any()
 return float(np.max(t[good,0,2]+aa[good]*(t[good,1,2]-t[good,0,2])+bb[good]*(t[good,2,2]-t[good,0,2])))
south='SITE_V12_REBUILT_COURT_0_-20_0';north='SITE_V12_REBUILT_COURT_0_0_0'
joint=[]
for x in np.linspace(2.75,10.25,81):joint.append(abs(height_at(south,x,0)-height_at(north,x,0)))
qa['court_joint_y0_max_height_difference_m']=max(joint);assert max(joint)<1e-5,max(joint)
near=[height_at(south,x,-.30) for x in [3.75,4.0,6.5,9.0,9.25]];qa['adjacent_single_riser_ground_levels_m']=near;assert max(abs(h+.15) for h in near)<.003,near
GP=json.loads((W/'v20_gate_pavilion/Mutation.json').read_text(encoding='utf8'));de=next(e for e in GP['add'] if e['name']=='SITE_V20_PAVILION_RAISED_WOOD_SLATS')
dvs=np.concatenate([ex.world_part(p,de)[0] for p in de['parts']]);db=np.array([dvs.min(0),dvs.max(0)]);ground=de['nominal_ground_m']
deck_points=[[x,y] for x in np.linspace(db[0,0]+.01,db[1,0]-.01,13) for y in np.linspace(db[0,1]+.01,db[1,1]-.01,13)]
levels=[height_at(south,x,y) for x,y in deck_points];assert max(abs(z-ground) for z in levels)<1e-6
qa['pavilion_ground']={'sample_points':len(deck_points),'coverage_gaps':0,'ground_min_m':min(levels),'ground_max_m':max(levels),'deck_bottom_m':de['board_bottom_m'],'wood_board_under_clearance_min_m':de['board_bottom_m']-max(levels),'wood_board_under_clearance_max_m':de['board_bottom_m']-min(levels)}
dm=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in de['parts']],mf.OpType.Add)
inter=(ms[south]^dm).volume();assert abs(inter)<1e-10
qa['pavilion_ground']['paving_deck_overlap_m3']=inter
audit=Q['house_reference_audit']['pavilion_ground'];ob=audit['old_platform_footprint_xy'];outer=audit['ground_transition_outer_bounds_xy'];cxy=[(ob[0]+ob[2])/2,(ob[1]+ob[3])/2]
bound=[height_at(south,x,y) for x,y in [[outer[0],cxy[1]],[outer[2],cxy[1]],[cxy[0],outer[1]],[cxy[0],outer[3]]]]
assert max(abs(z+.45) for z in bound)<1e-6;qa['pavilion_ground']['four_outer_transition_edges_m']=bound
qa['pavilion_ground']['entry_approach_disjoint']=audit['does_not_intersect_entry_grade'];assert audit['does_not_intersect_entry_grade']
qa['scope']={'original_native_not_touched':True,'all_perimeter_drains_and_original_scan_unmodified':True,'F3_supported_terrace_route_unmodified':True,'door_leaf_rotation_not_in_patch':True,'wall_positions_photo_fit_not_field_measured':True}
(D/'House_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(qa,ensure_ascii=False,indent=2),flush=True)
