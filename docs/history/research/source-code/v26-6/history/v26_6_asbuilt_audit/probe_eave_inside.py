from pathlib import Path
exec((Path(__file__).parent/'saved_native_qa.py').read_text('utf8').split('checks=[]')[0]+'checks=[]')
for x in [3.,3.049,3.051,3.10,3.15,3.179,3.181,3.3]:
 for y in [7.7,8.2,8.7,9.2,9.5]:
  hs=m.ray_cast([x,y,9.6],[x,y,10.3]);h=hs[0]if hs else None
  if h and abs(h.position[2]-10.02)>.001:print('CEILING_DROP',x,y,h.position)
