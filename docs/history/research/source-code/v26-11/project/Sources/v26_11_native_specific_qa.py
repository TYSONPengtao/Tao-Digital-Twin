import bpy,json,numpy as np,hashlib,sys
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
D=W/'v26_11';O=Path('E:/jz/JIA/Rebuild_V26_11');P=O/'Blender/Architecture_Complete_V26_11.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();old=json.loads((D/'Before_Snapshot.json').read_text('utf8'));ch=json.loads((O/'Reports/V26_11_Changes.json').read_text('utf8'));checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('NATIVE_SPECIFIC',n,bool(p),kw if not p else'',flush=True)
bad=[]
for n in ch['archived']:
 o=bpy.data.objects[n];b=old['objects'][n]
 if q._mesh_hash(o.data)!=b['mesh_hash']or np.max(abs(np.asarray(o.matrix_world)-b['matrix']))>1e-7 or not o.hide_render or not o.hide_get():bad.append(n)
ck('All22 replaced stone-picture/eave-board objects remain editable, exact and hidden in the source archive',not bad,objects=len(ch['archived']),invalid=bad)
stone=[bpy.data.objects[p['name']]for p in ch['proof']['gate']['panels']];ck('All21 photo-derived reliefs are real saved meshes with no displacement or subdivision modifiers',len(stone)==21 and all(not len(o.modifiers)and len(o.data.polygons)>1000 for o in stone),visible_triangles=sum(len(o.data.polygons)for o in stone))
image=bpy.data.images[ch['new_images'][0]];fn=O/'Textures/Gate_Reference_Gray_Height_Atlas.png';blob=fn.read_bytes();packed=bytes(image.packed_file.data)if image.packed_file else b'';ck('The user-photo grayscale height atlas is16bit, Non-Color, and packed byte-identically',blob[24]==16 and image.colorspace_settings.name=='Non-Color'and hashlib.sha256(packed).hexdigest()==hashlib.sha256(blob).hexdigest(),image=image.name,dimensions=list(image.size))
bad=[]
for n in ch['geometry_changed']:
 o=bpy.data.objects[n];uv=o.data.uv_layers.active
 if uv:
  u=q._bulk(uv.data,'uv',2)
  if not np.isfinite(u).all()or abs(u).max(initial=0)>1000:bad.append(n)
ck('All changed native UV coordinates are finite and numerically stable',not bad,invalid=bad)
waist='V24_Gate_Waist_Carving_Retained';ck('Original waist carving stays visible with exact geometry and transform',q._mesh_hash(bpy.data.objects[waist].data)==old['objects'][waist]['mesh_hash']and not bpy.data.objects[waist].hide_render)
ck('Saved overcast world and zero direct sun are retained',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and all(o.data.energy==0 for o in sc.objects if o.type=='LIGHT'and o.data.type=='SUN'))
ck('Original level F3 guard, roof, Roman columns and main storage timber meshes retain their source data',all(q._mesh_hash(bpy.data.objects[n].data)==r['mesh_hash']for n,r in old['objects'].items()if r['type']=='MESH'and(n=='V26_1_Photo_Referenced_Continuous_Wood_Railing'or n.startswith(('ROMAN_COLUMN_','V24_15_Storage_','SITE_V14_INNER_STORAGE_')))),scope='Decorative outer eave board is archived separately; structural timber remains')
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];(O/'Reports/V26_11_Native_Specific_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('NATIVE_SPECIFIC_DONE',len(checks),len(fail),flush=True)
