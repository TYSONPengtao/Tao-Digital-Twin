from pathlib import Path
import hashlib,zipfile,json,shutil,time
T=time.monotonic();W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V25');R=O/'Reports'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
build=json.loads((R/'V25_Rhino_Build_QA.json').read_text('utf8'));readback=json.loads((R/'V25_Rhino_Readback_QA.json').read_text('utf8'));comp=json.loads((R/'V25_Companion_QA.json').read_text('utf8'));desktop=json.loads((R/'V25_Rhino_Desktop_QA.json').read_text('utf8'));faces=json.loads((R/'V25_Material_Face_QA.json').read_text('utf8'))
assert readback['status'].startswith('PASS') and desktop['status'].startswith('PASS') and comp['status'].startswith('PASS');assert not readback['failures'] and not comp['failures']
assert readback['files']==build['files'],'Readback QA belongs to another file revision'
assert faces['status']=='PASS_SOURCE_MATERIAL_FACE_PARTITIONS' and faces['valid_triangles']==build['triangles'];assert desktop['object_count']==build['mesh_parts'] and desktop['mesh_triangles']==build['triangles']
for f in build['files']:assert sha(Path(f['file']))==f['sha256']
assert sha(O/'Blender/Architecture_Complete_V25.blend')==comp['model_sha256']
for c in desktop['captures']:assert Path(c['file']).stat().st_size>10000
for n in ['v25_export_blender.py','v25_build_rhino.py','v25_rhino_common.py','v25_mesh_bridge.cs','v25_verify_rhino.py','v25_verify_companion.py','v25_verify_material_faces.py','v25_clean_coplanar_backfaces.py','v25_clean_covered_wall_foot.py','v25_patch_native_local.py','v25_resume_enu.py','v25_viewport.py','v25_prepare_delivery.py','v25_finalize_texture_names.py','v25_package.py']:shutil.copy2(W/n,O/'Conversion_Source'/n)
delivery={'status':'PASS_FINAL_V25_RHINO_DELIVERY','native_kernel':build['native_kernel'],'rhino_files':build['files'],'model_type':'Independent grouped material meshes; Rhino 8 3dm','native_readback_checks':readback['total_checks'],'companion_preservation_checks':len(comp['checks']),'desktop_captures':len(desktop['captures']),'source_model_unchanged':True,'visual_review':json.loads((R/'V25_Visual_Review.json').read_text('utf8'))}
assert delivery['visual_review']['status']=='PASS_VISUAL_REVIEW';(R/'V25_Delivery_QA.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf8')
excluded={'Manifest_SHA256.json'}
used_textures={Path(t['file']).resolve() for t in json.loads((O/'Source_Metadata/Texture_Index.json').read_text('utf8'))}
files=[p for p in O.rglob('*') if p.is_file() and p.name not in excluded and not any(s.endswith('_embedded_files') or s=='__pycache__' for s in p.relative_to(O).parts) and p.suffix not in ['.rhl','.bak','.blend1','.blend2'] and not p.name.startswith('_Building') and not p.name.endswith('_Error.json') and (p.parent!=O/'Textures' or p.resolve() in used_textures)]
manifest={p.relative_to(O).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files};(O/'Manifest_SHA256.json').write_text(json.dumps({'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json');print('V25_MANIFEST_READY',len(files),flush=True)
archive=O.parent/'Rebuild_V25_Rhino_and_Safe_Roam.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=2,allowZip64=True) as z:
 for i,p in enumerate(sorted(files)):
  z.write(p,'Rebuild_V25/'+p.relative_to(O).as_posix())
  if i%500==0:print('ZIP_WRITE',i,len(files),flush=True)
print('ZIP_WRITTEN',archive.stat().st_size,flush=True)
with zipfile.ZipFile(archive) as z:
 bad=z.testzip();assert bad is None,bad
 for i,p in enumerate(files):
  entry='Rebuild_V25/'+p.relative_to(O).as_posix()
  with z.open(entry) as stream:h=hashlib.file_digest(stream,'sha256').hexdigest()
  expected=manifest.get(p.relative_to(O).as_posix(),{}).get('sha256') or sha(p);assert h==expected,entry
report={'status':'PASS_ZIP_CRC_AND_ALL_ENTRY_SHA256','archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'files':len(files),'seconds':time.monotonic()-T};(W/'v25/Archive_QA.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('V25_PACKAGE_OK',json.dumps(report),flush=True)
