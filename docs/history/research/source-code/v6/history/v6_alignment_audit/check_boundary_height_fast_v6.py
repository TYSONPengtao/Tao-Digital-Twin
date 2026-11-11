import json,math,collections,csv
from pathlib import Path
from check_hybrid_v6 import np,Polygon,surface_candidates,is_ground_patch,O,PROJECT
coord=json.loads((PROJECT/'02_Data/Coordinate.json').read_text(encoding='utf-8'));a=math.radians(coord['rotation_deg']);c=math.cos(a);s=math.sin(a);R=np.array([[c,-s,0],[s,c,0],[0,0,1]]);origin=np.array(coord['origin']);h=json.loads((PROJECT/'02_Data/Hole_Polygon.json').read_text(encoding='utf-8'));H=Polygon(h['local']['outer'],h['local']['holes']);source=[];patch=[];labels=[]
for p in sorted((PROJECT/'02_Data').glob('Base_*.npz')):
 d=np.load(p);v=(d['vertices']-origin)@R;f=d['faces'];t=v[f[:,:3]]
 if np.any(f[:,2]!=f[:,3]):t=np.concatenate([t,v[f[f[:,2]!=f[:,3]][:,[0,2,3]]]])
 n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nn=np.linalg.norm(n,axis=1);source.append(t[(np.abs(n[:,2])>=.5*nn)&(nn>1e-10)])
index=json.loads((PROJECT/'02_Data/Patch_Index.json').read_text(encoding='utf-8'))
for row in index:
 if not is_ground_patch(row):continue
 d=np.load(PROJECT/'02_Data'/row['file']);t=d['vertices'][d['faces']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nn=np.linalg.norm(n,axis=1);tt=t[(np.abs(n[:,2])>=.5*nn)&(nn>1e-10)];patch.append(tt);labels.extend([row['name']]*len(tt))
q=np.array([H.exterior.interpolate(float(x)).coords[0] for x in np.linspace(0,H.exterior.length,max(500,int(H.exterior.length/.1)),endpoint=False)]);src=np.concatenate(source);pat=np.concatenate(patch);ds,zs,si=surface_candidates(q,src);dp,zp,pi=surface_candidates(q,pat);rows=[]
for j,xy in enumerate(q):
 near=ds[j]<max(1e-5,float(ds[j].min())+1e-5);iz=np.flatnonzero(near)[np.argmin(zs[j,near])];sourcez=float(zs[j,iz]);valid=dp[j]<=.03
 if ds[j,iz]>.03 or not valid.any():rows.append({'x':float(xy[0]),'y':float(xy[1]),'status':'UNMATCHED','source_xy_distance_m':float(ds[j,iz]),'nearest_patch_xy_m':float(dp[j].min())});continue
 ids=np.flatnonzero(valid);jj=int(ids[np.argmin(np.abs(zp[j,valid]-sourcez))]);delta=float(zp[j,jj]-sourcez);rows.append({'x':float(xy[0]),'y':float(xy[1]),'status':'MATCHED','source_z_local_m':sourcez,'patch_z_local_m':float(zp[j,jj]),'delta_z_m':delta,'source_xy_distance_m':float(ds[j,iz]),'patch_xy_distance_m':float(dp[j,jj]),'patch_node':labels[int(pi[j,jj])]})
matched=[r for r in rows if r['status']=='MATCHED'];err=np.array([abs(r['delta_z_m']) for r in matched]);report={'method':'npz base source ENU-to-local; ring samples ~0.10m; source ground abs(normalZ)>=0.5, nearest XY<=0.03m; compare compatible site/slab/photo-recovery patch ground nearest interpolated source z. Not a watertightness claim.','source_ground_triangles':len(src),'patch_ground_triangles':len(pat),'sample_count':len(rows),'matched_count':len(matched),'unmatched_count':len(rows)-len(matched),'absolute_dz_m':dict(zip(['p50','p95','p99','max'],np.quantile(err,[.5,.95,.99,1]).tolist())) if len(err) else None,'count_over_0p02m':int(np.sum(err>.02)),'count_over_0p05m':int(np.sum(err>.05)),'count_over_0p10m':int(np.sum(err>.10)),'worst_samples':sorted(matched,key=lambda r:abs(r['delta_z_m']),reverse=True)[:30],'unmatched_samples':[r for r in rows if r['status']!='MATCHED']};(O/'Fast_Ground_Edge_Height_V6.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');keys=sorted({k for r in rows for k in r})
with (O/'Fast_Ground_Edge_Height_V6.csv').open('w',encoding='utf-8-sig',newline='') as fp:wr=csv.DictWriter(fp,keys);wr.writeheader();wr.writerows(rows)
print(json.dumps(report,ensure_ascii=False,indent=2))
