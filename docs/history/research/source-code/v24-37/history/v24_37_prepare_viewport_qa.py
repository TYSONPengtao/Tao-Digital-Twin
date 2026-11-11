from pathlib import Path
W=Path(__file__).parent;s=(W/'v24_34_viewport_qa.py').read_text('utf8').replace('Rebuild_V24_34','Rebuild_V24_37').replace('V24_34_Viewport','V24_37_Viewport')
start=s.index('jobs=[');end=s.index('\n',start);s=s[:start]+"jobs=[('V24_35_01_Kitchen_East','A'),('V24_35_01_Kitchen_East','B'),('V24_37_02_House_And_PTJIA6','A'),('V24_37_02_House_And_PTJIA6','B'),('V24_37_04_PTJIA6_Road_Eye','A'),('V24_37_05_PTJIA6_Field_Context','A')]"+s[end:];s=s.replace("bpy.data.objects['V24_34_'+tag]","bpy.data.objects[tag]").replace('space.clip_end=300.','space.clip_end=2000.')
compile(s,'v24_37_viewport_qa.py','exec');(W/'v24_37_viewport_qa.py').write_text(s,encoding='utf8')
