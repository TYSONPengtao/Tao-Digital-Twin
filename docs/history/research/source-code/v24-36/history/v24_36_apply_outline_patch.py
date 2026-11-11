from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_36';O=Path('E:/jz/JIA/Rebuild_V24_36');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_36.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);patch=json.loads((D/'Outline_Patch.json').read_text())
for r in patch['changed']:
 o=bpy.data.objects[r['name']];a=np.load(D/r['file']);me=bpy.data.meshes.new(r['name']+'_Filled_Outline_Cut');me.from_pydata(a['v'],[],a['f']);me.polygons.foreach_set('material_index',a['mi']);me.update();u=me.uv_layers.new(name='PTJIA6_Original_Photo_UV');u.data.foreach_set('uv',a['uv'].astype(np.float32).ravel())
 for m in o.data.materials:me.materials.append(m)
 o.data=me;o['Filled_Current_Outline_Exclusion']=True
for n in patch['remove']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
a=np.load(D/'Final_Collision.npz');cache=bpy.data.objects['V24_21_Navigation_Collision'];me=bpy.data.meshes.new('V24_36_Current_Outline_Protected_Collision');me.from_pydata(a['v'],[],a['f']);me.update();cache.data=me;cache['PTJIA6_Internal_Scan_Gaps_Excluded']=True
txt=bpy.data.texts['V24_21_漫游控制器.py'];code=txt.as_string();presets=json.loads((D/'New_Roam_Presets.json').read_text());line=next(s for s in code.splitlines()if s.startswith('PRESETS='));new=line+'\nPRESETS.update('+repr({k:tuple(v)for k,v in presets.items()})+')';code=code.replace(line,new);needle="  row=L.row();row.operator('arch_roam.measure_mode',text='测长度 / L').mode='LENGTH'";replacement="  row=L.row()\n  for key,label in [('PTJIA6_ROAD','PTJIA6道路'),('PTJIA6_FIELD','PTJIA6地块')]:row.operator('arch_roam.preset',text=label).location=key\n"+needle;assert needle in code;code=code.replace(needle,replacement);compile(code,'roam_controller.py','exec');txt.clear();txt.write(code);(O/'Roam/roam_controller.py').write_text(code,encoding='utf8')
col=bpy.data.collections['V24_36_PTJIA6_仅补充缺失外景'];road=np.array(presets['PTJIA6_ROAD']);field=np.array(presets['PTJIA6_FIELD']);newviews=[('04_PTJIA6_Road_Eye',road+np.array([0,0,1.53]),road+np.array([-4,15,1.4]),24),('05_PTJIA6_Field_Context',field+np.array([-20,-25,25]),field,30)]
views=json.loads((D/'Views.json').read_text())
for tag,pos,aim,lens in newviews:
 c=bpy.data.objects.new('V24_36_'+tag,bpy.data.cameras.new('V24_36_'+tag));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.03;c.data.clip_end=2000;views.append([tag,list(pos),list(aim),lens])
(D/'Views.json').write_text(json.dumps(views));q=json.loads((R/'V24_36_Changes.json').read_text());q['added']=[n for n in q['added']if n not in patch['remove']];q['display_triangles']=patch['new_triangles'];q['internal_gap_area_protected_m2']=patch['filled_internal_gap_area_m2'];q['PTJIA6_gap_fragments_removed']=patch['remove'];(R/'V24_36_Changes.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8');q=json.loads((R/'V24_36_Collision_Index.json').read_text());q['all_triangles']=len(a['f']);q['vertices']=len(a['v']);q['internal_gap_faces_trimmed']=patch['collision_trim_candidates'];(R/'V24_36_Collision_Index.json').write_text(json.dumps(q,indent=2));clip=json.loads((D/'Clip_Report.json').read_text());clip['added_triangles']=patch['new_triangles'];clip['added_tiles']=len(json.loads((D/'Final_Exterior_Index.json').read_text()));clip['existing_protected_footprint_m2']+=patch['filled_internal_gap_area_m2'];clip['internal_gaps_are_protected_not_import_regions']=True;(D/'Clip_Report.json').write_text(json.dumps(clip,indent=2))
for name in ['Existing_Coverage.geojson','Clip_Report.json']:(O/'Source_Metadata'/name).write_bytes((D/name).read_bytes())
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
q=json.loads((R/'V24_36_Build.json').read_text());q['sha256']=h;q['filled_scan_outline_protected']=True;(R/'V24_36_Build.json').write_text(json.dumps(q,indent=2));print('V36_PATCH_SAVED',h,flush=True)
