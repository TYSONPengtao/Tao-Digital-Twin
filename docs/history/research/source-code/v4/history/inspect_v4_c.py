exec(open(r'work\inspect_v4.py',encoding='utf-8-sig').read().split('for e in s')[0])
for e in s['elements']:
 if any(k in e['name'] for k in ['CARVED','PANEL','METAL_GATE','SW_GATE','WHITE_INSIDE','WEST_TILE_WALL']):
  print(e['name'],len(e.get('parts',[])),json.dumps(e.get('parts',[{}])[0])[:900])
