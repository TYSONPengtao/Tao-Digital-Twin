from pathlib import Path
W=Path(__file__).parent
s=(W/'blender_v9_hybrid.py').read_text(encoding='utf-8').replace('Rebuild_V9_Hybrid','Rebuild_V10_Hybrid').replace('V9','V10')
start=s.index('cameras=[');end=s.index('for name,pos,tar,fov in cameras:',start)
s=s[:start]+"cameras=[('V10_Whole_Site',[54,-68,56],[0,0,3],54),('V10_Courtyard_Corner',[4,-15,6],[.2,-10.7,2.25],48),('V10_Wall_Detail',[4,-5.8,3.7],[0,-6,2.1],48),('V10_Perimeter_Detail',[-27,1,7],[-23,1,2.6],48)]\n"+s[end:]
s=s.replace('inherited V8 authorized terrain clearance; V10 only local kitchen/gate terminal roof joint, retained original UV pixels','inherited authorized terrain clearance; V10 only wall detail patches, original UV pixels retained')
s=s.replace("pl.location=[8.5,-12.6,2.4]","pl.location=[4,-6,4]")
insert=s.index('for name,_,_,_ in cameras:')
s=s[:insert]+"""# Full native wall geometry is shown separately for construction detail review;
# the hybrid keeps the source exterior and inherited clipping scope.
fullcol=bpy.data.collections.new('FULL_EDITABLE_WALL_REVIEW_ONLY');sc.collection.children.link(fullcol)
for row in json.loads((O/'02_Data/Full_Wall_Index_V10.json').read_text(encoding='utf-8')):
 d=np.load(O/'02_Data'/row['file']);meshob(row['name'],d['vertices'],d['faces'],d['uv'],[mats[m] for m in row['materials']],d['material_ids'],fullcol)
fullcol.hide_render=True;fullcol.hide_viewport=True
"""+s[insert:]
s=s.replace("for name,_,_,_ in cameras:\n sc.camera=", "for name,_,_,_ in cameras:\n detail=name!='V10_Whole_Site';fullcol.hide_render=not detail;basecol.hide_render=detail;patchcol.hide_render=detail\n sc.camera=")
s=s.replace("sc.camera=bpy.data.objects['V10_Whole_Site'];bpy.ops.wm.save_as_mainfile", "basecol.hide_render=False;patchcol.hide_render=False;fullcol.hide_render=True;sc.camera=bpy.data.objects['V10_Whole_Site'];bpy.ops.wm.save_as_mainfile")
(W/'blender_v10_hybrid.py').write_text(s,encoding='utf-8')
print('Configured V10 hybrid and full native wall review renders',flush=True)
