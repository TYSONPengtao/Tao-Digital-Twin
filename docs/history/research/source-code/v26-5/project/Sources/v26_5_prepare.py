from v26_2_common import *
import v26_2_common as C
D=W/'v26_5';D.mkdir(exist_ok=True);C.D=D
FD=W/'v26_4/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
rows=[];proof=[];cache={}
def native(n):
 if n not in cache:
  r=J[n];a=np.load(FD/r['file']);cache[n]=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],n)
 return cache[n]
def put(n,m,reason):
 # Keep the original curved tile surfaces outside the local cutter exactly.
 # A global simplify can merge overlapping tile laps and change their skin.
 r,u=export(n,m.simplify(.000025)if n=='V26_3_House_Connected_Walls_And_Stairs'else m,reason);rows.append(r);print('PREPARED',n,r['triangles'],r['closed_components'],flush=True);return u
def wall_box(lo,hi,axis,outer_sign=1):
 m=cube(lo,hi);a=m.to_mesh64();v=np.array(a.vert_properties[:,:3]);f=np.array(a.tri_verts);tr=v[f];norm=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);mi=np.where(norm[:,axis]*outer_sign>0,1,0).astype(np.int32)
 return tracked(v,f,['M_Wall_Interior','M_V21_House_Exterior_Grey_White'],mi,name='V26.5 continuous rear wall finish')
HN='V26_3_House_Connected_Walls_And_Stairs';house=native(HN)
# Rebuild only the three rear ground-floor infill spans between original
# columns. Old generic corner exclusions left protruding finish ears and
# a 49.7 mm unclosed window-head end. Original core solids stay protected.
PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))}
coreproof=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components'];cores=[]
for r in coreproof:
 if not r['name'].startswith(('KZ_','BEAM_')):continue
 a=np.load(PD/PI[r['name']]['file']);cores.append(solid(a['v'],a['f'],r['name']))
core=union(cores)
for x0,x1,wn in [(.2,3.7,'WINDOW_BACK_F1_1_Geometry'),(4.1,8.9,'WINDOW_BACK_F1_2_Geometry'),(9.3,12.8,'WINDOW_BACK_F1_3_Geometry')]:
 region=cube([x0,9.5,-.45],[x1,10.05,3.320025]);r=J[wn];lo,hi=np.array(r['bounds']);opening=cube([lo[0],9.45,lo[2]],[hi[0],10.1,hi[2]])
 carrier=wall_box([x0,9.68,-.45],[x1,9.9002,3.320025],1)-finish(opening,'M_Wall_Interior','Actual unchanged rear window opening')
 if x0==9.3:carrier=carrier+finish(cube([10.6,9.45,-.45],[10.7,9.9002,3.320025]),'M_Wall_Interior','100 mm WC divider sealed to rear carrier')
 # Keep all original beam/column cores, including their actual corner seats.
 house=(house-finish(region-core,'M_Wall_Interior','Remove obsolete rear finish ears only'))+carrier
 proof.append({'repair':'Rear F1 span and window head','span_x_m':[x0,x1],'rear_inner_y_m':9.68,'rear_outer_y_m':9.9002,'nominal_thickness_mm':220.2,'window':wn,'window_bounds_unchanged':r['bounds']})
for k in [1,2,3]:
 n=f'CONSTRUCTION_SILL_WINDOW_BACK_F1_{k}_Geometry';wn=f'WINDOW_BACK_F1_{k}_Geometry';lo,hi=np.array(J[wn]['bounds']);m=native(n);trim=finish(cube([lo[0],9.,-.7],[hi[0],10.5,3.5]),J[n]['materials'][0],'Rear sill and head end at actual window jamb')
 put(n,m^trim,'Trim only rear ground-floor sill and head ends to their actual window width; no piece crosses the 100 mm WC divider or the adjacent column')
# Local west courtyard roof end follows the original bay's exterior plane.
# The secondary screenwall and original window mesh are never modified.
n=np.array([.8111365302967483,.5848568450639461]);limit=1.1723606549172076
poly=[[(limit-n[1]*y)/n[0],y]for y in [.7,2.3]]+[[1.,2.3],[1.,.7]];cut=section(poly,3.5).translate([0,0,-.7])
for name in J:
 if not(name.startswith('SITE_COURTYARD_WEST_TILE_WALL_')or name=='V26_1_Courtyard_West_Wall_Single_Surface'):continue
 m=native(name);removed=(m^cut).volume()
 if removed<1e-12:continue
 mat='M_V24_11_Plain_White_Limewash'if name.startswith('V26_1_')else J[name]['materials'][0]
 result=put(name,m-finish(cut,mat,'Local courtyard to bay end cut, 10 mm outside original frame'),'Trim only the west courtyard wall/roof end outside the unchanged left bay frame; remove roof intrusion into glass and seal newly cut solids')
 proof.append({'repair':'Local west courtyard bay junction','name':name,'removed_volume_m3':removed,'clip_normal_xy':n.tolist(),'clip_limit_m':limit,'new_bay_intersection_m3':(result^native('BAY_WINDOW_F1_L_0_Geometry')).volume()})
# Remaining facade junction repairs are kept in a small separately reviewable
# recipe. It operates only on the house mesh and leaves glazing untouched.
recipe=W/'v26_5_facade_recipe.py'
if recipe.exists():exec(compile(recipe.read_text('utf8'),str(recipe),'exec'))
put(HN,house,'Regular rear ground-floor window heads and WC divider junction; eliminate obsolete window sill protrusions, retain original beam/column cores, close confirmed floor-band and bay return finish gaps')
(D/'Prepared_Geometry.json').write_text(json.dumps({'source':'E:/jz/JIA/Rebuild_V26_4/Blender/Architecture_Complete_V26_4.blend','source_sha256':'c5f5465eea815fa3c3545855b25036629ed2a5ceda091ac6f2c6850fd4b81663','objects':rows,'archive':[],'proof':proof},ensure_ascii=False,indent=2),encoding='utf8')
print('PREPARE_DONE',len(rows),flush=True)
