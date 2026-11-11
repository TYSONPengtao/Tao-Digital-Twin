import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_37/Blender/Architecture_Complete_V24_37.blend');sc=bpy.context.scene;allowed=set();excluded=[]
def visit(c,hidden=False):
 hidden=hidden or c.hide_render
 if not hidden:allowed.update(o.name for o in c.objects)
 for ch in c.children:visit(ch,hidden)
visit(sc.collection)
def layers(c,path=''):
 if c.exclude:print('EXCLUDE_LAYER',path+'/'+c.name,flush=True)
 for ch in c.children:layers(ch,path+'/'+c.name)
layers(bpy.context.view_layer.layer_collection)
rows=json.loads((Path(__file__).parent/'v25/Export_Index.json').read_text('utf8'));names=set(r['source_object'] for r in rows)
for name in sorted(names):
 o=bpy.data.objects[name]
 if name not in allowed:excluded.append({'name':name,'collections':[c.name for c in o.users_collection]})
print('HIDDEN_COLLECTIONS',[(c.name,c.hide_render) for c in bpy.data.collections if c.hide_render],flush=True);print('EXPORTED_BUT_RENDER_HIDDEN',json.dumps(excluded,ensure_ascii=False),flush=True)
print('WHITE_MATERIAL_CULL',[(m.name,m.use_backface_culling) for m in bpy.data.materials if 'WHITE' in m.name.upper() or 'BLUE_BRICK' in m.name.upper()],flush=True)
