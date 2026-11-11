import sys,json,hashlib,struct,zipfile,time
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import rhino3dm as rh
O=Path(r'E:/jz/JIA/Rebuild_V14');P=O/'04_Rhino/Architecture_Complete_V14_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
Q=json.loads((O/'06_Report/V14_Native_Readback_QA.json').read_text(encoding='utf8'));assert Q['status']=='PASS_NATIVE_FILE_READBACK' and Q['sha256']==sha(P)
F=rh.File3dm.Read(str(P));assert len(F.Objects)==Q['native_objects'];views=[v.Name for v in F.NamedViews];assert 'V14_Valley_Detail' in views and 'V14_F3_Hall' in views
with (O/'05_Export/Complete_Site_V14_LOCAL.glb').open('rb') as f:
 h=f.read(12);magic,version,total=struct.unpack('<4sII',h);assert magic==b'glTF' and version==2;length,ctype=struct.unpack('<II',f.read(8));assert ctype==0x4E4F534A;g=json.loads(f.read(length))
assert total==(O/'05_Export/Complete_Site_V14_LOCAL.glb').stat().st_size
assert len(g.get('cameras',[]))==8 and len(g['meshes'])==Q['nodes']
assert len(g['images'])==5 and all('bufferView' in im and 'uri' not in im for im in g['images'])
native=json.loads((O/'02_Data/Native_Readback_Index_V14.json').read_text(encoding='utf8'));tri=sum(r['triangles'] for r in native);gtri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tri==gtri
for name in ['Contact_QA','Opening_QA','Merge_Route_QA']:
 v=json.loads((O/'06_Report'/f'{name}.json').read_text(encoding='utf8'));assert v['status'].startswith('PASS')
for name in ['Whole_Site','Top','Roof_Junction','Valley_Detail','Outer_Storage','F3_Hall','F3_Terrace','Terrace']:assert (O/'06_Report'/f'V14_Native_{name}.png').stat().st_size>10000
packqa={'status':'PASS_DELIVERY_FILES','native_objects':len(F.Objects),'native_readback_nodes':Q['nodes'],'glb_meshes':len(g['meshes']),'glb_triangles':gtri,'glb_embedded_original_images':len(g['images']),'glb_cameras':len(g['cameras']),'original_exterior_nodes':sum(r['name'].startswith('SITE_V14_ORIGINAL_EXTERIOR') for r in native),'named_views':views,'native_model_sha256':sha(P),'glb_sha256':sha(O/'05_Export/Complete_Site_V14_LOCAL.glb'),'ue5_import_tested':False}
(O/'06_Report/Delivery_QA.json').write_text(json.dumps(packqa,ensure_ascii=False,indent=2),encoding='utf8')
active={str(Path(r['file'])).replace('\\','/') for r in native};model=json.loads((O/'02_Data/Modeled_Index_V14.json').read_text(encoding='utf8'));active.update(str(Path(r['file'])).replace('\\','/') for r in model)
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name in ['File_Manifest_SHA256.json','Bundle_QA.json'] or p.suffix in ['.blend1','.bak','.3dmbak']:continue
 rel=p.relative_to(O).as_posix()
 if rel.startswith('02_Data/') and p.suffix=='.npz' and p.relative_to(O/'02_Data').as_posix() not in active:continue
 files.append(p)
manifest={'version':'V14','model':P.relative_to(O).as_posix(),'file_count':len(files),'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
out=W.parent/'outputs';out.mkdir(exist_ok=True);zp=out/'Production_1QK_Rhino_V14_Roof_Site_Storage.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for i,p in enumerate(files):
  z.write(p,'Rebuild_V14/'+p.relative_to(O).as_posix())
  if i%100==0:print('PACKED',i,len(files),flush=True)
with zipfile.ZipFile(zp) as z:
 assert len(z.infolist())==len(files);assert z.testzip() is None
bq={'status':'PASS_ZIP_CRC','zip':str(zp),'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(files),'native_model_sha256':packqa['native_model_sha256']};(O/'06_Report/Bundle_QA.json').write_text(json.dumps(bq,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bq,ensure_ascii=False),flush=True)
