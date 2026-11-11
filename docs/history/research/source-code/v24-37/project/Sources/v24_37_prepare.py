from pathlib import Path
import sys,json,time
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,shapely
from shapely.geometry import shape,mapping,Polygon,box
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
D=W/'v24_37';(D/'Clean').mkdir(exist_ok=True);rows=json.loads((D/'Source_Scan_Index.json').read_text());mask=shape(json.loads((D/'Complete_Scan_Retention.geojson').read_text()));projection=json.loads((W/'v24_36/Top_Projection.json').read_text());cx,cy,_=projection['center']
def xy(px,py):return (cx+(px-1200)*850/2400,cy-(py-800)*850/2400)
# Visually reviewed north extrapolation: blurred stretched green curtain above
# the detailed tree line. The source and review crop remain in the audit data.
line=[(1130,460),(1210,465),(1260,470),(1340,475),(1410,485),(1515,485),(1600,450),(1660,410)]
exclusion=Polygon([xy(*p)for p in line]+[xy(1660,0),xy(1130,0)])
(D/'Reviewed_Stretched_Skirt_Exclusion.geojson').write_text(json.dumps(mapping(exclusion)))
mask=mask.difference(exclusion).buffer(0);(D/'Final_Scan_Retention.geojson').write_text(json.dumps(mapping(mask)));shapely.prepare(mask);start=time.perf_counter();phase=[];removed=[];totbad=0;cutcount=0
def polys(g):return [g]if g.geom_type=='Polygon'else[q for q in getattr(g,'geoms',[])if q.geom_type=='Polygon']
for j,r in enumerate(rows):
 a=np.load(D/r['file']);v=a['v'];f=a['f'];uv=a['uv'];mi=a['mi'];t=v[f];tf=t.astype(np.float32).astype(float);cross=np.linalg.norm(np.cross(tf[:,1]-tf[:,0],tf[:,2]-tf[:,0]),axis=1);edge=np.max(np.linalg.norm(t-np.roll(t,1,axis=1),axis=2),axis=1);aspect=edge**2/np.maximum(cross,1e-15)
 valid3=(cross>1e-8)&(edge<6)&~((aspect>100)&(edge>1.5));totbad+=int((~valid3).sum());ar=np.abs(np.cross(t[:,1,:2]-t[:,0,:2],t[:,2,:2]-t[:,0,:2]));validxy=ar>1e-9;bb=box(*v[:,:2].min(0),*v[:,:2].max(0));partial=[]
 if shapely.covers(mask,bb):keep=valid3
 elif not shapely.intersects(mask,bb):keep=np.zeros(len(f),bool)
 else:
  pp=shapely.polygons(t[:,:,:2]);covers=shapely.covers(mask,pp);hits=shapely.intersects(mask,pp);keep=covers&valid3;keep[~validxy]=shapely.contains_xy(mask,t[~validxy].mean(1)[:,0],t[~validxy].mean(1)[:,1])&valid3[~validxy];partial=np.flatnonzero(hits&~covers&validxy&valid3)
 vv=[t[keep].reshape(-1,3)];uu=[uv[keep]];mm=[mi[keep]]
 for i in partial:
  g=pp[i].intersection(mask);at=t[i];inv=np.linalg.inv(np.vstack([at[:,:2].T,np.ones(3)]))
  for p in polys(g):
   if p.area<1e-9:continue
   for tr in shapely.constrained_delaunay_triangles(p).geoms:
    z=np.array(tr.exterior.coords[:-1]);weights=np.c_[z,np.ones(3)]@inv.T;q=weights@at;quv=weights@uv[i]
    if np.dot(np.cross(q[1]-q[0],q[2]-q[0]),np.cross(at[1]-at[0],at[2]-at[0]))<0:q=q[::-1];quv=quv[::-1]
    vv.append(q);uu.append(quv[None]);mm.append(np.array([mi[i]],np.int32))
 cutcount+=len(partial)
 if not any(len(x)for x in vv):removed.append(r['name']);continue
 if keep.all():phase.append({**r,'unchanged':True,'preclip_triangles':r['triangles']});continue
 vv=np.concatenate(vv);uu=np.concatenate(uu);mm=np.concatenate(mm);tt=vv.reshape(-1,3,3);tf=tt.astype(np.float32).astype(float);valid=np.linalg.norm(np.cross(tf[:,1]-tf[:,0],tf[:,2]-tf[:,0]),axis=1)>1e-8;vv=tt[valid].reshape(-1,3);uu=uu[valid];mm=mm[valid];vv,iv=np.unique(vv,axis=0,return_inverse=True);ff=iv.reshape(-1,3).astype(np.int32);fn='Clean/'+str(j).zfill(4)+'.npz';np.savez_compressed(D/fn,v=vv,f=ff,uv=uu,mi=mm);phase.append({**r,'file':fn,'unchanged':False,'preclip_triangles':r['triangles'],'triangles':len(ff),'vertices':len(vv),'bounds':[vv.min(0).tolist(),vv.max(0).tolist()]})
 if j%200==0:print('CLEAN_BOUNDARY',j,len(rows),'seconds',time.perf_counter()-start,flush=True)
(D/'Phase_A_Index.json').write_text(json.dumps(phase));print('BOUNDARY_DONE','kept',len(phase),'removed',len(removed),'seconds',time.perf_counter()-start,flush=True)
# Remove only tiny disconnected scraps, across source tile boundaries. Weld
# quantized vertices for connectivity, never alter display coordinates or UV.
vs=[];fs=[];offset=0;voff=[];foff=[]
for r in phase:
 a=np.load(D/r['file']);voff.append(offset);foff.append(len(a['f']));vs.append(a['v']);fs.append(a['f']+offset);offset+=len(a['v'])
v=np.concatenate(vs);f=np.concatenate(fs);del vs,fs
_,iv=np.unique(np.rint(v/.002).astype(np.int64),axis=0,return_inverse=True);iv=iv.astype(np.int32);wf=iv[f];nv=int(iv.max())+1;edges=np.concatenate([wf[:,[0,1]],wf[:,[1,2]]]);graph=coo_matrix((np.ones(len(edges),np.uint8),(edges[:,0],edges[:,1])),shape=(nv,nv)).tocsr();del edges
n,labels=connected_components(graph,directed=False);del graph;flab=labels[wf[:,0]];del labels,wf,iv
t=v[f];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2;counts=np.bincount(flab,minlength=n);areas=np.bincount(flab,weights=area,minlength=n);good=(counts>=100)|(areas>=2.);badfaces=~good[flab];pruned=int(badfaces.sum());print('CONNECTED_PARTS',n,'retained',int(good.sum()),'tiny_scrap_faces',pruned,flush=True);del v,f,t,area
final=[];startface=0;scraps=[]
for j,r in enumerate(phase):
 count=foff[j];sel=~badfaces[startface:startface+count];startface+=count
 if not sel.any():removed.append(r['name']);scraps.append({'name':r['name'],'faces':count});continue
 if not sel.all():
  a=np.load(D/r['file']);v=a['v'];f=a['f'][sel];used,iv=np.unique(f,return_inverse=True);vv=v[used];ff=iv.reshape(-1,3).astype(np.int32);fn='Clean/CC_'+str(j).zfill(4)+'.npz';np.savez_compressed(D/fn,v=vv,f=ff,uv=a['uv'][sel],mi=a['mi'][sel]);r={**r,'file':fn,'unchanged':False,'triangles':len(ff),'vertices':len(vv),'bounds':[vv.min(0).tolist(),vv.max(0).tolist()]}
 final.append(r)
(D/'Final_Scan_Index.json').write_text(json.dumps(final,indent=2));report={'source_meshes':len(rows),'retained_meshes':len(final),'fully_removed_meshes':len(removed),'removed':removed,'changed':[r['name']for r in final if not r['unchanged']],'source_triangles':sum(r['triangles']for r in rows),'retained_triangles':sum(r['triangles']for r in final),'boundary_cut_source_triangles':cutcount,'degenerate_or_stretched_source_faces':totbad,'global_connectivity_tolerance_m':.002,'tiny_component_rule':'remove only components with <100 triangles AND <2m2 measured 3D area; protected native architecture is excluded','tiny_disconnected_faces_removed':pruned,'component_count':n,'retained_components':int(good.sum()),'largest_component_triangles':np.sort(counts)[-12:][::-1].tolist(),'retention_plan_area_m2':mask.area,'reviewed_north_skirt_removed':True,'seconds':time.perf_counter()-start};(D/'Cleanup_Report.json').write_text(json.dumps(report,indent=2));print('PREPARE_DONE',{k:v for k,v in report.items()if k not in ['changed','removed']},flush=True)
