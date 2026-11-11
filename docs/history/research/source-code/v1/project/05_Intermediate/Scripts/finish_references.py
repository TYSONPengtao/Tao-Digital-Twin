import sys,json,hashlib,csv,math,shutil,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'libs'));sys.path.insert(0,str(Path(__file__).parent/'np1'))
import fitz,numpy as np,rhino3dm as rh
OUT=Path(r'E:\jz\JIA\Rebuild');scene=json.loads((OUT/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
pdfs=[Path(x) for x in (Path(__file__).parent/'source_paths.txt').read_text(encoding='utf-8-sig').splitlines() if x.lower().endswith('.pdf')]
rows=[];known={};index=list(csv.DictReader((OUT/'09_Report/Drawing_Index.csv').open(encoding='utf-8-sig')));idmap={r['文件']:r['编号'] for r in index}
for p in sorted(pdfs,key=lambda p:0 if str(p) in idmap else 1):
 d=fitz.open(p);h=hashlib.sha256();samples=[]
 for page in d:
  pix=page.get_pixmap(matrix=fitz.Matrix(.5,.5));h.update(pix.samples);h.update(str((pix.width,pix.height)).encode());samples.append([pix.width,pix.height])
 digest=h.hexdigest();match=idmap.get(str(p)) or known.get(digest,'UNMATCHED');known[digest]=match
 rows.append([str(p),len(d),digest,match,'ALL_PAGES_RENDER_READ; detailed discipline interpretation only for architecture and structural geometry'])
with (OUT/'09_Report/PDF_All_Files_Index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['SourcePath','Pages','Rendered_SHA256','NormalizedDrawingID','ReadScope']);w.writerows(rows)
for r in index:
 idn=int(r['编号'][1:]);r['楼层']='场地' if idn==1 else '全楼/说明' if idn in [2,5,6,7,8,23,26,27,28,29] else '首层/二层' if idn in [3,12,13,15,16,17,19,20,24,30,31] else '三层/屋顶' if idn in [4,14,18,21,22,25] else '楼梯'
 r['比例']='1:100（主体平/立/剖）；节点另标' if idn in [3,4,5,6] else '按各视口标题；未将单一比例套用于整页'
 r['备注']='主体几何已视觉读取；扫描图无可靠自动文本' if idn in [1,2,3,4,5,6,10,11,12,13,14,16,17,18,19,20,21,22] else '已渲染检查；机电/地下基础未细化建模'
with (OUT/'09_Report/Drawing_Index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=index[0].keys());w.writeheader();w.writerows(index)
print('PDF files',len(rows),'matched',sum(r[3]!='UNMATCHED' for r in rows),flush=True)
cats={5:'Context',40:'Entrance',79:'Entrance',153:'Interior_Stair',228:'Interior_Stair',302:'Interior_Living',377:'Detail_Balcony',451:'Interior_Bath',525:'Interior_Bedroom',600:'Interior',674:'Site',749:'Site',823:'Site',897:'Site_Gate',972:'Road',1046:'Context',1121:'Context',1195:'Context',1269:'Context'}
frows=[]
for p in sorted((OUT/'03_Insta360_Frames').glob('Center_L*.jpg')):
 t=int(p.stem.split('_')[-1][:-1]);lens=p.stem.split('_')[1];cat=cats.get(t,'Unclassified');dest=OUT/'03_Insta360_Frames'/cat;dest.mkdir(exist_ok=True);shutil.copy2(p,dest/p.name)
 frows.append([p.name,t,lens,cat,'180deg fisheye -> 90deg flat approximate','Not calibrated; not suitable for image-based measurement; no metric camera pose'])
with (OUT/'03_Insta360_Frames/Frame_Index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Frame','Seconds','Lens','Category','Projection','Limit']);w.writerows(frows)
# A separate reference model retains measured texture seams; it is never used as architectural solids.
model=rh.File3dm();model.Settings.ModelUnitSystem=rh.UnitSystem.Meters
ly=rh.Layer();ly.Name='00_REFERENCE';li=model.Layers.Add(ly);theta=math.radians(scene['coordinate']['rotation_deg']);R=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);origin=np.array(scene['coordinate']['origin'])
texture_dir=OUT/'04_ContextCapture/Textures';texture_dir.mkdir(exist_ok=True);stats=[]
for p in sorted(Path(r'E:\jz\JIA\Productions\Production_OBJ (2)\Data').rglob('*.obj')):
 verts=[];uv=[];faces=[]
 for line in p.open(encoding='utf-8'):
  if line.startswith('v '):verts.append([float(x) for x in line.split()[1:4]])
  elif line.startswith('vt '):uv.append([float(x) for x in line.split()[1:3]])
  elif line.startswith('f '):faces.append([tuple(int(z)-1 for z in tok.split('/')[:2]) for tok in line.split()[1:]])
 v=np.array(verts)-origin;v[:,:2]=v[:,:2]@R;mesh=rh.Mesh();lookup={};texcoords=[]
 for face in faces:
  ids=[]
  for vi,ti in face:
   key=(vi,ti)
   if key not in lookup:lookup[key]=mesh.Vertices.Add(*v[vi]);texcoords.append(uv[ti])
   ids.append(lookup[key])
  mesh.Faces.AddFace(*ids)
 mapping=rh.TextureMapping.CreatePlaneMapping(rh.Plane.WorldXY(),rh.Interval(0,1),rh.Interval(0,1),rh.Interval(0,1));mesh.SetTextureCoordinates(mapping,rh.Transform.Identity(),False)
 assert len(mesh.TextureCoordinates)==len(texcoords)
 for i,xy in enumerate(texcoords):mesh.TextureCoordinates[i]=rh.Point2f(*xy)
 mesh.Normals.ComputeNormals();mesh.Compact();assert mesh.IsValid,mesh.IsValidWithLog
 jpg=next(p.parent.glob('*.jpg'));dest=texture_dir/jpg.name;shutil.copy2(jpg,dest)
 mat=rh.Material();mat.Name=p.stem+'_Measured_Texture';mat.DiffuseColor=(255,255,255,255);mat.SetBitmapTexture(str(dest));mi=model.Materials.Add(mat)
 at=rh.ObjectAttributes();at.Name='REF_'+p.stem;at.LayerIndex=li;at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.MaterialIndex=mi;at.SetUserString('Source',str(p));at.SetUserString('Role','PHOTOGRAMMETRIC_REFERENCE_ONLY');model.Objects.AddMesh(mesh,at)
 stats.append({'source':str(p),'vertices_with_uv_seams':len(mesh.Vertices),'faces':len(mesh.Faces),'valid':mesh.IsValid});print('REFERENCE',stats[-1],flush=True)
for k,vv in scene['coordinate'].items():model.Strings['Coordinate_'+k]=json.dumps(vv)
model.Strings['Role']='Reference only, not rebuilt architecture; attach on 00_REFERENCE and keep separately switchable'
path=OUT/'04_ContextCapture/Production_1QK_Local_REFERENCE.3dm';assert model.Write(str(path),8);rr=rh.File3dm.Read(str(path));assert len(rr.Objects)==4
(OUT/'09_Report/Reference_QA.json').write_text(json.dumps({'path':str(path),'mesh_objects':4,'tiles':stats,'all_valid_after_readback':all(o.Geometry.IsValid for o in rr.Objects),'source_meshes_unchanged':True},indent=2),encoding='utf-8')
print('REFERENCE COMPLETE',flush=True)
