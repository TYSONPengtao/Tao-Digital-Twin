"""V5 local wall-opening editor. No I/O or source model changes at import.
The caller must supply evidence-supported transforms and write a new version.
"""
import math,copy
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely.affinity import rotate,translate

def _world(p,e):
 return translate(rotate(p,e.get('angle',0),origin=(0,0),use_radians=True),*e.get('origin',[0,0,0])[:2])
def _local(p,e):
 x,y=e.get('origin',[0,0,0])[:2]
 return rotate(translate(p,-x,-y),-e.get('angle',0),origin=(0,0),use_radians=True)
def _cutter(scene,door,host,depth):
 p=scene['definitions'][door['definition']]['parameters'];w=p.get('Opening_Width',p['Width']);h=p.get('Opening_Height',p['Height'])
 shape=_local(_world(box(0,-depth/2,w,depth/2),door),host)
 z=door['origin'][2]-host.get('origin',[0,0,0])[2]
 return shape,z,z+h

def _parts(shape,z,h,material):
 geoms=list(shape.geoms) if hasattr(shape,'geoms') else [shape];out=[]
 for p in geoms:
  if p.geom_type=='GeometryCollection':
   out.extend(_parts(p,z,h,material));continue
  if p.geom_type!='Polygon' or p.area<1e-10:continue
  if not p.is_valid:raise ValueError('Wall patch produced invalid polygon')
  out.append({'geometry':{'type':'prism_holes','outer':[list(q) for q in list(p.exterior.coords)[:-1]],'holes':[[list(q) for q in list(r.coords)[:-1]] for r in p.interiors],'z':z,'height':h},'material':material})
 return out

def patch_door_opening(scene,host_name,old_door,new_door,cutter_depth_m=.50):
 """Fill the old opening and cut the new one on a supplied scene in memory.
 Assumes host is an existing, vertical prism_holes partition. Leaves source
 beams/slabs/doors untouched. Return change metrics. Not for a removed wall,
 new wall, window-to-door conversion, or an opening spanning another host.
 """
 host=next(e for e in scene['elements'] if e['name']==host_name)
 original=copy.deepcopy(host['parts']);materials={p['material'] for p in original}
 if len(materials)!=1:raise ValueError('Mixed wall materials require separate patches')
 if any(p['geometry']['type']!='prism_holes' for p in original):raise ValueError('Expected vertical prism_holes host only')
 material=next(iter(materials));bands=[(Polygon(p['geometry']['outer'],p['geometry'].get('holes',[])),p['geometry']['z'],p['geometry']['z']+p['geometry']['height']) for p in original]
 envelope=unary_union([p for p,_,_ in bands]);old,oa,ob=_cutter(scene,old_door,host,cutter_depth_m);new,na,nb=_cutter(scene,new_door,host,cutter_depth_m)
 fill=old.intersection(envelope);newhost=new.intersection(envelope)
 if fill.area<1e-8:raise ValueError('Old opening is not represented by the host envelope; review host')
 if newhost.area<1e-8:raise ValueError('Target door does not cross this host wall; review host')
 beams=[];hz=host.get('origin',[0,0,0])[2]
 for e in scene['elements']:
  if not e['name'].startswith('BEAM_'):continue
  for p in e.get('parts',[]):
   g=p['geometry']
   if g['type']!='box':raise ValueError('Unexpected non-box beam geometry')
   x,y,z=g['origin'];w,d,h=g['size'];beam=_local(_world(box(x,y,x+w,y+d),e),host);a=z+e.get('origin',[0,0,0])[2]-hz
   if beam.intersects(envelope):beams.append((beam,a,a+h))
 low=min(a for _,a,_ in bands);high=max(b for _,_,b in bands)
 if not low-1e-8<=na<nb<=high+1e-8:raise ValueError('Target opening exceeds existing host elevation range')
 levels=sorted({round(v,9) for v in [low,high,oa,ob,na,nb]+[v for _,a,b in bands for v in [a,b]]+[v for _,a,b in beams for v in [a,b] if low<v<high] if low-1e-8<=v<=high+1e-8})
 result=[];added=0.;removed=0.
 for a,b in zip(levels[:-1],levels[1:]):
  if b-a<1e-9:continue
  mid=(a+b)/2;selected=[p for p,lo,hi in bands if lo-1e-8<mid<hi+1e-8]
  if not selected:continue
  previous=unary_union(selected);shape=previous
  if oa-1e-8<mid<ob-1e-8:shape=shape.union(fill)
  if na-1e-8<mid<nb-1e-8:shape=shape.difference(new)
  cut=[p for p,lo,hi in beams if lo-1e-8<mid<hi+1e-8]
  if cut:shape=shape.difference(unary_union(cut))
  added+=shape.difference(previous).area*(b-a);removed+=previous.difference(shape).area*(b-a)
  result.extend(_parts(shape,a,b-a,material))
 if not result:raise ValueError('Patch unexpectedly emptied host')
 host['parts']=result;host['v5_local_patch']={'old_door_id':old_door['name'],'new_door_id':new_door['name'],'old_origin':old_door['origin'],'new_origin':new_door['origin'],'old_angle':old_door.get('angle',0),'new_angle':new_door.get('angle',0),'evidence':new_door.get('video_evidence','UNSET'),'beam_cores_retained':True}
 return {'host':host_name,'added_wall_m3':added,'removed_wall_m3':removed,'delta_wall_m3':added-removed,'old_parts':len(original),'new_parts':len(result)}
