"""Fresh .blend readback, real-material render only, no mesh-format export."""
import bpy,json,sys,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_qa_blender import validate_v24
O=Path('E:/jz/JIA/Rebuild_V24');P=O/'Blender/Architecture_Complete_V24.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene
base=json.loads((O/'Reports/Baseline_V23_Snapshot.json').read_text(encoding='utf8'));qa=validate_v24(bpy,base,O/'Reports');qa['model_sha256']=hashlib.file_digest(P.open('rb'),'sha256').hexdigest();qa['model']=str(P);(O/'Reports/V24_Fresh_Blend_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
try:sc.render.engine='CYCLES'
except TypeError:pass
sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
views=[('V24_Gate_Front_Real_Materials','V24_Inner_Gate_Real_Materials',20),('V24_Gate_Carving_Closeup','V23_Gate_Carved_Corner',40),('V24_Gate_Roof_Sculpt','V23_Gate_Roof_Oblique',40),('V24_Gate_Courtyard_Soffit','V23_Gate_Underside_Courtyard',40)]
for label,name,frame in views:
 sc.frame_set(frame);sc.camera=bpy.data.objects[name];sc.render.filepath=str(O/'Reports'/f'{label}.png');bpy.ops.render.render(write_still=True);print('V24 MATERIAL RENDER',label,flush=True)
(O/'Reports/V24_Preview_States.json').write_text(json.dumps({'model_sha256':qa['model_sha256'],'geometry':'Fresh saved V24 Blender scene','materials':'Original real-material shader graphs; zero clay override','views':[{'file':l+'.png','camera':n,'frame':f} for l,n,f in views],'saved_default_frame':40,'runtime_UE_tested':False},ensure_ascii=False,indent=2),encoding='utf8')
print('V24 FRESH READBACK AND COLOR VIEWS COMPLETE',flush=True)
