import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_17');P=O/'Blender/Architecture_Complete_V26_17.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;h=bpy.data.objects['V26_3_House_Connected_Walls_And_Stairs'];h.data.calc_loop_triangles();v=[h.matrix_world@p.co for p in h.data.vertices];f=[t.vertices[:]for t in h.data.loop_triangles];tree=BVHTree.FromPolygons(v,f,all_triangles=True);leaves=[o for o in sc.objects if o.type=='MESH'and o.name.startswith('V24_18_BAY_WINDOW_')and'_Outward_Hinge_'in o.name];bad=[];poses=0
for frame in range(1,41):
 sc.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
 for source in leaves:
  ob=source.evaluated_get(deps);me=ob.to_mesh();me.calc_loop_triangles();lv=[ob.matrix_world@p.co for p in me.vertices];lf=[t.vertices[:]for t in me.loop_triangles];lt=BVHTree.FromPolygons(lv,lf,all_triangles=True)
  if tree.overlap(lt):bad.append({'frame':frame,'leaf':source.name})
  ob.to_mesh_clear();poses+=1
checks=[{'check':'All ten actual front casement leaves, frame and glass, clear the corrected house during40 evaluated frames','pass':len(leaves)==20 and poses==800 and not bad,'poses':poses,'objects':len(leaves),'invalid':bad}];fail=[q for q in checks if not q['pass']];(O/'Reports/V26_17_Window_Motion_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('WINDOW_MOTION_QA',poses,len(fail),flush=True)
