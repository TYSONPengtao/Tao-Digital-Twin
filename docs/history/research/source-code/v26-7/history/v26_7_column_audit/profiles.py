from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')];import numpy as np,manifold3d as mf
D=W/'v26_6/Final';J={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};r=J['V26_3_House_Connected_Walls_And_Stairs'];a=np.load(D/r['file']);v,ix=np.unique(a['v'],axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(v.astype(float),ix[a['f']].astype(np.uint64)));out=[]
for fl,base,top in [(1,-.45,3.32),(2,3.45,6.92),(3,7.05,10.02)]:
 for label,z in [('below_sill',base+.3),('under_header',top-.4),('top_header',top-.08)]:
  coords=[]
  for x in np.arange(.25,12.80,.02):
   hs=m.ray_cast([float(x),9.55,z],[float(x),10.1,z]);enter=[h for h in hs if h.normal[1]<-.8];coords.append((float(x),float(enter[0].position[1])if enter else None))
  seg=[]
  for x,y in coords:
   key=round(y,4)if y is not None else None
   if seg and seg[-1]['y']==key:seg[-1]['x'][1]=round(x+.01,4)
   else:seg.append({'x':[round(x-.01,4),round(x+.01,4)],'y':key})
  out.append({'floor':fl,'level':label,'z':z,'segments':seg});print('PROFILE',fl,label,z,seg)
for n in J:
 if n.startswith('WINDOW_BACK_'):print('WINDOW',n,J[n]['bounds'])
(Path(__file__).with_name('Rear_Inner_Face_Profiles.json')).write_text(json.dumps(out,indent=2),encoding='utf8')
