"""Independent hybrid QA. Source reads only; writes reports under work audit.
Checks exact native base arrays/IDs/materials, patch XY invariance, and edge z.
"""
import sys,json,math,hashlib,collections,csv
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from scipy.spatial import cKDTree
O=Path(__file__).parent;PROJECT=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid');BASE=Path(r'E:\jz\纯场地版本.3dm');NATIVE=PROJECT/'04_Rhino/Reality_Hybrid_V6.3dm'

def digest(a,dtype):
 a=np.asarray(a,dtype=dtype);return hashlib.sha256(a.tobytes()).hexdigest()
def mesh_data(m):
 return {'vertices':np.array([[p.X,p.Y,p.Z] for p in m.Vertices]),'faces':np.array(list(m.Faces),np.int32),'uv':np.array([[p.X,p.Y] for p in m.TextureCoordinates]),'normals':np.array([[p.X,p.Y,p.Z] for p in m.Normals]),'colors':np.array(list(m.VertexColors),np.uint8)}
def serial(x):
 if isinstance(x,(float,int,str,bool)) or x is None:return x
 if isinstance(x,(list,tuple)):return [serial(y) for y in x]
 if hasattr(x,'X'):return [getattr(x,k) for k in ['X','Y','Z'] if hasattr(x,k)]
 return str(x)
def material_fixed(m):
 keys=['Id','Name','AmbientColor','DiffuseColor','SpecularColor','ReflectionColor','EmissionColor','TransparentColor','DisableLighting','IndexOfRefraction','FresnelIndexOfRefraction','FresnelReflections','Transparency','Reflectivity','Shine','ReflectionGlossiness','RefractionGlossiness','RenderMaterialInstanceId','RenderPlugInId'];return {k:serial(getattr(m,k)) for k in keys}
def texture_fixed(t):
 if not t:return None
 r={k:serial(getattr(t,k)) for k in ['Id','Enabled','TextureType','WrapU','WrapV','WrapW','Repeat','Offset','Rotation']};r['UvwTransform']=[[getattr(t.UvwTransform,'M'+str(i)+str(j)) for j in range(4)] for i in range(4)];return r

def closest_xy(q,t):
 # q [N,2], t [N,3,3]. Exact in-triangle plane interpolation, or nearest edge.
 p=t[:,:,:2];a=p[:,0];u=p[:,1]-a;v=p[:,2]-a;r=q-a;den=u[:,0]*v[:,1]-u[:,1]*v[:,0];b=(r[:,0]*v[:,1]-r[:,1]*v[:,0])/den;c=(u[:,0]*r[:,1]-u[:,1]*r[:,0])/den;w=np.column_stack([1-b-c,b,c]);inside=(w.min(axis=1)>=-1e-9)
 cp=np.empty_like(q);bw=np.empty((len(q),3));cp[inside]=q[inside];bw[inside]=w[inside]
 out=np.flatnonzero(~inside)
 if len(out):
  tp=p[out];x=q[out];A=tp;B=np.roll(tp,-1,axis=1);e=B-A;lam=np.clip(np.sum((x[:,None,:]-A)*e,axis=2)/np.maximum(np.sum(e*e,axis=2),1e-20),0,1);cand=A+lam[:,:,None]*e;k=np.argmin(np.sum((cand-x[:,None,:])**2,axis=2),axis=1);ii=np.arange(len(out));cp[out]=cand[ii,k];weights=np.zeros((len(out),3));weights[ii,k]=1-lam[ii,k];weights[ii,(k+1)%3]=lam[ii,k];bw[out]=weights
 return np.linalg.norm(cp-q,axis=1),np.sum(bw*t[:,:,2],axis=1)

def surface_candidates(q,tri,k=64):
 if not len(tri):return None
 tree=cKDTree(tri[:,:,:2].mean(axis=1));kk=min(k,len(tri));d,ids=tree.query(q,k=kk,workers=4);ids=ids.reshape(len(q),kk);tt=tri[ids].reshape(-1,3,3);qq=np.repeat(q,kk,axis=0);dist,z=closest_xy(qq,tt);return dist.reshape(len(q),kk),z.reshape(len(q),kk),ids

def is_ground_patch(row):
 # Ground QA excludes shed roofs, wall tops, trees, furniture, and upper slabs.
 # Layer 60_SITE alone is insufficient: it includes all courtyard structures.
 return row['name'] in {
  'SLAB_JOINED_F1','SITE_MAIN_COURTYARD_PAVING','SITE_WEST_EARTH_COURTYARD',
  'SITE_CURVED_PUBLIC_ROAD','SITE_CONTEXT_TERRAIN','SITE_SOUTH_EAST_ANNEX_FLOOR',
  'SITE_KITCHEN_STONE_FLOOR','SITE_SW_GATE_APPROACH','SITE_SW_GATE_THRESHOLD'
 } or row['name']=='PHOTO_BOUNDARY_GROUND_RECOVERY'

def run():
 required=[NATIVE,PROJECT/'02_Data/Patch_Index.json',PROJECT/'02_Data/Materials.json',PROJECT/'02_Data/Hole_Polygon.json']
 missing=[str(p) for p in required if not p.exists()]
 if missing:print(json.dumps({'status':'WAITING_FOR_HYBRID_EXPORT','missing':missing},ensure_ascii=False));return
 A=rh.File3dm.Read(str(BASE));B=rh.File3dm.Read(str(NATIVE));checks=[]
 def ck(id,ok,detail,status=None):checks.append({'id':id,'status':status or ('PASS' if ok else 'FAIL'),'detail':detail})
 ck('Source_copy_file_hash',hashlib.sha256(BASE.read_bytes()).hexdigest()==hashlib.sha256((PROJECT/'01_Source/Pure_Site_UNMODIFIED.3dm').read_bytes()).hexdigest(),{})
 ck('Model_units_unchanged',A.Settings.ModelUnitSystem==B.Settings.ModelUnitSystem,{'source':str(A.Settings.ModelUnitSystem),'hybrid':str(B.Settings.ModelUnitSystem)})
 OB={str(o.Attributes.Id):o for o in B.Objects if type(o.Geometry).__name__=='Mesh' and not o.Attributes.IsInstanceDefinitionObject};base_rows=[];base_ground=[];coord=json.loads((PROJECT/'02_Data/Coordinate.json').read_text(encoding='utf-8'));angle=math.radians(coord['rotation_deg']);c=math.cos(angle);s=math.sin(angle);R=np.array([[c,-s,0],[s,c,0],[0,0,1]]);origin=np.array(coord['origin'])
 for i,ob in enumerate(A.Objects):
  id=str(ob.Attributes.Id);new=OB.get(id);ck('Base_object_ID_'+str(i),new is not None,{'source_id':id})
  if new is None:continue
  d=mesh_data(ob.Geometry);e=mesh_data(new.Geometry);hashes={}
  for key in ['vertices','faces','uv','normals','colors']:
   typ=np.int32 if key=='faces' else np.uint8 if key=='colors' else np.float32;ha=digest(d[key],typ);hb=digest(e[key],typ);ok=d[key].shape==e[key].shape and ha==hb;hashes[key]={'source':ha,'hybrid':hb,'shape':list(d[key].shape),'same':ok};ck('Base_'+str(i)+'_'+key,ok,hashes[key])
  ck('Base_material_index_'+str(i),ob.Attributes.MaterialIndex==new.Attributes.MaterialIndex and ob.Attributes.MaterialSource==new.Attributes.MaterialSource,{'source_index':ob.Attributes.MaterialIndex,'hybrid_index':new.Attributes.MaterialIndex})
  ma=A.Materials[ob.Attributes.MaterialIndex];mb=B.Materials[new.Attributes.MaterialIndex];ck('Base_material_ID_and_appearance_'+str(i),material_fixed(ma)==material_fixed(mb),{'source':material_fixed(ma),'hybrid':material_fixed(mb)})
  ta=ma.GetBitmapTexture();tb=mb.GetBitmapTexture();ck('Base_texture_ID_transform_'+str(i),texture_fixed(ta)==texture_fixed(tb),{'source':texture_fixed(ta),'hybrid':texture_fixed(tb)})
  src=Path(ta.FileName);copy=PROJECT/'03_Textures/Base'/src.name;sha=hashlib.sha256(src.read_bytes()).hexdigest();shb=hashlib.sha256(copy.read_bytes()).hexdigest() if copy.exists() else None;ck('Base_texture_bits_'+str(i),sha==shb,{'source':str(src),'copy':str(copy),'source_sha256':sha,'copy_sha256':shb,'native_binding':tb.FileName})
  base_rows.append({'index':i,'id':id,'arrays':hashes})
  v=(d['vertices']-origin)@R;f=d['faces'];tri=np.concatenate([v[f[:,:3]],v[f[f[:,2]!=f[:,3]][:,[0,2,3]]]]) if np.any(f[:,2]!=f[:,3]) else v[f[:,:3]];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);nn=np.linalg.norm(n,axis=1);ground=(np.abs(n[:,2])>=.5*nn)&(nn>1e-10);base_ground.append(tri[ground])
 print('Native original base arrays/material IDs checked',flush=True)
 HJ=json.loads((PROJECT/'02_Data/Hole_Polygon.json').read_text(encoding='utf-8'));H=Polygon(HJ['local']['outer'],HJ['local']['holes']);index=json.loads((PROJECT/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));coverage=[];outside_total=0.;inside_islands_total=0.;bad=[];patch_ground=[];ground_labels=[];counts=collections.Counter()
 for row in index:
  d=np.load(PROJECT/'02_Data'/row['file']);v=d['vertices'];tri=v[d['faces']];uv=d['uv'];mid=d['material_ids'];ck('Patch_data_'+row['name'],np.isfinite(v).all() and np.isfinite(uv).all() and len(uv)==len(v) and len(mid)==len(tri) and mid.min()>=0 and mid.max()<len(row['materials']),{'triangles':len(tri),'vertices':len(v),'materials':len(row['materials'])})
  xy=tri[:,:,:2];area=np.abs(np.cross(xy[:,1]-xy[:,0],xy[:,2]-xy[:,0]))/2;mask=area>1e-10;shapes=shapely.polygons(xy[mask]);partcov=shapely.union_all(shapes);outside=partcov.difference(H);out=outside.area;outside_total+=out;coverage.append(partcov);counts['positive_xy_triangles']+=int(mask.sum());counts['all_patch_triangles']+=len(tri)
  if out>1e-8:bad.append({'node':row['name'],'outside_m2':out})
  for ring in H.interiors:inside_islands_total+=partcov.intersection(Polygon(ring)).area
  layer=row['element'].get('layer');role=row.get('role');n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);nn=np.linalg.norm(n,axis=1)
  if is_ground_patch(row):
   g=(np.abs(n[:,2])>=.5*nn)&(nn>1e-10);patch_ground.append(tri[g]);ground_labels.extend([row['name']]*int(g.sum()))
 covered=unary_union(coverage);residual=H.difference(covered);outside=covered.difference(H);ck('Patch_projected_scope',outside.area<1e-7,{'union_outside_m2':outside.area,'sum_node_outside_m2':outside_total,'nodes_outside':bad});ck('Three_source_islands_preserved',inside_islands_total<1e-7,{'inner_ring_count':len(H.interiors),'sum_patch_overlap_m2':inside_islands_total});ck('Main_hole_projected_residual',residual.area<1e-5,{'hole_m2':H.area,'covered_m2':covered.intersection(H).area,'residual_m2':residual.area})
 (O/'Hybrid_XY_Residual.json').write_text(json.dumps({'residual_area_m2':residual.area,'parts':[{'outer':[list(p) for p in q.exterior.coords],'holes':[[list(p) for p in r.coords] for r in q.interiors]} for q in ([residual] if residual.geom_type=='Polygon' else list(residual.geoms)) if q.geom_type=='Polygon' and not q.is_empty]},ensure_ascii=False,indent=2),encoding='utf-8')
 print('Independent patch XY coverage complete',counts,'residual',residual.area,flush=True)
 # Visible-ground seam samples: compare interpolated actual source ground and the
 # nearest compatible patch ground at the same XY. This does not certify watertightness.
 boundary=H.exterior;samples=[boundary.interpolate(float(d)).coords[0] for d in np.linspace(0,boundary.length,max(400,int(boundary.length/.15)),endpoint=False)];q=np.array(samples);base_tri=np.concatenate(base_ground);patch_tri=np.concatenate(patch_ground);source=surface_candidates(q,base_tri);patch=surface_candidates(q,patch_tri);rows=[]
 if source is not None and patch is not None:
  ds,zs,si=source;dp,zp,pi=patch
  for j,xy in enumerate(q):
   near=ds[j]<max(1e-5,float(ds[j].min())+1e-5);iz=np.flatnonzero(near)[np.argmin(zs[j,near])];sourcez=float(zs[j,iz]);valid=(dp[j]<=.03)
   if ds[j,iz]>.03 or not valid.any():rows.append({'x':xy[0],'y':xy[1],'status':'NO_COMPATIBLE_GROUND_NEAR_BOUNDARY','source_xy_distance_m':float(ds[j,iz]),'nearest_patch_xy_m':float(dp[j].min())});continue
   valid_ids=np.flatnonzero(valid);jj=int(valid_ids[np.argmin(np.abs(zp[j,valid]-sourcez))]);delta=float(zp[j,jj]-sourcez);rows.append({'x':xy[0],'y':xy[1],'status':'MATCHED','source_z_local_m':sourcez,'patch_z_local_m':float(zp[j,jj]),'delta_z_m':delta,'source_xy_distance_m':float(ds[j,iz]),'patch_xy_distance_m':float(dp[j,jj]),'patch_node':ground_labels[int(pi[j,jj])]})
  matched=[r for r in rows if r['status']=='MATCHED'];err=np.array([abs(r['delta_z_m']) for r in matched]);seam={'method':'Exterior XY ring sampled every <=0.15m. Source ground |normalZ|>=0.5 selects lowest surface within nearest 0.03m XY; patch compatible ground selected within0.03m XY and closest interpolated z. Ground only; not wall/roof watertightness.','sample_count':len(rows),'matched_count':len(matched),'unmatched_count':len(rows)-len(matched),'absolute_dz_m':dict(zip(['p50','p95','p99','max'],np.quantile(err,[.5,.95,.99,1]).tolist())) if len(err) else None,'count_over_0p02m':int(np.sum(err>.02)),'count_over_0p05m':int(np.sum(err>.05)),'count_over_0p10m':int(np.sum(err>.10)),'worst_samples':sorted(matched,key=lambda r:abs(r['delta_z_m']),reverse=True)[:20]}
  ck('Boundary_ground_height',bool(len(err)) and np.quantile(err,.95)<=.02 and np.max(err)<=.05,seam,status=('PASS' if len(err) and np.quantile(err,.95)<=.02 and np.max(err)<=.05 else 'NEEDS_EDGE_HEIGHT_REVIEW'))
 else:ck('Boundary_ground_height',False,'No source/patch ground candidates',status='NEEDS_EDGE_HEIGHT_REVIEW');seam={}
 (O/'Hybrid_Boundary_Height_QA.json').write_text(json.dumps(seam,ensure_ascii=False,indent=2),encoding='utf-8')
 keys=sorted({k for r in rows for k in r})
 if keys:
  with (O/'Hybrid_Boundary_Height_Samples.csv').open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,keys);wr.writeheader();wr.writerows(rows)
 counts=collections.Counter(c['status'] for c in checks);report={'native':str(NATIVE),'native_sha256':hashlib.sha256(NATIVE.read_bytes()).hexdigest(),'source_base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'patch_index_sha256':hashlib.sha256((PROJECT/'02_Data/Patch_Index.json').read_bytes()).hexdigest(),'status_counts':dict(counts),'checks':checks,'base_array_hashes':base_rows,'scope':'Independent exact native base invariance and local XY patch scope. Height results are surface compatibility checks, not a construction/survey certification.'};(O/'Hybrid_V6_Independent_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');lines=['# V6 独立核查','','原五网格数组、UUID、材质与贴图比特；补块范围与地表边界核查。',f'结果：{dict(counts)}','']
 for c in checks:
  if c['status']!='PASS' or not c['id'].startswith(('Patch_data_','Base_')):lines.append(f"- {c['status']} — {c['id']}: {json.dumps(c['detail'],ensure_ascii=False)}")
 (O/'Hybrid_V6_Independent_QA.md').write_text('\n'.join(lines),encoding='utf-8');print(json.dumps({'status_counts':dict(counts),'scope_outside_m2':outside.area,'residual_m2':residual.area,'ground_seam':seam},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
