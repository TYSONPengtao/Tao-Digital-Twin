from v26_2_common import *
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
D=W/'v26_14';J=json.loads((D/'Source_Index.json').read_text('utf8'));r=next(r for r in J['objects']if r['name']=='V26_3_House_Connected_Walls_And_Stairs');a=np.load(D/r['file']);m=solid(a['v'],a['f']);rows=[]
def polygon_section(z):
 pos=[];neg=[]
 for p in m.slice(z).to_polygons():
  p=np.array(p);signed=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]);(pos if signed>0 else neg).append(Polygon(p))
 return unary_union(pos).difference(unary_union(neg))
for fl,z0 in [(1,-.45),(2,3.4500243664),(3,7.0500001907)]:
 for cx in [0.,2.2,3.9,9.1,10.8,13.]:
  z=z0+1.25;roi=box(cx-.65,6.65,cx+.65,7.95);sec=polygon_section(z).intersection(roi)
  probes=[]
  for y in [6.7,6.90,6.98,6.999,7.01,7.029,7.031,7.06,7.12,7.18,7.3,7.42,7.52,7.569,7.571,7.601,7.62,7.7,7.9]:
   h=m.ray_cast([cx-.5,y,z],[cx+.5,y,z]);probes.append({'y':y,'wall_x_intervals':[[float(q.position[0]),float(q.normal[0])]for q in h]})
  rows.append({'floor':fl,'center_x':cx,'z':z,'outline':sec.__geo_interface__,'probes':probes})
(D/'Wall_Sections_Before.json').write_text(json.dumps(rows,indent=2),'utf8')
for r in rows:
 if r['floor']==2 and r['center_x']in [2.2,3.9,9.1,10.8]:
  print('SECTION',r['floor'],r['center_x'],flush=True)
  for t in r['probes']:print(t,flush=True)
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGB',(2100,1160),'#eef2f3');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
dr.text((24,15),'V26.13 原生墙体剖面；虚线为此前交点修正范围',font=font,fill='#223c47')
for i,r in enumerate(rows):
 ox=(i%6)*350;oy=(i//6)*360+70;cx=r['center_x'];dr.rectangle((ox+8,oy+6,ox+342,oy+350),fill='white');dr.text((ox+16,oy+12),f"F{r['floor']} X={cx:g}",font=font,fill='#203b47')
 def pt(p):return(ox+175+(p[0]-cx)*220,oy+200-(p[1]-7.3)*220)
 g=__import__('shapely').geometry.shape(r['outline']).simplify(.000001,preserve_topology=True)
 for p in(g.geoms if hasattr(g,'geoms')else[g]):
  if p.is_empty:continue
  dr.polygon([pt(q)for q in p.exterior.coords],fill='#c4d7df',outline='#23434f',width=2)
 for y in[7.03,7.57]:
  ya=pt((cx,y))[1]
  for x in range(ox+24,ox+325,12):dr.line((x,ya,x+6,ya),fill='#bf7867',width=2)
im.save(D/'Wall_Sections_Before.png')
print('SECTIONS_DONE',len(rows),flush=True)
