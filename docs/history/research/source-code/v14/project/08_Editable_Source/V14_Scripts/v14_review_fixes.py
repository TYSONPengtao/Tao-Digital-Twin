import sys,json,math,ast,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V13/08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};Q=json.loads((W/'v14/Building_Mutation.json').read_text(encoding='utf8'));E.update({e['name']:e for e in Q['replace']+Q['add']})
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'solid','exec'))
changes=[]
def put(n,ps):
 e=copy.deepcopy(E[n]);e['parts']=ps;e['v14_review_fix']='Physical roof/wall and traversable door opening review';e['source']='DJI_0525/0526 and actual F3 hall photos';Q['replace']=[r for r in Q['replace'] if r['name']!=n];Q['add']=[r for r in Q['add'] if r['name']!=n];(Q['replace'] if n in {e['name'] for e in S['elements']} else Q['add']).append(e);E[n]=e
regions=[{'type':'box','origin':[13.13,-17.5,-.40],'size':[6.5,8.3,6.5]},{'type':'box','origin':[13.05,-12.2,-.40],'size':[1.65,10.1,6.5]}];cuts=[manifold(r) for r in regions];cs=cuts[0]+cuts[1]
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING','SITE_PERIMETER_JOINED_RETAINING_WALL_0_PROVISIONAL_FLOWER_CROWN','SITE_PERIMETER_JOINED_RETAINING_WALL_0_PLASTER_STEPPED_RELIEF']:
 ps=[];count=0
 for p in E[n]['parts']:
  v,_,_,_=ex.solid_data(p['geometry']);lo=v.min(0);hi=v.max(0)
  if not any(np.all(hi>np.array(r['origin'])) and np.all(lo<np.array(r['origin'])+r['size']) for r in regions):ps.append(p);continue
  m=manifold(p['geometry']);rr=m-cs
  if m.volume()-rr.volume()>1e-8:
   count+=1
   if not rr.is_empty():ps.append({'geometry':fromman(rr),'material':p['material']})
  else:ps.append(p)
 if count:put(n,ps);changes.append({'node':n,'trimmed_upper_wall_or_coping_parts':count,'below_floor_retaining_base_kept':True})
# Cut the actual ceramic finish as well as its wall core at the relocated exit.
n='TERRACE_SIDE_CERAMIC_PANEL_GRID';cu=manifold({'type':'box','origin':[3.60,6.30,7.48],'size':[.45,.90,2.13]});ps=[];count=0
for p in E[n]['parts']:
 v,_,_,_=ex.solid_data(p['geometry']);lo=v.min(0);hi=v.max(0)
 if np.all(hi>[3.6,6.3,7.48]) and np.all(lo<[4.05,7.2,9.61]):
  m=manifold(p['geometry']);r=m-cu
  if m.volume()-r.volume()>1e-9:
   count+=1
   if not r.is_empty():ps.append({'geometry':fromman(r),'material':p['material']})
  else:ps.append(p)
 else:ps.append(p)
put(n,ps);changes.append({'node':n,'exit_finish_parts_cut':count})
# Replace the two block-like ridge end markers with curled tile finial profiles.
profile=[[-.24,.08],[-.27,.31],[-.20,.58],[-.06,.64],[.05,.52],[.05,.34],[.22,.18],[.38,.09],[.39,.035],[.19,.035],[.05,.12],[-.07,.20],[-.12,.32],[-.14,.42],[-.18,.39],[-.19,.23],[-.15,.07]]
def finial(origin,axis):
 o=np.array(origin);a=np.array(axis,float);b=np.array([-a[1],a[0],0]);q=[(o+a*s+[0,0,z]-b*.065).tolist() for s,z in profile];return {'geometry':{'type':'prism','profile':q,'vector':(b*.13).tolist()},'material':'M_Roof'}
n='SITE_KITCHEN_RIDGE_CAP_AND_END_ORNAMENTS';ps=[];removed=0
for p in E[n]['parts']:
 v,_,_,_=ex.solid_data(p['geometry']);span=v.max(0)-v.min(0)
 if span[2]>.35:removed+=1
 else:ps.append(p)
cm=Q['roof_junction']['main_top_plane'];hm=lambda x,y:cm[0]*x+cm[1]*y+cm[2]
ps.extend([finial([11.515,-12.00,hm(11.515,-12.0)+.025],[0,1,0]),finial([11.515,-2.45,hm(11.515,-2.45)+.025],[0,-1,0])]);put(n,ps);changes.append({'node':n,'replaced_block_markers':removed,'curled_tile_finials':2})
cn=Q['roof_junction']['inner_north_top_plane'];cs0=Q['roof_junction']['inner_south_top_plane'];ry=lambda x:-((cn[0]-cs0[0])*x+(cn[2]-cs0[2]))/(cn[1]-cs0[1]);hh=lambda x:cn[0]*x+cn[1]*ry(x)+cn[2]
n='SITE_V14_INNER_STORAGE_RIDGE_CAPS';ps=E[n]['parts']+[finial([13.35,ry(13.35),hh(13.35)+.025],[1,-.052,0]),finial([19.0,ry(19.0),hh(19.0)+.025],[-1,.052,0])];put(n,ps)
Q['review_fixes']=changes;(W/'v14/Building_Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(W/'v14/Review_Fix_QA.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8');print('DONE',changes,flush=True)
