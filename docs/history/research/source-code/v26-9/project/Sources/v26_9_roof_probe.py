from v26_2_common import *
D=W/'v26_9';FD=W/'v26_8/Final';J=json.loads((FD/'Geometry_Index.json').read_text());rows=[]
for r in J:
 if r['bounds'][0][0]>3.81 or r['bounds'][0][1]>6.66 or r['bounds'][1][0]<-.2 or r['bounds'][1][1]<1. or r['bounds'][1][2]<9.72 or r['bounds'][0][2]>10.4:continue
 a=np.load(FD/r['file']);t=a['v'][a['f']];c=t.mean(1);mask=(c[:,0]>-.2)&(c[:,0]<3.81)&(c[:,1]>1)&(c[:,1]<6.66)&(t[:,:,2].max(1)>9.72)&(t[:,:,2].min(1)<10.4)
 if not mask.any():continue
 mats=[]
 for i in np.unique(a['mi'][mask]):
  q=t[mask&(a['mi']==i)];mats.append({'m':r['materials'][i],'n':len(q),'b':[q.min((0,1)).tolist(),q.max((0,1)).tolist()]})
 rows.append({'object':r['name'],'materials':mats})
(D/'Roof_White_Fragment_Probe.json').write_text(json.dumps(rows,indent=2),'utf8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
