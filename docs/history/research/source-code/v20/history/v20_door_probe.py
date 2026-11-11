exec(open(__file__.replace('v20_door_probe','v20_inventory'),encoding='utf8').read().split('rows=[]')[0])
rows=json.loads((D/'Inventory.json').read_text(encoding='utf8'))
for r in rows:
 n=r['name'];e=r['element']
 if 'DOOR' in n or 'GATE_TIMBER' in n or 'GATE_WOOD' in n:print(n,r['bounds'],e.get('definition'),e.get('pivot_world_m'),e.get('angle'),flush=True)
print('Definitions',[(n,len(e['parts'])) for n,e in S['definitions'].items() if 'DOOR' in n or 'LEAF' in n])
