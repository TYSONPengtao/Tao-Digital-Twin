"""Replace only the protruding slab tongues, retain tread heights and restore white fascia."""
from v26_2_common import *
import v26_2_common as C
from v26_15_native_cleanup import repair_indexed
D=W/'v26_18';P=D/'Prepared';P.mkdir(exist_ok=True);C.D=P
J=json.loads((D/'Input/Source_Index.json').read_text('utf8'));ix={r['name']:r for r in J['objects']};HN='V26_3_House_Connected_Walls_And_Stairs';r=ix[HN];a=np.load(D/'Input'/r['file']);h=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],HN);h0=h
OI={r['name']:r for r in json.loads((W/'v26/Geometry_Index.json').read_text('utf8'))};scopes=[];joins=[]
white='M_V26_3_Neutral_White_Interior_Ceiling'
def box(a,b):return cube(np.asarray(a,np.float32).astype(float),np.asarray(b,np.float32).astype(float))
def down_line(name):
 b=np.load(W/'v26'/OI[name]['file']);t=b['v'][b['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ar=np.linalg.norm(no,axis=1)/2;no/=np.maximum(2*ar[:,None],1e-30);ok=(no[:,2]<-.5)&(abs(no[:,1])<.001)&(abs(no[:,0])>.1);ids=np.flatnonzero(ok);i=ids[np.argmax(ar[ids])];slope=-no[i,0]/no[i,2];intercept=t[i,0,2]-slope*t[i,0,0];return float(slope),float(intercept)
def along_y(profile,y0,y1):return section(np.asarray(profile,np.float32).astype(float).tolist(),y1-y0).rotate([90,0,0]).translate([0,y1,0])
for fl,zs in [(1,float(np.float32(3.32))),(2,float(np.float32(6.92)))]:
 slope,b=down_line(f'STAIR_F{fl}_FLIGHT2_Geometry');cross=float(np.float32((zs-b)/slope));xa=float(np.float32(7.8));xb=float(np.float32(8.98));y0=float(np.float32(7.28));ym=float(np.float32(8.5));yn=float(np.float32(8.6));y1=float(np.float32(9.68));zl=float(np.float32(zs-.38));zc=float(np.float32(zs+.05))
 south_scope=box([xa,y0,zl],[xb,ym,zc]);profile=[[xa,slope*xa+b],[cross,zs],[xb,zs],[xb,zc],[xa,zc]];south=along_y(profile,y0,ym)
 middle_scope=box([xa,ym,zl],[xb,yn,zc]);middle=box([xa,ym,zs],[xb,yn,zc])
 nx=xa;nprofile=None
 if fl==1:
  ns,nb=down_line('STAIR_F2_FLIGHT1_Geometry');nx=float(np.float32(7.70));nc=float(np.float32((zs-nb)/ns));nprofile=[[nx,ns*nx+nb],[nc,zs],[xb,zs],[xb,zc],[nx,zc]]
 north_scope=box([nx,yn,zl],[xb,y1,zc]);north=along_y(nprofile,yn,y1)if nprofile else box([nx,yn,zs],[xb,y1,zc]);roi=union([south_scope,middle_scope,north_scope]);desired=union([south,middle,north]);old=h
 h=(h-finish(roi,white,'Remove the legacy underside tongue in the finite stair/slab joint'))+finish(desired,white,'Continuous planar white stair waist joining the original flat slab soffit')
 scopes.append(roi);pr={'floor_from':fl,'floor_to':fl+1,'slab_soffit_z_m':zs,'upper_cut_z_m':zc,'upper_flight_original_soffit_line':[slope,b],'soffit_meets_slab_at_x_m':cross,'north_flat_start_x_m':nx,'scope_m':[[min(xa,nx),y0,zl],[xb,y1,zc]],'old_tongue_soffit_z_m':float(np.float32(OI[f'SLAB_JOINED_F{fl+1}_Geometry']['bounds'][0][2]-.065)),'removed_m3':(old-h).volume(),'added_m3':(h-old).volume(),'reason':'Earlier end tongue extended65mm below the slab; original slab planes also differed by several micrometres. Replace the finite underside body, preserving the walking surfaces above.'};joins.append(pr);print('JOIN_REPAIRED',pr,flush=True)
scope=union(scopes);outside_removed=((h0-h)-scope).volume();outside_added=((h-h0)-scope).volume();assert max(abs(outside_removed),abs(outside_added))<1e-5,(outside_removed,outside_added)
# Partition an existing2mm-deep volume at the last walking riser so that its
# stone finish cannot be absorbed by a larger coplanar white fascia triangle.
# The physical envelope is identical; no finish skin is added.
for z0,z1 in[(1.3600585460662842,1.4999511241912842),(5.110058784484863,5.249951362609863)]:
 cap=box([5.198,8.6,z0],[5.200002,9.68,z1]);existing=h^cap;h=(h-cap)+finish(existing,'M_V24_31_Stair_Gray_Marble','Retain the actual final walking riser in stone, with an explicit finish boundary')
row,hm=export(HN,h,'Remove stair/slab underside tongue offsets and restore white half-landing fascia');aa=np.load(P/row['file']);v,f,mi,uv=aa['v'],aa['f'],aa['mi'],aa['uv'];v,f,mi,uv,cleanup=repair_indexed(v,f.astype(np.int64),mi,uv);tt=v[f];no=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);ar=np.linalg.norm(no,axis=1)/2;no/=np.maximum(2*ar[:,None],1e-30);fascias=[]
for fl,lo,hi in [(1,1.0800585746765137,1.4999511241912842),(2,4.830058574676514,5.249951362609863)]:
 riser_bottom=1.3600585460662842 if fl==1 else 5.110058784484863
 tread_riser=(no[:,0]>.999)&(tt[:,:,1].min(1)>=8.59999)&(tt[:,:,2].min(1)>=riser_bottom-.00002)
 select=(mi==row['materials'].index('M_V24_31_Stair_Gray_Marble'))&(abs(no[:,2])<.001)&(tt[:,:,0].min(1)>=5.02999)&(tt[:,:,0].max(1)<=5.20001)&(tt[:,:,1].min(1)>=7.41999)&(tt[:,:,1].max(1)<=9.68001)&(tt[:,:,2].min(1)>=lo-.00002)&(tt[:,:,2].max(1)<=hi+.00002)&~tread_riser
 assert select.sum()>10,(fl,'Landing fascia was not identified')
 fascias.append({'floor':fl,'faces':int(select.sum()),'area_m2':float(ar[select].sum()),'height_interval_m':[lo,hi],'before_material':'M_V24_31_Stair_Gray_Marble','after_material':'M_Wall_Interior','tread_risers_excluded':True});mi[select]=row['materials'].index('M_Wall_Interior')
bad_uv=~np.isfinite(uv).all((1,2))|(abs(uv).max((1,2))>1e5)
if bad_uv.any():uv[bad_uv]=uv_project(v[f[bad_uv]].reshape(-1,3),np.arange(bad_uv.sum()*3).reshape(-1,3))
np.savez_compressed(P/row['file'],v=v,f=f.astype(np.int64),mi=mi,uv=uv);m=solid(v,f);assert len(m.decompose())==1 and m.volume()>0
row.update(triangles=len(f),volume_m3=m.volume(),closed_components=1,native_cleanup=cleanup,invalid_uv_faces_reprojected=int(bad_uv.sum()))
proof={'joins':joins,'fascias':fascias,'outside_scope_removed_m3':outside_removed,'outside_scope_added_m3':outside_added,'scope_prisms':[{'bounds':q['scope_m'],'north_flat_start_x_m':q['north_flat_start_x_m']}for q in joins],'rear_gate_removed':'GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS_Geometry','source_user_blender_window_untouched':True,'tread_and_floor_datums_retained':True,'no_overlay_finish_skins':True}
prep={'source':J['model'],'source_sha256':J['sha256'],'objects':[row],'archive':['GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS_Geometry'],'proof':proof};(D/'Prepared.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2),'utf8');print('PREPARED',len(f),fascias,flush=True)
