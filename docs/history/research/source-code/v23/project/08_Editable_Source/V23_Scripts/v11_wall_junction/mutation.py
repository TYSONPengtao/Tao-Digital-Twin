"""Photo-backed V10 courtyard masonry wall finishes and real pierced ceramic coping.

The V9 masonry core, wall route, room layouts, gate and screenwall remain immutable.
All newly inferred detail dimensions are recorded below; no buried construction is fabricated.
"""
import sys, json, math, copy, hashlib
from pathlib import Path
from collections import Counter
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np, mapbox_earcut, manifold3d as mf
from shapely import set_precision
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient as polyorient
import export_v5 as ex

OUT=Path(__file__).parent
SRC=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
S=json.loads(SRC.read_text(encoding='utf8')); E={e['name']:e for e in S['elements']}
REFS=['D:/Desktop/屏幕截图 2026-10-09 115821.jpg', 'D:/Desktop/屏幕截图 2026-10-09 120147.jpg', 'D:/Desktop/d15a543f-dee1-492a-8cbb-cb87cb3bffa1.png', 'D:/Desktop/DJI_0511.DNG', 'D:/Desktop/DJI_0513.DNG',
      'D:/DJI/0002/DCIM/101MEDIA/DJI_0161.JPG','D:/DJI/0002/DCIM/101MEDIA/DJI_0156.JPG',
      'D:/DJI/0002/DCIM/101MEDIA/DJI_0025.JPG','D:/DJI/0002/DCIM/101MEDIA/DJI_0073.JPG']
R=[];A=[];checks=[];hole_probes=[];clipped_parts=[];layer_records=[];all_holes=[]
BASE_E=copy.deepcopy(E)

def put(name, parts, cls, **props):
    e=copy.deepcopy(E.get(name,dict(name=name,layer='60_SITE',family='SITE_MODEL',confidence='MEDIUM')))
    e.update(parts=[p for p in parts if p is not None],classification=cls,status='V11_USER_CONFIRMED_RIGHT_ANGLE_WALL; PHOTO_RELATIONS_AND_REFERENCE_DETAILS',source='; '.join(REFS),**props)
    (R if name in E else A).append(e);return e
def part(g,m):return dict(geometry=g,material=m) if g is not None else None
def check(name,ok,**data):
    checks.append(dict(name=name,passed=bool(ok),**data))
    if not ok:raise ValueError((name,data))

def triangles(v,fs):
    rr=[]
    for f in fs:
        if len(f)==3:rr.append(f)
        else:rr.extend([[f[i] for i in t] for t in ex.triangulate(v[f])])
    return np.asarray(rr,dtype=np.int32)
def oriented(g):
    v,fs,_,_=ex.solid_data(g);fs=[list(f) for f in fs];ee={}
    for i,f in enumerate(fs):
        for a,b in zip(f,f[1:]+f[:1]):ee.setdefault(tuple(sorted((a,b))),[]).append((i,a,b))
    if any(len(q)!=2 for q in ee.values()):raise ValueError(('open source body',g['type']))
    links=[[] for f in fs]
    for (i,a,b),(j,c,d) in ee.values():
        same=a==c and b==d;links[i].append((j,same));links[j].append((i,same))
    flips={}
    for root in range(len(fs)):
        if root in flips:continue
        flips[root]=False;stack=[root]
        while stack:
            i=stack.pop()
            for j,same in links[i]:
                wanted=flips[i]^same
                if j in flips:assert wanted==flips[j]
                else:flips[j]=wanted;stack.append(j)
    fs=[f[::-1] if flips[i] else f for i,f in enumerate(fs)]
    t=triangles(v,fs);volume=np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6
    if volume<0:fs=[f[::-1] for f in fs]
    return dict(type='polyhedron',vertices=v.tolist(),faces=fs)
def manifold(g):
    g=oriented(g);v=np.asarray(g['vertices']);t=triangles(v,g['faces'])
    a=mf.Manifold(mf.Mesh64(v.astype(np.float64),t.astype(np.uint64)))
    assert a.status()==mf.Error.NoError,a.status();return a
def fromman(a):
    # RemovesubmicronBooleanfacet slivers before CAD triangulation. This is
    # 0.1micron max tolerance, far below the1mm project CAD tolerance.
    mm=a.simplify(1e-7).to_mesh64();return dict(type='polyhedron',vertices=np.asarray(mm.vert_properties)[:,:3].tolist(),faces=np.asarray(mm.tri_verts).tolist())
def ringgeom(poly,z,h):
    poly=polyorient(poly,1)
    return dict(type='prism_holes',outer=[list(p) for p in list(poly.exterior.coords)[:-1]],holes=[[list(p) for p in list(q.coords)[:-1]] for q in poly.interiors],z=z,height=h)
def mapped(g,fn):
    v,fs,_,_=ex.solid_data(g)
    return oriented(dict(type='polyhedron',vertices=[fn(*q) for q in v],faces=fs))

class Segment:
    def __init__(self,a,b,za,zb,ba,bb,left_a,left_b, j, chain):
        self.a=np.array(a);self.b=np.array(b);self.L=float(np.linalg.norm(self.b-self.a));self.u=(self.b-self.a)/self.L
        self.n=np.array([-self.u[1],self.u[0]]);self.za=za;self.zb=zb;self.ba=ba;self.bb=bb
        self.offa=np.array(left_a);self.offb=np.array(left_b);self.j=j;self.chain=chain
        self.plan=Polygon([self.a-self.offa*.25,self.b-self.offb*.25,self.b+self.offb*.25,self.a+self.offa*.25])
        self.clipper=None
    def crown(self,s):
        # A 250 mm level corner collar gives both miter faces the same elevation.
        if self.chain=='SITE_COURTYARD_WEST_TILE_WALL':
            if self.j==0:
                return self.zb if s>=self.L-.25 else self.za+(self.zb-self.za)*s/(self.L-.25)
            if self.j==1:
                return self.za if s<=.25 else self.za+(self.zb-self.za)*(s-.25)/(self.L-.25)
        return self.za+(self.zb-self.za)*s/self.L
    def base(self,s):
        if self.chain=='SITE_COURTYARD_WEST_TILE_WALL':
            if self.j==0:
                return self.bb if s>=self.L-.25 else self.ba+(self.bb-self.ba)*s/(self.L-.25)
            if self.j==1:
                return self.ba if s<=.25 else self.ba+(self.bb-self.ba)*(s-.25)/(self.L-.25)
        return self.ba+(self.bb-self.ba)*s/self.L
    def xyz(self,s,d,z):return [*(self.a+self.u*s+self.n*d),float(z)]
    def local(self,q):
        r=np.asarray(q)-self.a;return float(r@self.u),float(r@self.n)
    def xystrip(self,half):return Polygon([self.a-self.offa*half,self.b-self.offb*half,self.b+self.offb*half,self.a+self.offa*half])
    def crop(self,g,label):
        # True angle-bisector plan partition: adjacent complete roof pieces never overlap.
        vv=np.asarray(g['vertices']);outside=any(not self.plan.buffer(1e-9).covers(Point(*p[:2])) for p in vv)
        if not outside:return g
        if self.clipper is None:self.clipper=manifold(ringgeom(self.plan,-4,10))
        hit=manifold(g)^self.clipper
        clipped_parts.append(dict(chain=self.chain,segment=self.j,part=label,volume_m3=hit.volume(),deleted=hit.is_empty()))
        return None if hit.is_empty() else fromman(hit)

def segments(chain, pts):
    body=E[chain]['parts'];p=np.array(pts,float);uv=np.diff(p,axis=0);uv/=np.linalg.norm(uv,axis=1)[:,None]
    nn=np.c_[-uv[:,1],uv[:,0]];offs=[]
    for j in range(len(p)):
        q=nn[0] if j==0 else nn[-1] if j==len(p)-1 else (nn[j-1]+nn[j])/2
        if 0<j<len(p)-1:q=q/np.dot(q,nn[j])
        offs.append(q)
    z=[];b=[]
    for j in range(len(p)):
        cand=[]
        for part0 in body:
            for v in part0['geometry']['vertices']:
                # Every corresponding corner has the same endpoint station and elevation.
                if j==0:station=np.dot(np.array(v[:2])-p[0],uv[0]);good=abs(station)<1e-7
                elif j==len(p)-1:station=np.dot(np.array(v[:2])-p[-1],uv[-1]);good=abs(station)<1e-7
                else:good=abs(v[0]-p[j,0])<.3 and abs(v[1]-p[j,1])<.3
                if good:cand.append(v[2])
        assert cand;z.append(max(cand));b.append(min(cand))
    return [Segment(p[j],p[j+1],z[j],z[j+1],b[j],b[j+1],offs[j],offs[j+1],j,chain) for j in range(len(p)-1)]

def strip_piece(seg, poly, top, bottom):
    poly=polyorient(set_precision(poly,1e-10).simplify(1e-9,preserve_topology=True),1)
    rings=[list(poly.exterior.coords)[:-1]]+[list(h.coords)[:-1] for h in poly.interiors]
    q=np.asarray([p for ring in rings for p in ring]);n=len(q)
    ts=mapbox_earcut.triangulate_float64(q,np.cumsum([len(r) for r in rings]).astype(np.uint32)).reshape(-1,3)
    v=[[*xy,top(*seg.local(xy))] for xy in q]+[[*xy,bottom(*seg.local(xy))] for xy in q]
    fs=[t.tolist() for t in ts]+[(t[::-1]+n).tolist() for t in ts]
    off=0
    for ring in rings:
        count=len(ring);fs += [[off+i,off+(i+1)%count,off+(i+1)%count+n,off+i+n] for i in range(count)];off+=count
    return oriented(dict(type='polyhedron',vertices=v,faces=fs))
def strip_solid(seg,poly,top,bottom):
    if seg.chain!='SITE_COURTYARD_WEST_TILE_WALL':return strip_piece(seg,poly,top,bottom)
    knee=seg.L-.25 if seg.j==0 else .25
    stations=[seg.local(p)[0] for p in list(poly.exterior.coords)]
    lo,hi=min(stations),max(stations)
    if not lo+1e-8<knee<hi-1e-8:return strip_piece(seg,poly,top,bottom)
    pieces=[]
    for a,b in [(lo-1,knee),(knee,hi+1)]:
        cut=Polygon([seg.xyz(a,-5,0)[:2],seg.xyz(b,-5,0)[:2],seg.xyz(b,5,0)[:2],seg.xyz(a,5,0)[:2]])
        q=poly.intersection(cut)
        for pp in getattr(q,'geoms',[q]):
            if pp.area>1e-12:pieces.append(manifold(strip_piece(seg,pp,top,bottom)))
    return fromman(mf.Manifold.batch_boolean(pieces,mf.OpType.Add))

def tile(seg,center,side,cover):
    radius=.043 if cover else .0435
    us=np.linspace(-radius,radius,13)
    ds=[.05,.205]
    v=[]
    def top(s,d,u):
        return seg.crown(s)+(.154 if cover else .149)-.6*abs(d)+(math.sqrt(max(0,radius*radius-u*u)) if cover else -.006+.005*(u/radius)**2)
    for u in us:
        for d0 in ds:
            d=d0*side;s=center+u;v.append(seg.xyz(s,d,top(s,d,u)))
    v+= [p[:2]+[p[2]-(.009 if cover else .008)] for p in v]
    N=len(us)*len(ds);fs=[]
    for i in range(len(us)-1):
        a=2*i;b=a+2;fs += [[a,b,b+1,a+1],[a+N,a+1+N,b+1+N,b+N]]
    rim=[0,1]+[2*i+1 for i in range(1,len(us))]+[2*(len(us)-1)]+[2*i for i in range(len(us)-2,0,-1)]
    fs += [[a,b,b+N,a+N] for a,b in zip(rim,rim[1:]+rim[:1])]
    g=oriented(dict(type='polyhedron',vertices=v,faces=fs))
    return seg.crop(g,('cover' if cover else 'pan')+f'_{center:.6f}_{side}')

def lotus_disc(seg,s,side):
    # One closed watertight relief disc, eight modeled radial petal lobes.
    radius=.053;centerz=seg.crown(s)+.154-.6*.205+.021
    rings=[.013,.027,.041,.053];N=32;v=[]
    v.append(seg.xyz(s,side*(.205+.006),centerz))
    for r in rings:
        for j in range(N):
            t=2*math.pi*j/N
            relief=.0035*(.5+.5*math.cos(8*t))*(math.sin(math.pi*r/radius)**2)+(.0025 if r==rings[-1] else 0)
            v.append(seg.xyz(s+r*math.cos(t),side*(.205+.002+relief),centerz+r*math.sin(t)))
    back=len(v);v.append(seg.xyz(s,side*(.205-.011),centerz))
    backstart=len(v)
    for j in range(N):
        t=2*math.pi*j/N;v.append(seg.xyz(s+radius*math.cos(t),side*(.205-.011),centerz+radius*math.sin(t)))
    fs=[[0,1+j,1+(j+1)%N] for j in range(N)]
    for k in range(len(rings)-1):
        a=1+k*N;b=a+N
        fs += [[a+j,b+j,b+(j+1)%N,a+(j+1)%N] for j in range(N)]
    outer=1+(len(rings)-1)*N
    fs += [[outer+j,backstart+j,backstart+(j+1)%N,outer+(j+1)%N] for j in range(N)]
    fs += [[back,backstart+(j+1)%N,backstart+j] for j in range(N)]
    return seg.crop(oriented(dict(type='polyhedron',vertices=v,faces=fs)),f'lotus_{s:.6f}_{side}')

def floral(seg,start,end):
    # Independent 500 mm nominal clay flower units with four connected-lobe holes.
    outer=box(start,0,end,.145);holes=[];probe=None
    pitch=.125
    for cx in np.arange(start+.0625,end-.04,pitch):
        cx=float(cx);cy=.0725
        if (seg.j==0 and cx>seg.L-.120) or (seg.j==1 and cx<.120):continue
        hole=unary_union([Point(cx+dx,cy+dy).buffer(.0265,quad_segs=8) for dx,dy in [(0,0),(.026,0),(-.026,0),(0,.026),(0,-.026)]])
        if outer.buffer(-.008).contains(hole):
            holes.append(hole);probe=(cx,cy,hole.bounds)
            all_holes.append(dict(node=seg.chain+'_V10_OPEN_FLOWER_BRICKS',segment=seg.j,station_local_m=cx,segment_length_m=seg.L,point_local_m=seg.xyz(cx,0,seg.crown(cx)+.2425),normal_local=[*seg.n,0],hole_width_m=.105,hole_height_m=.105,through_depth_m=.068,drill_diameter_m=.012,drill_depth_m=.1))
    poly=outer.difference(unary_union(holes))
    g=ringgeom(poly,0,.068)
    g=mapped(g,lambda s,z,d:seg.xyz(s,d-.034,seg.crown(s)+.170+z))
    g=seg.crop(g,f'flower_{start:.6f}')
    if probe and not hole_probes:
        cx,cy,bounds=probe
        hole_probes.append(dict(node=seg.chain+'_V10_OPEN_FLOWER_BRICKS',point_local_m=seg.xyz(cx,0,seg.crown(cx)+.170+cy),normal_local=[*seg.n,0],solid_probe_neighbor_local_m=seg.xyz(cx,.0,seg.crown(cx)+.170+.140),hole_width_m=bounds[2]-bounds[0],hole_height_m=bounds[3]-bounds[1],through_depth_m=.068,expected_intersection_volume_m3=0))
    return g,len(holes)

def frame(seg,s0,w,side,seat):
    h=.375;corner=.045;pth=[(0,corner),(corner,corner),(corner,0),(w-corner,0),(w-corner,corner),(w,corner),(w,h-corner),(w-corner,h-corner),(w-corner,h),(corner,h),(corner,h-corner),(0,h-corner)]
    outer=Polygon(pth);rings=[outer.difference(outer.buffer(-.019,join_style=2)),outer.buffer(-.033,join_style=2).difference(outer.buffer(-.041,join_style=2))]
    pp=[]
    for j,ring in enumerate(rings):
        g=ringgeom(ring,0,.022 if j==0 else .012)
        g=mapped(g,lambda s,z,d:seg.xyz(s+s0,side*(seat+d),seg.crown(s+s0)-.56+z))
        pp.append(part(g,'M_Stone_Frame'))
    return pp

def white_finish(seg):
    # Same18 mm known courtyard-facing finish, continued through the actual corner.
    q=seg.xystrip(.143).difference(seg.xystrip(.125))
    candidates=[p for p in getattr(q,'geoms',[q]) if p.area>1e-8]
    inner=[p for p in candidates if seg.local([p.centroid.x,p.centroid.y])[1]>0]
    return [part(strip_solid(seg,p,lambda s,d:seg.crown(s),lambda s,d:0.0),'M_Wall_Exterior') for p in inner]

# Only the inner west courtyard return changes; the door jamb and main-building
# endpoints stay fixed. User corrected the previous inferred oblique link.
CHAIN='SITE_COURTYARD_WEST_TILE_WALL'
OLD_ROUTE=[[0,1.9],[0,-10.7],[4.9,-11.7]]
NEW_ROUTE=[[0,1.9],[0,-11.7],[4.9,-11.7]]
oldv=[np.asarray(p['geometry']['vertices']) for p in E[CHAIN]['parts']]
bz=[float(oldv[0][0,2]),float(oldv[0][1,2]),float(oldv[2][1,2])]
tz=[float(oldv[1][4,2]),float(oldv[1][5,2]),float(oldv[3][5,2])]
# Keep established endpoint/joint heights rather than inventing a new survey datum.
seeds=[Segment([0,1.9],[0,-11.7],tz[0],tz[1],bz[0],bz[1],[1,0],[1,1],0,CHAIN),
       Segment([0,-11.7],[4.9,-11.7],tz[1],tz[2],bz[1],bz[2],[1,1],[0,1],1,CHAIN)]
core=[]
for seg in seeds:
    # Split at the level corner collar. Each resulting solid has planar triangles,
    # shared 45-degree corner seams, and matched top/bottom elevations.
    intervals=[(0,seg.L-.25),(seg.L-.25,seg.L+.125)] if seg.j==0 else [(-.125,.25),(.25,seg.L)]
    for s0,s1 in intervals:
        xy=Polygon([seg.xyz(s0,-1,0)[:2],seg.xyz(s1,-1,0)[:2],seg.xyz(s1,1,0)[:2],seg.xyz(s0,1,0)[:2]])
        q=seg.xystrip(.125).intersection(xy)
        core.append(part(strip_solid(seg,q,lambda s,d:seg.base(s)+2.,lambda s,d:seg.base(s)),'M_Grey_Brick'))
        core.append(part(strip_solid(seg,q,lambda s,d:seg.crown(s),lambda s,d:seg.base(s)+2.),'M_Wall_Exterior'))
E[CHAIN]=copy.deepcopy(E[CHAIN]);E[CHAIN]['parts']=core
put(CHAIN,core,'RIGHT_ANGLE_CHINESE_TILE_TOP_MASONRY_WALL',wall_route_local_m=NEW_ROUTE,previous_inferred_route_local_m=OLD_ROUTE,plan_width=.25,corner_angle_degrees=90.,corner_collar_length_m=.25,corner_height_datum_preserved=True,user_confirmed_plan_relation=True)
CHAINS=[(CHAIN,NEW_ROUTE),('SITE_GATE_EAST_FLANK',[[8.3,-11.7],[13.3,-11.7]])]
core_hashes={n:hashlib.sha256(json.dumps(BASE_E[n],sort_keys=True,separators=(',',':')).encode()).hexdigest() for n,_ in CHAINS}
allseg={n:segments(n,pts) for n,pts in CHAINS}
# The longer existing east flank is buried in the V9 south kitchen gable.
# Keep that core exactly, but do not install new ornament inside masonry.
kgparts=E['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES']['parts']
kv=np.asarray(kgparts[0]['geometry']['vertices'])
kplan=Polygon(np.r_[kv[::4,:2],kv[1::4,:2][::-1]])
hit=LineString(CHAINS[1][1]).intersection(kplan)
east_finish_stop_x=min(x for x,y in hit.coords)
kitchen_obstacle=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in kgparts],mf.OpType.Add)
def trim_kitchen(parts, name):
    out=[]
    for i,p in enumerate(parts):
        if p is None:continue
        a=manifold(p['geometry']);iv=(a^kitchen_obstacle).volume()
        if iv>1e-12:
            result=a-kitchen_obstacle
            clipped_parts.append(dict(chain='SITE_GATE_EAST_FLANK',part=name+f'_{i}',kitchen_trim_volume_m3=iv,deleted=result.is_empty()))
            if not result.is_empty():out.append(part(fromman(result),p['material']))
        else:out.append(p)
    return out
holes_total=0
for chain,pts in CHAINS[:1]:
    segs=allseg[chain]
    if chain=='SITE_GATE_EAST_FLANK':
        sg=segs[0];end=east_finish_stop_x-sg.a[0]
        segs=[Segment(sg.a,[east_finish_stop_x,-11.7],sg.za,sg.crown(end),sg.ba,sg.base(end),sg.offa,sg.offb,sg.j,sg.chain)]
    back=[];covers=[];pans=[];discs=[];flowers=[];cap=[];bricks=[];mortar=[];frames=[]
    for seg in segs:
        # Split on the real crest so the thin sheet expresses two slopes.
        for side in [-1,1]:
            q=seg.xystrip(.205).intersection(Polygon([seg.a,seg.b,seg.b+seg.offb*.26*side,seg.a+seg.offa*.26*side]))
            back.append(part(strip_solid(seg,q,lambda s,d:seg.crown(s)+.135-.6*abs(d),lambda s,d:seg.crown(s)+.112-.6*abs(d)),'M_Roof'))
        # Ridge seat is solid only below the open flower apertures.
        cap.append(part(strip_solid(seg,seg.xystrip(.045),lambda s,d:seg.crown(s)+.170,lambda s,d:seg.crown(s)+.126),'M_Roof'))
        cap.append(part(strip_solid(seg,seg.xystrip(.045),lambda s,d:seg.crown(s)+.331,lambda s,d:seg.crown(s)+.315),'M_Roof'))
        cap.append(part(strip_solid(seg,seg.xystrip(.055),lambda s,d:seg.crown(s)+.357-abs(d)*.15,lambda s,d:seg.crown(s)+.331),'M_Roof'))
        # At miter corners trim every end tile to the shared angle-bisector seam.
        centers=np.arange(.055,seg.L-.020,.120)
        for center in centers:
            for side in [-1,1]:
                covers.append(part(tile(seg,float(center),side,True),'M_Roof'))
                discs.append(part(lotus_disc(seg,float(center),side),'M_Roof'))
        for center in np.arange(.115,seg.L-.015,.120):
            for side in [-1,1]:pans.append(part(tile(seg,float(center),side,False),'M_Roof'))
        for start in np.arange(0,seg.L-.08,.5):
            g,count=floral(seg,float(start),min(float(start+.5),seg.L));flowers.append(part(g,'M_Roof'));holes_total+=count
        # Standard255 mm bond,7courses; only visible modeled skins, not buried masonry.
        for side in [-1,1]:
            d0,d1=(.125,.143) if side==1 else (-.145,-.125)
            visible_base=(lambda s:-.45) if side==1 else seg.base
            skin=seg.xystrip(max(abs(d0),abs(d1))).difference(seg.xystrip(min(abs(d0),abs(d1))))
            pp=[p for p in getattr(skin,'geoms',[skin]) if seg.local([p.centroid.x,p.centroid.y])[1]*side>0]
            for p in pp:mortar.append(part(strip_solid(seg,p,lambda s,d:visible_base(s)+.45,lambda s,d:visible_base(s)),'M_V10_Joint_Mortar'))
            for row in range(7):
                off=.1275 if row%2 else 0
                for x0 in np.arange(-off,seg.L,.255):
                    s0=max(.004,float(x0+.005));s1=min(seg.L-.004,float(x0+.250))
                    if s1-s0<.025:continue
                    g=ringgeom(box(s0,d0,s1,d1),0,.053)
                    g=mapped(g,lambda s,d,z:seg.xyz(s,d,visible_base(s)+row*.065+.005+z))
                    g=seg.crop(g,f'brick_{side}_{row}_{s0:.6f}')
                    bricks.append(part(g,'M_Grey_Brick'))
        # Long/short stepped plaster frames fit actual run, independent of reference3m bay.
        if seg.L>.9:
            bay_count=max(1,round((seg.L-.30)/2.45));bay=(seg.L-.30)/bay_count
            for b in range(bay_count):
                start=.15+b*bay;short=min(.48,bay*.22);long=bay-short-.20
                for s0,w in [(start,long),(start+long+.10,short)]:
                    for side in [-1,1]:frames += frame(seg,s0,w,side,.143 if side==1 else .125)
        layer_records.append(dict(chain=chain,segment=seg.j,crown_start_m=seg.za,crown_end_m=seg.zb,old_max_coping_delta_m=.170,new_top_delta_m=.357,new_top_minus_old_top_m=.187,tile_eave_projection_from_250mm_core_m=.080,flower_bottom_delta_m=.170,flower_top_delta_m=.315,cap_top_delta_m=.357,clay_pitch_m=.120,flower_module_length_m=.500,flower_hole_pitch_m=.125,brick_dimensions_nominal_m=[.245,.020,.053],brick_course_pitch_m=.065,plinth_height_m=.450))
    if chain=='SITE_GATE_EAST_FLANK':
        back,covers,pans,discs,flowers,cap,bricks,mortar,frames=[trim_kitchen(pp,n) for pp,n in zip([back,covers,pans,discs,flowers,cap,bricks,mortar,frames],['back','covers','pans','discs','flowers','cap','bricks','mortar','frames'])]
    put(chain+'_TILE_COPING',back,'MITERED_CLOSED_TILE_BEDDING_SHELL',masonry_core_unchanged=False,roof_rise_nominal_m=.130,tile_projection_m=.080,ornament_end_x_if_kitchen= east_finish_stop_x if chain=='SITE_GATE_EAST_FLANK' else None)
    put(chain+'_V10_COVER_TILES',covers,'INDIVIDUAL_CLOSED_CLAY_BARREL_TILE_COVERS',tile_pitch_m=.120,cover_diameter_m=.086)
    put(chain+'_V10_PAN_TILES',pans,'INDIVIDUAL_CLOSED_CLAY_PAN_TILES',tile_pitch_m=.120,pan_width_m=.087)
    put(chain+'_V10_LOTUS_DRIP_ENDS',discs,'MOLDED_EIGHT_PETAL_DRIP_TILE_END_RELIEF',nominal_diameter_m=.106,raised_petal_relief_m=.0035)
    put(chain+'_V10_OPEN_FLOWER_BRICKS',flowers,'TRUE_PIERCED_CLOVER_FLOWER_CLAY_RIDGE',true_through_holes=True,flower_module_nominal_m=.5,openwork_height_m=.145,through_depth_m=.068)
    put(chain+'_V10_RIDGE_SEAT_AND_CAP',cap,'MITERED_FLOWER_RIDGE_SEAT_AND_CAP',new_top_above_existing_masonry_crown_m=.357,cap_height_estimate=True)
    put(chain+'_V10_PLINTH_MORTAR_BACKING',mortar,'VISIBLE_PLINTH_JOINT_BACKING',buried_foundation=False)
    put(chain+'_V10_STAGGERED_GRAY_PLINTH_BRICKS',bricks,'INDIVIDUAL_VISIBLE_GRAY_BRICK_PLINTH_FINISH_UNITS',bond='HALF_BRICK_RUNNING_BOND',course_pitch_m=.065,plinth_height_m=.450,original_masonry_core_preserved=False)
    if chain=='SITE_COURTYARD_WEST_TILE_WALL':
        # Retain the10previous named panel elements; now combine matched stepped faceframes.
        for j in range(10):put('SITE_WEST_TILE_WALL_PANEL_'+str(j),frames[4*j:4*j+4],'STEPPED_LONG_SHORT_PLASTER_FRAME_PAIR',panel_face='WEST_AND_COURTYARD_EAST',original_rectangles_replaced=True)
        if len(frames)>40:put(chain+'_V10_CORNER_RETURN_STEPPED_FRAMES',frames[40:],'STEPPED_FRAME_COURTYARD_CORNER_RETURN')
        put('SITE_COURTYARD_WEST_WHITE_INSIDE',[p for seg in segs for p in white_finish(seg)],'WHITE_INNER_FACE_WITH_450MM_PLINTH_AND_MITER_RETURN',finish_thickness_m=.018,finish_bottom_z_m=0.,courtyard_floor_z_m=-.45,masonry_crown_unchanged=False)
    else:
        if frames:put(chain+'_V10_STEPPED_PLASTER_FRAMES',frames,'STEPPED_LONG_SHORT_PLASTER_FRAME_PAIR')
        put(chain+'_V10_WHITE_INSIDE',trim_kitchen([p for seg in segs for p in white_finish(seg)],'white_finish'),'WHITE_COURTYARD_FACE_ABOVE_VISIBLE_GRAY_PLINTH',finish_thickness_m=.018,finish_bottom_z_m=0.,courtyard_floor_z_m=-.45,masonry_core_unchanged=False,decorative_finish_ends_at_kitchen_gable_x=east_finish_stop_x)

# The oblique west wall ends on the left stone gate post, while its roof
# overhang reaches a little beyond the centerline endpoint. Abut the new
# finishes to the unchanged post; retain the V9 wall core exactly.
gate_obstacle=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in E['SITE_INNER_STONE_GATEHOUSE']['parts']],mf.OpType.Add)
for e in R+A:
    if not (e['name'].startswith('SITE_COURTYARD_WEST') or e['name'].startswith('SITE_WEST_TILE_WALL_PANEL')):continue
    keep=[]
    for i,p in enumerate(e['parts']):
        v=np.asarray(p['geometry']['vertices'])
        if v[:,0].max()<4.9-1e-8 or v[:,1].max()<-11.95 or v[:,1].min()>-11.45 or v[:,2].max()<-.45:
            keep.append(p);continue
        a=manifold(p['geometry']);iv=(a^gate_obstacle).volume()
        if iv>1e-12:
            cut=a-gate_obstacle
            clipped_parts.append(dict(chain='SITE_COURTYARD_WEST_TILE_WALL',part=e['name']+f'_{i}',gatepost_trim_volume_m3=iv,deleted=cut.is_empty()))
            if not cut.is_empty():keep.append(part(fromman(cut),p['material']))
        else:keep.append(p)
    e['parts']=keep

changes=[dict(id='V11_COURTYARD_RIGHT_ANGLE',description='用户115821俯视截图确认院墙直角。将旧[0,-10.7]斜接[4.9,-11.7]改为[0,-11.7]水平接门柱，墙芯/白内面/错缝砖饰/回纹框/双面瓦/真实花孔/压顶在45度角平分面收口。转角250mm冠高平段防止瓦帽错层，孔离转角至少120mm；主楼端与门柱端、门洞、厨房及外周墙保持。',source=REFS,dimension_status='USER_CONFIRMED_PLAN_RELATION; LOCAL_DIMENSIONS_FITTED_NOT_FIELD_SURVEY',wall_core_exactly_preserved=False,unchanged_gate_opening_local_m=[5.3,7.9],reference_iron_gate_not_generated=True,buried_foundation_not_generated=True)]
mutation=dict(replace=R,add=A,remove=[],definitions={},materials={},changes=changes,source_scene_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),old_node_sha256={e['name']:hashlib.sha256(json.dumps(BASE_E[e['name']],sort_keys=True,separators=(',',':')).encode()).hexdigest() for e in R},wall_core_hashes_before=core_hashes,layer_dimensions=layer_records,hole_probes=hole_probes,kitchen_gable_ornament_stop_x=east_finish_stop_x,kitchen_solids_preserved=True,gatepost_solids_preserved=True,new_west_terminal_details_trimmed_to_actual_gatepost=True,old_route_local_m=OLD_ROUTE,new_route_local_m=NEW_ROUTE,wall_changed_only_inside_explicit_user_correction_scope=True)

def verify():
    for e in R+A:
        for i,p in enumerate(e['parts']):
            g=p['geometry'];v,fs,_,_=ex.solid_data(g)
            check(e['name']+f'_{i}_finite',np.isfinite(v).all())
            edges=Counter(tuple(sorted((a,b))) for f in fs for a,b in zip(f,f[1:]+f[:1]))
            directed=Counter((a,b) for f in fs for a,b in zip(f,f[1:]+f[:1]))
            check(e['name']+f'_{i}_closed',all(n==2 for n in edges.values()) and all(n==directed[(b,a)] for (a,b),n in directed.items()))
            t=triangles(v,fs);vol=float(np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6)
            check(e['name']+f'_{i}_positive_volume',vol>1e-12,volume_m3=vol)
            check(e['name']+f'_{i}_no_zero_area_faces',np.all(np.linalg.norm(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]),axis=1)>1e-12))
    check('only_user_confirmed_west_wall_core_mutated',{n for n,_ in CHAINS}.intersection({e['name'] for e in R+A})=={CHAIN})
    check('right_angle_corner',abs(float((seeds[0].u)@(seeds[1].u)))<1e-12)
    check('untouched_east_flank_and_detail_nodes',not any(e['name'].startswith('SITE_GATE_EAST') for e in R+A))
    check('same_true_routes',all(np.allclose(allseg[n][0].a,np.array(pts[0])) and np.allclose(allseg[n][-1].b,np.array(pts[-1])) for n,pts in CHAINS))
    check('open_gate_preserved',not any(5.3<q[0]<7.9 and -11.85<q[1]<-11.55 for e in R+A for p in e['parts'] for q in p['geometry']['vertices']))
    check('flower_holes_actually_built',holes_total>0 and len(hole_probes)>0,hole_count=holes_total)
    check('no_reference_metal_gate_added',not any('METAL_ENTRY' in e['name'] for e in A))
    check('wall_main_building_terminus_not_extended',max(q[1] for e in R+A if 'COURTYARD_WEST' in e['name'] for p in e['parts'] for q in p['geometry']['vertices'])<=1.9+1e-8)
    qa=dict(status='PASS',checks_count=len(checks),checks=checks,elements=[dict(name=e['name'],parts=len(e['parts'])) for e in R+A],total_parts=sum(len(e['parts']) for e in R+A),reference_dimensions_status='DETAILS_ESTIMATED_FROM_IMAGE_AND_PHOTO; NOT_FIELD_MEASURED',wall_core_hashes_before=core_hashes,actual_open_holes=holes_total,hole_probes=hole_probes,exact_miter_clipped_parts=clipped_parts,layer_dimensions=layer_records,source_scene_sha256=mutation['source_scene_sha256'],kitchen_gable_ornament_stop_x=east_finish_stop_x)
    (OUT/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(status='PASS',replace=len(R),add=len(A),parts=qa['total_parts'],holes=holes_total,checks=len(checks),clipped_parts=len(clipped_parts)),ensure_ascii=False))

if __name__=='__main__':
    verify()
    (OUT/'Mutation.json').write_text(json.dumps(mutation,ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'All_Actual_Hole_Probes.json').write_text(json.dumps(dict(status='PASS',mutation_sha256=hashlib.sha256((OUT/'Mutation.json').read_bytes()).hexdigest(),count=len(all_holes),all_holes=all_holes),ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'Parameters.md').write_text('''# V11院墙直角连接

中心线 [0,1.9]→[0,-11.7]→[4.9,-11.7]，转角90度，250mm墙芯和18mm白内面在45度角平分面连续闭合。接主楼端/左门柱端原坐标和已登记高度保持，门洞X5.3~7.9不变。

转角瓦帽、双面筒瓦/板瓦、莲瓣滴水瓦当、花砖和压顶依墙线重新裁切；角点两侧250mm冠高平段使共享角平分面高程一致，孔距转角至少120mm。所有参考尺寸仍为图示拟合，没有宣称实测施工尺寸。原外周墙、东门侧、厨房/门楼/照壁与不涉及本拐角的对象原样保留。

亭全边界需在X>.22、Y>-11.48的院内，亭代理按150mm间距及完整顶点核查。
''',encoding='utf8')
