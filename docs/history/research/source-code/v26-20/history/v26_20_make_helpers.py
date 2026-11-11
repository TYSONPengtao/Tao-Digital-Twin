from pathlib import Path
W=Path(__file__).parent
for name in['build','build_fast','fast_display','verify_fast','physics_qa','native_qa','render','native_viewport_review','run_checks']:
 s=(W/('v26_19_'+name+'.py')).read_text('utf8').replace('v26_19','v26_20').replace('V26_19','V26_20').replace('V26.19','V26.20')
 if name=='build':
  s=s.replace('v26_18','v26_19').replace('V26_18','V26_19').replace('V26.18','V26.19')
  s='\n'.join("note=bpy.data.texts.new('V26_20_储藏房地面150mm台阶');note.write('储藏房地面及外廊局部抬高150mm，在西侧入口形成一阶。墙体与厨房、原地基下部保持；新顶面沿用世界XY贴图，外侧立面续接原地基UV。仅修短储藏房两扇门的下沿，保持门顶、合页及动画不变。继承前版梁端窗角、楼梯和内大门修正及花盆移除，保持阴天柔光。')"if l.startswith('note=bpy.data.texts.new(')else l for l in s.splitlines())+'\n'
  s=s.replace('V26_20_Clean_Beam_Heads_And_Courtyard_Fixtures','V26_20_Storage_Floor_150mm_Single_Entry_Step')
 if name=='native_qa':
  p0=s.index("previous=D/'Before_Planter_Removal_Index.json'");p1=s.index("ci=json.loads",p0);s=s[:p0]+s[p1:]
  where="cn='GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS_Geometry'"
  add="""protected=json.loads((D/'Protected_Object_State.json').read_text('utf8'));invalid=[]
for name,state in protected.items():
 ob=bpy.data.objects[name];now={'hide_viewport':ob.hide_viewport,'hide_render':ob.hide_render,'hide_set':ob.hide_get(),'modifiers':[(m.name,m.type,m.show_viewport,m.show_render)for m in ob.modifiers],'collections':sorted(c.name for c in ob.users_collection)}
 if json.loads(json.dumps(now))!=state:invalid.append(name)
ck('Kitchen and wall visibility, modifiers and collection membership stay exact',not invalid,invalid=invalid)
"""
  s=s.replace(where,add+where).replace('Source V26.18 file is unchanged','Source V26.19 file is unchanged')
 if name=='physics_qa':
  s=s.replace("w=Walker(world,(*a,-.4));rec=w.recoveries;ok,tr=go(w,b,limit=6.);traces['V26_20_'", "zz=-.25 if label=='storage_door'else-.4;w=Walker(world,(*a,zz));rec=w.recoveries;ok,tr=go(w,b,limit=6.);traces['V26_20_'")
  s=s.replace("all(abs(p[2]+.4)<.008 for p in tr)","all(abs(p[2]-zz)<.008 for p in tr)")
  marker="with P.open('rb')as f:h="
  new="""# The marked west portal has one real150mm riser, used by the live walker.
w=Walker(world,(12.85,-15.7,-.4));rec=w.recoveries;z0=w.p.z;ok,tr=go(w,(14.3,-15.7),limit=6.);traces['storage_new_entry_up']=tr
ck('Storage west entrance climbs the single150mm step without jumping or recovery',ok and w.grounded and w.recoveries==rec and abs(w.p.z+.25)<.008 and abs(w.p.z-z0-.15)<.01,position=list(w.p),rise_m=w.p.z-z0,recoveries=w.recoveries)
ok,tr=go(w,(12.85,-15.7),limit=6.);traces['storage_new_entry_down']=tr
ck('Storage west entrance descends to the unchanged outer court',ok and w.grounded and w.recoveries==rec and abs(w.p.z+.4)<.008,position=list(w.p),recoveries=w.recoveries)
w=Walker(world,(14.3,-15.7,-.25));rec=w.recoveries;ok,tr=go(w,(17.9,-15.7),limit=7.);traces['storage_gallery_raised_walk']=tr
ck('Raised storage gallery stays level with continuous support',ok and w.grounded and w.recoveries==rec and all(abs(p[2]+.25)<.008 for p in tr),position=list(w.p),recoveries=w.recoveries)
"""
  s=s.replace(marker,new+marker)
 if name=='native_viewport_review':
  s=s.replace('manual=[VIEWS[i]for i in[1,4,0]]','manual=[VIEWS[i]for i in[1,2,3]]')
  s=s.replace('running.walker.place((8.5,7.8,7.05));running.yaw=math.atan2(-2.48,-1.3);running.pitch=-.7','running.walker.place((12.85,-15.7,-.4));running.yaw=math.atan2(1.,0.);running.pitch=.35')
  s=s.replace('Viewport_01_F3_Hall_Tour','Viewport_01_Storage_Entry_Tour').replace('Delivered first-person tour looking up at the repaired third-floor hall beam heads','Delivered first-person tour at the real storage150mm entrance step').replace('Delivered Fast first-person tour runs on the third-floor landing','Delivered Fast first-person tour runs at the unchanged outside storage entry')
  s=s.replace("abs(records[0]['person_m'][0]-8.5)<.01 and abs(records[0]['person_m'][1]-7.8)<.01 and abs(records[0]['person_m'][2]-7.05)<.04", "abs(records[0]['person_m'][0]-12.85)<.01 and abs(records[0]['person_m'][1]+15.7)<.01 and abs(records[0]['person_m'][2]+.4)<.02")
 (W/('v26_20_'+name+'.py')).write_text(s,'utf8')
perf=W/'v26_20_perf';perf.mkdir(exist_ok=True);(perf/'roam_controller_fast.py').write_text((W/'v26_19_perf/roam_controller_fast.py').read_text('utf8').replace('V26.19','V26.20'),'utf8')
print('V26_20_HELPERS_READY')
