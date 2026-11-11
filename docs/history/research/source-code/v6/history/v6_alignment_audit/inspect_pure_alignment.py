# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh
from scipy.spatial import cKDTree
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent;P=Path(r'E:\jz\纯场地版本.3dm');M=rh.File3dm.Read(str(P));pts=[];details=[]
for ob in M.Objects:
 g=ob.Geometry
 if type(g).__name__!='Mesh':continue
 v=np.array([[p.X,p.Y,p.Z] for p in g.Vertices]);pts.append(v);details.append({'name':ob.Attributes.Name,'id':str(ob.Attributes.Id),'vertices':len(v),'faces':len(g.Faces),'uv_count':len(g.TextureCoordinates),'bounds':[v.min(axis=0).tolist(),v.max(axis=0).tolist()]})
new=np.concatenate(pts);oldp=[]
for p in Path(r'E:\jz\JIA\Productions\Production_OBJ (2)\Data').rglob('*.obj'):
 oldp.extend([[float(q) for q in l.split()[1:4]] for l in p.open(encoding='utf-8') if l.startswith('v ')])
old=np.array(oldp);tree=cKDTree(old);idx=np.linspace(0,len(new)-1,min(10000,len(new)),dtype=int);dist,near=tree.query(new[idx],workers=4)
# Treat the suspected same-frame relation explicitly, report distribution, do not fit any transform.
report={'new_mesh_path':str(P),'new_mesh_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'units':str(M.Settings.ModelUnitSystem),'meshes':details,'combined_bounds':[new.min(axis=0).tolist(),new.max(axis=0).tolist()],'sample_count':len(idx),'nearest_old_raw_obj_distance_m':dict(zip(['min','p50','p90','p95','p99','max'],np.quantile(dist,[0,.5,.9,.95,.99,1]).tolist())),'fractions_within_m':{str(x):float(np.mean(dist<x)) for x in [.00001,.001,.01,.05,.10]},'raw_frame_assessment':'PENDING','not_modified':True}
report['raw_frame_assessment']='SAME_ENU_FRAME_SUPPORTED' if np.mean(dist<.001)>.95 else 'SAME_ENU_RANGE_BUT_REGISTRATION_NEEDS_REVIEW'
O.joinpath('New_Pure_Mesh_Alignment.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');np.savez(O/'Alignment_Samples.npz',new=new[idx],old_nearest=old[near],distance=dist)
# Density overlay only for registration: grey old raw, blue pure raw; transform both identically to V5 local.
th=math.radians(19.65);R=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);org=np.array([-3.45191261,-3.90043098,TAO_PRIVATE_SITE_002]);lo=old-org;lo[:,:2]=lo[:,:2]@R;ln=new-org;ln[:,:2]=ln[:,:2]@R
im=Image.new('RGB',(2000,1600),'white');D=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',30);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23);x0,y0,x1,y1=-30,-30,30,25;scale=24.;left=180;bottom=1450
D.text((90,25),'纯场地版本 / 旧CC OBJ / V5网格：同坐标俯视对齐审查',font=font,fill=(30,45,60));D.text((90,75),'灰=旧CC  蓝=纯场地版本  红=V5建筑轴网；双方仅在检查图中做相同ENU→local变换。',font=small,fill=(75,80,90))
def pix(v):return (int(left+(v[0]-x0)*scale),int(bottom-(v[1]-y0)*scale))
for cloud,color in [(lo,(187,187,187)),(ln,(62,111,152))]:
 for v in cloud[::max(1,len(cloud)//220000)]:
  if x0<v[0]<x1 and y0<v[1]<y1:
   x,y=pix(v);im.putpixel((x,y),color)
for x in [0,3.9,9.1,13]:
 a=pix((x,0));b=pix((x,9.8));D.line([a,b],fill=(197,55,39),width=3);D.text((a[0]-20,a[1]+15),f'X{x:g}',font=small,fill=(150,45,30))
for y in [0,2.1,7.3,9.8]:D.line([pix((0,y)),pix((13,y))],fill=(197,55,39),width=3)
D.text((90,1520),f"Sample nearest distances (m): P50={np.median(dist):.7f}; P95={np.quantile(dist,.95):.7f}; within 1mm={np.mean(dist<.001):.2%}",font=small,fill=(45,60,70));im.save(O/'Pure_vs_OldCC_vs_V5_Registration_Plan.png')
print(json.dumps(report,ensure_ascii=False,indent=2))

