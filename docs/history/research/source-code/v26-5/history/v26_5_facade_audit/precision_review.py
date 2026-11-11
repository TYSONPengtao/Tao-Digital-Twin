from pathlib import Path
import sys,json
W=Path(__file__).resolve().parent.parent;sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
from shapely.geometry import Polygon
FD=W/'v26_5/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};r=J['V26_3_House_Connected_Walls_And_Stairs'];a=np.load(FD/r['file']);v=a['v'];f=a['f'];tr=v[f];norm=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);ar=np.linalg.norm(norm,axis=1)/2
key={};collisions=[];exact={};dups=[]
for i,t in enumerate(tr):
 k=tuple(sorted(map(tuple,np.round(t,7))));e=tuple(sorted(map(tuple,t)))
 if k in key:collisions.append((key[k],i))
 if e in exact:dups.append((exact[e],i))
 key[k]=i;exact[e]=i
edges=np.sort(np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);un,ct=np.unique(edges,axis=0,return_counts=True)
items=[]
for i,j in collisions:
 ni=norm[i]/(2*ar[i]);nj=norm[j]/(2*ar[j]);axis=int(np.argmax(abs(ni)));xy=[k for k in range(3)if k!=axis];p=Polygon(tr[i][:,xy]);q=Polygon(tr[j][:,xy]);intersection=p.intersection(q)
 items.append(dict(indices=[i,j],areas_m2=[ar[i],ar[j]],shared_vertex_indices=list(set(f[i])&set(f[j])),shared_triangle_edges=1 if len(set(f[i])&set(f[j]))==2 else 0,normal_dot=float(ni@nj),projection_axes=xy,projected_intersection_area_m2=float(intersection.area),intersection_geometry=intersection.wkt,triangles_m=tr[[i,j]].tolist(),seven_decimal_vertices_m=np.round(tr[[i,j]],7).tolist()))
print(json.dumps({'dtype':str(v.dtype),'all_stored_coordinates_are_exact_float32_values':bool(np.array_equal(v,v.astype(np.float32).astype(v.dtype))),'triangles':len(f),'exact_coordinate_duplicate_pairs':dups,'seven_decimal_collisions':len(collisions),'non_two_incidence_indexed_edges':int((ct!=2).sum()),'minimum_triangle_area_m2':float(ar.min()),'collision_details':items},indent=2,default=lambda v:int(v)if isinstance(v,np.integer)else str(v)))
