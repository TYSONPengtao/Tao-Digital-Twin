from v24_20_common import *
import hashlib
R=Path('E:/jz/JIA/Rebuild_V24_20/Reports');P=R.parent/'Blender/Architecture_Complete_V24_20.blend';ss=json.loads((D/'Solid_Export_Index.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());checks=[];stats=[];saved={};mesh_volumes={}
def ck(n,good,**kw):checks.append({'check':n,'pass':bool(good),**kw})
for r in ss['objects']:
 d=np.load(D/r['file']);t=d['v'][d['f']];mesh_volume=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);m=solid(d['v'],d['f'],r['name']);saved[r['name']]=m;mesh_volumes[r['name']]=mesh_volume;stats.append({'object':r['name'],'status':str(m.status()),'saved_signed_mesh_volume_m3':mesh_volume,'manifold_import_volume_m3':m.volume(),'closed_bodies':len(m.decompose())});ck('Saved closed positive-volume mesh / '+r['name'],m.status()==mf.Error.NoError and m.volume()>0)
for r in prep['objects']:
 a=mesh_volumes[r['name']];ck('Saved signed mesh volume matches prepared / '+r['name'],abs(a-r['volume_m3'])<max(2e-4,r['volume_m3']*1e-5),saved_m3=a,prepared_m3=r['volume_m3'])
for n in prep['proof']['perimeter_finish']['walls']:
 old=source(n);v=old['v'];now=saved[n];nv=np.array(now.to_mesh64().vert_properties[:,:3]);error=max(abs(nv.min(0)-v.min(0)).max(),abs(nv.max(0)-v.max(0)).max());ck('Closed wall restoration retains original bounds / '+n,error<3e-5,bounds_error_m=float(error))
n='SITE_KITCHEN_STONE_FLOOR_Geometry';now=saved[n];old=load(n);ck('Original kitchen floor retained in continuous repaired solid',(old-now).volume()<1e-5 and len(now.decompose())==1,lost_m3=(old-now).volume(),bodies=len(now.decompose()))
lipcut=now.slice(-.45).extrude(1).translate([0,0,-.40010]);n='SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry';toe=saved[n];oldtoe=load(n);ck('Interior foundation lip is flush below the kitchen floor',(toe^lipcut).volume()<1e-6,remaining_lip_m3=(toe^lipcut).volume());ck('Exterior and subfloor foundation retained after interior lip trim',((oldtoe-lipcut)-toe).volume()<1e-5,lost_outside_allowed_trim_m3=((oldtoe-lipcut)-toe).volume())
n='SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry';now=saved[n];nv=np.array(now.to_mesh64().vert_properties[:,:3]);ck('Refitted post feet keep the kitchen floor datum',abs(nv[:,2].min()+.4)<3e-5 and len(now.decompose())==4,minimum_z=float(nv[:,2].min()),connected_frame_bents=len(now.decompose()))
part=saved['PARTITIONS_JOINED_F1_Geometry'];room=cube([9.201,7.401,.01],[12.78,9.755,2.09])-part;ck('User blue partition forms two separate zones without rear bypass',len(room.decompose())==2 and room.volume()>15.5,clear_volume_m3=room.volume(),connected_components=len(room.decompose()))
for name in prep['proof']['roof_tiles']['kitchen']['objects']:
 roof=saved[name]
 for g in ['V24_Kitchen_Gable_Upper_Brick_Infill','V24_03_Kitchen_Rear_Gable_Wall']:
  overlap=(roof^saved[g]).volume();ck('Kitchen tile cover clears sealed gable / '+g,overlap<1e-5,overlap_m3=overlap)
for oldname,newname in [('SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE_Geometry','V24_20_Continuous_Graded_Road_Edge_0'),('SITE_V20_STORAGE_FRONT_GUTTER_AND_ROAD_SHOULDER_Geometry','V24_20_Continuous_Graded_Road_Edge_1')]:
 old=load(oldname);now=saved[newname];lost=(old-now).volume();ck('Road edge retains original support after channel fill / '+newname,lost<1e-4,lost_m3=lost,channel_fill_volume_m3=now.volume()-old.volume())
kt=union([saved[n]for n in prep['proof']['roof_tiles']['kitchen']['objects']]);st=saved['SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry'];overlap=(kt^st).volume();ck('Kitchen and storage tile fields meet without penetrating',overlap<1e-5,overlap_m3=overlap)
exclusion=cube([13.23,-12.5,2.24],[15,-9.08,6])
for n in ['SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry','SITE_KITCHEN_V12_LONGITUDINAL_ROUND_PURLINS_Geometry','SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry']:
 overlap=(saved[n]^exclusion).volume();ck('Refitted timber stays inside the junction masonry / '+n,overlap<1e-6,overlap_m3=overlap)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
ck('Geometry readback refers to current saved model',h==ss['model_sha256']);fail=[r for r in checks if not r['pass']];out={'status':'PASS_INDEPENDENT_GEOMETRY_QA'if not fail else'FAIL','model_sha256':h,'solids':stats,'checks':checks,'failures':fail};(R/'V24_20_Independent_Geometry_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('V20_SOLIDS_QA',len(stats),len(checks),'FAIL',len(fail),flush=True)
for r in fail:print('FAIL',r,flush=True)
