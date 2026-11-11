from pathlib import Path
W=Path(__file__).parent
def copy(n):return (W/('v24_23_'+n+'.py')).read_text('utf8').replace('v24_23','v24_24').replace('V24_23','V24_24')
s=copy('build').replace('V24_24_端柱门柱与储藏房接缝','V24_24_端部封墙门前退墙及院落补铺')
needle=" o['V24_24_Reference']='123051 / 123121 / 123155 / 00004 gate ideal model'"
insert=''' if row.get('gate_front_finish'):
  brick=me.materials.find('M_V24_18_Continuous_Blue_Brick')
  for face in me.polygons:
   c=o.matrix_world@face.center;no=o.matrix_world.to_3x3()@face.normal
   if 8.339<c.x<13.206 and abs(c.y+11.73)<.00005 and no.y<-.5:face.material_index=brick
 if row.get('paving_finish'):
  for mn in ['M_V22_Courtyard_Filled_Joint']+['M_V22_Courtyard_Stone_'+str(i)for i in range(4)]:
   if me.materials.find(mn)<0:me.materials.append(bpy.data.materials[mn])
  for face in me.polygons:
   c=o.matrix_world@face.center;iy=int(np.floor((c.y+10.9)/.62));offset=.4-(.56 if iy%2 else 0);ix=int(np.floor((c.x-offset)/1.12));xx=c.x-offset-ix*1.12;yy=c.y+10.9-iy*.62
   mn='M_V22_Courtyard_Stone_'+str((ix+iy*3)%4)if .003-1e-6<xx<1.117+1e-6 and .003-1e-6<yy<.617+1e-6 else'M_V22_Courtyard_Filled_Joint';face.material_index=me.materials.find(mn)
 o['V24_24_Reference']='150017 / 150243 / 150306 / 150819' '''.rstrip()
assert needle in s;s=s.replace(needle,insert)
a=s.index('views=[');b=s.index('\nfor tag,loc,aim,lens in views:',a)
views=[('Kitchen_Closure',(8.85,-7.0,1.13),(8.91,-3.0,1.3),28),('Gate_Front',(6.6,-15.8,1.13),(6.6,-11.6,1.3),25),('Gate_Junction_High',(10.,-15.0,4.9),(8.6,-11.65,2.8),35),('Gate_Back',(8.9,-8.6,1.13),(8.25,-11.65,1.45),25),('Paving_Overview',(6.4,-7.4,9.2),(6.4,-.2,-.35),25),('Paving_Close',(5.6,-2.2,1.9),(6.6,-.55,-.25),24)]
s=s[:a]+'views='+repr(views)+s[b:]
a=s.index("for fn in ['D:/Desktop/");b=s.index('\n im=bpy.data.images.load',a)
s=s[:a]+"for fn in ['D:/Desktop/屏幕截图 2026-10-19 '+t+'.jpg'for t in ['150017','150243','150306','150819']]:"+s[b:]
s=s.replace("sc.camera=bpy.data.objects['V24_24_Kitchen_North']","sc.camera=bpy.data.objects['V24_24_Kitchen_Closure']").replace('V24_24_END_POST_GATE_PIER_REVEAL_AND_STORAGE_JUNCTION','V24_24_VERANDA_CLOSURE_FRONT_GATE_SETBACK_AND_MATCHING_PAVING')
a=s.index("note=bpy.data.texts.new");b=s.index('\ndef write',a)
s=s[:a]+"note=bpy.data.texts.new('V24_24_本次修正说明');note.write('按150017将厨房北端木柱与木立面间的红框封白墙，墙顶随现有斜梁，保留木柱外露。按150243和150306，只把内大门正面砖墙退到现有白墙Y=-11.73面，门后、雕花柱和门楼屋顶保持。按150819将主楼前黄线范围补同款1.12×0.62米错缝石板，沿原坡面贴合，表面加高2毫米；原台阶、地坪基体和排水坡向保留。保留储藏房上版修正及1.65米人物漫游。')"+s[b:]
(W/'v24_24_build.py').write_text(s,encoding='utf8')
s=copy('render').replace("['Kitchen_North','Gate_Front','Gate_Pier','Storage_Joint','Storage_Wide','Storage_Foot']",repr([v[0]for v in views]));(W/'v24_24_render.py').write_text(s,encoding='utf8')
s=copy('launcher_smoke');(W/'v24_24_launcher_smoke.py').write_text(s,encoding='utf8')
s=copy('physics_qa')
s=s.replace("ck('New end post leaves the north veranda exit walkable',ok,position=list(w.p))","ck('New north white wall blocks the marked opening',not ok and w.p.y<-3.20,position=list(w.p))")
(W/'v24_24_physics_qa.py').write_text(s,encoding='utf8')
print('V24_24_BUILD_AND_QA_SCRIPTS_READY')
