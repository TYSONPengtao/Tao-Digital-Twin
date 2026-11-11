from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_35';ver=sys.argv[sys.argv.index('--version')+1]if '--version'in sys.argv else '35';O=Path('E:/jz/JIA/Rebuild_V24_'+ver);R=O/'Reports';P=O/('Blender/Architecture_Complete_V24_'+ver+'.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();before=json.loads((D/'Before_Snapshot.json').read_text());after=snapshot(bpy);prep=json.loads((D/'Prepared_Geometry.json').read_text());changed={r['name']for r in prep['changed']};removed=set(prep['remove']);allowed=changed|removed|{'V24_21_Navigation_Collision'};checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
delta=[n for n,v in before['objects'].items()if n not in allowed and after['objects'].get(n)!=v];ck('All original objects outside the specified scan repair remain unchanged',not delta,unexpected=delta)
ck('All ten wholly redundant scanned wall fragments are removed',not(removed&set(after['objects'])),removed=sorted(removed));ck('Four partial source fragments retain their legitimate exterior part',all(n in after['objects']for n in changed))
ck('All original door and window actions and poses remain unchanged',before['actions']==after['actions']and before['door_poses']==after['door_poses'])
used={m.name for o in bpy.data.objects if o.name in before['objects']and o.name not in allowed and o.type=='MESH'for m in o.data.materials if m};bad=[n for n in used if after['materials'].get(n,{}).get('hash')!=before['materials'][n]['hash']];ck('All original protected material shaders remain unchanged',not bad,changed=bad)
names=['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','V24_25_Kitchen_East_Unified_Pan_Barrel_Field','V24_08_Kitchen_Corrugated_Exhaust_Elbow','V24_08_Kitchen_Open_Round_Flue'];ck('Native blue brick masonry tile roof and both exhaust pipes are byte-identical',all(after['objects'][n]==before['objects'][n]for n in names))
rows=json.loads((D/'Visible_Artifact_Rays.json').read_text());targets=[r['pixel']for r in rows if r['object'].startswith('V24_34_MB7_')];sc.render.resolution_x=1500;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;c=bpy.data.objects['V24_35_01_Kitchen_East'];corners=c.data.view_frame(scene=sc);lo=Vector((min(v.x for v in corners),min(v.y for v in corners),corners[0].z));hi=Vector((max(v.x for v in corners),max(v.y for v in corners),corners[0].z));deps=bpy.context.evaluated_depsgraph_get();rays=[]
for x,y in targets:
 local=Vector((lo.x+(hi.x-lo.x)*x/1500,hi.y-(hi.y-lo.y)*y/1100,lo.z));direction=(c.matrix_world.to_3x3()@local).normalized();origin=c.location.copy();ob=None
 for _ in range(16):
  hit,p,no,face,o,mat=sc.ray_cast(deps,origin,direction,distance=100)
  if not hit:break
  if not o.hide_render:ob=o.name;break
  origin=p+direction*.001
 rays.append({'pixel':[x,y],'visible_object':ob});ck('Marked ghost surface is replaced by native wall at pixel '+str([x,y]),ob is not None and'ORIGINAL_EXTERIOR_'not in ob and not ob.startswith(('V24_34_MB7_','V24_36_PTJIA6_')),object=ob)
ck('Source V24.34 native file remains unchanged',hashlib.sha256(Path(json.loads((D/'Source.json').read_text())['model']).read_bytes()).hexdigest()==json.loads((D/'Source.json').read_text())['sha256'])
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];(R/('V24_'+ver+'_Repair_QA.json')).write_text(json.dumps({'status':'PASS_ANNOTATED_WALL_AND_EAVE_REPAIR'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail,'repaired_rays':rays},ensure_ascii=False,indent=2),encoding='utf8');print('REPAIR_QA',len(checks),'FAIL',len(fail),flush=True)
