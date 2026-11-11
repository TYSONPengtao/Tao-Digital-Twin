"""Isolated perimeter finish detail. Original retaining body and route are read-only."""
import sys, json, math, copy, hashlib
from pathlib import Path
from collections import defaultdict, Counter
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
import mapbox_earcut as ear
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient as pgorient

OUT=Path(__file__).parent
SRC=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
S=json.loads(SRC.read_text(encoding='utf8')); E={e['name']:e for e in S['elements']}
R=[]; A=[]; CHECKS=[]; PROBES=[]; ALL_HOLES=[]; REMOVED_CORNER_HOLES=[]; records=[]
REF='C:/Users/PENG/AppData/Local/Temp/codex-clipboard-9c94e772-aef6-49e7-8ca8-408562170f8a.png'
REFS=[REF,'D:/DJI/0002/DCIM/101MEDIA/DJI_0073.JPG','D:/DJI/0002/DCIM/101MEDIA/DJI_0161.JPG','E:/jz/JIA/JIA.ccm','V9 original retaining-wall body mesh vertices and crest levels']

def check(name,ok,**kw):
    CHECKS.append(dict(name=name,pass_=bool(ok),**kw))
    if not ok:raise AssertionError(name+' '+str(kw))

def part(g,m='M_Roof'):return dict(geometry=g,material=m)
def put(name,parts,cls,**props):
    e=copy.deepcopy(E.get(name,dict(name=name,layer='60_SITE',family='SITE_MODEL',confidence='MEDIUM')))
    e.update(parts=parts,source='; '.join(REFS),classification=cls,status='V10_REFERENCE_STYLE_DETAIL; NOMINAL_FINISH_SIZES_NOT_FIELD_MEASURED',**props)
    (R if name in E else A).append(e)
    return e

def triring(rings):
    pp=np.array([p for ring in rings for p in ring],float)
    ends=np.cumsum([len(q) for q in rings]).astype(np.uint32)
    tt=ear.triangulate_float64(pp,ends).reshape(-1,3).tolist()
    # Earcut removes collinear route stations. Reinsert every omitted boundary vertex,
    # otherwise vertical side walls have T junctions against their triangulated caps.
    used={i for t in tt for i in t}
    for k in range(len(pp)):
        if k in used:continue
        found=False
        for ti,t in enumerate(tt):
            for j in range(3):
                a=t[j];b=t[(j+1)%3];c=t[(j+2)%3]
                ab=pp[b]-pp[a];ak=pp[k]-pp[a];length2=float(np.dot(ab,ab))
                if length2<1e-20:continue
                alpha=float(np.dot(ak,ab)/length2)
                if 1e-10<alpha<1-1e-10 and abs(float(ab[0]*ak[1]-ab[1]*ak[0]))<1e-11:
                    tt[ti]=[a,k,c];tt.append([k,b,c]);found=True;break
            if found:break
        if not found:raise ValueError('Unused triangulation boundary vertex '+str(k))
        used.add(k)
    return pp,tt

def final_geometry(vertices,faces):
    v=np.asarray(vertices,float); ff=[]
    for f in faces:
        if len(f)==3:ff.append(f)
        elif len(f)==4:ff += [[f[0],f[1],f[2]],[f[0],f[2],f[3]]]
        else:
            q=v[f]; normal=np.sum(np.cross(q,np.roll(q,-1,axis=0)),axis=0)
            drop=int(np.argmax(abs(normal))); p=np.delete(q,drop,axis=1)
            _,tt=triring([p.tolist()]);ff += [[f[k] for k in t] for t in tt]
    ed=defaultdict(list)
    for i,f in enumerate(ff):
        for a,b in zip(f,f[1:]+f[:1]):ed[tuple(sorted((a,b)))].append((i,a,b))
    if any(len(q)!=2 for q in ed.values()):raise ValueError('Nonclosed '+str(Counter(map(len,ed.values()))))
    adj=[[] for _ in ff]
    for q in ed.values():
        (i,a,b),(j,c,d)=q;adj[i].append((j,a==c and b==d));adj[j].append((i,a==c and b==d))
    state={};components=0
    for root in range(len(ff)):
        if root in state:continue
        components+=1;state[root]=False; stack=[root]
        while stack:
            i=stack.pop()
            for j,same in adj[i]:
                flip=state[i]^same
                if j in state:
                    if state[j]!=flip:raise ValueError('Nonorientable')
                else:state[j]=flip;stack.append(j)
    ff=[f[::-1] if state[i] else f for i,f in enumerate(ff)]
    # Center before volume calculation; geographical/local position cannot dominate tiny tile volumes.
    vv=v-v.mean(axis=0)
    vol=sum(float(np.dot(vv[f[0]],np.cross(vv[f[1]],vv[f[2]])))/6 for f in ff)
    if vol<0:ff=[f[::-1] for f in ff];vol=-vol
    ar=np.linalg.norm(np.cross(v[np.array(ff)[:,1]]-v[np.array(ff)[:,0]],v[np.array(ff)[:,2]]-v[np.array(ff)[:,0]]),axis=1)
    if not(np.isfinite(v).all() and vol>1e-12 and ar.min()>1e-13 and components==1):raise ValueError('Degenerate geometry '+str((vol,ar.min(),components)))
    return dict(type='polyhedron',vertices=v.tolist(),faces=ff),dict(volume_m3=vol,min_double_triangle_area=float(ar.min()),faces=len(ff),vertices=len(v),components=components)

class PathWall:
    def __init__(self,name):
        self.name=name;self.body=E[name]
        whites=[p['geometry'] for p in self.body['parts'] if p['material']=='M_Wall_Exterior']
        self.P=[];self.O=[];self.Z=[];self.H=[]
        for i,g in enumerate(whites):
            v=np.array(g['vertices'],float)
            pa=(v[4]+v[7])/2;pb=(v[5]+v[6])/2
            if not i:self.P.append(pa[:2]);self.O.append((v[7,:2]-v[4,:2])/2);self.Z.append(pa[2]);self.H.append(pa[2]-(v[0,2]+v[3,2])/2)
            self.P.append(pb[:2]);self.O.append((v[6,:2]-v[5,:2])/2);self.Z.append(pb[2]);self.H.append(pb[2]-(v[1,2]+v[2,2])/2)
        self.P=np.array(self.P);self.O=np.array(self.O);self.Z=np.array(self.Z);self.H=np.array(self.H)
        self.original_body_offsets=self.O.copy()
        self.L=np.r_[0,np.cumsum(np.linalg.norm(np.diff(self.P,axis=0),axis=1))]
        # The two inherited open chains meet at NW, although source end offsets were
        # independently squared off. Join all NEW finish layers with one true miter.
        # Neither the original wall body nor its separate64mm crown step is changed.
        if name.endswith('_0'):
            other=E['SITE_PERIMETER_JOINED_RETAINING_WALL_1']['parts'][-1]['geometry']['vertices']
            ov=np.array(other,float);up=(ov[5,:2]+ov[6,:2]-ov[4,:2]-ov[7,:2])/2
            up/=np.linalg.norm(up);un=(self.P[1]-self.P[0]);un/=np.linalg.norm(un)
            n0=np.array([-up[1],up[0]]);n1=np.array([-un[1],un[0]])
            self.O[0]=(n0+n1)*(.16/np.dot(n0+n1,n1));self.shared_joint_s=0.0
        else:
            other=E['SITE_PERIMETER_JOINED_RETAINING_WALL_0']['parts'][1]['geometry']['vertices']
            ov=np.array(other,float);un=(ov[5,:2]+ov[6,:2]-ov[4,:2]-ov[7,:2])/2
            un/=np.linalg.norm(un);up=(self.P[-1]-self.P[-2]);up/=np.linalg.norm(up)
            n0=np.array([-up[1],up[0]]);n1=np.array([-un[1],un[0]])
            self.O[-1]=(n0+n1)*(.16/np.dot(n0+n1,n1));self.shared_joint_s=float(self.L[-1])
        # Match actual existing coping polygons, rather than reconstructing an approximate south skip rectangle.
        cps=E[name+'_TILE_COPING']['parts']; self.allowed=[];self.skip=[]
        for i in range(len(whites)):
            ca=(self.P[i]+self.P[i+1])/2
            found=False
            for p in cps:
                v=np.array(p['geometry']['vertices']);cb=(v[0,:2]+v[1,:2]+v[3,:2]+v[4,:2])/4
                if np.linalg.norm(ca-cb)<1e-7:found=True;break
            (self.allowed if found else self.skip).append(i)
        self.allowed_ranges=[(self.L[i],self.L[i+1]) for i in self.allowed]
        ds=np.diff(self.P,axis=0);ds/=np.linalg.norm(ds,axis=1)[:,None]
        self.sharp_corner_s=[float(self.L[i]) for i in range(1,len(self.L)-1) if math.acos(float(np.clip(np.dot(ds[i-1],ds[i]),-1,1)))>math.radians(12)]
        self.no_hole_joint_s=sorted(set(self.sharp_corner_s+[self.shared_joint_s]+[float(self.L[i]) for i in self.allowed if i==0 or i-1 not in self.allowed]+[float(self.L[i+1]) for i in self.allowed if i==len(self.L)-2 or i+1 not in self.allowed]))
    def ix(self,s):return int(np.clip(np.searchsorted(self.L,s,side='right')-1,0,len(self.L)-2))
    def sample(self,s):
        i=self.ix(s);a=(s-self.L[i])/(self.L[i+1]-self.L[i]);a=float(np.clip(a,0,1))
        return (1-a)*self.P[i]+a*self.P[i+1],(1-a)*self.O[i]+a*self.O[i+1],(1-a)*self.Z[i]+a*self.Z[i+1],(1-a)*self.H[i]+a*self.H[i+1]
    def mp(self,s,v,z):
        p,o,t,h=self.sample(s)
        return [*(p+o*(v/.16)),t+z]
    def permitted(self,a,b):
        return all(self.ix(x) in self.allowed for x in [a+1e-7,b-1e-7,(a+b)/2])
    def dense(self,ring):
        # Include every route breakpoint along horizontal edges so miters stay exact through corners.
        out=[]
        for p,q in zip(ring,ring[1:]+ring[:1]):
            out.append(p)
            if abs(p[1]-q[1])<1e-9 and abs(p[0]-q[0])>1e-7:
                a,b=sorted([p[0],q[0]]);xs=list(np.arange(a+.2,b,.2))+[x for x in self.L if a+1e-7<x<b-1e-7]
                xs=sorted(set(round(float(x),10) for x in xs),reverse=p[0]>q[0]);out.extend([[x,p[1]] for x in xs])
        return out
    def plate(self,poly,v0,v1):
        poly=pgorient(poly,1);rings=[self.dense(list(poly.exterior.coords)[:-1])]+[self.dense(list(h.coords)[:-1]) for h in poly.interiors]
        pp,tt=triring(rings);n=len(pp);vs=[self.mp(s,v,z) for v in [v0,v1] for s,z in pp];ff=[]
        ff += [t for t in tt]+[[x+n for x in t[::-1]] for t in tt]
        k=0
        for ring in rings:
            for j in range(len(ring)):
                a=k+j;b=k+(j+1)%len(ring);ff.append([a,b,b+n,a+n])
            k+=len(ring)
        return final_geometry(vs,ff)[0]
    def band(self,a,b,vhalf,z0,z1):
        return self.plate(Polygon([[a,z0],[b,z0],[b,z1],[a,z1]]),-vhalf,vhalf)

def roofbed(w,i):
    a=w.L[i];b=w.L[i+1];vs=[w.mp(s,v,z) for s in [a,b] for v,z in [(-.2,0),(.2,0),(0,.115)]]
    fs=[[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]]
    return final_geometry(vs,fs)[0]

def cover(w,s,side):
    # One watertight visible unit: semi-annular barrel plus joined round lotus/drip tile head.
    r=.038;ri=.029; rd=.053; vb=.048; ve=.197; vf=.214
    ang=np.linspace(0,math.pi,13);prof=[[r*math.cos(t),.004+r*math.sin(t)] for t in ang]+[[ri*math.cos(t),.004+ri*math.sin(t)] for t in ang[::-1]]
    pts=[];faces=[];ids={}
    def vi(u,v,h):
        key=tuple(round(q,12) for q in [u,v,h])
        if key not in ids:ids[key]=len(pts);pts.append(w.mp(s+u,side*v,.115*(1-v/.2)+h))
        return ids[key]
    aa=[vi(u,vb,h) for u,h in prof];bb=[vi(u,ve,h) for u,h in prof]
    _,tt=triring([prof]);faces += [[aa[k] for k in t] for t in tt]
    for j in range(len(prof)):k=(j+1)%len(prof);faces.append([aa[j],bb[j],bb[k],aa[k]])
    circ=[[rd*math.cos(t),.004+rd*math.sin(t)] for t in np.linspace(0,2*math.pi,32,endpoint=False)]
    p,tt=triring([circ,prof[::-1]])
    ii=[vi(u,ve,h) for u,h in p];faces += [[ii[k] for k in t] for t in tt]
    rings=[]
    for rr,base,mod in [(rd,0,0),(.038,.0015,.0015),(.016,.006,.003)]:
        ring=[vi(rr*math.cos(t),vf+base+mod*math.cos(8*t),.004+rr*math.sin(t)) for t in np.linspace(0,2*math.pi,32,endpoint=False)]
        rings.append(ring)
    start=[vi(u,ve,h) for u,h in circ]
    for p0,p1 in zip([start]+rings[:-1],rings):
        for j in range(32):k=(j+1)%32;faces.append([p0[j],p1[j],p1[k],p0[k]])
    center=vi(0,vf+.007,.004)
    for j in range(32):faces.append([rings[-1][j],center,rings[-1][(j+1)%32]])
    return final_geometry(pts,faces)[0]

def pan(w,s,side,pitch):
    half=(pitch-2*.038)/2-.001
    xx=np.linspace(-half,half,7);upper=[[float(x),.005+.010*(x/half)**2] for x in xx];profile=upper+[[x,h-.004] for x,h in upper[::-1]]
    pp,tt=triring([profile]);vs=[w.mp(s+u,side*v,.115*(1-v/.2)+h) for v in [.045,.209] for u,h in pp]
    n=len(pp);fs=[t for t in tt]+[[k+n for k in t[::-1]] for t in tt]
    for j in range(n):k=(j+1)%n;fs.append([j,k,k+n,j+n])
    return final_geometry(vs,fs)[0]

def flowerband(w,a,b):
    length=b-a;n=max(1,int(length/.123));step=length/n;holes=[]
    for j in range(n):
        sc=a+(j+.5)*step;zc=.245;rad=min(.035,step*.31)
        if any(abs(sc-corner)<.20 for corner in w.no_hole_joint_s):
            REMOVED_CORNER_HOLES.append(dict(element=w.name+'_PROVISIONAL_FLOWER_CROWN',route_s=sc,point_local_m=w.mp(sc,0,zc),reason='Solid200mm corner/terminal collar; physically remove hole instead of keeping an occluded motif'))
            continue
        hole=[[sc+rad*(1+.23*math.cos(4*t))*math.cos(t),zc+rad*(1+.23*math.cos(4*t))*math.sin(t)] for t in np.linspace(0,2*math.pi,32,endpoint=False)]
        holes.append(hole)
        p,o,z,h=w.sample(sc); normal=o/np.linalg.norm(o)
        probe=dict(element=w.name+'_PROVISIONAL_FLOWER_CROWN',center_local_m=[*p,z+zc],normal_local=[*normal,0],hole_radius_min_m=rad*.77,hole_width_max_m=2*rad*1.23,hole_height_max_m=2*rad*1.23,normal_depth_m=.08,route_s=sc,nearest_joint_distance_m=min(abs(sc-corner) for corner in w.no_hole_joint_s))
        ALL_HOLES.append(probe)
        if not PROBES or (w.name.endswith('_1') and len(PROBES)==1):PROBES.append(probe)
    p=Polygon([[a,.19],[b,.19],[b,.30],[a,.30]],holes)
    return w.plate(p,-.04,.04),len(holes)

def frames(w):
    pieces=[];positions=[]
    # Stop every decorative bay at real angular corner (>12deg); gentle curved wall can receive curved relief.
    ds=np.diff(w.P,axis=0);ds/=np.linalg.norm(ds,axis=1)[:,None]
    corners=[w.L[i] for i in range(1,len(w.L)-1) if math.acos(float(np.clip(np.dot(ds[i-1],ds[i]),-1,1)))>math.radians(12)]
    # Preserve the special screenwall region; its older frame/roof has a separate protected node.
    cuts=sorted(set([0,float(w.L[-1])]+corners+[float(w.L[i]) for j in w.skip for i in [j,j+1]]))
    for a,b in zip(cuts,cuts[1:]):
        if not w.permitted(a,b) or b-a<.50:continue
        count=max(1,int(round((b-a)/3)));module=(b-a)/count
        for j in range(count):
            lo=a+j*module+.055;hi=a+(j+1)*module-.055
            if abs(lo-w.shared_joint_s)<.23:lo=w.shared_joint_s+.23
            if abs(hi-w.shared_joint_s)<.23:hi=w.shared_joint_s-.23
            spans=[(lo,hi)] if hi-lo<1.2 else [(lo,hi-.45),(hi-.34,hi)]
            for s0,s1 in spans:
                if s1-s0<.20:continue
                samples=[w.sample(float(x))[3] for x in np.r_[np.linspace(s0,s1,13),w.L[(w.L>=s0)&(w.L<=s1)]]]
                H=min(.29,min(samples)-.15)
                if H<.12:continue
                z1=-.095;z0=z1-H; st=min(.032,H*.2,(s1-s0)*.08)
                outer=Polygon([[s0,z0+st],[s0+st,z0+st],[s0+st,z0],[s1-st,z0],[s1-st,z0+st],[s1,z0+st],[s1,z1-st],[s1-st,z1-st],[s1-st,z1],[s0+st,z1],[s0+st,z1-st],[s0,z1-st]])
                for offset,width,depth in [(0,.017,.016),(.025,.010,.011)]:
                    p=outer.buffer(-offset,join_style=2);q=p.buffer(-width,join_style=2);ring=p.difference(q)
                    if ring.is_empty:continue
                    for side in [-1,1]:
                        # Body surface normal is the exact original miter offset, not a straight proxy chord.
                        finish_offsets=w.O;w.O=w.original_body_offsets
                        g=w.plate(ring,side*.160,side*(.160+depth));w.O=finish_offsets
                        pieces.append(part(g,'M_Stone_Frame'))
                positions.append(dict(route_s0=s0,route_s1=s1,height=H,top_below_original_crest=.095))
    return pieces,positions

for name in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
    w=PathWall(name);cap_parts=[];crown_parts=[];tile_count=0;holes=0
    # Original 117 + 22 body segments remain byte-identical in Scene; patch does not replace body node.
    for i in w.allowed:
        cap_parts.append(part(roofbed(w,i)))
        cap_parts.append(part(w.band(float(w.L[i]),float(w.L[i+1]),.04,.115,.17)))
    length=float(w.L[-1]);n=max(1,int(round(length/.12)));pitch=length/n
    for j in range(n):
        s=(j+.5)*pitch
        if w.permitted(s-.053,s+.053):
            for side in [-1,1]:cap_parts.append(part(cover(w,s,side)))
            tile_count+=2
        if j<n-1:
            sp=(j+1)*pitch
            if w.permitted(sp-(pitch-2*.038)/2,sp+(pitch-2*.038)/2):
                for side in [-1,1]:cap_parts.append(part(pan(w,sp,side,pitch)))
                tile_count+=2
    for i in w.allowed:
        a=float(w.L[i]);b=float(w.L[i+1]);steps=max(1,int(math.ceil((b-a)/.5)))
        crown_parts.append(part(w.band(a,b,.043,.17,.19)))
        for j in range(steps):
            x=a+(b-a)*j/steps;y=a+(b-a)*(j+1)/steps;g,h=flowerband(w,x,y);crown_parts.append(part(g));holes+=h
        crown_parts.append(part(w.band(a,b,.065,.30,.328)))
    panel_parts,pos=frames(w)
    put(name+'_TILE_COPING',cap_parts,'V10_ORIGINAL_CREST_DOUBLE_SLOPE_INDIVIDUAL_TILES',nominal_pitch_m=.12,actual_pitch_m=pitch,original_body_preserved=True,ridge_height_above_crest_m=.17,circular_tile_head_diameter_m=.106,finish_sizes='REFERENCE_STYLE_AND_OBSERVED_LOW_COPING; unmeasured')
    put(name+'_PROVISIONAL_FLOWER_CROWN',crown_parts,'REFERENCE_STYLE_ONLY_LOW_PIERCED_CROWN',nominal_height_m=.158,source_crest_addition_m=.328,relative_old_coping_ridge_addition_m=.158,negative_spaces='Real through holes in closed carved flower-brick solids; not opaque planes',hidden_construction_omitted=True,style_status='User detail reference adapted to low perimeter cap; all-around crown not confirmed in current DJI perimeter photo')
    put(name+'_PLASTER_STEPPED_RELIEF',panel_parts,'TRADITIONAL_LONG_SHORT_STEPPED_PLASTER_PANELS',reference_only_sizes=True,frame_positions=pos,original_stone_retaining_base_unmodified=True)
    miter=w.O[0 if name.endswith('_0') else -1]
    rec=dict(name=name,original_body_sha256=hashlib.sha256(json.dumps(E[name],sort_keys=True,ensure_ascii=False).encode()).hexdigest(),original_body_parts=len(E[name]['parts']),centerline_points=w.P.tolist(),route_length_m=length,original_crest_z=w.Z.tolist(),allowed_segment_indices=w.allowed,screenwall_skip_segment_indices=w.skip,opening_endpoints_local=[w.P[0].tolist(),w.P[-1].tolist()],tile_pitch_m=pitch,individual_visible_tile_parts=tile_count,coping_parts=len(cap_parts),provisional_crown_parts=len(crown_parts),pierced_flower_holes=holes,relief_parts=len(panel_parts),relief_panels=len(pos),old_coping_ridge_crest_delta_m=.17,new_coping_ridge_crest_delta_m=.17,reference_crown_top_crest_delta_m=.328,reference_crown_top_old_ridge_delta_m=.158,shared_nw_true_miter_halfwidth_offset_xy=miter.tolist(),shared_nw_joint_s=w.shared_joint_s,flower_no_hole_joint_s=w.no_hole_joint_s,flower_no_hole_keepback_m=.20)
    records.append(rec)
    check(name+'_body_not_replaced',name not in {e['name'] for e in R+A})
    check(name+'_skip_match',len(w.allowed)==len(E[name+'_TILE_COPING']['parts']))
    check(name+'_no_crossing_gap',all(w.permitted((j+.5)*pitch-.053,(j+.5)*pitch+.053) for j in range(n) if w.permitted((j+.5)*pitch-.053,(j+.5)*pitch+.053)))

geom_records=[];total=0
for e in R+A:
    vols=[];mins=[]
    for p in e['parts']:
        g,q=final_geometry(p['geometry']['vertices'],p['geometry']['faces']);p['geometry']=g;vols.append(q['volume_m3']);mins.append(q['min_double_triangle_area']);total+=1
    geom_records.append(dict(name=e['name'],parts=len(e['parts']),all_closed_manifold=True,all_finite=True,minimum_positive_volume_m3=min(vols),minimum_double_triangle_area_m2=min(mins),classification=e['classification']))
    check(e['name']+'_closed_finite_nonzero',len(vols)>0)
check('south_screenwall_original_9_skipped_segments',len(records[0]['screenwall_skip_segment_indices'])==9)
check('southwest_openchain_gap_not_changed',abs(np.linalg.norm(np.array(records[0]['opening_endpoints_local'][-1])-np.array(records[1]['opening_endpoints_local'][0]))-5.168882)<.00001)
check('retaining_base_materials_not_replaced',not any(e['name']==r['name'] for r in records for e in R+A))
check('true_flower_through_hole_probes_available',len(PROBES)>=2)

changes=dict(version='V10',scope='Two surveyed perimeter retaining-wall finish nodes only; no body, plan line, opening, building or terrain source edits',original_scene_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),reference_image=REF,reference_dimensions_m=dict(overall_height=2.7,wall_thickness=.24,tile_pitch=.12,reference_status='MODEL_REFERENCE_ONLY'),actual_body_width_m=.32,route_length_m=sum(r['route_length_m'] for r in records),coping_old_crest_preserved=True,ornamental_crown_actual_photo_status='Low separate provisional style layer; source DJI perimeter shows lower simple coping. Original retainers kept exactly.',provisional_crown_top_above_old_ridge_m=.158,protected_elements=['SITE_SOUTH_SCREENWALL_*','SITE_INNER_GATEHOUSE_*','SITE_GATEHOUSE_*','SITE_KITCHEN_*','SITE_COURTYARD_*'],brick_plinth_replacement_omitted='Perimeter actual stone retaining base preserved; reference450mmbrickplinth not imposed',ground_crest_follow='All139 segment centerline and crown elevations directly reused; miter coordinates interpolated exactly',new_gate_omitted='Original southwest5.16888mopenchain remains; no reference iron gate inserted',walls=records,negative_space_probes=PROBES,new_part_count=total,style_dimensions_unmeasured=True)
changes.update(all_true_flower_hole_probes=ALL_HOLES,physically_removed_corner_terminal_holes=REMOVED_CORNER_HOLES,shared_nw_new_finish_miter=dict(point_xy_local=records[0]['centerline_points'][0],offset_xy_halfwidth_m=records[0]['shared_nw_true_miter_halfwidth_offset_xy'],original_wall0_crest_z=records[0]['original_crest_z'][0],original_wall1_crest_z=records[1]['original_crest_z'][-1],original_crest_step_m=records[0]['original_crest_z'][0]-records[1]['original_crest_z'][-1],body_or_crest_modified=False,finish='Closed mitered stepped end faces and200mm no-hole solid endcollars; no masking of retained occluded flower holes'))
mutation=dict(replace=R,add=A,remove=[],definitions={},materials={},changes=changes)
(OUT/'Mutation.json').write_text(json.dumps(mutation,ensure_ascii=False,indent=2),encoding='utf8')
qa=dict(status='PASS',checks=CHECKS,elements=geom_records,parts_total=total,original_scene_sha256=changes['original_scene_sha256'],mutation_sha256=hashlib.sha256((OUT/'Mutation.json').read_bytes()).hexdigest(),negative_space_probes=PROBES,wall_records=records,limitations=['No independent field dimensions beyond inherited actual model route and crest; new flower crown is user reference style adapted, unconfirmed all around source perimeter','Mesh topology and volume verified; compound solids not certified structural construction details','Intended tile/fascia/crown contacts use shared boundary planes; no hidden footing/rebar modeled'])
(OUT/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'All_Actual_Hole_Probes.json').write_text(json.dumps({'mutation_sha256':qa['mutation_sha256'],'all_holes':ALL_HOLES,'physically_removed_corner_terminal_holes':REMOVED_CORNER_HOLES},ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'Design_Notes.md').write_text('# V10 外周院墙细化\n\n保留V9外周挡墙所有石砌与白墙实体、中心线、139段标高和西南入口端点；原照壁飞檐处9段普通瓦帽仍留空。用独立筒瓦、板瓦和圆形莲瓣瓦当替换原简单双坡瓦帽，普通脊顶仍为原墙芯冠顶加170毫米。\n\n按新参考图新增长短回纹饰框。外周挡墙照片仅明确低瓦帽，因此低镂空花砖层独立命名为PROVISIONAL_FLOWER_CROWN，顶面比旧脊顶高158毫米；花孔为真实穿孔实体。青石挡墙不套用参考图450毫米青砖勒脚，2700毫米总高不覆盖随地形变化的既有高度。\n\n新细节尺寸是图像造型参考值，未作为实测施工尺寸。大门、照壁、厨房、室内、地形及原实景贴图不在本孤立补丁修改范围。\n',encoding='utf8')
print(json.dumps(dict(status='PASS',parts=total,replace=[e['name'] for e in R],add=[e['name'] for e in A],records=[{k:v for k,v in r.items() if k not in ['centerline_points','original_crest_z']} for r in records],mutation_sha256=qa['mutation_sha256']),ensure_ascii=False,indent=2))
