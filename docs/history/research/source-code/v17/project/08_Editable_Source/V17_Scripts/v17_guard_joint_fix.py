import ast,copy
from pathlib import Path
W=Path(__file__).parent;src=(W/'v17_join_contact_solids.py').read_text(encoding='utf8');tree=ast.parse(src);prefix=[]
for node in tree.body:
 if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='union_elements':break
 prefix.append(node)
exec(compile(ast.Module(prefix,type_ignores=[]),'<contact_native_helpers>','exec'))
WOOD='M_V12_Kitchen_HONEY_WOOD';STONE='M_Stone'
for file,ns in [('v14_building.py',['part','beam','box']),('v17_storage_geometry.py',['member','unite','stone_guard'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ns],type_ignores=[]),'<guard_helpers>','exec'))
WOOD='M_V12_Kitchen_HONEY_WOOD';STONE='M_Stone';points=[[13.59,-16.10],[18.9,-16.2],[20.2,-16.2],[21.30,-15.4],[21.45,-13],[20.95,-10.35],[18.9,-9.7]];ps,bays=stone_guard(points);a=manifold(ps[0]['geometry']);assert len(a.decompose())==1,[(q.volume(),q.bounding_box()) for q in a.decompose()]
n='SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD';e=copy.deepcopy(E[n]);e.update(parts=ps,v17_joint_overlap_m=.018,v17_guard_line=points,v17_bays=bays,v17_note='Stone rails and panels overlap posts by 18 mm; hourglass balusters overlap rail/panel by 2 mm; one connected closed solid');replacements[n]=e;write(e,True);proof.append({'node':n,'after_connected_components':1,'rail_to_post_overlap_m':.018,'baluster_end_overlap_m':.002,'closed_volume_m3':a.volume()})
# Octagonal fretwork is tied to the surrounding frame with four visible timber links.
n='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY';e=copy.deepcopy(E[n]);links=[];yf=-14.855;rr=.36*math.cos(math.pi/8)
for aa,bb in [(13.70,14.59),(14.64,15.53),(16.72,17.61),(17.66,18.55)]:
 cx=(aa+bb)/2;cz=.94
 links.extend([member([aa+.075,yf,cz],[cx-rr+.012,yf,cz],.032,.032),member([cx+rr-.012,yf,cz],[bb-.075,yf,cz],.032,.032),member([cx,yf,.458],[cx,yf,cz-rr+.012],.032,.032),member([cx,yf,cz+rr-.012],[cx,yf,1.412],.032,.032)])
a=manifold(e['parts'][0]['geometry'])+mf.Manifold.batch_boolean([manifold(p['geometry']) for p in links],mf.OpType.Add);assert len(a.decompose())==1,[(q.volume(),q.bounding_box()) for q in a.decompose()];e['parts'][0]['geometry']=fromman(a);e['v17_fretwork_links']='Four timber links per octagon attach the ornamental lattice to window frame; all timber is one connected solid';replacements[n]=e;write(e,True);proof.append({'node':n,'after_connected_components':1,'octagon_frame_links':16,'closed_volume_m3':a.volume()})
exec(compile(src[src.index('remove_nodes=[q for q in dict.fromkeys(remove_nodes)'):],'<save_contact_cleanup>','exec'))
