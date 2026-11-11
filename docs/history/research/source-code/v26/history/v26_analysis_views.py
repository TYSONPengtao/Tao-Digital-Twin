from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]
import numpy as np
from PIL import Image,ImageDraw,ImageFont
D=W/'v26';I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};SI=json.loads((D/'Original_Source_Index.json').read_text('utf8'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
# Exact source photo top view at the outer gate, using original UVs.
lo=np.array([-19.,-17.]);hi=np.array([-8.,-6.]);size=1100;scale=size/(hi-lo)[0];out=np.full((size,size,3),238,np.uint8);zb=np.full((size,size),-np.inf)
for r in SI['rows']:
 a=np.load(D/r['file']);t=a['v'][a['f']];uv=a['uv'];hit=(t[:,:,0].max(1)>=lo[0])&(t[:,:,0].min(1)<=hi[0])&(t[:,:,1].max(1)>=lo[1])&(t[:,:,1].min(1)<=hi[1])&(t[:,:,2].max(1)<1.)&(t[:,:,2].min(1)>-2.0)
 if not hit.any():continue
 tex=np.array(Image.open(r['texture']).convert('RGB'));th,tw=tex.shape[:2]
 for v,u in zip(t[hit],uv[hit]):
  xy=(v[:,:2]-lo)*scale;xy[:,1]=size-xy[:,1];b0=np.maximum(np.floor(xy.min(0)).astype(int),0);b1=np.minimum(np.ceil(xy.max(0)).astype(int)+1,size)
  if np.any(b1<=b0):continue
  A=xy[1]-xy[0];B=xy[2]-xy[0];det=np.cross(A,B)
  if abs(det)<1e-8:continue
  xx,yy=np.meshgrid(np.arange(b0[0],b1[0])+.5,np.arange(b0[1],b1[1])+.5);Q=np.stack([xx-xy[0,0],yy-xy[0,1]],-1);s=(Q[:,:,0]*B[1]-Q[:,:,1]*B[0])/det;w=(A[0]*Q[:,:,1]-A[1]*Q[:,:,0])/det;z=v[0,2]+s*(v[1,2]-v[0,2])+w*(v[2,2]-v[0,2]);zz=zb[b0[1]:b1[1],b0[0]:b1[0]];ok=(s>=-1e-7)&(w>=-1e-7)&(s+w<=1.0000001)&(z>zz)
  qu=u[0]+s[...,None]*(u[1]-u[0])+w[...,None]*(u[2]-u[0]);ix=np.clip((qu[:,:,0]*tw).astype(int),0,tw-1);iy=np.clip(((1-qu[:,:,1])*th).astype(int),0,th-1);out[b0[1]:b1[1],b0[0]:b1[0]][ok]=tex[iy,ix][ok];zz[ok]=z[ok]
im=Image.fromarray(out);dr=ImageDraw.Draw(im)
for x in np.arange(-19,-7):
 px=(x-lo[0])*scale;dr.text((px+3,size-24),str(x),font=font,fill='red')
for y in np.arange(-17,-5):
 py=size-(y-lo[1])*scale;dr.text((3,py-20),str(y),font=font,fill='red')
for n in ['SITE_SW_GATE_POST_0_CORE_Geometry','SITE_SW_GATE_POST_1_CORE_Geometry']:
 r=I[n];a=np.array(r['bounds']);pts=[(a[0,0],a[0,1]),(a[1,0],a[0,1]),(a[1,0],a[1,1]),(a[0,0],a[1,1])];pts=[((x-lo[0])*scale,size-(y-lo[1])*scale) for x,y in pts];dr.polygon(pts,outline='red',width=3)
im.save(D/'Original_Gate_Top.jpg',quality=95)
# Plan sections: built geometry, colour by actual solid.
from shapely.geometry import shape
im=Image.new('RGB',(1500,900),'white');dr=ImageDraw.Draw(im)
for idx,fl in enumerate([1,2,3]):
 ox=idx*500+30;oy=40;scale=75
 for kind,col in [('FACADE_CONTINUOUS','#b4c3d3'),('PARTITIONS_JOINED','#e0bd9a')]:
  z={1:.8,2:4.5,3:8.1}[fl];p=shape(json.loads((D/f'Plan_{kind}_F{fl}_{z}.json').read_text()))
  ps=[p]if p.geom_type=='Polygon'else list(p.geoms)
  for q in ps:
   dr.polygon([(ox+(x-3.3)*scale,oy+(10.25-y)*scale)for x,y in q.exterior.coords],fill=col,outline='black')
 for n,r in I.items():
  if not n.startswith('KZ_') or f'_F{fl}_'not in n:continue
  b=np.array(r['bounds']);x,y=b[:,:2].mean(0)
  if 3.3<x<9.6 and 6.8<y<10.25:dr.rectangle([ox+(b[0,0]-3.3)*scale,oy+(10.25-b[1,1])*scale,ox+(b[1,0]-3.3)*scale,oy+(10.25-b[0,1])*scale],outline='red',width=2)
 for n in [f'STAIR_LANDING_F{min(fl,2)}_Geometry',f'STAIR_F{min(fl,2)}_FLIGHT1_Geometry',f'STAIR_F{min(fl,2)}_FLIGHT2_Geometry']:
  b=np.array(I[n]['bounds']);dr.rectangle([ox+(b[0,0]-3.3)*scale,oy+(10.25-b[1,1])*scale,ox+(b[1,0]-3.3)*scale,oy+(10.25-b[0,1])*scale],outline='blue',width=2)
 dr.text((ox,10),'F'+str(fl)+' actual wall / column / stair plan',font=font,fill='black')
 for x in [3.7,3.8,4.0,4.1,5.2,7.7,7.8,8.1,9.1]:dr.text((ox+(x-3.3)*scale,oy+275),str(x),font=font,fill='black')
 # Flight XZ side view.
 for n,col in [(f'STAIR_F{min(fl,2)}_FLIGHT1_Geometry','#ffb473'),(f'STAIR_F{min(fl,2)}_FLIGHT2_Geometry','#8eb5ee'),(f'STAIR_LANDING_F{min(fl,2)}_Geometry','#8ac48f')]:
  a=np.load(D/I[n]['file']);v=a['v'];floor=[-.45,3.45,3.45][idx]
  for t in v[a['f']]:dr.polygon([(ox+(x-3.3)*scale,oy+730-(z-floor)*95) for x,y,z in t],fill=col,outline=None)
 dr.text((ox,oy+760),'Stair XZ section (all faces projected)',font=font,fill='black')
im.save(D/'Structure_Before_Plans.png')
print('VIEWS_DONE')
