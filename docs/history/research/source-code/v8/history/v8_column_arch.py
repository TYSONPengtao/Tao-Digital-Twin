import sys,json,copy,math
from pathlib import Path
W=Path(__file__).parent
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
import manifold3d as md
import export_v5 as ex
O=W/'v8_column_arch';O.mkdir(exist_ok=True)
def solid(g,origin=None):
    v,faces,_,_=ex.solid_data(g)
    ff=[]
    for face in faces:
        ids=ex.triangulate(v[face]) if len(face)>3 else [[0,1,2]]
        ff.extend([[face[i] for i in a] for a in ids])
    if origin is not None:v+=np.array(origin)
    s=md.Manifold(md.Mesh(np.asarray(v,np.float32),np.asarray(ff,np.uint32)))
    assert str(s.status())=='Error.NoError',str(s.status())
    return s
def apply(S):
    E={e['name']:e for e in S['elements']};changed=[];checks=[]
    for z,target in [(0,3.77),(3.9,7.37)]:
        name='ROMAN_COLUMN_X3.9_Z'+str(z)
        oldkey=E[name]['definition'];old=copy.deepcopy(S['definitions'][oldkey])
        Hold=old['parameters']['Height'];H=target-z
        key='V8_ROMAN_TO_SLAB_H'+str(int(round(H*1000)))
        d=copy.deepcopy(old)
        for i,p in enumerate(d['parts']):
            pr=p['geometry']['profile']
            if i==1:
                for q in pr:q[1]=.3+(q[1]-.3)*(H-.34-.3)/(Hold-.34-.3)
            elif i==2:
                for q in pr:q[1]+=H-Hold
        d['parameters'].update(Height=H,Column_Top_Target='Upper slab underside',Field_Survey_Status='PDF level datum; user-confirmed contact topology')
        d['source']='User clarification 2026-10-09 001628: column to slab underside; previous fluting/capital retained'
        S['definitions'][key]=d
        columns=[]
        for x in [3.9,9.1]:
            n='ROMAN_COLUMN_X'+str(x)+'_Z'+str(z);e=E[n]
            e.update(definition=key,status='V8_COLUMN_TOP_AT_SLAB_UNDERSIDE',source=d['source'])
            changed.append(n)
            body=None
            for p in d['parts']:
                q=solid(p['geometry'],e['origin']);body=q if body is None else body+q
            columns.append(body)
            checks.append({'id':n+'_top_contact','pass':abs(max(q[1] for p in d['parts'] for q in p['geometry']['profile'])+z-target)<1e-9,'top_z':target})
        n='PORCH_ARCH_BEAM_Z'+str(z);e=E[n]
        arch=solid(e['parts'][0]['geometry'])
        clip=md.Manifold.cube((5.2,.24,target+1),False).translate((3.9,-.12,-.5))
        arch=arch^clip
        cutters=columns[0]+columns[1]
        result=arch-cutters
        assert str(result.status())=='Error.NoError' and result.volume()>0
        mesh=result.to_mesh()
        e['parts']=[{'geometry':{'type':'polyhedron','vertices':np.asarray(mesh.vert_properties)[:,:3].astype(float).tolist(),'faces':np.asarray(mesh.tri_verts).astype(int).tolist()},'material':'M_Wall_Exterior'}]
        e.pop('bearing_seat_parameters',None)
        e['junction_v8']='Arch right end follows left surface of right Roman column; former under-cap square seats removed. Column reaches slab underside.'
        e['source']='User clarification 2026-10-09 001628; PDF slab levels retained'
        e['status']='V8_SIDE_CONTACT_ARCH_TO_FULL_HEIGHT_COLUMN'
        changed.append(n)
        overlap=(result^cutters).volume()
        checks.append({'id':n+'_no_column_volume_overlap','pass':overlap<1e-8,'overlap_m3':overlap,'arch_solid_volume_m3':result.volume(),'closed_manifold':str(result.status())})
        checks.append({'id':n+'_underside_same','pass':abs(float(np.asarray(mesh.vert_properties)[:,2].max())-target)<1e-6})
    assert all(c['pass'] for c in checks)
    S['v8_column_arch_changes']={'changed':changed,'checks':checks,'source':'User text answer to screenshot 001628; column tops meet existing level datum','metric_limit':'No revised structural design or reinforcement assertion'}
    return S['v8_column_arch_changes']
if __name__=='__main__':
    p=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
    S=json.loads(p.read_text(encoding='utf-8'));before=set(S['definitions']);report=apply(S)
    patch={'elements':[e for e in S['elements'] if e['name'] in report['changed']],'definitions':{k:v for k,v in S['definitions'].items() if k not in before},'report':report}
    (O/'Column_Arch_Patch_V8.json').write_text(json.dumps(patch,ensure_ascii=False,indent=2),encoding='utf-8')
    (O/'Column_Arch_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
