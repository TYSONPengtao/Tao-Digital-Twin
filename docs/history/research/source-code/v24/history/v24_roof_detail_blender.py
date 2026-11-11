"""Blender-only ceramic lap and ridge/verge connection details for V24.

Does not load/save the scene, change materials, regenerate relief, or alter the
converged outer eave width/height. Original meshes keep their UV and materials.
"""
import json, math
from pathlib import Path


def apply_v24_roof_detail(bpy, output_dir):
    import numpy as np
    import bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    tile=bpy.data.objects.get('SITE_V21_GATE_REFERENCE_LAYER_10_Geometry')
    carrier=bpy.data.objects.get('SITE_V21_GATE_REFERENCE_LAYER_09_Geometry')
    ridge=bpy.data.objects.get('SITE_V21_GATE_REFERENCE_LAYER_14_Geometry')
    if any(ob is None for ob in [tile,carrier,ridge]):raise RuntimeError('Missing compact gate roof nodes')
    if tile.get('V24_True_Ceramic_Laps'):raise RuntimeError('Roof-detail module already applied')
    me=tile.data
    # Recover each of the original 510 closed ceramic units without rewriting
    # their vertices, UV loops, material slots or object hierarchy. Material is
    # part of the weld key, keeping coincident neighbouring laps independent.
    v=np.empty(len(me.vertices)*3,dtype=np.float64);me.vertices.foreach_get('co',v);v=v.reshape(-1,3)
    ids=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',ids)
    totals=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('loop_total',totals)
    if np.any(totals!=3):raise RuntimeError('Expected actual triangulated V23 tile readback')
    faces=ids.reshape(-1,3);mats=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',mats)
    vm=np.zeros(len(v),dtype=np.int32);vm[faces.ravel()]=np.repeat(mats,3)
    packed=np.c_[np.rint(v*1e6).astype(np.int64),vm]
    unique,inverse=np.unique(packed,axis=0,return_inverse=True)
    parent=np.arange(len(unique),dtype=np.int32)
    def find(a):
        while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
        return a
    for a,b,c in inverse[faces]:
        ra,rb,rc=find(a),find(b),find(c)
        if ra!=rb:parent[rb]=ra
        if ra!=rc:parent[rc]=ra
    roots=np.asarray([find(i) for i in range(len(unique))])
    labels0,labels=np.unique(roots[inverse],return_inverse=True);n=len(labels0)
    lo=np.full((n,3),np.inf);hi=np.full((n,3),-np.inf)
    np.minimum.at(lo,labels,v);np.maximum.at(hi,labels,v)
    shifts=np.zeros(n);course_rows=[]
    for k,(a,b) in enumerate(zip(lo,hi)):
        yc=(a[1]+b[1])/2
        if b[1]<=-11.4859:
            frac=(yc+12.262)/.776;side='FRONT'
        elif a[1]>=-11.4861:
            frac=(-10.886-yc)/.600;side='REAR'
        else:raise RuntimeError(('Unexpected merged ceramic component',k,a.tolist(),b.tolist()))
        course=min(2,max(0,int(frac*3)))
        shifts[k]=course*.0015
        course_rows.append({'component':k,'side':side,'course':course,'raised_m':float(shifts[k])})
    if n!=510:raise RuntimeError(('Expected 510 independent ceramic units',n))
    original_positions=v.copy();v[:,2]+=shifts[labels]
    me.vertices.foreach_set('co',v.ravel());me.update();bpy.context.view_layer.update()
    tile['V24_True_Ceramic_Laps']='Upper courses raised 1.5 and 3.0 mm; original embedded bearing feet, UV and materials retained'

    def cache(ob):
        co=np.asarray([tuple(ob.matrix_world@q.co) for q in ob.data.vertices])
        fs=[list(p.vertices) for p in ob.data.polygons]
        tree=BVHTree.FromPolygons([Vector(q) for q in co],fs,all_triangles=False)
        uv=ob.data.uv_layers.active
        return ob,co,fs,tree,uv,co.min(0),co.max(0)
    tc=cache(tile);cc=cache(carrier)
    def surface(c,x,y):
        ob,co,fs,tree,uv,bblo,bbhi=c
        xx=min(max(float(x),bblo[0]+.000002),bbhi[0]-.000002)
        yy=min(max(float(y),bblo[1]+.000002),bbhi[1]-.000002)
        hit=tree.ray_cast(Vector((xx,yy,10.)),Vector((0.,0.,-1.)))
        if hit[0] is None:
            for dx,dy in [(0.,.000002),(0.,-.000002),(.000002,0.),(-.000002,0.)]:
                hit=tree.ray_cast(Vector((xx+dx,yy+dy,10.)),Vector((0.,0.,-1.)))
                if hit[0] is not None:break
        if hit[0] is None:raise RuntimeError(('No ceramic support surface',ob.name,x,y))
        point,normal,fi,dist=hit;poly=ob.data.polygons[fi];f=fs[fi]
        tex=(x,y)
        if uv and len(f)==3:
            a,b,d=co[f];u=b-a;w=d-a;p=np.asarray(point)-a
            den=np.dot(u,u)*np.dot(w,w)-np.dot(u,w)**2
            if abs(den)>1e-14:
                bu=(np.dot(w,w)*np.dot(p,u)-np.dot(u,w)*np.dot(p,w))/den
                bw=(np.dot(u,u)*np.dot(p,w)-np.dot(u,w)*np.dot(p,u))/den
                tx=[np.asarray(uv.data[i].uv) for i in poly.loop_indices]
                tex=tuple(tx[0]*(1-bu-bw)+tx[1]*bu+tx[2]*bw)
        return float(point.z),tex,int(poly.material_index)

    # Every retained bearing unit still penetrates the unchanged roof carrier.
    support=[]
    for k,(a,b) in enumerate(zip(lo,hi)):
        indices=np.flatnonzero(labels==k);q=v[indices];cx=(a[0]+b[0])/2
        candidate=np.flatnonzero((abs(q[:,0]-a[0])<2e-6)|(abs(q[:,0]-b[0])<2e-6)|(abs(q[:,0]-cx)<.00001))
        if len(candidate)>30:candidate=candidate[np.linspace(0,len(candidate)-1,30,dtype=int)]
        depths=[]
        for ii in candidate:
            p=q[ii];z,uv,mi=surface(cc,p[0],p[1]);depths.append(z-p[2])
        depth=max(depths,default=-1.)
        if depth<=.00015:raise RuntimeError(('Raised ceramic unit lost bearing',k,depth))
        support.append(depth)

    additions=[];mesh_reports=[]
    def mesh_object(name,verts,faces,uvs,material_source,poly_mats,parent_ob):
        data=bpy.data.meshes.new(name+'_Mesh');data.from_pydata(verts,[],faces);data.update()
        for mat in material_source.data.materials:data.materials.append(mat)
        for p,mi in zip(data.polygons,poly_mats):p.material_index=mi
        layer=data.uv_layers.new(name='Native_Surface_Interpolated_UV')
        for loop in data.loops:layer.data[loop.index].uv=uvs[loop.vertex_index]
        bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.normal_update()
        boundary=sum(not e.is_manifold for e in bm.edges);vol=abs(bm.calc_volume(signed=True));bm.free()
        if boundary or vol<=0:raise RuntimeError(('Open roof connection detail',name,boundary,vol))
        ob=bpy.data.objects.new(name,data)
        for coll in parent_ob.users_collection:coll.objects.link(ob)
        ob.parent=parent_ob.parent
        ob['Geometry_Source']='Blender-only ceramic detail sampled from exact compact V24 support surfaces'
        ob['Extent_Constraint']='Inside converged compact V23/V24 eave envelope'
        additions.append(ob)
        mesh_reports.append({'object':name,'vertices':len(data.vertices),'faces':len(data.polygons),'closed_manifold':True,'volume_m3':vol,'materials':[m.name if m else None for m in data.materials]})
        return ob

    def append_grid(V,F,U,PM,xs,ys,top,bottom,mat):
        start=len(V);nx=len(xs);ny=len(ys)
        for mode in [0,1]:
            for y in ys:
                for x in xs:
                    zz,uv=top(x,y) if mode else bottom(x,y);V.append([x,y,zz]);U.append(uv)
        plane=nx*ny
        for j in range(ny-1):
            for i in range(nx-1):
                a=start+j*nx+i;b=a+1;c=b+nx;d=a+nx
                F.extend([[a,d,c,b],[a+plane,b+plane,c+plane,d+plane]]);PM.extend([mat,mat])
        edge=[start+i for i in range(nx)]+[start+j*nx+nx-1 for j in range(1,ny)]+[start+(ny-1)*nx+i for i in range(nx-2,-1,-1)]+[start+j*nx for j in range(ny-2,0,-1)]
        for a,b in zip(edge,edge[1:]+edge[:1]):F.append([a,b,b+plane,a+plane]);PM.append(mat)

    # Fine lips only 0.7 mm proud, 6 mm long: enough to read a ceramic edge,
    # without the oversized collars/rings that would change the roof's scale.
    V=[];F=[];U=[];PM=[];lane_x=6.6+.87*(np.linspace(4.025,9.175,43)-6.6)
    rim_count=0
    for x in lane_x:
        for side,(edge,peak) in enumerate([(-12.262,-11.486),(-10.886,-11.486)]):
            direction=1. if side==0 else -1.
            for cut in np.linspace(edge,peak,4)[1:-1]:
                y0=cut-direction*.010
                xs=np.linspace(x-.032,x+.032,13);ys=np.linspace(y0,y0+direction*.006,3)
                z0,uv,mi=surface(tc,x,y0)
                def upper(xx,yy):
                    z,uv,mi=surface(tc,xx,yy);return z+.0007,uv
                def lower(xx,yy):
                    z,uv,mi=surface(tc,xx,yy);return z-.0008,uv
                append_grid(V,F,U,PM,xs,ys,upper,lower,mi);rim_count+=1
    mesh_object('V24_GATE_FINE_CERAMIC_LAP_LIPS',V,F,U,tile,PM,tile)

    # Sloped mortar fillets fill the real ridge-to-tile mouth below the caps.
    V=[];F=[];U=[];PM=[]
    for side in [-1,1]:
        ys=np.linspace(-11.486+side*.090,-11.486+side*.045,5)
        def upper(x,y):
            z,uv,mi=surface(cc,x,y);t=(.09-abs(y+11.486))/.045
            return z+.004+.008*max(0.,min(1.,t)),uv
        def lower(x,y):
            z,uv,mi=surface(cc,x,y);return z-.007,uv
        append_grid(V,F,U,PM,np.linspace(4.335,8.865,101),ys,upper,lower,0)
    mesh_object('V24_GATE_RIDGE_BEDDING_FILLETS',V,F,U,carrier,PM,carrier)

    # Short overlapping rounded verge covers connect eave wing roots to the
    # main ridge; each is embedded into the unchanged outer tile-bearing slab.
    V=[];F=[];U=[];PM=[];verges=0
    for x in [4.32495,8.87505]:
        for edge,peak in [(-12.262,-11.486),(-10.886,-11.486)]:
            cuts=np.linspace(edge,peak,4)
            for course,(a,b) in enumerate(zip(cuts,cuts[1:])):
                ys=np.linspace(min(a,b)-.005,max(a,b)+.005,7)
                ys=np.clip(ys,min(edge,peak),max(edge,peak))
                xs=np.linspace(x-.026,x+.026,15)
                def upper(xx,yy):
                    z,uv,mi=surface(cc,xx,yy);dx=(xx-x)/.026
                    return z-.002+course*.001+.029*math.sqrt(max(0.,1-dx*dx)),uv
                def lower(xx,yy):
                    z,uv,mi=surface(cc,xx,yy);return z-.009+course*.001,uv
                append_grid(V,F,U,PM,xs,ys,upper,lower,0);verges+=1
    mesh_object('V24_GATE_SEGMENTED_SIDE_VERGE_CAPS',V,F,U,ridge,PM,ridge)

    # The foreground gate in download.jpg has a small open diamond ridge
    # underneath the fine round copings. This is structural geometry, not an
    # alpha texture. Raise the original 34 copings exactly 72 mm; their vertex
    # indices, per-loop UV and original material slots remain unchanged.
    ridge_offset=.072
    ridge_old=np.asarray([tuple(q.co) for q in ridge.data.vertices])
    ridge_new=ridge_old.copy();ridge_new[:,2]+=ridge_offset
    ridge.data.vertices.foreach_set('co',ridge_new.ravel());ridge.data.update()
    ridge['V24_Photo_Confirmed_Open_Ridge']='Existing 34 copings raised 72 mm onto true open diamond ceramic band'
    V=[];F=[];U=[];PM=[]
    # Bottom and top rails embed into the roof carrier and coping undersides.
    for bottom_offset,top_offset in [(-.009,.005),(.050,.066)]:
        def upper(x,y):
            z,uv,mi=surface(cc,x,-11.486);return z+top_offset,uv
        def lower(x,y):
            z,uv,mi=surface(cc,x,-11.486);return z+bottom_offset,uv
        append_grid(V,F,U,PM,np.linspace(4.325,8.875,102),[-11.504,-11.468],upper,lower,0)

    def beam(a,b,width=.0065,depth=.028):
        # Rectangular ceramic diagonal in XZ, volumetric through the ridge.
        ax,az=a;bx,bz=b;dx,dz=bx-ax,bz-az;length=math.hypot(dx,dz)
        nx,nz=-dz/length*width/2,dx/length*width/2
        profile=[(ax+nx,az+nz),(bx+nx,bz+nz),(bx-nx,bz-nz),(ax-nx,az-nz)]
        start=len(V)
        for y in [-11.486-depth/2,-11.486+depth/2]:
            for x,z in profile:
                zz,uv,mi=surface(cc,x,-11.486);V.append([x,y,z]);U.append(uv)
        F.extend([[start+3,start+2,start+1,start],[start+4,start+5,start+6,start+7],
                  [start,start+1,start+5,start+4],[start+1,start+2,start+6,start+5],
                  [start+2,start+3,start+7,start+6],[start+3,start,start+4,start+7]])
        PM.extend([0]*6)
    diamond_count=45
    for x in np.linspace(4.385,8.815,diamond_count):
        zz,uv,mi=surface(cc,x,-11.486)
        # Offset each vertex to the registered ridge height at its own X.
        contour=[]
        for xx,off in [(x-.044,.028),(x,.054),(x+.044,.028),(x,.002)]:
            z,uv,mi=surface(cc,xx,-11.486);contour.append((xx,z+off))
        for a,b in zip(contour,contour[1:]+contour[:1]):beam(a,b)
    for x in [4.339,8.861]:
        z,uv,mi=surface(cc,x,-11.486);beam((x,z-.007),(x,z+.066),width=.026,depth=.036)
    lattice=mesh_object('V24_GATE_PHOTO_OPEN_DIAMOND_RIDGE',V,F,U,ridge,PM,ridge)
    lc=cache(lattice);clear_holes=0
    for x in np.linspace(4.385,8.815,diamond_count):
        z,uv,mi=surface(cc,x,-11.486)
        hit=lc[3].ray_cast(Vector((float(x),-11.54,z+.028)),Vector((0.,1.,0.)),.108)
        if hit[0] is None:clear_holes+=1
    if clear_holes!=diamond_count:raise RuntimeError(('Diamond ridge apertures blocked',clear_holes,diamond_count))
    bpy.context.view_layer.update()
    bounds=[]
    for ob in additions:
        bounds.extend([tuple(ob.matrix_world@Vector(c)) for c in ob.bound_box])
    bounds=np.asarray(bounds)
    if bounds[:,0].min()<3.9435 or bounds[:,0].max()>9.2565 or bounds[:,2].max()>3.3640:
        raise RuntimeError(('Roof-detail addition exceeded compact silhouette',bounds.min(0),bounds.max(0)))
    report={'status':'PASS_BLENDER_ROOF_DETAIL','roof_units':n,'raised_course_offsets_m':[0.,.0015,.003],
            'changed_old_objects':['SITE_V21_GATE_REFERENCE_LAYER_10_Geometry','SITE_V21_GATE_REFERENCE_LAYER_14_Geometry'],
            'added_objects':[ob.name for ob in additions],
            'original_tile_vertex_count':len(v),'original_tile_vertices_moved':int((shifts[labels]>0).sum()),
            'original_tile_materials_and_uv_untouched':True,'minimum_retained_carrier_penetration_m':min(support),
            'fine_lap_lips':rim_count,'segmented_side_verge_units':verges,'ridge_bedding_fillets':2,
            'open_diamond_ridge_cells':diamond_count,'existing_copings_raised_m':ridge_offset,
            'ray_verified_clear_diamond_apertures':clear_holes,'lattice_lower_rail_embed_m':.009,'nominal_lattice_top_rail_coping_overlap_m':.009,
            'coping_before_max_z_m':float(ridge_old[:,2].max()),'coping_after_max_z_m':float(ridge_new[:,2].max()),
            'height_exception':'User requested the missing open diamond ridge body below the existing fine copings; 72 mm rise only at the main ridge, outer wings/eaves unchanged',
            'added_bbox':[bounds.min(0).tolist(),bounds.max(0).tolist()],'meshes':mesh_reports,
            'preserved':['all existing material slots','all original tile UV loops','converged wing/eave width and height','sculpted wing mesh','relief and doors','kitchen structural junction'],
            'reference_fit':'Ceramic overlap, ridge bedding and verge construction fitted to registered roof; no new survey dimensions'}
    (out/'V24_Roof_Detail_Report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    return report
