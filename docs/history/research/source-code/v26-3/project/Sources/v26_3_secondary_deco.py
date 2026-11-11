from v26_2_common import *
D=W/'v26_3';FD=W/'v26_2'/'Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};source=json.loads((D/'Original_Secondary_Surfaces.json').read_text('utf8'));rows=[];proof=[]
A=np.array([10.67,-16.8545]);B=np.array([13.46,-16.5811]);u=(B-A)/np.linalg.norm(B-A);n=np.array([-u[1],u[0]]);basis=np.array([[*u,0.],[*n,0.],[0,0,1.]]);origin=np.r_[A,0.];lo=np.array([-.03,-.63,-4.5]);hi=np.array([np.linalg.norm(B-A)+.03,.63,3.8]);glo=np.array([12.85,-17.25,-4.85]);ghi=np.array([22.,-8.2,-.365])
def half(poly,axis,z,sign):
 inside=[];outside=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  a=sign*(p[0][axis]-z);b=sign*(q[0][axis]-z);pin=a>=-1e-9;qin=b>=-1e-9;(inside if pin else outside).append(p)
  if pin!=qin:
   t=a/(a-b);r=(p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1]));inside.append(r);outside.append(r)
 return inside,outside
def box_outside(poly,lo,hi):
 keep=[]
 for k in range(3):
  for z,sg in [(lo[k],1),(hi[k],-1)]:
   if not poly:break
   poly,out=half(poly,k,z,sg)
   if len(out)>2:keep.append(out)
 return keep
for r in source['objects'][1:]:
 name=r['name'];old=J[name];a=np.load(FD/old['file']);s=np.load(D/r['file']);vv=a['v'].tolist();ff=a['f'].tolist();uv=a['uv'].tolist();mi=a['mi'].tolist();restored=0
 st=s['v'][s['f']];loc=(st-origin)@basis.T;candidate=np.all((loc.max(1)>=lo)&(loc.min(1)<=hi),axis=1)
 for k in np.flatnonzero(candidate):
  t=st[k];nn=np.cross(t[1]-t[0],t[2]-t[0]);nl=np.linalg.norm(nn)
  if nl>1e-15 and nn[2]/nl>.45 and t[:,2].max()<-.90:continue
  poly=[(p,tex)for p,tex in zip(loc[k],s['uv'][k])]
  for axis in range(3):
   for z,sg in [(lo[axis],1),(hi[axis],-1)]:
    if not poly:break
    poly,_=half(poly,axis,z,sg)
  if len(poly)<3:continue
  poly=[(p@basis+origin,tex)for p,tex in poly]
  pieces=box_outside(poly,glo,ghi)
  for pp in pieces:
   for j in range(1,len(pp)-1):
    tr=[pp[0],pp[j],pp[j+1]];v=np.array([q[0]for q in tr]);ar=np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))/2
    if ar<1e-10:continue
    off=len(vv);vv.extend(v);ff.append([off,off+1,off+2]);uv.append([q[1]for q in tr]);mi.append(old['materials'].index(r['materials'][int(s['mi'][k])]))
    restored+=1
 fn='Secondary_Original_'+name+'.npz';np.savez_compressed(D/fn,v=np.array(vv),f=np.array(ff,np.int32),uv=np.array(uv),mi=np.array(mi,np.int32));rows.append({'name':name,'file':fn,'materials':old['materials'],'triangles':len(ff),'reason':'Restore only the V24.34 secondary screenwall original stepped frieze and cornices; every current outside-branch triangle retained unchanged'})
 proof.append({'name':name,'retained_current_triangles':len(a['f']),'restored_original_local_triangles':restored,'source_file':r['file'],'outside_secondary_mesh_prefix_preserved':True});print('ORIGINAL_SECONDARY_DECO',proof[-1],flush=True)
(D/'Prepared_Secondary_Deco.json').write_text(json.dumps({'objects':rows,'proof':proof},ensure_ascii=False,indent=2),encoding='utf8')
