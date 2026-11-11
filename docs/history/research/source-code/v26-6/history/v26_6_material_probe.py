from pathlib import Path
import bpy,json,sys
W=Path(__file__).parent;D=W/'v26_6';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend');s=bpy.context.scene;s.frame_set(40);bpy.context.view_layer.update();out={}
for name in ['M_Wall_Interior','M_Floor','M_V24_31_White_Painted_Ceiling','M_V26_3_Neutral_White_Interior_Ceiling','M_V24_31_Stair_Gray_Marble']:
 m=bpy.data.materials.get(name)
 if not m:continue
 r={'diffuse_color':list(m.diffuse_color),'nodes':[]}
 if m.node_tree:
  for n in m.node_tree.nodes:
   v={'name':n.name,'type':n.bl_idname,'inputs':[]}
   for p in n.inputs:
    q={'name':p.name,'linked':p.is_linked,'links':[[l.from_node.name,l.from_socket.name]for l in p.links]}
    if hasattr(p,'default_value'):
     x=p.default_value
     try:q['value']=list(x)
     except TypeError:
      if isinstance(x,(str,int,float,bool)):q['value']=x
    v['inputs'].append(q)
   if n.type=='GROUP':v['node_group']=n.node_tree.name
   r['nodes'].append(v)
 out[name]=r
out['viewports']=[{'workspace':w.name,**{key:getattr(a.spaces.active.shading,key)for key in ['light','studio_light','studiolight_rotate_z','studiolight_intensity','use_scene_world','use_scene_lights','color_type','type']}}for w in bpy.data.workspaces for a in w.screens[0].areas if a.type=='VIEW_3D']
out['available_studio_lights']=[{'name':s.name,'type':s.type}for s in bpy.context.preferences.studio_lights]
(D/'Material_Probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({n:{'diffuse':x.get('diffuse_color'),'BSDF':[k for k in x.get('nodes',[])if k['type']=='ShaderNodeBsdfPrincipled']}for n,x in out.items()if isinstance(x,dict)},ensure_ascii=False),flush=True)
