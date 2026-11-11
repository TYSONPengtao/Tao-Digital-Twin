from pathlib import Path
W=Path(__file__).parent
s=(W/'build_v9_patch.py').read_text(encoding='utf-8').replace('Rebuild_V9_Hybrid','Rebuild_V10_Hybrid').replace('Rebuild_V8_Hybrid','Rebuild_V9_Hybrid').replace('V9','V10')
s=s.replace("P=PhotoProjector.from_objs(sorted(Path(r'E:\\jz\\JIA\\Productions\\Production_OBJ (2)\\Data').rglob('*.obj')),np.linalg.inv(T));sub={k:PhotoProjector(P.triangles[P.material_ids==k],P.uv[P.material_ids==k],P.material_ids[P.material_ids==k],P.materials) for k in P.materials}","P=None;sub={}")
start=s.index("  photo=part['material']");end=s.index('\n',start)
s=s[:start]+"  photo=False # User wall detail geometry uses measured/observed gray finishes; avoid projecting adjacent vegetation or red gate paint."+s[end:]
s=s.replace("if 'TILE' in e['name'] and e['layer']=='50_ROOF':","if P is not None and 'TILE' in e['name'] and e['layer']=='50_ROOF':")
s=s.replace('V10_LOCAL_EAVE_JOINT_REPAIR','V10_COURTYARD_WALL_DETAIL_IN_INHERITED_REPAIR_SCOPE').replace('loading photo projector','retaining original photo/UV nodes').replace('changed roof nodes','changed courtyard wall nodes')
s=s.replace("V6=Path(r'E:\\jz\\JIA\\Rebuild_V10_Hybrid')","V6=Path(r'E:\\jz\\JIA\\Rebuild_V9_Hybrid')")
(W/'build_v10_patch.py').write_text(s,encoding='utf-8')
s=(W/'export_v9_native.py').read_text(encoding='utf-8').replace('Rebuild_V9_Hybrid','Rebuild_V10_Hybrid').replace('V9','V10').replace('V8_Current_Before_V10.3dm','V9_Current_Before_V10.3dm')
s=s.replace("F.Strings['PatchScope']='V10 local kitchen/gate terminal roof joint and visible eave layers; all other current V8 geometry, source photos and user-deleted 3F beam preserved'","F.Strings['PatchScope']='V10 Chinese courtyard wall detail clipped to inherited void/contact scope; unchanged current V9 geometry and source photographs outside changed wall nodes preserved; full editable wall solids in aligned companion'")
(W/'export_v10_native.py').write_text(s,encoding='utf-8')
print('Configured V10 incremental mesh exports',flush=True)
