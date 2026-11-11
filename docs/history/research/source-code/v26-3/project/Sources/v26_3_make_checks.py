from pathlib import Path
W=Path(__file__).parent
s=(W/'v26_2_readback.py').read_text('utf8').replace('v26_2','v26_3').replace('V26_2','V26_3')
s=s.replace("  if n=='DOOR_BATH_F1_R__LEAF':want[2,3]-=.45\n",'')
s=s.replace("All door poses retained except the explicit 450mm datum correction","All original evaluated door poses retained")
s=s.replace('V26.1 source remains byte identical','V26.2 source remains byte identical')
s=s.replace('V26_3_House_Flush_Continuous_Finished_Shell','V26_3_House_Connected_Walls_And_Stairs').replace('V26_3_Continuous_Ground_And_Perimeter_Shell','V26_2_Continuous_Ground_And_Perimeter_Shell')
where=s.index("# Export actual evaluated hinge matrices")
extra='''
# The recovered screenwall is the original native mesh, transform and finish.
orig=json.loads((D/'Original_Secondary.json').read_text('utf8'));restorebad=[]
for r in orig['objects']:
 o=bpy.data.objects[r['name']];a=np.load(D/r['file']);me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2))
 ok=v.shape==a['v'].shape and np.array_equal(v,a['v'])and np.array_equal(f,a['f'])and np.array_equal(mi,a['mi'])and np.array_equal(uv,a['uv'])and[m.name for m in me.materials]==r['materials']and not o.hide_render and not o.hide_get()
 if not ok:restorebad.append(r['name'])
ck('All 11 original V24.34 secondary screenwall components restored exactly',not restorebad,invalid=restorebad,components=len(orig['objects']),original_sha256=orig['sha256'])
ck('All five unintended replacement screenwall components hidden and excluded from collision',all(bpy.data.objects[n].hide_render and n not in cn for n in ch['archived']if n.startswith('V26_1_Secondary_Wall_')))
gn='V26_2_Continuous_Ground_And_Perimeter_Shell';oldindex={r['name']:r for r in json.loads((W/'v26_2'/'Final'/'Geometry_Index.json').read_text('utf8'))};oa=np.load(W/'v26_2'/'Final'/oldindex[gn]['file']);go=bpy.data.objects[gn];gv=np.array([go.matrix_world@p.co for p in go.data.vertices]);go.data.calc_loop_triangles();gf=np.array([t.vertices[:]for t in go.data.loop_triangles],np.int32)
ck('Secondary finish restoration preserves every ground and perimeter vertex and face',np.array_equal(gv,oa['v'])and np.array_equal(gf,oa['f']))
field=np.load(D/'Secondary_Restored_Point_Field.npz');attribute=go.data.attributes.get('V24_20_Height_Above_Finish_Division');got=np.array([attribute.data[int(i)].value for i in field['ids']])if attribute else np.array([])
ck('Original secondary-wall shader height field is present with the restored source values',attribute is not None and np.array_equal(got,field['values']),points=len(field['ids']))
bad=[]
for r in ch['restored_secondary_ornaments']:
 oldrow=oldindex[r['name']];olddata=np.load(W/'v26_2'/'Final'/oldrow['file']);o=bpy.data.objects[r['name']];me=o.data;me.calc_loop_triangles();verts=np.array([o.matrix_world@p.co for p in me.vertices]);faces=np.array([t.vertices[:]for t in me.loop_triangles],np.int32)
 if not np.array_equal(verts[:len(olddata['v'])],olddata['v'])or not np.array_equal(faces[:len(olddata['f'])],olddata['f']):bad.append(r['name'])
ck('Restoring the original secondary frieze leaves every existing outside-branch triangle unchanged',not bad,invalid=bad)
mp=json.loads((R/'V26_3_Secondary_Original_Photo_Mapping.json').read_text('utf8'));mapbad=[]
for row in mp['triangles']:
 face=go.data.polygons[row['triangle']];v=np.array([go.matrix_world@go.data.vertices[j].co for j in face.vertices]);uv=np.array([go.data.uv_layers.active.data[j].uv[:]for j in face.loop_indices]);pred=v@np.array(row['gradients_world'])+np.array(row['offsets_m']);mat=go.data.materials[face.material_index]
 if np.max(abs(uv-pred))>3e-5 or not mat.name.startswith('M_V26_3_Secondary_Original_Photo_'):mapbad.append(row['triangle'])
ck('Recovered secondary photograph mapping matches the original source UV coordinates',not mapbad,triangles=len(mp['triangles']),invalid=mapbad)
'''
s=s[:where]+extra+s[where:];(W/'v26_3_readback.py').write_text(s,encoding='utf8')
s=(W/'v26_2_geometry_qa.py').read_text('utf8').replace("from v26_2_common import *","from v26_2_common import *\nD=W/'v26_3'").replace('Rebuild_V26_2','Rebuild_V26_3').replace('Architecture_Complete_V26_2.blend','Architecture_Complete_V26_3.blend').replace('V26_2_Saved_Geometry_QA','V26_3_Saved_Geometry_QA').replace("HN='V26_2_House_Flush_Continuous_Finished_Shell'","HN='V26_3_House_Connected_Walls_And_Stairs'")
where=s.index("P=O/'Blender/")
extra='''
# New regressions require their own saved-surface probes; the legacy sill
# samples do not cover door transoms, upper wall closures, or room topology.
transom=[]
for fl,z0,z1 in [(1,2.16,2.99),(2,6.06,6.59)]:
 for x in np.linspace(4.2,8.8,9):
  for z in np.linspace(z0,z1,5):transom.append({'floor':fl,'x':float(x),'z':float(z),'opaque_hits':len(house.ray_cast([x,1.8,z],[x,2.6,z]))})
ck('All sampled F1 and F2 sliding-door transom glazing is unobstructed',not any(q['opaque_hits']for q in transom),samples=len(transom),invalid=[q for q in transom if q['opaque_hits']])
heads=[]
for fl,zs in [(1,[3.06,3.15,3.30]),(2,[6.66,6.8,6.90]),(3,[10.,10.1,10.2,10.28])]:
 for y in [8.05,8.55,9.05]:
  for z in zs:
   hits=house.ray_cast([12.55,y,z],[13.15,y,z]);heads.append({'floor':fl,'y':y,'z':z,'closed':bool(hits)})
ck('High-window upper wall heads close continuously to slab and hip-roof soffits',all(q['closed']for q in heads),samples=len(heads),invalid=[q for q in heads if not q['closed']])
stairheads=[]
for dz in [0.,3.6]:
 for x in [4.4,5.4,6.4,7.3]:
  for z in [3.06+dz,3.16+dz,3.30+dz]:
   for yy in [7.512,9.588]:
    hits=house.ray_cast([x,yy-.055,z],[x,yy+.055,z]);stairheads.append({'x':x,'y':yy,'z':z,'closed':bool(hits)})
ck('Both lower stair-storey wall heads are sealed below the original slabs',all(q['closed']for q in stairheads),samples=len(stairheads),invalid=[q for q in stairheads if not q['closed']])
thresholds=[]
for n in sorted(motion):
 frn=n.replace('__LEAF_Geometry','__FRAME_Geometry');a=read(frn);lo=a['v'].min(0);hi=a['v'].max(0);axis=0 if hi[0]-lo[0]<hi[1]-lo[1]else 1;other=1-axis;floor=lo[2]
 for along in np.linspace(lo[axis]-.08,hi[axis]+.08,5):
  q=(lo+hi)/2;q[axis]=along;q[other]=(lo[other]+hi[other])/2;q[2]=floor;hits=house.ray_cast(q+[0,0,.22],q-[0,0,.1]);zz=[h.position[2]for h in hits if h.normal[2]>.5];error=max(zz)-floor if zz else 999.;thresholds.append({'door':n,'point_m':q.tolist(),'surface_error_m':float(error)})
ck('Every sampled interior door threshold has continuous level floor support without a protruding block',all(abs(q['surface_error_m'])<.0005 for q in thresholds),samples=len(thresholds),invalid=[q for q in thresholds if abs(q['surface_error_m'])>=.0005])
partition=[]
for x in [9.55,9.9,10.25]:
 for z in [0.,.9,2.2]:partition.append({'x':x,'z':z,'closed':bool(house.ray_cast([x,6.9,z],[x,7.6,z]))})
ck('First-floor right room is separated from the stair-facing WC by masonry',all(q['closed']for q in partition),samples=len(partition),invalid=[q for q in partition if not q['closed']])
thickness=[]
for y in [7.8,8.3,9.1]:
 for z in [.2,1.,2.3]:
  hits=house.ray_cast([10.35,y,z],[10.95,y,z]);xx=sorted(h.position[0]for h in hits);thickness.append({'y':y,'z':z,'thickness_m':xx[-1]-xx[0]if len(xx)==2 else None})
ck('The WC internal divider retains its 100 mm thickness',all(q['thickness_m']is not None and abs(q['thickness_m']-.1)<.0006 for q in thickness),samples=thickness)
rear=[]
for y in [9.57,9.62,9.7,9.79]:
 for z in [.6,1.4,2.5]:rear.append({'y':y,'z':z,'closed':bool(house.ray_cast([10.55,y,z],[10.78,y,z]))})
ck('The 100 mm WC divider meets the rear window jamb without a reveal air gap',all(q['closed']for q in rear),samples=len(rear),invalid=[q for q in rear if not q['closed']])
rn='WINDOW_BACK_F1_3_Geometry';ra=read(rn);glassids=[i for i,m in enumerate(J[rn]['materials'])if 'glass'in m.lower()];rf=ra['f'][np.isin(ra['mi'],glassids)];rg=solid(ra['v'],rf,rn+' glass');overlap=max(0.,(rg^house).volume());ck('The rear WC jamb closes beside the original glazing without penetrating it',len(rf)>0 and overlap<.000001,glass_triangles=len(rf),glass_wall_intersection_m3=overlap,right_jamb_m=float(ra['v'][:,0].max()))
for n,axis in [('DOOR_BATH_F1_R__FRAME_Geometry',1),('DOOR_KITCHEN_F1__FRAME_Geometry',0)]:
 a=read(n);depth=float(np.ptp(a['v'][:,axis]));ck('WC frame reduced to 220 mm / '+n,abs(depth-.22)<3e-6,depth_m=depth)
for fl,head in [(1,3.05),(2,6.65)]:
 n=f'HOUSE_V22_FRONT_TRANSOM_F{fl}_Geometry';a=read(n);glass=sum(int(a['mi'][k])==J[n]['materials'].index('M_Glass_Clear')for k in range(len(a['f'])));ck('Original transom glass retained and seated under the beam F'+str(fl),glass>0 and abs(float(a['v'][:,2].max())-head)<3e-6,glass_triangles=glass,upper_frame_z_m=float(a['v'][:,2].max()))
ceilingbad=[int(k)for k in np.flatnonzero((no[:,2]<-.5)&(c[:,2]>7.05))if J[HN]['materials'][int(ha['mi'][k])]!='M_V26_3_Neutral_White_Interior_Ceiling']
ck('All downward third-floor roof and beam faces use neutral white paint',not ceilingbad,incorrect_faces=ceilingbad)
'''
s=s[:where]+extra+s[where:];s=s.replace("'door_sweep':doorstats,","'door_sweep':doorstats,'transom_glazing_samples':transom,'upper_wall_samples':heads,'stair_wall_head_samples':stairheads,'door_threshold_samples':thresholds,'f1_room_partition_samples':partition,'wc_divider_thickness':thickness,")
s=s.replace("wrong=[int(i)for i in np.flatnonzero(m)if gmat[int(gi[i])]=='M_V24_20_Continuous_AsBuilt_Perimeter']", "secondary_restored=set(json.loads((D/'Prepared_Fixtures.json').read_text('utf8'))['proof']['secondary_wall_base']['restored_triangle_indices']);wrong=[int(i)for i in np.flatnonzero(m)if int(i)not in secondary_restored and gmat[int(gi[i])]=='M_V24_20_Continuous_AsBuilt_Perimeter']")
s=s.replace('Obsolete per-vertex brick division is absent from the repaired exterior shell','Repaired gallery finish retained outside the explicitly restored original secondary screenwall')
(W/'v26_3_geometry_qa.py').write_text(s,encoding='utf8')
s=(W/'v26_2_physics_qa.py').read_text('utf8').replace('Rebuild_V26_2','Rebuild_V26_3').replace('Architecture_Complete_V26_2.blend','Architecture_Complete_V26_3.blend').replace('V26_2','V26_3')
where=s.index("w=Walker(world,(11.1,6.9,0.))")
s=s[:where]+"w=Walker(world,(10.,6.8,0.));ok,tr=go(w,(10.,8.0));traces['restored_wc_separation']=tr;ck('Restored WC front partition prevents bedroom entry through a missing wall',not ok and w.p.y<7.0,position=list(w.p))\n"+s[where:]
(W/'v26_3_physics_qa.py').write_text(s,encoding='utf8')
print('CHECK_SCRIPTS_READY')
