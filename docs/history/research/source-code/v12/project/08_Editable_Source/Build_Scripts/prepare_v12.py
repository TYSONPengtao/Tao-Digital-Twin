import sys,json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;D=W/'v12_reference_audit';O=Path(r'E:\jz\JIA\Rebuild_V12');B=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid')
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
sources=[]
for src in sorted(Path(r'E:\CODEXdata\before').rglob('*')):
 if not src.is_file() or src.suffix not in ['.3dm','.py','.json','.txt']:continue
 dst=O/'07_Reference/Before'/src.relative_to(Path(r'E:\CODEXdata\before'));dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);sources.append({'source':str(src),'copy':str(dst.relative_to(O)),'sha256':sha(src),'bytes':src.stat().st_size,'role':'Reference; never overwrites source'})
selected={'0001':['DJI_0844','DJI_0865','DJI_0868','DJI_0887','DJI_0890','DJI_0893','DJI_0926','DJI_0935','DJI_0956'], '0002':['DJI_0187','DJI_0191','DJI_0210'],'0003':['DJI_0981','DJI_0987','DJI_0994'],'0004':['DJI_0058','DJI_0097','DJI_0136','DJI_0262','DJI_0319','DJI_0416','DJI_0515','DJI_0554','DJI_0593','DJI_0612','DJI_0669'],'0005':['DJI_0050','DJI_0065','DJI_0068','DJI_0086','DJI_0095','DJI_0113']}
for folder,names in selected.items():
 for name in names:
  src=Path(r'G:\处理')/folder/(name+'.JPG');assert src.exists();dst=O/'07_Reference/Aerial'/folder/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);sources.append({'source':str(src),'copy':str(dst.relative_to(O)),'sha256':sha(src),'bytes':src.stat().st_size,'role':'Roof/top-view and height relationship reference'})
for src in D.glob('*'):
 if src.suffix in ['.jpg','.json']:shutil.copy2(src,O/'07_Reference'/src.name)
for src in [Path(r'E:\jz\纯场地版本.3dm'),Path(r'E:\jz\纯场地\纯场地版本.obj')]:sources.append({'source':str(src),'sha256':sha(src),'bytes':src.stat().st_size,'role':'Ground elevation reference; no photographic triangle copied into modeled gaps'})
for src in [B/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm',B/'08_Editable_Source/05_Intermediate/Architecture_Scene.json']:
 sources.append({'source':str(src),'sha256':sha(src),'bytes':src.stat().st_size,'role':'V11 preserved architecture baseline'})
shutil.copy2(B/'02_Data/Coordinate.json',O/'02_Data/Coordinate.json')
save(O/'01_Source/Source_Manifest_V12.json',{'version':'V12','sources':sources,'video':{'source':r'E:\jz\VID_20260507_152114_00_001.insv','sha256':'3651a3e01ca8d94447aef544ce379a4ef984f6e91a7d7099699812f7a28c237f','bytes':22128020751,'copied_into_package':False},'aerial_all_images_index':'07_Reference/Aerial_Inventory.json','photos_inventory':895,'raw_DNG_inventory':893,'reference_rules':{'human_visible':'INSV direct decoded frames, before component details adapted to actual outline','roof_and_topview':'G:/处理 photographs','missing_ground':'New closed modeled terrain, slopes, steps; no imported scan triangles','absolute_height':'Inherited ENU, unverified field datum'}})
roof_findings=[{'component':'Main building hip roof','evidence':['0001/DJI_0893.JPG','0004/DJI_0593.JPG','0005/DJI_0065.JPG'],'decision':'Retain registered V11 hip shell, ridge orientation and ceramic tile direction; rooftop west terrace/canopy stays independent','limitations':'No new field survey dimensions inferred from photographs'},{'component':'Kitchen pitched roof','evidence':['0005/DJI_0050.JPG','0001/DJI_0956.JPG','0004/DJI_0319.JPG'],'decision':'Retain asymmetric ridge near rear wall and longer courtyard-facing front slope; before symmetric roof used as detail reference only','limitations':'The supplied diagram total and stacked dimension annotations conflict; do not set measured heights from it'},{'component':'Pavilion hip roof','evidence':['0001/DJI_0947.JPG','0004/DJI_0416.JPG','0004/DJI_0673.JPG'],'decision':'Retain gray rectangular asphalt shingles, hip seams and metal edge entirely inside courtyard; prior independent tile units retained'},{'component':'Inner gatehouse/screenwall upturned eaves','evidence':['0001/DJI_0935.JPG','0005/DJI_0086.JPG','0005/DJI_0095.JPG'],'decision':'Preserve higher rear gate eave/lower front timber eave overlap; curved tip and piercework details reviewed against before screen model'}]
save(O/'06_Report/Aerial_Roof_Reference_Review.json',{'status':'REVIEWED','all_895_images_inventoried':True,'sampled_overviews_visually_reviewed':8,'selected_original_photos_packaged':sum(len(x) for x in selected.values()),'findings':roof_findings,'field_dimensions_certified':False})
print('V12 references prepared',len(sources),'hashed inputs',flush=True)
