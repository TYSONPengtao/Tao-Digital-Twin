from pathlib import Path
W=Path(__file__).parent;D=W/'v26_8_railing';D.mkdir(exist_ok=True)
s=(W/'v26_7_railing_audit/build_candidate.py').read_text('utf8')
s=s.replace("D=W/'v26_7_railing_audit'","D=W/'v26_8_railing'")
start=s.index(" old=min(eligible,key=");end=s.index('\ndef hz(',start)
s=s[:start]+" spindle_raw(float(x),float(y),float(z),float(top),tag,T)\n"+s[end:]
s=s.replace("r=.112;zarc", "r=.102;zarc")
s=s.replace("[(1,8.602),(2,8.498)]", "[(1,8.652),(2,8.448)]")
s=s.replace('np.linspace(xx+.025,7.65,81)','np.linspace(xx+.025,7.71,81)')
s=s.replace("[7.84,8.55,line(7.8)]", "[7.88,8.55,line(7.8)]")
s=s.replace('7.84+.112*math.cos(a)', '7.88+.112*math.cos(a)')
s=s.replace('7.84,8.55', '7.88,8.55')
a=s.index(' if fl==2:\n  # Short upper neck');b=s.index('# Final floor guard',a);s=s[:a]+s[b:]
s=s.replace("meta['original_spindle_seats_retained']=110", "meta['original_spindle_X_and_Z_retained']=True;meta['inner_railing_Y_refitted_for_central_well']=True;meta['central_well_clear_width_m']=.10;meta['flight_inner_axes_y_m']=[8.448,8.652];meta['latest_reference']='D:/Desktop/屏幕截图 2026-10-24 130324.jpg';meta['enlarged_return_and_double_neck_ring_removed']=True")
s=s.replace("'E:/jz/JIA/Rebuild_V26_6/Blender/Architecture_Complete_V26_6.blend'", "'E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend'").replace('ea7cd20cb3c30cf2b5984c1e262ca182fa3c168a8a16fd7201ef428267bf05b7','ae36eb7abde8241465d4d6707fa19c8a9ccd74aaebc025565f2843ee9be5711e')
s=s.replace('inherited treads, posts, wood material and guard ends retained', 'original XZ tread datums retained; inner rail axes and half-turn newel bases refitted around visible central well; wood material retained')
s=s.replace('preserves inherited step elevations, guard endpoints and wood material', 'preserves original step elevations and wood material; half-turn radius and inner rail positions refitted around the visible central well')
(D/'build_candidate.py').write_text(s,'utf8');print('RAIL_SCRIPT_READY')
