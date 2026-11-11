"""Remove the obsolete mid-screen band and partition the authoritative V18 native wall."""
import sys,json,math,ast,hashlib,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,manifold3d as mf,export_v5 as ex
from shapely.geometry import MultiPoint
O=Path(r'E:/jz/JIA/Rebuild_V19');B=Path(r'E:/jz/JIA/Rebuild_V18');D=W/'v19';P=O/'04_Rhino/Architecture_Complete_V19_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));BF=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V18_ALIGNED_ENU.3dm'));S=json.loads((O/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S;Q=json.loads((O/'08_Editable_Source/Mutation_V19.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Native_Readback_Index_V19.json').read_text(encoding='utf8'));AQ=json.loads((O/'06_Report/V19_Assembly_QA.json').read_text(encoding='utf8'));proof=json.loads((D/'Design_Control.json').read_text(encoding='utf8'));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));ang=math.radians(C['rotation_deg']);R=np.array([[math.cos(ang),-math.sin(ang),0],[math.sin(ang),math.cos(ang),0],[0,0,1]]);origin=np.array(C['origin']);NM=json.loads((D/'Materials.json').read_text(encoding='utf8'))
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold']),('v19_design.py',['fromman']),('v19_assemble.py',['gh','uv_for','make'])]:
 t=ast.parse((W/file).read_text(encoding='utf8'));ns=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names]
 if file=='v19_assemble.py':ns=[n for n in t.body if (isinstance(n,ast.FunctionDef) and n.name in names) or (isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ['FD','routes'] for x in n.targets)) or (isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='kind')]
 exec(compile(ast.Module(ns,type_ignores=[]),'<verified helpers>','exec'))
def addall(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def part(g,m):return {'geometry':g,'material':m}
def node(model,n):return [ob for ob in model.Objects if ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__')]
def native_man(ob):
 mm=ob.Geometry;v=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;ff=[]
 for f in mm.Faces:
  ff.append(f[:3])
  if f[3]!=f[2]:ff.append([f[0],f[2],f[3]])
 v,iv=np.unique(np.round(v,10),axis=0,return_inverse=True);f=iv[np.array(ff)];a=mf.Manifold(mf.Mesh64(v,f.astype(np.uint64)));assert a.status()==mf.Error.NoError,ob.Attributes.Name;return a,v,f
targets={};correction={'purpose':'Retain the current authoritative native wall facets; eliminate obsolete ordinary backing under the raised screen','walls':[]}
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 e=next(e for e in Q['replace'] if e['name']==n);bs=[];ls=[];ds=[];original=[];native_parts=[]
 for ob in node(BF,n):
  a,v,f=native_man(ob);original.append(a);mat=BF.Materials[ob.Attributes.MaterialIndex].Name
  if mat=='M_Grey_Brick':bs.append(a);native_parts.append(part({'type':'polyhedron','vertices':v.tolist(),'faces':f.tolist()},'M_V19_Perimeter_Brick'));continue
  assert mat=='M_Stone_Rubble',mat;t=v[f];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);top=t[nn[:,2]>.7*np.linalg.norm(nn,axis=1)].reshape(-1,3);co=np.linalg.lstsq(np.c_[top[:,:2],np.ones(len(top))],top[:,2],rcond=None)[0];xmin,ymin=v[:,:2].min(0)-.1;xmax,ymax=v[:,:2].max(0)+.1;xy=np.array([[xmin,ymin],[xmax,ymin],[xmax,ymax],[xmin,ymax]]);h=np.c_[xy,np.ones(4)]@co-.56;vv=np.vstack([np.c_[xy,np.full(4,-8.)],np.c_[xy,h]]);clip=manifold({'type':'polyhedron','vertices':vv.tolist(),'faces':[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]});lo=a^clip;da=a-lo
  if not lo.is_empty():ls.append(lo);native_parts.append(part(fromman(lo),'M_V19_Perimeter_Rubble'))
  if not da.is_empty():ds.append(da);native_parts.append(part(fromman(da),'M_V19_Perimeter_Dark_Stone'))
 brick=addall(bs);lower=addall(ls);dark=addall(ds);before=addall(original);after=brick+lower+dark;dv=(before-after).volume()+(after-before).volume();assert abs(dv)<1e-6,dv
 if n.endswith('_0'):
  # The fitted upper core begins at 2.14 m and overlaps the native 2.15 m head.
  fitted=addall([manifold(p['geometry']) for p in e['parts'] if p['material']=='M_V19_Perimeter_Brick']);screenmask=mf.Manifold.cube([7.55,.82,2.5]).translate([3.25,-17.4,2.14]);screen=fitted^screenmask;assert screen.volume()>2;brick+=screen;native_parts.append(part(fromman(screen),'M_V19_Perimeter_Brick'))
 e['parts']=native_parts;e['v19_native_wall_source']='V18 actual native facet geometry; original brick units retained individually to preserve cropped corner wedges';e['v19_note']='Authoritative brick solids and retaining envelope preserved; native stone solids partitioned into rubble and dark courses';targets[n]=e;correction['walls'].append({'node':n,'native_material_partition_symmetric_volume_m3':dv,'source_native_objects':len(original),'retained_individual_native_units':True})
 print('AUTHORITATIVE WALL PARTITION',n,flush=True)
de=next(e for e in Q['add'] if e['name']=='SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES');nb=de['v19_backing_piece_count'];mask=mf.Manifold.cube([7.55,1.,6.]).translate([3.25,-17.6,-2.5]);ps=[];removed=0;removed_volume=0
for j,p in enumerate(de['parts']):
 if j<nb-1:
  aa=manifold(p['geometry']);bb=aa-mask;removed_volume+=max(0,aa.volume()-bb.volume())
  if bb.volume()<1e-10:removed+=1;continue
  p=part(fromman(bb),p['material'])
 ps.append(p)
de['parts']=ps;de['v19_backing_piece_count']=nb-removed;de['v19_mid_screen_old_band_removed']=True;targets[de['name']]=de;correction.update(removed_mid_screen_band_pieces=removed,removed_mid_screen_band_volume_m3=removed_volume);print('OBSOLETE MID SCREEN BAND REMOVED',removed,flush=True)
# Complete the missing wedge between the two inherited independently squared wall ends.
cn='SITE_V19_JOINED_PERIMETER_NORTHWEST_MASONRY_MITER';corner=np.array([-25.0025,5.6025]);rr=[]
for wall in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 cand=[r for r in FD['brick'] if r['node']==wall and np.linalg.norm(np.array(r['b'])-np.array(r['a']))>.34];r=min(cand,key=lambda r:min(np.linalg.norm(np.array(r[k])-corner) for k in ['a','b']));p=min([np.array(r[k]) for k in ['a','b']],key=lambda p:np.linalg.norm(p-corner));u=np.array(r['b'])-np.array(r['a']);u/=np.linalg.norm(u);rr.append((p,u,np.array(r['normal'])))
(p0,u0,n0),(p1,u1,n1)=rr
def crosspoint(a,b):return a+u0*np.linalg.solve(np.column_stack([u0,-u1]),b-a)[0]
outer=crosspoint(p0,p1);inner=crosspoint(p0-.32*n0,p1-.32*n1);poly=MultiPoint([outer,p0,p0-.32*n0,inner,p1-.32*n1,p1]).convex_hull.buffer(.002,join_style=2);zz=[]
for ob in node(BF,'SITE_PERIMETER_JOINED_RETAINING_WALL_0'):
 a,v,f=native_man(ob);near=v[np.linalg.norm(v[:,:2]-p0,axis=1)<.005]
 if len(near):zz.append((BF.Materials[ob.Attributes.MaterialIndex].Name,near[:,2].min(),near[:,2].max()))
stonetop=next(z2 for m,z1,z2 in zz if m=='M_Stone_Rubble');base=next(z1 for m,z1,z2 in zz if m=='M_Stone_Rubble');crest=next(z2 for m,z1,z2 in zz if m=='M_Grey_Brick');cp=[]
for za,zb,mat in [(base-.001,stonetop-.56+.001,'M_V19_Perimeter_Rubble'),(stonetop-.56-.001,stonetop+.001,'M_V19_Perimeter_Dark_Stone'),(stonetop-.001,crest+.001,'M_V19_Perimeter_Brick')]:
 cp.append(part(fromman(manifold({'type':'prism_holes','outer':list(poly.exterior.coords)[:-1],'holes':[],'z':float(za),'height':float(zb-za)})),mat))
ce={'name':cn,'layer':'60_SITE','family':'SITE_MODEL','confidence':'PHOTO_FIT','parts':cp,'source':'Registered shared northwest wall endpoint; existing fitted miter coping; INSV 890 s wall finish reference','classification':'POSITIVE_MASONRY_MITER_CLOSURE','v19_perimeter':True,'v19_join_plan':list(poly.exterior.coords)[:-1],'v19_contact_overlap_m':.002,'v19_wall_heads_m':[float(base),float(stonetop),float(crest)]};targets[cn]=ce
if any(e['name']==cn for e in Q['add']):Q['add']=[ce if e['name']==cn else e for e in Q['add']]
else:Q['add'].append(ce)
if cn not in AQ['changed_nodes']:AQ['changed_nodes'].append(cn)
correction['northwest_miter']={'outer_corner':outer.tolist(),'inner_corner':inner.tolist(),'plan':list(poly.exterior.coords)[:-1],'overlap_m':.002};print('NORTHWEST MASONRY MITER READY',flush=True)
to_delete=[ob for n in targets for ob in node(F,n)];ids={str(ob.Attributes.Id) for ob in to_delete};AQ['created']=[r for r in AQ['created'] if r['id'] not in ids];AQ['deleted']+=[{'id':str(ob.Attributes.Id),'name':ob.Attributes.Name,'reason':'Superseded V19 validation draft mesh'} for ob in to_delete]
for ob in to_delete:F.Objects.Delete(ob.Attributes.Id)
for n,e in targets.items():
 gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr)
 for j,p in enumerate(e['parts']):
  mm=make(p['geometry'],p['material'],n);at=rh.ObjectAttributes();at.Name=f'{n}__{j+1}';at.LayerIndex=next(l.Index for l in F.Layers if l.Name=='60_SITE');at.AddToGroup(gid);at.MaterialIndex=next(i for i,m in enumerate(F.Materials) if m.Name==p['material']);at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[at.MaterialIndex].DiffuseColor;at.SetUserString('V19_Node',n);at.SetUserString('V19_Reference','INSV anchor 890s and same wall walk; V18 authoritative native wall');at.SetUserString('Dimension_Status','PHOTO_FIT');ident=F.Objects.Add(mm,at);AQ['created'].append({'id':str(ident),'name':at.Name,'node':n,'geometry_hash':gh(mm),'closed_expected':True})
existing={e['name'] for e in S['elements']};S['elements']=[targets.get(e['name'],e) for e in S['elements']]+[e for n,e in targets.items() if n not in existing];sp=O/'08_Editable_Source/Architecture_Scene_V19.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V19_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();assert F.Write(str(P),8)
if not any(r['name']==cn for r in I):I.append({'name':cn,'file':'Native_Readback/NATIVE_'+cn+'.npz'})
for r in I:
 n=r['name']
 if n not in targets:continue
 e=targets[n];vv=[];ff=[];uv=[];nn=[];mi=[];mats=[];oo=node(F,n)
 for ob in oo:
  mm=ob.Geometry;mat=F.Materials[ob.Attributes.MaterialIndex].Name
  if mat not in mats:mats.append(mat)
  off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
  for f in mm.Faces:ff.append((np.array(f[:3])+off).tolist());mi.append(mats.index(mat))
 np.savez_compressed(O/'02_Data'/r['file'],vertices=np.array(vv),faces=np.array(ff,np.int32),uv=np.array(uv),normals=np.array(nn),material_ids=np.array(mi,np.int32));r.update(materials=mats,triangles=len(ff),native_objects=len(oo),element={k:v for k,v in e.items() if k!='parts'})
for fn in ['Native_Readback_Index_V19.json','Modeled_Index_V19.json']:(O/'02_Data'/fn).write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf8')
AQ.update(status='AWAITING_FINAL_CORRECTED_READBACK',native_objects=len(F.Objects),nodes=len(I),final_native_corrections=correction);proof.setdefault('native_correction_history',[]).append(proof.get('final_native_corrections',{}));proof['final_native_corrections']=correction
(O/'06_Report/V19_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V19_Design_Control.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8');(D/'Design_Control.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
for fp in [D/'Mutation.json',O/'08_Editable_Source/Mutation_V19.json']:fp.write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
print('V19 FINAL NATIVE CORRECTIONS SAVED',len(F.Objects),P.stat().st_size,flush=True)
