import json
from pathlib import Path
Q=json.loads(Path('work/v10_perimeter_detail/Geometry_QA.json').read_text(encoding='utf-8'))
for w in Q['wall_records']:
 print(w['name'],'first',[w['centerline_points'][0],w['original_crest_z'][0]],'last',[w['centerline_points'][-1],w['original_crest_z'][-1]],'crown',w['provisional_crown_parts'])
S=json.loads(Path('work/v10_perimeter_detail/Mutation.json').read_text(encoding='utf-8'));e=next(e for e in S['add'] if e['name'].endswith('WALL_1_PROVISIONAL_FLOWER_CROWN'));print('lastpartbounds')
for i in [83,84,85,86]:
 v=e['parts'][i]['geometry']['vertices']; print(i,[[min(p[j] for p in v) for j in range(3)],[max(p[j] for p in v) for j in range(3)]])
