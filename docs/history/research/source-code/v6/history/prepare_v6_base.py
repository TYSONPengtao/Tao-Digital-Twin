import sys,json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid')
for d in ['01_Source','02_Data','03_Textures/Base','03_Textures/Patch','04_Rhino','05_Export','06_Report']:(O/d).mkdir(parents=True,exist_ok=True)
P=Path(r'E:\jz\纯场地版本.3dm');F=rh.File3dm.Read(str(P));info=[]
shutil.copy2(P,O/'01_Source/Pure_Site_UNMODIFIED.3dm')
for i,ob in enumerate(F.Objects):
 m=ob.Geometry;v=np.array([[p.X,p.Y,p.Z] for p in m.Vertices]);faces=np.array(list(m.Faces),np.int32);uv=np.array([[p.X,p.Y] for p in m.TextureCoordinates]);normals=np.array([[p.X,p.Y,p.Z] for p in m.Normals]);mat=F.Materials[ob.Attributes.MaterialIndex];tex=Path(mat.GetBitmapTexture().FileName);dest=O/'03_Textures/Base'/tex.name;shutil.copy2(tex,dest)
 np.savez_compressed(O/'02_Data'/f'Base_{i}.npz',vertices=v,faces=faces,uv=uv,normals=normals)
 info.append(dict(index=i,name='BASE_REALITY_'+str(i),source_id=str(ob.Attributes.Id),material_index=ob.Attributes.MaterialIndex,material_name=mat.Name,texture=str(dest),source_texture=str(tex),vertices=len(v),faces=len(faces),uv_count=len(uv)))
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V5\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
(O/'02_Data/Base_Index.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'02_Data/Coordinate.json').write_text(json.dumps(S['coordinate'],ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['Pure_Baseline_Hashes.json','Pure_Texture_Map.csv','All_Reality_Model_Files.csv','New_Rhino_Summary.json','Old_JIA_Texture_Source.json','README.md']:
 p=W/'v6_reality_inventory'/name
 if p.exists():shutil.copy2(p,O/'06_Report'/('Inventory_'+name))
for p in (W/'v6_alignment_audit').glob('*'):
 if p.suffix in ['.json','.png','.md']:shutil.copy2(p,O/'06_Report'/p.name)
print('Hybrid base extracted without weld/UV edits:',sum(x['vertices'] for x in info),'vertices',sum(x['faces'] for x in info),'faces',flush=True)
