from v26_2_common import *
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from collections import defaultdict
D=W/'v26_5';D.mkdir(exist_ok=True);FD=W/'v26_5/Final';J=json.loads((FD/'Geometry_Index.json').read_text('utf8'))
prepared='--prepared'in sys.argv
if prepared:
 prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));new={r['name']:r for r in prep['objects']};skip=set(prep['archive'])|{'V26_5_Terrace_Canopy_Connected_Frame'};J=[r for r in J if r['name']not in skip and r['name']not in new]
 for r in new.values():
  a=np.load(D/r['file']);J.append(dict(r,file=str((D/r['file']).resolve()),bounds=[a['v'].min(0).tolist(),a['v'].max(0).tolist()]))
groups=defaultdict(list);selected=[]
for r in J:
 lo,hi=np.array(r['bounds'])
 if np.any(hi<[-.5,-.5,-.8])or np.any(lo>[13.9,10.8,11.6]):continue
 a=np.load(FD/r['file']);t=a['v'][a['f']];c=t.mean(1);keep=np.all(c>[-.5,-.5,-.8],axis=1)&np.all(c<[13.9,10.8,11.6],axis=1);no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ar=np.linalg.norm(no,axis=1);no/=np.maximum(ar[:,None],1e-30);selected.append([r['name'],int(keep.sum())])
 for i in np.flatnonzero(keep&(ar>.000002)):
  n=no[i];axis=int(abs(n).argmax());ds=[j for j in range(3)if j!=axis];dist=float(n@t[i,0]);key=tuple(np.round(n,4))+(round(dist,4),);groups[key].append((r['name'],int(i),Polygon(t[i][:,ds]),n,t[i],ds))
hits=defaultdict(lambda:{'projected_area_m2':0.,'pairs':0,'examples':[]})
for key,rows in groups.items():
 if len(rows)<2:continue
 polys=[r[2]for r in rows];tree=STRtree(polys)
 for i,r in enumerate(rows):
  for k in tree.query(r[2],predicate='intersects'):
   k=int(k)
   if k<=i:continue
   s=rows[k]
   if abs(r[3]@s[4][0]-r[3]@r[4][0])>.00012:continue
   area=r[2].intersection(s[2]).area
   if area<.00001:continue
   name=' | '.join(sorted([r[0],s[0]]));h=hits[name];h['projected_area_m2']+=area;h['pairs']+=1
   if len(h['examples'])<10:h['examples'].append({'a':[r[0],r[1]],'b':[s[0],s[1]],'area_m2':area,'normal':list(key[:3]),'centers':[r[4].mean(0).tolist(),s[4].mean(0).tolist()]})
out={'source':'V26.4 prepared correction overlay'if prepared else'V26.4 actual saved mesh export','selected':selected,'same_facing_coplanar_overlap_candidates':dict(sorted(hits.items(),key=lambda kv:-kv[1]['projected_area_m2']))};(D/('Overlap_Audit_Prepared.json'if prepared else'Overlap_Audit_After.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('OBJECTS',len(selected),'TRIANGLES',sum(q[1]for q in selected),'OVERLAP_PAIRS',len(hits))
for name,h in sorted(hits.items(),key=lambda kv:-kv[1]['projected_area_m2'])[:35]:print(round(h['projected_area_m2'],6),h['pairs'],name)
