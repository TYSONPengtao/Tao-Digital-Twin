from pathlib import Path
import sys
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W))
from v26_2_common import *
import v26_2_common as C
BASE=W/'v26_7_column_audit';broad='--broad'in sys.argv
D=BASE/'candidate_broad'if broad else BASE;C.D=D;D.mkdir(parents=True,exist_ok=True)
FD=W/'v26_6/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
HN='V26_3_House_Connected_Walls_And_Stairs';r=J[HN];a=np.load(FD/r['file'])
house=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],HN);before=house
white='M_Wall_Interior';ceiling='M_V26_3_Neutral_White_Interior_Ceiling'
PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))}
cp=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components']
proof=[];rows=[];cuts=[]

def srcsolid(n):
 a=np.load(PD/PI[n]['file']);return solid(a['v'],a['f'],n)
stair_names=[f'STAIR_F{fl}_FLIGHT{k}_Geometry'for fl in[1,2]for k in[1,2]]+[f'STAIR_LANDING_F{fl}_Geometry'for fl in[1,2]]
stair_parts={n:srcsolid(n)for n in stair_names};stairs=union(list(stair_parts.values()))
beam_parts={}
for cr in cp:
 n=cr['name']
 if not n.startswith(('BEAM_','V26_Stair_Frame_')):continue
 lo,hi=np.array(cr['bounds_m']);beam_parts[n]=srcsolid(n)if n in PI else cube(lo,hi)
beams=union(list(beam_parts.values()))
eastwalk=union([cube([7.7998,7.2799,3.3199],[9.3004,9.8201,3.4502]),cube([7.7998,7.2799,6.9199],[9.3004,9.8201,7.0502])])
protect=stairs+beams

def cutter_finish(m,tag):
 b=m.to_mesh64();v=np.array(b.vert_properties[:,:3]);f=np.array(b.tri_verts);t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);mi=(n[:,2]>1e-9).astype(np.int32)
 return tracked(v,f,[white,ceiling],mi,name=tag)
def cut(m,tag,protect_extra=None):
 global house
 m=m-protect
 if protect_extra is not None:m=m-protect_extra
 removed=max(0.,(house^m).volume())
 if removed<1e-12:return
 cuts.append(m);house=house-cutter_finish(m,tag);proof.append({'operation':tag,'removed_volume_m3':removed});print('CUT',tag,removed,flush=True)
def wallcarrier(x0,x1,z0,z1,opening):
 m=cube([x0,9.68,z0],[x1,9.9002,z1]);b=m.to_mesh64();v=np.array(b.vert_properties[:,:3]);f=np.array(b.tri_verts);t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);mi=(n[:,1]>.001).astype(np.int32)
 m=tracked(v,f,[white,'M_V21_House_Exterior_Grey_White'],mi,name='Continuous rear interior wall carrier220.2mm')
 return m-finish(opening,white,'Unchanged actual rear glazing opening')

# Trim only each local synthetic400mm column/finish-halo joint outside the
# existing regular wall union. Original beam downstands and stair solids are
# protected. At rear joints the exterior north side remains untouched.
for fl,z0,z1 in[(1,-.45,3.32),(2,3.45,6.92),(3,7.05,10.22)]:
 joints=[(3.9,7.3,'SW'),(9.1,7.3,'SE'),(3.9,9.8,'NW'),(9.1,9.8,'NE')]
 if broad:
  joints=[]
  for cr in cp:
   if cr['name'].startswith('KZ_')and f'_F{fl}_'in cr['name']:
    xy=np.mean(np.array(cr['bounds_m']),axis=0)[:2];joints.append((round(float(xy[0]),1),round(float(xy[1]),1),cr['name']))
 for x,y,label in joints:
  reg=cube([x-.25,y-.25,z0+.0001],[x+.25,y+.25,z1-.0001])
  # Retain real crossing wall strips rather than a synthetic exposed400mm post.
  xp=[x-.12,x+.12]
  if fl==1 and x==9.1 and y==9.8:xp=[9.,9.2]
  yp=[9.68,9.9002]if y==9.8 else[y-.12,y+.12]
  allowed=cube([xp[0],y-.3,z0],[xp[1],y+.3,z1])+cube([x-.3,yp[0],z0],[x+.3,yp[1],z1])
  if broad and fl==1 and x==9.1 and y==7.3:
   # Existing main bedroom wall is240mm south of the crossing; the north
   # WC wall is200mm. Match each actual side instead of leaving20mm ears.
   allowed=cube([8.98,y-.3,z0],[9.22,7.42,z1])+cube([9.,7.42,z0],[9.2,y+.3,z1])+cube([x-.3,yp[0],z0],[x+.3,yp[1],z1])
  m=reg-allowed
  if y==9.8:m=m^cube([x-.3,9.5,z0],[x+.3,9.68,z1])
  if broad:
   # Trim only ordinary room-facing projections. Keep exterior column
   # silhouettes and front bay/porch geometry outside these inner planes.
   m=m^cube([.12,2.22,z0],[12.88,9.68,z1])
  cut(m,f'F{fl} local{label} unsupported exposed column and finish halo')
 # Align remaining hall-side old finish tabs to actual established wall faces.
 ztop=10.02 if fl==3 else z1
 band=[('west',[4.02,7.42,z0+.0001],[4.15,9.68,ztop-.0001]),
       ('south',[4.02,7.42,z0+.0001],[8.98,7.55,z1-.0001]),
       ('north',[4.02,9.55,z0+.0001],[8.98,9.68,z1-.0001])]
 # The F1 north WC side wall is200mm, unlike the240mm upper walls.
 ex=9.00 if fl==1 else 8.98
 band.append(('east',[8.85,7.42,z0+.0001],[ex,9.68,z1-.0001]))
 for label,lo,hi in band:cut(cube(lo,hi),f'F{fl} stair hall{label} obsolete finish tabs')

# The upper rear window carriers still used the old stepped head/underwindow
# joint plan. Rebuild their interior220.2mm finish to the exact native glazing
# bounds. Keep perpendicular WC walls, source beams, stairs and outer facade.
for fl,z0,z1 in[(2,3.45,6.92),(3,7.05,10.22)]:
 for k,(x0,x1)in enumerate([(.2,3.7),(4.1,8.9),(9.3,12.8)],1):
  wn=f'WINDOW_BACK_F{fl}_{k}_Geometry';lo,hi=np.array(J[wn]['bounds']);ztop=10.02 if fl==3 and k==1 else z1
  opening=cube([lo[0],9.45,lo[2]],[hi[0],10.1,hi[2]])
  region=cube([x0,9.5,z0+.0001],[x1,9.9002,ztop-.0001])
  perp=[]
  if fl==2 and k==1:perp.append(cube([2.116,9.45,z0],[2.284,9.68,ztop]))
  if k==3:perp.append(cube([10.716,9.45,z0],[10.884,9.68,ztop]))
  keeper=union(perp)if perp else mf.Manifold()
  cut(region,f'F{fl} rear window{k} old underpanel and notched head carrier',keeper)
  carrier=wallcarrier(x0,x1,z0+.0001,ztop,opening)
  old=house;house=house+carrier;proof.append({'operation':f'F{fl} rear window{k} regular carrier','added_volume_m3':max(0.,(house-old).volume()),'wall_thickness_mm':220.2,'window_bounds_unchanged':J[wn]['bounds']})

# Remove the92.2mm floor-level ledge only on non-walking west/north/south
# edges. The east upper-arrival floor, four flights, both midlandings and
# original finite-area bearing tongues are explicitly outside the cutters.
for fl,z0,z1 in[(1,3.31999,3.45004),(2,6.91999,7.05002)]:
 for label,lo,hi in[
  ('west',[4.02,7.42,z0],[4.15,9.68,z1]),
  ('north',[4.02,9.55,z0],[7.8,9.68,z1]),
  ('south',[4.02,7.42,z0],[7.8,7.55,z1])]:
  cut(cube(lo,hi),f'F{fl} nonwalking{label} floor band flush to wall',eastwalk)

def put(n,m,reason):
 for tol in[0.,.000001,.00001,.000025]:
  trial=m.simplify(tol)if tol else m
  if abs(trial.volume()-m.volume())>1e-5:continue
  try:
   row,saved=export(n,trial,reason);rows.append(row);print('EXPORTED',n,row['triangles'],row['closed_components'],flush=True);return saved
  except AssertionError as e:print('EXPORT_RETRY',n,tol,str(e),flush=True)
 raise RuntimeError('No clean export for'+n)
for fl in[2,3]:
 for k in[1,2,3]:
  n=f'CONSTRUCTION_SILL_WINDOW_BACK_F{fl}_{k}_Geometry';wn=f'WINDOW_BACK_F{fl}_{k}_Geometry';rr=J[n];aa=np.load(FD/rr['file']);m=tracked(aa['v'],aa['f'],rr['materials'],aa['mi'],aa['uv'],n);lo,hi=np.array(J[wn]['bounds']);clip=finish(cube([lo[0],9.,-.8],[hi[0],10.5,11.]),rr['materials'][0],'Actual original rear window jamb width')
  put(n,m^clip,'Upper rear sill/head ends match original native window jambs; unchanged window mesh, glazing and doors')
saved=put(HN,house,'Remove unsupported synthetic exposed column/finish-halo projections at stair hall joints, regularize upper rear underwindow/head carriers, remove only nonwalking floor ledges; preserve native stairs, bearings, beam downstands, openings and white ceilings')
out={'source':'E:/jz/JIA/Rebuild_V26_6/Blender/Architecture_Complete_V26_6.blend','source_sha256':'ea7cd20cb3c30cf2b5984c1e262ca182fa3c168a8a16fd7201ef428267bf05b7','objects':rows,'archive':[],'proof':proof,'protected_stair_names':stair_names,'protected_beam_names':list(beam_parts),'no_stairwell_fill':True,'no_new_thick_walls':True,'new_window_carrier_thickness_mm':220.2,'intentional_change':'Synthetic400mmcolumn source volumes are trimmed where they formed unsupported visible room projections; original beam downstand geometry and actual stairs remain protected.'}
(D/'Prepared_Geometry.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
# Save actual net subtraction/addition regions for independent locality checks.
for name,m in [('Removed_Only',before-saved),('Added_Only',saved-before)]:
 b=m.to_mesh64();np.savez_compressed(D/(name+'.npz'),v=np.array(b.vert_properties[:,:3]),f=np.array(b.tri_verts))
print('CANDIDATE_READY',len(rows),'REMOVED',(before-saved).volume(),'ADDED',(saved-before).volume(),flush=True)
