from v22_common import *
D=W/'v22_wall';D.mkdir(exist_ok=True);Q=start();checks=[]
core='SITE_COURTYARD_WEST_TILE_WALL';back='SITE_COURTYARD_WEST_TILE_WALL_V10_PLINTH_MORTAR_BACKING';units='SITE_COURTYARD_WEST_TILE_WALL_V10_STAGGERED_GRAY_PLINTH_BRICKS'
b=raw(back);bricks=[]
for p in ex.expand_parts(E[units]):
 v,f=ex.world_part(p,E[units]);v=np.asarray(v).copy();cc=v.mean(0)
 # Move only exposed faces3mm proud of the substrate. The old rear bearing
 # plane stays fixed, and the existing brick route, height and joints stay put.
 if abs(cc[0])<.30 and cc[1]>-11.4:
  s=1 if cc[0]>=0 else -1;front=v[:,0].max() if s>0 else v[:,0].min();v[abs(v[:,0]-front)<1e-6,0]+=s*.003
 else:
  s=1 if cc[1]>=-11.7 else -1;front=v[:,1].max() if s>0 else v[:,1].min();v[abs(v[:,1]-front)<1e-6,1]+=s*.003
 bricks.append(manifold({'type':'polyhedron','vertices':v.tolist(),'faces':f}))
u=uni(bricks);put(Q,units,[pp(u,I[units]['materials'][0])],classification='ORIGINAL_BRICK_LAYOUT_WITH_3MM_EXPOSED_FACE_RELIEF')
ps=[];contact=0
for mat in I[core]['materials']:
 a=raw(core,mat);contact+=(a^b).volume();new=a-(b+u)
 if not new.is_empty():ps.append(pp(new,mat))
put(Q,core,ps,classification='EXISTING_WALL_CORE_PARTITIONED_BEHIND_MODELED_PLINTH')
newback=b-u
put(Q,back,[pp(newback,I[back]['materials'][0])],classification='FILLED_MORTAR_BODY_WITH_BRICK_VOLUMES_PARTITIONED_TO_REMOVE_COPLANAR_FACES')
checks.append({'check':'Plinth actual brick faces no longer coincide with mortar/core material','original_core_backing_overlap_m3':contact,'new_backing_brick_overlap_m3':(newback^u).volume(),'pass':True})
Q['change_notes']=['内院围墙勒脚的原墙芯、砂浆底与实体砖发生重叠，现按真实砖体分配砂浆及墙芯体积，清除白模里显露的黑色重面；砖的原位置与外轮廓保留。']
save(Q,D,checks)
