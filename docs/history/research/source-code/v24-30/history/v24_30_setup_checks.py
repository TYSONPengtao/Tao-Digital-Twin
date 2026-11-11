from pathlib import Path
W=Path(__file__).parent
for kind in ['physics_qa','measure_math_qa','launcher_smoke']:
 s=(W/f'v24_29_{kind}.py').read_text('utf8').replace('V24_29','V24_30').replace('v24_29','v24_30')
 if kind=='physics_qa':
  s=s.replace('abs(w.p.z+.452)<.005','abs(w.p.z+.60)<.005')
  s=s.replace("'Walk graded court to the lower entry landing',ok and w.grounded and abs(w.p.z+.45)<.012","'Walk low paved court to the one-step entrance',ok and w.grounded and abs(w.p.z+.60)<.012")
  s=s.replace("'Enter the lowered house from the flush court'","'Enter the lowered house over the single 15cm step'")
  s=s.replace("'Return from the lowered house to the flush court'","'Return down the single entrance step to the low court'")
  s=s.replace("'Cross the old dividing step line without a height change',ok and abs(w.p.z-z0)<.012","'Step from low main court onto high north lane',ok and abs(w.p.z-z0-.15)<.012")
  s=s.replace("'Cross back over the flush seam without falling through'","'Step down from high north lane to low main court'")
  at='with P.open('
  extra='''# Walk from the outer gate along the actual graded approach, then enter\n# the flat white yard at its nearly flush inner landing.\nw=Walker(world,(-13.5,-10.9,-.80));success=True;tr=[]\nfor xy in [(-12.,-10.9),(-9.,-11.0),(-6.,-11.9),(-3.,-12.),(-.7,-12.),(-.7,-10.5),(-2.,-8.8)]:\n ok,t=go(w,xy,limit=8.);tr+=t\n if not ok:success=False;break\ntraces['outer_gate_road_to_white_yard']=tr\nck('Walk graded gate approach and enter the white building pad',success and w.grounded and abs(w.p.z+.60)<.008,position=list(w.p))\nw=Walker(world,(-12.,0.,-.5));ok,tr=go(w,(-3.,0.),limit=10.);traces['flat_white_pad']=tr\nck('Flat white outer pad has continuous foot support',ok and w.grounded and all(abs(p[2]+.60)<.003 for p in tr),position=list(w.p))\nw=Walker(world,(-.65,10.8,-.5));ok,tr=go(w,(.65,10.8),limit=4.);traces['rear_partition']=tr\nck('Rear partition physically separates outer yard and high internal strip',not ok and w.p.x<-.30,position=list(w.p))\nw=Walker(world,(13.7,2.0,-.3));ok,tr=go(w,(14.1,6.0),limit=9.);traces['high_rear_lane']=tr\nck('High lane remains walkable beside corrected perimeter wall',ok and w.grounded and abs(w.p.z+.45)<.008,position=list(w.p))\n'''
  s=s.replace(at,extra+at)
 (W/f'v24_30_{kind}.py').write_text(s,encoding='utf8')

