from pathlib import Path
exec((Path(__file__).parent/'diagnose.py').read_text('utf8').split('out=[]')[0]+'out=[]')
from shapely.geometry import box,mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
mask=unary_union([box(-.3,1.9,.3,10.1),box(12.7,1.9,13.3,10.1),box(-.3,9.5,13.3,10.1)])
contours=[]
for q in [mask]if mask.geom_type=='Polygon'else list(mask.geoms):
 q=orient(q,1);contours.append(np.array(q.exterior.coords)[:-1]);contours.extend(np.array(r.coords)[:-1]for r in q.interiors)
maskcs=mf.CrossSection(contours,mf.FillRule.NonZero)
plan=(m.slice(3.319)^m.slice(3.451))^maskcs
patch=plan.extrude(.132).translate([0,0,3.319]);fixed=m+patch
proof=[]
for axis,along in [(0,y)for y in np.arange(2.4,9.6,.2)]+[(1,x)for x in np.arange(.5,12.7,.2)]+[(2,y)for y in np.arange(7.5,9.6,.2)]:
 if axis==0:p0=[12.5,along,3.4];p1=[13.5,along,3.4];ax=0
 elif axis==1:p0=[along,9.3,3.4];p1=[along,10.3,3.4];ax=1
 else:p0=[-.5,along,3.4];p1=[.5,along,3.4];ax=0
 before=[h.position for h in m.ray_cast(p0,p1)];after=[h.position for h in fixed.ray_cast(p0,p1)]
 expectedbefore=[h.position for h in m.ray_cast(np.array(p0)+[0,0,-.081],np.array(p1)+[0,0,-.081])];expectedabove=[h.position for h in m.ray_cast(np.array(p0)+[0,0,.051],np.array(p1)+[0,0,.051])]
 target=min(max(h[ax]for h in expectedabove),max(h[ax]for h in expectedbefore))if axis!=2 and expectedabove and expectedbefore else max(min(h[ax]for h in expectedabove),min(h[ax]for h in expectedbefore))if expectedabove and expectedbefore else None
 ok=target is None or any(abs(h[ax]-target)<.001 for h in after)
 proof.append(dict(axis=axis,along=float(along),before=before,after=after,target=target,pass_=ok))
print('PATCH_AREA',plan.area(),'NEW_VOLUME',fixed.volume()-m.volume(),'COMPONENTS',len(fixed.decompose()),'STATUS',fixed.status(),'FAIL',sum(not row['pass_']for row in proof))
for row in proof:
 if not row['pass_']:print('FAIL',row)
mesh=patch.to_mesh64();np.savez_compressed(W/'v26_5_facade_audit/Native_Exterior_Floor_Band_Join.npz',v=np.array(mesh.vert_properties[:,:3]),f=np.array(mesh.tri_verts,np.int32))
(W/'v26_5_facade_audit/Native_Exterior_Floor_Band_Join.json').write_text(json.dumps({'method':'intersect native shell slices at Z3.319 and3.451 clipped to west east rear exterior bands','z_m':[3.319,3.451],'contours':[p.tolist()for p in plan.to_polygons()],'additional_volume_m3':fixed.volume()-m.volume(),'rays':proof},indent=2),'utf8')
# sample each perimeter against entire vertical band with 1000mm rays.
summary=[]
for axis,p0,p1 in [(0,[-.5,8.5,3.4],[.5,8.5,3.4]),(0,[12.5,5,3.4],[13.5,5,3.4]),(1,[5,9.3,3.4],[5,10.3,3.4]),(1,[11.8,9.3,3.4],[11.8,10.3,3.4])]:
 hs=fixed.ray_cast(p0,p1);summary.append({'axis':axis,'hit_positions':[h.position for h in hs]})
print(json.dumps(summary,indent=1))

