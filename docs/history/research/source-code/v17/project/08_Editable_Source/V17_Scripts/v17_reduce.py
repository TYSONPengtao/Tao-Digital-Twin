import json
from pathlib import Path
D=Path(__file__).parent/'v17';Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'));A=json.loads((D/'Geometry_QA.json').read_text(encoding='utf8'));unchanged={r['node'] for r in A['scan'] if not any(r[k] for k in ['removed_triangles','cut_triangles','blended_vertex_occurrences'])};Q['replace']=[e for e in Q['replace'] if e['name'] not in unchanged];(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');print('Unchanged original scan nodes retained',sorted(unchanged))
