exec((__import__('pathlib').Path(__file__).parent/'v25_clean_coplanar_backfaces.py').read_text('utf8').split("assert not (D/'Coplanar_Cleanup.json')")[0])
# Final pass against the continuous dark foundation skin from the adjacent
# source component. Remove only complete duplicate white foot triangles.
old_report=json.loads((D/'Coplanar_Cleanup.json').read_text('utf8'));meshes=[];target=None;cover=[]
for row in idx:
 is_target=row['source_object']==name and row['material'].endswith('::M_V24_11_Plain_White_Limewash')
 is_cover=row['source_object']=='SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry' and row['material'].endswith('::M_V24_18_Continuous_Dark_Courses')
 if not(is_target or is_cover):continue
 data=Path(row['file']).read_bytes();_,nv,nf=struct.unpack_from('<III',data,4);off=16+nv*44;v=np.frombuffer(data,'<f8',nv*3,16).reshape(-1,3);f=np.frombuffer(data,'<i4',nf*3,off).reshape(-1,3);tri=v[f];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(normal,axis=1)/2;normal/=np.linalg.norm(normal,axis=1)[:,None]
 if is_target:target=(row,data,nv,nf,off,v,f,tri,normal,area)
 else:cover.append((tri,normal))
row,data,nv,nf,off,v,f,tri,n,area=target;ct=np.concatenate([c[0]for c in cover]);cn=np.concatenate([c[1]for c in cover]);remove=[];proof=[]
for i in np.flatnonzero((np.abs(n[:,0])>.8)&(tri[:,:,2].max(1)<-.34)&(tri[:,:,0].min(1)>12)&(tri[:,:,0].max(1)<14.3)):
 t=tri[i];normal=n[i];coplanar=np.abs(np.einsum('fvi,i->fv',ct-t[0],normal)).max(1)<2e-6;parallel=np.abs(cn@normal)>.999999;axis=int(np.argmax(abs(normal)));axes=[k for k in range(3)if k!=axis];poly=Polygon(t[:,axes]);polys=[Polygon(q[:,axes]) for q in ct[coplanar&parallel]]
 if not polys:continue
 remainder=poly.difference(unary_union(polys)).area
 if remainder<=max(1e-10,poly.area*1e-5):remove.append(int(i));proof.append({'face_before_final_pass':int(i),'area_m2':float(area[i]),'uncovered_fraction':float(remainder/max(poly.area,1e-20)),'covered_by':'SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry::M_V24_18_Continuous_Dark_Courses','coplanarity_tolerance_m':2e-6})
assert remove,'No fully covered wall-foot duplicates found';keep=np.ones(nf,bool);keep[remove]=False;faces=f[keep].astype('<i4');oldhash=row['sha256'];p=Path(row['file']);new=b'R25M'+struct.pack('<III',1,nv,len(faces))+data[16:off]+faces.tobytes();p.write_bytes(new);row['sha256']=hashlib.sha256(new).hexdigest();row['triangles']=len(faces);row['area_m2']=float(area[keep].sum());row['geometry_method']+='; complete duplicate white wall-foot faces covered by the original continuous dark-course skin removed; retained surface information unchanged.'
old_report['faces_removed']+=len(remove);old_report['final_pass_faces_removed']=len(remove);old_report['final_pass_original_geometry_sha256']=oldhash;old_report['clean_geometry_sha256']=row['sha256'];old_report['coverage_proof'].extend(proof);old_report['status']='PASS_COPLANAR_COVERED_INTERNAL_FACE_CLEANUP'
for p in [D/'Coplanar_Cleanup.json',O/'Reports/V25_Coplanar_Cleanup_QA.json']:p.write_text(json.dumps(old_report,ensure_ascii=False,indent=2),encoding='utf8')
(D/'Export_Index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf8');r=json.loads((D/'Export_Report.json').read_text('utf8'));r['export_triangles']=sum(x['triangles']for x in idx);r['coplanar_internal_backfaces_removed']=old_report['faces_removed']
for p in [D/'Export_Report.json',O/'Reports/V25_Blender_Export_QA.json']:p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print('COVERED_FOOT_DUPLICATES_REMOVED',len(remove),'total',old_report['faces_removed'],flush=True)
