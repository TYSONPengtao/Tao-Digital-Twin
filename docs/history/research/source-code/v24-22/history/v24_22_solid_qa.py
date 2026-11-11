from v24_22_common import *
R=Path('E:/jz/JIA/Rebuild_V24_22/Reports');idx=json.loads((D/'Saved_Geometry_Index.json').read_text());checks=[];ms={}
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
for row in idx['objects']:
 d=np.load(D/row['file']);m=solid(d['v'],d['f'],row['name']);ms[row['name']]=m;err=abs(m.volume()-row['volume_m3']);ck('Saved closed solid / '+row['name'],m.status()==mf.Error.NoError and err<max(3e-5,row['volume_m3']*3e-5),bodies=len(m.decompose()),volume_m3=m.volume(),volume_error_m3=err)
frames=ms['SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry'];floor=load('SITE_KITCHEN_STONE_FLOOR_Geometry')
for i,m in enumerate(frames.decompose()):ck('Frame grounded through stone base '+str(i),m.min_gap(floor,.01)<.001,gap_m=m.min_gap(floor,.01))
header=ms['SITE_KITCHEN_V12_BEFORE_WOOD_04_Geometry'];front=load('SITE_KITCHEN_V12_UPPER_FACADE_COLUMN_CONTINUATIONS_Geometry');support=union([frames,header,front])
for i,m in enumerate(ms['V24_22_Porch_Single_Cross_Beams'].decompose()):ck('Porch cross beam joined to supports '+str(i),m.min_gap(support,.01)<.001)
for i,m in enumerate(ms['V24_22_Outer_Stepped_Square_Fretwork'].decompose()):ck('Open fret bay attached to header '+str(i),m.min_gap(header,.01)<.001)
wall=ms['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'];parts=wall.decompose();physical=[c for c in parts if abs(c.volume())>1e-10];roundoff=[{'volume_m3':c.volume(),'bounds':list(c.bounding_box())}for c in parts if abs(c.volume())<=1e-10]
# Float32 storage can split a zero-volume shell at a near-coincident boolean
# corner. Require one physical volume; disclose and bound numerical remnants.
tiny=all(max(np.array(c.bounding_box())[3:]-np.array(c.bounding_box())[:3])<.0002 for c in parts if abs(c.volume())<=1e-10)
ck('Joined masonry has one physical closed volume',len(physical)==1 and tiny,float32_zero_volume_shells=roundoff)
fail=[c for c in checks if not c['pass']];(R/'V24_22_Solid_QA.json').write_text(json.dumps({'status':'PASS_SAVED_SOLIDS_AND_SUPPORTS'if not fail else'FAIL','model_sha256':idx['model_sha256'],'checks':checks,'failures':fail},ensure_ascii=False,indent=2));print('V22_SOLID_QA',len(checks),'FAIL',len(fail))
