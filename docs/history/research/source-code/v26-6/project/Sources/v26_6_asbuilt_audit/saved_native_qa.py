from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parent.parent;sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,cube,union
O=Path('E:/jz/JIA/Rebuild_V26_6');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_6.blend';FD=W/'v26_6/Final';OD=W/'v26_5/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};OJ={r['name']:r for r in json.loads((OD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';a=np.load(FD/J[HN]['file']);oa=np.load(OD/OJ[HN]['file']);m=solid(a['v'],a['f']);old=solid(oa['v'],oa['f']);checks=[]
def ck(name,yes,**data):checks.append({'check':name,'pass':bool(yes),**data});print('CHECK',name,bool(yes),data if not yes else'',flush=True)
with P.open('rb')as ff:sha=hashlib.file_digest(ff,'sha256').hexdigest()
ck('Saved model hash matches final native readback model',sha==(sys.argv[1]if len(sys.argv)>1 else'91658818088645640cce31c57b4f256b937288523f44fd6f56fd28a1f48a29d6'),sha256=sha)
# Sight and clear-body rays are sampled over the formerly blocked infill.
opening=[]
for x in [.35,.65,1.,1.35,1.7,2.05,2.35,2.8,3.35]:
 for z in [7.10,7.4,7.9,8.4,8.9,9.4,9.8,9.93]:
  b=old.ray_cast([x,6.9,z],[x,7.7,z]);n=m.ray_cast([x,6.9,z],[x,7.7,z]);opening.append(dict(x_m=x,z_m=z,source_hits=len(b),saved_hits=len(n)))
ck('Photo-supported F3 terrace opening is clear across the column span below header',all(q['saved_hits']==0 for q in opening),samples=len(opening),source_previously_blocked_samples=sum(q['source_hits']>0 for q in opening),failures=[q for q in opening if q['saved_hits']])
# Compare complete original solids rather than just their bounding boxes.
PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))};core=[]
for name in ['BEAM_X_F3_7.3_0_Geometry','KZ_1_2_F3_Geometry','KZ_2_2_F3_Geometry']:
 q=np.load(PD/PI[name]['file']);c=solid(q['v'],q['f']);core.append(dict(name=name,source_volume_m3=c.volume(),source_missing_from_v26_5_m3=(c-old).volume(),saved_missing_volume_m3=(c-m).volume()))
ck('Original structural header and both columns are retained as complete solids',all(q['saved_missing_volume_m3']<=q['source_missing_from_v26_5_m3']+1e-7 for q in core),cores=core,tolerance_volume_m3=1e-7)
roof=[]
photo_interior=cube([.2,7.3,7.05],[3.7,9.9002,10.020025])
for name in ['ROOF_MAIN_JOINED_Geometry','ROOF_EAVE_FASCIA_Geometry']:
 q=np.load(PD/PI[name]['file']);mroof=solid(q['v'],q['f']);mroof=mroof-photo_interior if name=='ROOF_EAVE_FASCIA_Geometry'else mroof;was=old^mroof;now=m^mroof;diff=((was-now)+(now-was)).volume();roof.append(dict(name=name,scope='Exterior eave outside photographed alcove interior'if name=='ROOF_EAVE_FASCIA_Geometry'else'Complete original roof',source_occupied_volume_m3=was.volume(),saved_occupied_volume_m3=now.volume(),symmetric_difference_m3=diff))
ck('Original main roof and exterior eave remain unchanged outside photo-supported interior cleanup',all(q['symmetric_difference_m3']<1e-7 for q in roof),components=roof,tolerance_volume_m3=1e-7)
# Lower storeys must remain exactly as before apart from floating arithmetic
# and the separately authorised material-only stair front partition.
stair_material_zones=union([cube([5.1989,8.5399,1.3599],[5.2011,9.5501,1.5001]),cube([5.1989,8.5399,5.1099],[5.2011,9.5501,5.2501]),cube([7.7989,7.4199,3.3198],[7.8011,8.5601,3.4501]),cube([7.7989,7.4199,6.9198],[7.8011,8.5401,7.0501])]);region=cube([-1.,0.,-1.],[15.,11.,7.049])-stair_material_zones;lold=old^region;lnew=m^region;ldiff=((lold-lnew)+(lnew-lold)).volume()
ck('Photo-supported F3 opening did not change lower floors outside authorised stair-front material boundaries',ldiff<1e-6,source_lower_volume_m3=lold.volume(),saved_lower_volume_m3=lnew.volume(),symmetric_difference_m3=ldiff,tolerance_volume_m3=1e-6)
# Exact native world-coordinate data and material indices of the real glass,
# original frames, stone surrounds and original exterior terrace components.
names=['WINDOW_BACK_F3_1_Geometry','WINDOW_LEFT_C2120_F3_Geometry','CONSTRUCTION_SILL_WINDOW_BACK_F3_1_Geometry','CONSTRUCTION_SILL_WINDOW_LEFT_C2120_F3_Geometry','HOUSE_V21_F3_TERRACE_RECTANGULAR_TILE_FINISH_Geometry','HOUSE_V21_F3_TERRACE_TILE_GROUT_Geometry','TERRACE_SIDE_CERAMIC_PANEL_GRID_Geometry','V24_32_F3_Terrace_Panel_Recessed_Grout'];retained=[]
for name in names:
 n=np.load(FD/J[name]['file']);b=np.load(OD/OJ[name]['file']);retained.append(dict(name=name,unchanged=J[name]['materials']==OJ[name]['materials']and all(np.array_equal(n[k],b[k])for k in ['v','f','mi','uv'])))
ck('Alcove glazing frames surrounds and terrace tile components remain byte-exact native arrays',all(q['unchanged']for q in retained),components=retained)
# Check only glass-owned closed panes; legitimate frame/host contacts are
# excluded from a glazing occlusion test.
glass=[]
for name in ['WINDOW_BACK_F3_1_Geometry','WINDOW_LEFT_C2120_F3_Geometry']:
 q=np.load(FD/J[name]['file']);glass_ids=[i for i,n in enumerate(J[name]['materials'])if'Glass'in n];f=q['f'][np.isin(q['mi'],glass_ids)];g=solid(q['v'],f,name+' actual glass panes');overlap=(m^g).volume();glass.append(dict(window=name,glass_volume_m3=g.volume(),opaque_house_intersection_m3=overlap))
ck('New plain window heads do not block original glass panes',all(q['opaque_house_intersection_m3']<1e-9 for q in glass),windows=glass,tolerance_volume_m3=1e-9)
heads=[]
for x in [.35,.8,1.25,1.7,2.15,2.6,3.05,3.5]:
 for z in [9.905,9.925,9.945,9.965,9.985,10.005,10.015]:
  hs=m.ray_cast([x,9.4,z],[x,10.1,z]);first=hs[0]if hs else None;heads.append(dict(window='rear',along_m=x,z_m=z,head_face_m=first.position[1]if first else None,pass_=first is not None and abs(first.position[1]-9.68)<.001))
for y in [7.6,7.9,8.2,8.5,8.8,9.1,9.4,9.5]:
 for z in [9.905,9.925,9.945,9.965,9.985,10.005,10.015]:
  hs=m.ray_cast([.5,y,z],[-.3,y,z]);first=hs[0]if hs else None;heads.append(dict(window='west',along_m=y,z_m=z,head_face_m=first.position[0]if first else None,pass_=first is not None and abs(first.position[0]-.12)<.001))
ck('West and rear plain head faces continue without ledges or gaps to the flat ceiling',all(q['pass_']for q in heads),samples=len(heads),tolerance_m=.001,failures=[q for q in heads if not q['pass_']])
ceil=[]
for x in [.5,1.,1.5,2.,2.5,3.,3.051,3.10,3.15,3.179,3.3,3.4]:
 for y in [7.7,8.2,8.7,9.2,9.5]:
  hs=m.ray_cast([x,y,9.6],[x,y,10.3]);h=hs[0]if hs else None;ceil.append(dict(xy_m=[x,y],surface_z_m=h.position[2]if h else None,pass_=h is not None and abs(h.position[2]-10.02)<.001 and h.normal[2]<-.99))
ck('Photographed alcove has an unbroken flat ceiling at inherited model datum',all(q['pass_']for q in ceil),samples=len(ceil),model_datum_m=10.02,tolerance_m=.001,failures=[q for q in ceil if not q['pass_']])
ck('Saved house stays one closed positive manifold',m.status()==mf.Error.NoError and len(m.decompose())==1 and m.volume()>0,components=len(m.decompose()),volume_m3=m.volume())
fails=[c for c in checks if not c['pass']];out={'model':str(P),'model_sha256':sha,'source_model':'E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend','status':'PASS'if not fails else'FAIL','checks':checks,'failures':fails,'photo_evidence':str(W/'v26_6_asbuilt_audit/AsBuilt_F3_Terrace_Crosswall_Findings.json'),'evidence':{'opening_rays':opening,'head_rays':heads,'ceiling_rays':ceil},'metric_limit':'Absolute model coordinates are inherited design data; actual uncalibrated video independently supports the open terrace-to-alcove topology, retained columns/header and white flat ceiling, not surveyed dimensions.'}
(R/'V26_6_AsBuilt_Terrace_Regression_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('ASBUILT_TERRACE_GEOMETRY_DONE',out['status'],len(checks),len(fails),flush=True)


