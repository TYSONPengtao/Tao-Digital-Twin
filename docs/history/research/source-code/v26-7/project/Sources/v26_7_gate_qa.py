from v26_2_common import *
import hashlib
FD=W/'v26_7/Final';OD=W/'v26_6/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};OJ={r['name']:r for r in json.loads((OD/'Geometry_Index.json').read_text('utf8'))};checks=[]
def ck(n,b,**kw):checks.append({'check':n,'pass':bool(b),**kw});print('CHECK',n,bool(b),kw if not b else'',flush=True)
def get(n):
 a=np.load(FD/J[n]['file']);return a,solid(a['v'],a['f'],n)
n='SITE_V21_GATE_REFERENCE_LAYER_01_Geometry';a,stone=get(n);tops=[]
for x in[5.6,6.,6.6,7.2,7.6]:
 for y in[-11.9,-11.7,-11.4]:
  hs=stone.ray_cast([x,y,0.],[x,y,-.7]);tops.append(max((float(h.position[2])for h in hs if h.normal[2]>.9),default=-999.))
ck('Single closed stone threshold has a continuous low top at the fitted model datum',len(stone.decompose())==1 and all(abs(z+.5)<2e-6 for z in tops),top_samples_m=tops,nominal_rise_over_current_court_m=.1,dimensions_are_model_fit_not_site_measurements=True)
bad=[]
for n in ['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_03_Geometry','V24_07_Gate_Moulded_Timber_Jambs','GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS_Geometry','SITE_V20_INNER_GATE__LEAF_L_Geometry','SITE_V20_INNER_GATE__LEAF_R_Geometry']:
 a=np.load(FD/J[n]['file']);o=np.load(OD/OJ[n]['file']);upper=o['v'][:,2]>=.4
 if a['v'].shape!=o['v'].shape or np.max(abs(a['v'][:,:2]-o['v'][:,:2]))>3e-6 or np.max(abs(a['v'][upper]-o['v'][upper]),initial=0)>3e-6 or not np.array_equal(a['f'],o['f'])or not np.array_equal(a['uv'],o['uv']):bad.append(n)
ck('Gate plan upper carvings original faces and UVs retained while lower feet fit threshold',not bad,invalid=bad)
clear=[]
for n in ['SITE_V20_INNER_GATE__LEAF_L_Geometry','SITE_V20_INNER_GATE__LEAF_R_Geometry']:
 a=np.load(FD/J[n]['file']);bottom=float(a['v'][:,2].min());clear.append({'leaf':n,'lower_edge_z_m':bottom,'clearance_above_threshold_m':bottom+.5})
ck('Both leaves have positive lower clearance over the actual new threshold',all(.009<c['clearance_above_threshold_m']<.02 for c in clear),leaves=clear)
_,closure=get('V26_7_Inner_Gate_Rear_Return_Closure');_,ground=get('V26_2_Continuous_Ground_And_Perimeter_Shell');_,wall=get('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry')
ck('Rear return is finite closed geometry without duplicate ground or masonry surface',closure.volume()>1e-5 and (closure^ground).volume()<1e-7 and (closure^wall).volume()<1e-7,volume_m3=closure.volume(),ground_contact_overlap_m3=(closure^ground).volume(),wall_overlap_m3=(closure^wall).volume(),native_contact_volume_tolerance_m3=1e-7)
_,j2=get('SITE_V21_GATE_REFERENCE_LAYER_02_Geometry');_,j3=get('SITE_V21_GATE_REFERENCE_LAYER_03_Geometry');jamb=j2+j3
tops=[]
for x in[8.1,8.2,8.3,8.4,8.5,8.7,9.0,9.3]:
 for y in[-11.33,-11.26,-11.18]:
  occupied=sum(h.position[2]<-.40002 for h in jamb.ray_cast([x,y,-1],[x,y,4]))%2==1
  hs=sorted(closure.ray_cast([x,y,0],[x,y,-.7])+ground.ray_cast([x,y,0],[x,y,-.7]),key=lambda h:-h.position[2]);hs=[h for h in hs if h.normal[2]>.9];tops.append({'xy_m':[x,y],'occupied_by_retained_gate_jamb':occupied,'top_m':float(hs[0].position[2])if hs else None})
ck('Requested rear-side porch return has continuous finite support outside retained jamb footprints',all(r['occupied_by_retained_gate_jamb']or r['top_m']is not None and abs(r['top_m']+.40002)<.001 for r in tops),samples=tops)
# All unrelated opaque gate masonry and ground mesh coordinates stay exact.
for n in['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V26_2_Continuous_Ground_And_Perimeter_Shell','V26_Original_Site_Entrance_Ramp_0']:
 a=np.load(FD/J[n]['file']);o=np.load(OD/OJ[n]['file']);ck('Original native geometry retained '+n,all(np.array_equal(a[k],o[k])for k in['v','f','uv','mi']))
P=Path('E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend');fail=[r for r in checks if not r['pass']];report={'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail,'actual_reference_video':'E:/jz/VID_20260507_152114_00_001.insv','evidence_seconds_lens':[[650,0],[655,0],[655,1]],'scope':'Low stone threshold and missing rear return fitted to existing current court/porch levels using actual footage; no calibrated site measurement.'}
(P.parent.parent/'Reports/V26_7_Gate_Regression_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print('GATE_QA_DONE',len(checks),'FAIL',len(fail),flush=True)
