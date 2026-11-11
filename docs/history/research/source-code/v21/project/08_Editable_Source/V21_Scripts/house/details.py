exec(open('work/v21_house/inspect_house.py',encoding='utf-8-sig').read().split('for r in I:')[0])
E={e['name']:e for e in S['elements']}
for n in ['FACADE_CONTINUOUS_F3','PARTITIONS_JOINED_F3','DOOR_BED_F3_X9.1__FRAME','DOOR_LAUNDRY_F3__FRAME','DOOR_FRONT_CENTER_F1__FIXED']:
 e=E[n];print(n,json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False)[:2000])
 for j,p in enumerate(ex.expand_parts(e)):
  if n=='PARTITIONS_JOINED_F3' or j<10:
   v,f=ex.world_part(p,e); print(j,p['material'],np.round([v.min(0),v.max(0)],3).tolist())

