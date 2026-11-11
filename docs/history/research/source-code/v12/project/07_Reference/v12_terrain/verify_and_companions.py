import sys,json,math,hashlib,collections,shutil
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import shape,Point,box
from PIL import Image,ImageDraw
import export_v5 as ex
D=Path(__file__).parent;V=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');M=json.loads((D/'Mutation.json').read_text());Q=json.loads((D/'Geometry_QA.json').read_text());Dom=json.loads((D/'Terrain_Domain.json').read_text());domain=shape(Dom['domain']);F=rh.File3dm.Read(str(D/'Rebuilt_Terrain_LOCAL.3dm'));ramp=next(r for r in Q['terrain_parts'] if 'RAMP' in r['name']);checks=[]
def check(n,p,**k):checks.append({'name':n,'pass':bool(p),**k})
# Each final native object must be a closed regular-grid reconstructed mesh.
for o in F.Objects:check(o.Attributes.Name+' native valid and closed',isinstance(o.Geometry,rh.Mesh) and o.Geometry.IsValid and o.Geometry.IsClosed and o.Geometry.Vertices.UseDoublePrecisionVertices)
tr=[]
for e in M['add']:
 for p in e['parts']:
  g=p['geometry'];v=np.array(g['vertices']);f=g['faces'];N=len(v)//2
  for ff in f:
   if len(ff)==3 and max(ff)<N:tr.append(v[ff])
tr=np.array(tr);top=shapely.union_all(shapely.polygons(tr[:,:,:2]));missing=domain.difference(top).area;outside=top.difference(domain).area;check('exact reconstructed XY terrain coverage',missing<1e-5 and outside<1e-5,missing_m2=missing,outside_m2=outside)
q=tr.reshape(-1,3);foot=(q[:,0]>=0)&(q[:,0]<=13)&(q[:,1]>=0)&(q[:,1]<=11);check('main building terrain below floor',float(q[foot,2].max())<=-.44999,highest_ground_z=float(q[foot,2].max()),main_floor_z=0.0)
pav=(q[:,0]>=.325)&(q[:,0]<=4.595)&(q[:,1]>=-7.135)&(q[:,1]<=-3.565);check('pavilion ground footing grade',np.max(abs(q[pav,2]+.45))<1e-6)
k=(q[:,0]>=7.70)&(q[:,0]<=13.35)&(q[:,1]>=-11.87)&(q[:,1]<=-2.60);check('kitchen ground below retained stone platform',q[k,2].max()<=-.44999,ground_z_max=float(q[k,2].max()),kitchen_platform_z=-.4)
# Exterior gate lower vertices are tested against independent bilinear ramp stations.
ga=np.array([-14.78814941727704,-8.672411229164949]);gb=np.array([-12.691036702414301,-12.516460251600984]);gd=gb-ga;gw=np.linalg.norm(gd);gd/=gw;gin=np.array([-gd[1],gd[0]]);zg=np.array(ramp['gate_ground_Z_line_m']);zr=np.array(ramp['road_edge_Z_corners_m']);zi=np.array(ramp['yard_edge_Z_corners_m'])
def ramp_z(xy):
 uv=np.c_[(xy-ga)@gd,(xy-ga)@gin];t=np.clip(uv[:,0]/gw,0,1);v=uv[:,1];g=zg[0]*(1-t)+zg[1]*t;r=zr[0]*(1-t)+zr[1]*t;i=zi[0]*(1-t)+zi[1]*t;return np.where(v<0,g+(r-g)*np.clip(-v/2,0,1),g+(i-g)*np.clip(v/.90,0,1))
S=json.loads((V/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));ex.SCENE=S
for e in S['elements']:
 if e['name'].startswith('SITE_SW_METAL_ENTRY_GATE_V11__LEAF_'):
  vs=[]
  for p in ex.expand_parts(e):
   v,f=ex.world_part(p,e)
   if v is not None:vs.append(v)
  v=np.concatenate(vs);clear=v[:,2]-ramp_z(v[:,:2]);check(e['name']+' actual closed floor clearance',clear.min()>=.024,minimum_m=float(clear.min()))
steps=[e for e in S['elements'] if e['name'].startswith('ENTRANCE_STEP_')];check('three 150mm entrance steps retained',len(steps)==3 and all(abs(e['parts'][0]['geometry']['origin'][2]+.45)<1e-8 for e in steps));check('terrain global high difference retained',Q['domain_height_m_range'][1]-Q['domain_height_m_range'][0]>10)
# Reference-only source-ground texture companions use exact original JPEG bytes.
texdir=D/'Reference_Textures';texdir.mkdir(exist_ok=True);RF=rh.File3dm.Read(str(D/'Pure_Site_Cleaned_Ground_Reference_ENU.3dm'));textures=[]
for mat in RF.Materials:
 t=mat.GetBitmapTexture()
 if t:
  p=Path(t.FileName);dest=texdir/p.name;shutil.copy2(p,dest);mat.SetBitmapTexture(str(dest));textures.append({'name':mat.Name,'file':dest.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});check(mat.Name+' reference JPEG exact',hashlib.sha256(dest.read_bytes()).hexdigest()==textures[-1]['sha256'])
assert RF.Write(str(D/'Pure_Site_Cleaned_Ground_Reference_ENU.3dm'),8)
# Write an ENU terrain companion as well; primary Scene integration uses double LOCAL arrays.
C=json.loads((V/'02_Data/Coordinate.json').read_text());T=np.array(C['local_to_survey']);trans=rh.Transform.Identity()
for i in range(4):
 for j in range(4):setattr(trans,f'M{i}{j}',float(T[i,j]))
for o in F.Objects:o.Geometry.Transform(trans)
assert F.Write(str(D/'Rebuilt_Terrain_ENU.3dm'),8)
# Geometric height/topology preview, detached from source photographic fragments.
I=Image.new('RGB',(1250,1150),(250,250,247));draw=ImageDraw.Draw(I);lo=np.array([-50.,-48.]);scale=10.4
for t in tr:
 z=t[:,2].mean();n=np.cross(t[1]-t[0],t[2]-t[0]);n/=np.linalg.norm(n)+1e-30;light=.55+.45*abs(n@np.array([-.5,-.4,.768]));a=(z+9)/14;col=np.array([85+80*a,126+30*a,124-65*a])*light;col=tuple(np.clip(col,0,255).astype(int));xy=(t[:,:2]-lo)*scale;xy[:,1]=1100-xy[:,1];draw.polygon([tuple(p) for p in xy],fill=col)
for x in range(-40,70,10):
 px=(x-lo[0])*scale;draw.line([(px,20),(px,1100)],fill=(200,200,194));draw.text((px+2,1110),str(x),fill=(50,50,50))
for y in range(-40,60,10):
 py=1100-(y-lo[1])*scale;draw.line([(0,py),(1200,py)],fill=(200,200,194));draw.text((1202,py),str(y),fill=(50,50,50))
draw.text((10,5),'V12 reconstructed terrain: no imported photogrammetry faces; heights -8.74 ... +5.07 m LOCAL',fill=(20,20,20));I.save(D/'Rebuilt_Terrain_Height_Plan.png')
Q.update({'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','independent_geometry_checks':checks,'xy_projection_residual_m2':missing,'xy_outside_source_plan_m2':outside,'reference_textures':textures,'foundation_ground_grade_m':-.45,'main_floor_grade_m':0.0,'kitchen_stone_platform_top_m':-.40,'main_entrance_steps':'3 x 0.15m vertical, 0.30m tread; V11 preserved','gate_ramp':ramp,'evidence_video_frames':['Ground_L0_0600s_Y+00_P-35.jpg','Ground_L0_0625s_Y+00_P-35.jpg','Ground_L0_0650s_Y+00_P-35.jpg','Ground_L0_0775s_Y+00_P-35.jpg','Ground_L0_0897s_Y+00_P-35.jpg','Ground_L0_0972s_Y+00_P-35.jpg']});(D/'Geometry_QA.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf-8');print(Q['status'],len(checks),'checks','missing',missing,'outside',outside);print([c for c in checks if not c['pass']])
