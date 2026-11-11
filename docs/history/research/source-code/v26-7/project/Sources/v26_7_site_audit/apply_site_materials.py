"""Blender build helper: call apply_site_material_repairs() after native meshes.
Never opens/saves a .blend. Does not change any geometry, UV, point attribute,
original protected secondary material, or shared photograph group.
"""
import bpy
from pathlib import Path
import json

SCREEN_BOUNDS={'x_min':3.25,'x_max':13.46,'y_min':-17.60,'y_max':-16.05}
OUTER='M_V26_2_Continuous_Exterior_Strata'
GROUND='V26_2_Continuous_Ground_And_Perimeter_Shell'

def math_node(nt,op,a=None,b=None,label=''):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op;n.label=label
 for i,value in enumerate((a,b)):
  if value is None:continue
  if isinstance(value,(int,float)):n.inputs[i].default_value=value
  else:nt.links.new(value,n.inputs[i])
 return n.outputs[0]

def mix(nt,fac,a,b,label=''):
 n=nt.nodes.new('ShaderNodeMixShader');n.label=label
 for i,value in enumerate((fac,a,b)):nt.links.new(value,n.inputs[i])
 return n.outputs[0]

def position(nt):
 g=nt.nodes.new('ShaderNodeNewGeometry');s=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(g.outputs['Position'],s.inputs[0]);return s.outputs

def group(nt,name):
 n=nt.nodes.new('ShaderNodeGroup');n.node_tree=bpy.data.node_groups[name];return n.outputs['Shader']

def lower_group(nt,name,affine,suffix):
 # Original secondary UVs use an earlier perimeter route. Preserve those for
 # its original brick finish, but register repaired lower strata to the same
 # current physical arc-length coordinates as the surrounding site shell.
 g=bpy.data.node_groups[name].copy();g.name='V26_7_Registered_Lower_'+suffix+'_'+name
 tex=g.nodes.get('Metre_Arc_Length');assert tex is not None
 geo=g.nodes.new('ShaderNodeNewGeometry');dot=g.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=affine['gradient_world'];g.links.new(geo.outputs['Position'],dot.inputs[0])
 add=g.nodes.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=affine['offset_m'];g.links.new(dot.outputs['Value'],add.inputs[0]);co=g.nodes.new('ShaderNodeCombineXYZ');g.links.new(add.outputs[0],co.inputs['X'])
 for link in list(tex.outputs['UV'].links):target=link.to_socket;g.links.remove(link);g.links.new(co.outputs[0],target)
 node=nt.nodes.new('ShaderNodeGroup');node.node_tree=g;return node.outputs['Shader']

def screen_mask(nt,xyz):
 p=SCREEN_BOUNDS
 factors=[math_node(nt,'GREATER_THAN',xyz['X'],p['x_min']),math_node(nt,'LESS_THAN',xyz['X'],p['x_max']),math_node(nt,'GREATER_THAN',xyz['Y'],p['y_min']),math_node(nt,'LESS_THAN',xyz['Y'],p['y_max'])]
 cur=factors[0]
 for q in factors[1:]:cur=math_node(nt,'MULTIPLY',cur,q)
 return cur

def apply_site_material_repairs():
 lower_map=json.loads((Path(__file__).parent/'Lower_Strata_Continuous_Arc_Mapping.json').read_text('utf8'))
 report={'white_belt_m':[-.20,.04],'screenwall_white_belt_bounds_m':SCREEN_BOUNDS,'brick_photograph_scale_m':[1.6,.9],'stone_photograph_scale_m':[3.6,.48],'rubble_photograph_scale_m':[3.2,2.3],'gallery_stone_photograph_scale_m':[3.6,.67],'objects_geometry_changed':[],'uv_changed':False,'height_point_attribute_changed':False,'shared_original_groups_changed':False}
 source=bpy.data.materials[OUTER]
 name='M_V26_7_Exterior_Strata_Screenwall_Only_White_Belt'
 assert bpy.data.materials.get(name)is None,'Apply site material helper only once.'
 new=source.copy();new.name=name;nt=new.node_tree
 # Locate the existing -0.20..0.04 white branch structurally, without names.
 candidates=[]
 for node in nt.nodes:
  if node.type!='MIX_SHADER' or not node.inputs[0].links:continue
  gate=node.inputs[0].links[0].from_node
  if gate.type=='MATH' and gate.operation=='LESS_THAN' and abs(gate.inputs[1].default_value-.04)<1e-6:candidates.append(node)
 assert len(candidates)==1,('Expected exactly one existing white belt branch',len(candidates))
 belt=candidates[0];brick=belt.inputs[1].links[0].from_socket;white=belt.inputs[2].links[0].from_socket
 xyz=position(nt);original_factor=belt.inputs[0].links[0].from_socket
 restricted_factor=math_node(nt,'MULTIPLY',original_factor,screen_mask(nt,xyz),'White belt only on actual screenwall spans')
 for link in list(belt.inputs[0].links):nt.links.remove(link)
 nt.links.new(restricted_factor,belt.inputs[0]);new['V26_7_White_Belt_Only_Screenwalls']=True
 assigned=[]
 # Use a new material in current native mesh slots: originals stay recoverable.
 for ob in bpy.data.objects:
  if ob.type!='MESH' or ob.hide_render:continue
  for k,ma in enumerate(ob.data.materials):
   if ma==source:ob.data.materials[k]=new;assigned.append({'object':ob.name,'slot':k})
 report['outer_material_replacements']=assigned
 # Restore only the explicitly wrong lower base patch. Keep every original
 # affine brick coordinate graph exactly above Z0.04 and leave all 11 source
 # secondary objects, their UVs and materials completely untouched.
 ob=bpy.data.objects[GROUND];changed=[]
 for k,ma in enumerate(ob.data.materials):
  if not ma or not ma.name.startswith('M_V26_3_Secondary_Original_Photo_'):continue
  suffix=ma.name[len('M_V26_3_Secondary_Original_Photo_'):]
  nm=ma.copy();nm.name='M_V26_7_Secondary_Registered_Lower_Strata_'+suffix;nt=nm.node_tree
  outputs=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'and n.is_active_output]
  assert len(outputs)==1
  out=outputs[0];assert len(out.inputs['Surface'].links)==1
  original=out.inputs['Surface'].links[0].from_socket
  xyz=position(nt);z=xyz['Z'];cur=original
  affine=lower_map[ma.name]
  for threshold,shader in [(.04,group(nt,'V26_2_Limewash_Band')),(-.20,lower_group(nt,'V26_2_Arc_Dressed_Stone_Photo',affine,suffix))]:
   cur=mix(nt,math_node(nt,'LESS_THAN',z,threshold),cur,shader,'Restore matching lower finish layer')
  gallery_xy=math_node(nt,'MULTIPLY',math_node(nt,'GREATER_THAN',xyz['X'],13.),math_node(nt,'LESS_THAN',xyz['Y'],-8.2))
  rubble_factor=math_node(nt,'MAXIMUM',math_node(nt,'LESS_THAN',z,-.68),math_node(nt,'MULTIPLY',gallery_xy,math_node(nt,'LESS_THAN',z,-.375)))
  cur=mix(nt,rubble_factor,cur,lower_group(nt,'V26_2_Arc_Rubble_Photo',affine,suffix),'Continuous matching rubble without duplicate shader branches')
  gallery_stone_factor=math_node(nt,'MULTIPLY',gallery_xy,math_node(nt,'LESS_THAN',z,-.375))
  gallery_stone_factor=math_node(nt,'MULTIPLY',gallery_stone_factor,math_node(nt,'GREATER_THAN',z,-1.05))
  cur=mix(nt,gallery_stone_factor,cur,lower_group(nt,'V26_2_Arc_Gallery_Stone_Photo',affine,suffix),'Match existing terrace-side stone base registration')
  for link in list(out.inputs['Surface'].links):nt.links.remove(link)
  nt.links.new(cur,out.inputs['Surface']);nm['V26_7_Source_Affine_Material']=ma.name;nm['V26_7_Original_Affine_Brick_Unchanged_Above_Z_M']=.04
  ob.data.materials[k]=nm;changed.append({'slot':k,'original':ma.name,'new':nm.name})
 report['secondary_base_material_replacements']=changed
 assert changed,'Expected original restored secondary branch material slots'
 return report
