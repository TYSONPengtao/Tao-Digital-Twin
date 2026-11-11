from v26_2_common import *
from shapely.geometry import shape,box,Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import shapely,shutil
D=W/'v26_3';OLD=W/'v26_2';D.mkdir(exist_ok=True)
old=json.loads((OLD/'Exact_House_Parts.json').read_text('utf8'));ls=old['layers']
def oldplan(z):
 r=next((r for r in ls if r['z_m'][0]<=z<r['z_m'][1]),None)
 return shape(r['outline'])if r else Polygon()
headplans=[oldplan(z)for z in [3.04,6.64,9.94]]
levels=sorted(set(round(x,4)for x in [x for r in ls for x in r['z_m']]+[-.45,1.65,2.085,3.05,3.32,3.45,5.985,6.65,6.92,9.94,9.95]))
layers=[]
for z0,z1 in zip(levels,levels[1:]):
 z=(z0+z1)/2;P=oldplan(z)
 # Extend existing opaque wall heads to the slab underside; apertures are
 # independently re-cut below. A beam remains at its real original datum.
 for j,(lo,hi)in enumerate([(3.05,3.32),(6.65,6.92)]):
  if lo<=z<hi:P=P.union(headplans[j])
 if -.45<=z<3.32:
  # Restore the missing room / stair-facing washroom front partition.
  P=P.union(box(9.2,7.2,10.7,7.4))
  if z<3.05:
   # The 200 mm masonry wall stays thin between the actual 400 mm columns.
   P=P.difference(box(9.3003,7.075,12.7997,7.1999)).difference(box(9.3003,7.4001,12.7997,7.525))
   P=P.difference(box(8.875,7.5003,8.9999,9.56)).difference(box(9.2001,7.5003,9.325,9.56))
  # Keep the existing 100 mm internal divider, not a column-wide enclosure.
  if z<3.05:P=P.difference(box(10.59,7.4003,10.90,9.825)).union(box(10.6,7.4,10.7,9.825))
  # Finish the thin divider against a real rear-window jamb, rather than
  # leaving a 200 mm air gap or passing the partition through the glass.
  P=P.union(box(10.6,9.5878,10.7102,9.9002))
  if z<1.65:
   P=P.difference(box(10.7,7.05,11.5,7.55)).difference(box(8.87,8.6,9.33,9.4))
 for floor,head in [(-.45,3.05),(3.45,6.65)]:
  if floor<=z<head:P=P.difference(box(4.1,1.85,8.9,2.55))
 P=shapely.set_precision(P.buffer(0),.0001)
 layers.append({'name':'V26_3_Registered_Height_Layer_'+str(len(layers)),'z_m':[z0,z1],'outline':P.__geo_interface__,'area_m2':P.area})
for r in old['extras']:shutil.copy2(OLD/r['file'],D/r['file'])
proof=dict(old['proof']);proof.update({'source_is_current_v26_2_height_profiles':True,'whole_plan_rebuilt_from_v20':False,'wall_heads_closed_to_slabs_m':[[3.05,3.32],[6.65,6.92]],'f1_room_to_washroom_partition_restored_m':[[9.2,7.2,-.45],[10.7,7.4,3.32]],'f1_inner_wc_partition_thickness_m':.1,'front_sliding_door_clear_openings_m':[[[4.1,1.85,-.45],[8.9,2.55,3.05]],[[4.1,1.85,3.45],[8.9,2.55,6.65]]],'roof_infill_basis':'Existing hip roof underside, with 3 mm concealed seating; existing roof silhouette unchanged'})
out={'layers':layers,'extras':old['extras'],'frames':[],'proof':proof}
(D/'Exact_House_Parts.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
(D/'Upper_Wall_Plan.json').write_text(json.dumps(headplans[2].__geo_interface__),encoding='utf8')
# Reuse the previously verified conforming surface algorithm with this turn's
# scoped profiles, then join the continuous upper wall closure once.
code=(W/'v26_2_direct_surface.py').read_text('utf8').replace('from v26_2_common import *','from v26_2_common import *\nD=W/\'v26_3\'').replace('V26_2_House_Flush_Continuous_Finished_Shell','V26_3_House_Connected_Walls_And_Stairs')
needle="components=[{'name':'Registered wall column beam slab and landing surface'"
where=code.index(needle)
insert='''
# The top wall profile follows the existing hip roof, rather than stopping at
# a nominal flat height. There is no added false ceiling or exterior change.
def extrude_plan(P,z0,z1):
 contours=[]
 for q in polygons(P):
  q=orient(q,1);contours.append(np.array(q.exterior.coords)[:-1]);contours.extend(np.array(r.coords)[:-1]for r in q.interiors)
 return mf.CrossSection(contours,mf.FillRule.NonZero).extrude(z1-z0).translate([0,0,z0])
upplan=shape(json.loads((D/'Upper_Wall_Plan.json').read_text('utf8')))
roofrow=next(r for r in p['extras']if r['name']=='ROOF_MAIN_JOINED_Geometry');ra=np.load(D/roofrow['file']);rt=ra['v'][ra['f']];rn=np.cross(rt[:,1]-rt[:,0],rt[:,2]-rt[:,0]);rp=np.unique(rt[rn[:,2]<-1e-6].reshape(-1,3),axis=0);rp[:,2]+=.003
bottom=np.array([[3.1,.6,9.93],[13.8,.6,9.93],[13.8,10.6,9.93],[3.1,10.6,9.93]])
roofspace=mf.Manifold.hull_points(np.vstack([rp,bottom]))
mainplan=upplan.intersection(box(3.85,-20,30,30));westplan=upplan.intersection(box(-.16,6.6,3.85,10.01))
closure=(extrude_plan(mainplan,9.94,12.)^roofspace)+(extrude_plan(westplan,9.94,10.153))
base=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64),np.array(f,dtype=np.uint64)))
assert base.status()==mf.Error.NoError,base.status()
joined=base+closure
assert joined.status()==mf.Error.NoError,joined.status()
before_volume=joined.volume();joined=joined.simplify(.00002)
assert abs(joined.volume()-before_volume)<.0001,('Unexpected simplification volume change',before_volume,joined.volume())
a=joined.to_mesh64();jv=np.array(a.vert_properties[:,:3],np.float32).astype(float);jf=np.array(a.tri_verts,np.int32)
V=[];F=[];MI=[];UV=[];cache={}
for tr in jv[jf]:emit(tr)
v=np.array(V);f=np.array(F,np.int32);mi=np.array(MI,np.int32);uv=np.array(UV)
ed=np.sort(np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,ct=np.unique(ed,axis=0,return_counts=True)
print('JOINED_ROOF_WALL_CLOSURE',len(f),dict(zip(*np.unique(ct,return_counts=True))),'volume',joined.volume(),flush=True)
assert (ct==2).all(),('Closure float32 topology',dict(zip(*np.unique(ct,return_counts=True))))
'''
# box is needed only for the roof-domain split.
code=code[:where]+insert+code[where:];code=code.replace('from shapely.geometry import Polygon,shape','from shapely.geometry import Polygon,shape,box')
# Paint the true inward roof fascia underside in addition to the main roof.
code=code.replace("eu=a['uv']","eu=a['uv'];et=ev[ef];en=np.cross(et[:,1]-et[:,0],et[:,2]-et[:,0]);emi[en[:,2]<-1e-8]=2")
(W/'v26_3_surface.py').write_text(code,encoding='utf8')
print('V26_3_LAYER_PROFILES_READY',len(layers),flush=True)
