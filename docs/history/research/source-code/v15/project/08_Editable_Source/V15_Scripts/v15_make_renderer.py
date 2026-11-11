from pathlib import Path
W=Path(__file__).parent
s=(W/'v14_render_native.py').read_text(encoding='utf8').replace('Rebuild_V14','Rebuild_V15').replace('V14','V15').replace("O/'02_Data/Materials.json'","O/'02_Data/Native_Render_Materials.json'").replace("v.get('source_bitmap')","v.get('native_bitmap')").replace("v['source_bitmap']","v['native_bitmap']")
bump="""if v.get('native_bump'):
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(v['native_bump'],check_existing=True);tx.image.colorspace_settings.name='Non-Color';bn=m.node_tree.nodes.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.20;bn.inputs['Distance'].default_value=.004;m.node_tree.links.new(tx.outputs['Color'],bn.inputs['Height']);m.node_tree.links.new(bn.outputs['Normal'],bs.inputs['Normal'])
 m.diffuse_color="""
s=s.replace('m.diffuse_color=',bump).replace('Original exterior bitmap and original UV; architecture plain named-material review shading','Actual native named material bitmap and corrected mesh UV; original exterior bitmap and UV preserved')
start=s.index('cameras=[');end=s.index('\nfor name,pos,tar,fov,ortho in cameras:',start)
cams=[('V15_Native_Whole_Site',[50,-66,42],[-3,-4,2],49,None),('V15_Native_Top',[-1,-3,75],[-1,-3,0],50,64),('V15_Native_Roof_Junction',[26,-28,17],[13,-10.5,2.8],48,None),('V15_Native_Outer_Storage',[27,-24,4.8],[18,-13.2,1.2],55,None),('V15_Native_Inner_Gate',[6.55,-14.80,1.45],[6.55,-11.75,1.40],82,None),('V15_Native_Entry_Route',[-10.0,-11.22,1.30],[6.6,-11.95,1.0],63,None),('V15_Native_F3_Bedroom',[11.4,3.4,8.7],[9.3,1.35,7.75],78,None),('V15_Native_F3_Vestibule',[10.0,5.9,8.9],[9.3,7.8,8.6],90,None),('V15_Native_F3_Hall',[7.65,6.82,9],[3.1,6.8,8.15],82,None),('V15_Native_South_Wall',[16,-26,2.1],[7.5,-17,1.6],55,None)]
s=s[:start]+'cameras='+repr(cams)+s[end:]
s=s.replace("[6.55, -14.8, 1.45], [6.55, -11.75, 1.4], 82", "[6.55, -15.4, 1.8], [6.55, -11.75, 1.95], 89")
s=s.replace("sc.render.filepath=str(O/'06_Report'/f'{name}.png');bpy.ops.render.render","sc.view_settings.exposure=-.25 if 'F3_' in name else 0;sc.render.filepath=str(O/'06_Report'/f'{name}.png');bpy.ops.render.render")
s=s.replace('[[5.4,6.80,9.4],[7.7,6.82,9.4],[2.4,6.8,9.4]]','[[5.4,6.80,9.4],[7.7,6.82,9.4],[2.4,6.8,9.4],[10.6,3.4,9.8],[10.2,7.9,9.6]]')
s=s.replace("'SITE_V15_ORIGINAL_EXTERIOR'","'SITE_V14_ORIGINAL_EXTERIOR'")
s=s.replace("retained meshes verified against V13 native kernel meshes","retained geometry verified against V14 native kernel meshes")
(W/'v15_render_native.py').write_text(s,encoding='utf8')
print('renderer prepared')
