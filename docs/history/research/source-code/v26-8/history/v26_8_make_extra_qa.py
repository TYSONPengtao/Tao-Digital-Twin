from pathlib import Path
W=Path(__file__).parent
s=(W/'v26_7_railing_audit/saved_native_qa.py').read_text('utf8').replace('v26_7_railing_audit','v26_8_railing').replace("W/'v26_7/Final'","W/'v26_8/Final'").replace('Rebuild_V26_7/Reports/V26_7_Railing_Regression_QA.json','Rebuild_V26_8/Reports/V26_8_Railing_Regression_QA.json').replace('Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend','Rebuild_V26_8/Blender/Architecture_Complete_V26_8.blend')
a=s.index("orig=json.loads");b=s.index('ballclear=[]',a)
s=s[:a]+'''orig=json.loads((W/'v26_1/Prepared_Railing.json').read_text('utf8'))['proof'];seatbad=[]
for b in [q for q in rp['balusters']if ' flight 'in q['tag']and not q.get('added_local_end_gap_infill')]:
 old=min((q for q in orig['balusters']if q['tag']==b['tag']),key=lambda q:abs(q['xy'][0]-b['xy'][0]));want=8.652 if 'flight 1'in b['tag']else8.448
 if abs(b['xy'][0]-old['xy'][0])>1e-6 or abs(b['seat_z_m']-old['seat_z_m'])>1e-6 or abs(b['xy'][1]-want)>1e-6:seatbad.append({'new':b,'old':old})
ck('Flight spindles retain source tread XZ and follow the two new independent well-edge axes',not seatbad,changes=seatbad)
''' +s[b:]
s=s.replace('else8.448','else 8.448')
s=s.replace('All 110 original spindle foot positions and tread seat elevations retained exactly','Flight foot XZ retained and Y correctly refitted')
s=s.replace('PASS_CANDIDATE_GEOMETRY','PASS_SAVED_NATIVE_GEOMETRY')
(W/'v26_8_railing/saved_native_qa.py').write_text(s,'utf8')
# Window validation uses the actual saved array, not a re-application of the recipe.
s=(W/'v26_8_windows/qa.py').read_text('utf8');a=s.index('cuts=[]');b=s.index('heights=[]',a)
s=s[:a]+'''ND=W/'v26_8/Final';NJ={r['name']:r for r in json.loads((ND/'Geometry_Index.json').read_text('utf8'))};actual=np.load(ND/NJ[HN]['file']);house=solid(actual['v'],actual['f'])
check('Saved resized house is one positive closed solid',house.status()==mf.Error.NoError and len(house.decompose())==1)
check('All15 proposal iron guards are absent from actual visible native model',len(prep['remove'])==15 and not any(n in NJ for n in prep['remove']))
''' +s[b:]
s=s.replace("aa=np.load(D/r['file']);orig=np.load", "aa=np.load(ND/NJ[r['name']]['file']);expected=np.load(D/r['file']);check('Saved window matches prepared '+r['name'],aa['v'].shape==expected['v'].shape and np.max(abs(aa['v']-expected['v']))<3e-6 and np.array_equal(aa['f'],expected['f']));orig=np.load")
s=s.replace("np.array_equal(orig['v'][:,:2],aa['v'][:,:2])", "np.allclose(orig['v'][:,:2],aa['v'][:,:2],atol=3e-6,rtol=0)")
s=s.replace("house=house.simplify(1e-6)","# Validate the actual saved triangulation without simplifying it.")
s=s.replace("np.savez_compressed(BASE/'QA_Candidate_House.npz',v=v,f=f)","rail='BALCONY_F2_PHOTO_OPEN_STONE_RAIL_Geometry';oldrail=np.load(FD/J[rail]['file']);newrail=np.load(ND/NJ[rail]['file']);check('Original F2 stone rail remains exact',all(np.array_equal(oldrail[k],newrail[k])for k in ['v','f','mi','uv']))")
a=s.index("result={'source_sha256'")
s=s[:a]+'''P=Path('E:/jz/JIA/Rebuild_V26_8/Blender/Architecture_Complete_V26_8.blend');fail=[c for c in checks if not c['pass']];result={'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'source_sha256':prep['source_sha256'],'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail,'height_samples':heights,'glazing_samples':glazing,'scope':'Actual final saved native readback, five front room bay groups; user confirmed no iron guards on all three floors.'}
(Path('E:/jz/JIA/Rebuild_V26_8/Reports')/'V26_8_Window_Sill_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8');print('SAVED_WINDOW_QA',len(checks),'FAIL',len(fail),flush=True)
'''
(W/'v26_8_windows/saved_native_qa.py').write_text(s,'utf8')
print('EXTRA_QA_SCRIPTS_READY')
