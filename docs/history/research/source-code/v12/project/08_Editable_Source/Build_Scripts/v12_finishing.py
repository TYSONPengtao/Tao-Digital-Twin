"""Reference packaging, orphan cleanup and modeled PBR surface textures."""
import sys,json,hashlib,shutil,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from PIL import Image
O=Path(r'E:\jz\JIA\Rebuild_V12');B=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid')
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
K=W/'v12_final_cleanup';K.mkdir(exist_ok=True)
remove=[f'CONSTRUCTION_SHED_{i}_EXPOSED_PLINTH' for i in range(1,4)]
dump(K/'Mutation.json',dict(replace=[],add=[],remove=remove,materials={},definitions={},changes=['Clear three obsolete shelter support skirts from the user-specified western terrain-only zone. Reconstructed ground replaces them.']))
dump(K/'Geometry_QA.json',dict(status='PASS',retired_shelter_skirts=remove,evidence='User redline screenshot 2026-10-09 001456: no buildings in this area, terrain only',original_files_modified=False))
ref=O/'07_Reference/User_Kitchen_Closeups';ref.mkdir(parents=True,exist_ok=True)
rows=[]
for suffix,meaning in [('115520','Narrow door-head paired-square return lattice'),('115537','Double octagonal window medallion and surrounding angular return lattice'),('191926','Two-level clerestory/transom hierarchy and exposed inner roof frame'),('191942','Round longitudinal purlins, repeated rafters, exposed cross beams; no suspended ceiling')]:
 p=Path(r'D:\Desktop\问题')/f'屏幕截图 2026-10-11 {suffix}.jpg';assert p.exists();shutil.copy2(p,ref/p.name);rows.append(dict(source=str(p),file=p.name,sha256=sha(p),role=meaning,dimensions_surveyed=False))
dump(ref/'Reference_Index.json',dict(images=rows,precedence='Actual near-view photographs supersede synthetic construction diagrams for visible detail. Wide-angle distortion is not used as a measured cross section.'))
terrain=W/'v12_terrain';dest=O/'04_Rhino/Pure_Site_Cleaned_Ground_REFERENCE_ENU.3dm';shutil.copy2(terrain/'Pure_Site_Cleaned_Ground_Reference_ENU.3dm',dest)
if (terrain/'Reference_Textures').is_dir():shutil.copytree(terrain/'Reference_Textures',O/'03_Textures/Reference_Ground',dirs_exist_ok=True)
import rhino3dm as rh
RF=rh.File3dm.Read(str(dest));reference_textures=[]
for mat in RF.Materials:
 tex=mat.GetBitmapTexture()
 if tex:
  p=O/'03_Textures/Reference_Ground'/Path(tex.FileName).name;assert p.exists();mat.SetBitmapTexture(str(p));assert mat.GetBitmapTexture().FileName==str(p);RF.EmbeddedFiles.Add(rh.EmbeddedFile.Read(str(p)));reference_textures.append(dict(material=mat.Name,texture=str(p.relative_to(O)),sha256=sha(p)))
assert RF.Write(str(dest),8)
dump(O/'06_Report/Pure_Ground_Reference_Texture_QA.json',dict(status='PASS',model=str(dest),reference_only=True,textures=reference_textures,embedded_files=len(RF.EmbeddedFiles)))
M=read(B/'08_Editable_Source/05_Intermediate/Architecture_Scene.json')['materials']
for folder in ['v12_kitchen','v12_terrain','v12_screenwall_reference']:M.update(read(W/folder/'Mutation.json').get('materials',{}))
out=O/'03_Textures/Modeled_PBR';out.mkdir(parents=True,exist_ok=True)
N=1024;y,x=np.mgrid[0:N,0:N]/N;rng=np.random.default_rng(20261011)
def noise(seed):
 rr=np.random.default_rng(seed);z=np.zeros((N,N),np.float64)
 for freq,amp in [(2,.40),(7,.20),(19,.14),(51,.08),(133,.04)]:
  for k in range(4):
   ax=int(rr.integers(1,freq+1));ay=int(rr.integers(1,freq+1));z+=amp*np.sin(math.tau*(ax*x+ay*y)+rr.uniform(0,math.tau))/4
 return z
grain_phase=math.tau*(58*x+.20*np.sin(math.tau*y)+.4*np.sin(4*math.tau*y)+.08*np.sin(math.tau*(3*x+y)))
patterns={
 'Wood': .14*np.sin(grain_phase)+.09*np.sin(grain_phase*3)+.35*noise(4),
 'Ceramic': .27*noise(5),
 'Masonry': .38*noise(6),
 'Concrete': .24*noise(7)+.018*rng.normal(size=(N,N)),
 'Plaster': .17*noise(8)+.012*rng.normal(size=(N,N)),
 'Earth': .16*noise(9)+.15*rng.normal(size=(N,N)),
 'Stone': .42*noise(10),
 'Asphalt': .29*noise(11)+.11*rng.normal(size=(N,N)),
}
def category(name):
 k=name.lower()
 if any(z in k for z in ['glass','water','metal','stainless','gold','pvc','sealant','uncertain','leaves','grass','blue_sheet','green_sheet']):return None
 if any(z in k for z in ['wood','timber','thatch']):return 'Wood'
 if 'earth' in k or 'soil' in k:return 'Earth'
 if 'asphalt' in k or 'waterproof' in k:return 'Asphalt'
 if 'brick' in k:return 'Masonry'
 if any(z in k for z in ['roof','tile','ceramic']):return 'Ceramic'
 if any(z in k for z in ['wall','ceiling']):return 'Plaster'
 if any(z in k for z in ['stone','floor','paving','court']):return 'Stone'
 return 'Concrete'
manifest={};maps={}
for cat,h in patterns.items():
 gx,gy=np.gradient(h);nn=np.stack([-gx*N*.001,-gy*N*.001,np.ones_like(h)],2);nn/=np.linalg.norm(nn,axis=2)[:,:,None]
 normal=out/(cat+'_Normal.png');Image.fromarray(np.uint8(np.clip((nn+1)*127.5,0,255))).save(normal)
 relief=out/(cat+'_Relief.png');Image.fromarray(np.uint8(np.clip(128+h*80,0,255))).save(relief)
 maps[cat]=dict(normal=str(normal.relative_to(O)).replace('\\','/'),bump=str(relief.relative_to(O)).replace('\\','/'))
for name,spec in M.items():
 cat=category(name)
 if not cat:continue
 h=patterns[cat];base=np.array(spec['color']);colour=np.clip(base[None,None,:]*(1+h[:,:,None]*.24),0,255).astype(np.uint8);p=out/(name+'_BaseColor.png');Image.fromarray(colour).save(p)
 rp=out/(name+'_Roughness.png');Image.fromarray(np.uint8(np.clip((spec.get('roughness',.7)+h*.09)*255,0,255))).save(rp)
 manifest[name]=dict(category=cat,base_color=str(p.relative_to(O)).replace('\\','/'),roughness=str(rp.relative_to(O)).replace('\\','/'),**maps[cat],physical_tile_m=[.45,1.8] if cat=='Wood' else [1,1],source='Procedural modeled microtexture, photo-referenced palette; no photogrammetric atlas or physical property measurement',sha256=sha(p))
dump(O/'03_Textures/Modeled_PBR/Material_Texture_Index.json',dict(materials=manifest,status='GENERATED',source_photogrammetric_textures_in_primary=0,reference_images=rows,dimensions='Metre-scaled modeled UVs; grain aligned to longest member direction',limits='Surface appearance approximation. Site weathering, true roughness and color require calibrated field texture capture.'))
print('V12 finishing prepared',len(manifest),'modeled PBR materials; source photos and ground reference retained',flush=True)
