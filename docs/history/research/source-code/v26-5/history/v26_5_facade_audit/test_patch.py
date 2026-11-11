from pathlib import Path
exec((Path(__file__).parent/'diagnose.py').read_text('utf8').split("out=[]")[0]+'out=[]')
from shapely.geometry import box,mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
p=json.loads((W/'v26_4/Exact_House_Parts.json').read_text('utf8'))
below=shape(next(r['outline']for r in p['layers']if r['z_m'][1]==3.32));above=shape(next(r['outline']for r in p['layers']if r['z_m'][0]==3.45))
mask=unary_union([box(-.3,1.9,.3,10.1),box(12.7,1.9,13.3,10.1),box(-.3,9.5,13.3,10.1)])
P=below.intersection(above).intersection(mask)
contours=[]
for q in [P]if P.geom_type=='Polygon'else list(P.geoms):
 q=orient(q,1);contours.append(np.array(q.exterior.coords)[:-1]);contours.extend(np.array(r.coords)[:-1]for r in q.interiors)
patch=mf.CrossSection(contours,mf.FillRule.NonZero).extrude(.132).translate([0,0,3.319]);fixed=m+patch
proof=[]
for axis,along in [(0,y)for y in np.arange(2.4,9.6,.2)]+[(1,x)for x in np.arange(.5,12.7,.2)]:
 p0=[12.5,along,3.4]if axis==0 else[along,9.3,3.4];p1=[13.5,along,3.4]if axis==0 else[along,10.3,3.4]
 before=[h.position for h in m.ray_cast(p0,p1)];after=[h.position for h in fixed.ray_cast(p0,p1)]
 proof.append(dict(axis=axis,along=float(along),before=before,after=after))
print('PATCH_AREA',P.area,'NEW_VOLUME',fixed.volume()-m.volume(),'COMPONENTS',len(fixed.decompose()),'STATUS',fixed.status())
print('FAILED_REAR_OR_EAST',sum(not any(abs(h[axis]-(13.1 if axis==0 else 9.9))<.001 for h in row['after'])for row in proof for axis in [row['axis']]))
mesh=patch.to_mesh64();np.savez_compressed(W/'v26_5_facade_audit/Exterior_Floor_Band_Join.npz',v=np.array(mesh.vert_properties[:,:3]),f=np.array(mesh.tri_verts,np.int32))
(W/'v26_5_facade_audit/Exterior_Floor_Band_Join.json').write_text(json.dumps({'method':'intersection of immediately below / above plans clipped to west east rear exterior bands','z_m':[3.319,3.451],'plan':mapping(P),'additional_volume_m3':fixed.volume()-m.volume(),'saved_source_shell':J['V26_3_House_Connected_Walls_And_Stairs']['file'],'rays':proof},indent=2),'utf8')

