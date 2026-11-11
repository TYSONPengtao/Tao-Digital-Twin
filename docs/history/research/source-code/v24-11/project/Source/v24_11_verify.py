import bpy,sys,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
from v24_03_junction_blender import _closed_stats,_bounds
D=W/'v24_11';O=Path('E:/jz/JIA/Rebuild_V24_11');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_11.blend';B=Path('E:/jz/JIA/Rebuild_V24_10/Blender/Architecture_Complete_V24_10.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
checks=[]
def ck(n,p,**data):checks.append({'check':n,'pass':bool(p),**data})
before=json.loads((R/'V24_11_Before_Snapshot.json').read_text(encoding='utf8'));bpy.ops.wm.open_mainfile(filepath=str(P));after=json.loads(json.dumps(snapshot(bpy)));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
change=json.loads((R/'V24_11_Changes.json').read_text(encoding='utf8'));proof=json.loads((R/'V24_11_Corrections.json').read_text(encoding='utf8'));build=json.loads((R/'V24_11_Build.json').read_text(encoding='utf8'));allowed={r['name']for r in change['changed']};gone=set(change['removed']);new=set(change['added']);hashval=sha(P)
ck('Only recorded entrance canopy objects removed',set(before['objects'])-set(after['objects'])==gone)
ck('Only recorded new objects added',set(after['objects'])-set(before['objects'])==new)
for n,a in before['objects'].items():
 if n in gone:continue
 b=after['objects'][n]
 for key in['type','parent','hide_render','animation']:ck('Preserved '+key+' / '+n,a[key]==b[key])
 if n not in allowed:
  for key in['mesh_hash','matrix']:ck('Unchanged '+key+' / '+n,a[key]==b[key])
for n,v in before['materials'].items():ck('Original shader / '+n,after['materials'].get(n)==v)
for n,v in before['images'].items():ck('Original image / '+n,after['images'].get(n)==v)
ck('All original actions and all 26 moving doors preserved',after['actions']==before['actions']and after['doors']==before['doors']and len(after['doors'])==26)
ck('Every door pose identical at frames 1, 20 and 40',after['door_poses']==before['door_poses'])
ck('Independent outer storage canopy preserved',after['objects'][proof['preserved_outer_canopy']]==before['objects'][proof['preserved_outer_canopy']])
ck('Both entrance canopy sheet and frame deleted',all(n not in bpy.data.objects for n in ['V24_10_Entry_Metal_Canopy_Sheet','V24_10_Entry_Canopy_Attached_Frame']))
cols=[o for o in bpy.data.objects if o.name.startswith('V24_11_Storage_Veranda_Column_')and'_Base_'not in o.name];ck('Exactly two veranda columns',len(cols)==2)
for o in cols:
 a,b=_bounds(o);z0=a[2];z1=b[2];vv=np.array([o.matrix_world@v.co for v in o.data.vertices]);lo=vv[vv[:,2]<z0+.01,:2].mean(0);hi=vv[vv[:,2]>z1-.01,:2].mean(0);ck('Vertical shaft / '+o.name,np.linalg.norm(lo-hi)<2e-5,xy_drift_m=float(np.linalg.norm(lo-hi)))
angle=abs(proof['column_axis_degrees']-proof['rail_axis_degrees']);ck('Column axis oblique to the rail in plan',angle>12,relative_angle_degrees=angle)
pp=proof['veranda_columns'];fy=lambda x:-16.6828994751+.10589*(x-13.0393619537);width=[p['center_xy'][1]-fy(p['center_xy'][0])for p in pp];ck('Entry end wider than far end',width[0]>width[1]+1.0,axis_to_rail_distances_y_m=width)
def tree(n):
 o=bpy.data.objects[n];return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons])
mt=tree('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry');p=pp[0]['center_xy'];hits=[]
for z in[.2,1,1.9,2.5]:
 hit=mt.ray_cast(Vector((12.5,p[1],z)),Vector((1,0,0)),2.0);hits.append(bool(hit[0])and hit[0].x<p[0])
ck('Entry column hidden behind gable from the approach',all(hits),occlusion_samples=hits)
# The exact saved roof shell must cover the end of the lower secondary wall.
rt=tree('SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry');wt=tree('SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING_Geometry');over=[]
for x in[12.96,13.04,13.10]:
 for y in[-16.68,-16.77]:
  r=rt.ray_cast(Vector((x,y,6)),Vector((0,0,-1)),8)[0];w=wt.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),6)[0];over.append({'x':x,'y':y,'roof_z':r.z if r else None,'wall_cap_z':w.z if w else None,'pass':bool(r and w and r.z-w.z>.03)})
ck('Secondary screen wall lies under the storage eave',all(r['pass']for r in over),samples=over)
white=bpy.data.materials[proof['plain_white_material']];ck('White limewash shader has no image nodes',not any(n.type=='TEX_IMAGE'for n in white.node_tree.nodes))
o=bpy.data.objects['SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry'];cnt=sum(p.material_index<len(o.data.materials)and o.data.materials[p.material_index]==white for p in o.data.polygons);ck('Main screen-wall inner face uses the new plain white shader',cnt>=800,white_faces=cnt)
ck('No photographic plaster slot remains on screen wall',all(m.name!='M_V24_09_Screenwall_Aged_Lime'for m in o.data.materials))
# Probe across the entire curved rear wall at several heights, including its
# overlap with the retaining foundation. A single native masonry body closes it.
curve=np.array(proof['back_curve']);rays=[]
for k in range(2,len(curve)-2,6):
 x,y=curve[k];a=curve[k-1];b=curve[k+1];t=(b-a)/np.linalg.norm(b-a);no=Vector((-t[1],t[0],0))
 for z in[-.35,.2,1.4,2.5]:
  q=Vector((x,y,z));hit=mt.ray_cast(q+no*.4,-no,1.)[0];rays.append(bool(hit))
ck('Curved back wall continuous to the base at all tested sections',all(rays),probe_count=len(rays));ck('Kitchen and storage masonry form one connected solid',proof['masonry_connected_bodies']==1)
kpath=np.array(proof['kitchen_continuous_wall_trace']);rays=[]
for a,b in zip(kpath[:-1],kpath[1:]):
 u=(b-a)/np.linalg.norm(b-a);no=Vector((-u[1],u[0],0))
 for t in[.2,.5,.8]:
  xy=a+(b-a)*t
  for z in[-.35,.2,1.4,2.6]:
   p=Vector((*xy,z));hit=mt.ray_cast(p+no*.4,-no,1)[0];rays.append(bool(hit))
ck('Kitchen rear cheek is uninterrupted from plinth to eave',all(rays),probe_count=len(rays))
ck('No overlapping exposed wall and footing skins',abs(proof['wall_footing_overlap_volume_m3'])<1e-8,intersection_volume_m3=proof['wall_footing_overlap_volume_m3']);ck('Local retaining footing remains one connected body',proof['continuous_footing_bodies']==1)
ob=bpy.data.objects['SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE_Geometry'];tr=tree(ob.name);level=[]
for x in[3.5,5,7.025,9,10.5]:
 zz=[]
 for y in[-17.15,-16.90,-16.65]:
  p=tr.ray_cast(Vector((x,y,2)),Vector((0,0,1)),4)[0];zz.append(p.z if p else 99)
 level.append(max(zz)-min(zz))
ck('Screen-wall stone soffit level across its depth',max(level)<2e-5,maximum_cross_depth_z_difference_m=max(level));ck('Screen-wall stepped foot is one closed body',proof['screenwall_plinth']['one_closed_body'])
# Export only changed/new saved mesh geometry for independent solid checking.
rows=[];native_stats={}
for n in sorted(allowed|new):
 o=bpy.data.objects.get(n)
 if not o or o.type!='MESH':continue
 s=_closed_stats(o);native_stats[n]=s;o.data.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in o.data.vertices]);f=np.array([tuple(t.vertices)for t in o.data.loop_triangles]);fn=f'SOLID_{len(rows):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);rows.append({'name':n,'file':fn,'native_stats':s})
(D/'Solid_Export_Index.json').write_text(json.dumps({'model_sha256':hashval,'objects':rows},indent=2),encoding='utf8')
obstacles=['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry','SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry','SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES_Geometry','SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry','DOOR_STORAGE_V20_L__LEAF_Geometry','DOOR_STORAGE_V20_R__LEAF_Geometry','V24_11_Storage_Veranda_Column_1','V24_11_Storage_Veranda_Column_2','V24_11_Storage_Veranda_Column_Base_1','V24_11_Storage_Veranda_Column_Base_2','V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails'];rr=[]
for n in obstacles:
 o=bpy.data.objects[n];o.data.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in o.data.vertices]);f=np.array([tuple(t.vertices)for t in o.data.loop_triangles]);fn=f'QA_Obstacle_{len(rr):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);rr.append({'name':n,'file':fn})
(D/'QA_Obstacle_Index.json').write_text(json.dumps(rr,indent=2),encoding='utf8')
ck('Model SHA matches build',hashval==build['sha256']);ck('Input V24.10 retained unchanged',sha(B)==build['source_sha256']);ck('Original as-built 3dm retained unchanged',sha('E:/jz/实景三维场景模型.3dm')==json.loads((W/'v24_10/AsBuilt_Reference.json').read_text())['source_sha256']);ck('Photographic images remain packed',all(im.packed_file for im in bpy.data.images if im.source=='FILE'))
fail=[r for r in checks if not r['pass']];out={'status':'PASS_V24_11_FRESH_BLEND_QA'if not fail else'FAIL_V24_11_FRESH_BLEND_QA','model_sha256':hashval,'checks':checks,'failures':fail,'native_changed_mesh_stats':native_stats};(R/'V24_11_Fresh_Blend_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],len(checks),len(fail),flush=True)
for r in fail:print('FAIL',json.dumps(r,ensure_ascii=False),flush=True)
