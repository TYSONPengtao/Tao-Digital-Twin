"""Fresh saved .3dm readback of final seam nodes, with author/cache parity and seam QA."""
import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent.parent;D=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh
B=Path('E:/jz/JIA/Rebuild_V20');P=B/'04_Rhino/Architecture_Complete_V20_ALIGNED_ENU.3dm';log=W/'v20_assemble_final.log';assert 'V20 NATIVE SAVED' in log.read_text(encoding='utf8'), 'Wait until final native saved marker'
I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'))};Q=json.loads((D/'Seam_Correction.json').read_text(encoding='utf8'));E={e['name']:e for e in Q['replace']}
C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
F=rh.File3dm.Read(str(P));rows=[];actual_paths={}
for n in E:
 oo=[ob for ob in F.Objects if ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__')];assert oo,n;vv=[];ff=[];uv=[];nn=[];mi=[];mats=[];native=[]
 for ob in oo:
  mm=ob.Geometry;assert isinstance(mm,rh.Mesh) and mm.IsValid,(n,str(type(mm)));expected=not E[n].get('open_expected',False);assert mm.IsClosed or not expected,n;native.append({'name':ob.Attributes.Name,'id':str(ob.Attributes.Id),'valid':mm.IsValid,'closed':mm.IsClosed,'closed_expected':expected})
  mat=F.Materials[ob.Attributes.MaterialIndex].Name
  if mat not in mats:mats.append(mat)
  off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
  for face in mm.Faces:
   ff.append((np.array(face[:3])+off).tolist());mi.append(mats.index(mat))
   if face[2]!=face[3]:ff.append((np.array([face[0],face[2],face[3]])+off).tolist());mi.append(mats.index(mat))
 dat={'vertices':np.array(vv),'faces':np.array(ff,np.int32),'uv':np.array(uv),'normals':np.array(nn),'material_ids':np.array(mi,np.int32)};fp=D/('FINAL_NATIVE_'+n+'.npz');np.savez_compressed(fp,**dat);actual_paths[n]=str(fp)
 author=np.load(E[n]['v20_native_cache_override']);saved=np.load(B/'02_Data'/I[n]['file']);ta=author['vertices'][author['faces']];tn=dat['vertices'][dat['faces']];tc=saved['vertices'][saved['faces']];assert ta.shape==tn.shape==tc.shape,n;da=float(abs(ta-tn).max());dc=float(abs(tc-tn).max());au=author['uv'][author['faces']];nu=dat['uv'][dat['faces']];cu=saved['uv'][saved['faces']];du=float(abs(au-nu).max());duc=float(abs(cu-nu).max());assert da<1e-9 and dc<1e-9 and du<2e-6 and duc<1e-9,(n,da,dc,du,duc);assert mats==I[n]['materials'],(n,mats,I[n]['materials'])
 rows.append({'node':n,'native_objects':native,'triangles':len(ff),'source_surface_coordinate_max_delta_m':da,'delivery_readback_surface_coordinate_max_delta_m':dc,'source_uv_max_delta_float32':du,'delivery_readback_uv_max_delta':duc,'materials':mats})
# Execute the independent cavity and seam sampler with only the three final-node paths replaced by fresh native readbacks.
src=(D/'seam_validate.py').read_text(encoding='utf8');src=src.replace("P=json.loads((D/'Seam_Correction_QA.json').read_text(encoding='utf8'));E={e['name']:e for e in Q['replace']};cache={};trcache={}","P=json.loads((D/'Seam_Correction_QA.json').read_text(encoding='utf8'));E={e['name']:e for e in Q['replace']};\nfor n,fp in fresh_native_paths.items():E[n]['v20_native_cache_override']=fp\ncache={};trcache={}")
src=src.replace("(D/'Seam_Independent_Validation.json').write_text", "(D/'Final_Native_Seam_Samples.json').write_text");env={'__file__':str(D/'seam_validate.py'),'fresh_native_paths':actual_paths};exec(compile(src,'<final_native_seam_samples>','exec'),env)
report=json.loads((D/'Final_Native_Seam_Samples.json').read_text(encoding='utf8'));assert report['status']=='PASS_LOCAL_SEAM_CORRECTION',report['status'];report.update(status='PASS_FINAL_FRESH_NATIVE_SEAM_QA',model=str(P),model_bytes=P.stat().st_size,readback='Fresh saved Rhino .3dm read, no author-only inference',three_node_parity=rows)
target=B/'06_Report/Final_Native_Seam_QA.json';target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');(D/'Final_Native_Seam_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(report['status'],report['maximum_all_boundary_z_gap_m'],max(r['source_surface_coordinate_max_delta_m'] for r in rows),flush=True)
