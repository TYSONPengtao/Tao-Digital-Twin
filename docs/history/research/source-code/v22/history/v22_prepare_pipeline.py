from pathlib import Path
import re
W=Path(__file__).parent
def cv(s):
 return s.replace('V21','ZZNEWZZ').replace('V20','V21').replace('ZZNEWZZ','V22').replace('v21','zznewzz').replace('v20','v21').replace('zznewzz','v22')
s=cv((W/'v21_assemble.py').read_text(encoding='utf8'))
s=s.replace('087a4457d3df7feea42503cf6ea27788fd1374e55b8d4a8dbd1853b75424d4d4','19f0c4e6a5580606fa568091be01e8954444bcbfe55f48ba7e49e6935630e02e')
s=s.replace("['house','gate','site']","['house','gate','kitchen','pavilion']")
begin=s.index("for s in list(Path('D:/Desktop/问题')")
end=s.index("for n in ['Coordinate.json'",begin)
s=s[:begin]+"shutil.copytree(Path('D:/Desktop/问题大全（每个细节）'),O/'07_Reference/V22_AsBuilt/Latest_Comparison',dirs_exist_ok=True)\n"+s[end:]
# Literal legacy node/material identifiers are preserved in the scene, irrespective
# of the pipeline version. The new door flag is deliberately also accepted.
(W/'v22_assemble.py').write_text(s,encoding='utf8')
(W/'v22_native_qa.py').write_text(cv((W/'v21_native_qa.py').read_text(encoding='utf8')),encoding='utf8')
s=(W/'v21_door_native_review.py').read_text(encoding='utf8').replace('Rebuild_V21','Rebuild_V22').replace('Index_V21','Index_V22').replace('Manifest_V21','Manifest_V22').replace('Complete_V21','Complete_V22').replace('V21_Assembly','V22_Assembly')
# Include all decorative gate nodes in collision checks, regardless of naming.
s=s.replace("and not t.startswith('SITE_V21_GATE_REFERENCE')","and not ('GATE' in t)")
(W/'v22_door_native_review.py').write_text(s,encoding='utf8')
s=cv((W/'v21_render_native.py').read_text(encoding='utf8'))
start=s.index('inspection_rows=');end=s.index('I=json.loads',start)
s=s[:start]+"for ob in bpy.data.objects:\n if ob.type=='LIGHT':ob.visible_camera=False;ob.visible_glossy=False;ob.visible_transmission=False\n"+s[end:]
# Keep actual material colors in 3DM/GLB/Blend, use a clay review override only
# for matching the user's supplied ideal-model comparison images.
s=s.replace("sc.cycles.samples=24","sc.cycles.samples=20")
start=s.index("for n in names:\n sc.camera=")
end=s.index('native_hash=',start)
s=s[:start]+"""clay=bpy.data.materials.new('V22_Comparison_Clay');clay.use_nodes=True
bs=next(n for n in clay.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.62,.65,.67,1);bs.inputs['Roughness'].default_value=.78
for n in names:
 sc.view_layers[0].material_override=clay if n.startswith('V22_') and 'Native_' not in n else None
 sc.camera=bpy.data.objects[n];sc.render.filepath=str(O/'06_Report'/f'{n}.png');bpy.ops.render.render(write_still=True);print('RENDERED',n,flush=True)
sc.view_layers[0].material_override=None
"""+s[end:]
s=s.replace("'source_coordinate_system':'LOCAL metres'","'source_coordinate_system':'LOCAL metres','comparison_material':'Clay override only for comparison images; native and GLB retain real materials'")
(W/'v22_render_native.py').write_text(s,encoding='utf8')

s=(W/'v21_merge.py').read_text(encoding='utf8').replace("W/'v21'","W/'v22'").replace('Rebuild_V20','Rebuild_V21').replace('Scene_V20','Scene_V21').replace('Manifest_V20','Manifest_V21').replace("['house','gate','site']","['house','gate','kitchen','pavilion']").replace("f'v21_{task}'","f'v22_{task}'").replace("version='V21'","version='V22'").replace("'V21 PATCH'","'V22 PATCH'")
(W/'v22_merge.py').write_text(s,encoding='utf8')
print('V22 pipeline prepared',flush=True)
