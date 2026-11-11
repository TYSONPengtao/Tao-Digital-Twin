from v24_20_common import *
from collections import Counter
result={}
for n in ['SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry','SITE_KITCHEN_STONE_FLOOR_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','PARTITIONS_JOINED_F1_Geometry','SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE_Geometry','SITE_V20_STORAGE_FRONT_GUTTER_AND_ROAD_SHOULDER_Geometry']:
 m=load(n);dd=[]
 for c in m.decompose():
  if c.volume()<1e-7:continue
  v=np.array(c.to_mesh64().vert_properties[:,:3]);dd.append({'lo':v.min(0).tolist(),'hi':v.max(0).tolist(),'volume':c.volume(),'vertices':len(v)})
 result[n]=dd
 if 'TIMBER' in n:
  result['post_sections']=m.slice(1.8001).to_polygons()
  result['post_sections']=[a.tolist()for a in result['post_sections']]
for ver in ['v24_17','v24_16']:
 p=W/ver/'Inventory.json';idx={r['name']:r for r in json.loads(p.read_text())}
 n='SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry'
 if n in idx and idx[n].get('file'):
  d=np.load(p.parent/idx[n]['file']);v=d['v'];result['old_'+ver]={'row':idx[n],'keys':list(d.keys()),'bounds':[v.min(0).tolist(),v.max(0).tolist()]}
  np.savez_compressed(D/('Old_Timber_'+ver+'.npz'),v=v,f=d['f'])
for n in [f'SITE_PERIMETER_JOINED_RETAINING_WALL_{i}_Geometry'for i in range(2)]:
 d=source(n);v=d['v'];f=d['f'];t=v[f];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2
 areas={str(i):float(area[d['mi']==i].sum())for i in set(d['mi'])}
 # Existing metre/image scale on triangles whose UV and physical edges are regular.
 q=[]
 for p,uv in zip(t[d['mi']==2],d['uv'][d['mi']==2]):
  for a,b in [(0,1),(1,2),(2,0)]:
   e=p[b]-p[a];du=uv[b]-uv[a]
   if abs(e[2])>.03 and np.linalg.norm(e[:2])<1e-4:q.append(abs(du[1]/e[2]))
 result[n]={'areas':areas,'uv_v_per_m':np.quantile(q,[0,.5,1]).tolist()if q else[],'z_levels':Counter(np.round(v[:,2],4)).most_common(16)}
(D/'Diagnostics.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
