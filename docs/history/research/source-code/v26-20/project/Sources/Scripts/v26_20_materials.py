import bpy
def install(prep):
 for spec in prep.get('new_materials',[]):
  if spec['kind']!='extend_stone_photo':raise ValueError(spec)
  group=bpy.data.node_groups[spec['source_group']].copy();group.name='V26_20_Storage_Stone_Photo_Continuous_Extension'
  combine=next(n for n in group.nodes if n.type=='COMBXYZ'and any(l.to_node.type=='TEX_IMAGE'for o in n.outputs for l in o.links));old=next(iter(combine.inputs['Y'].links));source=old.from_socket;group.links.remove(old);ping=group.nodes.new('ShaderNodeMath');ping.name='Continue_Vertical_Photo_Past_Old_Top';ping.operation='PINGPONG';ping.inputs[1].default_value=1.;group.links.new(source,ping.inputs[0]);group.links.new(ping.outputs[0],combine.inputs['Y'])
  mat=bpy.data.materials.new(spec['name']);mat.use_nodes=True;mat.node_tree.nodes.clear();gn=mat.node_tree.nodes.new('ShaderNodeGroup');gn.node_tree=group;out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(gn.outputs['Shader'],out.inputs['Surface']);mat['V26_20_Only_New_Storage_150mm_Extension']=True
