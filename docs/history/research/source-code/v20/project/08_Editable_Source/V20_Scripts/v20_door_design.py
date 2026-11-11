import sys,json,math,copy,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V19');D=W/'v20';D.mkdir(exist_ok=True)
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
Q={'replace':[],'add':[],'remove':[]};doors=[]
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented']],type_ignores=[]),'<solid>','exec'))
def worldparts(e):
 ps=[]
 for p in ex.expand_parts(e):
  v,f=ex.world_part(p,e);ps.append({'geometry':{'type':'polyhedron','vertices':v.tolist(),'faces':f},'material':p['material']})
 return ps
def turn(ps,pivot,deg):
 a=math.radians(deg);r=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);p=np.array(pivot)
 return [{'material':q['material'],'geometry':{'type':'polyhedron','vertices':((np.array(oriented(q['geometry'])['vertices'])-p)@r.T+p).tolist(),'faces':oriented(q['geometry'])['faces']}} for q in ps]
def entry(name,ps,pivot,normal,closed_span,parent=None,angle=None):
 t=np.array(closed_span,dtype=float);t=t/np.linalg.norm(t);no=np.array(normal,dtype=float);deg=90 if np.dot([-t[1],t[0]],no)>0 else -90
 if angle is not None:deg=angle
 pivot=list(pivot)
 if not name.startswith('SITE_SW_METAL_ENTRY_GATE'):
  vv=np.vstack([oriented(q['geometry'])['vertices'] for q in ps if 'metal' not in q['material'].lower()]);axis=int(np.argmax(abs(no)));pivot[axis]=float(vv[:,axis].max()+.005 if no[axis]>0 else vv[:,axis].min()-.005)
  if 'FRONT_CENTER' in name:pivot[0]=5.350 if name.endswith('_1') else 7.650
 e=copy.deepcopy(E.get(name,{'name':name,'layer':'30_DOOR','family':'ARCH_MODEL','confidence':'USER_CORRECTED'}))
 for k in ['definition','origin','angle']:e.pop(k,None)
 e['parts']=turn(ps,pivot,deg);e.update(role='LEAF',v20_door=True,interaction='HINGED_INWARD',pivot_world_m=pivot,pivot_local_m=[0,0,0],hinge_axis_local=[0,0,1],inward_normal_local_xy=normal,open_angle_degrees=deg,current_pose='OPEN_INWARD',closed_pose=False,parent_door_id=parent,source='User 2026-10-13: all doors open inward for UE walkthrough; room topology from original INSV',dimension_status='Existing aperture retained; swing direction is explicit user preference')
 Q['replace' if name in E else 'add'].append(e);doors.append({'name':name,'hinge_local_m':pivot,'inward_normal_local_xy':normal,'closed_leaf_direction_xy':t.tolist(),'open_angle_deg':deg,'parent_door_id':parent})
 return e
for n,e in E.items():
 if not n.endswith('__LEAF'):continue
 if n.startswith('DOOR_BED_'):
  normal=[-1,0] if 'X3.9' in n else [1,0]
 elif n.startswith('DOOR_BATH_'):
  normal=[-1,0] if '_L__' in n else ([0,1] if 'F1_R' in n else [1,0])
 elif 'LAUNDRY_F3' in n:normal=[1,0]
 elif 'STUDY_F3' in n:normal=[0,-1]
 elif n=='DOOR_KITCHEN_F1__LEAF' or n.startswith('DOOR_COURTYARD_KITCHEN'):normal=[1,0]
 else:raise ValueError('Unmapped inward door '+n)
 pivot=list(e['pivot_world_m']);ps=worldparts(e);vv=np.vstack([p['geometry']['vertices'] for p in ps])
 if n.startswith('DOOR_COURTYARD_KITCHEN'):
  lo,hi=float(vv[:,2].min()),float(vv[:,2].max())
  for p in ps:
   v=np.array(p['geometry']['vertices']);v[:,2]=-.335+(v[:,2]-lo)*(1.875+.335)/(hi-lo);p['geometry']['vertices']=v.tolist()
  pivot[2]=-.335;vv=np.vstack([p['geometry']['vertices'] for p in ps])
 if 'LAUNDRY_F3' in n:pivot[1]=float(vv[:,1].max())
 t=vv.mean(0)[:2]-np.array(pivot)[:2];entry(n,ps,pivot,normal,t)
# Replace the two central glazed movable panels, keeping the side glazing and headlight fixed.
n='DOOR_FRONT_CENTER_F1';e=E[n];ps=worldparts(e);static=[ps[j] for j in [0,1,2,3,4,5,6,7,15,16,17,18]]
fixed={'name':n+'__FIXED','layer':'30_DOOR','family':'ARCH_MODEL','parts':static,'v20_role':'FIXED_SIDE_GLAZING_AND_HEADER','source':'Existing glazed facade, movable central pair separated for inward user swing'};Q['add'].append(fixed);Q['remove'].append(n)
fromparts=[ps[j] for j in [8,9,10,11]];entry(n+'__LEAF_1',fromparts,[5.345,2.1,0],[0,1],[1,0])
toparts=[ps[j] for j in [12,13,14]]
# The right leaf is given a meeting stile; fixed side jamb remains stationary.
g={'type':'box','origin':[7.602,2.055,.06],'size':[.053,.09,1.98]};toparts.append({'geometry':g,'material':'MAT_DOOR_FRAME_RED'})
entry(n+'__LEAF_2',toparts,[7.655,2.1,0],[0,1],[-1,0])
for j in [1,2]:
 n=f'DOOR_FRONT_CENTER_F2__SLIDE_{j}';e=E[n];ps=worldparts(e);vv=np.vstack([p['geometry']['vertices'] for p in ps]);lo,hi=vv[:,2].min(),vv[:,2].max()
 for p in ps:
  v=np.array(p['geometry']['vertices']);v[:,2]=3.926+(v[:,2]-lo)*(5.950-3.926)/(hi-lo);p['geometry']['vertices']=v.tolist()
 pivot=[float(vv[:,0].min() if j==1 else vv[:,0].max()),float(vv[:,1].mean()),3.9];entry(n,ps,pivot,[0,1],[1 if j==1 else -1,0]);Q['replace'][-1].update(v20_role='FORMER_CENTRAL_MOVABLE_GLAZED_PANEL',interaction='HINGED_INWARD_USER_REQUEST')
# Inner stone gate: two independent timber leaves and their own hardware, no closed sheet across the route.
n='SITE_INNER_DARK_TIMBER_DOORS';ps=worldparts(E[n]);Q['remove'].append(n)
left=entry('SITE_V20_INNER_GATE__LEAF_L',ps[:13],[5.312,-11.7,-.43],[0,1],[1,0]);right=entry('SITE_V20_INNER_GATE__LEAF_R',ps[13:],[7.888,-11.7,-.43],[0,1],[-1,0],angle=-50)
n='SITE_V15_INNER_GATE_TIMBER_TRANSOM_AND_HARDWARE';ps=worldparts(E[n]);static=[]
for p in ps:
 v=np.array(p['geometry']['vertices']);cc=v.mean(0)
 if cc[2]<1.9:
  target=left if cc[0]<6.6 else right;target['parts']+=turn([p],target['pivot_world_m'],target['open_angle_degrees'])
 else:static.append(p)
e=copy.deepcopy(E[n]);e['parts']=static;Q['replace'].append(e)
# The outer four-panel gate opens as two inward pairs. Inner panels are children of their outer hinge panel.
for j in [1,2,3,4]:
 n=f'SITE_SW_METAL_ENTRY_GATE_V11__LEAF_{j}';e=E[n];ps=worldparts(e);rootj=1 if j<3 else 4;root=E[f'SITE_SW_METAL_ENTRY_GATE_V11__LEAF_{rootj}'];pivot=root['hinge_world_m'];t=[math.cos(root['angle']),math.sin(root['angle'])];normal=[.877, .479];e2=entry(n,ps,pivot,normal,t,parent=f'SITE_SW_METAL_ENTRY_GATE_V11__LEAF_{rootj}' if j!=rootj else None)
 if j!=rootj:
  cp=np.array(e['hinge_world_m']);a=math.radians(e2['open_angle_degrees']);r=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);hinge=((cp-np.array(pivot))@r.T+np.array(pivot)).tolist();e2['pivot_world_m']=hinge;doors[-1]['hinge_local_m']=hinge;e2['relative_open_angle_degrees']=0;e2['folding_joint']='Second panel follows inward root leaf; retained registered intermediate hinge'
for e in Q['replace']+Q['add']:
 for p in e.get('parts',[]):p['geometry']=oriented(p['geometry'])
(D/'Door_Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
(D/'Door_Manifest.json').write_text(json.dumps({'coordinate_system':'LOCAL metres; Rhino ENU transform in Coordinate.json','default_pose':'OPEN_INWARD','doors':doors,'user_instruction':'All operable doors inward; two central glazed panels converted to inward user-requested operation, fixed glass retained','ue_import_tested':False},ensure_ascii=False,indent=2),encoding='utf8')
print('DOOR MUTATION',len(doors),len(Q['replace']),len(Q['add']),len(Q['remove']),flush=True)
