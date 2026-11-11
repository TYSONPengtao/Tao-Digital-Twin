from pathlib import Path
W=Path(__file__).parent;s=(W/'v24_34_exterior_physics_qa.py').read_text('utf8').replace("D=W/'v24_34'","D=W/'v24_37'").replace('Rebuild_V24_34','Rebuild_V24_37').replace('Architecture_Complete_V24_34','Architecture_Complete_V24_37').replace("R/'V24_34_Exterior_Physics_QA.json'","R/'V24_37_Exterior_Physics_QA.json'")
s=s.replace("for r in json.loads((D/'Planned_Routes.json').read_text()):","routes=json.loads((W/'v24_34/Planned_Routes.json').read_text())+json.loads((W/'v24_36/Planned_Routes.json').read_text())\nfor r in routes:")
s=s.replace("if okay and 'Seam'in r['name']:","if okay and ('Seam'in r['name']or r['name'].startswith('PTJIA6')):")
s=s.replace("ck('Same old MB7 road seam is walkable in reverse',","ck('Reverse human walk on '+r['name'],")
s=s.replace("south=json.loads((D/'Planned_Routes.json').read_text())[-1]['points'][-1]","south=json.loads((W/'v24_34/Planned_Routes.json').read_text())[-1]['points'][-1]")
needle="fail=[r for r in checks if not r['pass']];out="
extra="""for label,loc in [('PTJIA6_ROAD',(-80,100,.576007)),('PTJIA6_FIELD',(-390,5,-13.318422)),('PTJIA6_FAR_WEST',routes[-1]['points'][0])]:
 w=m.Walker(world,loc);z0=w.p.z;peak=z0
 for i in range(120):w.update((0,0),1/60,jump=i==0);peak=max(peak,w.p.z)
 ck('Distant support jump and landing '+label,w.grounded and w.recoveries==0 and peak-z0>.50 and abs(w.p.z-z0)<.025,position=list(w.p),jump_height_m=peak-z0,origin_distance_m=w.p.length)
import ast
code=bpy.data.texts['V24_21_漫游控制器.py'].as_string();tree=ast.parse(code);walker_calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='Walker'];ck('First and third person use the same supported walker',len(walker_calls)==1 and 'first_person'in code and 'PTJIA6_ROAD'in code,constructor_calls=len(walker_calls),verification='AST of embedded runtime')
"""
assert needle in s;s=s.replace(needle,extra+needle);compile(s,'v24_37_exterior_physics_qa.py','exec');(W/'v24_37_exterior_physics_qa.py').write_text(s,encoding='utf8')
