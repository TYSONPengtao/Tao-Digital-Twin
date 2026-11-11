from v26_2_common import *
import v26_2_common as C
D=W/'v26_4';D.mkdir(exist_ok=True);C.D=D;FD=W/'v26_3/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};rows=[];proof=[];archive=[];cache={}
def load_native(n,snap=False):
 if n in cache:return cache[n]
 r=J[n];a=np.load(FD/r['file']);v=a['v'].copy();delta=0.
 if snap:
  nearest=np.round(v*100)/100;sel=abs(v-nearest)<.000251;v[sel]=nearest[sel];delta=float(np.max(np.linalg.norm(v-a['v'],axis=1)))
 try:m=tracked(v,a['f'],r['materials'],a['mi'],a['uv'],n)
 except RuntimeError:
  from v26_4_orthogonal import recover_orthogonal
  m=recover_orthogonal(a,r['materials'],n)
 pieces=m.decompose();u=union(pieces);assert u.status()==mf.Error.NoError,(n,u.status());cache[n]=u;proof.append({'name':n,'source_parts':len(pieces),'joined_parts':len(u.decompose()),'source_triangle_count':len(a['f']),'removed_internal_overlap_volume_m3':max(0.,m.volume()-u.volume()),'maximum_coordinate_normalization_m':delta});return u
def put(n,m,reason):
 for tol in [0.,.000001,.00001,.00003]:
  trial=m.simplify(tol)if tol else m
  if abs(trial.volume()-m.volume())>.0001:continue
  try:r,u=export(n,trial,reason);rows.append(r);print('PREPARED',n,r['triangles'],r['closed_components'],'volume',r['volume_m3'],flush=True);return u
  except AssertionError as e:print('EXPORT_RETRY',n,tol,str(e),flush=True)
 raise RuntimeError('Cannot save a clean single-surface mesh '+n)
hn='V26_3_House_Connected_Walls_And_Stairs';hr=json.loads((D/'Prepared_House.json').read_text('utf8'))['objects'][0];ha=np.load(D/hr['file']);hv=ha['v'].copy();nearest=np.round(hv*100)/100;mask=(abs(hv-nearest)<.000251)&(hv[:,1]>=1.85)[:,None];hv[mask]=nearest[mask];hm=tracked(hv,ha['f'],['M_V26_3_Neutral_White_Interior_Ceiling'if s=='M_V24_31_White_Painted_Ceiling'else s for s in hr['materials']],ha['mi'],ha['uv'],hn);house=union(hm.decompose()).simplify(.000025)
# Real photographs at 160, 212, 218 and 235 s show a flat white ceiling with
# exposed beam drops. The previous pitched roof underside was incorrectly
# used as the finished ceiling. The absolute datum is inherited model data.
white='M_V26_3_Neutral_White_Interior_Ceiling'
ceiling=union([cube([3.9,2.1,10.22],[13.,9.8,10.28]),cube([0.,7.3,10.02],[3.9,9.8,10.08])]);ceiling=finish(ceiling,white,'F3 photo referenced flat white ceiling, model datum 10.22 / 10.02 m');house=house+ceiling
# Fit opaque wall returns to the actual complete bay frames, rather than to
# the inner glass dimension. The original window objects are untouched.
# Protect every original beam and column from the local wall-side relief.
bay=union([load_native(n)for n in J if n.startswith('BAY_WINDOW_')]);oldcore=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components'];coreindex={r['name']:r for r in json.loads((W/'v26_1/Geometry_Index.json').read_text('utf8'))};cores=[]
for cr in oldcore:
 n=cr['name']
 if not n.startswith(('KZ_','BEAM_')):continue
 ca=np.load(W/'v26_1'/coreindex[n]['file']);cores.append(solid(ca['v'],ca['f'],n))
relief=bay-union(cores);house=house-finish(relief,'M_Wall_Interior','Actual bay-window wall return clearance with original structural cores protected')
put(hn,house.simplify(.000025),'Ordinary wall spans at most 240 mm, retained thin WC partition and original room entries; joined stair solids and photo-referenced flat white third-floor ceiling with original beam drops')
# Reduce the previous over-deep door linings to match the corrected walls.
for n,r in J.items():
 if not(n.startswith('DOOR_')and n.endswith('__FRAME_Geometry')):continue
 a=np.load(FD/r['file']);lo=a['v'].min(0);hi=a['v'].max(0);axis=int(np.argmin((hi-lo)[:2]));depth=hi[axis]-lo[axis]
 if depth<=.24001:continue
 v=a['v'].copy();middle=(lo[axis]+hi[axis])/2;v[:,axis]=middle+(v[:,axis]-middle)*(.238/depth);m=tracked(v,a['f'],r['materials'],a['mi'],a['uv'],n);put(n,union(m.decompose()),'238 mm door lining recessed 1 mm from each plaster face of the 240 mm wall; aperture, original leaf, hinge and animation retained, competing coplanar finish surfaces removed')
for fl in [1,2]:
 n=f'DOOR_FRONT_CENTER_F{fl}__FIXED_Geometry';fixed=load_native(n);put(n,fixed,'Join original fixed frame parts, preserving outer shape and original glass / red frame material ownership')
 n=f'HOUSE_V22_FRONT_TRANSOM_F{fl}_Geometry';m=load_native(n);m=m-fixed;put(n,m,'Remove only transom surfaces already occupied by the existing fixed frame; preserve the visible glass aperture')
 for n in J:
  if n.startswith(f'DOOR_FRONT_CENTER_F{fl}__')and not'FIXED'in n:
   put(n,load_native(n),'Join overlapping parts within the original animated leaf; preserve its parent transform, motion, glass and handle geometry')
n='TERRACE_PHOTO_PIERCED_CROWN_Geometry';crown=load_native(n)
metal=[n for n in J if n.startswith(('TERRACE_CANOPY_POST_','TERRACE_CANOPY_V13_','TERRACE_CANOPY_VISIBLE_PURLINS','TERRACE_CANOPY_WEST_SUPPORTS'))]
parts=[load_native(n)for n in metal];parapet=load_native('TERRACE_STONE_PARAPET_Geometry');frame=union(parts);archive+=metal
canopy=union([load_native('CANOPY_CENTER_0_Geometry'),load_native('CANOPY_CENTER_1_Geometry')]);assembly=union([canopy,parapet,crown,frame]);put('CANOPY_CENTER_0_Geometry',assembly-house,'Join the original terrace parapet, pierced crown, canopy supports and roof carriers with their source materials; remove internal contact faces and trim against the unchanged house seating boundary');archive+=['CANOPY_CENTER_1_Geometry','TERRACE_STONE_PARAPET_Geometry','TERRACE_PHOTO_PIERCED_CROWN_Geometry']
n='CANOPY_CENTER_RIDGE_CAP_Geometry';ridge=load_native(n);trim=cube([-50,-50,-10],[50,2.04,30]);put(n,ridge^trim,'Trim the local ridge end back to Y=2.04 m so it does not penetrate the third-floor window frame and glass; the roof profile is retained')
(D/'Prepared_Geometry.json').write_text(json.dumps({'objects':rows,'archive':archive,'source':'E:/jz/JIA/Rebuild_V26_3/Blender/Architecture_Complete_V26_3.blend','source_sha256':'e257037e222d76990f3a644f11d8d3597071f1fcf849925e215aaa3a1e08eb68','proof':proof},ensure_ascii=False,indent=2),encoding='utf8');print('V26_4_GEOMETRY_READY',len(rows),len(archive),flush=True)
