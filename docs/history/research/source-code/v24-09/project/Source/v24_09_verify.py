import bpy,sys,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_09_common import *
from v24_03_junction_blender import _bounds,_tree,_closed_stats
from v24_09_roof import h,X0,X1,CY,HY,JL,JR
base=json.loads((R/'V24_09_Before_Snapshot.json').read_text());delta=json.loads((R/'V24_09_Changes.json').read_text());build=json.loads((R/'V24_09_Build.json').read_text());checks=[]
def ck(n,ok,**kw):checks.append({'check':n,'pass':bool(ok),**kw})
bpy.ops.wm.open_mainfile(filepath=str(B));original={}
for n in['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry']:
 o=bpy.data.objects[n];original[n]=q._world(o.data,o.matrix_world)
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();allowed=set(delta['allowed_objects'])
ck('Only screen-wall roof upper mouldings and local finish changed',set(delta['changed_objects'])<=allowed);ck('No existing objects removed',not delta['removed_objects'])
for n,r in base['materials'].items():ck('Original shader '+n,n in bpy.data.materials and q._material(bpy.data.materials[n])['hash']==r['hash'])
for n,r in base['images'].items():ck('Original packed image '+n,n in bpy.data.images and q._image(bpy.data.images[n])==r)
for n,r in base['actions'].items():ck('Original action '+n,n in bpy.data.actions and q._action(bpy.data.actions[n])==r)
for n,r in base['objects'].items():
 o=bpy.data.objects.get(n);ck('Retained scene object '+n,o is not None)
 if o is None:continue
 ck('Original transform parent visibility animation '+n,q._matrix(o.matrix_world)==r['matrix']and(o.parent.name if o.parent else None)==r['parent']and o.hide_render==r['hide_render']and q._animation(o)==r['animation'])
 if r['mesh_hash']and n not in allowed:ck('Original geometry UV and material slots '+n,q._mesh_hash(o.data)==r['mesh_hash'])
for n,dig in delta['expected_mesh_hashes'].items():ck('Saved mesh digest '+n,q._mesh_hash(bpy.data.objects[n].data)==dig)
for f,poses in base['door_poses'].items():
 sc.frame_set(int(f));bpy.context.view_layer.update()
 for n,m in poses.items():ck('Original door pose '+n+' frame '+f,q._matrix(bpy.data.objects[n].matrix_world)==m)
sc.frame_set(40);bpy.context.view_layer.update()
for n in delta['roof']['changed_objects']+delta['roof'].get('added_objects',[])+delta['facade']['added_objects']:
 s=_closed_stats(bpy.data.objects[n]);ck('Closed positive screen-wall component '+n,s['boundary_edges']==0 and s['nonmanifold_edges']==0 and s['volume_m3']>0,**s)
for n,old in original.items():
 now=q._world(bpy.data.objects[n].data,bpy.data.objects[n].matrix_world);ck('Original wall vertex count '+n,now.shape==old.shape)
 if now.shape==old.shape:
  diff=now-old;zone=(old[:,0]>=3.2499)&(old[:,0]<=10.8001)&(old[:,1]>=-17.56)&(old[:,1]<=-16.25)&(old[:,2]>2.65)
  ck('Original wall plan and foundation fixed '+n,float(np.abs(diff[:,:2]).max())<1e-6 and float(np.abs(diff[~zone]).max())<1e-6,maximum_xy_displacement_m=float(np.abs(diff[:,:2]).max()),maximum_other_region_displacement_m=float(np.abs(diff[~zone]).max()))
  ck('Crown stays within local contact adjustment '+n,float(np.abs(diff[:,2]).max())<.31,maximum_z_displacement_m=float(np.abs(diff[:,2]).max()))
roof=bpy.data.objects['SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL_Geometry'];a,b=_bounds(roof);ck('Registered screen roof length and depth retained',max(abs(a[0]-X0),abs(b[0]-X1),abs(a[1]-(CY-HY)),abs(b[1]-(CY+HY)))<1e-5,bounds=[a,b])
fin=bpy.data.objects['SITE_SOUTH_SCREENWALL_V12_HIGH_RIDGE_FINIALS_Geometry'];pts=q._world(fin.data,fin.matrix_world);corners=[]
for x in[X0,X1]:
 for side in[-1,1]:
  sel=(np.abs(pts[:,0]-x)<.09)&(np.abs(pts[:,1]-(CY+side*HY))<.15);corners.append(bool(sel.any()and pts[sel,2].max()>5.10))
ck('Four corner terminals, each connected to a branch',all(corners)and delta['roof']['fork_arm_count']==4 and delta['roof']['wing_terminal_count']==4)
ck('Central independent spear removed',not np.any(np.abs(pts[:,1]-CY)<.50));ck('No unintended extra overall height',pts[:,2].max()<5.31,maximum_tip_z_m=float(pts[:,2].max()))
forks=delta['roof']['fork_paths'];ck('Two actual Y-shaped ridge junctions',len(forks)==4 and math.dist(forks[0][0],forks[1][0])<1e-6 and math.dist(forks[2][0],forks[3][0])<1e-6 and forks[0][-1][1]<CY<forks[1][-1][1]and forks[2][-1][1]<CY<forks[3][-1][1]);ck('Transverse ceramic end fans built',delta['roof']['hip_fan_cover_tile_units']>=10)
seat=_tree(bpy.data.objects['V24_09_Screenwall_Solid_Fork_and_Ridge_Seats']);seat_checks=[]
for path in forks:
 for j in[8,16,24]:
  # Sample inside each loft segment, rather than exactly on its shared edge.
  x,y,z=[path[j][k]*.63+path[j+1][k]*.37 for k in range(3)];hh=h(x,y);top=seat.ray_cast(Vector((x,y,7)),Vector((0,0,-1)),10)[0];bot=seat.ray_cast(Vector((x,y,hh-1.0)),Vector((0,0,1)),3)[0];seat_checks.append({'xy':[x,y],'top_z':top.z if top else None,'bottom_z':bot.z if bot else None,'roof_surface_z':hh})
ck('Every fork roll has solid bedding embedded into the roof skin',all(r['top_z']is not None and r['bottom_z']is not None and r['top_z']>r['roof_surface_z']+.04 and r['bottom_z']<r['roof_surface_z']-.020 for r in seat_checks),samples=seat_checks)
lat=_tree(bpy.data.objects['SITE_SOUTH_SCREENWALL_OPEN_RIDGE_LATTICE_Geometry']);holes=[];count=delta['roof']['diamond_openings']
for i in range(count):
 x=JL+(JR-JL)*(i+.5)/count;p,no,f,d=lat.ray_cast(Vector((x,CY-.20,h(x,CY)+.127)),Vector((0,1,0)),.40);holes.append(p is None)
ck('Actual open negative spaces in all diamond cells',all(holes),clear_cells=sum(holes),total_cells=count)
ck('Seven alternating long-short panels on both sides',delta['facade']['panels_per_face']==7 and delta['facade']['sides']==2 and len(delta['facade']['panel_spans_x_m'])==7);ck('Two solid framed white end panels',delta['facade']['end_inset_panels']==2)
ck('Single continuous closed curved stepped support',bpy.data.objects['SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE_Geometry']['V24_09_Closed_Parts']==1)
for n in ['SITE_KITCHEN_STONE_FLOOR_Geometry','V24_03_Kitchen_Single_Veranda_Column','SITE_V12_REBUILT_COURT_0_-20_0_Geometry']:
 ck('Previous kitchen retreat and courtyard paving retained '+n,q._mesh_hash(bpy.data.objects[n].data)==base['objects'][n]['mesh_hash'])
gate=[o for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')];ck('Accepted gate soffit remains 3.10m',abs(min(_bounds(o)[0][2]for o in gate)-3.10)<1e-5);ck('15 stone relief fields and 26 moving doors retained',len([o for o in bpy.data.objects if o.name.startswith('V24_Gate_Reference_Relief_')])==15 and len(base['doors'])==26)
ck('No clay material override',all(v.material_override is None for v in sc.view_layers));ck('Build and saved file SHA agree',sha(P)==build['sha256']);ck('Input V24.08 remains unchanged',sha(B)==build['source_sha256'])
im=bpy.data.images.get(delta['plaster']['packed_image']);ck('Actual plaster photograph packed with original unmodified bytes',im is not None and im.packed_file is not None and delta['plaster']['source_unmodified_sha256']==delta['plaster']['packed_sha256']);ck('Original UV channels retained alongside explicit photograph UV',all(u.name!='V24_09_Actual_Plaster_Projective'for u in bpy.data.objects['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry'].data.uv_layers)and bpy.data.objects['SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry'].data.uv_layers.get('V24_09_Actual_Plaster_Projective')is not None)
fail=[c for c in checks if not c['pass']];out={'status':'PASS_V24_09_FRESH_BLEND_QA'if not fail else'FAIL_V24_09_FRESH_BLEND_QA','model_sha256':sha(P),'checks':checks,'failures':fail,'original_materials':len(base['materials']),'original_images':len(base['images']),'moving_doors':len(base['doors'])};write('V24_09_Fresh_Blend_QA.json',out);print(out['status'],len(checks),len(fail),flush=True)
if fail:raise AssertionError(json.dumps(fail[:20],ensure_ascii=False))
