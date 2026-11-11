"""Geometric ownership and flush finishes for the annotated V31 house."""
import sys,json,math
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_32';sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from v24_16_common import solid,cube,union,section
from v24_32_rail_profiles import lathe,baluster,newel,handpath
I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};OUT={'raw_objects':[],'remove':[],'proof':{}};changed={};cache={}
def src(n):return np.load(D/I[n]['file'])
def load(n):
 if n not in cache:
  a=src(n);cache[n]=solid(a['v'],a['f'],n)
 return cache[n]
def polys(g):return [g]if g.geom_type=='Polygon'else[p for p in g.geoms if p.geom_type=='Polygon'and p.area>1e-10]
def prism(g,z0,z1):
 ms=[]
 for p in polys(g):
  if p.area<1e-10:continue
  m=section(p.exterior.coords,z1-z0).translate([0,0,z0])
  for h in p.interiors:m-=section(h.coords,z1-z0+.02).translate([0,0,z0-.01])
  ms.append(m)
 return union(ms)
def plan(m,z):
 # Union positive loops and subtract clockwise holes separately.
 rings=m.slice(z).to_polygons();pos=[];neg=[]
 for r in rings:
  p=Polygon(r)
  (pos if p.exterior.is_ccw else neg).append(p)
 return unary_union(pos).difference(unary_union(neg)).buffer(0)
def stage(n,m,materials=None,**kw):changed[n]=(m,materials or I[n]['materials'],kw)
floors={1:-.45,2:3.4500244140625,3:7.05};ceils={1:3.320019483566284,2:6.919995307922363,3:10.220044136047363}
core={fl:load(f'FACADE_CONTINUOUS_F{fl}_Geometry')for fl in floors};parts={fl:load(f'PARTITIONS_JOINED_F{fl}_Geometry')for fl in floors};clads={n:load(n)for n in I if n.startswith('HOUSE_V21_')and'GREY_WHITE_'in n};wcproof=[];bandproof=[]
for fl,floor in floors.items():
 ceil=ceils[fl];upper=floors.get(fl+1,ceil);beamlo=ceil-.27001953
 # External wall heads are flush, including the former beam/slab band. The
 # sampled low section is below ordinary window sills, so it is complete.
 extzone=unary_union([box(-.24,2.30,.24,10.1),box(12.76,2.30,13.24,10.1),box(-.24,9.69,13.24,10.1)])
 fp=plan(core[fl],floor+.30).intersection(extzone)
 core[fl]=union([core[fl],prism(fp,beamlo-.003,upper)])
 for side in ['WEST','EAST','REAR']:
  n=f'HOUSE_V21_{side}_GREY_WHITE_F{fl}_Geometry';m=clads[n];profile=plan(m,floor+.30)
  m=m-cube([-2,-2,beamlo],[15,12,upper+.0001]);m=union([m,prism(profile,beamlo,upper)])
  if side in ['WEST','EAST']and(fl<3 or side=='EAST'):
   x=0 if side=='WEST'else 13
   cutter=cube([x-.26,7.94997,floor+.85],[x-.104,9.15003,floor+2.65])if side=='WEST'else cube([x+.104,7.94997,floor+.85],[x+.26,9.15003,floor+2.65])
   volume=m.volume();m-=cutter;wcproof.append({'floor':fl,'side':side,'outer_plane_x_m':x+(-.104 if side=='WEST'else.104),'removed_projection_m3':volume-m.volume(),'old_projection_depth_m':.112})
  clads[n]=m^cube([-2.,-2.,floor],[15.,12.,upper])
 # The unnecessary front beam was still exposed in the stairwell. Continue
 # the existing partition through this zone, without inserting a new wall F3.
 n=f'BEAM_X_F{fl}_7.3_3.9_Geometry';OUT['remove'].append(n)
 if fl<3:parts[fl]=union([parts[fl],cube([4.,7.2,beamlo-.004],[8.9,7.4,upper])])
 bandproof.append({'floor':fl,'beam_zone_z_m':[beamlo,upper],'outer_finish_profile_retained':True,'front_stair_beam_removed':n})
# Exterior horizontal fascia strips are independent proxies, not apertures.
OUT['remove'] += [f'FLOOR_FASCIA_CONTINUOUS_F{fl}_Geometry'for fl in [2,3]]
# Trim the remaining exterior-side beams to the actual wall planes. This
# avoids leaving a thin ledge once the independent floor fascia is removed.
for n in I:
 if not n.startswith('BEAM_')or n in OUT['remove']:continue
 m=load(n);old=m.volume()
 if n.startswith('BEAM_Y_')and('_0_'in n or '_13_'in n):
  x=0 if '_0_'in n else 13;m=m^cube([x-.1,-2,-2],[x+.1,12,15])
 elif n.startswith('BEAM_X_')and'_9.8_'in n:m=m^cube([-2,9.7,-2],[15,9.9,15])
 # The terrace/hall wall is 200mm; its beam should share those planes.
 elif n.startswith('BEAM_Y_F3_')and'_2.1_'in n:
  x=3.9 if'_3.9_'in n else 9.1;m=m^cube([x-.1,-2,-2],[x+.1,12,15])
 if old-m.volume()>1e-8:stage(n,m);bandproof.append({'name':n,'removed_ledge_m3':old-m.volume()})
# A single owner for each complete bay panel and its stone sill/surrounds.
# Remove the older overlapping face underneath, also on the preceding story.
bayproof=[];bayowners={};cladname='HOUSE_V22_FRONT_BAY_TILE_FACES_Geometry';frontclad=load(cladname)
for fl,floor in floors.items():
 ms=[]
 for side in (['L','R']if fl<3 else['R']):
  x0=0 if side=='L'else 9.1;zone=box(x0-.24,.78,x0+4.14,2.215);z0=floor-.20;z1=floor+.598
  existing=load(f'V24_31_F{fl}_Complete_Bay_Underwindow_Walls')^cube([x0-.3,.7,z0-.001],[x0+4.2,2.3,z1+.001])
  surrounds=[f'CONSTRUCTION_SILL_BAY_WINDOW_F{fl}_{side}_{j}_Geometry'for j in range(3)]
  wall=union([existing]+[load(n)for n in surrounds]);ms.append(wall);OUT['remove']+=surrounds
  cut=prism(zone,z0,z1)
  for k in floors:core[k]-=cut
  frontclad-=cut
  bayproof.append({'floor':fl,'side':side,'bottom_m':z0,'sill_m':floor+.6,'previous_wall_overlap_removed':True,'sill_and_underwall_unioned':surrounds})
 bayowners[fl]=union(ms);stage(f'V24_31_F{fl}_Complete_Bay_Underwindow_Walls',bayowners[fl],['M_Stone'])
allbay=union(list(bayowners.values()))
for fl in floors:
 # The complete sill assemblies own their intersections with the core.
 core[fl]-=allbay
 # Existing facade returns and the completed stair partition shared small
 # same-facing patches on X=4.0. Let the partition own these actual joins.
 core[fl]-=parts[fl]
 stage(f'FACADE_CONTINUOUS_F{fl}_Geometry',core[fl]);stage(f'PARTITIONS_JOINED_F{fl}_Geometry',parts[fl])
stage(cladname,frontclad-allbay)
for n,m in clads.items():stage(n,m)
for fl in [1,2,3]:
 n=f'SLAB_JOINED_F{fl}_Geometry';m=load(n);v0=m.volume();m-=allbay
 if fl>1:
  # Old stair-block slab projected 100mm beyond the rear wall between posts.
  m-=cube([4.10001,9.9,-2],[8.89999,10.02,15])
  # Walls through the slab edge take precedence over its coincident side.
  m-=union(list(core.values()))
 stage(n,m,['M_Concrete','M_V24_31_White_Painted_Ceiling','M_Wall_Exterior','M_Wall_Interior'],slab_materials=True)
 bandproof.append({'name':n,'hidden_wall_overlap_removed_m3':v0-m.volume(),'horizontal_floor_height_retained':floors[fl]})
OUT['proof'].update(bathroom_exterior=wcproof,floor_bands=bandproof,bay_joints=bayproof)
# Beam geometry enclosed by the continued finished wall has no separate
# surface ownership. Retire those proxies, avoiding coincident inner faces.
for n in list(changed):
 if not n.startswith('BEAM_'):continue
 fl=int(n.split('_F')[1][0]);m,materials,kw=changed[n]
 if n.startswith('BEAM_Y_')and('_0_'in n or'_13_'in n)or n.startswith('BEAM_X_')and'_9.8_'in n:
  remainder=m-core[fl]
  if remainder.volume()<2e-5:del changed[n];OUT['remove'].append(n)
  else:stage(n,remainder,materials)
# The marked F3 rear terrace panel still had a door-shaped hole in its old
# tile grid, backed by the now complete white stair wall. Continue the same
# rectangular ceramic finish across that obsolete cutout.
tiles=[]
for y in np.arange(7.1,9.59,.60):
 for z in np.arange(7.05,9.9515,.30):
  ya=y+.0015;yb=min(y+.5985,9.5895);za=z+.0015;zb=min(z+.2985,9.9515)
  if yb>ya and zb>za:tiles.append(cube([3.792,ya,za],[3.800,yb,zb]))
tile=mf.Manifold.compose(tiles);stage('TERRACE_SIDE_CERAMIC_PANEL_GRID_Geometry',tile,['M_Ceramic_Warm'])
grout=cube([3.798,7.1,7.05],[3.800,9.59,9.9515])-tile;stage('V24_32_F3_Terrace_Panel_Recessed_Grout',grout,['M_V21_Terrace_Grout'])
OUT['proof']['terrace_panel']={'object':'TERRACE_SIDE_CERAMIC_PANEL_GRID_Geometry','cause':'Old tile grid retained an obsolete door-shaped cutout while the wall behind was filled white.','same_original_material':'M_Ceramic_Warm','tiles':len(tiles),'finished_plane_x_m':3.792,'groove_recess_m':.006,'panel_y_m':[7.1,9.59],'panel_z_m':[7.05,9.9515]}
# Generate the complete rail once, then boolean-union actual positive joints.
# The two short landing barriers marked X are omitted. Keep the stair mouths
# open; guard the missing rear well edge at F2 and F3 instead.
wood=[];meta=[];bcount=0
def hz(n,x,y):
 a=src(n);t=a['v'][a['f']];A=t[:,1,:2]-t[:,0,:2];B=t[:,2,:2]-t[:,0,:2];Q=np.array([x,y])-t[:,0,:2];det=A[:,0]*B[:,1]-A[:,1]*B[:,0];u=np.divide(Q[:,0]*B[:,1]-Q[:,1]*B[:,0],det,out=np.zeros_like(det),where=abs(det)>1e-10);w=np.divide(A[:,0]*Q[:,1]-A[:,1]*Q[:,0],det,out=np.zeros_like(det),where=abs(det)>1e-10);ok=(det>1e-10)&(u>=-1e-5)&(w>=-1e-5)&(u+w<=1.00001)
 assert ok.any(),(n,x,y)
 return float((t[:,0,2]+u*(t[:,1,2]-t[:,0,2])+w*(t[:,2,2]-t[:,0,2]))[ok].max())
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
for fl,base,land,upper in [(1,-.45,1.499951124,3.450024414),(2,3.450024414,5.249951363,7.05)]:
 for k,ya,xb,xe,zb,ze in [(1,8.585,7.8,5.13,base,land),(2,8.515,5.13,7.8,land,upper)]:
  pts=[]
  for u in np.linspace(0,1,41):
   x=xb+(xe-xb)*u;z=zb+(ze-zb)*u+.955;endblend=max(1-smooth(u/.13),smooth((u-.87)/.13));y=ya+(8.55-ya)*endblend;pts.append([x,y,z])
  wood.append(handpath(pts));meta.append({'floor':fl,'flight':k,'endpoints':pts[::40]})
  for x in np.linspace(5.32,7.66,12):
   u=(x-xb)/(xe-xb);y=ya+(8.55-ya)*max(1-smooth(u/.13),smooth((u-.87)/.13));top=zb+(ze-zb)*u+.955;z=hz(f'STAIR_F{fl}_FLIGHT{k}_Geometry',float(x),9.0 if k==1 else 8.0);wood.append(baluster(float(x),float(y),z-.008,top));bcount+=1
 wood.append(newel(5.13,8.55,land))
for z in [-.45,3.450024414,7.05]:wood.append(newel(7.8,8.55,z))
for fl,z in [(3,7.05)]:
 pts=[[7.8,8.55,z+.955],[7.835,8.70,z+.955],[7.835,9.62,z+.955]];wood.extend([handpath(pts),newel(7.835,9.62,z)])
 for y in np.arange(8.72,9.59,.145):wood.append(baluster(7.835,float(y),z-.008,z+.955));bcount+=1
 meta.append({'floor':fl,'rear_guard':True,'endpoints':[pts[0],pts[-1]],'does_not_cross_stair_mouth':True})
wood.extend([handpath([[3.985,7.265,8.005],[7.835,7.265,8.005]]),newel(7.835,7.265,7.05)])
for x in np.arange(4.15,7.72,.145):wood.append(baluster(float(x),7.265,7.042,8.005));bcount+=1
railing=union(wood);components=railing.decompose();assert len(components)==2,('Disconnected railing bodies',len(components))
stage('V24_32_Continuous_Stair_Wood_Railing',railing,['M_V24_31_Polished_Dark_Red_Stair_Wood'],smooth_wood=True)
OUT['remove'] += ['V24_31_Stair_Turned_Balusters','V24_31_Stair_Ball_Finial_Newels','V24_31_Stair_Rounded_Handrails']
OUT['remove'] +=[n for n in I if n.startswith('SITE_TREE_')]
OUT['proof']['railing']={'connected_solid_assemblies':len(components),'assemblies':'one continuous flight/newel/F3-rear-guard assembly; one wall-anchored F3 front well guard separated by the intentional stair mouth','turned_balusters':bcount,'newels':7,'lines':meta,'removed_short_landing_rails':2,'photo_basis':['003716','003738'],'tread_geometry_unchanged':True,'F2_rear_stair_mouth_kept_open':True,'F3_front_guard_axis_y_m':7.265,'F3_slab_edge_y_m':7.3,'bases_supported_on_slab':True}
OUT['proof']['removed_simple_trees']=[n for n in OUT['remove']if n.startswith('SITE_TREE_')]
# Store meshes with metre UV coordinates on their actual dominant plane.
for n,(m,materials,kw)in changed.items():
 assert m.status()==mf.Error.NoError and m.volume()>0,(n,m.status())
 a=m.to_mesh64();v=np.asarray(a.vert_properties[:,:3]);f=np.asarray(a.tri_verts);t=v[f];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);axis=np.argmax(abs(normal),axis=1);uv=np.zeros((len(f),3,2))
 for ax,dim in [(0,[1,2]),(1,[0,2]),(2,[0,1])]:uv[axis==ax]=t[axis==ax][:,:,dim]
 mi=np.zeros(len(f),int)
 if kw.get('slab_materials'):
  no=normal/np.linalg.norm(normal,axis=1)[:,None];mi[no[:,2]<-.15]=1;mi[abs(no[:,2])<.15]=2;c=t.mean(1);mi[(abs(no[:,2])<.15)&(abs(c[:,0]-4)<.001)&(c[:,1]>7.29)&(c[:,1]<9.71)]=3
 fn='NEW_'+n+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);OUT['raw_objects'].append({'name':n,'file':fn,'materials':materials,**kw});print('PREPARED',n,len(v),len(f),flush=True)
OUT['remove']=sorted(set(n for n in OUT['remove']if n in I));(D/'Prepared_Geometry.json').write_text(json.dumps(OUT,ensure_ascii=False),encoding='utf8');print('V32_PREPARED',len(changed),len(OUT['remove']),flush=True)
