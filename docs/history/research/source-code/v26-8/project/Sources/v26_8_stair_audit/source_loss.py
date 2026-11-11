exec((__import__('pathlib').Path(__file__).parent/'diagnose.py').read_text('utf8').split('out=')[0])
out=[]
for fl in[1,2]:
 for k in[1,2]:
  n=f'STAIR_F{fl}_FLIGHT{k}_Geometry';a=np.load(W/'v26_1'/I[n]['file']);m=solid(a['v'],a['f']);loss=m-house
  roi=cube([5.1999,7.4199,-.7],[7.8001,9.6801,7.1]);expected=m^roi;local_loss=expected-house
  out.append({'floor':fl,'flight':k,'original_whole_source_volume':m.volume(),'source_missing_from_current_m3':max(0,loss.volume()),'source_missing_inside_ordinary_room_m3':max(0,local_loss.volume())})
print(json.dumps(out,indent=2));(D/'Original_Source_Stair_Loss.json').write_text(json.dumps(out,indent=2),'utf8')
