from v26_2_common import *
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
D=W/'v26_10';FD=D/'Final';BD=W/'v26_9/Final';ch=json.loads(Path('E:/jz/JIA/Rebuild_V26_10/Reports/V26_10_Changes.json').read_text('utf8'));J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};BJ={r['name']:r for r in json.loads((BD/'Geometry_Index.json').read_text('utf8'))}
for n,mask in [('V26_3_House_Connected_Walls_And_Stairs',union([cube([q['center_x']-.3601,7.0299,[-.44999998807907104,3.450024366378784,7.050000190734863][q['floor']-1]-.0001],[q['center_x']+.3601,7.5701,[3.32,6.92,10.220000267][q['floor']-1]+.0001])for q in ch['proof']['walls']['corrections']]+[cube([8.9798,7.3998,-.4501],[9.0002,9.5601,3.3201])])),('V26_1_Photo_Referenced_Continuous_Wood_Railing',cube([7.76,8.59,7.03],[8.,9.59,8.61]))]:
 a=np.load(FD/J[n]['file']);b=np.load(BD/BJ[n]['file']);ma=solid(a['v'],a['f']);mb=solid(b['v'],b['f']);print('DIFF',n,flush=True)
 for label,d in [('add',(ma-mb)-mask),('remove',(mb-ma)-mask)]:
  ds=sorted(d.decompose(),key=lambda x:x.volume(),reverse=True);print(label,d.volume(),len(ds),[(p.volume(),p.bounding_box())for p in ds[:8]],flush=True)
 # Source-to-new nearest vertices are only diagnostics; new vertices may lie on source faces.
from scipy.spatial import cKDTree
motion=json.loads((FD/'Gate_Leaf_Motion.json').read_text('utf8'))
for n,r in motion.items():
 a=np.load(FD/r['file']);v,f=a['v'],a['f'];e=np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);g=coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(len(v),len(v)));count,labels=connected_components(g,directed=False);_,ec=np.unique(np.sort(e,axis=1),axis=0,return_counts=True);print('LEAF',n,len(v),len(f),'components',count,'badedges',np.count_nonzero(ec!=2),flush=True)
 bad=[];parts=[]
 for i in range(count):
  fs=f[labels[f[:,0]]==i]
  try:parts.append(solid(v,fs,n))
  except Exception as ex:bad.append([len(fs),str(ex)])
 print('PARTS',len(parts),bad,flush=True)
