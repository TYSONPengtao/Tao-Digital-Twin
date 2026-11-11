from pathlib import Path
p=Path(__file__).parent/'build_candidate.py';s=p.read_text('utf8');s=s.replace("p=[q for q in p if q[0]<7.44];startreturn=np.array([7.44,ya,line(7.44)])", "p=[q for q in p if q[0]<7.70];startreturn=np.array([7.70,ya,line(7.70)])").replace("np.array([.40,0,slope*.40]),np.array([.40,0,0])", "np.array([.14,0,slope*.14]),np.array([.14,0,0])")
s=s.replace('def spindle(x,y,z,top,tag,tangent=None):','def spindle_raw(x,y,z,top,tag,tangent=None):')
wrap='''SOURCE_BALUSTERS=json.loads((W/'v26_1/Prepared_Railing.json').read_text('utf8'))['proof']['balusters']
def spindle(x,y,z,top,tag,tangent=None):
 T=np.array([1.,0.,0.])if tangent is None else np.array(tangent);slope=T[2]*T[:2]/max(float(T[:2]@T[:2]),1e-12)
 old=min((b for b in SOURCE_BALUSTERS if b['tag']==tag),key=lambda b:np.linalg.norm(np.array(b['xy'])-[x,y]));xy=np.array(old['xy']);assert np.linalg.norm(xy-[x,y])<.05
 top=float(top+slope@(xy-[x,y]));spindle_raw(float(xy[0]),float(xy[1]),float(old['seat_z_m']),top,tag,T)

'''
s=s.replace('def hz(n,x,y):',wrap+'def hz(n,x,y):');p.write_text(s,'utf8')
