from pathlib import Path
W=Path(__file__).parent
s=(W/'export_v6_native.py').read_text(encoding='utf-8').replace('Rebuild_V6_Hybrid','Rebuild_V7_Hybrid').replace('Reality_Hybrid_V6','Reality_Hybrid_V7').replace('V5 patch definition','V7 corrected patch definition').replace('V5_REBUILT','V7_REBUILT').replace('Original five embedded photos and added four original donor photos','Original five embedded photos, four original donor photos and a directly referenced DJI gable image')
(W/'export_v7_native.py').write_text(s,encoding='utf-8')
s=(W/'align_editable_rhino_v6.py').read_text(encoding='utf-8').replace('Rebuild_V6_Hybrid','Rebuild_V7_Hybrid').replace("V5=Path(r'E:\\jz\\JIA\\Rebuild_V5')","V5=O/'08_Editable_Source'").replace('Architecture_Edit_V5_ALIGNED_ENU','Architecture_Edit_V7_ALIGNED_ENU').replace('Reality_Hybrid_V6','Reality_Hybrid_V7').replace('V5 LOCAL','V7 LOCAL').replace('Editable_Rhino_Alignment_QA','Editable_Rhino_Alignment_QA').replace('Source_V5_untouched','source_v5_untouched')
(W/'align_editable_rhino_v7.py').write_text(s,encoding='utf-8')
s=(W/'blender_v6_hybrid.py').read_text(encoding='utf-8').replace('Rebuild_V6_Hybrid','Rebuild_V7_Hybrid').replace('Reality_Hybrid_V6','Reality_Hybrid_V7').replace('V6 textured','V7 corrected').replace("cameras=[('Hybrid_Whole_Site',[54,-68,56],[0,0,3],54),('Hybrid_Top',[5,-12,85],[4,-5,0],48),('Hybrid_Building',[25,-24,18],[5,3,6],58)]","cameras=[('V7_Whole_Site',[54,-68,56],[0,0,3],54),('V7_Building',[25,-24,18],[5,3,6],58),('V7_Closed_Gable',[6.5,-12,8.8],[6.5,0,7.6],43),('V7_Terrace_Door',[-4,4.4,10.5],[3.5,7.7,8.7],65),('V7_F2_Stair_Wall',[6.4,5.5,6.3],[6.4,7.3,5.5],60),('V7_Individual_Tiles',[10.1,-.9,14.0],[8.2,3.0,11.0],58)]").replace("bpy.data.objects['Hybrid_Whole_Site']","bpy.data.objects['V7_Whole_Site']")
(W/'blender_v7_hybrid.py').write_text(s,encoding='utf-8')
# Read-only source cut-rim checker, rerun against V7.
s=(W/'v6_alignment_audit/check_rim_3d_v6.py').read_text(encoding='utf-8').replace('Rebuild_V6_Hybrid','Rebuild_V7_Hybrid')
(W/'v6_alignment_audit/check_rim_3d_v7.py').write_text(s,encoding='utf-8')
print('V7 export/align/render/rim scripts prepared',flush=True)
