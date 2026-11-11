exec(open(__file__.replace('preview_plan.py','plan.py'),encoding='utf8').read().split('fig,ax=')[0])
from shapely.geometry import shape,Polygon
p=json.loads((D/'Prepared_Geometry.json').read_text('utf8'))['proof'];fig,ax=plt.subplots(figsize=(13,10));ax.set_aspect('equal')
for n,col in [('outer_pad','#f5f5f5'),('Low_Main_Court','#b0bbbf'),('High_North_Lane_And_Rear','#d4baa0'),('rear_separator','#999999')]:
 s=shape(p[n]['outline']);parts=[s]if s.geom_type=='Polygon'else list(s.geoms)
 for q in parts:xy=np.array(q.exterior.coords);ax.fill(*xy.T,color=col,ec='black',lw=.6)
q=np.array(p['curb']['route_xy']);ax.plot(*q.T,color='blue',lw=3)
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_1_Geometry']:
 a=source(n);t=a['v'][a['f']];ax.add_collection(PolyCollection(t[:,:,:2],facecolor='#555555',edgecolor='none'))
for x,y,w,h,tag in [(0,0,13,10,'HOUSE'),(8.15,-11.7,5.7,8.9,'KITCHEN')]:ax.add_patch(plt.Rectangle((x,y),w,h,fc='#eeeeee',ec='black'));ax.text(x+w/2,y+h/2,tag,ha='center')
ax.set_xlim(-27,17);ax.set_ylim(-17,14);ax.grid(alpha=.2);fig.savefig(D/'Plan_After.png',dpi=140)
