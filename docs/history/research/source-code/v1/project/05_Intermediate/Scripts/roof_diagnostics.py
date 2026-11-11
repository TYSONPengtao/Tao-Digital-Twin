import sys,math,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'libs'));sys.path.insert(0,str(Path(__file__).parent/'np1'))
import numpy as np
from PIL import Image,ImageDraw
out=Path(r'E:\jz\JIA\Rebuild');data=np.load(out/'05_Intermediate/Reality_Geometry.npz');p=data['points'].copy();n=data['normals'].copy();a=data['areas'];s=json.loads((out/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));th=math.radians(19.65);R=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);p-=s['coordinate']['origin'];p[:,:2]=p[:,:2]@R;n[:,:2]=n[:,:2]@R
m=(p[:,0]>-1)&(p[:,0]<14)&(p[:,1]>-1)&(p[:,1]<11)&(p[:,2]>10)&(p[:,2]<12.6)&(abs(n[:,2])>.75);p=p[m];n=n[m];a=a[m];im=Image.new('RGB',(1000,820),'white');dr=ImageDraw.Draw(im)
for pt in p[np.argsort(p[:,2])]:
 c=int(np.clip((pt[2]-10)/2.2,0,1)*255);dr.ellipse((50+pt[0]*60,740-pt[1]*60,53+pt[0]*60,743-pt[1]*60),fill=(c,50,255-c))
for x in range(15):dr.text((50+x*60,770),str(x),fill='black')
for y in range(11):dr.text((5,740-y*60),str(y),fill='black')
im.save(Path(__file__).parent/'Roof_Local_Height.png')
for y in np.arange(0,10.5,.5):
 sel=abs(p[:,1]-y)<.15;pp=p[sel];
 if len(pp)>10:print('Y',y,'Zquant',np.quantile(pp[:,2],[.1,.5,.9,.99]).round(3),'RidgeX',np.median(pp[pp[:,2]>np.quantile(pp[:,2],.95),0]).round(3))
print('HIGHROOF',np.quantile(p[p[:,2]>11.8],[0,.1,.5,.9,1],axis=0).round(3))
# Spatially selected major faces: fit z=ax+by+c using repeated trimming to avoid tile/mesh noise.
rois={'east':(10,13,2,8),'west':(3.6,6.5,2,6),'south':(5,10,0,1.7),'north':(4,10,9,10.4),'wing_south':(0,3,6.4,7.5),'wing_north':(0,3,9,10.4)}
for name,(x0,x1,y0,y1) in rois.items():
 sel=(p[:,0]>x0)&(p[:,0]<x1)&(p[:,1]>y0)&(p[:,1]<y1);pp=p[sel];aa=a[sel]
 for i in range(5):
  X=np.column_stack([pp[:,:2],np.ones(len(pp))]);coef=np.linalg.lstsq(X*np.sqrt(aa)[:,None],pp[:,2]*np.sqrt(aa),rcond=None)[0];res=abs(X@coef-pp[:,2]);keep=res<max(.08,np.quantile(res,.8));pp=pp[keep];aa=aa[keep]
 print('PLANE',name,'z=ax+by+c',coef.round(5),'n',len(pp),'med',np.median(res).round(3))
