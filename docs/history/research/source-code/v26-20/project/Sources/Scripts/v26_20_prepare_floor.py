"""Raise only the storage top volume; retain the shared kitchen/foundation shell."""
from v26_2_common import *
import v26_2_common as C
from v26_15_native_cleanup import repair_indexed
from shapely.geometry import Polygon,box,mapping
from shapely.geometry.polygon import orient
from scipy.spatial import cKDTree
D=W/'v26_20';P=D/'Prepared';P.mkdir(exist_ok=True);C.D=P
J=json.loads((D/'Input/Source_Index.json').read_text('utf8'));I={r['name']:r for r in J['objects']};n='V26_2_Continuous_Ground_And_Perimeter_Shell';r=I[n];a=np.load(D/'Input'/r['file']);old=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],n)
z0=float(np.float32(-.4));z1=float(np.float32(z0+.15));entry_x=float(np.float32(13.421809196472168));outline=Polygon(json.loads((W/'v24_10/AsBuilt_Plan.json').read_text('utf8'))['outline']);plan=orient(outline.intersection(box(entry_x,-30,30,10)),1)
# The kitchen east edge also places the single riser within the existing
# west entrance wall depth. The kitchen footprint is never filled or shifted.
pts=np.asarray(plan.exterior.coords,np.float32).astype(float)[:-1];slab=mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0]);sm=slab.to_mesh64();sv=np.asarray(sm.vert_properties[:,:3]);sf=np.asarray(sm.tri_verts);tt=sv[sf];no=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-30);mats=list(r['materials']);mi=np.full(len(sf),mats.index('M_V12_Road_Concrete'),np.int32);uv=uv_project(sv,sf)
# Continue the source foundation UV on matching outer planes. The new west
# entrance riser instead has a metric Y/Z cement projection; top is world X/Y.
ot=a['v'][a['f']];on=np.cross(ot[:,1]-ot[:,0],ot[:,2]-ot[:,0]);on/=np.maximum(np.linalg.norm(on,axis=1)[:,None],1e-30);ou=a['uv'];uva=abs(np.cross(ou[:,1]-ou[:,0],ou[:,2]-ou[:,0]));vertical=np.flatnonzero((abs(on[:,2])<.1)&(ot[:,:,2].min(1)<z0+.0001)&(np.ptp(ot[:,:,2],axis=1)>.03)&(uva>1e-8));tree=cKDTree(ot[vertical].mean(1));matches=[]
for k in np.flatnonzero(abs(no[:,2])<.1):
 c=tt[k].mean(0);_,near=tree.query(c,k=min(64,len(vertical)));ids=vertical[np.atleast_1d(near)];dist=abs((c-ot[ids,0])@no[k]);agree=on[ids]@no[k];valid=np.flatnonzero((dist<.00002)&(agree>.99999))
 if len(valid):
  ii=int(ids[valid[np.argmin(np.linalg.norm(ot[ids[valid]].mean(1)-c,axis=1))]]);uv[k]=bary_uv(tt[k:k+1],ot[ii:ii+1],a['uv'][ii:ii+1])[0];mi[k]=int(a['mi'][ii]);matches.append({'new_face':int(k),'source_triangle':ii,'material':mats[mi[k]]})
addition=tracked(sv,sf,mats,mi,uv,'Storage raised floor, single west entry riser and matching outer foundation texture');new=old+addition;row,new=export(n,new,'Raise storage room and gallery finished floor150mm within its footprint; kitchen, walls and original foundation held fixed')
aa=np.load(P/row['file']);v,f,mm,uu,cleanup=repair_indexed(aa['v'],aa['f'].astype(np.int64),aa['mi'],aa['uv']);nt=v[f];nn=np.cross(nt[:,1]-nt[:,0],nt[:,2]-nt[:,0]);nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-30)
from shapely.geometry import Point
boundary=np.array([plan.boundary.distance(Point(c[:2]))<.00002 for c in nt.mean(1)])
for k in np.flatnonzero(boundary&(abs(nn[:,2])<.1)&(nt[:,:,2].min(1)>=z0-.000001)&(nt[:,:,2].max(1)>z0+.001)&(nt[:,:,2].max(1)<=z1+.000002)):
 c=nt[k].mean(0);_,near=tree.query(c,k=min(128,len(vertical)));ids=vertical[np.atleast_1d(near)];dist=abs((c-ot[ids,0])@nn[k]);agree=on[ids]@nn[k];valid=np.flatnonzero((dist<.00002)&(agree>.99999))
 uu[k]=uv_project(v,f[k:k+1])[0];mm[k]=row['materials'].index('M_V12_Road_Concrete')
 if len(valid):
  ii=int(ids[valid[np.argmin(np.linalg.norm(ot[ids[valid]].mean(1)-c,axis=1))]]);uu[k]=bary_uv(nt[k:k+1],ot[ii:ii+1],a['uv'][ii:ii+1])[0];mm[k]=row['materials'].index(r['materials'][int(a['mi'][ii])])
top=(nn[:,2]>.99)&(abs(nt[:,:,2]-z1).max(1)<.000002)&np.array([plan.buffer(.00002).covers(Point(c[:2]))for c in nt.mean(1)]);uu[top]=nt[top,:,:2];mm[top]=row['materials'].index('M_V12_Road_Concrete')
# The original photo shader clamps its vertical image coordinate above the
# old stone-band top. On only the new extension, mirror that final photo strip
# continuously at the image edge to keep texture detail instead of stretching.
extended='M_V26_20_Storage_Foundation_Extended_Stone';row['materials'].append(extended);new_outer=boundary&(abs(nn[:,2])<.1)&(nt[:,:,2].min(1)>=z0-.000001)&(nt[:,:,2].max(1)>z0+.001)&(nt[:,:,2].max(1)<=z1+.000002)&(mm==row['materials'].index('M_V26_2_Continuous_Gallery_Base'));mm[new_outer]=len(row['materials'])-1
np.savez_compressed(P/row['file'],v=v,f=f,mi=mm,uv=uu);row.update(triangles=len(f),native_cleanup=cleanup)
proof={'outside_z_m':z0,'inside_z_m':z1,'rise_m':z1-z0,'entry_x_m':entry_x,'entry_clear_y_m':[-16.479,-15.24],'raise_plan_geometry':mapping(plan),'source_plan':'work/v24_10/AsBuilt_Plan.json','kitchen_east_protection_x_m':entry_x,'volume_addition_scope_z_m':[z0,z1],'new_volume_m3':new.volume()-old.volume(),'new_floor_area_m2':plan.area,'matching_foundation_uv_faces':matches,'top_uv':'World XY, same source scale and phase','riser_uv':'Metric world Y/Z at west entry; source barycentric UV on matching outer foundation planes','wall_movement_m':0,'kitchen_movement_m':0,'source_components':len(old.decompose()),'components':len(new.decompose())}
(D/'Prepared_Floor.json').write_text(json.dumps({'objects':[row],'proof':proof},ensure_ascii=False,indent=2),'utf8')
proof['new_stone_extension_material']={'name':extended,'source_group':'V26_2_Arc_Gallery_Stone_Photo','vertical_extension':'Continuous mirrored sampling past existing image edge; original world Z and arc U retained','triangles':int(new_outer.sum()),'original_material_graphs_modified':False}
doors=json.loads((D/'Prepared_Doors.json').read_text('utf8'));prepared={'source':J['model'],'source_sha256':J['sha256'],'objects':[row]+doors['objects'],'archive':[],'new_materials':[{'name':extended,'kind':'extend_stone_photo','source_group':'V26_2_Arc_Gallery_Stone_Photo'}],'proof':{'floor':proof,'doors':doors.get('proof',doors.get('doors',{})),'user_constraints':'Storage inside150mm above outside; walls and kitchen stay fixed'}};(D/'Prepared_Floor.json').write_text(json.dumps({'objects':[row],'proof':proof},ensure_ascii=False,indent=2),'utf8');(D/'Prepared.json').write_text(json.dumps(prepared,ensure_ascii=False,indent=2),'utf8');print('STORAGE_FLOOR_PREPARED',row['triangles'],proof['rise_m'],proof['new_floor_area_m2'],proof['components'],len(matches),flush=True)
