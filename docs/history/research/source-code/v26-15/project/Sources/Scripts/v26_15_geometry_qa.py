from v26_2_common import *
from shapely.geometry import Polygon,box as box2
from shapely.ops import unary_union
import hashlib
D=W/'v26_15';O=Path('E:/jz/JIA/Rebuild_V26_15');P=O/'Blender/Architecture_Complete_V26_15.blend';src=json.loads((D/'Input/Source_Index.json').read_text('utf8'));S={r['name']:r for r in src['objects']};out=json.loads((D/'Final/Geometry_Index.json').read_text('utf8'));F={r['name']:r for r in out};checks=[]
def ck(n,b,**kw):checks.append({'check':n,'pass':bool(b),**kw});print('GEOM',n,bool(b),kw if not b else'',flush=True)
def get(n,new=False):
 r=(F if new else S)[n];a=np.load(D/('Final'if new else'Input')/r['file']);return r,a,solid(a['v'],a['f'],n)
HN='V26_3_House_Connected_Walls_And_Stairs';GN='V26_2_Continuous_Ground_And_Perimeter_Shell';TN='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry'
_,ha,h0=get(HN);_,hb,h=get(HN,True);_,ga,g0=get(GN);_,gb,g=get(GN,True);roi=cube([3.4001,-.4999,-.7499],[9.5999,2.3499,-.3001]);before=(h0^roi)+(g0^roi);after=(h^roi)+(g^roi);dv=[(after-before).volume(),(before-after).volume()];over=(h^g^roi).volume()
lip=cube([3.3999,-.3002,-.6001],[9.6001,-.2199,-.2999]);outside_removed=((before-after)-lip).volume();ck('Saved porch overlap removed and only obsolete80mm front lip trimmed to the four-sided boundary',abs(over)<2e-8 and abs(dv[0])<2e-7 and .04<dv[1]<.067 and abs(outside_removed)<2e-7,overlap_before_m3=(h0^g0^roi).volume(),overlap_after_m3=over,combined_difference_m3=dv,outside_front_lip_removed_m3=outside_removed)
rr=F[HN];tt=hb['v'][hb['f']];cc=tt.mean(1);nn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);top=(cc[:,0]>3.68001)&(cc[:,0]<9.31999)&(cc[:,1]>-.21999)&(cc[:,1]<2.21999)&(abs(cc[:,2]+.45)<1e-6)&(nn[:,2]>1e-10);names=sorted({rr['materials'][i]for i in hb['mi'][top]});ck('Four-sided porch top has one continuous original stone finish without alternating tile patches',names==['M_Floor'],materials=names,top_triangles=int(top.sum()))
ck('House remains one positive closed body and original four ground components remain positive',len(h.decompose())==1 and len(g.decompose())==len(g0.decompose())==4 and all(p.volume()>0 for p in g.decompose()),house_components=len(h.decompose()),ground_components=len(g.decompose()))
stair=[]
for z0,z1 in[(3.319999933,3.450000048),(6.920000076,7.050000191)]:
 c=cube([4.02001,7.42001,z0+.00001],[4.20999,7.60999,z1-.00001]);stair.append({'z_m':[z0,z1],'before_m3':(h0^c).volume(),'after_m3':(h^c).volume()})
ck('Both former stair-corner seal cubes are now air outside the original wall planes',all(q['before_m3']>.0046 and abs(q['after_m3'])<1e-9 for q in stair),samples=stair)
well=cube([5.2001,8.5001,-.4498],[7.7999,8.5999,7.0499]);ck('Existing fitted narrow stairwell remains a through void',abs((h^well).volume())<1e-8,occupied_m3=(h^well).volume())
def xysection(m,z):
 pos=[];neg=[]
 for p in m.slice(z).to_polygons():
  a=np.asarray(p);sgn=np.sum(a[:,0]*np.roll(a[:,1],-1)-np.roll(a[:,0],-1)*a[:,1]);(pos if sgn>0 else neg).append(Polygon(a))
 return unary_union(pos).difference(unary_union(neg))
sections=[]
for z in[.8,1.48,2.,3.36,3.43,4.3,5.23,6.98,7.03,8.5]:
 b=xysection(h0,z);a=xysection(h,z);scope=box2(4.0199,7.4199,4.2101,7.6101) if 3.3199<z<3.4501 or 6.9199<z<7.0501 else Polygon();difference=a.symmetric_difference(b).difference(scope);sections.append({'z_m':z,'unexpected_area_m2':difference.area})
ck('Stair landings steps room plans and previous WC returns unchanged outside the two seal footprints',max(q['unexpected_area_m2']for q in sections)<1e-6,slices=sections)
tr,ta,_=get(TN);fr,fa,_=get(TN,True);v=ta['v'];badV=(v[:,0]>16.219)&(v[:,0]<16.254)&(v[:,1]>-14.402)&(v[:,1]<-14.356)&(v[:,2]>-.392)&(v[:,2]<1.744);bad=np.all(badV[ta['f']],1);same=np.array_equal(ta['v'][ta['f'][~bad]],fa['v'][fa['f']])and np.array_equal(ta['uv'][~bad].astype(np.float32),fa['uv'])and np.array_equal(ta['mi'][~bad],fa['mi'])
ck('Only six detached storage timber triangles removed; all retained triangle attributes exact',same and bad.sum()==6 and len(fa['f'])==5934,removed_triangles=int(bad.sum()),retained_triangles=len(fa['f']))
gate=[]
for x in np.linspace(8.4,9.4,11):
 for y in np.linspace(-11.59,-11.40,6):
  hs=g.ray_cast([x,y,0.],[x,y,-1.]);up=[q.position[2]for q in hs if q.normal[2]>.999];gate.append(max(up)if up else-999.)
ck('Former gate wall trench filled at the existing adjacent ground level',all(abs(z+.4000244140625)<2e-6 for z in gate),native_top_min_m=min(gate),native_top_max_m=max(gate))
ck('Source master SHA remains unchanged',hashlib.sha256(Path(src['model']).read_bytes()).hexdigest()==src['sha256'])
fail=[r for r in checks if not r['pass']];report={'status':'PASS'if not fail else'FAIL','model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':checks,'failures':fail};(O/'Reports/V26_15_Geometry_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print('GEOMETRY_QA_DONE',len(checks),len(fail),flush=True)
if fail:raise AssertionError(fail)
