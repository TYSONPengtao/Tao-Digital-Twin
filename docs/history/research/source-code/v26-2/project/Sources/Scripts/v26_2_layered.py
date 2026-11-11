from v26_2_common import *
from shapely.geometry import Polygon,box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import shapely,re
G=.0001;PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))};oldprep=json.loads((D/'Prepared_House.json').read_text('utf8'))
S=json.loads(Path('E:/jz/JIA/Rebuild_V20/08_Editable_Source/Architecture_Scene_V20.json').read_text('utf8'));E={e['name']:e for e in S['elements']};parts=[];extra=[];coreproof=[]
def snap(p):return shapely.set_precision(p.buffer(0),G)
def add(poly,z0,z1,kind,name):
 if not poly.is_empty and z1>z0:parts.append({'poly':snap(poly),'z0':round(z0,4),'z1':round(z1,4),'kind':kind,'name':name})
for fl in [1,2,3]:
 for kind in ['FACADE_CONTINUOUS','PARTITIONS_JOINED']:
  name=kind+'_F'+str(fl)
  for pp in E[name]['parts']:
   g=pp['geometry']
   if g['type']=='prism_holes':poly=Polygon(g['outer'],g.get('holes',[]));z=g['z']-.45;h=g['height']
   else:x,y,z=g['origin'];w,d,h=g['size'];poly=box(x,y,x+w,y+d);z-=.45
   add(poly,z,z+h,'wall',name)
names=json.loads((PD/'Prepared_House.json').read_text('utf8'))['archive']
for n in names:
 if n.startswith(('FACADE_CONTINUOUS','PARTITIONS_JOINED','V24_31_F'))or n=='HOUSE_V22_FRONT_BAY_TILE_FACES_Geometry'or(n.startswith('HOUSE_V21_')and'GREY_WHITE'in n):continue
 a=np.load(PD/PI[n]['file']);v=a['v'];f=a['f'];t=v[f];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);vol=abs(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);lo=v.min(0);hi=v.max(0);top=abs(nn[:,2])>np.linalg.norm(nn,axis=1)*.99999;poly=unary_union([Polygon(tr[:,:2])for tr in t[top]]).buffer(0)if top.any()else Polygon();prismvol=poly.area*(hi[2]-lo[2])
 if not poly.is_empty and (abs(prismvol-vol)<max(.0001,vol*.001)or n.startswith('SLAB_JOINED'))and not n.startswith(('STAIR_F','ROOF_')):
  add(poly,lo[2],hi[2],'core',n)
 else:
  fn='EXACT_EXTRA_'+str(len(extra))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=a['mi'],uv=a['uv']);extra.append({'name':n,'file':fn,'materials':PI[n]['materials']})
 coreproof.append({'name':n,'bounds_m':[lo.tolist(),hi.tolist()],'source_volume_m3':vol,'source_dimensions_retained_to_m':G})
floors=[-.45,3.45,7.05];ceilings=[3.32,6.92,10.22]
levels=sorted(set([p[k]for p in parts for k in ['z0','z1']]+[z for f,c in zip(floors,ceilings)for z in [f-.2,f,f+.6,f+2.1,c]]+[1.3167,5.0804]+[round(x,4)for n,r in I.items()if n.startswith(('WINDOW_LEFT_','WINDOW_RIGHT_','WINDOW_BACK_','WINDOW_FRONT_CENTER_F3'))for x in [r['bounds'][0][2],r['bounds'][1][2]]]))
targets=[('west_inside',0,1,.212,.099,.2119,-.45,10.22),('left_room_partition',0,-1,3.688,3.6881,3.801,-.45,6.92),('middle_west_partition',0,1,4.112,3.999,4.1119,-.45,10.22),('middle_east_partition',0,-1,8.888,8.8881,9.001,-.45,10.22),('right_room_partition',0,1,9.312,9.199,9.3119,-.45,10.22),('east_inside',0,-1,12.788,12.7881,12.901,-.45,10.22),('front_inside',1,1,2.312,2.199,2.3119,-.45,10.22),('rear_partition_front',1,-1,7.088,7.0881,7.201,-.45,10.22),('rear_partition_back',1,1,7.512,7.399,7.5119,-.45,10.22),('rear_inside',1,-1,9.588,9.5881,9.701,-.45,10.22),('terrace_wall',0,-1,3.680,3.681,3.801,7.05,10.22)]
layers=[]
for z0,z1 in zip(levels,levels[1:]):
 if z1-z0<.00009:continue
 z=(z0+z1)/2;wall=unary_union([p['poly']for p in parts if p['kind']=='wall'and p['z0']<z<p['z1']]);cores=[]
 for p in parts:
  if p['kind']!='core'or not p['z0']<z<p['z1']:continue
  q=p['poly']
  if p['name'].startswith('V26_Stair_Landing_Bearing_Beam_')and z>(1.3167 if p['name'].endswith('1')else 5.0804):q=q.difference(box(5.1999,8.54,5.31,9.83))
  cores.append(q)
 for fl,floor,ceiling in zip([1,2,3],floors,ceilings):
  if not floor<=z<ceiling:continue
  wall=wall.difference(box(4.112,7.512,8.888,9.7))
  if fl==1:
   wall=wall.difference(box(9.2,8.345,10.90,8.655)).difference(box(10.59,7.395,10.90,9.825)).union(box(10.6,7.395,10.7,9.825));left=box(9.,7.4,9.2,9.7)
   if z<floor+2.1:left=left.difference(box(8.9,8.6,9.3,9.4))
   wall=wall.union(left)
  if fl<3:wall=wall.union(box(4.112,7.2,7.8,7.4))
  if z<floor+2.1:
   if fl==1:wall=wall.union(box(11.9,7.2,12.7,7.4)).difference(box(10.7,7.05,11.5,7.55))
   if fl==3:wall=wall.union(box(9.,7.55,9.2,8.45)).difference(box(8.85,6.15,9.35,7.05))
  wall=wall.union(box(4.112,9.7,7.7,9.9))
  for n,r in I.items():
   if not n.startswith(('WINDOW_LEFT_','WINDOW_RIGHT_','WINDOW_BACK_','WINDOW_FRONT_CENTER_F3'))or f'_F{fl}'not in n:continue
   a,b=r['bounds']
   if n.startswith('WINDOW_LEFT_'):panel=box(-.1,a[1],.1,b[1])
   elif n.startswith('WINDOW_RIGHT_'):panel=box(12.9,a[1],13.1,b[1])
   elif n.startswith('WINDOW_BACK_'):panel=box(a[0],9.588,b[0],9.9)
   else:panel=box(a[0],2.0,b[0],2.2)
   wall=wall.difference(panel)if a[2]<z<b[2]else wall.union(panel)
 P=snap(unary_union([wall]+cores));base=P;fills=[]
 if P.is_empty:continue
 for label,ax,sgn,end,low,high,zlo,zhi in targets:
  if not zlo<=z<=zhi:continue
  extent=(1.884,10.016)if ax==0 else(-.216,13.216);band=box(low,extent[0],high,extent[1])if ax==0 else box(extent[0],low,extent[1],high);cut=base.intersection(band)
  for q in [cut]if cut.geom_type=='Polygon'else getattr(cut,'geoms',[]):
   if q.geom_type!='Polygon'or q.area<1e-9:continue
   b=q.bounds;u0,u1=(b[1],b[3])if ax==0 else(b[0],b[2]);a0,a1=(end,high)if sgn<0 else(low,end);fills.append(box(a0,u0,a1,u1)if ax==0 else box(u0,a0,u1,a1))
 P=snap(unary_union([P]+fills).buffer(.0002,join_style=2));cont=[]
 for q in [P]if P.geom_type=='Polygon'else getattr(P,'geoms',[]):
  if q.geom_type!='Polygon'or q.area<1e-9:continue
  q=orient(q,1);cont.append(np.array(q.exterior.coords)[:-1]);cont.extend(np.array(r.coords)[:-1]for r in q.interiors)
 m=mf.CrossSection(cont,mf.FillRule.NonZero).extrude(z1-z0+.00005).translate([0,0,z0-.00005]);a=m.to_mesh64();fn='EXACT_LAYER_'+str(len(layers))+'.npz';v=np.array(a.vert_properties[:,:3]);f=np.array(a.tri_verts);np.savez_compressed(D/fn,v=v,f=f,uv=uv_project(v,f),mi=np.zeros(len(f),np.int32));layers.append({'file':fn,'name':'V26_2_Analytic_Height_Layer_'+str(len(layers)),'z_m':[z0,z1],'area_m2':P.area,'outline':P.__geo_interface__,'materials':['M_Wall_Interior']});print('LAYER',len(layers),z0,z1,P.area,len(f),flush=True)
out={'layers':layers,'extras':extra,'frames':oldprep['objects'][1:],'proof':{'analytic_layer_topology':True,'canonical_grid_m':G,'internal_vertical_join_overlap_m':.00005,'source_wall_plans':'E:/jz/JIA/Rebuild_V20/08_Editable_Source/Architecture_Scene_V20.json','latest_door_and_window_openings_registered':True,'retained_core_components':coreproof,'finished_wall_profiles':[{'wall':a,'axis':b,'normal_sign':c,'plane_m':d,'z_m':[g,h]}for a,b,c,d,e,f,g,h in targets],'frames':oldprep['proof']['frames'],'actual_window_opaque_zones':oldprep['proof']['actual_window_opaque_zones'],'raised_first_floor_right_glazed_door_corrected_m':-.45,'protected_third_floor_guard_opening':True}}
(D/'Exact_House_Parts.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('EXACT_PARTS_READY',len(layers),len(extra),flush=True)
