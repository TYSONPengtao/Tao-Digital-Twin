import bpy,sys,types,json,hashlib,math,csv,tempfile
from pathlib import Path
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V24_31');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_31.blend';bpy.ops.wm.open_mainfile(filepath=str(P));m=types.ModuleType('architecture_roam_measure');sys.modules[m.__name__]=m;exec(compile(bpy.data.texts['V24_25_测量工具.py'].as_string(),'measurement module','exec'),m.__dict__);checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
ck('World distance includes height component',abs(m.distance([(0,0,0),(3,4,12)])-13)<1e-7)
ck('Unit scale applied to length',abs(m.distance([(0,0,0),(3000,4000,0)],.001)-5)<1e-7)
rect=[(0,0,0),(3,0,0),(3,4,0),(0,4,0)];r=m.polygon_metrics(rect);ck('Horizontal rectangle area and perimeter',abs(r['area_m2']-12)<1e-6 and abs(r['perimeter_m']-14)<1e-6)
tilt=[(0,0,0),(3,0,0),(3,4,3),(0,4,3)];r=m.polygon_metrics(tilt);ck('Tilted face area and horizontal projection distinguished',abs(r['area_m2']-15)<1e-6 and abs(r['horizontal_area_m2']-12)<1e-6)
L=[(0,0,0),(3,0,0),(3,1,0),(1,1,0),(1,3,0),(0,3,0)];ck('Concave polygon triangulated correctly',abs(m.polygon_metrics(L)['area_m2']-5)<1e-6)
ck('Reversed winding gives same area',abs(m.polygon_metrics(L[::-1])['area_m2']-5)<1e-6)
ck('Millimetre source scaling squares for area',abs(m.polygon_metrics([(x*1000,y*1000,z)for x,y,z in rect],.001)['area_m2']-12)<1e-6)
for name,ps in [('crossed',[(0,0,0),(3,3,0),(0,3,0),(3,0,0)]),('collinear',[(0,0,0),(1,0,0),(2,0,0)]),('duplicate',[(0,0,0),(1,0,0),(1,0,0),(1,1,0)])]:
 try:m.polygon_metrics(ps);ok=False
 except ValueError:ok=True
 ck('Invalid '+name+' boundary rejected',ok)
points=[(0,0,0),(2,0,0),(2,2,.2),(0,2,0)];r=m.polygon_metrics(points);ck('Nonplanar boundary deviation reported',r['max_plane_deviation_m']>.09 and r['area_m2']>4)
records=[{'type':'LENGTH','points':[[0,0,0],[3,4,0]],'length_m':5},{'type':'AREA','points':rect,**m.polygon_metrics(rect)}];sc=bpy.context.scene;sc[m.KEY]=json.dumps(records);ck('History round trip in scene',m.read_records(sc)==json.loads(json.dumps(records)))
path=R/'V24_31_Measure_Known_Values.csv';m.export_records(records,path)
with path.open('r',encoding='utf-8-sig',newline='')as f:rows=list(csv.reader(f))
ck('CSV stores metre length and square metre area',len(rows)==3 and float(rows[1][2])==5 and float(rows[2][3])==12)
m.register();ck('Length area undo and export operators register',hasattr(bpy.ops.arch_roam,'measure_mode')and hasattr(bpy.ops.arch_roam,'measure_export'));m.unregister()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];(R/'V24_31_Measure_Math_QA.json').write_text(json.dumps({'status':'PASS_MEASUREMENT_MATH_AND_CSV'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail},ensure_ascii=False,indent=2));print('V25_MEASURE_MATH',len(checks),'FAIL',len(fail),flush=True)
for r in fail:print('FAIL',r,flush=True)
