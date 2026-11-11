from pathlib import Path
W=Path(__file__).parent
p=W/'export_v9_native.py';s=p.read_text(encoding='utf-8')
s=s.replace("matids={m.Name:m.Index for m in F.Materials}","matids={m.Name:i for i,m in enumerate(F.Materials)}")
s=s.replace("vi.Name='Hybrid_Whole_Site'","vi.Name='V9_Whole_Site'")
s=s.replace("F.Strings['SourceBase']='../01_Source/Pure_Site_WORKING_V8.3dm'","F.Strings['SourceBase']='../01_Source/Pure_Site_WORKING_V8.3dm';F.Strings['V9Baseline']='../01_Source/V8_Current_Before_V9.3dm'")
s=s.replace("F.Strings['PatchScope']='V8 original missing-area plus explicitly authorized west terrain clearance and local roof/column repair regions'","F.Strings['PatchScope']='V9 local kitchen/gate terminal roof joint and visible eave layers; all other current V8 geometry, source photos and user-deleted 3F beam preserved'")
p.write_text(s,encoding='utf-8')
p=W/'build_v9_patch.py';s=p.read_text(encoding='utf-8').replace('Regenerate V7 changed nodes only; inherit V6 base, ground, rim, UV intact.','Regenerate V9 changed roof nodes only; inherit current V8 base, ground, rim and UV intact.')
s=s.replace('V9_CORRECTED_GEOMETRY_ONLY_INSIDE_MISSING_AREA','V9_LOCAL_EAVE_JOINT_REPAIR').replace('Patch_Incremental_Revision_V8.json','Patch_Incremental_Revision_V9.json').replace('Patch V7 done','Patch V9 done')
p.write_text(s,encoding='utf-8')
p=W/'align_editable_rhino_v9.py';s=p.read_text(encoding='utf-8').replace("['60_SITE','99_HELPER','90_UNCERTAIN','01_GRID','02_LEVEL']","['99_HELPER','90_UNCERTAIN','01_GRID','02_LEVEL']")
s=s.replace('Original V5 site retained hidden for reference; hybrid file governs final source preservation and patch scope.','Site components visible for editing the V9 eave joint; hybrid file governs final source preservation and patch scope.')
p.write_text(s,encoding='utf-8')
s=(W/'blender_v8_hybrid.py').read_text(encoding='utf-8').replace('Rebuild_V8_Hybrid','Rebuild_V9_Hybrid').replace('Reality_Hybrid_V8','Reality_Hybrid_V9').replace('localized V8 terrain/roof contact edits','inherited V8 authorized terrain clearance; V9 only local kitchen/gate terminal roof joint').replace('V8 corrected','V9 corrected')
start=s.index('cameras=[');end=s.index('for name,pos,tar,fov in cameras:',start)
s=s[:start]+"cameras=[('V9_Whole_Site',[54,-68,56],[0,0,3],54),('V9_Gate_Kitchen_Joint',[3.1,-14.8,8.1],[8.7,-11.5,3.8],60),('V9_Gate_Front',[2,-24,5.6],[7,-11.4,3.9],60),('V9_Joint_Underside',[8.7,-13.8,2.05],[8.1,-11.3,3.3],70)]\n"+s[end:]
s=s.replace("bpy.data.objects['V8_Whole_Site']","bpy.data.objects['V9_Whole_Site']")
# Export operators may rewrite image paths; restore source paths between exports.
needle="bpy.ops.export_scene.fbx(filepath="
pos=s.index(needle)
s=s[:pos]+"image_paths={im.name:im.filepath for im in bpy.data.images if im.source=='FILE'}\ndef restore_image_paths():\n for name,path in image_paths.items():bpy.data.images[name].filepath=path\n"+s[pos:]
s=s.replace("bpy.ops.export_scene.gltf(filepath=","restore_image_paths()\nbpy.ops.export_scene.gltf(filepath=").replace("bpy.ops.wm.obj_export(filepath=","restore_image_paths()\nbpy.ops.wm.obj_export(filepath=")
s=s.replace("sc.render.engine='CYCLES'","restore_image_paths()\nsc.render.engine='CYCLES'")
s=s.replace("pl.location=[6.4,5.8,6.8]","pl.location=[8.5,-12.6,2.4];pl['Role']='Inspection light added after exchange export, not an as-built fixture'")
(W/'blender_v9_hybrid.py').write_text(s,encoding='utf-8')
s=(W/'finalize_v8_views.py').read_text(encoding='utf-8').replace('Rebuild_V8_Hybrid','Rebuild_V9_Hybrid').replace('Reality_Hybrid_V8','Reality_Hybrid_V9')
start=s.index('cams=[');end=s.index('for name,pos,tar in cams:',start)
s=s[:start]+"cams=[('V9_Gate_Kitchen_Joint',[3.1,-14.8,8.1],[8.7,-11.5,3.8]),('V9_Gate_Front',[2,-24,5.6],[7,-11.4,3.9]),('V9_Joint_Underside',[8.7,-13.8,2.05],[8.1,-11.3,3.3])]\n"+s[end:]
# Give Rhino an immediately useful joint review viewport while retaining named whole-site views.
s=s.replace("assert F.Write(str(p),8)","for vi in F.Views:\n if vi.Name=='V9_Whole_Site':\n  pos=enu([3.1,-14.8,8.1]);tar=enu([8.7,-11.5,3.8]);vi.Viewport.SetCameraLocation(rh.Point3d(*pos));vi.Viewport.SetCameraDirection(rh.Vector3d(*[b-a for a,b in zip(pos,tar)]));vi.Name='V9_Gate_Kitchen_Joint_Review'\nassert F.Write(str(p),8)")
(W/'finalize_v9_views.py').write_text(s,encoding='utf-8')
print('Configured native, editable, Blender and review views for V9',flush=True)
