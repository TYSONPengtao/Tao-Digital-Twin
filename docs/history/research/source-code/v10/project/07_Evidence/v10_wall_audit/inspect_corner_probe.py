import json
from pathlib import Path
S=json.loads(Path('work/v10_perimeter_detail/Mutation.json').read_text(encoding='utf-8'));e=next(e for e in S['add'] if e['name'].endswith('WALL_1_PROVISIONAL_FLOWER_CROWN'));v=e['parts'][86]['geometry']['vertices'];print('parts',len(e['parts']),'bounds',[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]])
print('vfirst',v[:10]);print('probe',S['changes']['negative_space_probes'])
