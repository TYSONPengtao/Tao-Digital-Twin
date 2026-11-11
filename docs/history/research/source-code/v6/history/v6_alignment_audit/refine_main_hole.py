import sys,json,math,time
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent;raw=json.loads((O/'Main_Hole_Polygon.json').read_text(encoding='utf-8'));P=Polygon(raw['ENU']['outer'],raw['ENU']['holes']);exp=P.buffer(.15);band=P.boundary.buffer(.3);bound=exp.bounds
M=rh.File3dm.Read(r'E:\jz\纯场地版本.3dm');selected=[];selected_vertex_xy=[];counts=[]
for ob in M.Objects:
 if type(ob.Geometry).__name__!='Mesh':continue
 g=ob.Geometry;v=np.array([[p.X,p.Y,p.Z] for p in g.Vertices]);f=np.array([list(x) for x in g.Faces],dtype=np.int32);t=f[:,:3];q=f[f[:,2]!=f[:,3]]
 if len(q):t=np.vstack([t,q[:,[0,2,3]]])
 xyz=v[t];xy=xyz[:,:,:2];lo=xy.min(axis=1);hi=xy.max(axis=1);area=np.abs(np.cross(xy[:,1]-xy[:,0],xy[:,2]-xy[:,0]))/2
 mask=(hi[:,0]>=bound[0])&(lo[:,0]<=bound[2])&(hi[:,1]>=bound[1])&(lo[:,1]<=bound[3])&(area>1e-12);qxy=xy[mask];shapes=shapely.polygons(qxy);keep=shapely.intersects(shapes,exp);ss=shapes[keep];selected.extend(ss.tolist());selected_vertex_xy.extend(qxy[keep]);counts.append({'mesh_id':str(ob.Attributes.Id),'triangles':len(t),'bbox_candidate':int(mask.sum()),'expanded_candidate_intersections':len(ss)})
coverage=unary_union(selected);free=exp.difference(coverage);candidate_polys=list(free.geoms) if hasattr(free,'geoms') else [free];anchor=Point(raw['anchor_enu_xy']);matches=[q for q in candidate_polys if q.geom_type=='Polygon' and q.contains(anchor)]
if len(matches)!=1:raise ValueError('Expected exactly one free polygon containing centre: '+str(len(matches)))
H=matches[0];theta=math.radians(19.65);R=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);origin=np.array([-3.45191261,-3.90043098]);enuxy=np.array(H.exterior.coords);local=(enuxy-origin)@R
report={'source':raw['source'],'method':'Raster candidate expanded by 0.15m; exact original source triangle XY union subtracted. Full expanded-region overlap proof includes internal source islands in addition to boundary +/-0.30m refinement. Choose remaining free polygon containing V5 centre.','source_base_unchanged':True,'alignment':'same ENU frame; only donor V5 local transforms back to ENU','boundary_clip_status':'EXACT_SOURCE_TRIANGLE_XY_EDGE_WITHIN_REVIEWED_MAIN_VOID','original_candidate_area_m2':P.area,'refined_area_m2':H.area,'boundary_vertices':len(enuxy)-1,'inner_ring_count':len(H.interiors),'selected_source_triangles':len(selected),'per_mesh_selection':counts,'positive_overlap_with_selected_original_coverage_m2':H.intersection(coverage).area,'distance_to_expanded_candidate_boundary_m':H.boundary.distance(exp.boundary),'anchor_enu_xy':raw['anchor_enu_xy'],'anchor_local_xy':raw['anchor_local_xy'],'ENU':{'outer':enuxy[:-1].tolist(),'holes':[[list(q) for q in list(r.coords)[:-1]] for r in H.interiors]},'local':{'outer':local[:-1].tolist(),'holes':[((np.array(r.coords)-origin)@R)[:-1].tolist() for r in H.interiors]},'note':'2D surgical patch ROI, retain original base unchanged, retain donor real openings. This does not assert a measured legal site boundary or a fully watertight 3D seam.'}
O.joinpath('Refined_Main_Hole_Polygon.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# Detail plot: exact clipped free contour and selected original projected triangles.
img=Image.new('RGB',(2000,1550),'white');D=ImageDraw.Draw(img);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',31);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23);xx,yy,xx1,yy1=Polygon(local).bounds;scale=min(1720/(xx1-xx),1180/(yy1-yy));left=130;bottom=1350
pix=lambda p:(left+(p[0]-xx)*scale,bottom-(p[1]-yy)*scale)
for q in selected_vertex_xy:
 qq=(q-origin)@R;D.polygon([pix(p) for p in qq],fill=(186,205,215))
base_local=(np.array(P.exterior.coords)-origin)@R;D.line([pix(p) for p in base_local],fill=(175,170,170),width=2);D.line([pix(p) for p in local],fill=(221,48,32),width=4)
for x in [0,3.9,9.1,13]:D.line([pix((x,0)),pix((x,9.8))],fill=(109,60,155),width=2)
for y in [0,2.1,7.3,9.8]:D.line([pix((0,y)),pix((13,y))],fill=(109,60,155),width=2)
D.text((70,22),'主要空洞精化边界：沿原实景三角面投影贴边',font=font,fill=(30,40,60));D.text((70,76),f'红=精化孔界  浅蓝=原实景面  灰=初候选；面积{H.area:.3f}m²，与原覆盖重叠{H.intersection(coverage).area:.6f}m²',font=small,fill=(60,75,90));D.text((70,1470),'原底5网格、vertices、faces、UV、材质原样保留；只将旧模型补块裁剪到孔内。',font=small,fill=(95,60,40));img.save(O/'Refined_Main_Hole_Local_Overlay.png')
print(json.dumps({k:v for k,v in report.items() if k not in ['ENU','local']},ensure_ascii=False,indent=2))
