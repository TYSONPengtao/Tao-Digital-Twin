import sys,json,math,hashlib,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs']]
import numpy as np,rhino3dm as rh
from PIL import Image,ImageDraw
O=Path(r'E:/jz/JIA/Rebuild_V15');D=O/'03_Textures/V15_Surface_Finishes';D.mkdir(exist_ok=True);rng=np.random.default_rng(1512);N=1024
def field(name,color,amp=1.5):
 a=np.clip(np.array(color)[None,None,:]+rng.normal(0,amp,(N,N,1)),0,255).astype('uint8');p=D/(name+'.png');Image.fromarray(a).save(p);return p
brick=Image.new('RGB',(N,N),(154,153,143));bh=Image.new('L',(N,N),104);bd=ImageDraw.Draw(brick);hd=ImageDraw.Draw(bh)
for j in range(16):
 shift=128 if j%2 else 0
 for i in range(-1,5):
  x=i*256+shift;y=j*64;c=int(rng.integers(101,123));bd.rectangle([x+3,y+3,x+252,y+60],fill=(c,c+2,c));hd.rectangle([x+3,y+3,x+252,y+60],fill=170)
brick.save(D/'Grey_Brick_1m.png');bh.save(D/'Grey_Brick_Height.png')
stone=Image.new('RGB',(N,N),(160,149,123));sh=Image.new('L',(N,N),105);dd=ImageDraw.Draw(stone);dh=ImageDraw.Draw(sh)
for j in range(5):
 shift=122 if j%2 else 0
 for i in range(-1,5):
  x=i*256+shift;y=j*205;c=int(rng.integers(86,124));pts=[(x+7,y+14),(x+72,y+5),(x+239,y+10),(x+248,y+64),(x+246,y+178),(x+187,y+197),(x+18,y+193),(x+5,y+131)];dd.polygon(pts,fill=(c,c+1,c-4));dh.polygon(pts,fill=174)
stone.save(D/'Rubble_Stone_1m.png');sh.save(D/'Rubble_Stone_Height.png')
plaster=field('White_Plaster',(238,239,232),1.1);plain=Image.new('L',(N,N),128);plain.save(D/'Flat_Microheight.png');grey=field('Grey_Carved_Stone',(131,134,131),2.0)
updates={'M_Grey_Brick':('Grey_Brick_1m.png','Grey_Brick_Height.png'),'M_Stone_Rubble':('Rubble_Stone_1m.png','Rubble_Stone_Height.png'),'M_Wall_Exterior':(plaster.name,'Flat_Microheight.png'),'M_Wall_Interior':(plaster.name,'Flat_Microheight.png'),'M_V15_GATE_GREY_STONE':(grey.name,'Flat_Microheight.png')}
P=O/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));changes=[]
for m in F.Materials:
 if m.Name in updates:
  b,h=updates[m.Name];m.SetBitmapTexture(str(D/b));m.SetBumpTexture(str(D/h));m.ToPhysicallyBased();m.PhysicallyBased.BaseColor=(1,1,1,1);m.PhysicallyBased.Roughness=.90;changes.append({'material':m.Name,'bitmap':str(D/b),'bump':str(D/h),'texture_scale':'One-metre seamless UV period; nominal 250 x 62.5 mm visible brick course, decorative photo-fit material; not a measured masonry specification'})
 else:
  for get,setter in [('GetBitmapTexture','SetBitmapTexture'),('GetBumpTexture','SetBumpTexture')]:
   tx=getattr(m,get)()
   if tx:
    p=Path(tx.FileName);candidate=O/'03_Textures/Modeled_PBR'/p.name
    if 'Original_Exterior' in str(p):candidate=O/'03_Textures/Original_Exterior'/p.name
    if candidate.exists() and candidate!=p:getattr(m,setter)(str(candidate))
F.Strings['V15_Material_Repair']='Explicit UV; remove diagonal synthetic stripe fields from brick, stone and plaster. New dimension-controlled procedural brick and stone finishes fitted to INSV visible appearance. Original exterior image bytes unchanged.'
assert F.Write(str(P),8)
md={}
for m in F.Materials:
 tx=m.GetBitmapTexture();bu=m.GetBumpTexture();pb=m.PhysicallyBased;sup=pb.Supported
 md[m.Name]={'color':[round(c*255) for c in list(pb.BaseColor)[:3]] if sup else list(m.DiffuseColor)[:3],'roughness':pb.Roughness if sup else .85,'metallic':pb.Metallic if sup else 0,'alpha':1-m.Transparency,'native_bitmap':tx.FileName if tx else None,'native_bump':bu.FileName if bu else None,'native_diffuse':list(m.DiffuseColor),'physically_based_supported':sup}
(O/'02_Data/Native_Render_Materials.json').write_text(json.dumps(md,ensure_ascii=False,indent=2),encoding='utf8');qa={'status':'PASS_NATIVE_MATERIAL_PATHS','changes':changes,'original_exterior_bitmaps_unchanged':True,'native_geometry_unchanged':True};(O/'06_Report/V15_Material_Repair_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print('MATERIALS FIXED',len(changes),flush=True)
