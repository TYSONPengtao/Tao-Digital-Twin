"""V11 requested modern Chinese timber pavilion, bounded by the corrected courtyard.

The metal canopy being replaced crosses the west wall.  This is a user-authorized
design adaptation, not a claim that the reference diagram is a measured survey.
Every visible piece is a closed, independently editable solid in local metres.
"""
import json, math, sys, hashlib, copy
from pathlib import Path
from collections import Counter
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np, manifold3d as mf, mapbox_earcut
from shapely.geometry import Polygon, box as pbox, Point, LineString
from shapely.geometry.polygon import orient
import export_v5 as ex

O=Path(__file__).parent
SRC=Path('E:/jz/JIA/Rebuild_V10_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json')
S=json.loads(SRC.read_text(encoding='utf8')); E={e['name']:e for e in S['elements']}
baseline_scene_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest()
refs=['D:/DJI/0002/DCIM/101MEDIA/DJI_0303.JPG',
      'D:/Desktop/f5e2d2aa-b7ef-4bc3-8b39-c35d600db64b.png',
      'D:/Desktop/f9db2bcf-fe61-400b-9a97-12857a7cb553.png',
      'D:/Desktop/屏幕截图 2026-10-09 115821.jpg',
      'D:/Desktop/屏幕截图 2026-10-09 115843.jpg']
# True exterior roof envelope. The gutters add 35 mm, still entirely inside X>.22.
x0,x1,y0,y1=.36,4.56,-7.10,-3.60
cx,cy=(x0+x1)/2,(y0+y1)/2
half=(y1-y0)/2; slope=.80/half
ground=-.45; decktop=-.25; ze=decktop+2.60; zr=ze+.80
rl=cx-((x1-x0)-(y1-y0))/2; rr=cx+((x1-x0)-(y1-y0))/2
posts=[(x0+.10,y0+.10),(x1-.10,y0+.10),(x1-.10,y1-.10),(x0+.10,y1-.10)]
plane_polys=[Polygon([(x0,y0),(x1,y0),(rr,cy),(rl,cy)]),
             Polygon([(x1,y0),(x1,y1),(rr,cy)]),
             Polygon([(x1,y1),(x0,y1),(rl,cy),(rr,cy)]),
             Polygon([(x0,y1),(x0,y0),(rl,cy)])]
def height(x,y):return ze+slope*min(x-x0,x1-x,y-y0,y1-y)
def b(x,y,z,w,d,h):return {'type':'box','origin':[x,y,z],'size':[w,d,h]}
def cyl(x,y,z,r,h,n=12):return dict(type='cylinder',origin=[x,y,z],radius=r,height=h,segments=n)
def p(g,m):return {'geometry':g,'material':m}
def poly3(v,fs):
    v=np.asarray(v,float);fs=[list(f) for f in fs]
    # Positive signed volume fixes the global winding; every generated face is consistently directed.
    tris=[]
    for f in fs:
        if len(f)==3:tris.append(f)
        else:tris.extend([[f[j] for j in t] for t in ex.triangulate(v[f])])
    t=np.asarray(tris,dtype=int)
    vol=np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6
    if vol<0:fs=[f[::-1] for f in fs]
    return dict(type='polyhedron',vertices=v.tolist(),faces=fs)
def skin(poly,top,bottom):
    poly=orient(poly,1);q=np.asarray(list(poly.exterior.coords)[:-1],float)
    n=len(q);ts=mapbox_earcut.triangulate_float64(q,np.array([n],np.uint32)).reshape(-1,3)
    v=[[*a,top(*a)] for a in q]+[[*a,bottom(*a)] for a in q]
    f=[t.tolist() for t in ts]+[(t[::-1]+n).tolist() for t in ts]
    f += [[i,i+n,(i+1)%n+n,(i+1)%n] for i in range(n)]
    return poly3(v,f)
def horizontal_rod(a,b,r,n=12):
    a=np.array(a,float);bb=np.array(b,float);u=(bb-a)/np.linalg.norm(bb-a)
    v=np.cross(u,[0,0,1]);v/=np.linalg.norm(v);w=np.cross(u,v)
    vv=[(end+r*(v*math.cos(t)+w*math.sin(t))).tolist() for end in [a,bb] for t in np.linspace(0,2*math.pi,n,endpoint=False)]
    fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
    return poly3(vv,fs)

R=[];A=[];checks=[]
def put(name,parts,classification,**meta):
    e=copy.deepcopy(E.get(name,dict(name=name,layer='60_SITE',family='SITE_MODEL',confidence='MEDIUM')))
    e.update(parts=parts,classification=classification,source='; '.join(refs),
             status='V11_USER_REFERENCE_DESIGN; METRIC_DIMENSIONS_NOT_SURVEYED',**meta)
    e.pop('definition',None);(R if name in E else A).append(e)
    return e
def ck(name,value,**data):
    checks.append(dict(name=name,passed=bool(value),**data))
    if not value:raise ValueError((name,data))

# Baseplate, independent stone tile slab and four post feet. No chairs/table guessed.
slab=[p(b(x0,y0,ground,4.2,3.5,.15),'M_Concrete')]
tiles=[]
for i in range(7):
    for j in range(6):
        xa=x0+i*.6+.0015; xb=min(x0+(i+1)*.6-.0015,x1-.0015)
        ya=y0+j*.6+.0015; yb=min(y0+(j+1)*.6-.0015,y1-.0015)
        if xb>xa and yb>ya:tiles.append(p(b(xa,ya,ground+.15,xb-xa,yb-ya,.05),'M_Stone'))
put('SITE_GAZEBO_V11_STONE_PLATFORM',slab+tiles,'STONE_TILE_PLATFORM',platform_top_m=decktop,reference_height_m=.20)
foot=[]
for x,y in posts:
    foot.append(p(b(x-.09,y-.09,decktop,.18,.18,.03),'M_Metal_Black'))
    for dx,dy in [(-.065,-.065),(.065,-.065),(.065,.065),(-.065,.065)]:
        foot.append(p(cyl(x+dx,y+dy,decktop+.03,.012,.009,6),'M_Metal_Stainless'))
    # Thin steel collar is a real open-sided bracket made of four closed plate solids.
    for dx in [-.065,.061]:foot.append(p(b(x+dx,y-.065,decktop+.03,.004,.13,.10),'M_Metal_Black'))
    for dy in [-.065,.061]:foot.append(p(b(x-.061,y+dy,decktop+.03,.122,.004,.10),'M_Metal_Black'))
put('SITE_GAZEBO_V11_POST_BASE_CONNECTORS',foot,'VISIBLE_STEEL_POST_BRACKETS',buried_foundations_modeled=False,anchor_details='Reference style, not an engineering bolt certification')
ringtop=height(*posts[0])-.103; ringbottom=ringtop-.16
put('SITE_GAZEBO_POSTS',[p(b(x-.06,y-.06,decktop+.03,.12,.12,ringbottom-decktop-.03),'M_Timber_Honey') for x,y in posts],
    'MODERN_CHINESE_TIMBER_POSTS',post_section_m=[.12,.12],reference_scope='User requested timber redesign; prior photo canopy used metal posts')
px0,px1=posts[0][0],posts[1][0]; py0,py1=posts[0][1],posts[2][1]
rings=[p(b(px0-.06,y-.06,ringbottom,px1-px0+.12,.12,.16),'M_Timber_Honey') for y in [py0,py1]]
rings += [p(b(x-.06,py0+.06,ringbottom,.12,py1-py0-.12,.16),'M_Timber_Honey') for x in [px0,px1]]
put('SITE_GAZEBO_V11_RING_BEAMS',rings,'BUTT_JOINED_TIMBER_RING_BEAMS',section_m=[.12,.16],joints='X beams run continuously; Y beams butt between them without duplicated corner volumes')

knees=[]
for x,y in posts:
    for axis,sign in [(0,1 if x==px0 else -1),(1,1 if y==py0 else -1)]:
        a=(x if axis==0 else y)+sign*.06; end=a+sign*.60
        za=ringbottom-.60; zb=ringbottom
        profile=[[a,za],[a,za+.14],[end-sign*.14,zb],[end,zb]]
        if axis==0:g=dict(type='prism',profile=[[u,y-.04,z] for u,z in profile],vector=[0,.08,0])
        else:g=dict(type='prism',profile=[[x-.04,u,z] for u,z in profile],vector=[.08,0,0])
        knees.append(p(g,'M_Timber_Honey'))
put('SITE_GAZEBO_V11_KNEE_BRACES',knees,'TIMBER_KNEE_BRACES',joint_description='Brace ends meet the post inner face and ring beam underside')

# Four watertight OSB/fascia roof panels, same four-slope roof datum.
put('SITE_GAZEBO_ROOF',[p(skin(q,lambda x,y:height(x,y)-.011,lambda x,y:height(x,y)-.029),'M_Timber_Honey') for q in plane_polys],
    'FOUR_SLOPE_TIMBER_ROOF_DECK',roof_type='hip',roof_envelope_m=[4.2,3.5],eave_height_above_platform_m=2.6,rise_m=.8,
    ridge_endpoints=[[rl,cy,zr],[rr,cy,zr]],sheet_or_tile='Visible separate gray asphalt shingle tabs with silver metal edging')
put('SITE_GAZEBO_V11_ROOF_INNER_LINING',[p(skin(q,lambda x,y:height(x,y)-.029,lambda x,y:height(x,y)-.036),'M_Timber_Dark_Eave') for q in plane_polys],
    'ROOF_INNER_TIMBER_LINING',modeled_thickness_m=.007)
put('SITE_GAZEBO_V11_ROOF_MEMBRANE',[p(skin(q,lambda x,y:height(x,y)-.005,lambda x,y:height(x,y)-.011),'M_Waterproof') for q in plane_polys],
    'CONTINUOUS_ROOF_WATERPROOF_FINISH',modeled_thickness_m=.006)

# Model visible rafter field under each roof plane, cropped before every hip seam.
rafters=[];purlins=[]
for idx,facet in enumerate(plane_polys):
    inner=facet.buffer(-.026,join_style=2)
    alongY=idx in [0,2]
    qmin,qmax=(x0,x1) if alongY else (y0,y1)
    for station in np.arange(qmin+.15,qmax-.10,.30):
        strip=pbox(station-.025,y0-1,station+.025,y1+1) if alongY else pbox(x0-1,station-.025,x1+1,station+.025)
        hit=inner.intersection(strip)
        if hit.is_empty or hit.area<.001:continue
        rafters.append(p(skin(hit,lambda x,y:height(x,y)-.036,lambda x,y:height(x,y)-.106),'M_Timber_Honey'))
    # Three continuous bearing purlins per slope support rafter undersides.
    for depth in [.35,.80,1.25]:
        if idx==0: strip=pbox(x0-1,y0+depth-.05,x1+1,y0+depth+.05)
        elif idx==2:strip=pbox(x0-1,y1-depth-.05,x1+1,y1-depth+.05)
        elif idx==1:strip=pbox(x1-depth-.05,y0-1,x1-depth+.05,y1+1)
        else:strip=pbox(x0+depth-.05,y0-1,x0+depth+.05,y1+1)
        # Purlins end against the full 80 mm hip beam, rather than duplicate it.
        hit=facet.buffer(-.042,join_style=2).intersection(strip)
        if hit.is_empty or hit.area<.001:continue
        purlins.append(p(skin(hit,lambda x,y:height(x,y)-.106,lambda x,y:height(x,y)-.206),'M_Timber_Honey'))
put('SITE_GAZEBO_V11_RAFTERS',rafters,'VISIBLE_TIMBER_RAFTERS',section_m=[.05,.07],nominal_spacing_m=.30)
put('SITE_GAZEBO_V11_PURLINS',purlins,'SLOPED_TIMBER_PURLINS',section_m=[.10,.10])

# Hip beams and ridge beam meet the ring/rafters with actual sloping upper faces.
hipbeams=[]
for x,y in posts:
    end=(rl,cy) if x==px0 else (rr,cy)
    poly=LineString([(x,y),end]).buffer(.04,cap_style=2,join_style=2)
    # Subdivide along roof planes so every face is planar at the hips.
    for facet in plane_polys:
        q=poly.intersection(facet)
        if q.is_empty or q.area<1e-7:continue
        hipbeams.append(p(skin(q,lambda x,y:height(x,y)-.106,lambda x,y:height(x,y)-.226),'M_Timber_Honey'))
ridge=[p(b(rl-.02,cy-.06,zr-.226,rr-rl+.04,.12,.12),'M_Timber_Honey')]
put('SITE_GAZEBO_V11_HIP_AND_RIDGE_BEAMS',hipbeams+ridge,'TIMBER_HIP_BEAMS_AND_RIDGE',joints='Hip beams partition at plane seams, no full overlapping duplicate beam')

shingles=[];areas=[]
for idx,facet in enumerate(plane_polys):
    for row in range(int(math.ceil(half/.14))):
        d0=row*.14+.001;d1=min(half,(row+1)*.14-.001)
        if d1<=d0:continue
        start=(x0 if idx in [0,2] else y0)-(.15 if row%2 else 0)
        end=x1 if idx in [0,2] else y1
        for t in np.arange(start,end,.30):
            if idx==0:tile=pbox(t+.0008,y0+d0,t+.2992,y0+d1)
            elif idx==2:tile=pbox(t+.0008,y1-d1,t+.2992,y1-d0)
            elif idx==1:tile=pbox(x1-d1,t+.0008,x1-d0,t+.2992)
            else:tile=pbox(x0+d0,t+.0008,x0+d1,t+.2992)
            q=facet.intersection(tile)
            if q.is_empty or q.area<2e-5:continue
            shingles.append(p(skin(q,lambda x,y:height(x,y)+.002,lambda x,y:height(x,y)-.005),'M_Roof'));areas.append(q.area)
put('SITE_GAZEBO_V11_INDIVIDUAL_ASPHALT_SHINGLES',shingles,'INDIVIDUAL_VISIBLE_GRAY_ASPHALT_SHINGLE_TABS',
    material_evidence='DJI_0303 four hip surfaces show gray staggered shingle texture',nominal_visible_module_m=[.30,.14],
    modeled_tabs=len(shingles),hidden_overlap_modeled=False)

# Folded hip / ridge cap modules with closed end profiles; roof ends inset keep bounds.
caps=[]
cap_lines=[((x0+.08,y0+.08),(rl,cy)),((x1-.08,y0+.08),(rr,cy)),
           ((x1-.08,y1-.08),(rr,cy)),((x0+.08,y1-.08),(rl,cy)),((rl,cy),(rr,cy))]
for a,bb in cap_lines:
    a=np.array(a,float);bb=np.array(bb,float);L=np.linalg.norm(bb-a);u=(bb-a)/L;n=np.array([-u[1],u[0]])
    for st in np.arange(0,L,.27):
        en=min(st+.29,L)
        vv=[]
        for s in [st,en]:
            c=a+u*s
            xy=[c+n*d for d in [-.045,0,.045]]
            top=[[*q,height(*q)+(.020 if i==1 else .012)] for i,q in enumerate(xy)]
            vv+=top+[q[:2]+[q[2]-.005] for q in top[::-1]]
        N=6;fs=[list(range(N-1,-1,-1)),list(range(N,2*N))]+[[i,(i+1)%N,(i+1)%N+N,i+N] for i in range(N)]
        caps.append(p(poly3(vv,fs),'M_Roof'))
put('SITE_GAZEBO_V11_FOLDED_RIDGE_CAPS',caps,'INDEPENDENT_FOLDED_ASPHALT_RIDGE_CAPS',cap_pitch_m=.27)

fascia=[];gutters=[];edge=[]
for y in [y0,y1]:fascia.append(p(b(x0,y-.014,ze-.13,x1-x0,.028,.12),'M_Timber_Honey'))
for x in [x0,x1]:fascia.append(p(b(x-.014,y0+.014,ze-.13,.028,y1-y0-.028,.12),'M_Timber_Honey'))
# Real U-profile thin closed strips. Corners use mutually exclusive mitred slabs.
for i,(a,bb) in enumerate([((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]):
    a=np.array(a);bb=np.array(bb);u=(bb-a)/np.linalg.norm(bb-a);n=np.array([-u[1],u[0]])
    # Negative offset is outside; L-shaped corner partitions are mitred at the ends.
    def strip_poly(d0,d1):
        prev=np.array([u[1],-u[0]]) # End planes point to previous / next miter.
        return Polygon([a+n*d0-u*abs(d0),bb+n*d0+u*abs(d0),bb+n*d1+u*abs(d1),a+n*d1-u*abs(d1)])
    # Use a common outer rectangle clipped into four true diagonal corner zones.
    outer=pbox(x0-.035,y0-.035,x1+.035,y1+.035); inner=pbox(x0+.008,y0+.008,x1-.008,y1-.008)
    zone=Polygon([tuple(a),tuple(bb),tuple(bb-n*.15+u*.15),tuple(a-n*.15-u*.15)])
    ring=outer.difference(inner).intersection(zone)
    if ring.area>0:
        # 2 mm bottom tray and outer vertical lip, separated watertight plates.
        gutters.append(p(skin(ring,lambda x,y:ze-.063,lambda x,y:ze-.065),'M_Metal_Stainless'))
    if i==0:lip=pbox(x0-.033,y0-.035,x1+.033,y0-.033)
    elif i==1:lip=pbox(x1+.033,y0-.033,x1+.035,y1+.033)
    elif i==2:lip=pbox(x0-.033,y1+.033,x1+.033,y1+.035)
    else:lip=pbox(x0-.035,y0-.033,x0-.033,y1+.033)
    gutters.append(p(skin(lip,lambda x,y:ze-.011,lambda x,y:ze-.063),'M_Metal_Stainless'))
    if i==0:inlip=pbox(x0,y0-.002,x1,y0)
    elif i==1:inlip=pbox(x1,y0+.002,x1+.002,y1-.002)
    elif i==2:inlip=pbox(x0,y1,x1,y1+.002)
    else:inlip=pbox(x0-.002,y0+.002,x0,y1-.002)
    gutters.append(p(skin(inlip,lambda x,y:ze-.011,lambda x,y:ze-.063),'M_Metal_Stainless'))
    # Photo-supported silver top-edge flashing with return on fascia.
    if i==0:q=pbox(x0,y0-.014,x1,y0+.015)
    elif i==1:q=pbox(x1-.015,y0+.015,x1+.014,y1-.015)
    elif i==2:q=pbox(x0,y1-.015,x1,y1+.014)
    else:q=pbox(x0-.014,y0+.015,x0+.015,y1-.015)
    edge.append(p(skin(q,lambda x,y:ze+.004,lambda x,y:ze+.001),'M_Metal_Stainless'))
put('SITE_GAZEBO_V11_FASCIA',fascia,'TIMBER_EAVE_FASCIA')
put('SITE_GAZEBO_V11_METAL_GUTTERS',gutters,'MITERED_SILVER_METAL_GUTTERS',reference_scope='User diagram style; photo supports silver eave edge, dimensions not surveyed')
put('SITE_GAZEBO_V11_METAL_EDGE_FLASHING',edge,'SILVER_ROOF_EDGE_FLASHING')

# Optional reference-driven bamboo roller curtains on west/back sides, east entry clear.
bamboo=[];tapes=[]
blind_records=[('WEST',(px0+.01,py0+.18),(px0+.01,py1-.18),.55,2.02),
               ('NORTH',(px0+.18,py1-.01),(px1-.18,py1-.01),1.10,2.02),
               ('SOUTH',(px0+.18,py0+.01),(px1-.18,py0+.01),1.68,2.02)]
for side,a,bb,low,high in blind_records:
    for z in np.arange(low,high,.017):bamboo.append(p(horizontal_rod([*a,z],[*bb,z],.005,12),'M_Timber_Honey'))
    rollz=high+.035;bamboo.append(p(horizontal_rod([*a,rollz],[*bb,rollz],.028,20),'M_Timber_Honey'))
    for t in [.08,.30,.50,.70,.92]:
        q=np.array(a)+(np.array(bb)-np.array(a))*t
        tapes.append(p(b(float(q[0]-.006),float(q[1]-.006),low-.004,.012,.012,high-low+.04),'M_Thatch'))
put('SITE_GAZEBO_V11_BAMBOO_ROLLER_BLINDS',bamboo+tapes,'REFERENCE_STYLE_BAMBOO_ROLLER_BLINDS',entry_side='EAST_OPEN',actual_lowering_state='Proposed reference arrangement; not confirmed by room/video survey')

rails=[]
# Full west rail only; north / south corner rail returns keep two additional access bays.
raillines=[((px0,py0+.12),(px0,py1-.12)),((px0+.12,py0),(px0+.78,py0)),((px0+.12,py1),(px0+.78,py1))]
for a,bb in raillines:
    a=np.array(a);bb=np.array(bb);alongX=abs(bb[0]-a[0])>abs(bb[1]-a[1]);L=np.linalg.norm(bb-a)
    for z,h in [(decktop+.12,.07),(decktop+.75,.07)]:
        if alongX:g=b(a[0],a[1]-.035,z,L,.07,h)
        else:g=b(a[0]-.035,a[1],z,.07,L,h)
        rails.append(p(g,'M_Timber_Honey'))
    for d in np.arange(.08,L-.05,.10):
        q=a+(bb-a)*d/L
        rails.append(p(b(float(q[0]-.02),float(q[1]-.02),decktop+.19,.04,.04,.56),'M_Timber_Honey'))
    # The two short rail returns have their own end stiles fixed to the platform.
    if alongX:rails.append(p(b(float(bb[0]-.03),float(bb[1]-.03),decktop,.06,.06,.84),'M_Timber_Honey'))
put('SITE_GAZEBO_V11_TIMBER_RAILS',rails,'TIMBER_RAILING_WITH_OPEN_ENTRY_BAYS',east_entry_clear_width_m=py1-py0-.12,
    north_south_entry_clear_width_m=px1-px0-.78-.06)

# Validate every closed source part independently, all coordinate envelope constraints.
vertices=[];stats=Counter();vols=[];ids=[]
for e in R+A:
    for j,part in enumerate(e['parts']):
        v,fs,_,_=ex.solid_data(part['geometry']);v=np.asarray(v,float);t=[]
        for f in fs:
            if len(f)==3:t.append(f)
            else:t.extend([[f[k] for k in tri] for tri in ex.triangulate(v[f])])
        t=np.asarray(t,dtype=np.uint64);area=np.linalg.norm(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]),axis=1)/2
        # Mesh convention may be inward globally for prisms; reverse when needed.
        volume=np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6
        if volume<0:t=t[:,::-1]
        man=mf.Manifold(mf.Mesh64(v.astype(np.float64),t))
        ck(e['name']+'__'+str(j)+' closed',man.status()==mf.Error.NoError and man.volume()>1e-10,
           status=str(man.status()),volume_m3=man.volume())
        ck(e['name']+'__'+str(j)+' finite',np.isfinite(v).all() and (area>1e-12).all())
        vertices.extend(v.tolist());vols.append(man.volume());stats[part['geometry']['type']]+=1
        ids.append(e['name']+'__'+str(j))
vv=np.asarray(vertices);minimum=vv.min(0);maximum=vv.max(0)
ck('all_pavilion_inside_west_wall',minimum[0]>.22,minimum_x_m=float(minimum[0]),wall_coping_interior_limit_m=.22)
ck('all_pavilion_inside_south_return',minimum[1]>-11.48,minimum_y_m=float(minimum[1]))
ck('roof_entirely_in_courtyard',x0>.22 and y0>-11.48)
ck('exactly_four_posts',len(R[0]['parts'])==4 if R[0]['name']=='SITE_GAZEBO_POSTS' else len(next(e for e in R if e['name']=='SITE_GAZEBO_POSTS')['parts'])==4)
ck('removed_old_canopy_classification',all(e['classification']!='LIGHT_CANOPY_WITH_METAL_ROOF' for e in R))
ck('existing_scene_not_written',hashlib.sha256(SRC.read_bytes()).hexdigest()==baseline_scene_sha256)
out=dict(replace=R,add=A,remove=[],definitions={},materials={},changes=[dict(id='V11_PAVILION_INSIDE_WALL',elements=[e['name'] for e in R+A],
   description='Replace wall-crossing metal canopy with a user-reference modern Chinese timber hip pavilion wholly within the courtyard; real timber, shingle, bamboo, stone and metal solids.',
   evidence=refs,metric_status='REFERENCE_DIMENSIONS_NOT_FIELD_MEASURED',envelope_minimum=minimum.tolist(),envelope_maximum=maximum.tolist())])
(O/'Mutation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
qa=dict(status='PASS',parts=len(ids),nodes=len(R)+len(A),replace=[e['name'] for e in R],add=[e['name'] for e in A],
        geometry_types=dict(stats),closed_manifold_volumes=len(vols),minimum_m=minimum.tolist(),maximum_m=maximum.tolist(),
        west_coping_clearance_m=float(minimum[0]-.22),south_wall_clearance_m=float(minimum[1]+11.48),
        shingles=len(shingles),bamboo_parts=len(bamboo),rafters=len(rafters),checks=checks,
        existing_source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
        field_survey_certified=False,structural_design_certified=False)
(O/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
(O/'Parameters.md').write_text('''# V11 亭子修模参数\n\n替换 SITE_GAZEBO_POSTS 与 SITE_GAZEBO_ROOF。旧亭屋顶 X=-0.70..4.15m 跨越西院墙，新亭所有构件 X≥0.325m，墙帽院内界 X=0.22m，最小余量 105mm；南墙内界Y=-11.48m，亭最低Y=-7.135m。亭平台及屋面4.2×3.5m、柱中心4.0×3.3m、檐高2.6m、脊起0.8m、柱120方，取自用户最后两张四坡木亭图，属于参考造型尺寸，未称为实测。\n\nDJI_0303支持灰色错缝沥青瓦四坡屋面及银色檐框；原亭细金属柱改为木柱，是用户本轮授权的新中式做法，竹帘与栏杆同样为参考造型。DNG_0511/0513为厨房与外墙连接参考，不用于假定亭尺寸。\n\n木柱顶接圈梁底；X方向圈梁连续、Y方向圈梁端接，无角部重复梁；斜撑止于柱侧面/梁底；各坡椽子檩条裁在坡面范围，角梁顺屋脊分区。屋面内衬、OSB板、防水面、逐片可见沥青瓦与折脊帽分别闭合。天沟由底板及侧唇真实薄壁闭合板件组成，金属檐边独立。无虚构桌椅、植物、地埋基础。东侧通道保持开放，北/南短栏杆与帘示意为参考布置，不宣称与现场降帘状态一致。\n\n以 Geometry_QA.json 为准确最终件数与包络。生成过程中不写总场景及任何3dm，全部只在本子任务目录。\n''',encoding='utf8')
print(json.dumps({k:qa[k] for k in ['status','parts','nodes','geometry_types','minimum_m','maximum_m','west_coping_clearance_m','shingles','bamboo_parts','rafters']},ensure_ascii=False),flush=True)
