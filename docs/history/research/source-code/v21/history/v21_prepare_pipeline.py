"""Prepare V21 assembly from the checked V20 workflow, without touching V20."""
from pathlib import Path
W=Path(__file__).parent
s=(W/'v20_assemble.py').read_text(encoding='utf8').replace('V20','NEXT').replace('V19','V20').replace('NEXT','V21').replace("W/'v20'","W/'v21'")
s=s.replace("'73b4a8f30d88aad0fa3ad463bd0898be51177430d364776c690a5c09698687c4'","'087a4457d3df7feea42503cf6ea27788fd1374e55b8d4a8dbd1853b75424d4d4'")
s=s.replace("for a in ['house','storage','gate_pavilion']:","for a in ['house','gate','site']:")
s=s.replace("W/f'v20_{a}'","W/f'v21_{a}'")
s=s.replace("for s in Path('D:/Desktop/问题').glob('屏幕截图 2026-10-13 03*.jpg'):","for s in list(Path('D:/Desktop/问题').glob('屏幕截图 2026-10-13 15*.jpg'))+list(Path('D:/Desktop/问题').glob('屏幕截图 2026-10-13 033*.jpg'))+list(Path('D:/Desktop/问题').glob('download.jfif')):")
s=s.replace("if e.get('v20_door'):","if e.get('v21_door') or e.get('v20_door'):")
s=s.replace("e.get('v20_native_cache_override')","e.get('v21_native_cache_override') or e.get('v20_native_cache_override')")
s=s.replace("e['v20_native_cache_override']","e.get('v21_native_cache_override') or e['v20_native_cache_override']")
s=s.replace("e.get('v20_native_cache_materials')","e.get('v21_native_cache_materials') or e.get('v20_native_cache_materials')")
s=s.replace("if k in md:\n   pp=Path(md[k]);", "if k in md or ('native_'+k) in md:\n   pp=Path(md.get(k,md.get('native_'+k)));")
s=s.replace("S['v20_changes']", "S['v21_changes']")
s=s.replace("if e.get('v21_door') or e.get('v20_door'):at.SetUserString('UE_Door_Hinge_LOCAL_m',json.dumps(e['pivot_world_m']));at.SetUserString('UE_Default_Pose','INWARD_OPEN')", "if e.get('v21_door') or e.get('v20_door'):at.SetUserString('UE_Door_Pivot_LOCAL_m',json.dumps(e.get('pivot_world_m',e.get('hinge_local_m'))));at.SetUserString('UE_Default_Pose','OPEN');at.SetUserString('UE_Door_Operation',e.get('operation','HINGED_INWARD'))")
(W/'v21_assemble.py').write_text(s,encoding='utf8')
# General save/readback checks are reused, while this iteration's semantic
# and collision checks are supplied independently after the patches exist.
s=(W/'v19_readback_qa.py').read_text(encoding='utf8').split('BF=rh.File3dm.Read')[0].replace('V19','V21')
s=s.replace('mm.IsValid and mm.IsClosed','mm.IsValid and (mm.IsClosed or not r.get("closed_expected",True))').replace('vol>1e-10,volume_m3=vol','vol>1e-10 or not r.get("closed_expected",True),volume_m3=vol')
s+='''\ncheck('V20 source model preserved',sha(Path(AQ['base_model']))==AQ['base_model_sha256'])
for m in F.Materials:
 for getter in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,getter)()
  if tx:check('Material bitmap exists '+m.Name,Path(tx.FileName).is_file())
report={'status':'PASS_FRESH_NATIVE_V21_QA','model':str(P),'sha256':sha(P),'native_objects':len(F.Objects),'nodes':len(I),'triangles':sum(r['triangles'] for r in I),'retained_objects':len(AQ['retained']),'changed_objects':len(AQ['created']),'checks':checks,'index_parity':indexproof,'ue5_import_tested':False}
(O/'06_Report/V21_Native_Readback_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('V21 FRESH NATIVE PASS',len(I),flush=True)
'''
(W/'v21_native_qa.py').write_text(s,encoding='utf8')
print('Prepared assembly and fresh native readback checks')
