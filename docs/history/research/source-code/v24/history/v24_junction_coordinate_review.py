import bpy,json,numpy as np
from pathlib import Path
P=Path('E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24.blend');bpy.ops.wm.open_mainfile(filepath=str(P));out=Path(r'C:/Users/PENG/Documents/Codex/2026-10-07/files-pasted-by-the-user-rhino/work/v24_junction_reference_review');out.mkdir(exist_ok=True);rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH' or not any(s in ob.name for s in ['KITCHEN','GATE_REFERENCE_LAYER_02','GATE_REFERENCE_LAYER_09','GATE_REFERENCE_CLOSED_SOFFIT','GATE_REFERENCE_LAYER_14','V24_Sculpted_Wings','FLUSH_GABLE']):continue
 a=np.empty(len(ob.data.vertices)*3,np.float64);ob.data.vertices.foreach_get('co',a);v=a.reshape(-1,3);m=np.array(ob.matrix_world);v=v@m[:3,:3].T+m[:3,3];lo=v.min(0);hi=v.max(0)
 if hi[0]<8.0 or lo[0]>13.7 or hi[1]<-12.4 or lo[1]>-11.25 or hi[2]<2.4:continue
 mask=(v[:,0]>=8.0)&(v[:,0]<=13.7)&(v[:,1]>=-12.3)&(v[:,1]<=-11.65)&(v[:,2]>=2.3);q=v[mask]
 row={'object':ob.name,'materials':[x.name if x else None for x in ob.data.materials],'bbox_local_m':[lo.tolist(),hi.tolist()],'near_junction_vertex_count':int(len(q))}
 if len(q):row.update(near_junction_bbox=[q.min(0).tolist(),q.max(0).tolist()],front_y_levels=np.unique(np.round(q[:,1],5)).tolist()[:24])
 if 'MASONRY'in ob.name or'FLUSH_GABLE'in ob.name:
  f=v[(abs(v[:,1]+11.87)<.001)&(v[:,0]>=8.0)&(v[:,0]<=13.7)];xs=np.unique(np.round(f[:,0],4));row['front_y_minus11_87_top_profile']=[[float(x),float(f[abs(f[:,0]-x)<.00011,2].max())]for x in xs]
 rows.append(row)
(out/'Coordinate_Inventory.json').write_text(json.dumps({'model':str(P),'coordinates':'LOCAL metres','objects':rows},ensure_ascii=False,indent=2),encoding='utf8')
print('JUNCTION_READONLY_COORDINATES',len(rows),flush=True)
for r in rows:
 if any(s in r['object']for s in ['MASONRY','FLUSH','FASCIA','LAYER_02','LAYER_09']):print(r['object'],r['bbox_local_m'],r.get('front_y_minus11_87_top_profile'),flush=True)
