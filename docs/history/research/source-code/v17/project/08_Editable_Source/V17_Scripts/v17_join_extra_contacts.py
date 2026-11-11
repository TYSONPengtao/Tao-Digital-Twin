import ast
from pathlib import Path
W=Path(__file__).parent;src=(W/'v17_join_contact_solids.py').read_text(encoding='utf8');tree=ast.parse(src);prefix=[]
for node in tree.body:
 if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='union_elements':break
 prefix.append(node)
exec(compile(ast.Module(prefix,type_ignores=[]),'<contact_native_helpers>','exec'))
union_elements(['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY','SITE_V14_INNER_STORAGE_ROOF_WOOD_SHEATHING'],'SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY','M_V12_Kitchen_HONEY_WOOD','CHINESE_TIMBER_ASSEMBLY_WITH_CONTINUOUS_ROOF_SHEATHING')
n='SITE_V14_OUTER_STORAGE_VISIBLE_STONE_PLINTH';old=E[n];ps=[]
for p in old['parts']:
 v,fs,_,_=ex.solid_data(p['geometry']);v=np.array(v);v[v[:,2]>-.409,2]=-.408;ps.append(manifold(oriented({'type':'polyhedron','vertices':v.tolist(),'faces':[list(f) for f in fs]})))
a=mf.Manifold.batch_boolean(ps,mf.OpType.Add);nn='SITE_V17_OUTER_STORAGE_PLINTH_CAP_RETURN';e={'name':nn,'layer':'60_SITE','family':'SITE_MODEL','confidence':'PHOTO_FIT','parts':[{'geometry':fromman(a),'material':'M_Stone'}],'classification':'SUPPORTED_OUTER_STORAGE_STONE_PLINTH_WITH_RECESSED_CAP','source':'Existing V14 visible stone plinth; 8 mm cap recess prevents coplanar rendering against unchanged floor','v17_original_node':n,'v17_cap_top_z':-.408}
for ob in node_obs(n):deletion(ob,n)
remove_nodes.append(n);new[nn]=e;recipes[nn]=[{'element':old,'cap_recess_m':.008}];write(e);proof.append({'node':nn,'cap_recess_m':.008,'original_plan_retained':True})
tail=src[src.index('remove_nodes=[q for q in dict.fromkeys(remove_nodes)'):]
exec(compile(tail,'<save_contact_cleanup>','exec'))
