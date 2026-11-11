from v23_common import *
O=Path('E:/jz/JIA/Rebuild_V23');NI={r['name']:r for r in json.loads((O/'02_Data/Native_Readback_Index_V23.json').read_text(encoding='utf8'))};Q=json.loads((W/'v23/Mutation.json').read_text(encoding='utf8'));NE={e['name']:e for e in Q['replace']+Q['add']}
def src(n):return uni([manifold(p['geometry']) for p in NE[n]['parts']])
def nat(n):
 d=np.load(O/'02_Data'/NI[n]['file']);v=d['vertices'];f=d['faces'];vv,iv=np.unique(np.round(v,9),axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(vv,iv[f].astype(np.uint64)));print(n,'status',m.status(),'components',len(m.decompose()),'vol',m.volume());return m
j='GATE_V23_LEFT_WALL_JAMB_CLOSURE';jn=nat(j);js=src(j)
for n in ['SITE_V21_GATE_REFERENCE_LAYER_03','SITE_V21_GATE_REFERENCE_LAYER_04']:
 ns=src(n);nn=nat(n);nu=uni(nn.decompose());print('VOLS',ns.volume(),nn.volume(),nu.volume());print('OVERLAPS NS/JS',float((ns^js).volume()),'NN/JS',float((nn^js).volume()),'NU/JS',float((nu^js).volume()),'NS/JN',float((ns^jn).volume()),'NN/JN',float((nn^jn).volume()),'NU/JN',float((nu^jn).volume()));print('symdiff',float((nn-ns).volume()),float((ns-nn).volume()),'JDIFF',float((jn-js).volume()),float((js-jn).volume()))
