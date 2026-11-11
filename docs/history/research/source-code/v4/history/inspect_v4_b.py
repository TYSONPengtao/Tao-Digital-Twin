exec(open(r'work\inspect_v4.py',encoding='utf-8-sig').read().split('for e in s')[0])
for e in s['elements']:
 if e['layer'] in ['31_WINDOW','30_DOOR'] or e['name'] in ['CANOPY_CENTER_0','CANOPY_CENTER_1','SITE_MAIN_COURTYARD_PAVING','SITE_WEST_EARTH_COURTYARD','SITE_SHED_1_BACK_WALL'] or 'SLAB' in e['name'] or 'GATE_METAL' in e['name']:
  print(e['name'],e.get('origin'),e.get('angle'),json.dumps(e.get('parts',[]))[:1000])
print('site',s['site']);print('openings',json.dumps(s['openings'])[:1200])
