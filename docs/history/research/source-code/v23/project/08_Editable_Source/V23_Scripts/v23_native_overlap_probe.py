from v23_common import *
import rhino3dm as rh,gc
O=Path('E:/jz/JIA/Rebuild_V23');F=rh.File3dm.Read(str(O/'04_Rhino/Architecture_Complete_V23_ALIGNED_ENU.3dm'));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));aa=math.radians(C['rotation_deg']);R=np.array([[math.cos(aa),-math.sin(aa),0],[math.sin(aa),math.cos(aa),0],[0,0,1]]);origin=np.array(C['origin'])
ns=['GATE_V23_LEFT_WALL_JAMB_CLOSURE','SITE_V21_GATE_REFERENCE_LAYER_03','SITE_V21_GATE_REFERENCE_LAYER_04'];arrays={n:[]for n in ns}
for o in F.Objects:
 for n in ns:
  if not o.Attributes.Name.startswith(n+'__'):continue
  g=o.Geometry;v=(np.array([[p.X,p.Y,p.Z]for p in g.Vertices.ToPoint3dArray()])-origin)@R;f=[]
  for ff in g.Faces:
   f.append(list(ff[:3]))
   if ff[3]!=ff[2]:f.append([ff[0],ff[2],ff[3]])
  arrays[n].append((o.Attributes.Name,F.Materials[o.Attributes.MaterialIndex].Name,v,np.array(f,np.uint64)))
del F;gc.collect();out=[]
for dec in [10,9,8,7,6]:
 ms={}
 for n in ns:
  ps=[]
  for name,mat,v,f in arrays[n]:
   vv,iv=np.unique(np.round(v,dec),axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(vv,iv[f].astype(np.uint64)));assert m.status()==mf.Error.NoError,(name,dec,m.status());ps.append(m)
  ms[n]=uni(ps)
 j=ms[ns[0]];r=ms[ns[1]]+ms[ns[2]];ov=j^r;row={'decimals_m':dec,'jamb_m3':j.volume(),'frame_art_m3':r.volume(),'overlap_m3':ov.volume(),'overlap_components':[{'volume_m3':p.volume(),'bbox':p.bounding_box()}for p in ov.decompose() if abs(p.volume())>1e-10]};out.append(row);print(json.dumps(row),flush=True)
(W/'v23_native_overlap_diagnosis.json').write_text(json.dumps({'actual_native_objects_per_node':{n:len(x)for n,x in arrays.items()},'precision_trials':out},indent=2),encoding='utf8')
