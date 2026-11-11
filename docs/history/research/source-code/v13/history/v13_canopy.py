import sys,json,math,hashlib,copy,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
O=Path(r'E:\jz\JIA\Rebuild_V13');P=O/'08_Editable_Source/Architecture_Scene_V13.json'
S=json.loads(P.read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};old=copy.deepcopy(E);changes=[]
def panel_under(y):return 10.17+(y-1)*.18/5.65
def box(x,y,z,w,d,h):return {'geometry':{'type':'box','origin':[x,y,z],'size':[w,d,h]},'material':'M_Metal_Black'}
def slope_beam(x1,x2,y1,y2,bottom_offset,top_offset):
 z=panel_under(y1);return {'geometry':{'type':'prism','profile':[[x1,y1,z+bottom_offset],[x2,y1,z+bottom_offset],[x2,y1,z+top_offset],[x1,y1,z+top_offset]],'vector':[0,y2-y1,(y2-y1)*.18/5.65]},'material':'M_Metal_Black'}
def touch(name):
 e=E[name];e.update(v13_connection_revision='Photo-supported bearing chain; member dimensions and concealed fixings inferred',v13_evidence=['D:/DJI/0002/DCIM/101MEDIA/DJI_0623.JPG','INSV 175s L0','INSV 200s L1']);changes.append(name);return e
roof=touch('TERRACE_METAL_CANOPY')
for v in roof['parts'][0]['geometry']['vertices']:
 if abs(v[0]-3.45)<1e-8:v[0]=3.81
# The actual photo shows steel framing meeting the tiled building wall.
# Complete the right ends rather than leaving a 350 mm free gap to that wall.
purlins=touch('TERRACE_CANOPY_VISIBLE_PURLINS')
for p in purlins['parts']:
 g=p['geometry']
 if g['type']=='box':g['size'][0]=3.81-g['origin'][0]
# Match the four photographed outer posts and the front return post to
# continuous eave members. Foot positions and slab elevations are unchanged.
for n in ['TERRACE_CANOPY_POST_0','TERRACE_CANOPY_POST_3.3','TERRACE_CANOPY_WEST_SUPPORTS']:
 e=touch(n)
 for p in e['parts']:
  g=p['geometry']
  if g['type']=='box' and g['size'][2]>2:
   yc=g['origin'][1]+g['size'][1]/2;g['size'][2]=panel_under(yc)-.13+.002-g['origin'][2]
new={
 'TERRACE_CANOPY_V13_OUTER_EAVE_BEAM':[slope_beam(-.04,.04,1.105,6.65,-.13,-.035)],
 'TERRACE_CANOPY_V13_SIDE_WALL_LEDGER':[slope_beam(3.705,3.815,1.105,6.65,-.13,-.035)],
 'TERRACE_CANOPY_V13_FRONT_RETURN_BEAM':[box(-.04,1.105,panel_under(1.125)-.13,3.855,.08,.095)]}
for name,parts in new.items():
 assert name not in E
 e={'name':name,'layer':'51_CANOPY','family':'ARCH_MODEL','parts':parts,'source':'DJI_0623 and INSV 175/200s show continuous underside steel frame and posts; modeled connection profile inferred','confidence':'MEDIUM','status':'V13_PHOTO_REFERENCED_BEARING_CONNECTION; NOT_FORCE_CALCULATED','classification':'STEEL_CANOPY_BEARING_MEMBER','dimension_status':'INFERRED_PROFILE; FIELD_MEASUREMENT_PENDING'}
 E[name]=e;S['elements'].append(e);touch(name)
S['revision_notes'].append('V13 canopy transverse framing meets side wall; continuous eave/return bearing members connect existing post feet to roof. Roof right edge corrected to wall line. Concealed anchor details and member sections remain inferred.')
P.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');ex.SCENE=S
C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);T=rh.Transform.Multiply(rh.Transform.Translation(*C['origin']),rh.Transform.Rotation(a,rh.Vector3d(0,0,1),rh.Point3d(0,0,0)))
path=O/'04_Rhino/Architecture_Complete_V13_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(path));obs={ob.Attributes.Name:ob for ob in F.Objects};mids={m.Name:i for i,m in enumerate(F.Materials)};ly={l.Name:l.Index for l in F.Layers};native_changes=[]
def closedmesh(g):
 v,fs,_,_=ex.solid_data(g);m=rh.Mesh();m.Vertices.UseDoublePrecisionVertices=True
 for q in v:m.Vertices.AddPoint3d(*map(float,q))
 for face in fs:
  if len(face)<=4:m.Faces.AddFace(*map(int,face))
  else:
   for t in ex.triangulate(v[face]):m.Faces.AddFace(*[face[j] for j in t])
 m.Normals.ComputeNormals();m.Compact();assert m.IsValid and m.IsClosed;return m
for name in changes:
 e=E[name];gi=None
 for i,part in enumerate(e['parts']):
  n=name+'__'+str(i+1);original=obs.get(n)
  if original:
   at=original.Attributes;ident=at.Id;F.Objects.Delete(ident)
  else:
   if gi is None:
    gr=rh.Group();gr.Name=name;gi=len(F.Groups);F.Groups.Add(gr)
   at=rh.ObjectAttributes();at.Name=n;at.LayerIndex=ly[e['layer']];at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.MaterialIndex=mids[part['material']];at.AddToGroup(gi);ident=None
  g=ex.native(part['geometry']) if part['geometry']['type']=='box' else closedmesh(part['geometry']);g.Transform(ex.rh_transform(e));g.Transform(T)
  at.SetUserString('V13_Element',name);at.SetUserString('V13_Connection','Roof panel > cross members > eave/ledger > posts/wall > slab; geometry reviewed, capacity not calculated');at.SetUserString('Parameters',json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False));newid=F.Objects.Add(g,at)
  if ident:assert newid==ident
  native_changes.append({'id':str(newid),'name':n,'existing':bool(original)})
assert F.Write(str(path),8)
index=json.loads((O/'02_Data/Modeled_Index_V13.json').read_text(encoding='utf8'));rows={r['name']:r for r in index}
for name in changes:
 e=E[name];tris=[];uv=[];materials=[]
 for part in ex.expand_parts(e):
  v,fs=ex.world_part(part,e)
  for face in fs:
   for t in ex.triangulate(v[face]) if len(face)>3 else [[0,1,2]]:
    q=v[[face[j] for j in t]];nn=np.cross(q[1]-q[0],q[2]-q[0])
    if np.linalg.norm(nn)<1e-12:continue
    tris.append(q);axes=[j for j in range(3) if j!=int(np.argmax(abs(nn)))];uv.append(q[:,axes]);materials.append(part['material'])
 v=np.array(tris).reshape(-1,3);faces=np.arange(len(v),dtype=np.int32).reshape(-1,3);mm=list(dict.fromkeys(materials));mi=np.array([mm.index(k) for k in materials],np.int32);fn='MODEL_'+name+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=v,faces=faces,uv=np.array(uv).reshape(-1,2),material_ids=mi)
 rows[name]={'name':name,'file':fn,'materials':mm,'triangles':len(tris),'element':{k:v for k,v in e.items() if k!='parts'}}
(O/'02_Data/Modeled_Index_V13.json').write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2),encoding='utf8')
(O/'06_Report/Canopy_Connection_Changes.json').write_text(json.dumps({'status':'ASSEMBLED_PENDING_ACTUAL_NATIVE_CONTACT_QA','changed_nodes':changes,'native_changes':native_changes,'left_post_footprints_unchanged':True,'all_post_bottoms_unchanged':True,'roof_height_and_slope_unchanged':True,'roof_right_edge_before_m':3.45,'roof_right_edge_after_m':3.81,'source_evidence':['DJI_0623.JPG','Center_L0_0175s.jpg','Center_L1_0200s.jpg'],'force_capacity_calculated':False,'concealed_anchor_fasteners':'Not surveyed; no invented bolt or weld schedule'},ensure_ascii=False,indent=2),encoding='utf8')
for p in [Path(r'D:\DJI\0002\DCIM\101MEDIA\DJI_0623.JPG'),Path(r'E:\jz\JIA\Rebuild_V12\07_Reference\Panorama\Earlier_Interior\Center_L0_0175s.jpg'),Path(r'E:\jz\JIA\Rebuild_V12\07_Reference\Panorama\Earlier_Interior\Center_L1_0200s.jpg')]:shutil.copy2(p,O/'07_Reference'/p.name)
print('updated',len(changes),'nodes,',len(native_changes),'native parts',flush=True)
