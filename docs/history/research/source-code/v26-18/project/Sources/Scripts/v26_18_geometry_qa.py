from v26_2_common import *
import hashlib
D=W/'v26_18';J=json.loads((D/'Input/Source_Index.json').read_text('utf8'));ix={r['name']:r for r in J['objects']};prep=json.loads((D/'Prepared.json').read_text('utf8'));prepared='--prepared'in sys.argv;FD=D/('Prepared'if prepared else'Final');rows=prep['objects']if prepared else json.loads((FD/'Geometry_Index.json').read_text('utf8'));r=rows[0];a=np.load(FD/r['file']);b=np.load(D/'Input'/ix[r['name']]['file']);m=solid(a['v'],a['f']);old=solid(b['v'],b['f']);checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('GEOMETRY_QA',n,bool(yes),kw if not yes else'',flush=True)
scopes=[cube(*[np.asarray(q,np.float32).astype(float)for q in j['scope_m']])for j in prep['proof']['joins']];scope=union(scopes);outside=[((m-old)-scope).volume(),((old-m)-scope).volume()];ck('Native geometry changes stay inside the two stair/slab underside joint volumes',max(abs(q)for q in outside)<1e-5,outside_delta_m3=outside)
ck('House remains one closed positive volume',len(m.decompose())==1 and m.volume()>0)
soffits=[]
for j in prep['proof']['joins']:
 zs=j['slab_soffit_z_m'];slope,intercept=j['upper_flight_original_soffit_line']
 for y in[7.50,7.95,8.40,8.55,8.75,9.10,9.55]:
  for x in[7.815,7.90,8.00,8.08,8.13,8.21,8.40,8.70,8.90]:
   expected=min(slope*x+intercept,zs)if y<8.50 else zs
   hits=m.ray_cast([x,y,zs-.30],[x,y,zs+.055]);hz=[h.position[2]for h in hits];actual=hz[0]if hz else None
   soffits.append({'floor':j['floor_to'],'xy':[x,y],'expected_z_m':expected,'actual_z_m':actual,'pass':actual is not None and abs(actual-expected)<.000003})
ck('Both slab soffits meet the original sloping stair waist without the65mm step',all(q['pass']for q in soffits),samples=soffits)
treads=[]
for fl in[1,2]:
 for y in[7.75,8.00,8.25,8.80,9.10,9.40]:
  for x in np.linspace(4.25,8.85,31):
   z0=-.60 if fl==1 else 3.30;z1=(1.55 if fl==1 else 5.30)if y>8.5 else(3.50 if fl==1 else 7.10)
   def tops(mm):return[h.position[2]for h in mm.ray_cast([x,y,z1],[x,y,z0])]
   oa,na=tops(old),tops(m);treads.append({'floor':fl,'xy':[float(x),y],'before_z_m':oa[0]if oa else None,'after_z_m':na[0]if na else None,'pass':bool(oa and na and abs(oa[0]-na[0])<.000003)or not oa and not na})
ck('Stair treads, landings and upper walking floor heights are retained',all(q['pass']for q in treads),samples=treads)
tt=a['v'][a['f']];no=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);ar=np.linalg.norm(no,axis=1)/2;no/=np.maximum(2*ar[:,None],1e-30);fascia=[]
for q in prep['proof']['fascias']:
 lo,hi=q['height_interval_m'];riser_bottom=1.3600585460662842 if q['floor']==1 else 5.110058784484863;riser=(no[:,0]>.999)&(tt[:,:,1].min(1)>=8.59999)&(tt[:,:,2].min(1)>=riser_bottom-.00002);sel=(abs(no[:,0])>.999)&(tt[:,:,0].min(1)>=5.02999)&(tt[:,:,0].max(1)<=5.20001)&(tt[:,:,1].min(1)>=7.41999)&(tt[:,:,1].max(1)<=9.68001)&(tt[:,:,2].min(1)>=lo-.00002)&(tt[:,:,2].max(1)<=hi+.00002)&~riser
 fascia.append({'floor':q['floor'],'faces':int(sel.sum()),'materials':sorted({r['materials'][i]for i in a['mi'][sel]}),'pass':bool(sel.any())and all(r['materials'][i]=='M_Wall_Interior'for i in a['mi'][sel])})
ck('Both half-landing vertical fascias are white wall finish',all(q['pass']for q in fascia),surfaces=fascia)
risers=[]
for q in prep['proof']['fascias']:
 hi=q['height_interval_m'][1];bottom=1.3600585460662842 if q['floor']==1 else 5.110058784484863
 sel=(no[:,0]>.999)&(abs(tt[:,:,0]-5.2).max(1)<.00002)&(tt[:,:,1].min(1)>=8.59999)&(tt[:,:,1].max(1)<=9.68001)&(tt[:,:,2].min(1)>=bottom-.00002)&(tt[:,:,2].max(1)<=hi+.00002)
 risers.append({'floor':q['floor'],'faces':int(sel.sum()),'pass':bool(sel.any())and all(r['materials'][i]=='M_V24_31_Stair_Gray_Marble'for i in a['mi'][sel])})
ck('The adjacent final walking risers retain their original stone material',all(q['pass']for q in risers),surfaces=risers)
well=cube([5.2001,8.5001,-.4498],[7.6999,8.5999,7.0499]);ck('Existing narrow central stairwell remains open',abs((m^well).volume())<1e-8)
ed=np.sort(np.concatenate([a['f'][:,[0,1]],a['f'][:,[1,2]],a['f'][:,[2,0]]]),1);_,ct=np.unique(ed,axis=0,return_counts=True);ck('All faces have positive area, finite UV and closed indexed edges',ar.min()>1e-18 and np.isfinite(a['uv']).all()and np.all(ct==2),minimum_face_area_m2=float(ar.min()))
ck('Saved source V26.17 remains byte-identical',hashlib.sha256(Path(J['model']).read_bytes()).hexdigest()==J['sha256'])
fail=[c for c in checks if not c['pass']];out={'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail}
if prepared:path=D/'Prepared_Geometry_QA.json'
else:
 P=Path('E:/jz/JIA/Rebuild_V26_18/Blender/Architecture_Complete_V26_18.blend');out['model_sha256']=hashlib.sha256(P.read_bytes()).hexdigest();path=P.parent.parent/'Reports/V26_18_Geometry_QA.json'
path.write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('GEOMETRY_QA_DONE',len(checks),len(fail),flush=True)
if fail:raise AssertionError([c['check']for c in fail])
