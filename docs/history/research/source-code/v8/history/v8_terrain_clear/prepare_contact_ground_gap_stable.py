"""Controlled provisional terrain grades over exactly four final V8 projection gaps. Read-only to model."""
from pathlib import Path
p=Path(__file__).with_name('prepare_contact_ground_gap.py');prefix=p.read_text(encoding='utf-8-sig').split('tri=[];uv=[];mat=[];fromids=[]')[0];exec(compile(prefix,str(p),'exec'))
from shapely.geometry import box,LineString
# Measured source has three near-horizontal elevation groups separated by inferred terraces.
BREAKS=[-4.78,-4.45];groups=[base_tri[base_tri.mean(1)[:,2]<-2.9],base_tri[(base_tri.mean(1)[:,2]>=-2.9)&(base_tri.mean(1)[:,2]<-1.8)],base_tri[base_tri.mean(1)[:,2]>=-1.8]];gxy=[];gtrees=[]
for t in groups:
 assert len(t)>0;q=t.copy();q[:,:,2]=0;gxy.append(q);gtrees.append(cKDTree(t[:,:,:2].mean(1)))
def group_height(xy,grade):
 if grade<0:return height(xy)
 xy=np.asarray(xy);t=groups[grade];tt=gxy[grade];tree=gtrees[grade];k=min(32,len(t));_,ii=tree.query(xy,k=k);ii=np.asarray(ii).reshape(len(xy),k);query=np.repeat(np.c_[xy,np.zeros(len(xy))],k,axis=0);_,w,dist=closest_on_triangles(query,tt[ii].reshape(-1,3,3));dist=dist.reshape(-1,k);w=w.reshape(-1,k,3);pick=dist.argmin(1);j=np.arange(len(xy));return (w[j,pick]*t[ii[j,pick],:,2]).sum(1)
tri=[];uv=[];mat=[];fromids=[]
for j in np.flatnonzero(earth):
 for tt in clipped(gt[j],G):
  if np.linalg.norm(np.cross(tt[1]-tt[0],tt[2]-tt[0]))<1e-9:continue
  _,bw,_=closest_on_triangles(tt,np.repeat(gt[j][None,:,:],3,axis=0));tri.append(tt);uv.append(bw@gu[j]);mat.append(r['materials'][int(mid[j])]);fromids.append(int(j))
measured_cov=shapely.union_all(shapely.polygons(np.array(tri)[:,:,:2])) if tri else Polygon();missing=G.difference(measured_cov);fill=[];filluv=[];grades=[];step=.075
regions=[(-1,missing.intersection(box(-100,-100,10,100))),(0,missing.intersection(box(10,-100,100,BREAKS[0]))),(1,missing.intersection(box(10,BREAKS[0],100,BREAKS[1]))),(2,missing.intersection(box(10,BREAKS[1],100,100)))]
for grade,region in regions:
 if region.is_empty:continue
 b=region.bounds
 for x in np.arange(math.floor(b[0]/step)*step,b[2]+step,step):
  for y in np.arange(math.floor(b[1]/step)*step,b[3]+step,step):
   cell=Polygon([(x,y),(x+step,y),(x+step,y+step),(x,y+step)]).intersection(region)
   for pp in polys(cell):
    if pp.area<1e-10:continue
    for xy in polygon_tris(pp):
     tt=np.c_[xy,group_height(xy,grade)];n=np.cross(tt[1]-tt[0],tt[2]-tt[0])
     if np.linalg.norm(n)<1e-9:continue
     if n[2]<0:tt=tt[[0,2,1]]
     fill.append(tt);filluv.append(tt[:,:2]);grades.append(grade)
# Add inferred vertical earth risers; ends use the exact same horizontal mesh edge vertices.
riser_count=0;top_tri=np.array(fill)
for j,y in enumerate(BREAKS):
 line=G.intersection(LineString([[10,y],[100,y]]));segs=[line] if line.geom_type=='LineString' else [s for s in getattr(line,'geoms',[]) if s.geom_type=='LineString']
 for seg in segs:
  if seg.is_empty:continue
  xx=np.array(seg.coords)[:,0];vals=top_tri[:,:,:2].reshape(-1,2);xvals=np.unique(np.r_[xx,vals[(abs(vals[:,1]-y)<1e-8)&(vals[:,0]>=xx.min()-1e-8)&(vals[:,0]<=xx.max()+1e-8),0]]);coords=np.c_[xvals,np.full(len(xvals),y)];zl=group_height(coords,j);zh=group_height(coords,j+1)
  for k in range(len(coords)-1):
   a=np.r_[coords[k],zl[k]];b=np.r_[coords[k+1],zl[k+1]];c=np.r_[coords[k+1],zh[k+1]];d=np.r_[coords[k],zh[k]]
   for tt in [np.array([a,b,c]),np.array([a,c,d])]:
    if np.linalg.norm(np.cross(tt[1]-tt[0],tt[2]-tt[0]))<1e-9:continue
    fill.append(tt);filluv.append(tt[:,[0,2]]);grades.append(10+j);riser_count+=1
rows=[]
def save(name,tri,uv,mat,role,confidence):
 if not tri:return
 v=np.array(tri).reshape(-1,3);f=np.arange(len(v),dtype=np.int32).reshape(-1,3);ms=list(dict.fromkeys(mat));mi=np.array([ms.index(m) for m in mat],np.int32);fn=name+'.npz';np.savez_compressed(D/fn,vertices=v,faces=f,uv=np.array(uv).reshape(-1,2),material_ids=mi)
 rows.append({'index':0,'file':fn,'name':name,'element':{'name':name,'layer':'60_SITE','family':'SITE_MODEL','source':'Original measured ground UV clipped to actual four gaps' if confidence=='HIGH' else 'Provisional three terrace grades from nearby Base3 measured low terrain; grades/risers not field-controlled','confidence':confidence,'role':role,'survey_status':'SOURCE_TRIANGLES' if confidence=='HIGH' else 'INFERRED_GRADE_BREAKS_REQUIRE_FIELD_CHECK'},'materials':ms,'triangles':len(f),'vertices':len(v),'role':role,'photo_triangles':len(f) if confidence=='HIGH' else 0})
save('V8_CONTACT_GAP_MEASURED_GROUND',tri,uv,mat,'FINAL_LOCAL_CONTACT_GROUND_ONLY_ORIGINAL_SOURCE_UV','HIGH');save('V8_CONTACT_GAP_INTERPOLATED_GROUND',fill,filluv,['M_V8_West_Earth']*len(fill),'FINAL_LOCAL_CONTACT_GROUND_ONLY_PROVISIONAL_TERRACE_GRADES','MEDIUM');np.savez_compressed(D/'Ground_Support_And_Donor_Indices.npz',support=support,donor_triangle_indices=np.array(fromids,int),base3_support_triangles=base_tri,grade_ids=np.array(grades,int),grade_break_y_local=np.array(BREAKS))
combined=np.concatenate([np.array(a).reshape(-1,3,3) for a in [tri,fill] if len(a)]);ar=np.abs(np.cross(combined[:,1,:2]-combined[:,0,:2],combined[:,2,:2]-combined[:,0,:2]));cov=shapely.union_all(shapely.polygons(combined[ar>1e-11,:,:2]));res=G.difference(cov).area;over=cov.difference(G).area;assert res<1e-6;assert over<1e-9;assert combined[:,:,2].max()<.08
qa={'status':'PASS_STABLE_PROVISIONAL_TERRAIN_CANDIDATE','input_residual_area_m2':G.area,'significant_polygons_only':4,'measured_ground_area_m2':measured_cov.area,'provisional_graded_ground_area_m2':missing.area,'measured_triangles':len(tri),'inferred_ground_and_riser_triangles':len(fill),'inferred_vertical_earth_riser_triangles':riser_count,'ground_support_points':len(support),'measured_base3_ground_support_triangles':len(base_tri),'nominal_ground_grid_m':step,'inferred_grade_breaks_y_local_m':BREAKS,'grade_support_triangles':[len(t) for t in groups],'output_ground_elevation_range_local_m':[float(combined[:,:,2].min()),float(combined[:,:,2].max())],'output_residual_m2':res,'output_outside_gap_m2':over,'existing_base_low_ground_coverage_m2':0.,'actual_source_contact_samples':0,'source_uv_only_measured_faces':True,'existing_base_and_model_files_modified':False,'dropped_numerical_slivers_m2':.31034868342669475-G.area,'limits':['East gaps have no direct existing source ground contact; nearby low-terrain samples lie 0.13 to 0.40m away in XY.','The three grade breaks and their risers are inferred to avoid large triangles crossing the observed elevation groups; their exact positions and heights require field control.','Original source-photo UV is assigned only to the 3 directly supported source-ground triangles. Provisional terraces use soil material.','No construction centimeter accuracy or measured seam matching is claimed. Native/export validation remains parent task.']}
(D/'Candidate_Patch_Index_Rows.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');(D/'Contact_Gap_Ground_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(qa,ensure_ascii=False,indent=2))
