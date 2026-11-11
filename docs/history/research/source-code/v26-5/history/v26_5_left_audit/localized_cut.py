exec((__import__('pathlib').Path(__file__).parent/'probe.py').read_text('utf8').split('for n in [')[0])
name='BAY_WINDOW_F1_L_0_Geometry';a=np.load(D/I[name]['file']);v=a['v'];p=np.array([0.06934793293476105,1.9972580671310425]);q=np.array([0.6801928281784058,1.1500787734985352]);t=(q-p)/np.linalg.norm(q-p);n=np.array([-t[1],t[0]]);c=np.dot(p,n);allp=v[:,:2]@n
print('normal',n.tolist(),'glass_outer_c',c,'frame_outer_c',allp.min(),'frame_inner_c',allp.max(),'recommended_limit_c',allp.min()-.010,flush=True)
# Local room-side prism: x,y crossing bay pane and immediate host jamb.
from shapely.geometry import Polygon,box
limit=allp.min()-.010
poly=box(-.6,.7,1.,2.3)
# Intersect finite exterior tile endpoint neighbourhood with interior half-plane.
hp=Polygon([[(limit-n[1]*y)/n[0],y] for y in [.7,2.3]]+[[1.,2.3],[1.,.7]])
poly=poly.intersection(hp);cut=section(list(poly.exterior.coords)[:-1],1.).translate([0,0,1.8])
report=[]
for nm in list(I):
 if nm.startswith('SITE_COURTYARD_WEST_TILE_WALL_') or nm in ['SITE_WEST_TILE_WALL_PANEL_0_Geometry','V26_1_Courtyard_West_Wall_Single_Surface','V26_2_Continuous_Ground_And_Perimeter_Shell']:
  ar=np.load(D/I[nm]['file']);m=solid(ar['v'],ar['f'],nm);G=solid(v,a['f'],name);inter=m^G;removed=m^cut
  if not (inter.volume()>1e-12 or removed.volume()>1e-12):continue
  r={'name':nm,'original_glazing_intersection_m3':inter.volume(),'suggested_cut_removed_m3':removed.volume(),'postcut_glazing_intersection_m3':((m-cut)^G).volume()};report.append(r);print(r,flush=True)
(Path(__file__).parent/'localized_cut_report.json').write_text(json.dumps({'normal':n.tolist(),'frame_exterior_plane_constant':float(allp.min()),'cut_limit_constant':float(limit),'xy_polygon':list(poly.exterior.coords),'z_range':[1.8,2.8],'rows':report},indent=2),'utf8')
