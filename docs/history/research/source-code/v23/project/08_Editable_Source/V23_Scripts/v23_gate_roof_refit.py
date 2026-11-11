"""Compact, shallow gate eaves following the user's ideal-image correction."""
from v23_common import *
D=W/'v23_gate_roof_refit';D.mkdir(exist_ok=True);Q=start();checks=[]
P=json.loads((W/'v23_gate_roof/Mutation.json').read_text(encoding='utf8'))
N={e['name']:e for e in P['replace']+P['add']}
names=['SITE_V21_GATE_REFERENCE_LAYER_'+str(i).zfill(2) for i in range(9,16)]+['SITE_V21_GATE_REFERENCE_CLOSED_SOFFIT','GATE_V22_EMBOSSED_TILE_END_CAPS']
grids=[]
for p in E['SITE_V21_GATE_REFERENCE_LAYER_09']['parts']:
 v=np.asarray(ex.world_part(p,E['SITE_V21_GATE_REFERENCE_LAYER_09'])[0]);xs=np.unique(np.round(v[:,0],6));ys=np.unique(np.round(v[:,1],6));z=np.full((len(ys),len(xs)),-1e6)
 for x,y,zz in v:
  i=np.argmin(abs(xs-x));j=np.argmin(abs(ys-y));z[j,i]=max(z[j,i],zz)
 assert z.min()>0;grids.append((xs,ys,z))

def oldtop(x,y):
 xs,ys,z=grids[0 if y<=-11.486 else 1];y=min(max(y,float(ys[0])),float(ys[-1]));j=min(max(np.searchsorted(ys,y)-1,0),len(ys)-2);t=(y-ys[j])/(ys[j+1]-ys[j]);return np.interp(x,xs,z[j])*(1-t)+np.interp(x,xs,z[j+1])*t

def point(x,y,z):
 # Preserve the central ridge and soffit disk exactly. Eave end uplift becomes
 # 37%; ridge-end uplift becomes 3%, avoiding the old tall swept corner ridge.
 span=.776 if y<=-11.486 else .600
 ridge=max(0.,1.-abs(y+11.486)/span)
 rise=oldtop(x,y)-oldtop(6.6,y)
 lowering=(.63+.34*ridge)*rise
 # The old ornamental horns continued beyond the carrier. Flatten those
 # extensions smoothly rather than leaving long, nearly metre-high fins.
 t=min(1.,max(0.,(abs(x-6.6)-2.55)/.50));horn=.27*t*t*(3-2*t)
 return [6.6+.87*(x-6.6),y,z-lowering-horn]

before=[];after=[];new_by_name={}
for name in names:
 src=N.get(name,E[name]);ps=[];ms=[]
 for k,p in enumerate(ex.expand_parts(src)):
  vv,ff=ex.world_part(p,src)
  before.extend([np.asarray(vv).min(0).tolist(),np.asarray(vv).max(0).tolist()])
  m=manifold({'type':'polyhedron','vertices':np.asarray(vv).tolist(),'faces':ff})
  # Long carrier and beam faces are refined before the nonlinear deformation
  # so their joints follow the same curve as their small adjacent tile pieces.
  mm=m.refine_to_length(.08).to_mesh64();v=np.asarray(mm.vert_properties)[:,:3];f=np.asarray(mm.tri_verts)
  v=np.asarray([point(*q) for q in v]);g={'type':'polyhedron','vertices':v.tolist(),'faces':f.tolist()};m=manifold(g)
  assert m.status()==mf.Error.NoError and m.volume()>1e-10,(name,k)
  out=copy.deepcopy(p);out['geometry']=fm(m);ps.append(out);ms.append(m);after.extend([v.min(0).tolist(),v.max(0).tolist()])
 e=put(Q,name,ps,classification='V23_COMPACT_SHALLOW_EAVE_IDEAL_IMAGE_REFIT',v23_roof_refit=True)
 e['source']='User correction: 屋檐太夸张，参考理想模型.png; compact shallow eave correction, 2026-10-16'
 new_by_name[name]=uni(ms)
 print('REFIT',name,len(ps),flush=True)

b=np.asarray(before);a=np.asarray(after)
checks.append({'check':'REGISTERED_ROOF_ENVELOPE_REDUCED','before_bbox':[b.min(0).tolist(),b.max(0).tolist()],'after_bbox':[a.min(0).tolist(),a.max(0).tolist()],'before_width_m':float(np.ptp(b[:,0])),'after_width_m':float(np.ptp(a[:,0])),'width_scale':.87,'eave_corner_lift_retained_fraction':.37,'ridge_corner_lift_retained_fraction':.03,'outer_horn_additional_lowering_m':.27})
for p in [[6.6,-11.6,2.5409],[6.6,-11.486,3.2383],[6.6,-12.262,2.8093]]:
 assert np.max(abs(np.asarray(point(*p))-p))<1e-12
checks.append({'check':'CENTRAL_SOFFIT_DISK_EAVE_AND_RIDGE_HEIGHTS_UNCHANGED','passed':True})
roof=new_by_name['SITE_V21_GATE_REFERENCE_LAYER_09'];tiles=new_by_name['SITE_V21_GATE_REFERENCE_LAYER_10'];soffit=new_by_name['SITE_V21_GATE_REFERENCE_CLOSED_SOFFIT']
assert (roof^tiles).volume()>1e-5
assert (roof^soffit).volume()>1e-5
checks.append({'check':'DEFORMED_CARRIER_RETAINS_POSITIVE_TILE_AND_SOFFIT_CONTACT','tile_carrier_overlap_m3':(roof^tiles).volume(),'roof_soffit_overlap_m3':(roof^soffit).volume()})
for name in ['SITE_V21_GATE_REFERENCE_LAYER_11','SITE_V21_GATE_REFERENCE_LAYER_12','SITE_V21_GATE_REFERENCE_LAYER_13','SITE_V21_GATE_REFERENCE_LAYER_15']:
 m=new_by_name[name];ov=(m^(roof+soffit)).volume();assert ov>1e-8,(name,ov)
 checks.append({'check':'RETAINED_SUPPORT_CONTACT','node':name,'overlap_m3':ov})
Q['change_notes']=['按用户指出的“屋檐太夸张”修正：门楼屋顶总宽缩至原来的 87%，檐角上翘保留约 37%，脊端弧升保留约 3%，外挑长角额外压低。','对屋面、厚瓦、瓦当、檐枋、滴水、短椽和封闭檐底同时变形，避免分别移动造成脱节；门楼中部檐底圆盘接触面、正脊与檐口标高保持不变。']
save(Q,D,checks)
