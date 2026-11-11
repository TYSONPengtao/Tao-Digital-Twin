"""Four local geometry repairs from saved V26.14; keep provenance and source immutable."""
from v26_2_common import *
import v26_2_common as C
from v26_8_native_cleanup import repair_native
from v26_15_native_cleanup import repair_indexed
import hashlib
D=W/'v26_15';I=D/'Input';P=D/'Prepared';P.mkdir(exist_ok=True);C.D=P
J=json.loads((I/'Source_Index.json').read_text('utf8'));ix={r['name']:r for r in J['objects']};loaded={}
SRC=Path(J['model']);assert hashlib.sha256(SRC.read_bytes()).hexdigest()==J['sha256']
HN='V26_3_House_Connected_Walls_And_Stairs';GN='V26_2_Continuous_Ground_And_Perimeter_Shell';TN='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry';CN='V26_7_Inner_Gate_Rear_Return_Closure';SN='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'
def get(n):
 if n not in loaded:
  r=ix[n];a=np.load(I/r['file']);loaded[n]=(r,a,tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],n))
 return loaded[n]
def box(lo,hi):return cube(np.asarray(lo,np.float32).astype(float),np.asarray(hi,np.float32).astype(float))
hr,ha,h0=get(HN);gr,ga,g0=get(GN);_,_,s=get(SN)
proof={'source':str(SRC),'source_sha256':J['sha256'],'dimensions':'Existing native planes and supplied reference relationships; not newly surveyed field dimensions','repairs':[]}
# Transfer a bounded ground patch into the house owner before union. The
# combined envelope stays identical, and the competing visible porch faces
# become one Boolean surface; shared patch interfaces remain below the floor.
roi=box([3.4,-.5,-.75],[9.6,2.35,-.30]);pieces=g0.decompose();lipcut=box([3.4,-.3001,-.600000024],[9.6,-.2199999988079071,-.30]);trimmed=[];lip_removed=0.
for p in pieces:
 bb=np.asarray(p.bounding_box())
 if abs(bb[0]-3.75)<1e-5 and abs(bb[1]+.3)<1e-5 and abs(bb[3]-9.25)<1e-5:
  lip_removed+=(p^lipcut).volume();p-=finish(lipcut,'M_Wall_Exterior','Trim only old porch raised front lip to the existing four-sided platform boundary')
 trimmed.append(p)
assert .065<lip_removed<.067,lip_removed
gbase=mf.Manifold.compose(trimmed);patch=gbase^roi;h=h0+patch;g=gbase-roi
# Coplanar Boolean faces can inherit alternating old paving materials even
# after the duplicate geometry is gone. Replace the existing ten-millimetre
# top volume with itself using the porch stone finish and original floor UV.
# This is part of the same solid, at the same top level, not an overlay.
caplo=[float(np.float32(3.68)),float(np.float32(-.22)),float(np.float32(-.46))];caphi=[float(np.float32(9.32)),float(np.float32(2.22)),float(np.float32(-.45))];cap=box(caplo,caphi);capmesh=cap.to_mesh64();cv=np.asarray(capmesh.vert_properties[:,:3]);cf=np.asarray(capmesh.tri_verts);cn=np.cross(cv[cf][:,1]-cv[cf][:,0],cv[cf][:,2]-cv[cf][:,0]);cuv=uv_project(cv,cf);ctop=cn[:,2]>0;oldtr=ha['v'][ha['f']];oldno=np.cross(oldtr[:,1]-oldtr[:,0],oldtr[:,2]-oldtr[:,0]);olds=(oldno[:,2]>1e-10)&(abs(oldtr[:,:,2].mean(1)+.45)<1e-6)&(ha['mi']==hr['materials'].index('M_Floor'));_,cuv[ctop]=remap({'v':ha['v'],'f':ha['f'][olds],'mi':ha['mi'][olds],'uv':ha['uv'][olds]},cv,cf[ctop]);capmats=['M_Floor','M_Wall_Exterior'];cmi=np.ones(len(cf),int);cmi[ctop]=0;capfinish=tracked(cv,cf,capmats,cmi,cuv,'Existing rectangular porch top assigned continuous native stone finish');h=(h-cap)+capfinish
old_combined=(h0^roi)+(g0^roi);trimmed_combined=(h0^roi)+(gbase^roi);new_combined=(h^roi)+(g^roi)
pr={'issue':'Porch edge striped z fighting','cause':'V26.11 rectangular porch was added over the inherited ground porch. Two separate owners retained coincident and intersecting finish faces. The old porch front lip also extended80mm past the new four-sided boundary.','method':'Trim only the old porch component lip above the court level, retain underlying court/lane; union transferred finite ground patch into house and remove it from ground. No plane offsets or overlay skins.','scope_m':[[3.4,-.5,-.75],[9.6,2.35,-.30]],'overlap_before_m3':(h0^g0^roi).volume(),'overlap_after_m3':(h^g^roi).volume(),'combined_envelope_added_m3':(new_combined-old_combined).volume(),'combined_envelope_removed_m3':(old_combined-new_combined).volume(),'old_lip_component_removed_m3':lip_removed,'old_lip_scope_m':[[3.4,-.3001,-.600000024],[9.6,-.2199999988079071,-.30]],'ownership_union_envelope_error_m3':max(abs((new_combined-trimmed_combined).volume()),abs((trimmed_combined-new_combined).volume()))}
assert abs(pr['overlap_after_m3'])<1e-8 and abs(pr['combined_envelope_added_m3'])<1e-8 and .04<pr['combined_envelope_removed_m3']<.067 and pr['ownership_union_envelope_error_m3']<1e-8,pr
pr['continuous_top_finish']='Existing10mm top volume replaced at exactly the same level and footprint, using original M_Floor UV; no superposed skin';proof['repairs'].append(pr);print('PORCH_FIXED',pr,flush=True)
# Only the two 190 x190 x130mm slab-seal protrusions at the west/front
# stair corner are removed. The bearing that is inside the wall is retained.
staircutters=[];removed=[]
for z0,z1 in [(3.319999933242798,3.450000047683716),(6.920000076293945,7.050000190734863)]:
 c=box([4.019999980926514,7.420000076293945,z0],[4.210001,7.610001,z1]);delta=h^c;removed.append({'bounds_m':[[4.019999980926514,7.420000076293945,z0],[4.210001,7.610001,z1]],'removed_m3':delta.volume()});staircutters.append(c);h-=finish(c,'M_Wall_Interior','Trim stair-side slab-seal tongues to existing X4.02 Y7.42 finish planes')
assert all(.0046<q['removed_m3']<.0048 for q in removed),removed
proof['repairs'].append({'issue':'Stair wall isolated cube / uneven corner','cause':'Earlier slab slit repair extended its rectangular seal beyond both existing finished stair wall planes. Two130mm slab-edge tongues projected190mm into the stair room.','method':'Subtract only the exposed two tongues, retaining the buried slab support and native wall faces.','cuts':removed,'finish_planes_m':{'x':4.019999980926514,'y':7.420000076293945}})
# The closure stopped at Y-11.382, but the actual kitchen return finishes at
# Y-11.62. Fill that recess as finite support, bonded into the actual ground.
# Replace the old closure (not a second overlay on it).
piers=get('V26_10_Inner_Gate_Rectangular_Stone_Piers')[2];step=get('SITE_V21_GATE_REFERENCE_LAYER_01_Geometry')[2]
floor_z=float(np.float32(-.4000244140625));floor_scope=box([8.02856,-11.64,-.75],[9.50,-11.0999,floor_z]);fill=floor_scope-s-piers-step
g+=finish(fill,'M_Floor','Gate rear return reaches actual wall at existing porch datum; solid support not overlay')
oldclosure=get(CN)[2];newadd=(g-(gbase-roi))
proof['repairs'].append({'issue':'Gate rear wall-side sunken trench','cause':'Old finite closure stopped atY-11.382 while the wall face isY-11.619999886, leaving a237.9999mm unfilled strip.','method':'Replace closure with a finite ground extension to the real wall, cut around retained masonry, stone jambs and threshold, and union into ground owner.','old_closure_y_min_m':float(np.min(get(CN)[1]['v'][:,1])),'actual_wall_y_m':-11.619999885559082,'nominal_extension_m':-11.382-(-11.619999885559082),'floor_z_m':floor_z,'scope_m':[[8.02856,-11.64,-.75],[9.5,-11.0999,floor_z]],'new_ground_added_m3':newadd.volume(),'old_closure_archived':CN,'separate_overlay_added':False})
rows=[]
for name,m,why in [(HN,h,'Single porch surface owner and trimmed stair wall seal tongues'),(GN,g,'Transferred porch patch removed; gate rear floor extended flush to wall as bonded support')]:
 m=clean(m).simplify(.0000001)
 r,m=export(name,m,why);a=np.load(P/r['file']);v,f,mi,uv=a['v'],a['f'],a['mi'],a['uv'];tt=v[f];ar=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)/2;ed=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,ct=np.unique(ed,axis=0,return_counts=True)
 if not np.all(ct==2) or ar.min()<=1e-18:v,f,mi,uv,r['native_cleanup']=repair_indexed(v,f,mi,uv)
 f=f.astype(np.int64);np.savez_compressed(P/r['file'],v=v,f=f,mi=mi,uv=uv);m=solid(v,f);r.update(triangles=len(f),closed_components=len(m.decompose()),volume_m3=m.volume());expected=1 if name==HN else len(g0.decompose());assert r['closed_components']==expected and all(q.volume()>0 for q in m.decompose()),(name,r['closed_components'],expected);rows.append(r)
# Directly delete the positively identified disconnected six-triangle remnant.
# Every retained timber triangle, UV, material, and coordinate stays exact.
tr,ta,_=get(TN);v=ta['v'];f=ta['f'];vghost=(v[:,0]>16.219)&(v[:,0]<16.254)&(v[:,1]>-14.402)&(v[:,1]<-14.356)&(v[:,2]>-.392)&(v[:,2]<1.744);bad=np.all(vghost[f],axis=1);assert int(vghost.sum())==5 and int(bad.sum())==6
ids,reverse=np.unique(f[~bad].ravel(),return_inverse=True);fn=TN+'.npz';np.savez_compressed(P/fn,v=v[ids],f=reverse.reshape(-1,3).astype(np.int64),mi=ta['mi'][~bad],uv=ta['uv'][~bad]);rows.append({'name':TN,'file':fn,'materials':tr['materials'],'triangles':int((~bad).sum()),'reason':'Remove the isolated old timber sliver from the open storage doorway; all retained triangles attributes exact'})
proof['repairs'].append({'issue':'Storage floating shadow / suspended timber strip','cause':'A fixed detached five-vertex six-triangle timber fragment remained in the doorway independently of both animated leaves. Its bottom was8.37mm above the finished floor.','method':'Remove exactly the detached remnant, no global component cleanup.','removed_triangles':6,'removed_vertices':5,'bounds_m':[v[vghost].min(0).tolist(),v[vghost].max(0).tolist()],'retained_triangles_and_attributes_exact':True})
prep={'source':str(SRC),'source_sha256':J['sha256'],'objects':rows,'archive':[CN],'proof':proof};(D/'Prepared.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2),'utf8');print('PREPARED',[(r['name'],r['triangles'])for r in rows],flush=True)
