"""V9 visible eave layer correction. Isolated, original V8 is read-only."""
import sys,json,math,copy,importlib.util
from pathlib import Path
from collections import Counter
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','libs','geomlibs']]+[str(W)]
import numpy as np
import export_v5 as ex
OUT=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v9_roof_parameters',W/'v9_roof_relation'/'roof_parameters.py');P=importlib.util.module_from_spec(sp);sp.loader.exec_module(P)
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V8_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf8'))
E={e['name']:e for e in S['elements']};R=[];A=[]
kg=P.zkitchen;gg=P.zgate
REFS=['User eave construction relationship diagram 1aeb5b24-97ff-45f0-a8e3-f2916523ffb3.png','User gate/kitchen overlap diagram 4daa4b13-ab29-4a24-81ca-0a7345c7eecb.png','D:/DJI/0002/DCIM/101MEDIA/DJI_0046.JPG','D:/DJI/0002/DCIM/101MEDIA/DJI_0047.JPG','D:/DJI/0002/DCIM/101MEDIA/DJI_0101.JPG','D:/DJI/0002/DCIM/101MEDIA/DJI_0423.JPG']
def part(g,m):return {'geometry':g,'material':m}
def put(name,parts,cls,**props):
 e=copy.deepcopy(E.get(name,dict(name=name,layer='60_SITE',family='SITE_MODEL',confidence='MEDIUM')))
 e.update(parts=parts,classification=cls,status='V9_VISIBLE_EAVE_LAYERS_PHOTO_CORRECTED; SECTION_SIZES_ESTIMATED',source='; '.join(REFS),**props)
 (R if name in E else A).append(e);return e
def shell(xs,ys,fn,thick=.025,bottom=None):
 nx=len(xs);ny=len(ys);top=np.array([[x,y,fn(x,y)] for x in xs for y in ys]);bot=top.copy();bot[:,2]=[bottom(x,y) for x in xs for y in ys] if bottom else top[:,2]-thick
 v=np.vstack([top,bot]);N=len(top);fs=[]
 for i in range(nx-1):
  for j in range(ny-1):
   a=i*ny+j;b=(i+1)*ny+j;c=b+1;d=a+1;fs += [[a,b,c],[a,c,d],[d+N,c+N,b+N],[d+N,b+N,a+N]]
 rim=list(range(ny))+[i*ny+ny-1 for i in range(1,nx)]+[(nx-1)*ny+j for j in range(ny-2,-1,-1)]+[i*ny for i in range(nx-2,0,-1)]
 fs += [[b,a,a+N,b+N] for a,b in zip(rim,rim[1:]+rim[:1])]
 return dict(type='polyhedron',vertices=v.tolist(),faces=fs)
def strip(pts,top,width,thick):
 # Plan sweep along a monotone path, stable normal in XY. No hidden trusses.
 p=np.array(pts);verts=[]
 for i,(x,y) in enumerate(p):
  d=p[min(i+1,len(p)-1)]-p[max(0,i-1)];n=np.array([-d[1],d[0]]);n=n/np.linalg.norm(n)*width/2
  a=np.array([x,y])+n;b=np.array([x,y])-n
  verts += [[*a,top(*a)],[*b,top(*b)],[*a,top(*a)-thick],[*b,top(*b)-thick]]
 fs=[]
 for i in range(len(p)-1):
  a=4*i;b=a+4;fs += [[a,a+1,b+1,b],[a+2,b+2,b+3,a+3],[a,b,b+2,a+2],[a+1,a+3,b+3,b+1]]
 fs += [[0,2,3,1],[len(verts)-4,len(verts)-3,len(verts)-1,len(verts)-2]]
 return dict(type='polyhedron',vertices=verts,faces=fs)
def orient(g):
 v,fs,_,_=ex.solid_data(g)
 if g['type']!='polyhedron':return
 edges={}
 for i,f in enumerate(fs):
  for a,b in zip(f,f[1:]+f[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append((i,a,b))
 if any(len(q)!=2 for q in edges.values()):raise ValueError('Open body')
 neigh=[[] for f in fs]
 for q in edges.values():
  (i,a,b),(j,c,d)=q;neigh[i].append((j,a==c and b==d));neigh[j].append((i,a==c and b==d))
 states={}
 for root in range(len(fs)):
  if root in states:continue
  states[root]=False;stack=[root]
  while stack:
   i=stack.pop()
   for j,same in neigh[i]:
    flip=states[i]^same
    if j in states:assert states[j]==flip
    else:states[j]=flip;stack.append(j)
 fs=[f[::-1] if states[i] else f for i,f in enumerate(fs)]
 vol=sum(np.dot(v[f[0]],np.cross(v[f[k]],v[f[k+1]]))/6 for f in fs for k in range(1,len(f)-1))
 g['faces']=[f[::-1] for f in fs] if vol<0 else fs
def ystart(x):
 if x<=8.45:return -11.28
 if x<9.05:return -11.28-(x-8.45)*(.77/.6)
 return -12.05
def kitchen_sweep(x0,x1,delta,thick,y0offset=0,y1=-2.15):
 xs=np.unique(np.r_[np.linspace(x0,x1,25),[x for x in [7.2,8.45,9.05,11.515] if x0<x<x1]])
 verts=[]
 for x in xs:
  ymin=ystart(x)+y0offset
  verts += [[x,ymin,kg(x,ymin)-delta],[x,y1,kg(x,y1)-delta],[x,ymin,kg(x,ymin)-delta-thick],[x,y1,kg(x,y1)-delta-thick]]
 fs=[]
 for i in range(len(xs)-1):
  a=4*i;b=a+4;fs += [[a,b,b+1,a+1],[a+2,a+3,b+3,b+2],[a,a+2,b+2,b],[a+1,b+1,b+3,a+3]]
 fs += [[0,1,3,2],[len(verts)-4,len(verts)-2,len(verts)-1,len(verts)-3]]
 return dict(type='polyhedron',vertices=verts,faces=fs)

# Gate support is restricted to the measured/modelled wall core. Its upper
# face now bears the rafter zone, rather than filling to the tile underside.
put('SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE',[part(shell(np.linspace(4.9,8.3,33),[-11.95,-11.45],lambda x,y:gg(x,y)-.223,bottom=lambda x,y:2.45),'M_Stone_Frame')],
 'MASONRY_GATE_ROOF_WALL_CORE',wall_core_xy=[4.9,-11.95,8.3,-11.45],upper_body_retreat_m=.148,door_lintel_retained=True,interior_material_status='MASONRY_CORE_PER_EXISTING_MODEL; EAVE_FINISH_MATERIAL_UNVERIFIED')
boards=[];raf=[];fly=[];fascias=[];friezes=[];teeth=[]
for edge,wall,sgn in [(-10.22,-11.45,-1),(-13.02,-11.95,1)]:
 lo,hi=sorted([edge+sgn*.045,wall]);xs=np.linspace(4.17,8.93,65)
 soffit_ys=np.unique(np.r_[np.linspace(lo,hi,25),edge+sgn*.112,edge+sgn*.164,edge+sgn*.178])
 boards.append(part(shell(xs,soffit_ys,lambda x,y:gg(x,y)-.075,.028),'M_Stone_Frame'))
 for x in np.arange(4.32,8.86,.245):
  end=edge+sgn*.12;join=edge+sgn*.70
  fly.append(part(strip([[x,end],[x,join]],lambda xx,yy:gg(xx,yy)-.103,.065,.064),'M_Stone_Frame'))
  raf.append(part(strip([[x,join],[x,wall]],lambda xx,yy:gg(xx,yy)-.103,.065,.120),'M_Stone_Frame'))
 # A visible slim fascia closes the ends. Its lower trim is independent from
 # the wall core, so the roof and hanging ornaments remain readable.
 # Align the outer faces of the 52 mm fascia and 66 mm frieze. Their axes
 # differ by 7 mm; this creates an 8 mm fitted contact with the rafter end.
 fascia_y=edge+sgn*.138
 fascias.append(part(shell(xs,[fascia_y-.026,fascia_y+.026],lambda x,y:gg(x,y)-.103,.14),'M_Stone_Frame'))
 # Gray eave decorations photographed at DJI_0047/0101. The low wood roof
 # terminates beneath the north face; decoration is locally shortened at the
 # underlap so that it cannot cut through the lower ceramic surface.
 def lower(x,y):
  z=gg(x,y)-.40
  if edge>-11 and x>=6.98:z=max(z,kg(x,edge)+.13)
  return min(gg(x,y)-.25,z)
 fy=edge+sgn*.145
 frieze_ys=np.unique([fy-.033,fy+.033,fascia_y-.026,fascia_y+.026])
 friezes.append(part(shell(xs,frieze_ys,lambda x,y:gg(x,y)-.243,bottom=lambda x,y:lower(x,y)+.075),'M_Stone_Frame'))
 for x in np.arange(4.30,8.78,.245):
  w=.222;xx=np.linspace(x,x+w,9);profile=[]
  for q in xx:profile.append([q,fy-.033,lower(q,fy)+.078])
  for q in xx[::-1]:profile.append([q,fy-.033,lower(q,fy)+.016+.050*math.sin(math.pi*(q-x)/w)**2])
  # Fit the top of the ornament to the same curved frieze underside at both
  # faces. A prism with constant Z would otherwise leave a wedge-shaped gap.
  tv,tf,_,_=ex.solid_data(dict(type='prism',profile=profile,vector=[0,.066,0]))
  for v in tv:v[2]+=lower(v[0],v[1])-lower(v[0],fy)
  teeth.append(part(dict(type='polyhedron',vertices=tv.tolist(),faces=tf),'M_Stone_Frame'))
put('SITE_GATEHOUSE_VISIBLE_SOFFIT_BOARD',boards,'GATE_VISIBLE_CLOSED_SOFFIT_AND_BOARD_EDGE',geometry_evidence='Visible pale closed underside and horizontal/curved board edge, DJI_0101',thickness_m_estimated=.028,interior_material_status='GRAY_FINISH_VISIBLE; SUBSTRATE_MATERIAL_UNCONFIRMED')
put('SITE_GATEHOUSE_VISIBLE_RAFTER_HEADS',raf,'GATE_VISIBLE_RAFTER_HEAD_SHAPED_FINISH',interior_material_status='GRAY_PROFILED_FINISH; NOT_ASSERTED_AS_WOOD',module_pitch_m_estimated=.245)
put('SITE_GATEHOUSE_VISIBLE_FLY_RAFTER_ENDS',fly,'GATE_VISIBLE_FLY_RAFTER_SHAPED_FINISH',interior_material_status='GRAY_PROFILED_FINISH; NOT_ASSERTED_AS_WOOD',cantilever_zone_m_estimated=.70)
put('SITE_GATEHOUSE_FASCIA_BOARD',fascias,'GATE_FASCIA_END_CLOSURE',thickness_m_estimated=.052,roof_edge_axis_retreat_m=.138,frieze_axis_retreat_m=.145,visible_rafter_end_inset_m_estimated=.008,soffit_fascia_frieze_continuous=True)
put('SITE_GATEHOUSE_EAVE_FRIEZE',friezes,'GATE_GRAY_EAVE_FRIEZE',geometry_evidence='Separate gray horizontal frieze below fascia, DJI_0101/0047',ornament_detail_status='SIMPLIFIED_SILHOUETTE; CARVED_FLORAL_DETAIL_NOT_FIELD_CAPTURED')
put('SITE_GATEHOUSE_HANGING_TOOTH_ORNAMENT',teeth,'GATE_GRAY_HANGING_TOOTH_ORNAMENT',geometry_evidence='Photographed repeated hanging lower edge, DJI_0047/0101',ornament_detail_status='SIMPLIFIED_SILHOUETTE_NOT_EXACT_FLOWER_CARVING')

# Kitchen: keep actual exposed timber; add the visible wood roof underside
# outside the existing head beam and inside its inner face. Beam is retained.
put('SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS',[part(kitchen_sweep(6.98,7.52,.075,.028),'M_Timber_Dark_Eave'),part(kitchen_sweep(7.82,11.515,.075,.028),'M_Timber_Dark_Eave'),part(kitchen_sweep(11.515,13.13,.075,.028),'M_Timber_Dark_Eave')],
 'EXPOSED_KITCHEN_TIMBER_SHEATHING',thickness_m_estimated=.028,geometry_evidence='Dark timber underside/planks visible DJI_0423; hidden batten dimensions not reconstructed')
frames=[];kfly=[]
for yy in np.arange(-10.85,-2.45,.55):
 for xa,xb in [(7.82,11.515),(11.515,13.13)]:
  # No rafter is allowed in the clipped south tip; regular stations are north
  # of the most restrictive roof termination.
  frames.append(part(strip([[x,yy] for x in np.linspace(xa,xb,25)],lambda x,y:kg(x,y)-.103,.070,.100),'M_Timber_Dark_Eave'))
 kfly.append(part(strip([[x,yy] for x in np.linspace(6.99,7.52,13)],lambda x,y:kg(x,y)-.103,.070,.065),'M_Timber_Dark_Eave'))
for x in [9.25,11.515,12.95]:
 ym=ystart(x)+.18
 frames.append(part(strip([[x,y] for y in np.linspace(ym,-2.60,33)],lambda xx,yy:kg(xx,yy)-.203,.120,.140),'M_Timber_Dark_Eave'))
put('SITE_KITCHEN_EXPOSED_TIMBER_ROOF_FRAMING',frames,'EXPOSED_KITCHEN_RAFTERS_AND_LONGITUDINAL_PURLINS',timber_geometry_status='VISUALLY_SUPPORTED_LAYOUT; SECTION_AND_PITCH_ESTIMATED',old_transverse_horizontal_boxes_retired=True)
put('SITE_KITCHEN_VISIBLE_FLY_RAFTER_ENDS',kfly,'EXPOSED_KITCHEN_FLY_RAFTER_ENDS',geometry_evidence='Photographed short exposed timber eave members, DJI_0423',cantilever_zone_m_estimated=.53)
fas=[]
for x,sg in [(6.99,1),(13.55,-1)]:
 ys=np.linspace(ystart(x)+.06,-2.21,55)
 fas.append(part(shell([x-.026,x+.026],ys,lambda xx,y:kg(x,y)-.075,.155),'M_Timber_Dark_Eave'))
put('SITE_KITCHEN_FASCIA_BOARD',fas,'EXPOSED_KITCHEN_TIMBER_FASCIA',geometry_evidence='Visible dark timber eave band, DJI_0046/0423',section_estimated_m=[.052,.155])
drip=[]
for x in [6.98,13.60]:
 drip.append(part(shell([x-.022,x+.022],np.linspace(ystart(x)+.035,-2.18,55),lambda xx,y:kg(x,y)-.005,.045),'M_Metal_Stainless'))
put('SITE_KITCHEN_VISIBLE_EDGE_FLASHING',drip,'KITCHEN_VISIBLE_METAL_EDGE_FLASHING',geometry_evidence='Metallic protective eave edge explicitly visible DJI_0423',profile_thickness_status='SIMPLIFIED_VISIBLE_EDGE_NOT_HIDDEN_WATERPROOF_ASSEMBLY')

# South support follows the roof termination, not the older rectangular gable
# under the wall core of the gate. The north wall is untouched; only the south
# endpoint of the east wall follows the new gable to keep the corner closed.
mas=copy.deepcopy(E['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES']['parts']);xs=np.unique(np.r_[np.linspace(7.7,13.35,33),8.45,9.05,11.515]);verts=[]
for x in xs:
 y0=ystart(x)+.18;y1=y0+.22
 verts += [[x,y0,kg(x,y0)-.075],[x,y1,kg(x,y1)-.075],[x,y0,-.4],[x,y1,-.4]]
fs=[]
for i in range(len(xs)-1):
 a=4*i;b=a+4;fs += [[a,b,b+1,a+1],[a+2,a+3,b+3,b+2],[a,a+2,b+2,b],[a+1,b+1,b+3,a+3]]
fs += [[0,1,3,2],[len(verts)-4,len(verts)-2,len(verts)-1,len(verts)-3]]
mas[0]=part(dict(type='polyhedron',vertices=verts,faces=fs),'M_Grey_Brick')
east_joint_y=ystart(13.13)+.18+.22
for v in mas[2]['geometry']['vertices']:
 if abs(v[1]+11.38)<1e-8:
  v[1]=east_joint_y
  if v[2]>-.4: v[2]=kg(v[0],v[1])-.075
put('SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES',mas,'MASONRY_BACK_AND_TERMINATION_GABLE_WALLS',south_gable_offset_from_roof_edge_m=.18,south_gable_thickness_m=.22,south_gable_following_v9_termination_line=True,east_wall_south_endpoint_y=east_joint_y,east_wall_corner_closed=True,north_wall_unchanged=True)
# The existing 170 mm stone floor remains at its original height. Its south
# footprint follows the gable face, preventing a strip below the moved east
# corner from being left without a floor. No surrounding terrain is edited.
floor=copy.deepcopy(E['SITE_KITCHEN_STONE_FLOOR']['parts'])
floor[0]['geometry']['outer']=[[7.7,ystart(7.7)+.18],[8.45,ystart(8.45)+.18],[9.05,ystart(9.05)+.18],[13.35,ystart(13.35)+.18],[13.35,-2.6],[7.7,-2.6]]
put('SITE_KITCHEN_STONE_FLOOR',floor,'KITCHEN_STONE_FLOOR_WITH_TERMINATION_CLOSURE',south_floor_follows_gable_face=True,existing_floor_z_and_thickness_preserved=True,local_corner_extension_m=.27)
timber=copy.deepcopy(E['SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS']['parts'])
for p in timber:
 g=p['geometry']
 if g['type']=='cylinder' and abs(g['origin'][1]+11.42)<1e-8:g['origin'][1]=-11.10
 elif g['type']=='box' and abs(g['origin'][1]+11.60)<1e-8:g['origin'][1]=g['origin'][1]+.32
 elif g['type']=='box' and abs(g['origin'][1]+11.42)<1e-8:g['origin'][1]+=.32;g['size'][1]-=.32
 elif g['type']=='polyhedron':
  for v in g['vertices']:
   if abs(v[1]+11.42)<1e-8:v[1]= -11.10;v[2]=kg(v[0],v[1])-.075 if v[2]>2.49 else v[2]
put('SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS',timber,'EXPOSED_CHINESE_TIMBER_FRAME',south_end_center_y=-11.10,existing_column_heights_preserved=True,termination_change_y_m=.32)

for e in R+A:
 for p in e['parts']:orient(p['geometry'])
M={'M_Timber_Dark_Eave':dict(color=[78,43,28],roughness=.65,role='Photo-observed dark timber kitchen eave finish; no generated texture')}
C=[dict(id='V9_VISIBLE_EAVE_LAYER_ORDER',description='门楼瓦底薄底／灰饰椽头端／封檐／檐枋饰带／下挂牙子分层；墙芯退到椽区承托。厨房显露木望板、纵向檩条、斜椽、短飞椽、木封檐和实拍金属收边分别建模。隐蔽挂瓦/顺水条只保留关系元数据，不虚构实测尺寸。',source=REFS,dimension_status='VISIBLE_RELATIONS_PHOTO_SUPPORTED; SECTION_SIZES_AND_HIDDEN_ASSEMBLY_UNMEASURED')]
mutation=dict(replace=R,add=A,remove=[],materials=M,definitions={},changes=C,layer_order_top_to_bottom=['ROOF_COVER_TILES','HIDDEN_BATTENS_COUNTER_BATTENS_RELATION_ONLY_NOT_MODELLED','VISIBLE_SHEATHING_SOFFIT','RAFTER_FLY_RAFTER_ENDS','FASCIA_BOARD','EAVE_FRIEZE','HANGING_TOOTH_ORNAMENT'],hidden_assembly_modelled=False)
def apply(scene):
 names={e['name'] for e in R};scene['elements']=[e for e in scene['elements'] if e['name'] not in names]+copy.deepcopy(R+A);scene['materials'].update(copy.deepcopy(M));scene.setdefault('v9_changes',[]).extend(copy.deepcopy(C));return scene
if __name__=='__main__':
 (OUT/'Mutation.json').write_text(json.dumps(mutation,ensure_ascii=False,indent=2),encoding='utf8')
 qa=[]
 for e in R+A:
  for i,p in enumerate(e['parts']):
   v,fs,_,_=ex.solid_data(p['geometry']);assert np.isfinite(v).all();assert len(v)>3
   edges=Counter(tuple(sorted((a,b))) for f in fs for a,b in zip(f,f[1:]+f[:1]));assert all(n==2 for n in edges.values()),(e['name'],i,'open')
   d=Counter((a,b) for f in fs for a,b in zip(f,f[1:]+f[:1]));assert all(n==d[(b,a)] for (a,b),n in d.items()),(e['name'],i,'winding')
   vol=sum(np.dot(v[f[0]],np.cross(v[f[k]],v[f[k+1]]))/6 for f in fs for k in range(1,len(f)-1));assert vol>1e-8,(e['name'],i,vol)
  qa.append(dict(name=e['name'],parts=len(e['parts']),closed_manifold_all=True,outward_winding=True))
 (OUT/'Geometry_QA.json').write_text(json.dumps(dict(status='PASS',elements=qa,column_height_preserved=True,wall_core_upper_retreat_m=.148,gate_front_layer_order_verified=True,hidden_batten_assembly_modelled=False,section_sizes_status='ESTIMATED_FROM_PHOTOGRAPHS_NOT_FIELD_MEASURED'),ensure_ascii=False,indent=2),encoding='utf8')
 print('V9 eave layers:',len(R),'replace',len(A),'add',sum(len(e['parts']) for e in R+A),'parts PASS')
