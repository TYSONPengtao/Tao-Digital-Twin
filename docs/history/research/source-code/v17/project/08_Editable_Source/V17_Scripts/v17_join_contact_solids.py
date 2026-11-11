"""Remove coincident interface faces from adjoining masonry, timber and stone guards."""
import sys,json,math,hashlib,ast,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,manifold3d as mf,export_v5 as ex
from shapely.geometry import LineString
from shapely.geometry.polygon import orient
O=Path(r'E:/jz/JIA/Rebuild_V17');P=O/'04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm';S=json.loads((O/'08_Editable_Source/Architecture_Scene_V17.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};F=rh.File3dm.Read(str(P));AQ=json.loads((O/'06_Report/V17_Assembly_QA.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'))
C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold','fromman']),('v17_assemble.py',['make_mesh','gh','node_obs'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<helpers>','exec'))
removedids=set();deleted=[];created=[];remove_nodes=[];replacements={};new={};proof=[];recipes={}
def deletion(ob,n):
 ident=str(ob.Attributes.Id);removedids.add(ident);deleted.append({'id':ident,'name':ob.Attributes.Name,'node':n});F.Objects.Delete(ob.Attributes.Id)
def write(e,reuse=False):
 n=e['name'];oo=node_obs(n)
 if reuse:
  assert len(oo)==1;at=oo[0].Attributes;deletion(oo[0],n)
 else:
  assert not oo,n;gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr);at=rh.ObjectAttributes();at.LayerIndex=next(l.Index for l in F.Layers if l.Name=='60_SITE');at.AddToGroup(gid)
 for j,p in enumerate(e['parts']):
  assert len(e['parts'])==1;mm,_,_,_=make_mesh(p['geometry']);at.Name=n+'__1';at.MaterialIndex=next(i for i,m in enumerate(F.Materials) if m.Name==p['material']);at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[at.MaterialIndex].DiffuseColor;at.SetUserString('V17_Node',n);at.SetUserString('V17_Repair','United adjoining solids; duplicate contact faces removed');ident=F.Objects.Add(mm,at);created.append({'id':str(ident),'name':at.Name,'node':n,'geometry_hash':gh(mm),'closed_expected':True})
def union_elements(names,n,material,classification,select=None):
 bodies=[];recipe=[]
 for oldn in names:
  e=E[oldn];selected=[];kept=[];oo=node_obs(oldn)
  for j,p in enumerate(e['parts']):
   if p['material']==material:
    selected.append(p);bodies.append(manifold(p['geometry']))
   else:kept.append(p)
  recipe.append({'source_node':oldn,'element':copy.deepcopy(e),'selected_material':material})
  for ob in oo:
   if F.Materials[ob.Attributes.MaterialIndex].Name==material:deletion(ob,oldn)
  if kept:replacements[oldn]={**e,'parts':kept,'v17_geometry_note':'Wood or guard component belongs to the connected assembly; remaining material components retained','v17_connected_assembly':n}
  else:remove_nodes.append(oldn)
 a=mf.Manifold.batch_boolean(bodies,mf.OpType.Add);g=fromman(a);after=manifold(g);sym=(a-after).volume()+(after-a).volume();assert sym<1e-6
 e={'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'PHOTO_FIT','parts':[{'geometry':g,'material':material}],'classification':classification,'source':'V17 photo-fitted component geometry; native solid union removes only overlapping/coincident interface faces','v17_source_components':names,'v17_envelope_change_m3':sym};new[n]=e;recipes[n]=recipe;proof.append({'node':n,'source_components':names,'before_union_components':len(bodies),'after_connected_components':len(a.decompose()),'symmetric_volume_difference_m3':sym,'closed_volume_m3':a.volume()});write(e);print('JOINED',n,len(bodies),len(a.decompose()),sym,flush=True)
union_elements(['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES','SITE_V14_INNER_STORAGE_MASONRY'],'SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY','M_Grey_Brick','CONTINUOUS_KITCHEN_STORAGE_MASONRY_WITH_ORIGINAL_PORTALS')
union_elements(['SITE_V14_INNER_STORAGE_TIMBER_ROOF_FRAME','SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES','SITE_V17_STORAGE_VERANDA_TIMBER_ENTRY_FRONT','SITE_V17_STORAGE_VERANDA_EAVE_HANGING_LATTICE'],'SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY','M_V12_Kitchen_HONEY_WOOD','CHINESE_TIMBER_POST_BEAM_PURLIN_RAFTER_AND_VERANDA_FRAME')
union_elements(['SITE_V17_STORAGE_EAVE_GALLERY_STONE_GUARD','SITE_V14_OUTER_STORAGE_STONE_BALUSTRADE'],'SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD','M_Stone','CONTINUOUS_GALLERY_AND_OUTER_STORAGE_STONE_GUARD')
# A 3 mm outward base return hides the old slab side faces while retaining their closed solids.
n='SITE_V17_KITCHEN_STORAGE_CONTINUOUS_STONE_BASE';e=copy.deepcopy(E[n]);facade=e['v17_facade_outer_line'];p=orient(LineString(facade).buffer(.003,single_sided=True,join_style=2),1);g={'type':'prism_holes','outer':list(p.exterior.coords)[:-1],'holes':[],'z':-4.45,'height':4.07};a=manifold(e['parts'][0]['geometry'])+manifold(g);e['parts'][0]['geometry']=fromman(a);e['v17_surface_return_m']=.003;e['v17_repair']='3 mm exterior stone return covers coincident slab-side interface; L support and inside grade unchanged';replacements[n]=e;write(e,True)
remove_nodes=[q for q in dict.fromkeys(remove_nodes) if q not in new];S['elements']=[replacements.get(e['name'],e) for e in S['elements'] if e['name'] not in remove_nodes and e['name'] not in new]+list(new.values());changed=set(remove_nodes)|set(replacements)|set(new);rows=[r for r in I if r['name'] not in changed]
for n in sorted(set(replacements)|set(new)):
 e=next(e for e in S['elements'] if e['name']==n);vv=[];ff=[];uv=[];nn=[];mi=[];mats=[];oo=node_obs(n)
 for ob in oo:
  mm=ob.Geometry;mat=F.Materials[ob.Attributes.MaterialIndex].Name
  if mat not in mats:mats.append(mat)
  off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
  for f in mm.Faces:ff.append((np.array(f[:3])+off).tolist());mi.append(mats.index(mat))
 fn='Native_Readback/NATIVE_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=np.array(vv),faces=np.array(ff,np.int32),uv=np.array(uv),normals=np.array(nn),material_ids=np.array(mi,np.int32));rows.append({'name':n,'file':fn,'materials':mats,'triangles':len(ff),'native_objects':len(oo),'element':{k:v for k,v in e.items() if k!='parts'}})
newids={r['id'] for r in created};AQ['retained']=[r for r in AQ['retained'] if r['id'] not in removedids];AQ['created']=[r for r in AQ['created'] if r['id'] not in removedids]+created;olddeleted={r['id'] for r in AQ['deleted']};AQ['deleted']+=[r for r in deleted if r['id'] not in newids and r['id'] not in olddeleted];AQ['changed_nodes']=sorted((set(AQ['changed_nodes'])|set(replacements)|set(new))-set(remove_nodes));AQ['removed_nodes']=sorted(set(AQ.get('removed_nodes',[]))|set(remove_nodes));AQ['native_objects']=len(F.Objects);AQ['nodes']=len(rows)
sp=O/'08_Editable_Source/Architecture_Scene_V17.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V17_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();F.Strings['V17_Contact_Solid_Cleanup']='Connected masonry, timber and stone guard union; constituent recipes preserved';assert F.Write(str(P),8)
for nm in ['Native_Readback_Index_V17.json','Modeled_Index_V17.json']:(O/'02_Data'/nm).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
(O/'06_Report/V17_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8')
pp=O/'06_Report/V17_Connected_Solids_QA.json';prior=json.loads(pp.read_text(encoding='utf8')) if pp.exists() else {};combined=[r for r in prior.get('assemblies',[]) if r['node'] not in {q['node'] for q in proof}]+proof;pp.write_text(json.dumps({'status':'PASS_CONTACT_UNION_GEOMETRY','assemblies':combined,'stone_base_return_m':.003},ensure_ascii=False,indent=2),encoding='utf8')
rp=O/'08_Editable_Source/Contact_Component_Recipes_V17.json';oldrecipes=json.loads(rp.read_text(encoding='utf8')) if rp.exists() else {}
for k,v in recipes.items():oldrecipes[k]=oldrecipes.get(k,[])+v
rp.write_text(json.dumps(oldrecipes,ensure_ascii=False,indent=2),encoding='utf8');print('CONTACT CLEANUP SAVED',len(F.Objects),len(rows),flush=True)
