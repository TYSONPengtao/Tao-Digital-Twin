from v26_2_common import *
import v26_2_common as C
import hashlib
D=W/'v26_8';D.mkdir(exist_ok=True);C.D=D
FD=W/'v26_7/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))}
HN='V26_3_House_Connected_Walls_And_Stairs';old=np.load(FD/J[HN]['file']);house=tracked(old['v'],old['f'],J[HN]['materials'],old['mi'],old['uv'],HN)
native_cube=cube
def cube(lo,hi):return native_cube(np.asarray(lo,np.float32).astype(float),np.asarray(hi,np.float32).astype(float))
GRAY='M_V24_31_Stair_Gray_Marble';WHITE='M_Wall_Interior';CEIL='M_V26_3_Neutral_White_Interior_Ceiling'
proof={'stair_gap_fit_m':.10,'gap_is_reference_fit_not_survey':True,'latest_stair_reference':'D:/Desktop/屏幕截图 2026-10-24 130324.jpg','levels_m':[-.4499999881,3.450024414,7.050000191],'half_landing_levels_m':[1.499951124,5.249951363],'rebuilt_stairs':[]}
# Clear the room-side flight/landing volume, while retaining actual downstand
# beams at the room perimeter. Original finished wall planes stay outside.
room=cube([4.02,7.42,-.4499999881],[7.8,9.68,7.050000191])
cp=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components']
beamkeep=union([cube(*r['bounds_m']) for r in cp if r['name'].startswith(('BEAM_','V26_Stair_Frame_'))])
room=room-beamkeep
removed=(house^room).volume();house-=finish(room,WHITE,'Local stair room replacement cutter')
proof['room_replacement_removed_m3']=removed
for fl in[1,2]:
 for k,(ya,yb,sa,sb)in enumerate([(8.60,9.68,8.56,9.82),(7.42,8.50,7.28,8.54)],1):
  n=f'STAIR_F{fl}_FLIGHT{k}_Geometry';a=np.load(PD/PI[n]['file']);m=tracked(a['v'],a['f'],PI[n]['materials'],a['mi'],a['uv'],n+' original XZ nosings')
  # Clip the old auxiliary starter/bearing wing to its actual flight width,
  # then redistribute the width within the measured model wall planes.
  m=m^cube([-100,sa,-100],[100,sb,100]);sy=(yb-ya)/(sb-sa);m=m.transform([[1,0,0,0],[0,sy,0,ya-sy*sa],[0,0,1,0]])
  # Extend less than 1mm into the opaque wall for robust Boolean contact.
  # The extra is internal and introduces no added visible trim surface.
  if k==1:m=m.transform([[1,0,0,0],[0,(yb-ya+.0004)/(yb-ya),0,ya*(1-(yb-ya+.0004)/(yb-ya))],[0,0,1,0]])
  else:m=m.transform([[1,0,0,0],[0,(yb-ya+.0004)/(yb-ya),0,yb*(1-(yb-ya+.0004)/(yb-ya))],[0,0,1,0]])
  house+=m
  proof['rebuilt_stairs'].append({'name':n,'inner_y_m':ya if k==1 else yb,'wall_y_m':yb if k==1 else ya,'nominal_width_m':yb-ya,'source_XZ_unchanged':True})
 for n in[f'STAIR_LANDING_F{fl}_Geometry',f'V26_Stair_Landing_Bearing_Beam_F{fl}']:
  if n in PI:
   a=np.load(PD/PI[n]['file']);m=tracked(a['v'],a['f'],PI[n]['materials'],a['mi'],a['uv'],n)
  else:
   r=next(r for r in cp if r['name']==n);m=finish(cube(*r['bounds_m']),WHITE,n)
  # Retain the real landing/bearing depth, within the renewed platform.
  m=m^cube([4.0196,7.4196,-100],[5.200000286102295,9.6804,100]);house+=m
# Explicit through-void: no slab tongue, landing beam or old starter wing
# may bridge the fitted central well. Only the base floor remains below.
well=cube([5.200001,8.50,-.44998],[7.799999,8.60,7.05005]);house-=finish(well,GRAY,'Narrow photo referenced central stair well between independent flights')
sys.path.insert(0,str(W/'v26_8_windows'));from apply_house_recipe import apply_window_sills
house=apply_window_sills(house)
footp=W/'v26_8_windows/Foot_Closure_Recipe.json'
if footp.exists():
 fp=json.loads(footp.read_text('utf8'));fr=fp['row'];fa=np.load(footp.parent/'Foot_Closure'/fr['file']);fm=tracked(fa['v'],fa['f'],fr['materials'],fa['mi'],fa['uv'],fr['reason']);house+=fm;proof['bay_foot_closure']=fr
sys.path.insert(0,str(W/'v26_8_entry_jambs'));from apply_recipe import apply_front_entry_jamb_recipe
proof['entry_jamb_recipe']=[];house=apply_front_entry_jamb_recipe(house,proof['entry_jamb_recipe'])
# The actual fixed metal frames own their exposed faces. Some inherited
# plaster shared those same planes, including the bottom frame top. Give
# their existing seats a finite submillimetre reveal rather than leaving
# coplanar black/white competing triangles. Glazing and frames do not move.
wp=json.loads((W/'v26_8_windows/Prepared_Geometry.json').read_text('utf8'));seats=[]
for wr in wp['objects']:
 if not wr['name'].startswith('BAY_WINDOW_'):continue
 wa=np.load(W/'v26_8_windows/Prepared'/wr['file']);gt=wa['v'][wa['f'][np.isin(wa['mi'],[i for i,m in enumerate(wr['materials'])if 'Glass'in m])]];gn=np.cross(gt[:,1]-gt[:,0],gt[:,2]-gt[:,0]);normal=gn[np.argmax(np.linalg.norm(gn,axis=1)),:2];normal/=np.linalg.norm(normal);tangent=np.array([normal[1],-normal[0]])
 u=wa['v'][:,:2]@tangent;n=wa['v'][:,:2]@normal;lo=[u.min()-.0004,n.min()-.0004,wa['v'][:,2].min()-.0004];hi=[u.max()+.0004,n.max()+.0004,wa['v'][:,2].max()+.0004]
 expanded=cube(lo,hi).transform([[tangent[0],normal[0],0,0],[tangent[1],normal[1],0,0],[0,0,1,0]])
 house-=finish(expanded,WHITE,'Existing fixed bay frame seat with finite0.4mm reveal');seats.append(wr['name'])
proof['fixed_frame_coplanar_ownership']={'frames':seats,'seat_reveal_m':.0004,'actual_frame_and_glass_vertices_unchanged':True}
row,house=export(HN,house.simplify(.000001),'Photo referenced stair wall contact and visible central well; fitted door jambs and 30cm/F2 stone-rail-height room sills')
# Give the new solid a single, deliberate visible finish at each surface.
a=np.load(D/row['file']);vv=a['v'];ff=a['f'];mi=a['mi'].copy();uu=a['uv'];t=vv[ff];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-30);cc=t.mean(1);mats=row['materials']
for mat in[GRAY,WHITE,CEIL]:
 if mat not in mats:mats.append(mat)
stairmask=(cc[:,0]>4.02001)&(cc[:,0]<8.221)&(cc[:,1]>7.42001)&(cc[:,1]<9.67999)&(cc[:,2]>-.45002)&(cc[:,2]<7.05003)
mi[stairmask]=mats.index(GRAY);mi[stairmask&(nn[:,2]<-.6)]=mats.index(CEIL)
mi[(nn[:,2]<-.7)&(cc[:,2]>-.4)&(mi==mats.index(WHITE))]=mats.index(CEIL)
from v26_8_native_cleanup import repair_native
vv,ff,mi,uu,nativeproof=repair_native(vv,ff,mi,uu);proof['native_float32_cleanup']=nativeproof
np.savez_compressed(D/row['file'],v=vv,f=ff,mi=mi,uv=uu);row['triangles']=len(ff)
wp=json.loads((W/'v26_8_windows/Prepared_Geometry.json').read_text('utf8'));rows=[row]
import shutil
for rr in wp['objects']:
 src=W/'v26_8_windows/Prepared'/rr['file'];target=D/Path(rr['file']).name;shutil.copy2(src,target);rr=dict(rr);rr['file']=target.name;rows.append(rr)
proof['window_recipe']=wp.get('proof',{});proof['window_selection']='5 front room bay groups; user confirmed no iron guards on any of the three floors; actual balcony stone rail unchanged'
remove=sorted(set(wp.get('remove',[])+[r['name'] for r in wp.get('optional_f1_guard_rows',[])]))
rp=json.loads((W/'v26_8_railing/Prepared_Railing.json').read_text('utf8'))
for rr in rp['objects']:
 shutil.copy2(W/'v26_8_railing'/rr['file'],D/rr['file']);rows.append(rr)
proof['railing']=rp['proof']
prep={'source':'E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend','source_sha256':'ae36eb7abde8241465d4d6707fa19c8a9ccd74aaebc025565f2843ee9be5711e','objects':rows,'remove':remove,'proof':proof}
(D/'Prepared_Geometry.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2),'utf8');print('PREPARED',len(rows),len(prep['remove']),house.num_tri(),house.volume(),len(house.decompose()),flush=True)
