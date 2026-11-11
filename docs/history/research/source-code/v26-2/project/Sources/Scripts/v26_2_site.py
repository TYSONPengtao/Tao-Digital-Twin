from v26_2_common import *
OUTER='M_V26_2_Continuous_Exterior_Strata';GALLERY='M_V26_2_Continuous_Gallery_Base'
route=json.loads((W/'v24_20/Prepared_Geometry.json').read_text('utf8'))['wall_uv_route']
class ArcMap:
 def __init__(self,route):
  self.p=np.array(route['xy']);self.a=self.p[:-1];self.d=np.diff(self.p,axis=0);self.l=np.linalg.norm(self.d,axis=1);good=self.l>1e-7;self.a=self.a[good];self.d=self.d[good];self.l=self.l[good];self.u=self.d/self.l[:,None];self.n=np.c_[self.u[:,1],-self.u[:,0]];self.s=np.r_[0,np.cumsum(self.l)[:-1]];self.planes={}
 def triangle(self,t):
  normal=np.cross(t[1]-t[0],t[2]-t[0]);nn=np.linalg.norm(normal)
  if nn<1e-12:return t[:,[0,2]]
  normal/=nn
  if abs(normal[2])>.85:return t[:,[0,1]]
  q=t[:,:2].mean(0);nh=normal[:2]/max(np.linalg.norm(normal[:2]),1e-15);key=(*np.round(nh,4),round(float(q@nh),3))
  if key not in self.planes:
   r=q-self.a;proj=(r*self.u).sum(1);closest=self.a+self.u*np.clip(proj,0,self.l)[:,None];dist=np.linalg.norm(closest-q,axis=1);align=self.n@nh;score=dist+np.maximum(0,.70-align)*5;i=int(np.argmin(score));tangent=np.array([-nh[1],nh[0]])
   if tangent@self.u[i]<0:tangent=-tangent
   offset=self.s[i]+float((q-self.a[i])@self.u[i])-float(q@tangent);self.planes[key]=(tangent,offset)
  tangent,offset=self.planes[key];return np.c_[t[:,:2]@tangent+offset,t[:,2]]
mapper=ArcMap(route)
names=['V26_1_Continuous_Court_Road_And_Floor_Surfaces','SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_1_Geometry','SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE_Geometry']
ms=[];proof=[]
for name in names:
 a=arr(name);v=a['v'];f=a['f'];mi=a['mi'].copy();uv=a['uv'].copy();mats=list(I[name]['materials']);t=v[f];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-30)
 if name.startswith('V26_1_Continuous'):
  ids=[j for j,m in enumerate(mats)if m in ['M_V24_18_Continuous_Rubble','M_V24_18_Continuous_Dark_Courses','M_V24_18_Continuous_Blue_Brick']];sel=np.isin(mi,ids);mat=GALLERY
 else:
  ids=[j for j,m in enumerate(mats)if m in ['M_V24_20_Continuous_AsBuilt_Perimeter','M_V26_1_Reference_Wall_Rubble_Stone_Limewash_Brick']];sel=np.isin(mi,ids);mat=OUTER
 mats.append(mat);mi[sel]=len(mats)-1
 for k in np.flatnonzero(sel):uv[k]=mapper.triangle(t[k])
 m=tracked(v,f,mats,mi,uv,name+' continuous exterior material ownership');ms.append(m);proof.append({'name':name,'reassigned_triangles':int(sel.sum()),'inside_white_material_unchanged':not name.startswith('V26_1_Continuous'),'source_floor_uv_retained':True,'arc_length_uv_m':True})
 print('SITE_OWNER',name,len(f),int(sel.sum()),flush=True)
body=union(ms);row,body=export('V26_2_Continuous_Ground_And_Perimeter_Shell',body,'One visible owner at perimeter/retaining-base/road joins; continuous photographed rubble, dressed stone and limewash bands')
# Remove only obsolete white frieze/frame pieces underneath the storage
# gallery. The actual upper wall cornice and white frieze stay in place.
def split(poly,axis,z,sign):
 ins=[];outs=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  a=sign*(p[0][axis]-z);b=sign*(q[0][axis]-z);pin=a>=-1e-9;qin=b>=-1e-9;(ins if pin else outs).append(p)
  if pin!=qin:
   s=a/(a-b);r=(p[0]+s*(q[0]-p[0]),p[1]+s*(q[1]-p[1]));ins.append(r);outs.append(r)
 return ins,outs
objects=[row];clipped=[];lo=np.array([12.85,-17.25,-4.85]);hi=np.array([22.,-8.2,-.365])
for name in [n for n in I if n.startswith('V24_21_Exterior_')]:
 a=arr(name);v=a['v'];f=a['f'];tt=v[f];vv=v.tolist();ff=[];uu=[];mm=[];changed=0;removed=0.
 for face,tex,mat in zip(f,a['uv'],a['mi']):
  t=v[face]
  if ((t.max(0)<lo)|(t.min(0)>hi)).any():ff.append(face);uu.append(tex);mm.append(mat);continue
  poly=[(p,u)for p,u in zip(t,tex)];keep=[]
  for k in range(3):
   for z,s in [(lo[k],1),(hi[k],-1)]:
    if not poly:break
    poly,side=split(poly,k,z,s)
    if len(side)>2:keep.append(side)
  if not poly:ff.append(face);uu.append(tex);mm.append(mat);continue
  changed+=1;before=np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))/2;after=0.
  for pp in keep:
   for j in range(1,len(pp)-1):
    tri=[pp[0],pp[j],pp[j+1]];p=np.array([r[0]for r in tri]);ar=np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))/2
    if ar<1e-10:continue
    after+=ar;k=len(vv);vv.extend(p);ff.append([k,k+1,k+2]);uu.append([r[1]for r in tri]);mm.append(mat)
  removed+=max(0,before-after)
 fn='TRIM_'+name+'.npz';np.savez_compressed(D/fn,v=np.array(vv),f=np.array(ff,np.int32),uv=np.array(uu),mi=np.array(mm,np.int32));objects.append({'name':name,'file':fn,'materials':I[name]['materials'],'reason':'Remove obsolete low white ornament under the stone gallery base; retain original upper cornices'});clipped.append({'name':name,'touched_triangles':changed,'removed_surface_m2':removed,'clip_box_m':[lo.tolist(),hi.tolist()]});print('OLD_ORNAMENT',name,changed,removed,flush=True)
out={'objects':objects,'archive':names,'proof':{'material_ownership':proof,'old_low_ornament_removed':clipped,'outer_strata_z_m':[-.68,-.20,.04],'gallery_dressed_stone_band_z_m':[-1.05,-.38],'texture_basis':'Existing embedded site photographs; continuous arc-length coordinates, no overlay faces','core_removed_m3':0,'ground_positive_components':len(body.decompose())}}
(D/'Prepared_Site.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('SITE_PREPARED',body.volume(),body.num_tri(),len(body.decompose()),flush=True)
