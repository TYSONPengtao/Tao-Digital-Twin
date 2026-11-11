from v26_2_common import *
from shapely.geometry import box,Polygon
from shapely.geometry.polygon import orient
p=json.loads((D/'Prepared_House.json').read_text('utf8'));proof=p['proof']['frames']
for r in p['objects'][1:]:
 name=r['name'];s=I[name];lo,hi=np.array(s['bounds']);rr=next(q for q in proof if q['name']==name);axis=rr['axis'];other=1-axis;d0,d1=rr['frame_depth_limits_m'];lo[2]+=rr['vertical_correction_m'];hi[2]+=rr['vertical_correction_m'];left=.042 if name=='DOOR_BATH_F3_R__FRAME_Geometry'else .045;right=left;poly=box(lo[other],lo[2],hi[other],hi[2]).difference(box(lo[other]+left,lo[2]-.01,hi[other]-right,hi[2]-.045));poly=orient(poly,1);m=mf.CrossSection([np.array(poly.exterior.coords)[:-1]]).extrude(d1-d0);matrix=[[0,0,1,d0],[1,0,0,0],[0,1,0,0]]if axis==0 else[[1,0,0,0],[0,0,1,d0],[0,1,0,0]];m=m.transform(matrix);a=m.to_mesh64();v=np.array(a.vert_properties[:,:3]);f=np.array(a.tri_verts);fn='FRAME_ANALYTIC_'+name+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=np.zeros(len(f),np.int32),uv=uv_project(v,f));r.update(file=fn,materials=s['materials'],triangles=len(f),reason='One-piece full-depth U-frame with continuous head and jambs; 3mm edge rebates at the F3 right wood door');print('ANALYTIC_FRAME',name,len(f),flush=True)
(D/'Prepared_House.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8')
