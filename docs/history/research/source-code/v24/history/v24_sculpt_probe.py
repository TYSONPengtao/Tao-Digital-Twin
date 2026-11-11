import sys,json
from pathlib import Path
import bpy,numpy as np
W=Path(r'C:/Users/PENG/Documents/Codex/2026-10-07/files-pasted-by-the-user-rhino/work');sys.path.insert(0,str(W))
from v24_sculpt_blender import apply_v24_sculpt
O=Path('E:/jz/JIA/Rebuild_V23')
I=json.loads((O/'02_Data/Native_Readback_Index_V23.json').read_text(encoding='utf8'))
r=next(r for r in I if r['name']=='SITE_V21_GATE_REFERENCE_LAYER_14');d=np.load(O/'02_Data'/r['file']);v=d['vertices'];f=d['faces']
me=bpy.data.meshes.new(r['name']);me.from_pydata(v.tolist(),[],f.tolist());me.update()
for n in r['materials']:
 m=bpy.data.materials.new(n);m.diffuse_color=(.32,.35,.36,1);me.materials.append(m)
me.polygons.foreach_set('material_index',d['material_ids'])
u=me.uv_layers.new(name='Native_Review_UV');u.data.foreach_set('uv',d['uv'][f.ravel()].astype(np.float32).ravel())
p=bpy.data.objects.new(r['name'],None);bpy.context.scene.collection.objects.link(p)
ob=bpy.data.objects.new(r['name']+'_Geometry',me);bpy.context.scene.collection.objects.link(ob);ob.parent=p
report=apply_v24_sculpt(bpy,W/'v24_sculpt_probe')
print(json.dumps(report,ensure_ascii=False))
