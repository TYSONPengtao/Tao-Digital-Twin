from pathlib import Path
W=Path(__file__).parent;s=(W/'v24_34_plan_walkable_routes.py').read_text('utf8').replace('v24_34','v24_36').replace('V24_34','V24_36');start=s.index('for name,waypoints in ');end=s.index(':\n path=[]',start)
routes=[('PTJIA6_North_Road',[(-25,12),(-45,15),(-58,18),(-67,24),(-77,40),(-83,65),(-84,80),(-80,100),(-84,120),(-88,135),(-100,144),(-110,146)]),('PTJIA6_Central_Field',[(-390,5),(-405,12),(-420,0)]),('PTJIA6_Far_West_Field',[(-615,-150),(-600,-145),(-590,-160)])]
s=s[:start]+'for name,waypoints in '+repr(routes)+s[end:];s=s.replace('  closed.add(u);x,y=map(int,p[u,:2])','  closed.add(u)\n  if len(closed)>7000:return None\n  x,y=map(int,p[u,:2])');(W/'v24_36_plan_walkable_routes.py').write_text(s,encoding='utf8');compile(s,'planner','exec')
