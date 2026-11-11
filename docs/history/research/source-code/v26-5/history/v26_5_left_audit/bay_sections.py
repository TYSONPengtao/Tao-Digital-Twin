exec((__import__('pathlib').Path(__file__).parent/'probe.py').read_text('utf8').split('for n in [')[0])
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from PIL import Image,ImageDraw
im=Image.new('RGB',(1500,900),'white');draw=ImageDraw.Draw(im)
class AX:
 def __init__(self,j,x0):self.j=j;self.x0=x0
 def pts(self,x,y):return [(round(60+self.j*750+(a-self.x0-.4)*1200),round(800-(b-.95)*1800)) for a,b in zip(x,y)]
 def fill(self,x,y,alpha=None,color=None):draw.polygon(self.pts(x,y),fill=color)
 def plot(self,x,y,color=None,lw=1):draw.line(self.pts(x,y),fill=color,width=2)
 def set_xlim(self,*args):pass
 def set_ylim(self,*args):pass
 def set_aspect(self,*args):pass
 def grid(self,*args):pass
 def set_title(self,t):draw.text((40+self.j*750,20),t,fill='black')

def slice_shape(m,z):
 pp=m.slice(z).to_polygons();p=mf.CrossSection(pp,mf.FillRule.NonZero);ps=[];holes=[]
 for path in p.to_polygons():
  q=np.array(path);ar=.5*np.sum(np.cross(q,np.roll(q,-1,axis=0)));(ps if ar>0 else holes).append(Polygon(q))
 return unary_union(ps).difference(unary_union(holes))
a=np.load(D/I['V26_3_House_Connected_Walls_And_Stairs']['file']);house=solid(a['v'],a['f'],'house')
axes=[AX(0,9.1),AX(1,0.)];out=[]
for ax,(f,s,z,x0) in zip(axes,[(1,'R',1.,9.1),(1,'L',1.,0.)]):
 clip=box(x0+.45,.9,x0+.95,1.32);hp=slice_shape(house,z).intersection(clip).simplify(.00002,preserve_topology=True)
 for poly in [hp]if hp.geom_type=='Polygon'else hp.geoms:
  ax.fill(*poly.exterior.xy,alpha=.5,color='orange');ax.plot(*poly.exterior.xy,color='brown',lw=1)
  out.append({'bay':f'F{f}_{s}','house_corner_profile':list(poly.exterior.coords)})
 for j in range(3):
  nm=f'BAY_WINDOW_F{f}_{s}_{j}_Geometry';a=np.load(D/I[nm]['file'])
  for mi,col in [(0,'black'),(1,'cyan')]:
   m=solid(a['v'],a['f'][a['mi']==mi],nm);p=slice_shape(m,z).intersection(clip)
   for q in [p]if p.geom_type=='Polygon'else p.geoms:
    if q.is_empty:continue
    ax.fill(*q.exterior.xy,alpha=.5,color=col)
 ax.set_xlim(x0+.4,x0+.95);ax.set_ylim(.95,1.35);ax.set_aspect('equal');ax.grid();ax.set_title(f'F{f}_{s}: orange=house, black=frame, cyan=glass')
im.save(Path(__file__).parent/'front_bay_corner_sections.png')
(Path(__file__).parent/'front_bay_corner_sections.json').write_text(json.dumps(out,indent=2),'utf8')
