from v26_2_common import *
from collections import defaultdict
D=W/'v26_15';I=D/'Input';J=json.loads((I/'Source_Index.json').read_text('utf8'));ix={r['name']:r for r in J['objects']};cache={}
def get(n):
 if n not in cache:
  r=ix[n];a=np.load(I/r['file']);cache[n]=(r,a,solid(a['v'],a['f'],n))
 return cache[n]
HN='V26_3_House_Connected_Walls_And_Stairs';GN='V26_2_Continuous_Ground_And_Perimeter_Shell';SN='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';CN='V26_7_Inner_Gate_Rear_Return_Closure'
r,a,h=get(HN);t=a['v'][a['f']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(n,axis=1)/2;n/=np.maximum(2*area[:,None],1e-30);c=t.mean(1)
planes=defaultdict(list)
mask=(c[:,0]>3.9)&(c[:,0]<9.11)&(c[:,1]>7.3)&(c[:,1]<9.81)&(c[:,2]>-.45)&(c[:,2]<10.25)
for k in np.flatnonzero(mask):
 axis=int(np.argmax(abs(n[k])))
 if abs(n[k,axis])<.99999:continue
 # Small near-wall faces and any exposed horizontal projection on wall corners.
 if not((axis==0 and (3.99<c[k,0]<4.16 or 8.84<c[k,0]<9.01))or(axis==1 and (9.55<c[k,1]<9.71 or 7.3<c[k,1]<7.58))or(axis==2 and (c[k,0]<4.16 or c[k,0]>8.84) and c[k,1]>7.3)):continue
 planes[(axis,round(float(c[k,axis]),6),int(np.sign(n[k,axis])),r['materials'][a['mi'][k]])].append(k)
rows=[]
for key,ids in planes.items():
 tt=t[ids];rows.append({'plane':key,'triangles':len(ids),'area':float(area[ids].sum()),'bounds':[tt.min((0,1)).tolist(),tt.max((0,1)).tolist()]})
(D/'Stair_Planes.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
for row in rows:
 if row['area']<.15 or row['plane'][0]==2:print('STAIR',row,flush=True)
print('STAIR_SECTIONS',flush=True)
for z in[.5,1.6,2.0,2.5,3.0,3.1,3.3,3.36,3.44,3.46,3.6,4.,4.6,5.4,6.,6.7,7.0,7.06,7.2,8.,9.9]:
 sl=h^cube([3.95,9.54,z],[4.13,9.79,z+.002]);me=sl.to_mesh64();vv=np.array(me.vert_properties[:,:3]);print('CORNER_SLICE',z,sl.volume(),[vv.min(0).tolist(),vv.max(0).tolist()]if len(vv)else None,flush=True)
gr,ga,g=get(GN);sr,sa,s=get(SN);cr,ca,cl=get(CN);floor=[]
for x in np.arange(8.1,9.41,.1):
 for y in np.arange(-11.55,-10.99,.025):
  vals={}
  for label,m in [('ground',g),('closure',cl),('wall',s)]:
   hits=m.ray_cast([x,y,.15],[x,y,-.9]);vals[label]=[{'z':q.position[2],'normal':list(q.normal)}for q in hits]
  floor.append({'x':float(x),'y':float(y),**vals})
(D/'Gate_Floor_Profile.json').write_text(json.dumps(floor,indent=2),'utf8')
for label,m in [('ground',g),('closure',cl),('wall',s)]:
 for x in[8.2,8.5,8.8,9.1,9.35]:
  hits=m.ray_cast([x,-10.9,-.35],[x,-11.65,-.35]);print('GATE_HORIZONTAL',label,x,[{'p':list(q.position),'n':list(q.normal)}for q in hits],flush=True)
print('FOCUSED_DONE',flush=True)
