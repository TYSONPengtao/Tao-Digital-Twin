from pathlib import Path
W=Path(__file__).parent
s=(W/'v26_18_native_viewport_review.py').read_text('utf8').replace('v26_18','v26_19').replace('V26_18','V26_19').replace('V26.18','V26.19')
s=s.replace('manual=[VIEWS[i]for i in[2,5,0]]','manual=[VIEWS[i]for i in[1,4,0]]')
s=s.replace('running.walker.place((7.15,9.10,.10));running.yaw=math.atan2(1.,-.45);running.pitch=-1.0','running.walker.place((8.5,7.8,7.05));running.yaw=math.atan2(-2.48,-1.3);running.pitch=-.7')
s=s.replace('Viewport_01_Stair_Underside_Tour','Viewport_01_F3_Hall_Tour')
s=s.replace('Delivered first-person tour looking up at the repaired first stair/slab soffit','Delivered first-person tour looking up at the repaired third-floor hall beam heads')
s=s.replace('Delivered Fast first-person tour runs on the actual first stair','Delivered Fast first-person tour runs on the third-floor landing')
s=s.replace("abs(records[0]['person_m'][0]-7.15)<.01 and abs(records[0]['person_m'][1]-9.10)<.01", "abs(records[0]['person_m'][0]-8.5)<.01 and abs(records[0]['person_m'][1]-7.8)<.01 and abs(records[0]['person_m'][2]-7.05)<.04")
(W/'v26_19_native_viewport_review.py').write_text(s,'utf8')
print('V26_19_RUNTIME_REVIEW_READY')
