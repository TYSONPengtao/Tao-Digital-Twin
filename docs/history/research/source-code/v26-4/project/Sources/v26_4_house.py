from v26_2_common import *
import v26_2_common as C
from shapely.geometry import shape,box,Polygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
import shapely,shutil
D=W/'v26_4';D.mkdir(exist_ok=True);C.D=D
old=json.loads((W/'v26_3/Exact_House_Parts.json').read_text('utf8'));layers=[];proof=[]
# Finish planes at each established wall centreline. The ordinary masonry
# span is at most 240 mm. Cross-wall returns and actual column/beam cores
# are retained as joints, not enlarged into an entire thickened wall.
xaxes=[0.,3.9,9.1,13.];yaxes=[2.1,7.3,9.8]
core=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components']
for r in old['layers']:
 z0,z1=r['z_m'];z=(z0+z1)/2;P=shape(r['outline']);before=P.area
 fl=next((i for i,(a,b)in enumerate([(-.45,3.32),(3.45,6.92),(7.05,10.22)],1)if a<=z<b),None)
 if fl:
  actualcores=[]
  for c in core:
   if not c['name'].startswith(('KZ_','BEAM_')):continue
   lo,hi=np.array(c['bounds_m'])
   if lo[2]-.0003<z<hi[2]+.0003:actualcores.append(box(lo[0],lo[1],hi[0],hi[1]))
  retain=unary_union(actualcores).buffer(.0003,join_style=2)if actualcores else Polygon()
  # An intersecting wall's actual thickness is a corner exception.
  for axis,centres,other in [(0,xaxes,yaxes),(1,yaxes,xaxes+[2.2,10.65,10.8])]:
   for a in centres:
    strips=[]
    for lo,hi in [(a-.25,a-.12),(a+.12,a+.25)]:
     q=box(lo,1.85,hi,10.04)if axis==0 else box(-.25,lo,13.25,hi)
     # Above a beam soffit the original core itself supplies the joint.
     # A full-height corner exemption here would retain obsolete thick
     # finish blocks over the thin WC partitions.
     local_other=other if z<(3.05 if fl==1 else 6.65 if fl==2 else 9.95) else []
     for b in local_other:
      corner=box(-1,b-.23,15,b+.23)if axis==0 else box(b-.23,-1,b+.23,12)
      q=q.difference(corner)
     strips.append(q.difference(retain))
    P=P.difference(unary_union(strips))
  # Preserve the user-confirmed two WC zones and their distinct entries.
  if fl==1:
   P=P.difference(box(9.22,8.345,10.59,8.655))
   P=P.union(box(9.,7.4,9.2,9.68))
   if z<1.65:P=P.difference(box(8.85,8.6,9.35,9.4))
   P=P.union(box(9.2,7.2,12.88,7.4)).union(box(10.6,7.4,10.7,9.8))
   if z<1.65:P=P.difference(box(10.7,7.05,11.5,7.55))
  else:
   # The upper-floor bathroom entry is in the side wall. Close the entire
   # front wall continuously, including the old front-door infill seam.
   # The open rear recess at X=9.32..10.7 stays outside this wall strip.
   P=P.union(box(10.8,7.18,12.88,7.42))
  P=P.union(box(.12,7.2,2.2,7.4))
  P=shapely.set_precision(P.buffer(0),.0001)
 proof.append({'z_m':[z0,z1],'floor':fl,'area_removed_m2':max(0,before-P.area)})
 layers.append(dict(r,outline=P.__geo_interface__,area_m2=P.area))
for r in old['extras']:shutil.copy2(W/'v26_3'/r['file'],D/r['file'])
(D/'Exact_House_Parts.json').write_text(json.dumps(dict(old,layers=layers),ensure_ascii=False,indent=2),encoding='utf8')
shutil.copy2(W/'v26_3/Upper_Wall_Plan.json',D/'Upper_Wall_Plan.json')
code=(W/'v26_3_surface.py').read_text('utf8').replace("D=W/'v26_3'","D=W/'v26_4'").replace('if ar<1e-12:return','if ar<1e-18:return')
needle="V=[];F=[];MI=[];UV=[];cache={}\nfor tr in jv[jf]:emit(tr)"
repair="""
raw=mf.Mesh64(np.array(jv,copy=True),np.array(jf,np.uint64,copy=True),tolerance=.000025)
fixed=mf.Manifold(raw)
if fixed.status()!=mf.Error.NoError:
 raw.merge();fixed=mf.Manifold(raw)
print('AFTER_FLOAT32_STATUS',fixed.status(),flush=True)
assert fixed.status()==mf.Error.NoError
fixed=fixed.set_tolerance(.000025).simplify(.000025)
fb=fixed.to_mesh64();jv=np.array(fb.vert_properties[:,:3]);jf=np.array(fb.tri_verts,np.int32)
V=[];F=[];MI=[];UV=[];cache={}
for tr in jv[jf]:emit(tr)
np.savez_compressed(D/'Debug_Closure.npz',v=np.array(V),f=np.array(F,np.int32))
"""
assert needle in code
code=code.replace(needle,repair)
(W/'v26_4_surface.py').write_text(code,encoding='utf8')
(D/'Wall_Thickness_Proof.json').write_text(json.dumps({'limit_m':.24,'corner_halfwidth_m':.23,'preserved_original_column_beam_cores':True,'ordinary_wall_spans_only':True,'layers':proof},indent=2),encoding='utf8')
print('V26_4_WALL_PROFILES_READY',len(layers),flush=True)
