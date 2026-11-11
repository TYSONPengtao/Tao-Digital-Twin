"""Repair the annotated residual floor, timber, and southern wall interfaces."""
import sys,json,math
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_33';sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from scipy.spatial import cKDTree
from v24_16_common import solid,cube,union
I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};cache={};changed={};OUT={'raw_objects':[],'remove':[],'proof':{}}
def src(n):return np.load(D/I[n]['file'])
def load(n):
 if n not in cache:
  a=src(n)
  try:cache[n]=solid(a['v'],a['f'],n)
  except RuntimeError:
   for dec in [9,8,7,6]:
    v,iv=np.unique(np.round(a['v'],dec),axis=0,return_inverse=True);f=iv[a['f']];tr=v[f];ok=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)>1e-14;f=f[ok];_,ids=np.unique(np.sort(f,axis=1),axis=0,return_index=True);f=f[np.sort(ids)]
    try:cache[n]=solid(v,f,n);break
    except RuntimeError:pass
   if n not in cache:raise RuntimeError('Cannot make original source solid: '+n)
 return cache[n]
def stage(n,m,**kw):
 assert m.status()==mf.Error.NoError and m.volume()>0,(n,m.status(),m.volume())
 changed[n]=(m,kw);print('STAGE',n,round(m.volume(),6),flush=True)
floors={2:float(src('SLAB_JOINED_F2_Geometry')['v'][:,2].max()),3:float(src('SLAB_JOINED_F3_Geometry')['v'][:,2].max())};floorproof=[]
for fl,z in floors.items():
 slab=f'SLAB_JOINED_F{fl}_Geometry';part=f'PARTITIONS_JOINED_F{fl-1}_Geometry';z0=float(src(slab)['v'][:,2].min());mask=cube([4.,7.19999,z0],[8.90001,7.40001,z+.000001]);p=load(part);cap=p^mask
 stage(part,p-mask)
 # The previous story wall occupied the floor band. Transfer that band into
 # the real slab, with a single continuous concrete top at the same level.
 stage(slab,union([load(slab),cap]),slab_materials=True)
 floorproof.append({'floor':fl,'top_z_m':z,'bottom_z_m':z0,'cap_transferred_m3':cap.volume(),'source_wall':part,'floor_owner':slab,'front_edge_y_m':7.4,'stair_void_beyond_y_7_4_retained':True})
OUT['proof']['floor_white_strips']=floorproof
OUT['remove'].append('CONSTRUCTION_TERRACE_SLOPED_FINISH_Geometry')
OUT['proof']['terrace_overlay']={'removed':'CONSTRUCTION_TERRACE_SLOPED_FINISH_Geometry','maximum_raise_m':float(src('CONSTRUCTION_TERRACE_SLOPED_FINISH_Geometry')['v'][:,2].max())-floors[3],'real_slab_preserved':'SLAB_JOINED_F3_Geometry','finished_floor_z_m':floors[3]}
# Clip only the portion of the centre porch roof that penetrated the usable
# F3 terrace, without altering its visible front or the main roof silhouette.
roof_clear_z=float(src('SLAB_JOINED_F3_Geometry')['v'][:,2].min())-.001
clip=cube([-.2,1.2,roof_clear_z],[3.8,7.25,9.5]);roofproof=[]
for n in ['CANOPY_CENTER_0_Geometry','CANOPY_CENTER_INDIVIDUAL_COVER_TILES_Geometry']:
 m=load(n);new=m-clip;stage(n,new);roofproof.append({'object':n,'removed_intrusion_m3':m.volume()-new.volume(),'terrace_clearance_box':[[-.2,1.2,roof_clear_z],[3.8,7.25,9.5]]})
OUT['proof']['terrace_roof_intrusion']=roofproof
# Remove the north-end legacy column pieces identified by rays from the
# matching 042705 view. Keep the other stations and the real eave beams.
timber=[]
for n in ['SITE_KITCHEN_V12_UPPER_FACADE_COLUMN_CONTINUATIONS_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_29_Geometry','V24_06_Kitchen_Carved_Bracket_Heads']:
 m=load(n);new=m-cube([9.30,-3.45,1.8],[9.85,-2.60,3.17]);stage(n,new);timber.append({'object':n,'removed_north_end_m3':m.volume()-new.volume()})
n='SITE_KITCHEN_V12_BEFORE_WOOD_35_Geometry';m=load(n);new=m-cube([9.30,-2.867,-1],[9.85,-2.60,3.17]);stage(n,new);timber.append({'object':n,'trimmed_hidden_end_to_y_m':-2.867,'removed_m3':m.volume()-new.volume()})
OUT['proof']['kitchen_timber']=timber
# The old threshold covers the newly graded approach and the gallery sheet
# overlaps it. Retire both layers and join a flush gallery into the approach.
OUT['remove']+=['V24_10_Entry_Continuous_Threshold','SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry'];road='V24_31_Continuous_Gray_Road_And_Storage_Approach';gallery=load('SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry');gallery=gallery-cube([0,-30,-.4],[30,0,3]);combined=union([load(road),gallery]);stage(road,combined,metric_uv=True)
OUT['proof']['storage_floor']={'removed_layers':OUT['remove'][-2:],'owner':road,'gallery_final_z_m':-.4,'gallery_original_z_m':-.394,'grade_approach_retained':True,'added_gallery_volume_m3':combined.volume()-load(road).volume()}
# Remove the incorrectly white overlay on the southern end of the blue
# brick perimeter. The original masonry, photo texture, UV and coping stay.
n='SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry';m=load(n);mask=cube([10.633,-17.0,-2.],[13.25,-16.25,2.61]);new=m-mask;stage(n,new,preserve_height_attribute=True);OUT['proof']['south_brick_wall']={'removed_white_overlay_m3':m.volume()-new.volume(),'region_m':[[10.633,-17.,-2.],[13.25,-16.25,2.61]],'underlying_original_blue_wall_retained':'SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','decorated_white_frieze_and_coping_unchanged':True}
# The marked isolated terminal column is an extra cube assembly. Remove
# just this column; retain the adjacent photographed stone guard panels.
n='SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry';m=load(n);bay=json.loads((W/'v24_10/Prepared_Geometry.json').read_text('utf8'))['guard_bays'][0];a=np.array(bay['a']);b=np.array(bay['b']);u=(b-a)/np.linalg.norm(b-a);post=a-u*.08;lo=[post[0]-.1001,post[1]-.1001,-.43];hi=[post[0]+.1001,post[1]+.1001,.65];new=m-cube(lo,hi);stage(n,new);OUT['proof']['extra_stone_post']={'removed_box_m':[lo,hi],'column_center_xy_m':post.tolist(),'removed_volume_m3':m.volume()-new.volume(),'adjacent_panel_retained_and_cut_end_capped':True}
def transferred(n,v,f):
 a=src(n);old=a['v'][a['f']];oc=old.mean(1);tr=v[f];c=tr.mean(1);tree=cKDTree(oc);_,ids=tree.query(c,k=min(16,len(oc)));ids=np.asarray(ids).reshape(len(c),-1);p=old[ids];A=p[:,:,1]-p[:,:,0];B=p[:,:,2]-p[:,:,0];Q=c[:,None]-p[:,:,0];aa=np.einsum('nki,nki->nk',A,A);ab=np.einsum('nki,nki->nk',A,B);bb=np.einsum('nki,nki->nk',B,B);aq=np.einsum('nki,nki->nk',A,Q);bq=np.einsum('nki,nki->nk',B,Q);det=aa*bb-ab*ab;det=np.maximum(det,1e-24);s=(bb*aq-ab*bq)/det;t=(aa*bq-ab*aq)/det;ss=np.maximum(s,0);tt=np.maximum(t,0);total=np.maximum(1,ss+tt);ss/=total;tt/=total;near=p[:,:,0]+ss[:,:,None]*A+tt[:,:,None]*B;dist=np.linalg.norm(near-c[:,None],axis=2);pick=ids[np.arange(len(c)),dist.argmin(1)];p=old[pick];A=p[:,1]-p[:,0];B=p[:,2]-p[:,0];aa=np.einsum('ni,ni->n',A,A);ab=np.einsum('ni,ni->n',A,B);bb=np.einsum('ni,ni->n',B,B);det=np.maximum(aa*bb-ab*ab,1e-24);Q=tr-p[:,None,0];aq=np.einsum('nki,ni->nk',Q,A);bq=np.einsum('nki,ni->nk',Q,B);s=(bb[:,None]*aq-ab[:,None]*bq)/det[:,None];t=(aa[:,None]*bq-ab[:,None]*aq)/det[:,None];q=a['uv'][pick];uv=q[:,None,0]+s[:,:,None]*(q[:,None,1]-q[:,None,0])+t[:,:,None]*(q[:,None,2]-q[:,None,0]);return a['mi'][pick],uv
for n,(m,kw) in changed.items():
 a=m.to_mesh64();v=np.array(a.vert_properties[:,:3]);f=np.array(a.tri_verts);materials=I[n]['materials'];mi,uv=transferred(n,v,f)
 if kw.get('slab_materials'):
  tr=v[f];no=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-24);mi=np.zeros(len(f),dtype=int);mi[no[:,2]<-.15]=1;mi[abs(no[:,2])<.15]=2;c=tr.mean(1);mi[(abs(no[:,2])<.15)&(abs(c[:,0]-4)<.001)&(c[:,1]>7.29)&(c[:,1]<9.71)]=3
  for ax,dims in [(0,[1,2]),(1,[0,2]),(2,[0,1])]:
   mask=np.argmax(abs(no),axis=1)==ax;uv[mask]=tr[mask][:,:,dims]
 if kw.get('metric_uv'):
  tr=v[f];normal=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);axis=np.argmax(abs(normal),axis=1)
  for ax,dims in [(0,[1,2]),(1,[0,2]),(2,[0,1])]:uv[axis==ax]=tr[axis==ax][:,:,dims]
 fn='NEW_'+n+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);OUT['raw_objects'].append({'name':n,'file':fn,'materials':materials,'volume_m3':m.volume(),'components':len(m.decompose()),**kw})
(D/'Prepared_Geometry.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2),encoding='utf8');print('V33_PREPARED',len(changed),len(OUT['remove']),flush=True)
