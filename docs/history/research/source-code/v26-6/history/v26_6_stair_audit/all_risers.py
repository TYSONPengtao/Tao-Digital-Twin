exec((__import__('pathlib').Path(__file__).parent/'landing_faces.py').read_text('utf8').split('rows=[]')[0])
rows=[]
for fl,zbase,mid,top in [(1,-.45,1.5,3.45),(2,3.45,5.25,7.05)]:
 lo=np.array([4.8,7.42,zbase]);hi=np.array([8.6,9.68,top]);sel=(T.max(1)>=lo).all(1)&(T.min(1)<=hi).all(1)&(abs(N[:,0])>.99);summary={};faces=[]
 for i in np.flatnonzero(sel):
  p=clip(T[i],lo,hi)
  if len(p)<3:continue
  ar=.5*np.linalg.norm(sum((np.cross(p[j]-p[0],p[j+1]-p[0])for j in range(1,len(p)-1)),np.zeros(3)))
  if ar<1e-10:continue
  cn=p.mean(0);material=r['materials'][int(a['mi'][i])];plane=round(float(cn[0]),4);role='stair flight riser or landing side'
  if abs(plane-5.2)<.0001 and N[i,0]>.99:role='midlanding front riser'
  if abs(plane-8.2)<.0001 and N[i,0]<-.99:role='storey floor arrival riser'
  k=(plane,round(float(N[i,0]),1),material,role)
  if k not in summary:summary[k]={'area_m2':0.,'bounds_min':p.min(0),'bounds_max':p.max(0),'triangles':[]}
  q=summary[k];q['area_m2']+=ar;q['bounds_min']=np.minimum(q['bounds_min'],p.min(0));q['bounds_max']=np.maximum(q['bounds_max'],p.max(0));q['triangles'].append(int(i));faces.append({'index':int(i),'plane_x':plane,'normal_x':float(N[i,0]),'material':material,'role':role,'clipped_polygon':p.tolist()})
 groups=[{'plane_x':k[0],'normal_x':k[1],'material':k[2],'role':k[3],'area_m2':v['area_m2'],'bounds':[v['bounds_min'].tolist(),v['bounds_max'].tolist()],'triangles':v['triangles']}for k,v in summary.items()];rows.append({'floor':fl,'groups':groups,'faces':faces});print('FLOOR',fl)
 for q in groups:
  if q['material']!='M_V24_31_Stair_Gray_Marble':print(q,flush=True)
(Path(__file__).parent/'all_equivalent_risers.json').write_text(json.dumps(rows,indent=2),'utf8')
