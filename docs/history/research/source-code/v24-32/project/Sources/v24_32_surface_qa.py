"""Independent vertical surface audit of the saved model export."""
import sys,json,hashlib,itertools
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
D=W/'v24_32';O=Path('E:/jz/JIA/Rebuild_V24_32');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_32.blend';I={r['name']:r for r in json.loads((D/'Final_Geometry_Index.json').read_text('utf8'))};B={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
def facepoly(row,axis,coordinate,sign,window=None,visible=False):
 a=np.load(D/row['file']);t=a['v'][a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);mag=np.linalg.norm(no,axis=1);unit=no/np.maximum(mag[:,None],1e-20);mask=(unit[:,axis]*sign>.999999)&(np.max(abs(t[:,:,axis]-coordinate),axis=1)<2e-5)
 if visible:mask&=a['visible']
 dims=[q for q in range(3)if q!=axis];ps=[]
 for q in t[mask][:,:,dims]:
  p=Polygon(q)
  if p.area>1e-11:ps.append(p)
 g=unary_union(ps)
 return g.intersection(window)if window is not None else g
# Exact duplicated outside faces at the three formerly overlapping joints.
for fl,side in [(2,'L'),(2,'R'),(3,'R')]:
 floor={2:3.450024414,3:7.05}[fl];x0=0 if side=='L'else 9.1;region=box(x0+.8,floor-.20,x0+3.1,floor+.12);panel=f'V24_31_F{fl}_Complete_Bay_Underwindow_Walls';lower=f'FACADE_CONTINUOUS_F{fl-1}_Geometry'
 before=facepoly(B[panel],1,1.,-1,region).intersection(facepoly(B[lower],1,1.,-1,region)).area
 after=facepoly(I[panel],1,1.,-1,region).intersection(facepoly(I[lower],1,1.,-1,region)).area
 ck('Shared exterior bay joint face removed '+str((fl,side)),before>.02 and after<1e-7,before_duplicate_area_m2=before,after_duplicate_area_m2=after)
# Audit all visible vertical partners on the marked facade and stair planes.
planes=[(0,-.104,-1,'west facade'),(0,13.104,1,'east facade'),(1,9.904,1,'rear facade'),(1,1.,-1,'bay front'),(0,4.,1,'stair left wall'),(1,9.7,-1,'stair rear wall'),(1,7.4,1,'stair front wall')]
for ax,co,sg,label in planes:
 groups={}
 for n,row in I.items():
  if not n.startswith(('FACADE','PARTITIONS','HOUSE_V21','HOUSE_V22','SLAB','BEAM','KZ','V24_31_F','CONSTRUCTION_SILL')):continue
  g=facepoly(row,ax,co,sg,visible=True)
  if not g.is_empty and g.area>1e-8:groups[n]=g
 collisions=[]
 for a,b in itertools.combinations(groups,2):
  overlap=groups[a].intersection(groups[b]).area
  if overlap>2e-6:collisions.append({'objects':[a,b],'duplicate_m2':overlap})
 ck('Saved exposed plane has no duplicate face owners / '+label,not collisions,partners=len(groups),duplicate_faces=collisions)
# Full geometry has both the former sill and panel in one closed owner,
# rather than a second mesh whose depth happens to hide an overlap.
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'))
ck('All 15 obsolete bay sill meshes integrated into the complete panels',len([n for n in prep['remove']if n.startswith('CONSTRUCTION_SILL_BAY')])==15)
ck('Both standalone floor fascia meshes retired',all(n not in I for n in ['FLOOR_FASCIA_CONTINUOUS_F2_Geometry','FLOOR_FASCIA_CONTINUOUS_F3_Geometry']))
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
failed=[r for r in checks if not r['pass']];(R/'V24_32_Surface_QA.json').write_text(json.dumps({'status':'PASS_SAVED_VERTICAL_SURFACE_OWNERSHIP'if not failed else'FAIL','model_sha256':h,'scope':'Marked axis-aligned exterior bay joints, exterior finish planes and all three stair blank wall planes; exposed same-facing triangles only. Not a claim about every hidden legacy face in the full site.','checks':checks,'failures':failed},ensure_ascii=False,indent=2),encoding='utf8');print('V32_SURFACE_QA',len(checks),'FAIL',len(failed),flush=True)
