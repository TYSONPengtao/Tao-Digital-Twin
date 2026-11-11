"""Read saved V26.6 export; remove only obsolete generic decoration overlays.
Does not open or save Blender or alter shared work scripts.
"""
from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
D=Path(__file__).parent;F=W/'v26_6/Final';F2=W/'v26_2/Final'
I={r['name']:r for r in json.loads((F/'Geometry_Index.json').read_text('utf8'))}
I2={r['name']:r for r in json.loads((F2/'Geometry_Index.json').read_text('utf8'))}
restoration=json.loads((W/'v26_3/Prepared_Secondary_Deco.json').read_text('utf8'))
rows=[];checks=[];removed=[]
for r in restoration['objects']:
 n=r['name'];a=np.load(F/I[n]['file']);b=np.load(F2/I2[n]['file']);cut=len(b['f'])
 for k in ['f','mi','uv']:
  ok=np.array_equal(a[k][:cut],b[k]);checks.append({'name':n+' original V26.2 '+k+' exact retained prefix','pass':bool(ok)})
  assert ok,(n,k)
 assert np.array_equal(a['v'][:len(b['v'])],b['v'])
 assert int(a['f'][:cut].max())<len(b['v'])
 gone=a['v'][a['f'][cut:]];bounds=[gone.min((0,1)).tolist(),gone.max((0,1)).tolist()]
 assert bounds[0][0]>10.79 and bounds[1][0]<13.18 and bounds[0][1]>-17.10 and bounds[1][1]<-16.75
 fn='TRIM_'+n+'.npz';np.savez_compressed(D/fn,v=a['v'][:len(b['v'])],f=a['f'][:cut],mi=a['mi'][:cut],uv=a['uv'][:cut])
 rows.append({'name':n,'file':fn,'materials':I[n]['materials'],'reason':'Remove V26.3 generic duplicate sloping frieze and descending diagonal; expose the unchanged original level secondary screenwall band. No original secondary object edited.'})
 removed.append({'name':n,'first_removed_triangle':cut,'count':len(gone),'bounds_m':bounds,'volume_removed_from_wall_m3':0,'note':'Decoration-only appended duplicate surfaces; original 11 secondary objects remain exact and supply the true horizontal frieze.'})
protected=[n for n in I if 'Secondary_Screenwall' in n]
assert len(protected)==11
src=Path('E:/jz/JIA/Rebuild_V26_6/Blender/Architecture_Complete_V26_6.blend')
with src.open('rb')as fp:h=hashlib.file_digest(fp,'sha256').hexdigest()
proof={'source_model':str(src),'source_model_sha256':h,'source_export':str(F),'objects':rows,'checks':checks,'removed_duplicate_surfaces':removed,'protected_original_secondary_objects':protected,'wall_base_or_ground_geometry_changed':False,'protected_original_secondary_geometry_changed':False,'texture_uv_changed':False,'original_v26_2_vertex_arrays_retained_exact':True,'unused_v26_3_appended_vertex_tail_removed':True,'source_evidence':['D:/Desktop/屏幕截图 2026-10-24 023323.jpg','D:/Desktop/屏幕截图 2026-10-24 023700.jpg'],'material_recipe':'apply_site_materials.py'}
(D/'Prepared_Site_Decoration.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'rows':rows,'checks_pass':all(c['pass']for c in checks),'removed':removed},ensure_ascii=False,indent=2))
