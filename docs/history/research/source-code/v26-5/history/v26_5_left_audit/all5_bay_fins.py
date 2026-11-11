exec((__import__('pathlib').Path(__file__).parent/'probe.py').read_text('utf8').split('for n in [')[0])
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
hn='V26_3_House_Connected_Walls_And_Stairs';a=np.load(D/I[hn]['file']);H=solid(a['v'],a['f'],hn)
P=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components'];CI={r['name']:r for r in json.loads((W/'v26_1/Geometry_Index.json').read_text('utf8'))};cores=[]
for r in P:
 if not r['name'].startswith(('KZ_','BEAM_','ROOF_')):continue
 a=np.load(W/'v26_1'/CI[r['name']]['file']);cores.append(solid(a['v'],a['f'],r['name']))
C=union(cores);cuts=[];rows=[]
for fl,s,xbase in [(1,'L',0.),(2,'L',0.),(1,'R',9.1),(2,'R',9.1),(3,'R',9.1)]:
 ns=[f'BAY_WINDOW_F{fl}_{s}_{i}_Geometry'for i in range(3)];mats=[];metals=[];glasses=[]
 for nm in ns:
  ar=np.load(D/I[nm]['file']);metals.append(solid(ar['v'],ar['f'][ar['mi']==0],nm+' black'));glasses.append(solid(ar['v'],ar['f'][ar['mi']==1],nm+' glass'))
 metal=union(metals);glass=union(glasses);lo=np.array(I[ns[1]]['bounds'][0]);hi=np.array(I[ns[1]]['bounds'][1]);z0=lo[2];z1=hi[2]
 boxes=[cube([xbase+.55,.98,z0],[xbase+.95,1.25,z1]),cube([xbase+2.95,.98,z0],[xbase+3.35,1.25,z1])];cut=union(boxes)-C;cuts.append(cut);r={'bay':f'F{fl}_{s}','front_frame_z_range':[z0,z1],'cut_boxes':[[[xbase+.55,.98,z0],[xbase+.95,1.25,z1]],[[xbase+2.95,.98,z0],[xbase+3.35,1.25,z1]]],'old_fin_volume_m3':(H^cut).volume(),'remaining_opaque_volume_in_mask_after_m3':((H-cut)^cut).volume(),'core_removed_m3':(C^cut).volume(),'metal_side_front_contact_m3':[(metals[0]^metals[1]).volume(),(metals[2]^metals[1]).volume()],'metal_frame_components_after_union':len(metal.decompose()),'metal_intersection_house_before_m3':(metal^H).volume(),'glass_intersection_house_before_m3':(glass^H).volume(),'glass_intersection_house_after_m3':(glass^(H-cut)).volume(),'house_removed_at_front_fin_vs_glass_m3':((H^cut)^glass).volume()};rows.append(r);print(r,flush=True)
new=H-union(cuts);print('RESULT',new.status(),len(new.decompose()),H.volume()-new.volume())
(Path(__file__).parent/'all5_bay_corner_fin_report.json').write_text(json.dumps({'rows':rows,'new_house_components':len(new.decompose()),'new_house_status':str(new.status()),'removed_total_m3':H.volume()-new.volume()},indent=2),'utf8')
