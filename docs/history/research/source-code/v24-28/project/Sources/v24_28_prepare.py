"""Apply the 15:14, 15:16 and 15:24 marked corrections to the V24.26 source.

The exterior is one level.  The courtyard has a real, continuous step from
the kitchen gallery edge to the right corner of the existing house step.
Building slabs are never used as terrain controls and are never deformed.
"""
import sys, json, shutil, hashlib
from pathlib import Path
W = Path(__file__).parent
sys.path[:0] = [str(W/'np1'), str(W/'geomlibs'), str(W/'libs'), str(W)]
import numpy as np
D = W/'v24_28'; D.mkdir(exist_ok=True)
prior = W/'v24_27'
for fn in ['Source.json', 'Before_Snapshot.json']:
    shutil.copy2(prior/fn, D/fn)
rows = json.loads((prior/'Inventory.json').read_text('utf8'))
for row in rows:
    if 'file' in row: row['file'] = str((prior/row['file']).resolve())
if (D/'Extra_Files.json').exists():
    extra={r['name']:r['file']for r in json.loads((D/'Extra_Files.json').read_text())}
    for row in rows:
        if row['name'] in extra:row['file']=extra[row['name']]
(D/'Inventory.json').write_text(json.dumps(rows, ensure_ascii=False), encoding='utf8')
import v24_16_common as base
base.D=D; base.INDEX={r['name']:r for r in rows}
base.OUT={'objects':[], 'raw_objects':[], 'remove':[], 'proof':{}}
from v24_16_common import *
from shapely.geometry import Polygon, box, LineString
INDEX=base.INDEX; OUT=base.OUT
def compose(ms):return mf.Manifold.compose(ms)
BRICK='M_V24_18_Continuous_Blue_Brick'
CLAY='M_V24_20_Unified_Weathered_Gray_Clay'
WHITE='M_V24_11_Plain_White_Limewash'

# Reuse the already checked, affine-only subdivision routine. The source
# coordinates and per-face UV interpolation are retained in the audit files.
oldcode=(W/'v24_27_grade.py').read_text('utf8')
start=oldcode.index('def refine('); end=oldcode.index('def clamp(')
exec(oldcode[start:end].replace('(hi[:,1]>-3.8)', '(hi[:,1]>-12.0)').replace('>-6.3','>-7.3'), globals())
def clamp(a): return min(1., max(0., a))
A=np.array([8.15,-.30]); B=np.array([8.15,-3.12])
U=(A-B)/np.linalg.norm(A-B); HIGH=np.array([U[1],-U[0]])
def side(x,y): return float((np.array([x,y])-B)@HIGH)
def progress(y): return clamp((y-B[1])/(A[1]-B[1]))
def low_level(y): return -.45+.30*progress(y)
def high_level(y): return -.40+.40*progress(y)

# A physically closed, 100mm stone edge continues the gallery's step crest
# to the existing house entry step. The two ends use those existing datums.
vs=[]
for pt,z in [(B,-.40),(A,0.)]:
    for xy,zz in [(pt,-.65),(pt+HIGH*.10,-.65),(pt+HIGH*.10,z),(pt,z)]:
        vs.append([*xy,zz])
fs=[[0,3,2],[0,2,1],[4,5,6],[4,6,7]]
for j in range(4):
    k=(j+1)%4;fs.extend([[j,k,k+4],[j,k+4,j+4]])
put('V24_28_Continuous_Kitchen_To_House_Step', solid(vs,fs), 'M_Stone', True)

def sampler(d):
    t=d['v'][d['f']]; n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]); t=t[n[:,2]>1e-11]
    aa=t[:,1,:2]-t[:,0,:2];bb=t[:,2,:2]-t[:,0,:2];dd=aa[:,0]*bb[:,1]-aa[:,1]*bb[:,0]
    def get(x,y):
        q=np.array([x,y])-t[:,0,:2]
        a=(q[:,0]*bb[:,1]-q[:,1]*bb[:,0])/dd;b=(aa[:,0]*q[:,1]-aa[:,1]*q[:,0])/dd
        good=(a>=-2e-5)&(b>=-2e-5)&(a+b<=1+2e-5)
        if good.any():return float((t[:,0,2]+a*(t[:,1,2]-t[:,0,2])+b*(t[:,2,2]-t[:,0,2]))[good].max())
        v=d['v'];ids=np.argsort(((v[:,:2]-[x,y])**2).sum(1))[:12]
        return float(v[ids,2].max())
    return get

def cut_at_step(v,f,mi,uv,parent):
    """Split only intersecting faces, with affine UVs on both level sides."""
    vv=v.tolist(); ff=[];mm=[];uu=[];pp=[];ss=[];edge={}
    dist=(v[:,:2]-B)@HIGH
    for ids,mat,tex,par in zip(f,mi,uv,parent):
        xy=v[ids,:2]
        intersects=(xy[:,0].max()>.125 and xy[:,0].min()<14.08 and
                    xy[:,1].max()>-3.6 and xy[:,1].min()<1.9)
        signs=dist[ids]
        if not intersects or signs.min()>=-1e-9 or signs.max()<=1e-9:
            ff.append(ids); mm.append(mat); uu.append(tex);pp.append(par)
            ss.append(int(signs.mean()>=0));continue
        for region in [0,1]:
            poly=[(int(i),np.array(t))for i,t in zip(ids,tex)];result=[]
            for (i,ti),(j,tj) in zip(poly,poly[1:]+poly[:1]):
                di=dist[i];dj=dist[j];ki=(di>=-1e-10)if region else(di<=1e-10)
                kj=(dj>=-1e-10)if region else(dj<=1e-10)
                if ki:result.append((i,ti))
                if ki!=kj and abs(di-dj)>1e-12:
                    t=di/(di-dj);key=tuple(sorted((i,j)))
                    if key not in edge:edge[key]=len(vv);vv.append((v[i]+t*(v[j]-v[i])).tolist())
                    result.append((edge[key],ti+t*(tj-ti)))
            for j in range(1,len(result)-1):
                part=[result[0],result[j],result[j+1]]
                if len(set(p[0]for p in part))<3:continue
                ff.append([p[0]for p in part]);mm.append(mat);uu.append([p[1]for p in part]);pp.append(par);ss.append(region)
    # The high and low copies of a seam vertex have separate Z values.
    mapping={};out=[];newf=[];src=[];region=[]
    for face,s in zip(ff,ss):
        nf=[]
        for i in face:
            key=(int(i),int(s))
            if key not in mapping:
                mapping[key]=len(out);out.append(vv[i]);src.append(i);region.append(s)
            nf.append(mapping[key])
        newf.append(nf)
    return np.array(out),np.array(newf),np.array(mm),np.array(uu),np.array(pp),np.array(region),np.array(src)

def split_at_height_break(v,f,mi,uv,parent):
    """Insert the exact cap station before grading, with affine source UVs."""
    global B,HIGH
    saved_b=B.copy();saved_high=HIGH.copy()
    ycap=saved_b[1]+(.388/.40)*(A[1]-saved_b[1])
    B=np.array([0.,ycap]);HIGH=np.array([0.,1.])
    vv,ff,mm,uu,pp,_,_=cut_at_step(v,f,mi,uv,parent)
    B=saved_b;HIGH=saved_high
    return vv,ff,mm,uu,pp

ground=['SITE_V16_GRADED_INTERIOR_SOIL_Geometry',
 'SITE_V12_REBUILT_COURT_-20_-20_0_Geometry','SITE_V12_REBUILT_COURT_-20_0_0_Geometry',
 'SITE_V12_REBUILT_COURT_0_-20_0_Geometry','SITE_V12_REBUILT_COURT_0_0_0_Geometry',
 'V24_24_House_Front_Matching_Stone_Paving']
records=[]
for name in ground:
    fn='GRADE_'+name+'.npz'
    if '--reuse-ground' in sys.argv and (D/fn).exists():
        a=np.load(D/fn);OUT['raw_objects'].append({'name':name,'file':fn,'materials':INDEX[name]['materials'],'smooth_top':False,'kind':'ground'})
        records.append({'object':name,'vertices':len(a['v']),'triangles':len(a['f']),'maximum_change_m':float(abs(a['v']-a['source_v']).max()),'xy_unchanged':bool(np.array_equal(a['v'][:,:2],a['source_v'][:,:2]))})
        continue
    d=source(name); sv,f,mi,uv,parent=refine(d)
    soil='SOIL' in name; finish=name.startswith('V24_24_')
    if soil:
        regions=np.zeros(len(sv),int);source_index=np.arange(len(sv))
    else:
        sv,f,mi,uv,parent=split_at_height_break(sv,f,mi,uv,parent)
        sv,f,mi,uv,parent,regions,source_index=cut_at_step(sv,f,mi,uv,parent)
    v=sv.copy();lower=float(sv[:,2].min());sample=sampler(d)
    topids=np.unique(f[np.cross(sv[f][:,1]-sv[f][:,0],sv[f][:,2]-sv[f][:,0])[:,2]>1e-11])
    tops={}
    for i in topids:
        x,y,z=sv[i];key=(round(float(x),7),round(float(y),7));tops[key]=max(tops.get(key,-1e10),z)
    cache={}
    for i,(x,y,z) in enumerate(sv):
        exterior= (soil or x<=.000001) and x<.25 and -11.6<y<11.9 and x>-7.1
        court=not soil and -.125-1e-6<=x<14.08001 and -3.6001<y<1.9001
        if not exterior and not court:continue
        key=(round(float(x),7),round(float(y),7))
        if key not in cache:cache[key]=tops[key] if key in tops else sample(float(x),float(y))
        oldtop=cache[key];wanted=oldtop
        if exterior:
            # The complete visible west yard and wall-foot line are level.
            w=clamp((x+7.1)/1.1)*clamp((y+11.6)/.2)*clamp((11.9-y)/.25)
            wanted=oldtop+(-.15-oldtop)*w
        elif court:
            # The low courtyard falls away from the existing house entry.
            wanted=low_level(float(y))
            if regions[i]:wanted=min(-.012,high_level(float(y)))
            # At the slab footprint the courtyard finish always stays below
            # the retained indoor slab; it cannot become an indoor floor.
            if y>=-.29999 and regions[i]:wanted=-.012
            if y<=-3.12:wanted=oldtop if regions[i] else oldtop+(-.45-oldtop)*clamp((y+3.6)/.30)
            if not finish:
                wanted-=.002
                if .125<x<13.10 and -3.6<y<1.9:wanted-=.008
            # Retain the existing low gallery and its drainage stone band.
            if y<=-3.12 and x>7.25:wanted=oldtop
        factor=1. if finish else clamp((float(z)-lower)/max(1e-7,oldtop-lower))
        v[i,2]+=(wanted-oldtop)*factor
    fn='GRADE_'+name+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv,source_v=sv,parent=parent,regions=regions)
    OUT['raw_objects'].append({'name':name,'file':fn,'materials':INDEX[name]['materials'],'smooth_top':False,'kind':'ground'})
    rec={'object':name,'vertices':len(v),'triangles':len(f),'maximum_change_m':float(abs(v-sv).max()),'xy_unchanged':bool(np.array_equal(v[:,:2],sv[:,:2]))}
    records.append(rec);print('GROUND',rec,flush=True)

# Kitchen north gable: set its face to the accepted closure plane, keeping
# the timber post, glazing, floor and both roof pitches in place.
name='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'
old=load(name);zone=cube([8.1,-3.00,-.60],[14.4,-2.40,5.8])
part=old^zone
new=union([old-zone,part.translate([0,-.28,0])])
new=new-cube([7.9,-3.28,-.60],[8.341,-2.4,5.8])
# At the facade joint the end wall uses the closure's 180mm thickness.
# Its old 350mm return extended south across the north window pane.
window_clearance=cube([8.341,-3.281,-.55],[9.70,-3.035,3.15])
new=new-window_clearance
# Concealed L-shaped bond behind the right-angle corner; it occupies only
# the wall thickness, never the courtyard side of either finished plane.
bond=union([cube([14.07,-2.885,-.55],[14.16,-2.855,2.44720006]),cube([14.115,-2.885,-.55],[14.16,-2.825,2.44720006])])
new=union([new,bond])
put(name,new,BRICK,transfer=True)
closure='V24_24_Kitchen_North_Veranda_White_Closure'
put(closure,load(closure)-cube([9.430,-3.5,-.6],[9.8,-2.4,3.5]),BRICK)
for name in ['V24_03_Kitchen_Rear_Stone_Plinth','V24_17_Kitchen_North_Gable_Coping',
             'V24_22_North_Verge','V24_22_North_Verge_Bead']+[f'V24_19_Kitchen_North_Faceted_Head_Frame_{i}'for i in [1,2,3]]:
    put(name,load(name).translate([0,-.28,0]),INDEX[name]['materials'][0],transfer=True)
NORTH=-2.80
for name in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','V24_20_Kitchen_Unified_Pan_Barrel_Slope_0','V24_25_Kitchen_East_Unified_Pan_Barrel_Field']:
    put(name,load(name)-cube([7.,NORTH,1.9],[15.5,-1.9,5.8]),CLAY)

# The east courtyard wall's old rise toward the kitchen is removed. Use the
# existing wall's native top stations as the deformation datum, preserving
# the retaining foot, curved plan and every unrelated perimeter section.
H=2.44720006; LOW=-.55
name='SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry';a=source(name);tt=a['v'][a['f']]
nn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);cc=tt.mean(1)
select=(cc[:,0]>13.7)&(cc[:,1]>-2.2)&(cc[:,1]<10.35)&(cc[:,2]>1.5)&(nn[:,2]>1e-6)
q=tt[select].reshape(-1,3);stations=[]
for yy in np.unique(np.round(q[:,1],5)):
    p=q[abs(q[:,1]-yy)<1e-4];stations.append([float(yy),float(p[:,2].max())])
stations=np.array(sorted(stations))
def old_top(y):return float(np.interp(y,stations[:,0],stations[:,1]))
def wall_weight(x,y):
    return clamp((x-13.60)/.22)*clamp((10.50-y)/.25) if y>-2.10001 else 0.
for name,kind in [
 ('SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','wall'),
 ('SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING_Geometry','attached'),
 ('SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry','wall'),
 ('V24_21_Exterior_Continuous_White_Frieze','attached'),
 ('V24_21_Exterior_Stepped_Cornices','attached')]:
    a=source(name);v=a['v'].copy()
    for i,(x,y,z)in enumerate(v):
        w=wall_weight(x,y)
        if not w:continue
        oh=old_top(float(y));factor=clamp((float(z)-LOW)/max(.1,oh-LOW))if kind=='wall'else 1.
        v[i,2]+=(H-oh)*factor*w
    if name=='SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry':
        topids=np.unique(a['f'][select])
        for i in topids:
            x,y,z=a['v'][i]
            if wall_weight(x,y)>.9999:v[i,2]=H
    fn='WALL_'+name+'.npz';np.savez_compressed(D/fn,v=v,f=a['f'],mi=a['mi'],uv=a['uv'])
    OUT['raw_objects'].append({'name':name,'file':fn,'kind':'copy_mesh','smooth_top':False})

# Remove the entire old oblique connector. The courtyard face is one plane,
# exactly perpendicular to the kitchen end wall, with no intermediate return.
OUT['remove']+=['V24_04_Kitchen_Perimeter_Upper_Return','V24_04_Kitchen_Perimeter_Return_Coping','V24_04_Kitchen_Perimeter_Upper_Return_Stone_Toe']

# A continuous, thin lime finish bridges the old connector/white-wall seam.
# The plan follows the original inside edge, rather than an invented straight
# wall through the curved perimeter. Its top is horizontal beneath the tiles.
wall=source('SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry');wv=wall['v']
points=[]
for yy in np.unique(np.round(wv[(wv[:,0]>14.15)&(wv[:,1]>-1.94)&(wv[:,1]<10.3),1],5)):
    p=wv[(abs(wv[:,1]-yy)<1e-4)&(wv[:,0]>14.15)]
    if len(p):points.append((float(p[:,0].min()),float(yy)))
route=[(13.8188,-2.9254),(14.1694,-1.9877)]+sorted(points,key=lambda p:p[1])
route=np.array([p for i,p in enumerate(route)if i==0 or np.linalg.norm(np.array(p)-route[i-1])>.001])
INNER_X=14.10;Y0=-2.855;Y1=10.25
oldroute=route.copy()
def old_inner_x(y):return float(np.interp(y,oldroute[:,1],oldroute[:,0]))
wall_ys=sorted(set([Y0,Y1]+[float(y)for y in oldroute[:,1]if Y0<y<Y1]))
fill_outline=[(INNER_X+.015,Y0),(INNER_X+.015,Y1)]+[(max(14.43,old_inner_x(y)+.03),y)for y in wall_ys[::-1]]
white_core=section(fill_outline,H-LOW).translate([0,0,LOW])
white_face=cube([INNER_X,Y0,LOW],[INNER_X+.016,Y1,H])
put('V24_28_Continuous_White_Courtyard_Wall_Face',union([white_core,white_face]),WHITE,True)

# Finish the previously unpaved narrow band against the white wall in the
# same running-bond modules as the adjacent court. Its bottom is solid, so
# the old earth cannot poke through the new high approach at the wall foot.
def inner_x(y):return INNER_X+.020
ys=sorted(set([-.0,-.3846,-2.855]+[float(y)for y in route[:,1]if -2.855<y<0]))
footprint=Polygon([(13.10,-2.855),(13.10,0.)]+[(inner_x(y)-.020,y)for y in ys[::-1]])
def high_top(y):return min(-.012,high_level(y))
def fitted_block(poly,grout=False):
    ycap=B[1]+(.388/.40)*(A[1]-B[1]);parts=[]
    for mask in [box(12.,-4.,16.,ycap),box(12.,ycap,16.,1.)]:
        cut=poly.intersection(mask)
        if cut.is_empty:continue
        for pp in [cut]if cut.geom_type=='Polygon'else cut.geoms:
            if pp.area<1e-10:continue
            m=section(list(pp.exterior.coords)[:-1],1.)
            a=m.to_mesh64();v=np.array(a.vert_properties[:,:3]);f=np.array(a.tri_verts)
            for i,(x,y,z)in enumerate(v):v[i,2]=-.65+(high_top(y)-(.0015 if grout else 0)+.65)*z
            parts.append(solid(v,f))
    return union(parts)
pieces=[]
for i in range(-4,5):
    y=-10.9+(i+17)*.62
    if y>0 or y+.62<-2.855:continue
    offset=.4-(.56 if (i+17)%2 else 0)
    for j in range(10,14):
        x=offset+j*1.12
        tile=footprint.intersection(box(x+.003,y+.003,x+1.117,y+.617))
        if tile.is_empty:continue
        for pp in [tile]if tile.geom_type=='Polygon'else tile.geoms:
            if pp.area>1e-8:
                put('V24_28_High_Approach_Stone_'+str(len(pieces)),fitted_block(pp),f'M_V22_Courtyard_Stone_{len(pieces)%4}',True)
                pieces.append(pp)
from shapely.ops import unary_union
grout=footprint.difference(unary_union(pieces));gs=[]
for pp in [grout]if grout.geom_type=='Polygon'else grout.geoms:
    if pp.area>1e-9:gs.append(fitted_block(pp,True))
put('V24_28_High_Approach_Stone_Joints',compose(gs),'M_V22_Courtyard_Filled_Joint',True)

# Remove the old raised tile terminal and give the whole visible wall a
# constant eave and ridge datum. The curved native plan is retained.
capline=LineString([(14.265,Y0),(14.265,Y1)]);length=capline.length
def frame(s):
    s=max(0.,min(length,float(s)));p=np.array(capline.interpolate(s).coords[0]);a=np.array(capline.interpolate(max(0,s-.002)).coords[0]);b=np.array(capline.interpolate(min(length,s+.002)).coords[0]);u=(b-a)/np.linalg.norm(b-a);return p,np.array([-u[1],u[0]])
def xyz(s,d,z):
    p,n=frame(s);outer=max(14.43,old_inner_x(p[1])+.33)+.075;inner=INNER_X-.075
    centre=(inner+outer)/2;scale=(outer-inner)/.48
    return [float(centre-d*scale),float(p[1]),float(z)]
# Continuous, thick bedding with a flat eave line beneath the barrel tiles.
stations=[0.]+list(np.arange(.15,length,.15))+[length];profile=[(-.24,H-.09),(.24,H-.09),(.24,H-.04),(0,H+.14),(-.24,H-.04)]
v=[xyz(s,d,z)for s in stations for d,z in profile];f=[];N=len(profile)
for i in range(len(stations)-1):
    for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.extend([[a,b,b+N],[a,b+N,a+N]])
for j in range(1,N-1):f.extend([[0,j+1,j],[(len(stations)-1)*N,(len(stations)-1)*N+j,(len(stations)-1)*N+j+1]])
cap_parts=[solid(v,f)]
def tile_shell(s,side,pan=False):
    us=np.linspace(-(.067 if pan else .065),(.067 if pan else .065),9 if pan else 13);vs=[];fs=[]
    for bottom in [False,True]:
        for d in [.018,.245]:
            for u in us:
                curve=.008*(u/.067)**2 if pan else np.sqrt(max(0,.065**2-u*u))
                vs.append(xyz(s+u,side*d,H+.151-.75*d+curve-(.012 if bottom else 0)))
    n=len(us);k=n*2
    for j in range(n-1):fs.extend([[j,j+n,j+n+1],[j,j+n+1,j+1],[j+k,j+1+k,j+1+n+k],[j+k,j+1+n+k,j+n+k]])
    rim=list(range(n))+list(range(2*n-1,n-1,-1))
    for a,b in zip(rim,rim[1:]+rim[:1]):fs.extend([[a,b,b+k],[a,b+k,a+k]])
    return solid(vs,fs)
for s in np.arange(.07,length-.055,.18):
    for side_ in [-1,1]:
        cap_parts.append(tile_shell(float(s),side_))
        p,n=frame(s);centre=np.array(xyz(s,side_*.251,H+.035));normal=np.r_[n,0.];cap_parts.append(rod(centre-normal*side_*.012,centre+normal*side_*.010,.070,24))
for s in np.arange(.16,length-.055,.18):
    for side_ in [-1,1]:cap_parts.append(tile_shell(float(s),side_,True))
# The imported old coping has legacy non-manifold joins. Clip only the marked
# local faces, retaining all unrelated triangles and UVs verbatim, rather
# than welding or rebuilding the entire perimeter to satisfy a boolean.
capname='SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING_Geometry'
oldcap=source(capname);ov=oldcap['v'];of=oldcap['f'];om=oldcap['mi'];ou=oldcap['uv'];cv=ov.tolist();cf=[];cm=[];cu=[]
bounds=np.array([[13.5,-2.101,1.8],[16.,10.30,3.6]])
def split_poly(poly,axis,limit,sign):
    ins=[];out=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        di=sign*(p[1][axis]-limit);dj=sign*(q[1][axis]-limit);pi=di>=-1e-10;qi=dj>=-1e-10
        (ins if pi else out).append(p)
        if pi!=qi:
            t=di/(di-dj);xyz_=p[1]+t*(q[1]-p[1]);tex=p[2]+t*(q[2]-p[2]);i=len(cv);cv.append(xyz_.tolist());r=(i,xyz_,tex);ins.append(r);out.append(r)
    return ins,out
def add_poly(poly,mat):
    for j in range(1,len(poly)-1):
        ps=[poly[0],poly[j],poly[j+1]]
        if len(set(p[0]for p in ps))<3:continue
        cf.append([p[0]for p in ps]);cm.append(mat);cu.append([p[2]for p in ps])
for face,mat,tuv in zip(of,om,ou):
    t=ov[face]
    if ((t.max(0)<bounds[0])|(t.min(0)>bounds[1])).any():
        cf.append(face);cm.append(mat);cu.append(tuv);continue
    poly=[(int(i),np.array(p),np.array(uv_))for i,p,uv_ in zip(face,t,tuv)]
    for axis in range(3):
        for limit,sign in [(bounds[0,axis],1),(bounds[1,axis],-1)]:
            if not poly:break
            poly,out=split_poly(poly,axis,limit,sign);add_poly(out,mat)
fn='CLIPPED_OLD_PERIMETER_CAP.npz';np.savez_compressed(D/fn,v=np.array(cv),f=np.array(cf),mi=np.array(cm),uv=np.array(cu))
for row in OUT['raw_objects']:
    if row['name']==capname:row.update(file=fn,kind='clipped_cap')
put('V24_28_Level_White_Wall_Tile_Coping',compose(cap_parts),CLAY,True)

# Timber that was embedded in the old north gable must stay behind the new
# face; exposed gallery posts and all glazing remain in their original place.
timbercut=cube([9.61,-2.875,-.45],[14.3,-2.4,5.3])
for name in ['SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry','SITE_KITCHEN_V12_UPPER_FACADE_COLUMN_CONTINUATIONS_Geometry']:
    put(name,load(name)-timbercut,INDEX[name]['materials'][0],transfer=True)
OUT['object_offsets']=[{'name':'SITE_PLANTER_1_Geometry','translation':[0.,0.,high_top(-1.)+.449951171875]}]

OUT['proof']={
 'references':['123610','123632','151433','151622','151816','152427'],
 'reference_files':['Step_Alignment_Before_Redline.png','Kitchen_Frame_Overlap_Before.png','Wall_Perpendicular_Join_Before.png'],
 'exterior':{'visible_west_yard_level_z_m':-.15,'flat_scope_xy':[-6.,-11.4,.25,11.65],'remote_blend_only':True},
 'courtyard_step':{'kitchen_end_xy':B.tolist(),'house_entry_end_xy':A.tolist(),'high_side':'east, as marked in the latest red line','low_side':'west','crest_z_at_ends_m':[-.40,0.],'low_court_z_at_ends_m':[-.45,-.15],'stone_edge_width_m':.10,'indoor_slabs_deformed':False,'original_entry_step_retained':True},
 'latest_step_alignment':{'reference':'Conversation red line on Step_Alignment_Before_Redline.png; crossed-out diagonal','old_house_end_xy':[9.25,-.30],'new_house_end_xy':A.tolist(),'aligned_to_kitchen_gallery_outer_edge_x_m':8.15,'old_diagonal_removed':True,'red_line_pixels_used':[[350,718],[400,728],[500,745],[600,765],[670,773]]},
 'window_joint':{'closure_ends_at_frame_x_m':9.430,'end_wall_south_limit_at_window_y_m':-3.035,'north_glass_limit_y_m':-3.04,'pane_clearance_m':.005,'windows_moved':False,'overlapping_masonry_removed':True},
 'kitchen_end':{'north_face_before_y_m':-2.575,'north_face_after_y_m':-2.855,'roof_north_limit_y_m':NORTH,'gable_recess_m':.28,'west_projection_removed_to_x_m':8.341,'timber_post_axis_unchanged':True},
 'facing_white_wall':{'top_z_m':H,'inside_face_x_m':INNER_X,'kitchen_end_face_y_m':-2.855,'intersection_angle_degrees':90.,'oblique_connector_removed':True,'extra_return_faces_removed':True,'continuous_single_plane_white_face':True,'outer_retaining_trace_retained':True},
 'ground':records,
 'preserved':['All three house floor slabs, indoor floors, thresholds and columns','Kitchen and storage indoor floors','All 26 animated doors','High bathroom windows','Inner gate and gate back','Kitchen south short verge, both roof pitches and tile phase','Inner courtyard thick tile coping','Original 1.65m roam and L/P measurement runtime'],
 'dimensions_basis':'Existing model datums and the user-marked photographs; fitted geometry, not a new field survey'}
write();print('V28_PREPARED',len(OUT['raw_objects']),len(OUT['objects']),len(OUT['remove']),flush=True)
