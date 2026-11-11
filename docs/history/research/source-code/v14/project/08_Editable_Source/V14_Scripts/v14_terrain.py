import sys,json,math,collections,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,shapely,rhino3dm as rh,export_v5 as ex
from shapely.geometry import Polygon,box,mapping
O=W/'v14';D=O/'data';D.mkdir(exist_ok=True)
B=Path(r'E:\jz\JIA\Rebuild_V13');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));ex.SCENE=S
H=json.loads(Path(r'E:\jz\JIA\Rebuild_V11_Hybrid\02_Data\Hole_Polygon.json').read_text(encoding='utf8'))
mask=Polygon(H['local']['outer']).buffer(0)
# Clear source islands in the original central void as well as the revised storage footprint.
mask=mask.union(box(13.3,-16.55,21.75,-9.4)).buffer(0)
for e in S['elements']:
 if 'SITE_V12_OUTER_GATE' in e['name'] and 'RAMP' in e['name']:
  for p in e['parts']:
   v,fs=ex.world_part(p,e);mask=mask.union(Polygon(v[:,:2]).convex_hull)
mask=mask.buffer(0)
json.dump(mapping(mask),(O/'Merge_Boundary_LOCAL.json').open('w',encoding='utf8'),ensure_ascii=False,indent=2)
def polys(g):return [g] if g.geom_type=='Polygon' else [q for q in getattr(g,'geoms',[]) if q.geom_type=='Polygon']
def clipped(v,f,uv,inside):
 t=v[f];area=abs(np.cross(t[:,1,:2]-t[:,0,:2],t[:,2,:2]-t[:,0,:2]));valid=area>1e-14
 p=shapely.polygons(t[:,:,:2]);covers=shapely.covers(mask,p);hits=shapely.intersects(mask,p)
 keep=covers if inside else ~hits
 # Vertical source faces carry their real wall heights and UVs outside the central void.
 keep[~valid]=shapely.contains_xy(mask,t[~valid].mean(1)[:,0],t[~valid].mean(1)[:,1]) if inside else ~shapely.contains_xy(mask,t[~valid].mean(1)[:,0],t[~valid].mean(1)[:,1])
 out=t[keep].reshape(-1,3).tolist();u=uv[f[keep]].reshape(-1,2).tolist();ff=np.arange(len(out)).reshape(-1,3).tolist();partial=np.where(hits&~covers&valid)[0]
 for i in partial:
  g=p[i].intersection(mask) if inside else p[i].difference(mask)
  a=t[i];mat=np.vstack([a[:,:2].T,np.ones(3)]);inv=np.linalg.inv(mat)
  for pp in polys(g):
   if pp.area<1e-12:continue
   for tri in shapely.constrained_delaunay_triangles(pp).geoms:
    xy=np.array(tri.exterior.coords[:-1]);weights=np.c_[xy,np.ones(3)]@inv.T;q=weights@a;quv=weights@uv[f[i]]
    if np.dot(np.cross(q[1]-q[0],q[2]-q[0]),np.cross(a[1]-a[0],a[2]-a[0]))<0:q=q[::-1];quv=quv[::-1]
    k=len(out);out.extend(q.tolist());u.extend(quv.tolist());ff.append([k,k+1,k+2])
 out=np.asarray(out).reshape(-1,3);ff=np.asarray(ff,np.int32).reshape(-1,3);u=np.asarray(u).reshape(-1,2);tt=out[ff]
 edge=np.linalg.norm(np.roll(tt,-1,axis=1)-tt,axis=2).min(1);area3=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)
 nondeg=(edge>1e-7)&(area3>1e-10)
 # Coincident source vertices and exact boundary slivers have no displayable area.
 # Discard only these degenerate triangles; preserve every remaining source coordinate and UV.
 print('DEGENERATE REMOVED',int((~nondeg).sum()),'AREA',float(area3[~nondeg].sum()/2),flush=True)
 ids=ff[nondeg].ravel();out=out[ids];u=u[ids];ff=np.arange(len(out),dtype=np.int32).reshape(-1,3)
 return out,ff,u,int(keep.sum()),len(partial)
def closed_top(v,f):
 # Coordinate weld retains exact interpolated heights and closes only the new interior patch.
 q,iv=np.unique(np.round(v,7),axis=0,return_inverse=True);fs=iv[f];N=len(q);bottom=q.copy();bottom[:,2]-=.20
 edges=collections.Counter(tuple(sorted((int(a),int(b)))) for t in fs for a,b in zip(t,np.roll(t,-1)))
 oriented={tuple(sorted((int(a),int(b)))):(int(a),int(b)) for t in fs for a,b in zip(t,np.roll(t,-1))}
 assert not any(c>2 for c in edges.values())
 allf=fs.tolist()+(fs[:,::-1]+N).tolist()
 for e,c in edges.items():
  if c==1:
   a,b=oriented[e];allf.extend([[b,a,a+N],[b,a+N,b+N]])
 return {'type':'polyhedron','vertices':np.vstack([q,bottom]).tolist(),'faces':allf}
new=[];replace=[];remove=[];rows=[]
for e in S['elements']:
 if not e['name'].startswith(('SITE_V12_REBUILT_EARTH','SITE_V12_REBUILT_ROAD','SITE_V12_REBUILT_COURT')):continue
 vv=[];ff=[];offset=0
 for p in e['parts']:
  v,fs=ex.world_part(p,e);fs=np.array([f for f in fs if len(f)==3]+[t for f in fs if len(f)==4 for t in [[f[0],f[1],f[2]],[f[0],f[2],f[3]]]],np.int32)
  n=np.cross(v[fs[:,1]]-v[fs[:,0]],v[fs[:,2]]-v[fs[:,0]]);fs=fs[n[:,2]>1e-10]
  vc,fc,_,whole,cut=clipped(v,fs,v[:,:2],True)
  if len(fc):vv.append(vc);ff.append(fc+offset);offset+=len(vc)
 if not ff:remove.append(e['name']);continue
 g=closed_top(np.vstack(vv),np.vstack(ff));e=dict(e);e['parts']=[{'geometry':g,'material':e['parts'][0]['material']}];e['v14_scope']='Modeled interior only; outside replaced by original pure-site texture meshes';replace.append(e)
 print('CLIPPED INTERIOR',e['name'],len(g['faces']),flush=True)
C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);F=rh.File3dm.Read(r'E:\jz\纯场地版本.3dm')
for i,ob in enumerate(F.Objects):
 m=ob.Geometry;v=np.array([[p.X,p.Y,p.Z] for p in m.Vertices]);v=(v-origin)@R;f=[]
 for z in m.Faces:
  f.append(z[:3])
  if z[2]!=z[3]:f.append([z[0],z[2],z[3]])
 f=np.array(f,np.int32);uv=np.array([[p.X,p.Y] for p in m.TextureCoordinates]);vc,fc,uc,whole,cut=clipped(v,f,uv,False)
 name='SITE_V14_ORIGINAL_EXTERIOR_'+str(i);mat='M_V14_ORIGINAL_EXTERIOR_'+str(i);filename=name+'.npz';np.savez_compressed(D/filename,vertices=vc,faces=fc,uv=uc,material_ids=np.zeros(len(fc),np.int32))
 e={'name':name,'layer':'80_CONTEXT','family':'EXTERIOR_SOURCE_SITE','parts':[],'external_mesh_file':filename,'source':'E:/jz/纯场地版本.3dm','source_mesh_id':str(ob.Attributes.Id),'source_material_index':ob.Attributes.MaterialIndex,'confidence':'SOURCE','v14_scope':'Original exterior retained, central reconstruction masked out; UV barycentrically preserved at cut edges'};new.append(e)
 rows.append({'name':name,'source_triangles':len(f),'uncut_triangles':whole,'cut_source_triangles':cut,'output_triangles':len(fc),'materials':[mat],'source_vertex_uv_sha256':hashlib.sha256(v.tobytes()+uv.tobytes()).hexdigest()})
 print('EXTERIOR',i,len(fc),flush=True)
out={'replace':replace,'remove':remove,'add':new,'source_rows':rows,'mask_area_m2':mask.area,'source_sha256':hashlib.sha256(Path(r'E:\jz\纯场地版本.3dm').read_bytes()).hexdigest()}
(O/'Terrain_Mutation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('DONE',len(replace),len(remove),flush=True)
