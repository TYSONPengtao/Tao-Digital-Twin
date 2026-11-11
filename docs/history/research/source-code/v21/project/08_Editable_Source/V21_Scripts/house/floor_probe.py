exec(open('work/v21_house/inspect_house.py',encoding='utf-8-sig').read().split('for r in I:')[0])
for r in I:
 if any(s in r['name'] for s in ['TERRACE','LAUNDRY','BALCONY','F3_FLOOR','SLAB_JOINED_F3']):
  d=np.load(B/'02_Data'/r['file']);v=d['vertices'];print(r['name'],[v.min(0).round(3).tolist(),v.max(0).round(3).tolist()],r['materials'])
