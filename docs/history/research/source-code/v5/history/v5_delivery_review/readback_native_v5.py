"""Actual native block/component transform checks; no writes to native models."""
import sys,json,math,ctypes as C,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W),str(W/'libs')]
import rhino3dm as rh
import skp_api as su
OUT=Path(r'E:\jz\JIA\Rebuild_V5')
S=json.loads((OUT/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
REG={r['leaf_element']:r for r in S['door_registry'] if r.get('leaf_element')}
report={'scope':'Final native Rhino InstanceReference and SketchUp component instance translations, metres; native model files read only',
        'rhino':{},'sketchup':{}}
for mode in ['ARCH','VIS']:
    p=OUT/'06_Rhino'/f'Production_1QK_{mode}.3dm';m=rh.File3dm.Read(str(p));rows=[]
    for ob in m.Objects:
        name=ob.Attributes.Name
        if name not in REG or ob.Attributes.IsInstanceDefinitionObject:continue
        assert isinstance(ob.Geometry,rh.InstanceReference),(mode,name)
        t=ob.Geometry.Xform;actual=[t.M03,t.M13,t.M23];expected=REG[name]['hinge_world_m']
        error=math.dist(actual,expected);assert error<1e-8,(mode,name,error)
        params=json.loads(ob.Attributes.GetUserString('Parameters'))
        assert params['door_id']==REG[name]['door_id'] and params['role']=='LEAF'
        rows.append({'door_id':REG[name]['door_id'],'leaf':name,'origin_error_m':error,
                     'door_id_and_role_in_native_attributes':True})
    assert len(rows)==13,(mode,len(rows))
    report['rhino'][mode]={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'leaves_passed':len(rows),'results':rows}

for n,args in {
    'SUComponentInstanceGetTransform':[su.Ref,C.POINTER(su.Transform)],
    'SUComponentInstanceGetName':[su.Ref,su.PRef],
    'SUStringCreate':[su.PRef],'SUStringGetUTF8Length':[su.Ref,C.POINTER(su.SZ)],
    'SUStringGetUTF8':[su.Ref,su.SZ,C.c_void_p,C.POINTER(su.SZ)],
    'SUStringRelease':[su.PRef],
}.items():su.bind(n,args)
def name_of(ins):
    sr=su.new('SUStringCreate');su.ck(su.SUComponentInstanceGetName(ins,C.byref(sr)))
    length=su.SZ();su.ck(su.SUStringGetUTF8Length(sr,C.byref(length)))
    buf=C.create_string_buffer(length.value+1);got=su.SZ()
    su.ck(su.SUStringGetUTF8(sr,length.value+1,buf,C.byref(got)))
    value=buf.value.decode('utf-8');su.SUStringRelease(C.byref(sr));return value
def instances(ents):
    n=su.count('SUEntitiesGetNumInstances',ents);arr=(su.Ref*n)();got=su.SZ()
    su.ck(su.SUEntitiesGetInstances(ents,n,arr,C.byref(got)));result=list(arr)
    n=su.count('SUEntitiesGetNumGroups',ents);groups=(su.Ref*n)();got=su.SZ()
    su.ck(su.SUEntitiesGetGroups(ents,n,groups,C.byref(got)))
    for group in groups:result+=instances(su.new('SUGroupGetEntities',group))
    return result
su.SUInitialize()
for mode in ['ARCH','VIS']:
    p=OUT/'07_SketchUp'/f'Production_1QK_{mode}.skp';m=su.new('SUModelCreateFromFile',str(p).encode());rows=[]
    root=su.new('SUModelGetEntities',m)
    for ins in instances(root):
        name=name_of(ins)
        if name not in REG:continue
        t=su.Transform();su.ck(su.SUComponentInstanceGetTransform(ins,C.byref(t)))
        actual=[t.values[k]*.0254 for k in [12,13,14]]
        error=math.dist(actual,REG[name]['hinge_world_m']);assert error<1e-8,(mode,name,error)
        rows.append({'door_id':REG[name]['door_id'],'leaf':name,'origin_error_m':error})
    assert len(rows)==13,(mode,len(rows))
    su.SUModelRelease(C.byref(m))
    report['sketchup'][mode]={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'leaves_passed':len(rows),'results':rows}
su.SUTerminate()
report['pass']=True
(OUT/'09_Report/Door_Pivot_Native_Readback_V5.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Actual native Rhino ARCH/VIS + SKP ARCH/VIS: 13 leaves each PASS')
