import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'libs'));import rhino3dm as rh
s=json.loads(Path(r'E:\jz\JIA\Rebuild_V5\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
print('Terrain nodes',[e['name'] for e in s['elements'] if any(p['geometry']['type']=='terrain' for p in e['parts'])])
f=rh.File3dm.Read(r'E:\jz\JIA\Rebuild_V6_Hybrid\04_Rhino\Reality_Hybrid_V6.3dm')
for ob in f.Objects:
 if not ob.Geometry.IsValid:print(ob.Attributes.Name,ob.Geometry.IsValidWithLog)
m=rh.Mesh();print('Vertexlist properties',dir(m.Vertices));print('Face properties',[x for x in dir(m.Faces) if 'Deg' in x or 'Cull' in x])
