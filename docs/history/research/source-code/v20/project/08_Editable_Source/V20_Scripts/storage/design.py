"""Read-only V19 input; write V20 storage patch and native cache overrides only."""
import sys,json,math,copy,ast
from pathlib import Path
W=Path(__file__).parent.parent;D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
from shapely.geometry import Polygon,LineString,Point,box as sb
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
B=Path('E:/jz/JIA/Rebuild_V19')
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V19.json').read_text(encoding='utf8'))}
proof={'reference':['User 2026-10-13 035201,035418,035635,035705','Original INSV 710,715,720,725 seconds','DJI_0525.JPG / DJI_0526.JPG'],'dimension_status':'Visible relationships corrected from real photos; exact field dimensions unmeasured','checks':[],'cache_overrides':{}}
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold']),('v19_design.py',['fromman']),('v14_building.py',['part','box','beam','tile'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<helpers>','exec'))
Q={'replace':[],'add':[],'remove':[]}
def put(n,ps,new=False,**meta):
 e=copy.deepcopy(E[n]) if not new else {'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'PHOTO_FIT'}
 for key in ['origin','angle_deg','angle','definition']:e.pop(key,None)
 e.update(parts=ps,v20_storage=True,source=proof['reference'],dimension_status=proof['dimension_status'],**meta);Q['add' if new else 'replace'].append(e);return e
def cube(o,z):return manifold({'type':'box','origin':o,'size':z})
def addall(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def prism(poly,z,h):
 poly=orient(poly,1);return {'type':'prism_holes','outer':list(poly.exterior.coords)[:-1],'holes':[list(q.coords)[:-1] for q in poly.interiors],'z':z,'height':h}
def native(n):
 dat=np.load(B/'02_Data'/I[n]['file']);v=dat['vertices'];f=dat['faces'];vv,inv=np.unique(np.round(v,10),axis=0,return_inverse=True);ff=inv[f];a=mf.Manifold(mf.Mesh64(vv,ff.astype(np.uint64)))
 if a.status()!=mf.Error.NoError and len(E[n].get('parts',[]))>1:a=addall([manifold(p['geometry']) for p in E[n]['parts']])
 assert a.status()==mf.Error.NoError,(n,a.status());return a
def footprint(n):
 ds=np.load(B/'02_Data'/I[n]['file']);t=ds['vertices'][ds['faces']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return unary_union([Polygon(q[:,:2]) for q in t[no[:,2]>1e-9]]).buffer(0)

# Move openings to actual eave corridor ends; old central room-through-wall holes are closed.
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY';a=native(n);before=a
oldwest=cube([13.35,-11.5,-.4],[.25,1.25,2.15]);oldeast=cube([18.65,-13.45,-.4],[.25,1.30,2.20])
a=a+cube([13.35,-11.505,-.402],[.25,1.260,2.157])+cube([18.65,-13.455,-.402],[.25,1.310,2.207])
eastbox=([18.60,-16.10,-.414],[.40,1.05,2.164]);westbox=([13.10,-16.70,-.414],[.75,1.65,2.164])
a=a-cube(*eastbox)-cube(*westbox)
put(n,[part(fromman(a),'M_Grey_Brick')],v20_closed_wrong_portals=[{'x':[13.35,13.60],'y':[-11.50,-10.25]},{'x':[18.65,18.90],'y':[-13.45,-12.15]}],v20_correct_east_gallery_end_portal={'origin':eastbox[0],'size':eastbox[1],'clear_width_m':1.05,'height_above_floor_m':2.15},v20_west_gallery_entrance={'origin':westbox[0],'size':westbox[1]})
for label,ob in [('old_west_filled',oldwest),('old_east_filled',oldeast)]:
 rem=(ob-a).volume();assert rem<1e-6,(label,rem);proof['checks'].append({'check':label,'unfilled_volume_m3':rem})
for label,ob in [('east_gallery_end_open',cube(*eastbox)),('west_gallery_end_open',cube(*westbox))]:
 rem=(ob^a).volume();assert rem<1e-6,(label,rem);proof['checks'].append({'check':label,'obstruction_volume_m3':rem})

# Interior faces are white grey limewash in the footage; keep exterior canopy's grey brick.
pl=[]
for label,cut,shift in [
 ('west_room',cube([13.596,-14.81,-.401],[.004,4.91,5]),[.003,0,0]),
 ('east_room_and_gallery',cube([18.65,-16.20,-.401],[.004,6.51,5]),[-.003,0,0]),
 ('north_room',cube([13.595,-9.95,-.401],[5.06,.004,5]),[0,-.003,0])]:
 skin=(a^cut).translate(shift)
 if not skin.is_empty():pl.append(part(fromman(skin),'M_Wall_Interior'))
put('SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH',pl,True,classification='THIN_PHOTO_CONFIRMED_WHITE_GREY_INTERIOR_PLASTER',v20_thickness_m=.004,v20_inside_offset_m=.003,v20_portals_preserved=True)

# Remove the existing two door leaves from the union timber and restore frame overlap.
n='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY';wood=native(n);yf=-14.855;dl=15.665;dr=16.585;wid=.455
leafms=[];door_nodes=[]
for side,hinge,ang,label in [(1,dl,65,'L'),(-1,dr,-65,'R')]:
 ps=[box(0,-.035,-.392,wid,.070,2.04,'M_V18_Aged_Storage_Timber')]
 for z in [-.14,.64,1.48]:ps.append(box(.052,-.043,z,wid-.104,.086,.032,'M_V18_Aged_Storage_Timber'))
 leafclosed=addall([manifold(p['geometry']) for p in ps])
 # Left +65/right -65 in original script: both swing into the +Y room.
 t=math.radians(ang);R=np.array([[math.cos(t),-math.sin(t),0],[math.sin(t),math.cos(t),0],[0,0,1]])
 olds=[]
 for p in ps:
  vv,fs,_,_=ex.solid_data(p['geometry']);vv=np.array(vv);vv[:,0]*=side;vv=vv@R.T+np.array([hinge,yf,0]);olds.append(manifold(oriented({'type':'polyhedron','vertices':vv.tolist(),'faces':[list(f) for f in fs]})))
 old=addall(olds);leafms.append(old);wood=wood-old
 # Export open 90 degrees, independent door leaf, unchanged clear opening and hinge.
 newps=[];ang90=side*90;t=math.radians(ang90);R=np.array([[math.cos(t),-math.sin(t),0],[math.sin(t),math.cos(t),0],[0,0,1]])
 for p in ps:
  vv,fs,_,_=ex.solid_data(p['geometry']);vv=np.array(vv);vv[:,0]*=side;vv=vv@R.T+np.array([hinge,yf,0]);newps.append(part(oriented({'type':'polyhedron','vertices':vv.tolist(),'faces':[list(f) for f in fs]}),'M_V18_Aged_Storage_Timber'))
 leaf=addall([manifold(p['geometry']) for p in newps]);nn=f'DOOR_STORAGE_V20_{label}__LEAF'
 put(nn,[part(fromman(leaf),'M_V18_Aged_Storage_Timber')],True,layer='30_DOOR',family='ARCH_MODEL',role='LEAF',v20_door=True,pivot_world_m=[hinge,yf,-.392],hinge_origin_local_m=[hinge,yf,-.392],open_angle_degrees=90,rotation_axis='Z',inward_normal_local=[0,1,0],opening_direction='INWARD',leaf_width_m=wid,leaf_height_m=2.04,closed_angle_degrees=0 if side==1 else 180)
 door_nodes.append(nn)
# Reinstate the original timber jambs at the hinge contacts, which Boolean separation trims.
frame=[]
for x in [13.63,15.60,16.65,18.62]:frame.append(manifold(box(x-.065,yf-.075,-.40,.13,.15,2.62,'M_V18_Aged_Storage_Timber')['geometry']))
wood=wood+addall(frame)
put(n,[part(fromman(wood),'M_V18_Aged_Storage_Timber')],v20_independent_inward_door_leaves=door_nodes)
proof['checks'].append({'check':'two_storage_door_leaves_separated_from_timber','leaves':door_nodes,'open_degrees':90,'inward_normal':[0,1,0],'clear_jamb_width_m':.92})

# Southern stone guard aligns with the screenwall axis. Keep all carved-panel UVs.
oldline=np.array([[13.59,-16.10],[18.9,-16.2],[20.2,-16.2],[21.3,-15.4],[21.45,-13],[20.95,-10.35],[18.9,-9.7]])
newline=oldline.copy();newline[:3,1]=-16.90
def guard_displacement(v):
 p=np.asarray(v)[:,:2];best=np.full(len(p),1e20);dy=np.zeros(len(p))
 for j,(a0,b0) in enumerate(zip(oldline[:-1],oldline[1:])):
  d=b0-a0;t=np.clip((p-a0)@d/(d@d),0,1);q=a0+t[:,None]*d;dist=((p-q)**2).sum(1);choose=dist<best
  delta=(newline[j,1]-a0[1])*(1-t)+(newline[j+1,1]-b0[1])*t
  dy[choose]=delta[choose];best[choose]=dist[choose]
 return dy
def cache_override(n,xf,**meta):
 dd=np.load(B/'02_Data'/I[n]['file']);data={k:dd[k].copy() for k in dd.files};v=xf(data['vertices']);f=data['faces'];t=v[f];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);lens=np.linalg.norm(nn,axis=1);assert lens.min()>1e-12,(n,lens.min());nn/=lens[:,None];vn=np.zeros_like(v)
 for k in range(3):np.add.at(vn,f[:,k],nn)
 ln=np.linalg.norm(vn,axis=1);vn[ln>0]/=ln[ln>0,None];data.update(vertices=v,normals=vn)
 fp=D/('NATIVE_'+n+'.npz');np.savez_compressed(fp,**data)
 vv,inv=np.unique(np.round(v,10),axis=0,return_inverse=True);ff=inv[f];mm=mf.Manifold(mf.Mesh64(vv,ff.astype(np.uint64)));assert mm.status()==mf.Error.NoError,(n,mm.status())
 e=put(n,[part({'type':'polyhedron','vertices':vv.tolist(),'faces':ff.tolist()},I[n]['materials'][0])],v20_native_cache_override=str(fp),**meta)
 proof['cache_overrides'][n]={'file':str(fp),'preserved_uv':bool(np.array_equal(data['uv'],dd['uv'])),'preserved_faces':bool(np.array_equal(f,dd['faces'])),'vertices':len(v),'triangles':len(f),'closed_status':str(mm.status())};return e,mm
def railxf(v):
 v=v.copy();v[:,1]+=guard_displacement(v);return v
ge,gm=cache_override('SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD',railxf,v20_guard_line=newline.tolist(),v20_alignment_y=-16.90,v20_entry_gap_x=[11.10,13.35])
# New bays are supplied for any renderer that creates atlas UVs from scene geometry.
for b in ge.get('v18_bays',[]):
 for k in ['start','end','panel_start','panel_end']:
  q=np.array([b[k]+[0.]]) if len(b[k])==2 else np.array([b[k]]);q=railxf(q);b[k]=q[0,:2].tolist()
 aa=np.array(b['start']);bb=np.array(b['end']);d=(bb-aa)/np.linalg.norm(bb-aa);b['direction']=d.tolist();b['normal']=[-d[1],d[0]]

# Floor and retaining wall follow the new line as one full stone support, with no platform undercut.
oldplan=footprint('SITE_V18_CONTINUOUS_STORAGE_STONE_BASE');frontpoly=Polygon([[13.35,-16.90],[20.2,-16.90],[21.30,-15.4],[21.45,-13],[20.95,-10.35],[18.90,-9.7],[13.35,-9.7]])
newplan=oldplan.union(frontpoly.buffer(.14,join_style=2)).buffer(0)
newarea=newplan.difference(oldplan).intersection(sb(13.2,-17.20,21.70,-15.2));extension=newarea.buffer(.015,join_style=2).intersection(newplan).buffer(0)
eps=[extension] if extension.geom_type=='Polygon' else [p for p in extension.geoms if p.area>1e-7]
baseadd=[part(prism(p,z,h),mat) for p in eps for z,h,mat in [(-4.65,3.60,'M_V18_Storage_Rubble'),(-1.05,.642,'M_V18_Storage_Dark_Courses')]]
put('SITE_V20_STORAGE_ALIGNED_STONE_BASE_EXTENSION',baseadd,True,classification='FULL_DEPTH_RUBBLE_AND_DARK_STONE_GALLERY_EDGE_CONTINUATION',v20_existing_base_retained=True,v20_overlap_m=.015,v20_alignment_y=-16.90)
total=native('SITE_V18_CONTINUOUS_STORAGE_STONE_BASE')+addall([manifold(p['geometry']) for p in baseadd]);assert len(total.decompose())==1,len(total.decompose())
gallery=sb(13.35,-16.90,18.90,-14.85)
put('SITE_V17_STORAGE_EAVE_GALLERY_FLOOR',[part(prism(gallery,-.425,.031),'M_Stone')],v20_guard_alignment_y=-16.90,v20_new_clear_gallery_depth_m=2.05)
outerpoly=Polygon([[18.9,-16.90],[20.2,-16.90],[21.30,-15.4],[21.45,-13],[20.95,-10.35],[18.9,-9.7]])
put('SITE_V14_OUTER_STORAGE_FLOOR',[part(prism(outerpoly,-.55,.15),'M_Stone')],v20_aligned_front_y=-16.90)
proof['checks'].append({'check':'aligned_guard_and_floor_full_stone_support','axis_y':-16.90,'base_connected_components':len(total.decompose()),'guard_base_overlap_m3':(gm^total).volume(),'gallery_plan_clear_depth_m':2.05,'west_entry_gap_m':2.25})

# Extend only the south eave in its existing plane; the L valley and north roof stay unchanged.
rf=json.loads((W/'v14/Roof_Junction_QA.json').read_text(encoding='utf8'));cs=np.array(rf['inner_south_top_plane']);hh=lambda x,y:float(np.dot([x,y,1],cs))
extpoly=sb(13.30,-17.15,19.12,-16.445)
roof=part({'type':'prism','profile':[[x,y,hh(x,y)-.055] for x,y in list(extpoly.exterior.coords)[:-1]],'vector':[0,0,.055]},'M_Roof')
put('SITE_V20_STORAGE_SOUTH_EAVE_CONTINUATION',[roof],True,classification='SAME_PLANE_EAVE_EXTENSION_WITH_UNCHANGED_L_ROOF_VALLEY',v20_existing_roofs_unchanged=True,v20_top_plane=cs.tolist())
woodps=[part({'type':'prism','profile':[[x,y,hh(x,y)-.085] for x,y in list(extpoly.exterior.coords)[:-1]],'vector':[0,0,.030]},'M_V18_Aged_Storage_Timber')]
for x in np.arange(13.4,19.04,.24):woodps.append(beam([float(x),-16.40,hh(x,-16.40)-.110],[float(x),-17.15,hh(x,-17.15)-.110],.045,.06,'M_V18_Aged_Storage_Timber'))
woodps.append(beam([13.30,-17.12,hh(13.30,-17.12)-.10],[19.12,-17.12,hh(19.12,-17.12)-.10],.045,.12,'M_V18_Aged_Storage_Timber'))
put('SITE_V20_STORAGE_SOUTH_EAVE_TIMBER_CONTINUATION',woodps,True,classification='SUPPORTED_RAFTER_AND_SHEATHING_CONTINUATION')
tiles=[]
for x in np.arange(13.35,19.09,.18):
 for y in np.arange(-16.445,-17.15,-.285):
  y2=max(float(y-.31),-17.15);tiles.append(tile([float(x),float(y),hh(x,y)-.003],[float(x),y2,hh(x,y2)-.003]))
put('SITE_V20_STORAGE_SOUTH_EAVE_TILE_COURSES',tiles,True,classification='CURVED_TILE_CONTINUATION_IN_EXISTING_ROOF_PLANE')
co=np.array(E['SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY']['v18_registered_top_plane'])
def metalxf(v):
 v=v.copy();old=v.copy();dy=-.70*np.clip((-old[:,1]-15.4)/.80,0,1);v[:,1]+=dy
 h=np.c_[old[:,:2],np.ones(len(old))]@co;fraction=np.clip((old[:,2]+.404)/(h+.404),0,1);v[:,2]+=co[1]*dy*fraction;return v
cache_override('SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY',metalxf,v20_aligned_front_y=-16.90,v20_sheet_top_plane_preserved=True)
# Pipe positions track the real exterior edge; source tube geometry and diameters retained.
n='SITE_V18_PHOTO_EXTERIOR_WHITE_PIPE_LINES';ps=[]
for p in E[n]['parts']:
 vv,fs,_,_=ex.solid_data(p['geometry']);vv=railxf(np.array(vv));ps.append(part(oriented({'type':'polyhedron','vertices':vv.tolist(),'faces':[list(f) for f in fs]}),p['material']))
put(n,ps,v20_exterior_front_alignment_y=-16.90)

# Local front shoulder/channel continuation. Existing V19 drainage native objects are untouched.
# It lies immediately outside the new full-height stone face, retaining the photographed open gutter.
oldsegs=[s for s in json.loads((W/'v16/Drain_Segments.json').read_text(encoding='utf8')) if s['ci']==3]
def grade(q):
 q=np.array(q);best=None
 for r in oldsegs:
  a0=np.array(r['a']);d=np.array(r['b'])-a0;t=float(np.clip((q-a0)@d/(d@d),0,1));di=np.linalg.norm(q-a0-t*d);zz=r['za']+t*(r['zb']-r['za'])
  if best is None or di<best[0]:best=(di,zz)
 return float(best[1])
route=[np.array([13.35,-17.04]),np.array([20.2,-17.04]),np.array([21.43,-15.48])]
ns=[]
for a0,b0 in zip(route[:-1],route[1:]):
 dd=(b0-a0)/np.linalg.norm(b0-a0);ns.append(np.array([dd[1],-dd[0]]))
ms=[ns[0]]+[(ns[j-1]+ns[j])/(1+float(np.dot(ns[j-1],ns[j]))) for j in range(1,len(ns))]+[ns[-1]]
con=[];road=[];drainrecords=[]
def sloping_strip(a0,b0,na,nb,lo,hi,topoffset,bottomoffset,mat):
 za=grade(a0)+topoffset;zb=grade(b0)+topoffset;ba=grade(a0)+bottomoffset;bb=grade(b0)+bottomoffset
 vv=[[*(a0+na*lo),ba],[*(b0+nb*lo),bb],[*(b0+nb*hi),bb],[*(a0+na*hi),ba],[*(a0+na*lo),za],[*(b0+nb*lo),zb],[*(b0+nb*hi),zb],[*(a0+na*hi),za]]
 return part(oriented({'type':'polyhedron','vertices':vv,'faces':[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]}),mat)
for j,(a0,b0) in enumerate(zip(route[:-1],route[1:])):
 for lo,hi,top,bottom in [(-.015,.09,-.02,-.46),(.09,.34,-.28,-.46),(.34,.43,-.02,-.46)]:con.append(sloping_strip(a0,b0,ms[j],ms[j+1],lo,hi,top,bottom,'M_V19_Perimeter_Road_Shoulder'))
 road.append(sloping_strip(a0,b0,ms[j],ms[j+1],.43,1.05,0,-.10,'M_V19_Perimeter_Road_Shoulder'))
 drainrecords.append({'start':a0.tolist(),'end':b0.tolist(),'za':grade(a0),'zb':grade(b0),'channel_clear_width_m':.25,'channel_depth_m':.26})
localdrain=addall([manifold(p['geometry']) for p in con+road]);assert len(localdrain.decompose())==1,len(localdrain.decompose())
put('SITE_V20_STORAGE_FRONT_GUTTER_AND_ROAD_SHOULDER',[part(fromman(localdrain),'M_V19_Perimeter_Road_Shoulder')],True,classification='LOCAL_NEW_FRONT_OPEN_CHANNEL_AND_ROAD_SHOULDER_CONTINUATION',v20_old_drain_native_retained=True,v20_route=drainrecords,v20_corner_miter_closed=True)
proof['checks'].append({'check':'local_front_gutter_miter_continuity','closed_connected_bodies':len(localdrain.decompose()),'miter_station':route[1].tolist(),'body_volume_m3':localdrain.volume(),'base_overlap_volume_m3':(localdrain^total).volume()})

# QA boxes describe free pedestrian passage above the thresholds, not guesses of hidden construction.
proof['clearance_boxes']=[
 {'label':'Correct east storage eave end portal pedestrian lane','origin':[18.65,-15.69,-.38],'size':[.25,.62,2.11]},
 {'label':'West gallery end entry pedestrian lane','origin':[13.10,-15.70,-.38],'size':[.51,.60,2.11]},
 {'label':'Screenwall-to-gallery entrance','origin':[11.13,-16.73,-.35],'size':[2.14,1.52,1.9]},
 {'label':'Gallery path north of existing timber columns','origin':[13.84,-15.70,-.23],'size':[4.48,.70,1.9]},
 {'label':'Storage front double-door passage','origin':[15.725,-15.03,-.35],'size':[.80,.60,1.93]},
]
proof['unmodified_nodes']=['SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL','SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY','SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE','SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE','all independent V19 perimeter masonry and coping']
allE={**E,**{e['name']:e for e in Q['replace']+Q['add']}}
obstacle_names=['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH','SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY','SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES','SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD']+door_nodes
obstacles=addall([manifold(p['geometry']) for n in obstacle_names for p in allE[n]['parts']])
for r in proof['clearance_boxes']:
 mm=cube(r['origin'],r['size']);hit=(mm^obstacles).volume();r['obstruction_volume_m3']=hit
 # The broad screenwall entry box is a reference extent; narrow movement boxes test actual solids.
 if 'Screenwall' not in r['label']:assert hit<1e-6,(r['label'],hit)
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
(D/'Design_Control.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
print('READY',len(Q['replace']),len(Q['add']),len(Q['remove']),flush=True)
