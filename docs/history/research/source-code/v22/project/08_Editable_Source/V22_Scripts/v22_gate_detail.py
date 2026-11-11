from v22_common import *
D=W/'v22_gate';D.mkdir(exist_ok=True);Q=start();checks=[]
GRAY='M_V21_GATE_REF_04';WOOD='M_V21_GATE_REF_06'
Q['materials']['M_V22_Gate_Aged_Bronze']={'color':[101,81,53],'roughness':.50,'metallic':.7}
# Organic plant relief replaces the former isolated straight triangular leaves.
# A shallow stone panel is embedded in the native pier, supporting every stem.
panels=[]
for cx in [5.195,8.005]:
 for lo,hi in [(-.18,.46),(.78,2.31)]:
  ms=[cube([cx-.158,-11.927,lo],[.316,.061,hi-lo])]
  zc=(lo+hi)/2
  if hi>1:
   for k in range(3):
    z0=lo+.05;z1=hi-.06;xx=cx+(k-1)*.065
    pts=[[xx+.018*math.sin(t*4+k),z0+t*(z1-z0)] for t in np.linspace(0,1,35)]
    ms.append(stroke(pts,.007,.019).translate([0,-11.944,0]))
    for j,t in enumerate(np.linspace(.19,.88,5)):
     z=z0+t*(z1-z0);side=-1 if (j+k)%2 else 1
     ms.append(petal(xx+side*.050,z+.025,.145,.044,50 if side>0 else 130,.024).translate([0,-11.947,0]))
  else:
   ms.append(flower(cx,zc+.07,.142,.027).translate([0,-11.950,0]))
   stem=[[cx-.09+.18*t,lo+.035+.10*math.sin(t*4)] for t in np.linspace(0,1,30)]
   ms.append(stroke(stem,.008,.018).translate([0,-11.943,0]))
   for xx,a in [(cx-.085,25),(cx+.080,150)]:ms.append(petal(xx,lo+.12,.13,.065,a,.022).translate([0,-11.948,0]))
  panels.append(pp(uni(ms),GRAY))
put(Q,'SITE_V21_GATE_REFERENCE_LAYER_04',panels,classification='CURVILINEAR_BAMBOO_AND_FLORAL_BAS_RELIEF',motif_status='Ideal-image inspired curved botanical contours; no claim of exact hand-carving reproduction')

# The real portal has a dark wooden upper fixed panel under a carved stone
# header. The former low stone band incorrectly occupied the wood transom.
header=cube([5.338095,-11.8084,2.435],[2.52381,.4264,.2643]);parts=[pp(header,'M_V21_GATE_REF_05')]
for cx in [5.78,6.60,7.42]:
 frame=rectframe(cx-.373,cx+.373,2.463,2.671,-11.827,.016,.020)
 motif=flower(cx,2.567,.083,.022)
 for side in [-1,1]:
  motif+=stroke([[cx+side*t,2.565+.027*math.sin(t*24)] for t in np.linspace(.06,.32,25)],.006,.017)
  motif+=petal(cx+side*.20,2.590,.104,.045,30 if side>0 else 150,.020)
 parts+=[pp(frame+motif.translate([0,-11.843,0]),GRAY)]
put(Q,'SITE_V21_GATE_REFERENCE_LAYER_05',parts,classification='THREE_RECESSED_FLORAL_STONE_HEADER_PANELS')
wood=cube([5.45714,-11.751,2.0833],[2.28572,.325,.3547]);trim=[]
trim.append(rectframe(5.485,7.715,2.114,2.410,-11.768,.021,.021))
trim.append(rectframe(5.485,7.715,2.114,2.410,-11.426,.021,.022))
put(Q,'SITE_V21_GATE_REFERENCE_FIXED_TIMBER_TRANSOM',[pp(wood,WOOD),pp(uni(trim),'M_V21_GATE_REF_07')],classification='REAL_DARK_WOOD_UPPER_FIXED_PANEL_AND_MOULDED_BORDER')
rear=[]
for x in [5.105,7.785]:
 panel=cube([x,-11.304,-.404],[.310,.045,2.475])
 borders=[rectframe(x+.018,x+.292,z0,z1,-11.264,.018,.018) for z0,z1 in [(-.345,.28),(.34,1.88)]]
 rear+=[pp(panel,WOOD),pp(uni(borders),'M_V21_GATE_REF_07')]
put(Q,'GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS',rear,classification='BACK_FACE_NARROW_WOOD_PANELS_SUPPORTED_ON_STONE_PIERS')

# Small cast handles and bottom diamond fields follow the actual moving leaves.
DM={r['name']:r for r in json.loads((B/'02_Data/Door_Manifest_V21.json').read_text(encoding='utf8'))['doors']}
for n in ['SITE_V20_INNER_GATE__LEAF_L','SITE_V20_INNER_GATE__LEAF_R']:
 r=DM[n];pivot=np.array(r['hinge_local_m']);ang=r['open_angle_deg'];m=raw(n).translate((-pivot).tolist()).rotate([0,0,-ang]).translate(pivot.tolist());bb=m.bounding_box()
 ps=[copy.deepcopy(p) for p in E[n]['parts'] if not any(s in p.get('reference_object_name','') for s in ['拉环','门环','铜环','拉手'])]
 cx=(bb[0]+bb[3])/2;y=bb[1]-.005;z=bb[2]+.31;diam=[]
 for x in np.linspace(bb[0]+.20,bb[3]-.20,3):diam.append(prismxz([[x-.055,z],[x,z+.055],[x+.055,z],[x,z-.055]],y,.052))
 ornament=uni(diam).translate((-pivot).tolist()).rotate([0,0,ang]).translate(pivot.tolist());ps.append(pp(ornament,'M_V21_GATE_REF_07'))
 hx=bb[3]-.13 if n.endswith('_L') else bb[0]+.13
 pulls=[cyl(hx,y-.025,.66,.014,.27,24)]
 for zz in [.67,.91]:pulls.append(cube([hx-.019,y-.025,zz],[.038,.085,.032]))
 handle=uni(pulls).translate((-pivot).tolist()).rotate([0,0,ang]).translate(pivot.tolist());ps.append(pp(handle,'M_V22_Gate_Aged_Bronze'))
 put(Q,n,ps,v22_door=True,operation='HINGED_INWARD',v22_detail='Independent inward leaf retains pivot; raised bottom diamonds and cast vertical pull added')

# Replace the visually pointed drip frieze by scalloped stone lace relief.
lace=[]
for x in np.linspace(4.045,9.155,69):
 a=abs((x-6.6)/2.65);ze=2.6058+.08*a*a+.65*a**7
 poly=[[x-.038,ze+.014],[x+.038,ze+.014],[x+.038,ze-.025],[x+.020,ze-.035],[x,ze-.058],[x-.020,ze-.035],[x-.038,ze-.025]]
 lace.append(prismxz(poly,-12.327,.028))
lace=uni(lace);put(Q,'SITE_V21_GATE_REFERENCE_LAYER_13',[pp(lace,'M_V21_GATE_REF_13')],classification='SCALLOPED_DRIP_FRIEZE_REPLACES_LONG_POINTED_TEETH')
# Tile end caps with radial embossing are individual volumetric parts.
ends=[]
for x in np.linspace(4.06,9.14,33):
 a=abs((x-6.6)/2.65);z=2.83+.08*a*a+.58*a**7
 disc=prismxz([[x+.043*math.cos(t),z+.043*math.sin(t)] for t in np.linspace(0,2*math.pi,24,endpoint=False)],-12.315,.038)
 motif=flower(x,z,.029,.008).translate([0,-12.322,0]);ends.append(pp(disc+motif,'M_V21_GATE_REF_10'))
put(Q,'GATE_V22_EMBOSSED_TILE_END_CAPS',ends,classification='ROUNDED_TILE_TERMINALS_WITH_RADIAL_MEDALLION')
# Shallow ceiling rose/light disk is visible in both ideal and real pictures.
disk=cyl(6.6,-11.60,2.524,.128,.019,64);rim=cyl(6.6,-11.60,2.520,.135,.009,64)-cyl(6.6,-11.60,2.519,.124,.012,64)
put(Q,'GATE_V22_PALE_CEILING_DISK',[pp(disk+rim,'M_V21_GATE_CLOSED_PALE_SOFFIT')],classification='PHOTO_CIRCULAR_SOFFIT_LIGHT_DISK')

# Actual column-head carving in the courtyard, facing across the axis.
carved=[]
for y in [-11.24,-8.26,-5.94,-2.96]:
 m=flower(0,2.435,.065,.028);q=m.to_mesh64();v=np.asarray(q.vert_properties)[:,:3];v=np.c_[7.482+v[:,1],y+v[:,0],v[:,2]]
 carved.append(pp(manifold({'type':'polyhedron','vertices':v.tolist(),'faces':np.asarray(q.tri_verts).tolist()}),'M_V12_Kitchen_HONEY_WOOD'))
put(Q,'KITCHEN_V22_CARVED_PROJECTING_TIE_ENDS',carved,classification='FLOWER_CARVED_TIE_HEADS_FITTED_TO_V22_SUPPORTED_CROSS_TIES')
Q['cameras']=[['V22_Inner_Gate_Ideal_Compare',[6.6,-16.1,1.16],[6.6,-11.65,1.52],70],['V22_Inner_Gate_Organic_Detail',[5.99,-13.35,.95],[5.2,-11.89,1.02],58],['V22_Inner_Gate_Rear_Wood',[6.85,-8.22,1.08],[6.58,-11.46,1.20],74]]
Q['change_notes']=['内大门改为三格花卉石门楣及深木上亮，门柱的孤立三角竹叶替换为有连续底板的曲线竹叶、花卉浅浮雕。','按理想图补门楼瓦端圆花、短波形滴水花边及檐底圆盘；院内侧补窄木侧板。双门保持内开，拉手及底部菱饰随门运动。','厨房穿头木外端增加有体积的花形雕刻，接在新增横向穿头木上。']
save(Q,D,checks)
