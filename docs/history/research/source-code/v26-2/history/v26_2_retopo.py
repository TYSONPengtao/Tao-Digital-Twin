"""Rebuild wall topology from original prism plans, retaining current cores.

The previous finished shell contains self-intersecting sliver caps. Reusing
that triangulation for more Booleans is unstable. Original analytic wall plans
and the archived current core objects are the source of this replacement.
"""
from v26_2_common import *
from shapely.geometry import Polygon,box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import shapely,re
WHITE='M_Wall_Interior';CEILING='M_V24_31_White_Painted_Ceiling';GRID=.0001;JOINT=.0002
OLD='V26_1_House_Continuous_Opaque_Shell';PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))}
previous=json.loads((D/'Prepared_House.json').read_text('utf8'));frames=previous['objects'][1:];frameproof=previous['proof']['frames']
S=json.loads(Path('E:/jz/JIA/Rebuild_V20/08_Editable_Source/Architecture_Scene_V20.json').read_text('utf8'));E={e['name']:e for e in S['elements']}
def grid(a):return np.round(np.asarray(a)/GRID)*GRID
def normalize(v,f,mi=None,uv=None,name=''):
 v=grid(v);vv,ix=np.unique(v,axis=0,return_inverse=True);ff=ix[f];tr=vv[ff];good=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)>1e-12;ff=ff[good];mm=solid(vv,ff,name)
 if mi is None:return mm
 # Keep the exact per-face UV field while dropping only collapsed triangles.
 aa=mm.to_mesh64();nv=np.array(aa.vert_properties[:,:3]);nf=np.array(aa.tri_verts);nmi,nuv=remap({'v':vv,'f':ff,'mi':mi[good],'uv':uv[good]},nv,nf);return tracked(nv,nf,PI[name]['materials'],nmi,nuv,name+' canonical core')
def polygon_prism(poly,z0,z1):
 poly=shapely.set_precision(poly.buffer(0),GRID);parts=[poly]if poly.geom_type=='Polygon'else[p for p in poly.geoms if p.geom_type=='Polygon'];cont=[]
 for p in parts:
  if p.area<1e-10:continue
  p=orient(p,1);cont.append(np.array(p.exterior.coords)[:-1]);cont.extend(np.array(r.coords)[:-1]for r in p.interiors)
 return mf.CrossSection(cont,mf.FillRule.NonZero).extrude(round((z1-z0)/GRID)*GRID).translate([0,0,round(z0/GRID)*GRID])
def desc(g):
 if g['type']=='box':
  lo=grid(g['origin']);lo[2]-=.45;return cube(lo,grid(lo+g['size']))
 return polygon_prism(Polygon(g['outer'],g.get('holes',[])).buffer(JOINT,join_style=2),g['z']-.45-JOINT,g['z']+g['height']-.45+JOINT)
walls=[];wallproof=[];floors=[-.45,3.45,7.05];ceilings=[3.32,6.92,10.22]
for fl,floor,ceiling in zip([1,2,3],floors,ceilings):
 for kind in ['FACADE_CONTINUOUS','PARTITIONS_JOINED']:
  name=f'{kind}_F{fl}';parts=[desc(p['geometry'])for p in E[name]['parts']];m=union(parts)
  if kind.startswith('PARTITIONS'):
   # Current confirmed bedroom doorway is south of its column, and the
   # previous inferred opening is closed. Retain the plain terrace passage.
   if fl==3:
    m+=cube([9.,7.55,floor],[9.2,8.45,floor+2.1]);m-=cube([8.85,6.15,floor-.001],[9.35,7.05,floor+2.101])
   if fl==1:
    m+=cube([11.9,7.2,floor],[12.7,7.4,floor+2.1]);m-=cube([10.7,7.05,floor-.001],[11.5,7.55,floor+2.101])
   # Use the whole current stair chamber. The two real stair flights and
   # landings are separate core objects, not inferred wall slices.
   m-=cube([4.112,7.512,floor-.001],[8.888,9.588,ceiling+.001])
   if fl<3:m+=cube([4.112,7.2,floor],[7.8,7.4,ceiling])
  else:
   # Replace tall legacy side-window cutouts with the actual saved glazing
   # aperture. No window position or animation is changed.
   for side in ['LEFT','RIGHT']:
    n=f'WINDOW_{side}_C1212_F{fl}_Geometry'
    if n not in I:continue
    lo,hi=np.array(I[n]['bounds']);x0,x1=(-.1,.1)if side=='LEFT'else(12.9,13.1)
    m+=cube([x0,7.95,floor],[x1,9.15,ceiling]);m-=cube([x0-.02,7.95,round(lo[2],4)],[x1+.02,9.15,round(hi[2],4)])
   # Continue the low opaque bay/parapet footprints down to the slab base.
   low=E[name]['parts'][0]['geometry'];m+=polygon_prism(Polygon(low['outer'],low.get('holes',[])),floor-.2,floor)
   # Close the existing stair rear opaque wall to the current slab soffit.
   m+=cube([4.112,9.7,floor],[7.7,9.9,ceiling])
  # Parametric wall nodes have beam exclusions. Extend each actual top wall
  # footprint into the retained beam zone, preserving all door/window holes.
  z=ceiling-.28;cs=m.slice(z);m+=cs.extrude(.29).translate([0,0,z-.01])
  m=finish(m,WHITE,name+' rebuilt prism topology');walls.append(m);wallproof.append({'name':name,'parts':len(parts),'volume_m3':m.volume(),'components':len(m.decompose()),'source':'Original editable prism-hole plans plus the current confirmed openings','canonical_grid_m':GRID});print('RETOPO_WALL',name,m.num_tri(),m.volume(),flush=True)
names=json.loads((PD/'Prepared_House.json').read_text('utf8'))['archive'];core=[];coreproof=[]
for n in names:
 if n.startswith(('FACADE_CONTINUOUS','PARTITIONS_JOINED','V24_31_F'))or n=='HOUSE_V22_FRONT_BAY_TILE_FACES_Geometry'or(n.startswith('HOUSE_V21_')and'GREY_WHITE'in n):continue
 a=np.load(PD/PI[n]['file'])
 if n.startswith('SLAB_JOINED'):
  tr=a['v'][a['f']];nn=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);fp=unary_union([Polygon(t[:,:2])for t in tr[nn[:,2]>1e-9]]).buffer(JOINT,join_style=2);m=finish(polygon_prism(fp,float(a['v'][:,2].min())-JOINT,float(a['v'][:,2].max())),'M_Floor',n+' analytic slab footprint')
 elif n.startswith('STAIR_F'):
  tr=a['v'][a['f']];nn=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);fp=unary_union([Polygon(t[:,[0,2]])for t in tr[abs(nn[:,1])>1e-9]]).buffer(JOINT,join_style=2);m=polygon_prism(fp,float(a['v'][:,1].min())-JOINT,float(a['v'][:,1].max())+JOINT);m=m.transform([[1,0,0,0],[0,0,1,0],[0,1,0,0]]);m=finish(m,'M_V24_31_Stair_Gray_Marble',n+' analytic tread and stringer profile')
 else:
  m=normalize(a['v'],a['f'],a['mi'],a['uv'],n);lo,hi=np.array(m.bounding_box()).reshape(2,3);center=(lo+hi)/2;scale=(hi-lo+2*JOINT)/(hi-lo);m=m.translate(-center).scale(scale).translate(center)
 if n.startswith('V26_Stair_Landing_Bearing_Beam_'):
  fl=int(n[-1]);f=np.load(PD/PI[f'STAIR_F{fl}_FLIGHT1_Geometry']['file']);t=f['v'][f['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);tr=t[(no[:,2]>1e-5)&(t[:,:,0].mean(1)>5.20001)&(t[:,:,0].mean(1)<5.46)];z=round(float(tr[:,:,2].max()),4);m-=cube([5.1999,8.54,z-.006],[5.31,9.83,z+.3])
 core.append(m);coreproof.append({'name':n,'normalized_volume_m3':m.volume(),'maximum_coordinate_rounding_m':float(np.max(abs(grid(a['v'])-a['v']))),'existing_local_tread_beam_notch_retained':n.startswith('V26_Stair_Landing_Bearing_Beam_')});print('CORE',n,m.num_tri(),flush=True)
body=union(walls+core);print('RETOPO_BASE',body.num_tri(),body.volume(),len(body.decompose()),flush=True)
# Derive all finish silhouettes from the rebuilt walls, not from the retired
# triangulated shell. Each source face already lies on the canonical grid.
a=body.to_mesh64();v=np.array(a.vert_properties[:,:3]);f=np.array(a.tri_verts);t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-30);c=t.mean(1)
targets=[('west_inside',0,1,.212,.099,.2119,-.45,10.22),('left_room_partition',0,-1,3.688,3.6881,3.801,-.45,6.92),('middle_west_partition',0,1,4.112,3.999,4.1119,-.45,10.22),('middle_east_partition',0,-1,8.888,8.8881,9.001,-.45,10.22),('right_room_partition',0,1,9.312,9.199,9.3119,-.45,10.22),('east_inside',0,-1,12.788,12.7881,12.901,-.45,10.22),('front_inside',1,1,2.312,2.199,2.3119,-.45,10.22),('rear_partition_front',1,-1,7.088,7.0881,7.201,-.45,10.22),('rear_partition_back',1,1,7.512,7.399,7.5119,-.45,10.22),('rear_inside',1,-1,9.588,9.5881,9.701,-.45,10.22),('terrace_wall',0,-1,3.680,3.681,3.801,7.05,10.22)]
adds=[];profiles=[]
for label,axis,sgn,end,low,high,zlo,zhi in targets:
 other=1-axis;mask=(no[:,axis]*sgn>.99999)&(c[:,axis]>low)&(c[:,axis]<high)&(t[:,:,2].max(1)>zlo+1e-6)&(t[:,:,2].min(1)<zhi-1e-6);extent=(1.884,10.016)if axis==0 else(-.216,13.216);shape=unary_union([Polygon(tr[:,[other,2]]).intersection(box(extent[0],zlo,extent[1],zhi))for tr in t[mask]]).buffer(0);shape=shapely.set_precision(shape,GRID)
 if shape.is_empty:continue
 parts=[shape]if shape.geom_type=='Polygon'else list(shape.geoms);cont=[]
 for p in parts:
  if p.area<1e-9:continue
  p=orient(p,1);cont.append(np.array(p.exterior.coords)[:-1]);cont.extend(np.array(r.coords)[:-1]for r in p.interiors)
 start=round((high if sgn<0 else low)/GRID)*GRID;begin=start+.0002 if sgn<0 else start-.0002;depth=abs(end-start)+.0002
 matrix=[[0,0,sgn,begin],[1,0,0,0],[0,1,0,0]]if axis==0 else[[1,0,0,0],[0,0,sgn,begin],[0,1,0,0]];m=mf.CrossSection(cont,mf.FillRule.NonZero).extrude(round(depth/GRID)*GRID).transform(matrix);adds.append(finish(m,WHITE,label+' continuous finish'));profiles.append({'wall':label,'axis':axis,'normal_sign':sgn,'plane_m':end,'z_m':[zlo,zhi],'opaque_profile_area_m2':shape.area,'canonical_grid_m':GRID});print('RETOPO_FINISH',label,m.num_tri(),flush=True)
body=union([body]+adds);a=body.to_mesh64();print('FINAL_RAW',body.volume(),body.num_tri(),len(body.decompose()),flush=True)
np.savez_compressed(D/'Debug_Raw_House.npz',v=a.vert_properties[:,:3],f=a.tri_verts)
for tag,verts in [('plain',np.array(a.vert_properties[:,:3])),('float32',np.array(a.vert_properties[:,:3]).astype(np.float32).astype(np.float64))]:
 test=mf.Manifold(mf.Mesh64(np.array(verts,copy=True),np.array(a.tri_verts,np.uint64,copy=True)));print('RAW_RELOAD',tag,test.status(),test.volume(),len(test.decompose()),[(p.volume(),p.bounding_box())for p in test.decompose()if abs(p.volume())<4],flush=True)
row,body=export('V26_2_House_Flush_Continuous_Finished_Shell',body,'Wall topology regenerated from analytic source plans and current registered openings; original beam column slab stair and roof cores retained on a 0.1mm canonical grid')
a=np.load(D/row['file']);v=a['v'];f=a['f'];mi=a['mi'].copy();uv=a['uv'];t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-30);c=t.mean(1);mats=row['materials']
for mat in [WHITE,CEILING,'M_Floor','M_V24_31_Stair_Gray_Marble','M_V21_House_Exterior_Grey_White']:
 if mat not in mats:mats.append(mat)
# Every exposed interior wall is plaster; roof and marble stair geometry keep
# their source materials, except the painted slab/beam soffits.
for label,axis,sgn,end,low,high,zlo,zhi in targets:
 mask=(n[:,axis]*sgn>.999)&(abs(c[:,axis]-end)<2e-5)&(c[:,2]>=zlo-1e-5)&(c[:,2]<=zhi+1e-5);mi[mask]=mats.index(WHITE)
mi[(n[:,2]<-.7)&(c[:,2]>-.4)]=mats.index(CEILING)
for z in floors:mi[(n[:,2]>.999)&(abs(c[:,2]-z)<.0002)]=mats.index('M_Floor')
# Preserve the gray-white outside as a material on the wall body itself.
mask=((n[:,0]<-.99)&(c[:,0]<-.09)|(n[:,0]>.99)&(c[:,0]>13.09)|(n[:,1]>.99)&(c[:,1]>9.89))&(c[:,2]<10.221)&(c[:,2]>-.45);mi[mask]=mats.index('M_V21_House_Exterior_Grey_White')
np.savez_compressed(D/row['file'],v=v,f=f,mi=mi,uv=uv)
# Retain explicit sill/head QA zones, now generated through clean wall topology.
sp=[]
for name,r in I.items():
 if not name.startswith(('WINDOW_LEFT_','WINDOW_RIGHT_','WINDOW_BACK_','WINDOW_FRONT_CENTER_F3')):continue
 lo,hi=np.array(r['bounds']);fl=int(re.search(r'_F([123])',name)[1]);floor,ceiling=floors[fl-1],ceilings[fl-1]
 if name.startswith('WINDOW_LEFT_'):a0=[-.104,float(lo[1]),floor];a1=[.212,float(hi[1]),ceiling]
 elif name.startswith('WINDOW_RIGHT_'):a0=[12.788,float(lo[1]),floor];a1=[13.104,float(hi[1]),ceiling]
 elif name.startswith('WINDOW_BACK_'):a0=[float(lo[0]),9.588,floor];a1=[float(hi[0]),9.904,ceiling]
 else:a0=[float(lo[0]),1.996,floor];a1=[float(hi[0]),2.312,ceiling]
 for zone,z0,z1 in [('sill',floor,float(lo[2])),('head',float(hi[2]),ceiling)]:
  if z1-z0>.0001:p0=a0.copy();p1=a1.copy();p0[2]=z0;p1[2]=z1;sp.append({'window':name,'zone':zone,'bounds_m':[p0,p1]})
for rr,m in zip(coreproof,core):rr['difference_to_final_m3']=max(0,(m-body).volume())
out={'objects':[row]+frames,'archive':[OLD],'proof':{'retopology':True,'canonical_grid_m':GRID,'wall_source_plans':wallproof,'core_components':coreproof,'finished_wall_profiles':profiles,'actual_window_opaque_zones':sp,'frames':frameproof,'raised_first_floor_right_glazed_door_corrected_m':-.45,'house_positive_components':len(body.decompose()),'structural_core_preserved':True,'invalid_legacy_caps_replaced':True}}
(D/'Prepared_House.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('RETOPO_READY',body.volume(),len(f),len(body.decompose()),'MAX_CORE_LOSS',max(p['difference_to_final_m3']for p in coreproof),flush=True)
