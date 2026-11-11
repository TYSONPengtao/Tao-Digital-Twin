"""Front room bay sills: preserve frames, glazing, real balcony and all apertures.

Produces tracked local replacements and a cut/add recipe for the fused house.
Never opens or saves a native Blender document.
"""
from pathlib import Path
import sys,json,hashlib,re
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W))
from v26_2_common import *
import v26_2_common as C
BASE=W/'v26_8_windows';D=BASE/'Prepared';D.mkdir(exist_ok=True);C.D=D
FD=W/'v26_7/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
HN='V26_3_House_Connected_Walls_And_Stairs';a=np.load(FD/J[HN]['file'])
house=tracked(a['v'],a['f'],J[HN]['materials'],a['mi'],a['uv'],HN)
out={'source_model':'E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend','source_sha256':'ae36eb7abde8241465d4d6707fa19c8a9ccd74aaebc025565f2843ee9be5711e','objects':[],'remove':[],'house_recipe':[],'glazing_clearance_recipe':[],'proof':{},'optional_f1_guard_rows':[]}
# Actual horizontal floor/stone-rail surfaces, from the current saved mesh.
floors={1:-.44999998807907104,2:3.450000047683716,3:7.050000190734863}
rail_top=4.600049018859863
height=rail_top-floors[2]
targets={1:floors[1]+.3,2:rail_top,3:floors[3]+height}
base_sills={fl:float(J[f'BAY_WINDOW_F{fl}_{"L" if fl<3 else "R"}_1_Geometry']['bounds'][0][2])for fl in floors}
anchors={1:2.2839,2:5.9679,3:9.3519}

def warp_z(v,fl):
 v=v.copy();z=v[:,2];old=base_sills[fl];delta=targets[fl]-old;floor=floors[fl]
 # Preserve finished floor, original lower 60 mm stone/frame edge profiles,
 # and the upper transom geometry. Only the clear lower-height interval varies.
 weight=np.interp(z,[floor,old-.061,old+.080,anchors[fl]],[0.,1.,1.,0.],left=0.,right=0.)
 weight[abs(z-floor)<.001]=0.
 v[:,2]+=weight*delta
 return v

def stage_vertices(n,fl,optional=False,translate_only=False):
 r=J[n];a=np.load(FD/r['file']);v=a['v'].copy()
 if translate_only:v[:,2]+=targets[fl]-base_sills[fl]
 else:v=warp_z(v,fl)
 fn=n+'.npz';np.savez_compressed(D/fn,v=v,f=a['f'],mi=a['mi'],uv=a['uv'])
 row={'name':n,'file':fn,'materials':r['materials'],'triangles':len(a['f']),'reason':'User-confirmed sill height; preserve glazing, frame widths, original XY and upper transoms','floor':fl,'bounds':[v.min(0).tolist(),v.max(0).tolist()]}
 out['optional_f1_guard_rows'if optional else'objects'].append(row)
 return row

for fl,floor in floors.items():
 for side in (['L','R']if fl<3 else['R']):
  x0=0. if side=='L'else 9.1
  # Entire front bay low section, with invariant boundary planes at floor
  # and transom, is cut and replaced once. Nothing reaches rear room partitions.
  lo=np.array([x0-.24,.78,floor-.205],np.float32).astype(float)
  hi=np.array([x0+4.14,2.215,anchors[fl]],np.float32).astype(float)
  cutter=finish(cube(lo,hi),'M_Wall_Interior',f'Bay F{fl} {side} cut box')
  part=(house^cutter).simplify(1e-6)
  cutrow,_=export(f'Cut_F{fl}_{side}_Room_Bay_Sill',cutter,'Local bay replacement cutter; boundary floor/slab/room planes invariant')
  row,_=export(f'Part_F{fl}_{side}_Room_Bay_Sill_Source',part,'Source local bay wall profile with provenance')
  aa=np.load(D/row['file']);vv=warp_z(aa['v'],fl)
  # Preserve exact source-owned materials and UV per face after vertical fit.
  warped=tracked(vv,aa['f'],row['materials'],aa['mi'],aa['uv'],f'Photo fitted F{fl} {side} sill')
  addrow,_=export(f'Add_F{fl}_{side}_Room_Bay_Sill',warped.simplify(1e-6),'Same bay footprint and thickness; user height applied with real glass opening retained')
  out['house_recipe'].append({'floor':fl,'side':side,'cut':cutrow,'add':addrow,'source_part':row,'cut_bounds_m':[lo.tolist(),hi.tolist()],'old_sill_world_z_m':base_sills[fl],'target_sill_world_z_m':targets[fl],'target_height_above_native_room_floor_m':targets[fl]-floor})
  for k in range(3):
   window_row=stage_vertices(f'BAY_WINDOW_F{fl}_{side}_{k}_Geometry',fl)
   if k in [0,2]:
    # V26.7 already blocked about 12% of each oblique glass pane with the
    # old corner plaster. Preserve the actual frame outlines and punch only
    # a prism of the actual clear glass outline through the wall thickness.
    b=np.load(D/window_row['file']);gf=b['f'][np.isin(b['mi'],[i for i,n in enumerate(window_row['materials'])if 'Glass'in n])]
    gg=solid(b['v'],gf);me=gg.to_mesh64();gv=np.array(me.vert_properties[:,:3]);ff=np.array(me.tri_verts)
    tri=gv[ff];norms=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);size=np.linalg.norm(norms,axis=1);norm=norms[np.argmax(size)]/size.max();normal=norm[:2]/np.linalg.norm(norm[:2])
    t=gv[:,:2]@normal;mid=(t.min()+t.max())/2
    depth=max(.6,float(t.max()-t.min()))
    gv[:,:2]+=((t-mid)*(depth/(t.max()-t.min())-1))[:,None]*normal
    gc=finish(solid(gv,ff),'M_Wall_Interior',f'Existing F{fl} {side} oblique pane clear opening')
    gr,_=export(f'Clear_F{fl}_{side}_{k}_Oblique_Glass',gc,'Actual existing glass outline extruded only along wall normal; do not alter frame width or pier between adjacent panes')
    out['glazing_clearance_recipe'].append({'window':window_row['name'],'cut':gr,'normal_xy':normal.tolist(),'normal_depth_m':depth,'reason':'Source-model obsolete white plaster blocks original glass panes; opening clearance is not a new frame/door aperture'})
  for handed in ['Left','Right']:
   for typ in ['Frame','Glass']:stage_vertices(f'V24_18_BAY_WINDOW_F{fl}_{side}_1_{handed}_Outward_Hinge_{typ}',fl)
  for k in range(3):
   n=f'CONSTRUCTION_LOW_SILL_GUARD_BAY_WINDOW_F{fl}_{side}_{k}_Geometry'
   out['remove'].append(n)
   if fl==1:stage_vertices(n,fl,optional=True,translate_only=True)

out['proof']={'scope':'Five front room bay windows only. Bathroom high windows, rear/stair glazing, true stone balcony and terrace railings unchanged.','upper_sill_reference':{'source_object':'BALCONY_F2_PHOTO_OPEN_STONE_RAIL_Geometry','native_continuous_grip_top_z_m':rail_top,'native_f2_room_floor_z_m':floors[2],'derived_height_m':height,'ornamental_post_top_z_m':4.720044136047363,'measurement_status':'Inherited native rail/floor datums matched by user instruction; not new physical survey'},'f1_sill':{'height_m':.3,'status':'Explicit user measurement 2026-10-24'},'guards':{'root_cause':'build_scene_v4.py lines 64-77 explicitly inserted proposal guards, not photographed existing elements.','upper_removed_count':9,'f1_removed_count':6,'total_removed_count':len(out['remove']),'f1_optional_count':len(out['optional_f1_guard_rows']),'f1_final_action':'User explicitly confirmed first floor also has no iron guards. Remove all 15. Optional first-floor moved arrays are archived exploration only and must not be installed.'},'upper_glazing':'Fifteen fixed/oblique panes and twenty operable frame/glass objects resized coherently; same face arrays/materials/UV, all XY unchanged, upper transoms unchanged.'}
(BASE/'Prepared_Geometry.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('WINDOWS_PREPARED',len(out['objects']),len(out['remove']),len(out['house_recipe']),flush=True)
