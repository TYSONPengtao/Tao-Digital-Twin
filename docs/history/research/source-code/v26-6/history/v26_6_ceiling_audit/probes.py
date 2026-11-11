from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')];import numpy as np,manifold3d as mf
D=W/'v26_5/Final';J={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};a=np.load(D/J['V26_3_House_Connected_Walls_And_Stairs']['file']);v,ix=np.unique(a['v'],axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(v.astype(float),ix[a['f']].astype(np.uint64)));out=[]
for fl,base,soff,top,nextfloor in [(1,-.45,3.05,3.32,3.45),(2,3.45,6.65,6.92,7.05),(3,7.05,9.95,10.22,10.28)]:
 for edge,axis,center,span in [('east',0,9.1,np.linspace(7.6,9.5,20)),('west',0,3.9,np.linspace(7.6,9.5,20)),('north',1,9.8,np.linspace(4.2,8.8,24)),('south',1,7.3,np.linspace(4.2,8.8,24))]:
  for u in span:
   for z in [soff-.01,soff+.01,top-.001,top+.001,(top+nextfloor)/2,nextfloor-.001,nextfloor+.001]:
    p=np.array([center,u,z]if axis==0 else[u,center,z]);d=np.eye(3)[axis]*40.;hs=m.ray_cast(p-d,p+d);occupied=bool(sum(1 for h in hs if h.position[axis]<p[axis])%2);out.append({'floor':fl,'edge':edge,'u_m':float(u),'z_m':float(z),'occupied':occupied,'hits':[{'p':h.position,'n':h.normal}for h in hs]})
fn=Path(__file__).with_name('Edge_Head_Probes.json');fn.write_text(json.dumps(out,indent=2),encoding='utf8')
for fl,top,nextfloor in [(1,3.32,3.45),(2,6.92,7.05),(3,10.22,10.28)]:
 for edge in ['east','west','north','south']:
  rows=[r for r in out if r['floor']==fl and r['edge']==edge and abs(r['z_m']-(top+nextfloor)/2)<.00001];gaps=[r['u_m']for r in rows if not r['occupied']];print(fl,edge,'band clear',len(gaps),'of',len(rows),'range',([min(gaps),max(gaps)]if gaps else[]))
