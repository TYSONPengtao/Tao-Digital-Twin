from pathlib import Path
W=Path(__file__).parent;D=W/'v26_10_railing';D.mkdir(exist_ok=True)
s=(W/'v26_9_railing/build_candidate.py').read_text('utf8').replace("D=W/'v26_9_railing'","D=W/'v26_10_railing'")
a=s.index('z=level[2];h=z+1.175');b=s.index('for y in np.r_[8.66',a)
s=s[:a]+'''z=level[2];h=float(curves[2,2][-1,2])
pts0=[[7.88,8.55,h],[7.88,9.49,h]];pieces.append(sweep(pts0));post(7.88,9.49,z,h,'F3 rear guard end');meta['grip_paths'].append({'tag':'F3 rear horizontal guard between level newels','path':pts0,'width_m':.082,'depth_m':.058,'constant_collar_z_m':h})
'''+s[b:]
s=s.replace("'tag':'F3 rear','axis_x_m':7.88,'slab_edge_x_m':7.8,'rail_top_above_floor_m':1.204", "'tag':'F3 rear','axis_x_m':7.88,'slab_edge_x_m':7.8,'rail_top_above_floor_m':h-z+.029,'level_two_newel_collars':True")
s=s.replace('y=7.215;front_h=h-.15','y=7.215;front_h=z+1.025')
s=s.replace("meta['all_sloping_grip_paths_and_rear_guard_retained']=True", "meta['all_sloping_grip_paths_retained']=True;meta['rear_guard_rebuilt_horizontal']=True")
s=s.replace('rear guard rise beyond ball','horizontal rear guard between level newels')
(D/'build_candidate.py').write_text(s,'utf8');exec(compile(s,str(D/'build_candidate.py'),'exec'),{'__file__':str(D/'build_candidate.py')})
exec(compile((W/'v26_10_preserve_railing.py').read_text('utf8'),str(W/'v26_10_preserve_railing.py'),'exec'),{'__file__':str(W/'v26_10_preserve_railing.py')})
