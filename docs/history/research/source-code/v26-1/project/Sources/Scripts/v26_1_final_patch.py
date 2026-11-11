from pathlib import Path
import bpy,numpy as np,json,hashlib,math
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_1';O=Path('E:/jz/JIA/Rebuild_V26_1');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_1.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.preferences.filepaths.save_version=0
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
site=json.loads((D/'Prepared_Site.json').read_text('utf8'));railing=json.loads((D/'Prepared_Railing.json').read_text('utf8'));ctx=json.loads((D/'Prepared_Context_Trim.json').read_text('utf8'));names=['V26_1_Courtyard_West_Wall_Single_Surface','V26_1_Secondary_Wall_Horizontal_Panel_Mouldings','V26_1_Secondary_Wall_Shallow_Ceramic_Coping','V26_1_Secondary_Wall_Cover_Tiles_And_Ends'];rows=[r for r in site['objects']if r['name']in names]+railing['objects']+[r for r in ctx['objects']if r['name'].startswith('V24_21_Exterior_')];edited=[]
for r in rows:
 o=bpy.data.objects[r['name']];a=np.load(D/r['file']);old=o.data;smooth=any(p.use_smooth for p in old.polygons);me=bpy.data.meshes.new(o.name+'_Final_V26_1');iv=o.matrix_world.inverted();me.from_pydata([iv@Vector(v)for v in a['v']],[],a['f']);o.data=me
 for mn in r['materials']:me.materials.append(bpy.data.materials[mn])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_1_Source_Metre_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel())
 if smooth or r.get('smooth_wood'):
  me.polygons.foreach_set('use_smooth',np.ones(len(me.polygons),bool))
  if r.get('smooth_wood'):
   try:me.set_sharp_from_angle(angle=math.radians(38))
   except Exception:pass
 me.update();o['V26_1_Repair']=r['reason'];edited.append(o.name);print('FINAL_INSTALLED',o.name,len(me.polygons),flush=True)
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=cache.data;me.calc_loop_triangles();v=np.array([p.co[:]for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);data=json.loads((R/'V26_1_Collision_Index.json').read_text('utf8'));vv=[];ff=[];ci=[]
for r in data['objects']:
 n=r['name'];start=len(vv);first=len(ff)
 if n in edited:
  o=bpy.data.objects[n];m=o.data;m.calc_loop_triangles();nv=np.array([o.matrix_world@p.co for p in m.vertices]);nf=np.array([t.vertices[:]for t in m.loop_triangles])
 else:
  fs=f[r['first_triangle']:r['first_triangle']+r['triangles']];ids,ix=np.unique(fs.ravel(),return_inverse=True);nv=v[ids];nf=ix.reshape(-1,3)
 vv.extend(nv);ff.extend(nf+start);ci.append(dict(r,first_triangle=first,triangles=len(nf)))
me=bpy.data.meshes.new('V26_1_Final_Collision');me.from_pydata(vv,[],ff);me.update();cache.data=me;data.update(objects=ci,triangles=len(ff));(R/'V26_1_Collision_Index.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
views=json.loads((D/'Views.json').read_text('utf8'));row=next(r for r in views if r[0].startswith('04_'));row[1]=[6.3,9.10,5.65];row[2]=[6.3,9.65,6.85];row[3]=22;c=bpy.data.objects['V26_1_'+row[0]];c.location=row[1];c.rotation_euler=(Vector(row[2])-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=row[3]
views.append(['13_Stair_Flush_Glazing_Jamb',[7.4,9.05,1.2],[4.4,9.6,5.5],20]);tag,pos,aim,lens=views[-1];col=bpy.data.collections['V26_1_穿模重面与实拍扶手修正'];c=bpy.data.objects.new('V26_1_'+tag,bpy.data.cameras.new('V26_1_'+tag));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=600;(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8')
ch=json.loads((R/'V26_1_Changes.json').read_text('utf8'));ch['changed']=sorted(set(ch['changed'])|set(edited));ch['added']=sorted(set(ch['added'])|{c.name});ch['site_proof']=site['proof'];ch['railing_proof']=railing['proof'];ch['context_trim_proof']=ctx['proof'];ch['final_visual_repairs']=['Shared-ring sweep removes dark cap seams at wreath transitions','Both sides of west wall borders seated into original registered wall','Legacy V24_21 exterior frieze and cornices clipped at the replaced branch and east wall, including diagonal fragments'];(R/'V26_1_Changes.json').write_text(json.dumps(ch,ensure_ascii=False,indent=2),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);(R/'V26_1_Build.json').write_text(json.dumps({'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'source':ch['source'],'source_sha256':ch['source_sha256'],'blender':bpy.app.version_string,'visual_patch_applied':True},indent=2),encoding='utf8');print('V26_1_FINAL_SAVED',sha(P),flush=True)
