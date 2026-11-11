import bpy,json,sys,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_05_common import *
from v24_03_junction_blender import _bounds,_tree,_closed_stats
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();base=json.loads((R/'V24_05_Before_Snapshot.json').read_text(encoding='utf8'));delta=json.loads((R/'V24_05_Changes.json').read_text(encoding='utf8'));build=json.loads((R/'V24_05_Build.json').read_text(encoding='utf8'));checks=[]
def ck(n,ok,**kw):checks.append({'check':n,'pass':bool(ok),**kw})
allowed=set(delta['translated_050m_objects'])|set(delta['restored_contacts'])
ck('Only declared roof and adjoining components changed',set(delta['changed_objects'])<=allowed,unexpected=sorted(set(delta['changed_objects'])-allowed));ck('No prior scene objects removed',not delta['removed_objects'])
for n,r in base['materials'].items():ck('Original shader '+n,n in bpy.data.materials and q._material(bpy.data.materials[n])['hash']==r['hash'])
for n,r in base['images'].items():ck('Packed image '+n,n in bpy.data.images and q._image(bpy.data.images[n])==r)
for n,h in base['actions'].items():ck('Original action '+n,n in bpy.data.actions and q._action(bpy.data.actions[n])==h)
for n,r in base['objects'].items():
 ob=bpy.data.objects.get(n);ck('Retained object '+n,ob is not None)
 if ob is None:continue
 ck('Parent and action '+n,(ob.parent.name if ob.parent else None)==r['parent']and q._animation(ob)==r['animation'])
 before=np.array(r['matrix']);after=np.array(q._matrix(ob.matrix_world));expected=before.copy()
 if n in delta['translated_050m_objects']:expected[2,3]+=.50
 ck('Exact 0.50m lift or unchanged transform '+n,np.max(np.abs(after-expected))<1e-5)
 if r['mesh_hash']and n not in delta['restored_contacts']:ck('Original mesh/UV '+n,q._mesh_hash(ob.data)==r['mesh_hash'])
for n,h in delta['expected_mesh_hashes'].items():ck('Saved mesh digest '+n,q._mesh_hash(bpy.data.objects[n].data)==h)
for n in delta['added_objects']:
 if n not in bpy.data.objects or bpy.data.objects[n].type!='MESH':continue
 ob=bpy.data.objects[n];s=q._stats(ob.data);ck('Closed new bearing '+n,s['closed']and s['signed_volume_m3']>0,**s)
for n in delta['restored_contacts']:
 s=_closed_stats(bpy.data.objects[n]);ck('Closed kitchen contact '+n,s['boundary_edges']==0,**s)
for f,poses in base['door_poses'].items():
 sc.frame_set(int(f));bpy.context.view_layer.update()
 for n,m in poses.items():ck('Original door pose '+n+' frame '+f,q._matrix(bpy.data.objects[n].matrix_world)==m)
sc.frame_set(40);bpy.context.view_layer.update();ck('26 moving doors retained',len(base['doors'])==26);ck('15 carved fields retained',len([o for o in bpy.data.objects if o.name.startswith('V24_Gate_Reference_Relief_')])==15);ck('Real materials enabled',all(v.material_override is None for v in sc.view_layers))
ceil=bpy.data.objects['V24_XIESHAN_07_Closed_Pale_Ceiling'];cz=_bounds(ceil)[0][2]
ck('Soffit raised from 2.538m to 3.038m',abs(cz-3.038)<1e-5,soffit_z_m=cz)
for k in [1,2]:
 n='V24_05_Gate_Upper_Pier_Bearing_'+str(k);lo,hi=_bounds(bpy.data.objects[n]);ck('Pier extension overlaps original pillar and raised ceiling '+str(k),lo[2]<2.6333 and hi[2]>cz+.01,lower_z_m=lo[2],upper_z_m=hi[2])
roof=[(o,_bounds(o),_tree(o))for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')];coll=[]
for n in delta['restored_contacts']:
 ob=bpy.data.objects[n];lo,hi=_bounds(ob);tr=_tree(ob)
 for ro,bb,rt in roof:
  if any(hi[i]<bb[0][i]or lo[i]>bb[1][i]for i in range(3)):continue
  ov=tr.overlap(rt)
  if ov:coll.append({'kitchen':n,'gate':ro.name,'triangles':len(ov)})
ck('No gate/kitchen roof interpenetration',not coll,collisions=coll)
gtr=[t for o,bb,t in roof if o.name.startswith(('V24_XIESHAN_01_','V24_XIESHAN_02_'))];ktr=[_tree(bpy.data.objects[n])for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0_Geometry']];gap=[]
for r in delta['junction_height_samples']:
 p=Vector((r['x'],r['y'],8));d=Vector((0,0,-1));gh=[h[0].z for t in gtr if(h:=t.ray_cast(p,d,10))[0]is not None];kh=[h[0].z for t in ktr if(h:=t.ray_cast(p,d,10))[0]is not None]
 if gh and kh:gap.append(max(gh)-max(kh))
ck('Gate roof higher than adjacent kitchen slope at marked junction',bool(gap)and min(gap)>.05,samples=len(gap),minimum_vertical_gap_m=min(gap)if gap else None)
returnwall=_tree(bpy.data.objects['V24_04_Kitchen_Perimeter_Upper_Return']);perimeter=_tree(bpy.data.objects['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry']);backwall=_tree(bpy.data.objects['V24_03_Kitchen_Rear_Gable_Wall']);ck('Full-height kitchen rear closure retained',bool(returnwall.overlap(perimeter))and bool(returnwall.overlap(backwall)))
ck('Saved model SHA matches build',sha(P)==build['sha256']);fail=[r for r in checks if not r['pass']];report={'status':'PASS_V24_05_FRESH_BLEND_QA'if not fail else'FAIL_V24_05_FRESH_BLEND_QA','model_sha256':sha(P),'checks':checks,'failures':fail,'roof_raise_m':.5,'marked_junction_minimum_gap_m':min(gap)if gap else None,'retained_materials':len(base['materials']),'retained_images':len(base['images']),'moving_doors':len(base['doors'])};write('V24_05_Fresh_Blend_QA.json',report);print(report['status'],len(checks),len(fail),report['marked_junction_minimum_gap_m'],flush=True)
if fail:raise AssertionError(json.dumps(fail[:12],ensure_ascii=False))
