from v22_common import *
Q=json.loads((W/'v22_gate/Mutation.json').read_text(encoding='utf8'));G={e['name']:e for e in Q['replace']+Q['add']};results=[]
tile=raw('SITE_V21_GATE_REFERENCE_LAYER_10')+raw('SITE_V21_GATE_REFERENCE_LAYER_09');det=G['GATE_V22_EMBOSSED_TILE_END_CAPS']
for j,p in enumerate(det['parts']):
 a=manifold(p['geometry']);vol=(a^tile).volume();results.append({'detail':'tile_end','part':j,'contact_m3':vol,'pass':vol>1e-9})
piers=raw('SITE_V21_GATE_REFERENCE_LAYER_02')
for j,p in enumerate(G['SITE_V21_GATE_REFERENCE_LAYER_04']['parts']):
 a=manifold(p['geometry']);vol=(a^piers).volume();results.append({'detail':'organic_relief_backing','part':j,'contact_m3':vol,'pass':vol>1e-6})
out={'status':'PASS_SOURCE_CONTACTS' if all(r['pass'] for r in results) else 'DETAIL_CONTACTS_NEED_ADJUSTMENT','results':results}
(W/'v22_gate/Contact_QA.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
