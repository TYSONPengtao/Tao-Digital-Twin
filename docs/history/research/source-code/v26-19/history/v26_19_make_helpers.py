from pathlib import Path
W=Path(__file__).parent
for name in['build','build_fast','fast_display','verify_fast','physics_qa','native_qa','run_checks']:
 s=(W/('v26_18_'+name+'.py')).read_text('utf8').replace('v26_18','v26_19').replace('V26_18','V26_19').replace('V26.18','V26.19')
 if name=='build':
  s=s.replace('v26_17','v26_18').replace('V26_17','V26_18').replace('V26.17','V26.18');needle="for r in prep['objects']:";block="""for mat in prep.get('new_materials',[]):
 m=bpy.data.materials.get(mat['name'])or bpy.data.materials.new(mat['name']);m.use_nodes=True;m.diffuse_color=mat['color'];bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat['color'];bs.inputs['Roughness'].default_value=mat['roughness']
""";s=s.replace(needle,block+needle,1)
  s='\n'.join("note=bpy.data.texts.new('V26_19_梁端窗角与院内构件');note.write('按相邻墙身和原梁截面清理旧屋顶封口与装饰包边，梁芯保留，西侧窗边柱身恢复连续原矩形截面。移除早期推定的阳台雨水支管，罗马柱保留；按用户确认移除院内红圈占位花盆。前版楼梯板底、白色平台侧面及内门后部修正保留，窗扇动作与阴天柔光保持。')"if l.startswith('note=bpy.data.texts.new(')else l for l in s.splitlines())+'\n';s=s.replace('V26_19_Stair_Soffit_And_Gate_Rear','V26_19_Clean_Beam_Heads_And_Courtyard_Fixtures')
 if name=='native_qa':s=s.replace('Rear fixed decorative panels have no visible or rendered surface','Previously removed rear gate panels remain hidden').replace('Current collision contains repaired house and excludes the removed rear gate panels','Current collision contains corrected meshes and excludes the archived original fixtures')
 (W/('v26_19_'+name+'.py')).write_text(s,'utf8')
perf=W/'v26_19_perf';perf.mkdir(exist_ok=True);(perf/'roam_controller_fast.py').write_text((W/'v26_18_perf/roam_controller_fast.py').read_text('utf8').replace('V26.18','V26.19'),'utf8');print('HELPERS_CREATED')
