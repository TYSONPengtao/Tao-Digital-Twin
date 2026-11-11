"""Local photo-based F1 fixed lower lights, upper sill lowering and flush wall returns."""
from v26_2_common import *
import v26_2_common as C
from shapely.geometry import LineString
from v26_8_native_cleanup import repair_native

D=W/'v26_9';D.mkdir(exist_ok=True);C.D=D
FD=W/'v26_8/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
HN='V26_3_House_Connected_Walls_And_Stairs'
WHITE='M_Wall_Interior';BLACK='M_Metal_Black';GLASS='M_Glass_Clear'
floors={1:-.44999998807907104,2:3.450000047683716,3:7.050000190734863}
rail_top=4.600049018859863
targets={1:floors[1]+.30,2:rail_top-.10,3:floors[3]+rail_top-floors[2]-.10}
old_sills={fl:float(J[f'BAY_WINDOW_F{fl}_{"L"if fl<3 else"R"}_1_Geometry']['bounds'][0][2])for fl in floors}
anchors={2:5.9679,3:9.3519}
split=floors[1]+1.20
proof={'f1_lower_light':'User confirmed lower fixed glass, shorter opening leaves, retained30cm base',
       'upper_sill':'Opening leaves end at solid sill wall, no lower fixed light on F2/F3',
       'upper_lowering_m':.10,'new_sill_world_z_m':targets,
       'f1_lower_transom_center_z_m':split,'f1_lower_transom_height_above_floor_m':1.20,
       'dimension_status':'Heights other than user-confirmed F1 30cm are reference-image/native-model fits, not field survey',
       'bay_sill_repairs':[],'glass_clearance':[]}


def old(n):
    r=J[n];a=np.load(FD/r['file'])
    uv=a['uv'].copy();bad=~np.isfinite(uv).all(axis=(1,2))
    if bad.any():
        uv[bad]=uv_project(a['v'],a['f'])[bad]
        proof.setdefault('repaired_source_invalid_uv_faces',[]).append({'object':n,'faces':np.flatnonzero(bad).tolist()})
    return tracked(a['v'],a['f'],r['materials'],a['mi'],uv,n)


def upper_warp(v,fl):
    v=v.copy();z=v[:,2]
    weight=np.interp(z,[floors[fl],old_sills[fl]-.061,old_sills[fl]+.08,anchors[fl]],
                     [0.,1.,1.,0.],left=0.,right=0.)
    weight[(abs(z-floors[fl])<.00001)|(abs(z-anchors[fl])<.00001)]=0.
    v[:,2]+=weight*(targets[fl]-old_sills[fl])
    return v


def raw_export(n,v,a,r,why):
    fn=n+'.npz';np.savez_compressed(D/fn,v=v,f=a['f'],mi=a['mi'],uv=a['uv'])
    return {'name':n,'file':fn,'materials':r['materials'],'triangles':len(a['f']),
            'bounds':[v.min(0).tolist(),v.max(0).tolist()],'reason':why}


house=old(HN);before=house;rows=[];fixed_rows=[];scope=[]
for fl in[1,2,3]:
 for side in(['L','R']if fl<3 else['R']):
    x0=0. if side=='L'else 9.1
    if fl>1:
        lo=np.array([x0-.24,.78,floors[fl]-.205],np.float32).astype(float)
        hi=np.array([x0+4.14,2.215,anchors[fl]],np.float32).astype(float)
        cutter=finish(cube(lo,hi),WHITE,f'F{fl}{side} local sill lowering')
        part=house^cutter
        sr,_=export(f'Temp_F{fl}_{side}_Bay',part)
        a=np.load(D/sr['file']);v=upper_warp(a['v'],fl)
        warped=tracked(v,a['f'],sr['materials'],a['mi'],a['uv'],f'F{fl}{side} lower sill')
        house=(house-cutter)+warped
        scope.append(cube(lo,hi))
    # A constant200mm under-window strip reconnects the chipped diagonal
    # returns to the actual narrow jamb. It does not turn into a thick post.
    centre=[(x0,2.10),(x0+.72,1.10),(x0+3.18,1.10),(x0+3.90,2.10)]
    poly=LineString(centre).buffer(.10,cap_style=2,join_style=2)
    z0=-.600000024 if fl==1 else floors[fl]-.0004
    z1=targets[fl]-.001
    strip=finish(section(list(poly.exterior.coords)[:-1],z1-z0).translate([0,0,z0]),WHITE,
                 f'F{fl}{side} continuous200mm sill and diagonal wall return')
    added=(strip-house).volume();house+=strip;scope.append(strip)
    # The oblique strip meets a narrow orthogonal door/outer jamb. Close
    # the small triangular base recess at both ends below the frame only.
    for xx in [x0,x0+3.9]:
        foot=finish(cube([xx-.12,1.98,z0],[xx+.12,2.22,z1]),WHITE,'Finite240mm corner bond below the black window frame')
        house+=foot;scope.append(foot)
    proof['bay_sill_repairs'].append({'floor':fl,'side':side,'plan':list(poly.exterior.coords),
                                    'ordinary_thickness_m':.20,'bottom_z_m':z0,'top_z_m':z1,
                                    'added_corner_volume_m3':added})
    for k in range(3):
        n=f'BAY_WINDOW_F{fl}_{side}_{k}_Geometry';r=J[n];a=np.load(FD/r['file'])
        if fl>1:
            row=raw_export(n,upper_warp(a['v'],fl),a,r,'Lower sill100mm beneath original stone rail; retain upper transoms and XY')
        else:
            ids=[i for i,m in enumerate(r['materials'])if'Glass'in m]
            gf=a['f'][np.isin(a['mi'],ids)];bf=a['f'][~np.isin(a['mi'],ids)]
            black=tracked(a['v'],bf,[BLACK],np.zeros(len(bf),int),a['uv'][~np.isin(a['mi'],ids)],n+' original black frame')
            glass=tracked(a['v'],gf,[GLASS],np.zeros(len(gf),int),a['uv'][np.isin(a['mi'],ids)],n+' original glass')
            if k==1:
                xmin,xmax=x0+.72,x0+3.18
                bar=finish(cube([xmin+.035,1.055,split-.02],[xmax-.035,1.145,split+.02]),BLACK,'Fixed lower-light transom')
                gc=cube([xmin-1.,.8,split-.0204],[xmax+1.,1.4,split+.0204])
                glass-=finish(gc,GLASS,'Glass ends clear of transom')
                for xa,xb in[(xmin+.04,xmin+.80),(xmin+1.66,xmax-.04)]:
                    glass+=finish(cube([xa+.0004,1.097,targets[1]+.0404],[xb-.0004,1.103,split-.0204]),GLASS,'Independent lower fixed pane beneath opening leaf')
            else:
                ts=a['v'][gf];norms=np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]);nxy=norms[np.argmax(np.linalg.norm(norms,axis=1)),:2];nxy/=np.linalg.norm(nxy)
                u=np.array([nxy[1],-nxy[0]]);uv=a['v'][:,:2]@u;nv=a['v'][:,:2]@nxy
                transform=[[u[0],nxy[0],0,0],[u[1],nxy[1],0,0],[0,0,1,0]]
                bar=finish(cube([uv.min()+.055,nv.min(),split-.02],[uv.max()-.055,nv.max(),split+.02]).transform(transform),BLACK,'Oblique lower fixed glass transom')
                gc=cube([uv.min()-1,nv.min()-1,split-.0204],[uv.max()+1,nv.max()+1,split+.0204]).transform(transform)
                glass-=finish(gc,GLASS,'Oblique glazing clear of new transom')
            combined=(black+bar)+glass
            row,_=export(n,combined,'Photo-matched first-floor lower fixed lights; retain black perimeter and upper transom')
        rows.append(row);fixed_rows.append((fl,side,k,row))
    for handed in['Left','Right']:
        fn=f'V24_18_BAY_WINDOW_F{fl}_{side}_1_{handed}_Outward_Hinge_Frame'
        fa=np.load(FD/J[fn]['file']);lo=fa['v'][:,2].min();hi=fa['v'][:,2].max()
        mid=(lo+hi)/2;newlo=split+.026;newmid=(newlo+hi)/2
        for kind in['Frame','Glass']:
            n=f'V24_18_BAY_WINDOW_F{fl}_{side}_1_{handed}_Outward_Hinge_{kind}';r=J[n];a=np.load(FD/r['file']);v=a['v'].copy()
            if fl>1:v=upper_warp(v,fl)
            else:
                v[:,2]=np.interp(v[:,2],[lo,lo+.060,mid-.10,mid+.10,hi-.060,hi],
                                  [newlo,newlo+.060,newmid-.10,newmid+.10,hi-.060,hi])
            rows.append(raw_export(n,v,a,r,'Shortened F1 opening leaf above independent fixed light'if fl==1 else'Upper opening leaf lands directly on lowered solid sill'))

# Original frame seats already have the correct XY footprint. Upper seats
# move coherently with the sill warp. Avoid re-cutting their unchanged top
# edges and creating submicron slivers along a previously fused boundary.
for fl,side,k,row in []:
    a=np.load(D/row['file']);ids=[i for i,m in enumerate(row['materials'])if'Glass'in m]
    gt=a['v'][a['f'][np.isin(a['mi'],ids)]]
    ns=np.cross(gt[:,1]-gt[:,0],gt[:,2]-gt[:,0]);n=ns[np.argmax(np.linalg.norm(ns,axis=1)),:2];n/=np.linalg.norm(n);u=np.array([n[1],-n[0]])
    aa=a['v'][:,:2]@u;bb=a['v'][:,:2]@n
    cutter=cube([aa.min()-.0004,bb.min()-.0004,a['v'][:,2].min()-.0004],
                [aa.max()+.0004,bb.max()+.0004,a['v'][:,2].max()+.0004]).transform([[u[0],n[0],0,0],[u[1],n[1],0,0],[0,0,1,0]])
    house-=finish(cutter,WHITE,'Frame-owned finite reveal without white/black competing faces')
    scope.append(cutter)

row,house=export(HN,house.simplify(.00003),'Local bay sill lowering and continuous200mm underwindow corner returns')
a=np.load(D/row['file']);v,f,mi,uv,repair=repair_native(a['v'],a['f'],a['mi'],a['uv'])
np.savez_compressed(D/row['file'],v=v,f=f,mi=mi,uv=uv);row['triangles']=len(f)
np.savez_compressed(D/('Window_Base_'+row['file']),v=v,f=f,mi=mi,uv=uv)
proof['native_cleanup']=repair
rows.insert(0,row)
mask=union(scope)
proof['outside_scope_removed_m3']=((before-house)-mask).volume()
proof['outside_scope_added_m3']=((house-before)-mask).volume()
proof['house_components']=len(house.decompose())
proof['house_volume_m3']=house.volume()
proof['reference_files']=['D:/Desktop/屏幕截图 2026-10-24 '+s+'.jpg'for s in['142610','142814','143050','143117']]
(D/'Prepared_Geometry.json').write_text(json.dumps({'objects':rows,'proof':proof,'remove':[]},ensure_ascii=False,indent=2),'utf8')
print('V26_9_PREPARED',len(rows),house.num_tri(),proof['house_components'],flush=True)
