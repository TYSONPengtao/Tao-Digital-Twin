import json,hashlib
from pathlib import Path
import v24_qa_blender as q
O=Path('E:/jz/JIA/Rebuild_V24_05');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_05.blend'
B=Path('E:/jz/JIA/Rebuild_V24_04/Blender/Architecture_Complete_V24_04.blend')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(name,data):
 R.mkdir(parents=True,exist_ok=True);(R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
def snapshot(bpy):
 bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
 obs={o.name:{'type':o.type,'matrix':q._matrix(o.matrix_world),'parent':o.parent.name if o.parent else None,'mesh_hash':q._mesh_hash(o.data)if o.type=='MESH'else None,'animation':q._animation(o),'hide_render':o.hide_render} for o in bpy.data.objects}
 doors=sorted(o.name for o in bpy.data.objects if o.get('UE_Interaction')in ['HINGED_INWARD','SLIDING']);poses={}
 for f in [1,20,40]:
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update();poses[str(f)]={n:q._matrix(bpy.data.objects[n].matrix_world)for n in doors}
 return {'objects':obs,'materials':{m.name:q._material(m)for m in bpy.data.materials},'images':{im.name:q._image(im)for im in bpy.data.images if im.source!='VIEWER'and im.type not in ['RENDER_RESULT','COMPOSITING']},'actions':{a.name:q._action(a)for a in bpy.data.actions},'doors':doors,'door_poses':poses}
