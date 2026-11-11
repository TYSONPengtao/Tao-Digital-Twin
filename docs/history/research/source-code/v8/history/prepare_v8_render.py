from pathlib import Path
W=Path(__file__).parent
s=(W/'blender_v7_hybrid.py').read_text(encoding='utf-8').replace('Rebuild_V7_Hybrid','Rebuild_V8_Hybrid').replace('Reality_Hybrid_V7','Reality_Hybrid_V8').replace('V7_','V8_').replace('V7 corrected hybrid','V8 corrected hybrid')
a=s.index('cameras=[');b=s.index('\nfor name,pos,tar,fov',a)
s=s[:a]+"cameras=[('V8_Whole_Site',[54,-68,56],[0,0,3],54),('V8_West_Terrain_Only',[-8,-5,68],[-8,-2,-.3],53),('V8_Chinese_Eaves',[1,-24,7.2],[7,-13,3.7],65),('V8_Kitchen_Gate_Joint',[3.1,-14.8,8.1],[8.7,-11.7,4.2],63),('V8_Roman_Arch_Contact',[6.5,-8.8,2.8],[6.5,0,2.85],56),('V8_Stair_Right_Wall',[8.6,9.2,1.55],[5.8,9.2,2.15],78),('V8_Wall_Building_Closure',[-4,3.5,3.3],[0,1.6,1.0],55)]"+s[b:]
s=s.replace('SOURCE_REALITY_INTACT','SOURCE_REALITY_AUTHORIZED_LOCAL_DERIVATIVE').replace('Rigid ENU-to-local only; no weld, decimation, UV changes','Rigid ENU-to-local; original source preserved; localized V8 terrain/roof contact edits, retained original UV pixels')
(W/'blender_v8_hybrid.py').write_text(s,encoding='utf-8')
s=(W/'clean_v7_white_finishes.py').read_text(encoding='utf-8').replace('Rebuild_V7_Hybrid','Rebuild_V8_Hybrid').replace('Only rebuilt surfaces inside missing area; original source five meshes/materials untouched','Only rebuilt facade/column finishes; original photo pixels and retained source materials untouched, working base carries separate authorized local geometric edits')
(W/'clean_v8_white_finishes.py').write_text(s,encoding='utf-8')
s=(W/'finalize_v8_views.py').read_text(encoding='utf-8')
a=s.index('cams=[');b=s.index('\nfor name,pos,tar',a)
s=s[:a]+"cams=[('V8_Chinese_Flying_Eaves',[1,-24,7.2],[7,-13,3.7]),('V8_Kitchen_Gate_Joint',[3.1,-14.8,8.1],[8.7,-11.7,4.2]),('V8_Roman_Arch_Contact',[6.5,-8.8,2.8],[6.5,0,2.85]),('V8_Right_Wall_Stair',[8.6,9.2,1.55],[5.8,9.2,2.15]),('V8_West_Terrain_Only',[-8,-5,68],[-8,-2,-.3])]"+s[b:]
(W/'finalize_v8_views.py').write_text(s,encoding='utf-8')
print('V8 preview cameras and retained finish prepared')
