import sys,json,math,csv,copy
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['geomlibs','np1','libs']]
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely.affinity import rotate,translate
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent; S=json.loads(Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
def world(poly,e):
 return translate(rotate(poly,e.get('angle',0),origin=(0,0),use_radians=True),*e.get('origin',[0,0,0])[:2])
def interval(p,e):
 g=p['geometry'];t=g['type'];dz=e.get('origin',[0,0,0])[2]
 if t=='prism_holes':return world(Polygon(g['outer'],g.get('holes',[])),e),g['z']+dz,g['z']+g['height']+dz
 if t=='box':
  x,y,z=g['origin'];w,d,h=g['size'];return world(box(x,y,x+w,y+d),e),z+dz,z+h+dz
 return None
walls=[]
for e in S['elements']:
 if e['layer'] in ['10_WALL_EXT','11_WALL_INT']:
  for p in e.get('parts',[]):
   r=interval(p,e)
   if r:walls.append((e['name'],*r))
doors=[e for e in S['elements'] if e['layer']=='30_DOOR']; results=[]
for e in doors:
 d=S['definitions'][e['definition']];w=d['parameters']['Width'];h=d['parameters']['Height'];z=e['origin'][2]
 cutter=world(box(.001,-.16,w-.001,.16),e)
 vol=0;clearvol=0;hosts=set();framewidth=.045 if 'WOOD' in e['definition'] else .06;clear=world(box(framewidth+.001,-.16,w-framewidth-.001,.16),e)
 for name,P,a,b in walls:
  dh=max(0,min(z+h-.001,b)-max(z+.001,a))
  if dh<=0:continue
  inter=P.intersection(cutter).area
  vol+=inter*dh;clearvol+=P.intersection(clear).area*dh
  if inter>1e-8:hosts.add(name)
 # Match within 250mm margin, even when correctly empty.
 nearby=set(n for n,P,a,b in walls if a<z+1<b and P.distance(cutter)<.25)
 leaf=d['parts'][0]['geometry'] if 'WOOD' in e['definition'] else None
 results.append(dict(name=e['name'],floor=next((f for f in [1,2,3] if abs(z-S['levels'][f-1])<.01),None),origin=e['origin'],angle=e.get('angle',0),definition=e['definition'],outer_width_m=w,outer_height_m=h,clear_width_model_m=(w-.09 if leaf else w-.12),clear_height_model_m=(h-.045 if leaf else h-.12),wall_occupancy_inside_nominal_opening_m3=round(vol,12),wall_occupancy_inside_clear_opening_m3=round(clearvol,12),intersecting_wall_names=sorted(hosts),nearby_wall_names=sorted(nearby),status=e.get('status','NOT_FIELD_VERIFIED'),source=e.get('source'),pivot_defined=any('pivot' in x.lower() for x in d['parameters']),part_roles_defined=any('role' in p for p in d['parts'])))
(O/'Door_Wall_Audit.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'Door_Wall_Audit.csv').open('w',encoding='utf-8-sig',newline='') as fp:
 keys=['name','floor','origin','angle','definition','outer_width_m','outer_height_m','clear_width_model_m','clear_height_model_m','wall_occupancy_inside_nominal_opening_m3','wall_occupancy_inside_clear_opening_m3','status','pivot_defined','part_roles_defined'];wr=csv.DictWriter(fp,fieldnames=keys);wr.writeheader();wr.writerows({k:r[k] for k in keys} for r in results)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',27)
images=[]
for f,z in enumerate(S['levels'][:3],1):
 I=Image.new('RGB',(1700,1500),'white');D=ImageDraw.Draw(I);scale=100.;left=150.;bottom=1210.
 def pix(p):return (left+p[0]*scale,bottom-p[1]*scale)
 D.text((90,36),f'V4 F{f} - current drawing-derived layout (not an as-built plan)',font=bold,fill=(50,50,50));D.text((90,78),f'Horizontal cut: z = {z+1.0:.2f} m; x/y are local model coordinates.',font=font,fill=(70,70,70))
 for x in S['grid_x']:
  D.line([pix((x,-.2)),pix((x,10.6))],fill=(215,222,230),width=1);D.text((pix((x,0))[0]-22,1245),f'x={x:g}',font=small,fill=(70,70,70))
 for y in S['grid_y']:
  D.line([pix((-.4,y)),pix((13.4,y))],fill=(215,222,230),width=1);D.text((65,pix((0,y))[1]-9),f'y={y:g}',font=small,fill=(70,70,70))
 def poly(P,color):
  for p in (list(P.geoms) if hasattr(P,'geoms') else [P]):
   if p.geom_type!='Polygon':continue
   D.polygon([pix(q) for q in p.exterior.coords],fill=color)
   for ring in p.interiors:D.polygon([pix(q) for q in ring.coords],fill='white')
 for name,P,a,b in walls:
  if a-1e-8<z+1<b-1e-8:poly(P,(110,120,135) if name.startswith('PARTITIONS') else (70,78,92))
 for e in S['elements']:
  if e['layer']=='20_COLUMN':
   for p in e.get('parts',[]):
    r=interval(p,e)
    if r and r[1]<z+1<r[2]:poly(r[0],(40,40,40))
 for idx,r in enumerate([r for r in results if r['floor']==f],1):
  e=next(e for e in doors if e['name']==r['name']);w=r['outer_width_m'];q=world(box(0,-.03,w,.03),e);poly(q,(199,90,55));c=q.centroid;xx,yy=pix((c.x,c.y));D.ellipse((xx-18,yy-18,xx+18,yy+18),fill=(255,226,151),outline=(160,110,60),width=2);D.text((xx-7,yy-11),str(idx),font=small,fill=(30,30,30))
 for idx,r in enumerate([r for r in results if r['floor']==f],1):D.text((90,1300+(idx-1)*27),f"{idx}. {r['name']}  ({r['origin'][0]:g}, {r['origin'][1]:g})  W={r['outer_width_m']:g} m",font=small,fill=(45,45,45))
 I.save(O/f'V4_F{f}_Door_Plan.png');images.append(I)
thumb=Image.new('RGB',(1700,1500*3),'white')
for i,I in enumerate(images):thumb.paste(I,(0,i*1500))
thumb.resize((1133,3000)).save(O/'V4_All_Floors_Door_Plans.jpg',quality=95)
print('15 door audit: clear-opening wall overlap =', sum(r['wall_occupancy_inside_clear_opening_m3'] for r in results))
