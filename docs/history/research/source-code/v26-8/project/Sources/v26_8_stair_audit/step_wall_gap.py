exec((__import__('pathlib').Path(__file__).parent/'diagnose.py').read_text('utf8').split('out=')[0])
rows=[]
for fl in[1,2]:
 for k in[1,2]:
  n=f'STAIR_F{fl}_FLIGHT{k}_Geometry';a=np.load(W/'v26_1'/I[n]['file']);m=solid(a['v'],a['f'],n)
  for x in np.arange(5.33,7.75,.26):
   top=sorted([h.position[2]for h in m.ray_cast([x,9.05 if k==1 else 8.,10.],[x,9.05 if k==1 else 8.,-1.])if h.normal[2]>.9])[-1]
   z=top-.01
   start=[float(x),9.05 if k==1 else 8.,z];end=[float(x),10.1 if k==1 else 7.0,z]
   hs=house.ray_cast(start,end);h=[{'position':list(q.position),'normal':list(q.normal)}for q in hs]
   gaps=[]
   for p,q in zip(h[:-1],h[1:]):
    a0,b0=p['position'][1],q['position'][1];dist=abs(a0-b0)
    if .005<dist<.25 and (p['normal'][1]if k==1 else-p['normal'][1])>.9 and (q['normal'][1]if k==1 else-q['normal'][1])<-.9:gaps.append({'y0':min(a0,b0),'y1':max(a0,b0),'gap_m':dist})
   r={'floor':fl,'flight':k,'x':float(x),'tread_z':top,'test_z':z,'ray':h,'cavity_gaps':gaps};rows.append(r)
  print('F',fl,'K',k,[(round(r['x'],2),r['cavity_gaps'])for r in rows[-10:]])
(D/'Step_To_Wall_Gaps.json').write_text(json.dumps(rows,indent=2),'utf8')
