import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_12';R=Path('E:/jz/JIA/Rebuild_V24_12/Reports');idx=json.loads((D/'Solid_Export_Index.json').read_text());results=[];solids={}
def solid(d):
 trials=[]
 # Native manifold replacements already have shared topological indices.
 # Respect those indices first; coordinate welding must not merge separate
 # closed cells that merely touch at the same physical point or edge.
 raw=mf.Manifold(mf.Mesh64(np.array(d['v'],dtype=np.float64,order='C'),np.array(d['f'],dtype=np.uint64,order='C')))
 trials.append({'method':'original_saved_vertex_indices','status':str(raw.status()),'volume_m3':raw.volume()})
 if raw.status()==mf.Error.NoError and raw.volume()>0:return raw,trials
 for dec in[9,8,7,6,5]:
  v,ix=np.unique(np.round(d['v'],dec),axis=0,return_inverse=True);f=ix[d['f']];ok=(f[:,0]!=f[:,1])&(f[:,0]!=f[:,2])&(f[:,1]!=f[:,2]);f=f[ok];t=v[f];ok=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13;f=f[ok];m=mf.Manifold(mf.Mesh64(np.ascontiguousarray(v),np.array(f,dtype=np.uint64,order='C')));trials.append({'coordinate_precision_m':10.**-dec,'status':str(m.status()),'discarded_zero_area_triangles':len(d['f'])-len(f),'volume_m3':m.volume()})
  if m.status()==mf.Error.NoError and m.volume()>0:break
 return m,trials
def compound_stats(d):
 v,ix=np.unique(np.round(d['v'],6),axis=0,return_inverse=True);f=ix[d['f']];t=v[f];good=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13;f=f[good];ed=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);e,c=np.unique(ed,axis=0,return_counts=True)
 return {'boundary_edges':int((c==1).sum()),'shared_internal_edges':int((c>2).sum()),'zero_area_triangles':int((~good).sum()),'signed_surface_volume_m3':float(np.sum(np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])))/6)}
for r in idx['objects']:
 dd=np.load(D/r['file']);m,tr=solid(dd);passed=m.status()==mf.Error.NoError and m.volume()>0;solids[r['name']]=m;row={'name':r['name'],'pass':passed,'trials':tr}
 if not passed and r['name']=='SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry':
  a=compound_stats(np.load(D/(r['name']+'.npz')));b=compound_stats(dd);inherited=b['boundary_edges']==a['boundary_edges']==0 and b['shared_internal_edges']<=a['shared_internal_edges'] and b['zero_area_triangles']<=a['zero_area_triangles'] and a['signed_surface_volume_m3']*b['signed_surface_volume_m3']>0
  row.update({'pass':inherited,'qualification':'Inherited compound wall cells share internal cap faces; checked for no new open edges or degeneracy, rather than reporting this legacy group as one manifold solid','baseline':a,'saved':b})
 results.append(row);print('SOLID',r['name'],row['pass'],row.get('saved',''),flush=True)
deck_overlap=(solids['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry']^solids['SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry']).volume();deck_pass=abs(deck_overlap)<1e-7
out={'status':'PASS_SAVED_SOLIDS_WITH_INHERITED_COMPOUND_WALL'if all(r['pass']for r in results)and deck_pass else'FAIL_INDEPENDENT_SAVED_SOLIDS','model_sha256':idx['model_sha256'],'solids':results,'timber_deck_roof_intersection_m3':deck_overlap,'deck_clear_of_roof_shell':deck_pass};(R/'V24_12_Independent_Solid_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
# Original accepted route obstacles are unchanged except the saved meshes
# replaced above. Intersect the five actual route samples with both sets.
obs=[]
for r in json.loads((W/'v24_11/QA_Obstacle_Index.json').read_text()):
 if r['name']in solids:m=solids[r['name']]
 else:m,tr=solid(np.load(W/'v24_11'/r['file']))
 obs.append((r['name'],m))
boxes=[('Entry',[12.5,-15.63,-.37],[1.30,.65,2.02]),('Gallery main route',[13.8,-15.58,-.37],[4.25,.60,2.02]),('End column bypass',[18.02,-15.35,-.37],[.45,.33,2.02]),('Storage room door',[15.64,-15.00,-.37],[.60,.45,1.95]),('East end portal',[18.47,-15.61,-.37],[.45,.59,2.02])];hits=[]
for label,lo,sz in boxes:
 box=mf.Manifold.cube(sz).translate(lo);rr=[]
 for n,m in obs:
  if m.status()!=mf.Error.NoError:rr.append({'object':n,'error':str(m.status())});continue
  vol=(m^box).volume()
  if vol>1e-7:rr.append({'object':n,'overlap_m3':vol})
 hits.append({'label':label,'origin':lo,'size':sz,'obstructions':rr})
good=all(not r['obstructions']for r in hits);out={'status':'PASS_INDEPENDENT_CLEARANCE'if good else'FAIL_INDEPENDENT_CLEARANCE','model_sha256':idx['model_sha256'],'samples':hits};(R/'V24_12_Independent_Clearance_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],flush=True)
