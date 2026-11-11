from pathlib import Path
W=Path(__file__).parent
s=(W/'v26_7_site_audit/test_materials_blender.py').read_text('utf8')
s=s.replace("sys.path.insert(0,str(D));from apply_site_materials import apply_site_material_repairs\nresult=apply_site_material_repairs();after=snap(ob);checks=[]", "P=Path('E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend');bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update();ob=bpy.data.objects['V26_2_Continuous_Ground_And_Perimeter_Shell'];result=json.loads(Path('E:/jz/JIA/Rebuild_V26_7/Reports/V26_7_Site_Material_Changes.json').read_text('utf8'));after=snap(ob);checks=[]")
s=s.replace("'ADD':lambda:a+b}","'ADD':lambda:a+b,'MAXIMUM':lambda:max(a,b)}")
s=s.replace("'source_model_sha256':sha", "'model_sha256':sha").replace("'applied_recipe_in_memory_only':True", "'verified_saved_recipe':True")
s=s.replace("(D/'Material_Recipe_Independent_Test.json')", "Path('E:/jz/JIA/Rebuild_V26_7/Reports/V26_7_Site_Material_QA.json')")
(W/'v26_7_site_audit/saved_material_qa.py').write_text(s,'utf8')
s=(W/'v26_7_railing_audit/qa_candidate.py').read_text('utf8').replace("FD=W/'v26_6/Final'", "FD=W/'v26_7/Final'")
s=s.replace("fail=[q for q in checks if not q['pass']];out=", "actual=np.load(FD/J['V26_1_Photo_Referenced_Continuous_Wood_Railing']['file']);ck('Saved native railing matches the audited candidate',actual['v'].shape==a['v'].shape and np.max(abs(actual['v']-a['v']))<3e-6 and np.array_equal(actual['f'],a['f']) and np.array_equal(actual['mi'],a['mi']));fail=[q for q in checks if not q['pass']];out=")
s=s.replace("'source_model_sha256':rp['source_sha256']", "'source_model_sha256':rp['source_sha256'],'model_sha256':__import__('hashlib').sha256(Path('E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend').read_bytes()).hexdigest()")
s=s.replace("(D/'Railing_Candidate_QA.json')", "Path('E:/jz/JIA/Rebuild_V26_7/Reports/V26_7_Railing_Regression_QA.json')")
(W/'v26_7_railing_audit/saved_native_qa.py').write_text(s,'utf8')
print('EXTRA_CHECKS_READY')
