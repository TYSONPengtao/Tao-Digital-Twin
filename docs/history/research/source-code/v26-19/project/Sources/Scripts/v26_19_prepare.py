"""Bounded repair of oversized historical beam encasements and annotated courtyard fixtures."""
from v26_2_common import *
import v26_2_common as C
from v26_15_native_cleanup import repair_indexed
from shapely.geometry import Polygon,box,mapping,GeometryCollection
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
D=W/'v26_19';P=D/'Prepared';P.mkdir(exist_ok=True);C.D=P;J=json.loads((D/'Input/Source_Index.json').read_text('utf8'));ix={r['name']:r for r in J['objects']};HN='V26_3_House_Connected_Walls_And_Stairs';r=ix[HN];a=np.load(D/'Input'/r['file']);h0=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],HN);h=h0
OI={r['name']:r for r in json.loads((W/'v26/Geometry_Index.json').read_text('utf8'))};WHITE='M_Wall_Interior';CEIL='M_V26_3_Neutral_White_Interior_Ceiling';scopes=[];repairs=[]
def bb(lo,hi):return cube(np.asarray(lo,np.float32).astype(float),np.asarray(hi,np.float32).astype(float))
def polys(p):return[p]if p.geom_type=='Polygon'else[q for q in getattr(p,'geoms',[])if q.geom_type=='Polygon'and q.area>1e-12]
def prism(p,z0,z1):
 rings=[]
 for q in polys(p):
  q=orient(q,1);rings.append(np.asarray(q.exterior.coords,np.float32).astype(float)[:-1]);rings.extend(np.asarray(k.coords,np.float32).astype(float)[:-1]for k in q.interiors)
 return mf.CrossSection(rings,mf.FillRule.NonZero).extrude(z1-z0).translate([0,0,z0])if rings else mf.Manifold()
def plan(m,z):
 p=GeometryCollection()
 for ring in m.slice(z).to_polygons():p=p.symmetric_difference(Polygon(ring))
 return p
roi_plan=unary_union([box(x-.225,2.30002,x+.225,7.525)for x in[3.9,9.1]]+[box(-.225,7.075,4.125,7.525),box(8.875,7.075,13.225,7.525),box(-.225,9.575,.225,10.025)])
for fl,floor,under,ceiling in[(1,-.45,3.049999952316284,3.319999933242798),(2,3.45,6.649975776672363,6.920000076293945),(3,7.05,9.950024604797363,10.220000267028809)]:
 z0=float(np.float32(under-.0123));zt=float(np.float32(ceiling));profile=plan(h0,under-.4).intersection(roi_plan).simplify(.00001,preserve_topology=True);roi=prism(roi_plan,z0,zt);wall=prism(profile,z0,zt);beam_parts=[];beam_proof=[]
 for name,br in OI.items():
  if not name.startswith('BEAM_')or f'_F{fl}_'not in name:continue
  lo,hi=br['bounds'];core=bb(lo,hi);kept=h0^core^roi
  if kept.volume()>1e-10:beam_parts.append(kept);beam_proof.append({'source':name,'retained_core_m3':kept.volume()})
 headers=[]
 side=next((q for q in J['objects']if q['name']==f'WINDOW_LEFT_C2120_F{fl}_Geometry'),None)
 if side:
  lo,hi=side['bounds'];head=bb([-.1000000015,lo[1],hi[2]],[.1199999973,hi[1],zt])^roi
  if head.volume()>1e-10:headers.append(head)
 # The rear edge of the left side window meets the original rear-wall header.
 for wr in[q for q in J['objects']if q['name'].startswith(f'WINDOW_BACK_F{fl}_')and q['name'].endswith('_Geometry')]:
  lo,hi=wr['bounds'];head=bb([lo[0],9.68,hi[2]],[hi[0],9.9002,zt])^roi
  if head.volume()>1e-10:headers.append(head)
 desired=wall+union(beam_parts+headers);old=h;h=(h-finish(roi,CEIL,'Remove only oversized historical finish/roof-closure silhouettes above the original beam soffit'))+finish(desired,WHITE,'Continue the adjacent wall and retain existing nominal beam cores and window headers')
 repairs.append({'floor':fl,'z_scope_m':[z0,zt],'wall_profile_sample_z_m':under-.4,'scope_plan':mapping(roi_plan),'wall_profile':mapping(profile),'beam_cores':beam_proof,'removed_m3':(old-h).volume(),'added_m3':(h-old).volume(),'cause':'Historical roof/wall closure extruded an oversized finished outline. Beam-side faces reached X4.1122 instead of the adjacent wall at4.02 or original200/250mm beam section. Side-window nodes also inherited tiny flange fragments and ceiling material on vertical faces.'});scopes.append(roi);print('HEAD_REPAIRED',fl,repairs[-1]['removed_m3'],repairs[-1]['added_m3'],flush=True)
jambs=[]
for fl,floor,ceiling in[(1,-.44999998807907104,3.319999933242798),(2,3.450000047683716,6.920000076293945),(3,7.050000190734863,10.220000267028809)]:
 for cy in[7.3,9.8]:
  # Restore the original400mm rectangular pier at this side-window axis.
  # Its two ends coincide with the existing7.50--9.60m window clear span.
  # This buries the fragmented beam/pier finish without trimming the beam.
  lo=[-.2000202239,cy-.2,floor];hi=[.2000201792,cy+.2,ceiling];arm=bb(lo,hi);addition=(arm-h).volume();h+=finish(arm,WHITE,'Restore continuous original400mm rectangular side-window pier, retaining window clear span');scopes.append(arm);jambs.append({'floor':fl,'axis_y_m':cy,'bounds_m':[lo,hi],'original_section_m':[.4,.4],'added_m3':addition})
scope=union(scopes);row,m=export(HN,h,'Normalize beam/head encasements to adjacent wall sections and preserve existing nominal beam cores');aa=np.load(P/row['file']);v,f,mi,uv,cleanup=repair_indexed(aa['v'],aa['f'].astype(np.int64),aa['mi'],aa['uv']);tt=v[f];no=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);ar=np.linalg.norm(no,axis=1)/2;no/=np.maximum(2*ar[:,None],1e-30);centres=tt.mean(1);inside=np.zeros(len(f),bool)
import shapely
in_plan=shapely.contains_xy(roi_plan.buffer(.000003),centres[:,0],centres[:,1])
for q in repairs:inside|=in_plan&(centres[:,2]>=q['z_scope_m'][0]-.000003)&(centres[:,2]<=q['z_scope_m'][1]+.000003)
vertical=inside&(abs(no[:,2])<.001);down=inside&(no[:,2]<-.999);mi[vertical]=row['materials'].index(WHITE);mi[down]=row['materials'].index(CEIL);bad=~np.isfinite(uv).all((1,2))|(abs(uv).max((1,2))>1e5)
if bad.any():uv[bad]=uv_project(v,f[bad])
np.savez_compressed(P/row['file'],v=v,f=f.astype(np.int64),mi=mi,uv=uv);saved=solid(v,f);row.update(triangles=len(f),closed_components=len(saved.decompose()),volume_m3=saved.volume(),native_cleanup=cleanup);assert len(saved.decompose())==1
outside=[((saved-h0)-scope).volume(),((h0-saved)-scope).volume()];assert max(abs(x)for x in outside)<1e-5,outside
proof={'head_repairs':repairs,'window_jamb_alignments':jambs,'outside_scope_delta_m3':outside,'vertical_white_faces':int(vertical.sum()),'neutral_soffit_faces':int(down.sum()),'fixtures':{'pipe':'CONSTRUCTION_BALCONY_RAINWATER_BRANCH_Geometry','pipe_source':'work/build_scene_v4.py proposedDN100 balcony drainage branch, not a Roman column','planter':'SITE_PLANTER_1_Geometry','planter_source':'work/refine_scene_v3.py solid cylinder assigned M_Wood'},'prior_stair_window_and_gate_repairs_retained':True};rows=[row]
# The annotated cylinder is an early placeholder. Preserve its centre, height
# and ground datum while modelling a tapered ceramic pot, rim and recessed soil.
new_mats=[{'name':'M_V26_19_Terracotta','color':[.25,.085,.038,1.],'roughness':.60},{'name':'M_V26_19_Terracotta_Rim','color':[.30,.11,.052,1.],'roughness':.52},{'name':'M_V26_19_Planter_Soil','color':[.055,.035,.019,1.],'roughness':.96}]
choice='pot'
if(D/'Fixture_Choice.json').exists():choice=json.loads((D/'Fixture_Choice.json').read_text('utf8'))['choice']
archive=['CONSTRUCTION_BALCONY_RAINWATER_BRANCH_Geometry']
if choice=='remove':archive.append('SITE_PLANTER_1_Geometry');new_mats=[]
else:
 pr=ix['SITE_PLANTER_1_Geometry'];lo,hi=np.asarray(pr['bounds']);cx,cy=(lo+hi)[:2]/2;z0=float(lo[2]);z1=float(hi[2]);outline=np.array([[-.8,-1],[.8,-1],[1,-.8],[1,.8],[.8,1],[-.8,1],[-1,.8],[-1,-.8]])
 def loft(zb,zt,rb,rt):
  vv=np.vstack([np.c_[outline*rb+[cx,cy],np.full(8,zb)],np.c_[outline*rt+[cx,cy],np.full(8,zt)]]);ff=[]
  for k in range(1,7):ff.extend([[0,k+1,k],[8,8+k,8+k+1]])
  for k in range(8):n=(k+1)%8;ff.extend([[k,n,8+n],[k,8+n,8+k]])
  return solid(vv,ff)
 outer=loft(z0,z1,.18,.25);inner=loft(z0+.035,z1+.01,.151,.226);body=outer-inner;rim_zone=bb([cx-.26,cy-.26,z1-.025],[cx+.26,cy+.26,z1+.002]);rim=body^rim_zone;body-=rim_zone;soil=loft(z0+.03,z1-.045,.157,.220)
 pot=finish(body,new_mats[0]['name'],'Tapered ceramic body with real inner walls')+finish(rim,new_mats[1]['name'],'Continuous raised planter rim')+finish(soil,new_mats[2]['name'],'Recessed dark soil with no wood texture');rr,pm=export(pr['name'],pot,'Replace wooden solid placeholder with a hollow-rimmed tapered ceramic planter at the original ground datum');pa=np.load(P/rr['file']);pv,pf,pmi,puv,pc=repair_indexed(pa['v'],pa['f'].astype(np.int64),pa['mi'],pa['uv']);np.savez_compressed(P/rr['file'],v=pv,f=pf,mi=pmi,uv=puv);rr.update(triangles=len(pf),native_cleanup=pc);rows.append(rr);proof['fixtures']['planter_model']={'centre_xy_m':[float(cx),float(cy)],'base_z_m':z0,'top_z_m':z1,'soil_z_m':z1-.045,'outer_top_width_m':.5,'body_bottom_width_m':.36,'new_materials':[q['name']for q in new_mats]}
prep={'source':J['model'],'source_sha256':J['sha256'],'objects':rows,'archive':archive,'new_materials':new_mats,'proof':proof};(D/'Prepared.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2),'utf8');print('PREPARED',[(r['name'],r['triangles'])for r in rows],outside,flush=True)
