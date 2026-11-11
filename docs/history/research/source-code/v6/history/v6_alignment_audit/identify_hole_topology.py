import sys,json,math,time
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import polygonize,unary_union
O=Path(__file__).parent;M=rh.File3dm.Read(r'E:\jz\纯场地版本.3dm');verts=[];tris=[];offset=0
for ob in M.Objects:
 if type(ob.Geometry).__name__!='Mesh':continue
 m=ob.Geometry;v=np.array([[p.X,p.Y,p.Z] for p in m.Vertices]);f=np.array([list(p) for p in m.Faces],dtype=np.int64);t=f[:,:3];quads=f[f[:,2]!=f[:,3]]
 if len(quads):t=np.vstack([t,quads[:,[0,2,3]]])
 verts.append(v);tris.append(t+offset);offset+=len(v)
v=np.concatenate(verts);t=np.concatenate(tris);rounded=np.round(v,3);unique,first,inv=np.unique(rounded,axis=0,return_index=True,return_inverse=True);p=v[first];t=inv[t];edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);edges.sort(axis=1);edge,count=np.unique(edges,axis=0,return_counts=True);bound=edge[count==1];nonmanifold=int(np.sum(count>2))
lines=[LineString(p[e,:2]) for e in bound if np.linalg.norm(p[e[0],:2]-p[e[1],:2])>1e-6]
anchor=np.array([.9881880024293777,2.9941688308305223]);polys=list(polygonize(lines));containing=[P for P in polys if P.contains(Point(anchor))];best=min(containing,key=lambda p:p.area) if containing else None
report={'method':'Original mesh XYZ positions quantized 0.001m only in analysis index to ignore UV seams; count degree-1 geometric edges and polygonize their ENU XY projection. Source meshes unchanged.','geometric_vertex_count':len(unique),'triangle_count':len(t),'boundary_edge_count':len(bound),'nonmanifold_edge_count':nonmanifold,'polygon_count':len(polys),'containing_anchor_candidates':len(containing),'selected_area_m2':best.area if best else None}
if best:
 th=math.radians(19.65);R=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);org=np.array([-3.45191261,-3.90043098]);enu=np.array(best.exterior.coords);local=(enu-org)@R
 report.update(ENU={'outer':enu[:-1].tolist(),'holes':[[list(q) for q in list(r.coords)[:-1]] for r in best.interiors]},local={'outer':local[:-1].tolist(),'holes':[((np.array(r.coords)-org)@R)[:-1].tolist() for r in best.interiors]})
O.joinpath('Main_Hole_Topological_Polygon.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['ENU','local']},ensure_ascii=False,indent=2))
