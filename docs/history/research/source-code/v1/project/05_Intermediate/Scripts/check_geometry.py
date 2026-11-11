import sys,json,csv,math,collections,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'libs'));sys.path.insert(0,str(Path(__file__).parent/'np1'))
import numpy as np,rhino3dm as rh
from export_models import SCENE,OUT,solid_data,triangulate,world_part,expand_parts
issues=[];rows=[];hashes={};duplicates=[];coincident=collections.defaultdict(list);solid_n=0
for e in SCENE['elements']:
 for pi,p in enumerate(expand_parts(e)):
  g=p['geometry'];v,faces=world_part(p,e)
  if v is None or g['type'] in ['surface_polygon','mesh']:continue
  tris=[]
  for face in faces:
   for t in ([range(3)] if len(face)==3 else triangulate(v[face])):tris.append([face[i] for i in t])
  tris=np.array(tris);q=v[tris];area=np.linalg.norm(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]),axis=1)/2;vol=float(np.sum(np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])))/6)
  edges=collections.Counter(tuple(sorted(pair)) for t in tris for pair in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]);bad=sum(n!=2 for n in edges.values());name=e['name']+f'__{pi+1}';solid_n+=1
  if bad or min(area)<1e-10 or vol<=1e-10:issues.append({'part':name,'nonmanifold_edges':bad,'minimum_area':float(min(area)),'signed_volume':vol})
  digest=hashlib.sha256(str(sorted(tuple(pt.round(6)) for pt in v)).encode()).hexdigest()
  if digest in hashes:duplicates.append([hashes[digest],name])
  else:hashes[digest]=name
  for face in faces:
   key=tuple(sorted(tuple(pt.round(6)) for pt in v[face]));coincident[key].append(name)
  rows.append([name,e['layer'],len(tris),vol,bad,float(min(area))])
with (OUT/'09_Report/Solid_Geometry_QA.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Part','Layer','Triangles','SignedVolume_m3','NonManifoldEdges','MinimumTriangleArea_m2']);w.writerows(rows)
coincident_groups=[val for val in coincident.values() if len(val)>1]
# Dimensional validation from saved Rhino geometry rather than source parameter constants.
measure={}
for mode in ['ARCH','VIS']:
 model=rh.File3dm.Read(str(OUT/'06_Rhino'/f'Production_1QK_{mode}.3dm'));bbs=[o.Geometry.GetBoundingBox() for o in model.Objects if o.Attributes.Name.startswith('DOOR_W900_H2100_WOOD_part')];width=max(b.Max.X for b in bbs)-min(b.Min.X for b in bbs)
 measure[mode]={'900mm_door_actual_bbox_m':width,'units':str(model.Settings.ModelUnitSystem),'named_views':len(model.NamedViews),'named_view_valid_camera':all(v.Viewport.IsValidCamera for v in model.NamedViews),'mesh_objects':sum(type(o.Geometry).__name__=='Mesh' for o in model.Objects)}
 assert abs(width-.9)<1e-8
# Numerical roof comparison samples existing photogrammetry; this is not independent survey validation.
data=np.load(OUT/'05_Intermediate/Reality_Geometry.npz');points=data['points'].copy();normals=data['normals'];th=math.radians(SCENE['coordinate']['rotation_deg']);R=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);points-=SCENE['coordinate']['origin'];points[:,:2]=points[:,:2]@R
selected=(points[:,0]>-.8)&(points[:,0]<13.8)&(points[:,1]>-.8)&(points[:,1]<10.6)&(points[:,2]>10.2)&(points[:,2]<12.6)&(abs(normals[:,2])>.75);pp=points[selected];dist=np.full(len(pp),np.inf)
for e in SCENE['elements']:
 if e['layer']!='50_ROOF':continue
 p=np.array(e['parts'][0]['geometry']['profile']);normal=np.cross(p[1]-p[0],p[2]-p[0]);normal=normal/np.linalg.norm(normal)
 for ti in triangulate(p):
  a,b,c=p[ti,:2];area=np.cross(b-a,c-a);u=np.cross(pp[:,:2]-a,c-a)/area;vv=np.cross(b-a,pp[:,:2]-a)/area;inside=(u>=0)&(vv>=0)&(u+vv<=1);dd=abs((pp-p[0])@normal);dist[inside]=np.minimum(dist[inside],dd[inside])
finite=dist[np.isfinite(dist)];roof={'sample_count':len(finite),'median_plane_distance_m':float(np.median(finite)),'p90_plane_distance_m':float(np.quantile(finite,.9)),'maximum_plane_distance_m':float(max(finite)),'scope':'Existing OBJ face centroids, mostly horizontal roof samples inside model roof polygons; no independent GCP or as-built certification'}
inventory=list(csv.DictReader((OUT/'01_Source/Source_Inventory.csv').open(encoding='utf-8-sig')));changed=[]
for r in inventory:
 p=Path(r['Path']);st=p.stat()
 if st.st_size!=int(r['Bytes']) or abs(st.st_mtime-float(r['Modified']))>1e-4:changed.append(str(p))
qa={'solid_parts_tested':solid_n,'invalid_topology_or_negative_volume':issues,'exact_duplicate_solids':duplicates,'coincident_full_polygon_groups':len(coincident_groups),'coincident_full_polygons':coincident_groups,'coincident_scope':'Touching joints, slab segmentation and structural interfaces included. This does not certify Boolean clash freedom or CFD watertightness.','rhino_readback':measure,'roof_comparison':roof,'source_inventory_entries':len(inventory),'source_size_or_mtime_changed':changed,'stair_levels_m':[0,1.95,3.9,5.7,7.5],'stair_final_riser':'Formed by the landing or upper floor; 11 rises and 10 treads per flight.','known_limit':'Separate native solids have intentional structural contacts; building is not a single Boolean union.'}
(OUT/'09_Report/Geometry_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in qa.items() if k not in ['coincident_full_polygons']},indent=2),flush=True)
