exec(open('work/v21_house/qa.py',encoding='utf-8-sig').read().split('for n,e in QE.items():')[0])
for x0,x1 in [(9.31,10.68),(4.2,7.7)]:
 bbx=np.array([[x0,7.22,.02],[x1,7.38,3.67]]);c=manifold({'type':'box','origin':bbx[0].tolist(),'size':(bbx[1]-bbx[0]).tolist()});ms=[];names=[]
 for n in physical if 'physical' in globals() else AE:
  if n in REM or n.startswith('SITE') or n not in ii|QE:continue
  if overlap(bbx,bb(n)):
   mm=get(n)^c
   if mm.volume()>1e-7:ms.append(mm);names.append((n,mm.volume()))
 out=mf.Manifold.batch_boolean(ms,mf.OpType.Add);print(names);print('Full height ratio',out.volume()/c.volume())
