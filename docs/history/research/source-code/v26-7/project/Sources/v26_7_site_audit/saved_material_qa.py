from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
D=Path(__file__).parent;W=D.parent
P=Path('E:/jz/JIA/Rebuild_V26_6/Blender/Architecture_Complete_V26_6.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
def snap(ob):
 me=ob.data;me.calc_loop_triangles()
 return {'v':np.array([ob.matrix_world@p.co for p in me.vertices]),'f':np.array([t.vertices[:]for t in me.loop_triangles]),'uv':np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles])if me.uv_layers.active else None,'mi':np.array([p.material_index for p in me.polygons]),'materials':[m.name for m in me.materials]}
protected={n:snap(bpy.data.objects[n])for n in bpy.data.objects.keys()if 'Secondary_Screenwall' in n and bpy.data.objects[n].type=='MESH'and not bpy.data.objects[n].hide_render}
ob=bpy.data.objects['V26_2_Continuous_Ground_And_Perimeter_Shell'];before=snap(ob);field=np.array([d.value for d in ob.data.attributes['V24_20_Height_Above_Finish_Division'].data])
def graph(g):
 return repr(([(n.name,n.bl_idname,getattr(n,'operation',None),getattr(getattr(n,'node_tree',None),'name',None),[(s.name,str(s.default_value))for s in n.inputs if hasattr(s,'default_value')])for n in g.nodes],[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in g.links]))
group_before={g.name:graph(g)for g in bpy.data.node_groups if g.name.startswith(('V26_2_Arc_','V26_2_Limewash','V26_3_Original_Secondary_Affine_'))}
P=Path('E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend');bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update();ob=bpy.data.objects['V26_2_Continuous_Ground_And_Perimeter_Shell'];result=json.loads(Path('E:/jz/JIA/Rebuild_V26_7/Reports/V26_7_Site_Material_Changes.json').read_text('utf8'));after=snap(ob);checks=[]
for k in ['v','f','mi','uv']:checks.append({'check':'Ground '+k+' unchanged','pass':bool(np.array_equal(before[k],after[k]))})
for n,a in protected.items():
 b=snap(bpy.data.objects[n]);checks.append({'check':'Protected exact '+n,'pass':all(np.array_equal(a[k],b[k])for k in a)})
checks.append({'check':'Original secondary point field unchanged','pass':bool(np.array_equal(field,np.array([d.value for d in ob.data.attributes['V24_20_Height_Above_Finish_Division'].data])))})
checks.append({'check':'Only 36 source affine triangle materials receive lower repair','pass':len(result['secondary_base_material_replacements'])==36})
checks.append({'check':'Physical photograph scales kept','pass':all(bpy.data.node_groups[n]['V26_2_Photo_Width_Metres']==w and abs(bpy.data.node_groups[n]['V26_2_Photo_Height_Metres']-h)<1e-6 for n,w,h in [('V26_2_Arc_Blue_Brick_Photo',1.6,.9),('V26_2_Arc_Dressed_Stone_Photo',3.6,.48),('V26_2_Arc_Rubble_Photo',3.2,2.3)])})
original=json.loads((W/'v26_3/Original_Secondary.json').read_text('utf8'))
checks.append({'check':'All eleven protected native objects present','pass':len(protected)==11})
checks.append({'check':'Every original shared photograph or affine brick node group unchanged','pass':all(graph(bpy.data.node_groups[n])==v for n,v in group_before.items()),'groups':len(group_before)})

def shader_at(ma,point):
 def inp(s):return val(s.links[0].from_socket)if s.links else s.default_value
 def val(s):
  n=s.node
  if n.type=='GROUP':return n.node_tree.name
  if n.type=='NEW_GEOMETRY':assert s.name=='Position';return point
  if n.type=='SEPXYZ':return inp(n.inputs[0])[{'X':0,'Y':1,'Z':2}[s.name]]
  if n.type=='MATH':
   a,b=inp(n.inputs[0]),inp(n.inputs[1])
   return {'LESS_THAN':lambda:float(a<b),'GREATER_THAN':lambda:float(a>b),'MULTIPLY':lambda:a*b,'ADD':lambda:a+b,'MAXIMUM':lambda:max(a,b)}[n.operation]()
  if n.type=='MIX_SHADER':return inp(n.inputs[2 if inp(n.inputs[0])>=.5 else 1])
  raise AssertionError((n.type,s.name))
 out=next(n for n in ma.node_tree.nodes if n.type=='OUTPUT_MATERIAL'and n.is_active_output)
 return inp(out.inputs['Surface'])

outer=bpy.data.materials['M_V26_7_Exterior_Strata_Screenwall_Only_White_Belt']
samples=[('ordinary long exterior wall',(0,-16.9,-.1),'Blue_Brick'),('curved gate approach',(-24,3,-.1),'Blue_Brick'),('ordinary west perimeter',(-15,-8,-.1),'Blue_Brick'),('main screenwall',(6,-17,-.1),'Limewash'),('original secondary',(11.5,-17,-.1),'Limewash'),('beyond original secondary',(15,-15,-.1),'Blue_Brick'),('main dressed stone',(6,-17,-.4),'Dressed_Stone'),('main rubble',(6,-17,-.9),'Rubble'),('gallery dressed stone',(15,-15,-.9),'Gallery_Stone')]
for label,point,expected in samples:
 got=shader_at(outer,point);checks.append({'check':'Saved graph branch / '+label,'pass':expected in got,'point':point,'expected':expected,'actual':got})
wrapped=bpy.data.materials[result['secondary_base_material_replacements'][0]['new']]
for label,point,expected in [('secondary original upper',(11.5,-17,2.3),'Original_Secondary_Affine'),('secondary white belt',(11.5,-17,-.1),'Limewash'),('secondary matched stone',(11.5,-17,-.4),'Dressed_Stone'),('secondary matched rubble',(11.5,-17,-.9),'Rubble'),('secondary terrace stone',(13.05,-17,-.9),'Gallery_Stone')]:
 got=shader_at(wrapped,point);checks.append({'check':'Saved affine wrapper branch / '+label,'pass':expected in got,'point':point,'expected':expected,'actual':got})
with P.open('rb')as fp:sha=hashlib.file_digest(fp,'sha256').hexdigest()
fail=[q for q in checks if not q['pass']]
report={'model_sha256':sha,'status':'PASS'if not fail else'FAIL','verified_saved_recipe':True,'source_model_saved_or_changed':False,'checks':checks,'failures':fail,'applied_recipe':result}
Path('E:/jz/JIA/Rebuild_V26_7/Reports/V26_7_Site_Material_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('MATERIAL_RECIPE_TEST',report['status'],len(checks),len(fail),flush=True)
