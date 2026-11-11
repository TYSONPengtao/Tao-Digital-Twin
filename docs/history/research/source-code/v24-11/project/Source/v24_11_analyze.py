import sys,json,math,subprocess
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W/'v8_interior/plotlibs')]
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=W/'v24_11';rows=json.loads((D/'Inventory.json').read_text(encoding='utf8'))
for r in rows:
 if any(s in r['name']for s in ['MASONRY','SCREENWALL','GATE_REFERENCE_LAYER_01','GATE_REFERENCE_LAYER_02','GATE_REFERENCE_LAYER_03','Kitchen_Rear','Upper_Return','Rear_Drain']):print(r['name'],r['bounds'],r['materials'])
out=[]
for name in ['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry','SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry']:
 d=np.load(D/(name+'.npz'));v,inv=np.unique(np.round(d['v'],5),axis=0,return_inverse=True);f=inv[d['f']];e=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);G=coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(len(v),len(v)));N,lab=connected_components(G,directed=False)
 comps=[]
 for i in range(N):
  vv=v[lab==i];comps.append({'i':i,'nv':len(vv),'bounds':[vv.min(0).tolist(),vv.max(0).tolist()]})
 out.append({'name':name,'components':comps});print(name,N,'COMPONENTS')
 if N<15:print(comps)
 if 'MASONRY'in name:
  fig,ax=plt.subplots(figsize=(12,12));tri=v[f]
  for t in tri:
   if t[:,0].max()<12.8:continue
   pp=np.vstack([t,t[0]]);ax.plot(pp[:,0],pp[:,1],c=plt.cm.viridis(np.clip((np.mean(t[:,2])+.4)/4.7,0,1)),lw=.8)
  p=json.loads((W/'v24_10/AsBuilt_Plan.json').read_text())['outline'];p=np.array(p+[p[0]]);ax.plot(p[:,0],p[:,1],'k--',lw=2);ax.set_aspect('equal');ax.set_xlim(11,22);ax.set_ylim(-18,-7);ax.grid();fig.savefig(D/'Existing_Storage_Masonry_Plan.png',dpi=130);plt.close(fig)
 if 'ASSEMBLY'in name:
  vv=v[(v[:,2]<1.8)&(v[:,1]<-15.05)];fig,ax=plt.subplots(figsize=(12,4));ax.scatter(vv[:,0],vv[:,1],s=4);ax.grid();ax.set_aspect('equal');fig.savefig(D/'Existing_Veranda_Column_Plan.png',dpi=140);plt.close(fig)
(D/'Components.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
FF='C:/Users/PENG/anaconda3/Library/bin/ffmpeg.exe';(D/'Video').mkdir(exist_ok=True)
for t,y,p in [(12,-40,5),(18,-40,8),(24,-45,10),(34,35,12)]:
 n=f'MP4_{t:02d}s_Y{y:+04d}_P{p:+03d}.jpg';vf=f'v360=input=e:output=flat:yaw={y}:pitch={p}:h_fov=110:v_fov=90:w=1200:h=1000';r=subprocess.run([FF,'-v','error','-threads','3','-ss',str(t),'-i','E:/VID_20260507_152114_00_001.mp4','-frames:v','1','-vf',vf,'-q:v','2','-y',str(D/'Video'/n)],capture_output=True);assert r.returncode==0,r.stderr;print('VIDEO',n,flush=True)
