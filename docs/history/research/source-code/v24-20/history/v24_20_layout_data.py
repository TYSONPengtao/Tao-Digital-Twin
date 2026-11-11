from v24_20_common import *
out={}
for n,z in [('SITE_KITCHEN_STONE_FLOOR_Geometry',-.45),('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry',1.),('PARTITIONS_JOINED_F1_Geometry',1.)]:
 ps=load(n).slice(z).to_polygons();out[n]=[p.tolist()for p in ps]
n='ROOF_MAIN_JOINED_Geometry';d=source(n);v=d['v'];f=d['f'];groups={}
for ids in f:
 t=v[ids];nn=np.cross(t[1]-t[0],t[2]-t[0]);nn/=np.linalg.norm(nn)
 if nn[2]<.2:continue
 key=tuple(np.round(np.r_[nn,nn@t[0]],4));groups.setdefault(str(key),[]).extend(t.tolist())
out['roof_planes']=groups
p=W/'v24_17';r=next(r for r in json.loads((p/'Inventory.json').read_text())if r['name']=='SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry');d=np.load(p/r['file']);m=solid(d['v'],d['f']);out['old_post_footprints']=[p.tolist()for p in m.slice(-.20).to_polygons()];out['old_stone_bounds']=[d['v'][np.unique(d['f'][d['mi']==1])].min(0).tolist(),d['v'][np.unique(d['f'][d['mi']==1])].max(0).tolist()]
(D/'Layout_Data.json').write_text(json.dumps(out,indent=2));print('ROOF',json.dumps(groups));print('old_bases',out['old_stone_bounds']);print('floor_polys',[(len(p),Polygon(p).bounds)for p in out['SITE_KITCHEN_STONE_FLOOR_Geometry']])
