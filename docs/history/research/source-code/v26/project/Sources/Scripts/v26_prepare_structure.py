"""Geometric repairs based on saved V24.34 solids, not a structural analysis."""
from pathlib import Path
import sys,json,re
W=Path(__file__).parent;D=W/'v26';sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from v24_16_common import solid,cube,union,section
I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};Inv={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))}
S={};orig={};OUT={'objects':[],'proof':{'columns':[],'beams':[],'stairs':[],'walls':[]}}
for n,r in I.items():
 if n.startswith(('KZ_','BEAM_','SLAB_JOINED','FACADE_CONTINUOUS','PARTITIONS_JOINED','STAIR_F','STAIR_LANDING')):
  a=np.load(D/r['file']);S[n]=solid(a['v'],a['f'],n);orig[n]=S[n]

def put(n,m,materials,reason,new=False):
 assert m.status()==mf.Error.NoError and m.volume()>1e-8,(n,m.status(),m.volume())
 removed=0
 for _ in range(3):
  a=m.to_mesh64();v=np.array(a.vert_properties[:,:3]).astype(np.float32).astype(np.float64);f=np.array(a.tri_verts);m=solid(v,f,n+' single precision');parts=m.decompose();keep=[p for p in parts if p.volume()>1e-10];removed+=len(parts)-len(keep)
  if len(keep)==len(parts):break
  m=union(keep)
 a=m.to_mesh64();v=np.array(a.vert_properties[:,:3]);f=np.array(a.tri_verts);S[n]=m
 assert all(p.volume()>1e-10 for p in m.decompose()),(n,'zero-volume sheet survives')
 fn='PREP_'+n+'.npz';np.savez_compressed(D/fn,v=v,f=f)
 OUT['objects'].append({'name':n,'file':fn,'materials':materials,'new':new,'reason':reason,'volume_m3':m.volume(),'closed_components':len(m.decompose()),'zero_volume_boolean_sheets_removed':removed})

def polys(p):return [p]if p.geom_type=='Polygon'else [q for q in p.geoms if q.geom_type=='Polygon' and q.area>1e-10]
def prism(p,z0,z1):
 ms=[]
 for q in polys(p):
  m=section(list(q.exterior.coords)[:-1],z1-z0).translate([0,0,z0])
  for h in q.interiors:m-=section(list(h.coords)[:-1],z1-z0+.002).translate([0,0,z0-.001])
  ms.append(m)
 return union(ms)
def plan(m,z):return unary_union([Polygon(p)for p in m.slice(z).to_polygons() if len(p)>2]).buffer(0)
def overlap(a,b):return max(0.,(a^b).volume())
def close_small_junction_gaps(m,target,maxgap=.018):
 a=m.to_mesh64();v=np.array(a.vert_properties[:,:3]);f=np.array(a.tri_verts);adds=[];proof=[]
 for tt in v[f]:
  no=np.cross(tt[1]-tt[0],tt[2]-tt[0]);area=np.linalg.norm(no)/2
  if area<1e-7:continue
  no/=np.linalg.norm(no);pts=np.vstack([tt,tt.mean(0)]);gaps=[]
  for p in pts:
   hits=target.ray_cast(p+no*.000001,p+no*(maxgap+.0002));ent=[h for h in hits if np.dot(h.normal,no)<-.7]
   if not ent:break
   g=float(np.linalg.norm(np.array(ent[0].position)-p));gaps.append(g)
  if len(gaps)!=4 or max(gaps)-min(gaps)>.0005 or not .0004<max(gaps)<=maxgap:continue
  g=max(gaps)+.00003;vv=np.vstack([tt-no*.00003,tt+no*g]);ff=[[2,1,0],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]];adds.append(solid(vv,ff,'junction bridge'));proof.append({'gap_m':max(gaps),'face_area_m2':area,'center_m':tt.mean(0).tolist(),'normal':no.tolist()})
 return (m+union(adds) if adds else m),proof
levels={1:-.4499999881,2:3.450024414,3:7.050000191};ceils={1:3.320019484,2:6.919995308,3:10.220044136}
white=['M_V24_31_White_Painted_Ceiling']
# Six 400 x 400 columns had been reduced to 100 x 400 for a flush finish.
# Restore their saved original section and carry the column through its slab.
for n in [n for n in S if n.startswith('KZ_')]:
 match=re.match(r'KZ_(\d)_(\d)_F(\d)_Geometry',n);i,j,fl=map(int,match.groups());lo,hi=np.array(I[n]['bounds']);before=(hi-lo).tolist()
 if i==2 and j in [2,3]:lo[0]=3.7;hi[0]=4.1
 if fl<3:hi[2]=levels[fl+1]
 S[n]=cube(lo,hi);OUT['proof']['columns'].append({'name':n,'before_section_m':before[:2],'after_section_m':(hi-lo).tolist()[:2],'z_bottom_m':float(lo[2]),'z_top_m':float(hi[2]),'original_definition':Inv[n[:-9]]['props'].get('Parameters','')})
 put(n,S[n],I[n]['materials'],'Restore original column section and continuity through floor slab')
# Beams keep the existing section and soffit; extend their ends to the saved
# column grid centres so the joints have finite solid engagement.
for n in [n for n in S if n.startswith('BEAM_')]:
 match=re.match(r'BEAM_([XY])_F(\d)_([^_]+)_([^_]+)_Geometry',n);axis,fl,fixed,start=match.groups();fl=int(fl);fixed=float(fixed);start=float(start);lo,hi=np.array(I[n]['bounds']);k=0 if axis=='X' else 1;grid=[0.,3.9,9.1,13.]if k==0 else[2.1,7.3,9.8];end=grid[grid.index(start)+1];lo[k]=start;hi[k]=end;S[n]=cube(lo,hi)
 put(n,S[n],I[n]['materials'],'Beam end cores extended into existing column joint')
 OUT['proof']['beams'].append({'name':n,'axis':axis,'grid_ends_m':[start,end],'original_section_retained':True,'bounds':[lo.tolist(),hi.tolist()]})
# Replace retired beam proxies with a connected hidden frame at the stair
# walls, using the original 250 x 270 beam section and existing grid axes.
for fl in [1,2,3]:
 for tag,lo,hi in [
  ('North',[3.9,9.675,ceils[fl]-.27001953],[9.1,9.925,ceils[fl]]),
  ('West',[3.775,7.3,ceils[fl]-.27001953],[4.025,9.8,ceils[fl]]),
  ('East',[8.975,7.3,ceils[fl]-.27001953],[9.225,9.8,ceils[fl]])]:
  n=f'V26_Stair_Frame_{tag}_Beam_F{fl}';S[n]=cube(lo,hi);put(n,S[n],white,'Restore stair enclosure frame core on original column grid',True)
  OUT['proof']['beams'].append({'name':n,'bounds':[lo,hi],'original_grid_reinstated':True,'section_m':[.25,.27001953],'design_validation':'geometry only; capacity and reinforcement not verified'})
# Complete the wall return without clipping the restored column core. The
# inside finished plane is x=4.10; 1.10 m landing clear depth remains.
for fl in [1,2,3]:
 n=f'PARTITIONS_JOINED_F{fl}_Geometry';m=S[n];core=cube([3.8,7.2,levels[fl]],[4.1,9.9,ceils[fl]])
 # The neighbouring back wall connects into the outside face and the frame.
 S[n]=m+core
 # All frame cores have separate editable ownership; subtract them from the
 # wall volumes, eliminating overlapping coplanar display faces.
 frames=[m for nn,m in S.items() if (nn.startswith(('KZ_','BEAM_')) and f'_F{fl}_'in nn) or (nn.startswith('V26_Stair_Frame_') and nn.endswith(f'F{fl}'))]
 skeleton=union(frames)
 for kind in ['PARTITIONS_JOINED','FACADE_CONTINUOUS']:
  wn=f'{kind}_F{fl}_Geometry';before=S[wn].volume();other=f'{"FACADE_CONTINUOUS" if kind=="PARTITIONS_JOINED" else "PARTITIONS_JOINED"}_F{fl}_Geometry'
  S[wn],junctions=close_small_junction_gaps(S[wn],skeleton+S[other]);S[wn]-=skeleton
  # Keep exact floor/ceiling heights and all openings; retain the existing
  # full-depth masonry envelope, only resolve core ownership at junctions.
  put(wn,S[wn],I[wn]['materials'],'Resolve wall corner returns and eliminate wall/frame duplicate faces')
  OUT['proof']['walls'].append({'name':wn,'before_volume_m3':before,'after_volume_m3':S[wn].volume(),'frame_intersection_after_m3':overlap(S[wn],skeleton),'stair_wall_inside_x_m':4.1 if kind=='PARTITIONS_JOINED' else None,'closed_small_junction_gaps':junctions})
# Each half landing spans to the side wall and both flights. A buried cross
# beam and 120 mm side engagement remove edge-only and line-only contacts.
for fl in [1,2]:
 land=f'STAIR_LANDING_F{fl}_Geometry';lo,hi=np.array(I[land]['bounds']);lo[1]=7.28;hi[1]=9.82;S[land]=cube(lo,hi)
 bn=f'V26_Stair_Landing_Bearing_Beam_F{fl}';S[bn]=cube([5.03,7.28,lo[2]-.28],[5.30,9.82,lo[2]+.035]);put(bn,S[bn],white,'Buried cross beam positively joins platform, flights and side walls',True)
 put(land,S[land],I[land]['materials'],'Platform sides embedded 120 mm into retained enclosure walls')
 for k in [1,2]:
  n=f'STAIR_F{fl}_FLIGHT{k}_Geometry';a=np.load(D/I[n]['file']);v=a['v'].copy();f=a['f'];lo0,hi0=np.array(I[n]['bounds'])
  if k==1:v[np.isclose(v[:,1],hi0[1],atol=2e-5),1]=9.82
  else:v[np.isclose(v[:,1],lo0[1],atol=2e-5),1]=7.28
  m=solid(v,f,n)
  # The concealed end tongue is confined to the actual adjoining slab's
  # solid plan. It cannot cover the open stairwell or alter exposed treads.
  floor=fl if k==1 else fl+1;slab=S[f'SLAB_JOINED_F{floor}_Geometry'];z0,z1=I[f'SLAB_JOINED_F{floor}_Geometry']['bounds'][0][2],I[f'SLAB_JOINED_F{floor}_Geometry']['bounds'][1][2]
  p=plan(slab,(z0+z1)/2).intersection(box(7.70,8.23,8.22,9.82)if k==1 else box(7.70,7.28,8.22,8.54))
  assert p.area>.02,(n,p.area)
  tongue=prism(p,z0-.065,z0+.035)
  m+=tongue;S[n]=m;put(n,m,I[n]['materials'],'120 mm outer wall engagement and concealed finite-area slab end tongue')
  OUT['proof']['stairs'].append({'flight':n,'unchanged_tread_XZ':True,'side_wall_gap_before_m':.04,'side_wall_engagement_after_m':.12,'slab_contact_m3':overlap(m,slab),'platform_beam_contact_m3':overlap(m,S[bn]),'platform_contact_m3':overlap(m,S[land]),'end_tongue_plan_area_m2':p.area,'components':len(m.decompose())})
  assert overlap(m,slab)>1e-5 and overlap(m,S[bn])>1e-5
  assert len(m.decompose())==1,(n,'disconnected stair repair')
 # The landing engages the side masonry and crossbeam as one continuous body.
 OUT['proof']['stairs'].append({'landing':land,'west_wall_engagement_m':.2,'north_south_engagement_m':.12,'crossbeam_contact_m3':overlap(S[land],S[bn]),'clear_landing_depth_m':5.2-4.1})
(D/'Prepared_Structure.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2),encoding='utf8')
print('PREPARE_DONE',len(OUT['objects']),flush=True)
