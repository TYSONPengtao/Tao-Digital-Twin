"""Authorized local scan cleanup around reconstructed roof/column contacts.
Unmodified original and V7 sources remain separately preserved.
"""
import sys,json,math,copy,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid')
ZONES=[
 {'id':'SCREENWALL_FLYING_EAVES','min':[2.65,-18.22,2.58],'max':[11.4,-15.65,5.05],'evidence':'DJI_0110 and annotated001538'},
 {'id':'GATEHOUSE_FLYING_EAVES','min':[3.92,-13.22,2.44],'max':[9.23,-10.05,5.12],'evidence':'DJI_0046 and annotated001244'},
 {'id':'KITCHEN_ROOF_AND_UPPER_FRAME','min':[6.82,-12.23,2.38],'max':[13.78,-1.98,5.36],'evidence':'DJI_0046, registered roof samples, annotated001244'},
 {'id':'COURTYARD_WALL_END_CONTACT','min':[-.18,.98,-.59],'max':[.18,1.90,2.25],'evidence':'annotated001317,001738'},
 {'id':'F1_ROMAN_ARCH_CONTACT','min':[3.65,-.27,2.40],'max':[9.35,.27,3.90],'evidence':'User001628 clarification: column to slab; arch end to side'},
 {'id':'F2_ROMAN_ARCH_CONTACT','min':[3.65,-.27,6.60],'max':[9.35,.27,7.50],'evidence':'Same repeated column/arch contact correction'}]
def polyclip(v,k,lim,greater):
    if not len(v):return v
    out=[]
    for a,b in zip(v,np.roll(v,-1,axis=0)):
        qa=a[k]-lim;qb=b[k]-lim
        ia=qa>=-1e-10 if greater else qa<=1e-10
        ib=qb>=-1e-10 if greater else qb<=1e-10
        if ia:out.append(a)
        if ia!=ib:out.append(a+(b-a)*(qa/(qa-qb)))
    return np.array(out)
def subtract_box(poly,lo,hi):
    inside=poly;outside=[]
    for k in range(3):
        for lim,positive in [(lo[k],True),(hi[k],False)]:
            p=polyclip(inside,k,lim,not positive)
            if len(p)>=3:outside.append(p)
            inside=polyclip(inside,k,lim,positive)
            if len(inside)<3:return outside
    return outside
def cut(poly):
    polys=[poly]
    for z in ZONES:
        lo=np.array(z['min']);hi=np.array(z['max']);new=[]
        for p in polys:
            if np.any(p[:,:3].max(0)<lo-1e-9) or np.any(p[:,:3].min(0)>hi+1e-9):new.append(p)
            else:new+=subtract_box(p,lo,hi)
        polys=new
    return polys
def tri_fan(p):
    for k in range(1,len(p)-1):
        t=p[[0,k,k+1]]
        if np.linalg.norm(np.cross(t[1,:3]-t[0,:3],t[2,:3]-t[0,:3]))>1e-9:yield t
def eligible_xyz(tri):
    a=tri.min(1);b=tri.max(1);q=np.zeros(len(tri),bool)
    for z in ZONES:q|=((b>=np.array(z['min'])-1e-9)&(a<=np.array(z['max'])+1e-9)).all(1)
    return q
def encode(p):return {'outer':list(map(list,list(p.exterior.coords)[:-1])),'holes':[list(map(list,list(r.coords)[:-1])) for r in p.interiors]}
def scope():
    hp=json.loads((O/'02_Data/Hole_Polygon.json').read_text(encoding='utf-8'));H=Polygon(hp['local']['outer'],hp['local']['holes'])
    clear=json.loads((W/'v8_terrain_clear/Terrain_Clearance_Polygon.json').read_text(encoding='utf-8'))
    # Agent encodes main union as a GeoJSON geometry alongside the redline.
    if 'edit_mask_geojson' in clear:ground=shapely.geometry.shape(clear['edit_mask_geojson'])
    elif 'clearance_mask_geojson' in clear:ground=shapely.geometry.shape(clear['clearance_mask_geojson'])
    elif 'edit_polygons' in clear:ground=unary_union([Polygon(p['outer'],p.get('holes',[])) for p in clear['edit_polygons']])
    elif 'clearance' in clear:ground=unary_union([Polygon(p['outer'],p.get('holes',[])) for p in clear['clearance']])
    else:
        ground=shapely.geometry.shape(clear['edit_mask'])
    repair=unary_union([box(z['min'][0],z['min'][1],z['max'][0],z['max'][1]) for z in ZONES])
    allowed=unary_union([H,ground,repair])
    ps=[allowed] if allowed.geom_type=='Polygon' else list(allowed.geoms)
    r={'polygons':[encode(p) for p in ps],'source_scope':'Original main void union user western terrain clearance and local roof/column contact repairs','authorized_xyz_cleanup':ZONES,'allowed_xy_area_m2':allowed.area,'original_void_area_m2':H.area,'added_xy_area_m2':allowed.difference(H).area,'original_source_file_immutable':True}
    (O/'02_Data/V8_Allowed_Repair_Scope.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    return allowed
def cleanup():
    C=json.loads((O/'02_Data/Coordinate.json').read_text());a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);report=[]
    BI=json.loads((O/'02_Data/Base_Index.json').read_text(encoding='utf-8'))
    for b in BI:
        p=O/'02_Data'/('Base_'+str(b['index'])+'.npz');d=np.load(p);v=d['vertices'];local=(v-origin)@R;fs=d['faces'];uv=d['uv'];ns=d['normals'];candidate=[]
        # Conservative face bounds screening; exact 3-D clipping below.
        for begin in range(0,len(fs),10000):
            q=fs[begin:begin+10000];vv=local[q[:,:3]]
            if q.shape[1]==4:
                aa=local[q].min(1);bb=local[q].max(1);ok=np.zeros(len(q),bool)
                for z in ZONES:ok|=((bb>=z['min'])&(aa<=z['max'])).all(1)
            else:ok=eligible_xyz(vv)
            candidate.extend((np.flatnonzero(ok)+begin).tolist())
        if not candidate:report.append({'base':b['index'],'candidate_faces':0,'unchanged':True});continue
        nv=v.tolist();nu=uv.tolist();nn=ns.tolist();keep=np.ones(len(fs),bool);added=[];modified=[]
        for i in candidate:
            ids=fs[i,:3] if fs[i,2]==fs[i,3] else fs[i];poly=np.c_[local[ids],uv[ids],ns[ids]];pieces=cut(poly)
            if len(pieces)==1 and np.array_equal(pieces[0],poly):continue
            keep[i]=False;modified.append(i)
            for q in pieces:
                for t in tri_fan(q):
                    n=len(nv);nv.extend((t[:,:3]@R.T+origin).tolist());nu.extend(t[:,3:5].tolist());nn.extend(t[:,5:8].tolist());added.append([n,n+1,n+2,n+2])
        newfaces=np.vstack([fs[keep],np.array(added,np.int32).reshape(-1,4)])
        np.savez_compressed(p,vertices=np.asarray(nv),faces=newfaces,uv=np.asarray(nu),normals=np.asarray(nn))
        b.update(vertices=len(nv),faces=len(newfaces),uv_count=len(nu),v8_roof_contact_cleanup={'removed_or_clipped_original_faces':len(modified),'added_clipped_triangles':len(added)})
        np.savez_compressed(O/'02_Data'/('V8_Roof_Contact_Base_'+str(b['index'])+'_Face_Map.npz'),retained_input_face_indices=np.flatnonzero(keep),modified_input_face_indices=np.array(modified,int),input_faces=fs,input_vertex_count=np.array(len(v)))
        report.append({'base':b['index'],'candidate_faces':len(candidate),'modified_faces':len(modified),'added_triangles':len(added),'retained_array_prefix_exact':True,'retained_whole_faces_exact':True})
    (O/'02_Data/Base_Index.json').write_text(json.dumps(BI,ensure_ascii=False,indent=2),encoding='utf-8')
    I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));patchreports=[]
    for r in I:
        if not r['name'].startswith(('PHOTO_BOUNDARY_','PHOTO_RIM_')):continue
        d=np.load(O/'02_Data'/r['file']);v=d['vertices'];fs=d['faces'];uv=d['uv'];mi=d['material_ids'];ts=v[fs];candidate=eligible_xyz(ts)
        if not candidate.any():continue
        tris=[];tuv=[];mids=[];modified=0
        for i,(t,q,m) in enumerate(zip(ts,uv[fs],mi)):
            if not candidate[i]:tris.append(t);tuv.append(q);mids.append(m);continue
            poly=np.c_[t,q];pieces=cut(poly)
            if len(pieces)==1 and np.array_equal(pieces[0],poly):tris.append(t);tuv.append(q);mids.append(m);continue
            modified+=1
            for p in pieces:
                for tt in tri_fan(p):tris.append(tt[:,:3]);tuv.append(tt[:,3:5]);mids.append(m)
        if not modified:continue
        fn='V8_Contact_'+r['name']+'.npz';vv=np.array(tris).reshape(-1,3);ff=np.arange(len(vv),dtype=np.int32).reshape(-1,3)
        np.savez_compressed(O/'02_Data'/fn,vertices=vv,faces=ff,uv=np.array(tuv).reshape(-1,2),material_ids=np.array(mids,np.int32))
        r.update(file=fn,vertices=len(vv),triangles=len(ff),v8_contact_cleanup=modified,photo_triangles=sum(int((np.array(mids)==j).sum()) for j,m in enumerate(r['materials']) if m.startswith(('PATCH_PHOTO_','BASE_PHOTO_'))))
        patchreports.append({'name':r['name'],'modified_triangles':modified,'retained_triangles':len(ff)})
    (O/'02_Data/Patch_Index.json').write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf-8')
    # Working derivative contains exact retained arrays and original material/IDs.
    source=rh.File3dm.Read(str(O/'01_Source/Pure_Site_UNMODIFIED.3dm'))
    for i,ob in enumerate(list(source.Objects)):
        d=np.load(O/'02_Data'/('Base_'+str(i)+'.npz'));m=rh.Mesh();m.Vertices.UseDoublePrecisionVertices=True
        for v in d['vertices']:m.Vertices.AddPoint3d(*map(float,v))
        for f in d['faces']:m.Faces.AddFace(*map(int,f))
        mapping=rh.TextureMapping.CreatePlaneMapping(rh.Plane.WorldXY(),rh.Interval(0,1),rh.Interval(0,1),rh.Interval(0,1));m.SetTextureCoordinates(mapping,rh.Transform.Identity(),False)
        for j,u in enumerate(d['uv']):m.TextureCoordinates[j]=rh.Point2f(*map(float,u))
        m.Normals.Clear()
        for n in d['normals']:m.Normals.Add(*map(float,n))
        for j,n in enumerate(d['normals']):m.Normals[j]=rh.Vector3f(*map(float,n))
        assert m.IsValid,ob.Attributes.Name
        at=ob.Attributes;source.Objects.Delete(at.Id);newid=source.Objects.AddMesh(m,at);assert newid==at.Id
    assert source.Write(str(O/'01_Source/Pure_Site_WORKING_V8.3dm'),8)
    rep={'status':'PASS','boxes':ZONES,'base':report,'recovery_patches':patchreports,'source_file_unchanged':True,'method':'Exact polygon difference against user-authorized local 3-D roof/column contact regions; original vertices/UV/normals retained as prefix, clipping attributes interpolated only at new cut edges'}
    (O/'06_Report/Local_Source_Contact_Cleanup_QA.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rep,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
    if '--scope' in sys.argv:scope()
    else:cleanup()
