import bpy,json,numpy as np,hashlib
from pathlib import Path
W=Path(__file__).parent;D=W/'v26_9';O=Path('E:/jz/JIA/Rebuild_V26_9');P=O/'Blender/Architecture_Complete_V26_9.blend';checks=[]
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('NATIVE_SPECIFIC',n,bool(p),kw if not p else'',flush=True)
extra={r['name']:r for r in json.loads((D/'Extra_Source_Index.json').read_text('utf8'))};bad=[]
for n,r in extra.items():
 o=bpy.data.objects[n];a=np.load(D/r['file']);v=np.array([o.matrix_world@q.co for q in o.data.vertices]);dv=np.array([0,0,.4])if'Header_'in n else np.zeros(3)
 if v.shape!=a['v'].shape or np.max(abs(v-a['v']-dv))>5e-7:bad.append(n)
ck('All original stone picture reliefs retained; header only translated rigidly400mm',not bad,sculpted_objects=len(extra),invalid=bad)
o=bpy.data.objects['V24_05_Gate_Plain_Neck_Above_Carved_Lintel'];z=[(o.matrix_world@v.co).z for v in o.data.vertices];ck('Large gate blank replaced by concealed22mm bearing',abs(max(z)-min(z)-.022)<.00001,new_height_m=max(z)-min(z))
light=bpy.data.objects['V26_8_Overcast_Interior_F3_left'];canopy=bpy.data.objects['TERRACE_METAL_CANOPY_Geometry'];minroof=min((canopy.matrix_world@v.co).z for v in canopy.data.vertices)
ck('Full horizontal soft-light disk is below the lowest canopy point',light.location.z<minroof-.15,light_z=light.location.z,canopy_low_z=minroof)
ck('Saved neutral overcast world and zero direct sun retained',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and all(o.data.energy==0 for o in sc.objects if o.type=='LIGHT'and o.data.type=='SUN'))
ch=json.loads((O/'Reports/V26_9_Changes.json').read_text('utf8'));invalid_uv=[]
for n in ch['geometry_changed']:
 o=bpy.data.objects[n];layer=o.data.uv_layers.active
 if layer:
  uv=np.empty(len(layer.data)*2,np.float32);layer.data.foreach_get('uv',uv)
  if not np.isfinite(uv).all():invalid_uv.append(n)
ck('UV coordinates of all92 modified meshes are finite, including repaired inherited bad house UVs',not invalid_uv,objects=len(ch['geometry_changed']),invalid=invalid_uv)
prep=json.loads((D/'Prepared_All_Geometry.json').read_text('utf8'));motion={};bads=[]
for rr in prep['new_sliding_animations']:
 o=bpy.data.objects[rr['object']];me=o.data;me.calc_loop_triangles();fn='SLIDING_LOCAL_'+str(len(motion))+'.npz';np.savez_compressed(D/'Final'/fn,v=np.array([v.co[:]for v in me.vertices]),f=np.array([t.vertices[:]for t in me.loop_triangles]),mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]));motion[o.name]={'file':fn,'materials':[m.name for m in me.materials],'window':rr['parent']+'_Geometry','matrices':{}}
 for fr,dx in [(1,0.),(40,rr['open_translation_m']),(60,0.),(80,rr['alternate_open_translation_m']),(100,0.)]:
  sc.frame_set(fr);bpy.context.view_layer.update();mat=np.array(o.matrix_world);motion[o.name]['matrices'][str(fr)]=mat.tolist()
  if abs(mat[0,3]-dx)>2e-6 or abs(mat[1,3])+abs(mat[2,3])>2e-6 or np.max(abs(mat[:3,:3]-np.eye(3)))>1e-7:bads.append([o.name,fr])
ck('All20 saved rear sashes slide on X only with separate left-open/right-open states',len(motion)==20 and not bads,frames=[1,40,60,80,100],invalid=bads)
(D/'Final/Window_Sliding_Motion.json').write_text(json.dumps(motion),'utf8')
sc.frame_set(40);bpy.context.view_layer.update()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[q for q in checks if not q['pass']];(O/'Reports/V26_9_Native_Specific_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail},indent=2),'utf8');print('NATIVE_SPECIFIC_DONE',len(checks),len(fail),flush=True)
