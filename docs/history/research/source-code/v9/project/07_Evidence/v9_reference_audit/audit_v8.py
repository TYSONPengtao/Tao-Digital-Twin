import sys,json,hashlib,math
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
import manifold3d as md
import export_v5 as ex
O=Path(__file__).parent
SOURCE=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
S=json.loads(SOURCE.read_text(encoding='utf8'));E={e['name']:e for e in S['elements']}
def solid(g):
    v,faces,_,_=ex.solid_data(g);ff=[]
    for face in faces:
        ids=ex.triangulate(v[face]) if len(face)>3 else [[0,1,2]]
        ff.extend([[face[i] for i in a] for a in ids])
    s=md.Manifold(md.Mesh(np.asarray(v,np.float32),np.asarray(ff,np.uint32)))
    assert str(s.status())=='Error.NoError',str(s.status())
    return s,np.asarray(v)
base,bv=solid(E['SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE']['parts'][0]['geometry'])
rows=[]
for name in ['SITE_KITCHEN_CHINESE_TILE_ROOF','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0','SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES','SITE_KITCHEN_EXPOSED_TIMBER_ROOF_FRAMING','SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS']:
    hit=0.;parts=[]
    for i,p in enumerate(E[name]['parts']):
        s,v=solid(p['geometry']);vol=(s^base).volume()
        if vol>1e-7:parts.append({'index':i,'volume_m3':vol})
        hit+=vol
    rows.append({'name':name,'intersection_with_gate_base_m3':hit,'parts_intersecting':parts})
def zk(x,y):return min(-.29889484+.39953197*x-.00177447*y,9.41247826-.440834917*x+.00312578606*y)-.05+.08*max(0,(7.2-x)/.22)**2
def zg(x,y):
    t=abs((x-6.55)/2.55);v=abs((y+11.62)/1.4)
    return 4.35-.58*v**1.6+.30*t**6+.40*t**5*v**3
q=np.array([[x,y,zg(x,y)-.075-zk(x,y)-.10] for x in np.linspace(6.98,9.05,101) for y in np.linspace(-12.05,-10.22,101)])
refs=[Path(r'D:\Desktop\1aeb5b24-97ff-45f0-a8e3-f2916523ffb3.png'),Path(r'D:\Desktop\4daa4b13-ab29-4a24-81ca-0a7345c7eecb.png')]+[Path(r'D:\DJI\0002\DCIM\101MEDIA')/f'DJI_{n:04}.JPG' for n in [46,47,48,100,101]]+[Path(r'D:\DJI\0003\DCIM\101MEDIA\DJI_0059.JPG')]
r={'status':'READ_ONLY_V8_AUDIT','source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'method':'Original Scene mesh conversion and manifold3d volume Boolean; shell-local meters; no model edits','base_bounds_min':bv.min(0).tolist(),'base_bounds_max':bv.max(0).tolist(),'roof_rectangular_xy_overlap_m2':(9.05-6.98)*(-10.22+12.05),'roof_rectangular_xy_overlap_bounds':[6.98,-12.05,9.05,-10.22],'roof_to_roof_only_min_net_gap_m':float(q[:,2].min()),'roof_to_roof_only_min_net_gap_point':q[q[:,2].argmin()].tolist(),'collisions':rows,'sources':[{'path':str(p),'exists':p.exists(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else ''} for p in refs],'limitations':['Two user diagrams explicitly state photo-inferred schematic, not measured construction drawing','Roof-to-roof gap excludes solid gate closure and fascia details; do not reuse alone as clearance pass','Gray eave supports cannot be certified as structural timber from photographs','Drainage arrows are visual roof fall indications, not hydraulic/drainage design']}
(O/'V8_Independent_Reference_Audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(r,ensure_ascii=False,indent=2))
