import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
D=W/'v26_13';D.mkdir(exist_ok=True);report={}
for ver in['V24','V26_12']:
 p=Path('E:/jz/JIA/Rebuild_'+ver+'/Blender/Architecture_Complete_'+ver+'.blend');bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.scene.frame_set(40);bpy.context.view_layer.update();rows=[]
 names=['SITE_V21_GATE_REFERENCE_LAYER_01_Geometry','SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_03_Geometry','SITE_V21_GATE_REFERENCE_LAYER_05_Geometry','V24_Gate_Waist_Carving_Retained','V26_10_Inner_Gate_Rectangular_Stone_Piers']
 names += [o.name for o in bpy.data.objects if o.name.startswith('SITE_V20_INNER_GATE__LEAF_')and o.type=='MESH']
 for name in names:
  o=bpy.data.objects.get(name)
  if not o or o.type!='MESH':continue
  me=o.data;me.calc_loop_triangles();v=q._world(me,o.matrix_world);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn=ver+'_'+name+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
  belt=v[(v[:,2]>.60)&(v[:,2]<.75)&(v[:,0]<6.)];r={'name':name,'file':fn,'materials':[m.name for m in me.materials],'bounds':[v.min(0).tolist(),v.max(0).tolist()],'belt_bounds':[belt.min(0).tolist(),belt.max(0).tolist()]if len(belt)else None,'mesh_hash':q._mesh_hash(me),'matrix':q._matrix(o.matrix_world),'hide_render':o.hide_render};rows.append(r);print('OBJECT',ver,name,r['bounds'],'BELT',r['belt_bounds'],flush=True)
 mats={}
 for n in['M_V21_GATE_REF_01','M_V21_GATE_REF_02','M_V21_GATE_REF_03','M_V21_GATE_REF_04']:
  m=bpy.data.materials.get(n)
  if m:mats[n]=q._material(m)
 report[ver]={'model':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':rows,'materials':mats}
(D/'Probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
