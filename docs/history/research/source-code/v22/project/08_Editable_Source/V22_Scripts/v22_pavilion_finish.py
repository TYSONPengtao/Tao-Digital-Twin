from v22_common import *
D=W/'v22_pavilion';Q=json.loads((D/'Photo_Patch_Input.json').read_text(encoding='utf8'))
for n in ['SITE_GAZEBO_V11_KNEE_BRACES']:
 ps=[]
 for x in [.4457142857,3.8742857143]:
  for y in [-7.,-3.7]:
   for axis in [0,1]:
    sign=1 if (x<2 if axis==0 else y<-5) else -1
    poly=[[0,-.235],[.055,-.235],[.13,-.175],[.20,-.115],[.29,-.070],[.345,-.045],[.345,.012],[-.025,.012],[-.025,-.235]]
    vs=[]
    for side in [-.034,.034]:
     for u,z in poly:vs.append([x+sign*u,y+side,2.132714+z] if axis==0 else [x+side,y+sign*u,2.132714+z])
    ct=len(poly);f=[list(range(ct-1,-1,-1)),list(range(ct,ct*2))]+[[j,(j+1)%ct,(j+1)%ct+ct,j+ct] for j in range(ct)]
    ps.append(pp(manifold({'type':'polyhedron','vertices':vs,'faces':f}),'M_V22_Pavilion_Aged_Warm_Posts'))
 put(Q,n,ps,classification='SHORT_PROFILED_KNEE_BLOCKS_MATCHING_IDEAL_PAVILION_CORNERS')
Q['change_notes'].append('按最新“正确亭子”理想图把过长斜撑收短为曲线角托，入口不再被粗大的Y形撑占据；原收回位置和50mm木板净空保留。')
Q['cameras']=[['V22_Pavilion_Ideal_Compare',[7.3,-10.9,1.36],[2.35,-4.75,1.20],70],['V22_Pavilion_Wood_Drain_Detail',[5.38,-8.48,.65],[3.88,-6.93,1.01],64]]
save(Q,D,[{'check':'Pavilion shortened brackets are positive closed; original roof, deck, axis retreat retained','pass':True}])
