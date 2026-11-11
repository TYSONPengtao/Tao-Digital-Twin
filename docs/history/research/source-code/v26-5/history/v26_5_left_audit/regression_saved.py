from pathlib import Path
import sys,json,hashlib,datetime
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,cube,union,section
OLD=W/'v26_4/Final';NEW=W/'v26_5/Final';OI={r['name']:r for r in json.loads((OLD/'Geometry_Index.json').read_text('utf8'))};NI={r['name']:r for r in json.loads((NEW/'Geometry_Index.json').read_text('utf8'))}
MODEL=Path('E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend');expected=sys.argv[1] if len(sys.argv)>1 else '93714f92b665c81808d656501e26660658e8bef0d156bb68c4b16d9876ca0758';report={'model':str(MODEL),'model_sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'basis':'Fresh native saved V26.5 export independently compared to fresh native V26.4 export; no prepared replacement meshes used for final tests.','checks':[],'failures':[]};cache={}
def ck(name,value,**data):
 r={'name':name,'pass':bool(value),**data};report['checks'].append(r)
 if not value:report['failures'].append(r)
 print('CHECK',name,bool(value),flush=True)
def arr(d,ind,n):return np.load(d/ind[n]['file'])
def load(d,ind,n,mat=None):
 key=(str(d),n,mat)
 if key not in cache:
  a=arr(d,ind,n);f=a['f'] if mat is None else a['f'][a['mi']==mat];cache[key]=solid(a['v'],f,n)
 return cache[key]
def sample_surface(m):
 a=m.to_mesh64();v=np.asarray(a.vert_properties)[:,:3];f=np.asarray(a.tri_verts);t=v[f]
 return np.vstack([v,t.mean(1),.5*(t[:,0]+t[:,1]),.5*(t[:,1]+t[:,2]),.5*(t[:,2]+t[:,0])])
def exact_triangle_distance_bound(points,m):
 a=m.to_mesh64();t=np.asarray(a.vert_properties)[:,:3][np.asarray(a.tri_verts)];out=[]
 for j in range(0,len(points),8):
  Q=points[j:j+8,None,:];T=t[None,:,:,:];A=T[:,:,1]-T[:,:,0];B=T[:,:,2]-T[:,:,0];V=Q-T[:,:,0];aa=np.sum(A*A,-1);bb=np.sum(B*B,-1);ab=np.sum(A*B,-1);aq=np.sum(A*V,-1);bq=np.sum(B*V,-1);det=np.maximum(aa*bb-ab*ab,1e-30);u=(bb*aq-ab*bq)/det;w=(aa*bq-ab*aq)/det;N=np.cross(A,B);dd=np.sum(V*N,-1)**2/np.maximum(np.sum(N*N,-1),1e-30);dd=np.where((u>=-1e-10)&(w>=-1e-10)&(u+w<=1+1e-10),dd,np.inf)
  for k in range(3):
   P=T[:,:,k];E=T[:,:,(k+1)%3]-P;fac=np.clip(np.sum((Q-P)*E,-1)/np.maximum(np.sum(E*E,-1),1e-30),0,1);dd=np.minimum(dd,np.sum((Q-P-fac[:,:,None]*E)**2,-1))
  out.extend(np.sqrt(np.maximum(0,dd.min(1))).tolist())
 return float(max(out,default=0))
ck('Saved model hash matches exact tested delivery',report['model_sha256']==expected)
HN='V26_3_House_Connected_Walls_And_Stairs';OH=load(OLD,OI,HN);NH=load(NEW,NI,HN)
bays=[n for n in OI if n.startswith('BAY_WINDOW_')]
for n in bays:
 a=arr(OLD,OI,n);b=arr(NEW,NI,n);keys=['v','f','mi','uv'];same={k:bool(np.array_equal(a[k],b[k]))for k in keys};ck('Original bay frame and glass mesh exact: '+n,all(same.values())and OI[n]['materials']==NI[n]['materials'],arrays_exact=same,materials_exact=OI[n]['materials']==NI[n]['materials'])
# Native manifold and edge topology, not reconstructed replacement stats.
a=arr(NEW,NI,HN);edges=np.sort(np.vstack([a['f'][:,[0,1]],a['f'][:,[1,2]],a['f'][:,[2,0]]]),axis=1);_,ct=np.unique(edges,axis=0,return_counts=True)
ck('Native corrected house remains one closed solid',NH.status()==mf.Error.NoError and len(NH.decompose())==1 and bool((ct==2).all()),components=len(NH.decompose()),nonmanifold_edge_count=int((ct!=2).sum()),volume_m3=NH.volume())
# Four explicitly reported tile penetrations, separately against actual clear glass.
G=load(NEW,NI,'BAY_WINDOW_F1_L_0_Geometry',1);F=load(NEW,NI,'BAY_WINDOW_F1_L_0_Geometry')
pre='SITE_COURTYARD_WEST_TILE_WALL_';keys=['TILE_COPING','V10_COVER_TILES','V10_LOTUS_DRIP_ENDS','V10_PAN_TILES']
for k in keys:
 n=pre+k+'_Geometry';o=load(OLD,OI,n);m=load(NEW,NI,n);before=(o^G).volume();after=(m^G).volume();frame=(m^F).volume();ck('Reported tile intrusion cleared: '+k,before>1e-8 and abs(after)<1e-9 and abs(frame)<1e-9,before_glass_intersection_m3=before,after_glass_intersection_m3=after,after_complete_frame_intersection_m3=frame)
# All changes limited to prescribed tiny courtyard/window junction prism.
norm=np.array([.8111365302967483,.5848568450639461]);limit=1.1723606549172076;poly=[[(limit-norm[1]*y)/norm[0],y]for y in [.7,2.3]]+[[1.,2.3],[1.,.7]];cut=section(poly,3.5).translate([0,0,-.7]);ck('Cut plane is 10 mm exterior of original window frame',abs(1.1823606549172077-limit-.010)<1e-12,normal_xy=norm.tolist(),limit_m=limit)
localnames=[n for n in OI if n.startswith(pre)]+['V26_1_Courtyard_West_Wall_Single_Surface']
for n in localnames:
 o=load(OLD,OI,n);m=load(NEW,NI,n);added=(m-o).volume();lost_outside=((o-m)-cut).volume();residual=(m^cut).volume();target=o-cut;err=(m-target).volume()+(target-m).volume();strict=abs(added)<1e-7 and abs(lost_outside)<1e-7 and abs(residual)<1e-7 and abs(err)<1e-7;surface=None;precision=False
 if not strict and max(abs(added),abs(lost_outside),abs(residual))<1e-7:
  s1=sample_surface(target);s2=sample_surface(m);d1=exact_triangle_distance_bound(s1,m);d2=exact_triangle_distance_bound(s2,target);surface={'method':'All triangle vertices, all edge midpoints and all triangle centroids checked against every opposite triangle; no nearest-centroid shortcut','expected_to_native_samples':len(s1),'native_to_expected_samples':len(s2),'expected_to_native_max_sampled_m':d1,'native_to_expected_max_sampled_m':d2,'native_float32_surface_tolerance_m':1e-6};precision=max(d1,d2)<1e-6
 ck('Courtyard change localized within native save precision: '+n,strict or precision,strict_boolean_volume_gate=bool(strict),direct_float32_surface_gate=bool(precision),surface_comparison=surface,added_volume_m3=added,lost_outside_local_prism_m3=lost_outside,residual_inside_cut_m3=residual,expected_cut_symmetric_difference_m3=err,removed_volume_m3=o.volume()-m.volume())
# Actual original cores checked independently, with source mesh and baseline comparison.
PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))};proof=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components'];cores=[];coredetails=[]
for r in proof:
 n=r['name']
 if not n.startswith(('KZ_','BEAM_','ROOF_')):continue
 a=arr(PD,PI,n);c=solid(a['v'],a['f'],n);cores.append(c);was=c^OH;now=c^NH;lost=(was-now).volume();missing=(c-NH).volume();coredetails.append({'name':n,'baseline_retained_volume_m3':was.volume(),'retained_now_m3':now.volume(),'lost_from_baseline_m3':lost,'total_source_missing_m3':missing})
C=union(cores);bad=[r for r in coredetails if r['lost_from_baseline_m3']>1e-6];ck('No original beam column or roof core lost',not bad,core_count=len(coredetails),maximum_core_loss_m3=max(r['lost_from_baseline_m3']for r in coredetails),details=coredetails)
new_added=NH-OH
for fl,s,base in [(1,'L',0.),(2,'L',0.),(1,'R',9.1),(2,'R',9.1),(3,'R',9.1)]:
 ns=[f'BAY_WINDOW_F{fl}_{s}_{i}_Geometry'for i in range(3)];lo,hi=np.array(NI[ns[1]]['bounds']);boxes=[cube([base+.55,.98,lo[2]],[base+.95,1.25,hi[2]]),cube([base+2.95,.98,lo[2]],[base+3.35,1.25,hi[2]])];full=union(boxes);cutter=full-C;oldvol=(OH^cutter).volume();remaining=(NH^cutter).volume();protected_old=OH^full^C;protected_new=NH^full^C;lost=(protected_old-protected_new).volume();ck(f'Obsolete opaque corner fins removed: F{fl}_{s}',oldvol>.01 and abs(remaining)<1e-7 and lost<1e-7,before_unprotected_fin_volume_m3=oldvol,remaining_unprotected_fin_m3=remaining,protected_roof_or_core_volume_m3=protected_new.volume(),protected_core_loss_m3=lost)
 nearbay=cube([base-.25,.9,lo[2]],[base+4.15,2.4,hi[2]]);added_near_bay=(new_added^nearbay).volume();ck(f'No new opaque cover within complete bay aperture region: F{fl}_{s}',abs(added_near_bay)<1e-8,new_opaque_in_front_bay_region_m3=added_near_bay,region_bounds=[[base-.25,.9,float(lo[2])],[base+4.15,2.4,float(hi[2])]])
 gg=union([load(NEW,NI,n,1)for n in ns]);intrusion=(new_added^gg).volume();ck(f'No new opaque closure over original bay glass: F{fl}_{s}',abs(intrusion)<1e-8,new_opaque_inside_glass_m3=intrusion,original_glass_volume_m3=gg.volume())
report['status']='PASS'if not report['failures']else'FAIL';report['check_count']=len(report['checks']);out=Path('E:/jz/JIA/Rebuild_V26_5/Reports/V26_5_Bay_Clearance_Regression_QA.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print('BAY_REGRESSION_DONE',report['status'],report['check_count'],len(report['failures']),str(out),flush=True)
