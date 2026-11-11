from v26_2_common import *
import v26_2_common as C
D=W/'v26_6';D.mkdir(exist_ok=True);C.D=D
FD=W/'v26_5/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';r=J[HN];a=np.load(FD/r['file']);house=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],HN);before=house;proof=[]
PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))};cp=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components'];cores=[]
for row in cp:
 if not row['name'].startswith(('KZ_','BEAM_')):continue
 x=np.load(PD/PI[row['name']]['file']);cores.append(solid(x['v'],x['f'],row['name']))
core=union(cores)
def cap_material(m,name,floor_bottom=False):
 b=m.to_mesh64();v=np.array(b.vert_properties[:,:3]);f=np.array(b.tri_verts);t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);mi=np.zeros(len(f),np.int32)
 if floor_bottom:mi[n[:,2]<0]=1
 return tracked(v,f,['M_Wall_Interior','M_Floor'],mi,name=name)
# Actual video at175s/lens0 and180s/lens1 shows the whole F3 alcove
# opening below the existing header. Never propagate this removal to F1/F2.
opening=cube([.19,7.0,7.05],[3.71,7.60,9.951])-core
house=house-cap_material(opening,'Photo supported F3 terrace full-width opening',True)
proof.append({'repair':'Remove erroneous F3 west terrace crosswall only','source_video':'E:/jz/VID_20260507_152114_00_001.insv','evidence_frames':[[175,0],[180,1],[200,0],[205,1]],'removed_region_m':[[.19,7.,7.05],[3.71,7.6,9.951]],'original_columns_header_retained':True,'lower_floor_partitions_not_removed':True})
# The two high windows in the photographed alcove have plain white heads
# meeting a flat white ceiling. Replace only obsolete stepped finish ears.
white='M_V26_3_Neutral_White_Interior_Ceiling';ceiling=cube([0.,7.3,10.02],[3.9,9.8,10.08]);protect=core+ceiling
for name,region,carrier in [
 ('rear',cube([.2,9.4,9.899975],[3.7,9.9002,10.02001]),cube([.2,9.68,9.899975],[3.7,9.9002,10.08])),
 ('left',cube([-.1,7.5,9.899975],[.3,9.6,10.02001]),cube([-.1,7.5,9.899975],[.12,9.6,10.08]))]:
 house=(house-finish(region-protect,'M_Wall_Interior','Remove obsolete high-window head finish ears'))+finish(carrier,'M_Wall_Interior','Photo referenced plain white alcove window head')
 proof.append({'repair':'F3 alcove '+name+' window head','source_frames':[[170,0],[175,0],[205,1]],'plain_finish_to_existing_flat_ceiling':True,'glazing_and_roof_unchanged':True})
# The old main-roof fascia passes through the photographed flat alcove
# ceiling. Trim its INSIDE portion only; retain the exterior eave silhouette.
inside=cube([.20001,7.42501,9.95],[3.69999,9.67999,10.02001])-protect
house=house-finish(inside,white,'Photo supported clearance below the existing flat white alcove ceiling')
proof.append({'repair':'Remove only interior obsolete roof fascia below alcove white ceiling','crop_m':[[.20001,7.42501,9.95],[3.69999,9.67999,10.02001]],'source_frames':[[170,0],[175,0],[205,1]],'original_exterior_eave_retained':True})
# Assign only existing walking-facing polygons; there is no added material
# layer and no slicing operation on the stair mesh.
risers=[{'name':'F1_midlanding','x':5.2,'normal_x':1.,'lo':[5.199,8.54,1.32269],'hi':[5.201,9.550001,1.500001]},
 {'name':'F2_midlanding','x':5.2,'normal_x':1.,'lo':[5.199,8.54,5.08636],'hi':[5.201,9.550001,5.250001]},
 {'name':'F1_upper_arrival','x':7.8,'normal_x':-1.,'lo':[7.799,7.42,3.31999],'hi':[7.801,8.560001,3.450001]},
 {'name':'F2_upper_arrival','x':7.8,'normal_x':-1.,'lo':[7.799,7.42,6.91999],'hi':[7.801,8.540001,7.050001]}]
row,house=export(HN,house,'Photo supported F3 open terrace and plain window heads, before material-only riser assignment');pa=np.load(D/row['file']);v=pa['v'];f=pa['f'];t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-30);mi=pa['mi'].copy();gray='M_V24_31_Stair_Gray_Marble';g=row['materials'].index(gray)
for q in risers:
 sel=(np.max(abs(t[:,:,0]-q['x']),axis=1)<.00001)&(n[:,0]*q['normal_x']>.99)
 if 'midlanding' in q['name']:
  # Include tiny junction triangles crossing the real adjacent tread height.
  # Their full faces may extend a few mm below it, hidden by the tread.
  sel&=(t.max(1)[:,1]>=q['lo'][1]-.00001)&(t.min(1)[:,1]<=q['hi'][1]+.00001)&(t.max(1)[:,2]>=q['lo'][2]-.00001)&(t.min(1)[:,2]<=q['hi'][2]+.00001)
 else:
  sel&=(t.min(1)[:,2]>=q['lo'][2]-.00001)&(t.max(1)[:,2]<=q['hi'][2]+.00001)
 mi[sel]=g;proof.append({'repair':'Gray stone walking front at '+q['name'],'source_video_frames':[[115,0],[125,0],[140,0],[150,0]],'triangles_recolored':int(sel.sum()),'original_tread_and_landing_elevations_unchanged':True,'white_undersides_retained':True,'paint_region_m':[q['lo'],q['hi']]})
np.savez_compressed(D/row['file'],v=v,f=f,mi=mi,uv=pa['uv']);row['reason']='Photo supported F3 terrace opening and plain white window heads; material-only gray stone stair and arrival walking fronts; original stair elevations retained'
(D/'Prepared_Geometry.json').write_text(json.dumps({'source':'E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend','source_sha256':'202625cfe023a542ce75b7cbee3e05f0dee1767543a4ac7633b401d796e6c51a','objects':[row],'archive':[],'proof':proof,'material_only_riser_regions':risers,'lighting':'Preserve white paint; replace forest.exr tint with neutral studio.exr Material Preview'},ensure_ascii=False,indent=2),encoding='utf8')
print('PREPARED_V26_6',row['triangles'],row['closed_components'],'volume',house.volume(),'total_removed_m3',(before-house).volume(),'total_added_m3',(house-before).volume(),flush=True)
