import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','libs']]
import numpy as np,rhino3dm as rh
O=Path(__file__).parent;scene=json.loads(Path(r'E:\jz\JIA\Rebuild_V5\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'));C=scene['coordinate'];th=math.radians(C['rotation_deg']);R=np.array([[math.cos(th),-math.sin(th),0],[math.sin(th),math.cos(th),0],[0,0,1]]);origin=np.array(C['origin']);T=np.eye(4);T[:3,:3]=R;T[:3,3]=origin;Ti=np.linalg.inv(T)
refp=Path(r'E:\jz\JIA\Rebuild_V5\04_ContextCapture\Production_1QK_Local_REFERENCE.3dm');model=rh.File3dm.Read(str(refp));report={'coordinate_record':C,'local_to_enu_4x4':T.tolist(),'enu_to_local_4x4':Ti.tolist(),'row_vector_formula':'local = (enu - origin) @ R; enu = local @ R.T + origin','old_reference_path':str(refp),'old_reference_sha256':hashlib.sha256(refp.read_bytes()).hexdigest(),'native_reference_unit':str(model.Settings.ModelUnitSystem),'reference_mesh_count':len(model.Objects),'reference_user_strings':{},'tiles':[]}
for key in ['Coordinate_srs','Coordinate_origin','Coordinate_rotation_deg','Coordinate_local_to_survey','Coordinate_confidence','Coordinate_vertical_datum']:
 report['reference_user_strings'][key]=model.Strings[key]
for ob in model.Objects:
 mesh=ob.Geometry;source=Path(ob.Attributes.GetUserString('Source'));verts=[];uv=[];ids=[];lookup={};faces=[]
 for line in source.open(encoding='utf-8'):
  if line.startswith('v '):verts.append([float(q) for q in line.split()[1:4]])
  elif line.startswith('vt '):uv.append([float(q) for q in line.split()[1:3]])
  elif line.startswith('f '):
   face=[]
   for tok in line.split()[1:]:
    vi,ti=(int(q)-1 for q in tok.split('/')[:2]);key=(vi,ti)
    if key not in lookup:lookup[key]=len(lookup);ids.append(key)
    face.append(lookup[key])
   faces.append(face)
 raw=np.array(verts);local=(raw-origin)@R;expected=np.array([local[vi] for vi,ti in ids]);actual=np.array([[v.X,v.Y,v.Z] for v in mesh.Vertices]);tex=np.array([[v.X,v.Y] for v in mesh.TextureCoordinates]);expected_uv=np.array([uv[ti] for vi,ti in ids]);same_shape=expected.shape==actual.shape
 geometry_difference=float(np.max(np.abs(expected-actual))) if same_shape else None;uv_difference=float(np.max(np.abs(expected_uv-tex))) if expected_uv.shape==tex.shape else None
 actual_faces=[list(f[:3])+([f[3]] if f[3]!=f[2] else []) for f in mesh.Faces];faces_match=faces==actual_faces
 item={'reference_object':ob.Attributes.Name,'raw_obj_source':str(source),'raw_vertex_count':len(raw),'uv_seam_expanded_vertex_count':len(actual),'face_count':len(faces),'raw_survey_bounds_m':[raw.min(axis=0).tolist(),raw.max(axis=0).tolist()],'reference_local_bounds_m':[actual.min(axis=0).tolist(),actual.max(axis=0).tolist()],'source_to_reference_transform_max_component_error_m':geometry_difference,'max_uv_error':uv_difference,'face_corner_indices_match_after_documented_uv_split':faces_match,'alignment_verified':same_shape and geometry_difference<1e-5 and faces_match,'source_obj_sha256':hashlib.sha256(source.read_bytes()).hexdigest()};report['tiles'].append(item)
 report['alignment_method']='Fixed documented coordinate transform, no ICP fitted or source geometry changed.'
 print(ob.Attributes.Name,item['alignment_verified'],geometry_difference,uv_difference)
report['reference_transform_verified']=all(r['alignment_verified'] for r in report['tiles']);(O/'Existing_Alignment_Evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('Verified',report['reference_transform_verified'])
