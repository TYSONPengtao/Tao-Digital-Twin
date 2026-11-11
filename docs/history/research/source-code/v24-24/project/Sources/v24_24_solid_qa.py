from v24_24_common import *
R=Path('E:/jz/JIA/Rebuild_V24_24/Reports');idx=json.loads((D/'Saved_Geometry_Index.json').read_text());checks=[];ms={}
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
for row in idx['objects']:
 d=np.load(D/row['file']);m=solid(d['v'],d['f'],row['name']);ms[row['name']]=m;err=abs(m.volume()-row['volume_m3']);ck('Saved closed solid / '+row['name'],m.status()==mf.Error.NoError and err<max(3e-5,row['volume_m3']*3e-5),bodies=len(m.decompose()),volume_error_m3=err)
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';wall=ms[n];old=load(n);back=cube([0,-11.73,-2],[25,5,10]);err=((old-wall)^back).volume()+((wall-old)^back).volume();ck('Gate back wall volume retained exactly',abs(err)<3e-5,symmetric_difference_m3=err)
cut=cube([8.34,-12.25,-.8],[13.205,-11.73,6.]);err=((old-wall)-cut).volume()+((wall-old)-cut).volume();ck('Masonry edits confined to requested front layer',abs(err)<3e-5,outside_scope_difference_m3=err)
for n in ['V24_22_South_Verge','V24_22_South_Verge_Bead']:
 back_side=cube([0,-11.62,-2],[25,5,10]);a=load(n);b=ms[n];err=abs(((a-b)^back_side).volume())+abs(((b-a)^back_side).volume());ck('Front cornice moves without changing back side / '+n,err<1e-8,back_difference_m3=err)
roof_return=ms['V24_24_Gate_Front_Closed_Roof_Return'];ck('Roof notch return stays completely on front side',abs((roof_return^back).volume())<1e-8)
gate=cube([7.73,-12.,-.6],[8.30,-11.2,3.12]);ck('Masonry does not cover carved gate pier',abs((wall^gate).volume())<1e-9)
closure=ms['V24_24_Kitchen_North_Veranda_White_Closure'];ck('White closure meets the existing raking beam',closure.min_gap(load('V24_22_Porch_Single_Cross_Beams'),.025)<.001)
ck('White closure meets recessed north wall',closure.min_gap(wall,.025)<.001)
ck('White closure meets veranda slab',closure.min_gap(load('SITE_KITCHEN_STONE_FLOOR_Geometry'),.025)<.001)
front_post_zone=cube([8.15,-3.245,-.05],[8.54,-3.055,2.34]);ck('White wall keeps front timber post visible',abs((closure^front_post_zone).volume())<1e-9)
floor=ms['V24_24_House_Front_Matching_Stone_Paving'];outline=[(.125,-3.60),(13.10,-3.60),(13.10,1.90),(.125,1.90)];zone=section(outline,3).translate([0,0,-2]);outside=abs((floor-zone).volume());ck('New paving confined to marked house-front band',outside<3e-7,outside_saved_float32_volume_m3=outside)
fail=[c for c in checks if not c['pass']];(R/'V24_24_Solid_QA.json').write_text(json.dumps({'status':'PASS_SAVED_SOLIDS_AND_LOCAL_SCOPE'if not fail else'FAIL','model_sha256':idx['model_sha256'],'checks':checks,'failures':fail},ensure_ascii=False,indent=2));print('V24_SOLID_QA',len(checks),'FAIL',len(fail))
for c in fail:print('FAIL',c)
