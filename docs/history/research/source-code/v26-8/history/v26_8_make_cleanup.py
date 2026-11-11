from pathlib import Path
W=Path(__file__).parent
s=(W/'v26_7_finalize_house.py').read_text('utf8');a=s.index('vv=aa[\'v\'].copy()');b=s.index("white_index=row['materials']",a)
body=s[a:b].replace("vv=aa['v'].copy();ff=aa['f'].copy();mm=aa['mi'].copy();uu=aa['uv'].copy();repairs=[];sourceverts={tuple(p)for p in old['v']}", "vv=v.copy();ff=f.copy();mm=mi.copy();uu=uv.copy();repairs=[];sourceverts=set()")
body=body.replace("ss=solid(vv,ff,'Final exact local edge collapse')", "ss=solid(vv,ff,'Final native local edge collapse')")
header='from v26_2_common import *\n\ndef repair_native(v,f,mi,uv):\n'
out=header+'\n'.join(' '+line for line in body.splitlines())+'\n return vv,ff,mm,uu,{\'edge_repairs\':repairs,\'opposite_internal_faces_removed\':internal_removed,\'minimum_triangle_area_m2\':float(ar.min())}\n'
(W/'v26_8_native_cleanup.py').write_text(out,'utf8')
