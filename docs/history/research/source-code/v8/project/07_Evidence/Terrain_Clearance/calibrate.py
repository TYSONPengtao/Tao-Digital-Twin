import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
from PIL import Image,ImageDraw
from shapely.geometry import Polygon
out=W/'v8_terrain_clear'
pts=[([-11.5,-5.9,2],[498,714]),([-6.6,-5.9,2],[613,718]),([-6.6,-10.4,2],[611,824]),([-11.5,-10.4,2],[496,820]),([3.1,10.6,10.5],[871,341]),([13.8,10.6,10.5],[1159,343]),([13.8,.6,10.5],[1144,603]),([3.1,.6,10.5],[864,597]),([-.7,-2.7,2.54],[754,651]),([4.15,-2.7,2.54],[874,657]),([4.15,-7.3,2.54],[870,763]),([-.7,-7.3,2.54],[752,757])]
world=np.array([p[0]+[1] for p in pts]);pix=np.array([p[1] for p in pts]);rows=[]
for x,(u,v) in zip(world,pix):
 rows.append(np.concatenate([x,np.zeros(4),-u*x]));rows.append(np.concatenate([np.zeros(4),x,-v*x]))
_,s,V=np.linalg.svd(np.array(rows));P=V[-1].reshape(3,4);P/=P[2,3];q=world@P.T;yp=q[:,:2]/q[:,2:];print('RMS',np.sqrt(((yp-pix)**2).sum(1).mean()),'errors',np.round(np.linalg.norm(yp-pix,axis=1),2).tolist());print(P)
red=[[758,306],[746,316],[712,328],[687,337],[625,351],[568,376],[503,393],[438,406],[366,427],[315,446],[283,474],[273,496],[273,551],[283,578],[303,597],[317,636],[341,676],[347,701],[378,745],[423,775],[455,802],[488,818],[528,824],[592,824],[647,835],[700,844],[729,841],[750,834],[750,807],[742,780],[730,755],[728,696],[733,619],[735,560],[749,505],[751,442],[757,393],[758,353]]
zg=-.35;G=np.column_stack([P[:,0],P[:,1],P[:,2]*zg+P[:,3]]);r=np.column_stack([np.array(red),np.ones(len(red))])@np.linalg.inv(G).T;xy=r[:,:2]/r[:,2:];poly=Polygon(xy);print('bounds',poly.bounds,'area',poly.area,'xy',np.round(xy,3).tolist())
meta={'source_screenshot':r'D:\Desktop\新建文件夹\屏幕截图 2026-10-09 001456.jpg','landmarks':[{'local_xyz':p[0],'pixel':p[1]} for p in pts],'projective_camera_fit':P.tolist(),'fit_rms_pixels':float(np.sqrt(((yp-pix)**2).sum(1).mean())),'annotation_pixels':red,'annotation_ground_z_for_mapping_m':zg,'raw_local_polygon':xy.tolist(),'note':'Manual screenshot calibration; boundary is a task editing mask, not surveying control. Ground interpolation follows measured source ground heights.'}
(out/'Redline_Calibration.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
im=Image.open(meta['source_screenshot']).convert('RGB');d=ImageDraw.Draw(im)
for pp,est in zip(pix,yp):d.ellipse((est[0]-5,est[1]-5,est[0]+5,est[1]+5),fill='lime')
d.line(red+[red[0]],fill='yellow',width=3);im.save(out/'Redline_Calibration_Overlay.png')
