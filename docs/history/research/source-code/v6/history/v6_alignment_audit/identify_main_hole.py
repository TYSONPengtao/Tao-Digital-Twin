import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh,cv2
from scipy.ndimage import label,binary_fill_holes
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Polygon,Point
from shapely.affinity import rotate,translate
O=Path(__file__).parent;M=rh.File3dm.Read(r'E:\jz\纯场地版本.3dm');res=.05
allv=[];data=[]
for ob in M.Objects:
 if type(ob.Geometry).__name__!='Mesh':continue
 g=ob.Geometry;v=np.array([[p.X,p.Y,p.Z] for p in g.Vertices]);faces=np.array([list(f) for f in g.Faces],dtype=np.int32);allv.append(v);data.append((v,faces))
allv=np.concatenate(allv);lo=allv[:,:2].min(axis=0)-.5;hi=allv[:,:2].max(axis=0)+.5;size=np.ceil((hi-lo)/res).astype(int)+1;I=Image.new('1',(int(size[0]),int(size[1])));D=ImageDraw.Draw(I)
for v,faces in data:
 q=np.column_stack([(v[:,0]-lo[0])/res,(hi[1]-v[:,1])/res]);q=np.rint(q).astype(int)
 for f in faces:
  ids=f[:3] if f[3]==f[2] else f
  D.polygon([tuple(p) for p in q[ids]],fill=1)
mask=np.array(I,dtype=bool);labels,n=label(~mask);theta=math.radians(19.65);R=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);origin=np.array([-3.45191261,-3.90043098]);anchor=np.array([6.5,5.0])@R.T+origin;xp=int(round((anchor[0]-lo[0])/res));yp=int(round((hi[1]-anchor[1])/res));which=int(labels[yp,xp]);target=(labels==which) if which else np.zeros(mask.shape,bool)
# Build contour of the selected missing region. Remove only subpixel speckles in the polygon; base remains untouched.
contours,_=cv2.findContours(target.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);contour=max(contours,key=cv2.contourArea);coords=np.column_stack([lo[0]+contour[:,0,0]*res,hi[1]-contour[:,0,1]*res]);P=Polygon(coords).buffer(0);P=P.simplify(.08,preserve_topology=True)
local=(np.array(P.exterior.coords)-origin)@R
report={'source':r'E:\jz\纯场地版本.3dm','method':'All mesh faces projected to ENU XY raster; selected uncovered connected component at V5 building centre. No source mesh modification.','raster_resolution_m':res,'anchor_local_xy':[6.5,5.0],'anchor_enu_xy':anchor.tolist(),'component_id':which,'component_count':n,'touches_raster_border':bool(np.any(target[0]) or np.any(target[-1]) or np.any(target[:,0]) or np.any(target[:,-1])),'uncovered_pixel_area_m2':float(target.sum()*res**2),'candidate_polygon_area_m2':P.area,'candidate_status':'CANDIDATE_2D_VOID_EXTENT; REVIEW_WITH_SCREENSHOT_AND_3D_BOUNDARY','ENU':{'outer':[list(p) for p in list(P.exterior.coords)[:-1]],'holes':[[list(p) for p in list(r.coords)[:-1]] for r in P.interiors]},'local':{'outer':local[:-1].tolist(),'holes':[]},'strict_clip_note':'The raster-derived polygon is approximate. Conservative inward clipping avoids modifying valid original faces. Preserve base faces, vertices, UV/material indices and textures; append repair as separate geometry. Real doors/windows are retained in donor model.'}
O.joinpath('Main_Hole_Polygon.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');I.convert('L').save(O/'Pure_XY_Face_Coverage.png');Image.fromarray((target*255).astype('uint8')).save(O/'Main_Hole_Raster_Mask.png')
# Registration / missing-area plot in model local coordinates.
img=Image.new('RGB',(1800,1400),'white');draw=ImageDraw.Draw(img);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21);left=100;bottom=1260;scale=29;x0=-30;y0=-25
pix=lambda p:(left+(p[0]-x0)*scale,bottom-(p[1]-y0)*scale)
q=(allv[:,:2]-origin)@R
for p in q[::max(1,len(q)//180000)]:
 x,y=pix(p)
 if 0<=x<1800 and 120<=y<1320:img.putpixel((int(x),int(y)),(135,171,190))
draw.polygon([pix(p) for p in local],outline=(220,61,43),width=4)
for x in [0,3.9,9.1,13]:draw.line([pix((x,0)),pix((x,9.8))],fill=(130,75,160),width=3)
for y in [0,2.1,7.3,9.8]:draw.line([pix((0,y)),pix((13,y))],fill=(130,75,160),width=3)
A=pix((6.5,5));draw.ellipse((A[0]-6,A[1]-6,A[0]+6,A[1]+6),fill=(30,40,60));draw.text((60,25),'主要空洞候选（红）与 V5 主建筑轴网（紫）',font=font,fill=(30,45,60));draw.text((60,70),f'原实景面XY投影覆盖分析，网格{res:g}m；空洞候选面积{P.area:.1f}m²；底网格只读。',font=small,fill=(65,75,90));draw.text((60,1325),'此为补块裁剪范围候选；最终贴边须参考原三维边界，不改变原faces、UV、材质和坐标。',font=small,fill=(100,55,30));img.save(O/'Main_Hole_Local_Overlay.png')
print(json.dumps({k:v for k,v in report.items() if k not in ['ENU','local']},ensure_ascii=False,indent=2))
