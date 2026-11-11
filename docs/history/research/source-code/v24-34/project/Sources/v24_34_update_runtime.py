from pathlib import Path
import bpy,hashlib,json
from mathutils import Vector
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V24_34');P=O/'Blender/Architecture_Complete_V24_34.blend';bpy.ops.wm.open_mainfile(filepath=str(P))
for text,fn in [('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py')]:
 code=(W/('v24_34_'+fn)).read_text('utf8');compile(code,fn,'exec');bpy.data.texts[text].clear();bpy.data.texts[text].write(code);(O/'Roam'/fn).write_text(code,encoding='utf8')
c=bpy.data.objects['V24_34_03_Added_South_Road'];c.location=(-49.,-45.,-10.04);c.rotation_euler=(Vector((-40.,-44.5,-10.4))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=24
bpy.context.scene.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
r=json.loads((O/'Reports/V24_34_Build.json').read_text());r['sha256']=h;r['physics']='9 support rays and exact low sphere seating against walkable real triangles; finite edge stop and last safe recovery';(O/'Reports/V24_34_Build.json').write_text(json.dumps(r,indent=2));print('RUNTIME_SAVED',h,flush=True)
