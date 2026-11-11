# Executed by v26_5_prepare.py with the tracked current house and source cores.
# Bridge the confirmed first/second floor exterior band only; intersection
# of native slices preserves the existing column and left-wing footprints.
band=(house.slice(3.319)^house.slice(3.451)).extrude(.132).translate([0,0,3.319])
mask=union([cube([-.3,1.9,3.31],[.3,10.1,3.46]),cube([12.7,1.9,3.31],[13.3,10.1,3.46]),cube([-.3,9.5,3.31],[13.3,10.1,3.46])]);band=band^mask
b=band.to_mesh64();v=np.array(b.vert_properties[:,:3]);f=np.array(b.tri_verts);tr=v[f];no=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);mid=tr.mean(1);exterior=((no[:,0]>0)&(mid[:,0]>13.))|((no[:,0]<0)&(mid[:,0]<0.))|((no[:,1]>0)&(mid[:,1]>9.8));mi=exterior.astype(np.int32)
band=tracked(v,f,['M_Wall_Interior','M_V21_House_Exterior_Grey_White'],mi,name='Continuous original-plan exterior first floor slab edge')
oldvol=house.volume();house=house+band;proof.append({'repair':'Exterior first to second floor wall/slab junction','height_m':[3.319,3.451],'method':'Intersect native below and above wall footprints; west east and rear exterior strips only','added_volume_m3':house.volume()-oldvol,'stairwell_interior_not_filled':True})
# Clean obsolete white fin branches at the diagonal/front bay joints.
# Original side/front black frames already meet; preserve their whole meshes.
roof=[]
for n in ['ROOF_EAVE_FASCIA_Geometry','ROOF_MAIN_JOINED_Geometry']:
 a=np.load(PD/PI[n]['file']);roof.append(solid(a['v'],a['f'],n))
protect=core+union(roof)
for fl,side,base in [(1,'L',0.),(1,'R',9.1),(2,'L',0.),(2,'R',9.1),(3,'R',9.1)]:
 r=J[f'BAY_WINDOW_F{fl}_{side}_1_Geometry'];lo,hi=np.array(r['bounds']);z0,z1=lo[2],hi[2]
 boxes=[[[base+x0,.98,z0],[base+x1,1.25,z1]]for x0,x1 in[(.55,.95),(2.95,3.35)]]
 cutter=union([cube(a,b)for a,b in boxes])-protect;removed=(house^cutter).volume();house=house-finish(cutter,'M_Wall_Interior','Remove only redundant exterior bay opaque corner fins')
 proof.append({'repair':'Redundant white bay corner fins','bay':f'F{fl}_{side}','cut_boxes_m':boxes,'removed_volume_m3':removed,'original_window_unchanged':True,'actual_beams_columns_roof_protected':True})
