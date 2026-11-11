"""Photo-fitted front chamfers, continuous low plinth and longer lower carving."""
from v26_2_common import *
import v26_2_common as C
from math import sqrt
D=W/'v26_13';C.D=D;J=json.loads((D/'Probe.json').read_text('utf8'));cur={r['name']:r for r in J['V26_12']['objects']};rows=[];panels=[]
CORE='M_V26_13_Gate_Gray_Stone_Core';TRIM='M_V26_13_Gate_Gray_Stone_Edge';ART='M_V26_13_Gate_Gray_Stone_Carving';STEP='M_V26_13_Gate_Gray_Stone_Sill'
PN='V26_10_Inner_Gate_Rectangular_Stone_Piers';PL='SITE_V21_GATE_REFERENCE_LAYER_01_Geometry'
def native(name):
 r=cur[name];a=np.load(D/r['file']);return tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],name)
def plan(x0,x1,y0,y1,c):return[(x0+c,y0),(x1-c,y0),(x1,y0+c),(x1,y1),(x0,y1),(x0,y0+c)]
def mapped(m,a,b):
 a=np.asarray(a);b=np.asarray(b);t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]]);return m.transform([[t[0],n[0],0,a[0]],[t[1],n[1],0,a[1]],[0,0,1,0]])
def ring(w,z0,z1,depth0,depth1,border):return cube([0,depth0,z0],[w,depth1,z1])-cube([border,depth0-.001,z0+border],[w-border,depth1+.001,z1-border])
def foot(x0,x1):
 y0,y1=-11.87,-11.294;p=.020;c=.09;lo=plan(x0-p,x1+p,y0-p,y1+p,c+p*(2-sqrt(2)));hi=plan(x0,x1,y0,y1,c);v=np.array([[x,y,-.510]for x,y in lo]+[[x,y,-.475]for x,y in hi]);f=[];n=len(lo)
 for k in range(1,n-1):f.extend([[0,k+1,k],[n,n+k,n+k+1]])
 for k in range(n):j=(k+1)%n;f.extend([[k,j,n+j],[k,n+j,n+k]])
 return solid(v,np.asarray(f),'Tapered20mm stone plinth')
source_rows=json.loads((D/'Input_Reliefs.json').read_text('utf8'));cutters=[]
for r in source_rows:
 if 'Header'in r['source_object']:continue
 a=np.load(D/r['file']);v=a['v'].copy();old_n=np.asarray(r['inside']);old_origin=np.asarray(r['origin']);old_t=np.cross(old_n,[0,0,1.]);u=(v-old_origin)@old_t;depth=(v-old_origin)@old_n
 pi=1 if '_P1_'in r['source_object']else 2;x0,x1=[(4.9333333969,5.4571428571),(7.7428571429,8.2666664124)][pi-1];face='front'if'_front'in r['source_object']else'left'if'_left'in r['source_object']else'right'
 if face=='front':aa=np.array([(x0+x1)/2-.1409,-11.87]);bb=np.array([(x0+x1)/2+.1409,-11.87])
 else:
  corner=np.array([x0,-11.78])if face=='left'else np.array([x1-.09,-11.87]);t=np.array([1.,-1.])/sqrt(2)if face=='left'else np.array([1.,1.])/sqrt(2);aa=corner+t*.029;bb=corner+t*(.09*sqrt(2)-.029)
 t=(bb-aa)/np.linalg.norm(bb-aa);n=np.array([-t[1],t[0]]);uu=(u-u.min())/np.ptp(u)*np.linalg.norm(bb-aa);v[:,:2]=aa+uu[:,None]*t+depth[:,None]*n
 z_before=[float(v[:,2].min()),float(v[:,2].max())];lower=r['source_object'].endswith('_1')and 'Upper'not in r['source_object']
 if lower:v[:,2]=-.433+(v[:,2]-z_before[0])/(z_before[1]-z_before[0])*(.553+.433)
 name=r['name'].replace('V26_12_Restored_','V26_13_Photo_Fit_');fn=name+'.npz';np.savez_compressed(D/fn,v=v,f=a['f'],mi=np.zeros(len(a['f']),int),uv=a['uv']);row={'name':name,'source':r['name'],'file':fn,'materials':[ART],'non_collision_detail':True,'smooth':True,'vertex_correspondence':True};rows.append(row)
 width=np.linalg.norm(bb-aa);z0,z1=float(v[:,2].min()),float(v[:,2].max());cutters.append(mapped(cube([0,-.001,z0],[width,.014,z1]),aa,bb));panels.append({'name':name,'source':r['name'],'pier':pi,'face':face,'base_segment_m':[aa.tolist(),bb.tolist()],'inside':[*n,0.],'origin':[*aa,0.],'source_z_m':z_before,'target_z_m':[z0,z1],'lower_extended':lower,'front_vertex_ids':r['original_front_vertex_ids'],'uv_and_height_differences_preserved':True,'side_chamfer_angle_deg':45 if face!='front'else 0})
# Original sculpted waist and its fitted faceted collar remain at the photo's
# lower-third station. Only the broad rectangular replacement is discarded.
waist=finish(native('SITE_V21_GATE_REFERENCE_LAYER_03_Geometry')^cube([4.7,-12.1,.60],[8.5,-11.15,.75]),TRIM,'Original faceted82mm waist collar')
parts=[]
for pi,(x0,x1)in enumerate([(4.9333333969,5.4571428571),(7.7428571429,8.2666664124)],1):
 core=finish(section(plan(x0,x1,-11.87,-11.294,.09),3.595).translate([0,0,-.485]),CORE,'Photo-fitted90mm front chamfers; original rear bearing preserved')
 fp=foot(x0,x1)
 if pi==1:fp-=cube([x1,-11.75,-.52],[x1+.05,-11.24,-.46])
 else:fp-=cube([x0-.05,-11.75,-.52],[x0,-11.24,-.46])
 parts.extend([core,finish(fp,TRIM,'Low35mm tapered plinth;20mm maximum overhang')])
 for a,b,margin in[([x0+.09,-11.87],[x1-.09,-11.87],.010),([x0,-11.78],[x0+.09,-11.87],.008),([x1-.09,-11.87],[x1,-11.78],.008)]:
  a=np.asarray(a);b=np.asarray(b);t=(b-a)/np.linalg.norm(b-a);start=a+t*margin;width=np.linalg.norm(b-a)-2*margin
  for z0,z1 in[(-.455,.575),(.778,2.312),(2.395,3.025)]:
   fr=ring(width,z0,z1,-.014,.012,.016)+ring(width-.012,z0+.006,z1-.006,-.022,-.010,.006).translate([.006,0,0]);parts.append(finish(mapped(fr,start,start+t*width),TRIM,'Two shallow continuous stone moulding beads'))
body=union(parts)+waist
body-=finish(union(cutters),CORE,'Fourteen-millimetre actual carving recesses')
rr,m=export(PN,body.simplify(.000003),'Photo-fitted45degree carved corner faces, original faceted waist and reduced plinth');rows.insert(0,rr)
old_step=native(PL);bounds=[[4.9033333969,-11.96,-.90],[8.2966664124,-11.18,-.50]]
buried=old_step^cube(bounds[0],[bounds[1][0],bounds[1][1],-.59999]);step=finish(cube([bounds[0][0],bounds[0][1],-.60],bounds[1]),STEP,'Continuous100mm one-step sill with limited90mm front projection')+finish(buried,STEP,'Existing buried foundation retained within the reduced footprint')
rr,m=export(PL,step,'Remove the oversized foreground apron and outer foot pads; retain one continuous entrance step');rows.insert(1,rr)
proof={'reference_images':['D:/Desktop/屏幕截图 2026-10-25 003420.jpg','D:/Desktop/屏幕截图 2026-10-25 003523.jpg'],'dimensions_are_photo_and_original_model_fit_not_surveyed':True,'chamfer_m':.09,'previous_chamfer_m':.012,'waist_z_m':[.633,.715],'previous_waist_z_m':[.608,.738],'plinth_z_m':[-.510,-.475],'plinth_overhang_m':.020,'sill_bounds_m':bounds,'previous_sill_bounds_m':cur[PL]['bounds'],'sill_top_m':-.5,'court_m':-.6,'sill_front_projection_from_pier_m':.09,'lower_panel_extension_m':.15,'panels':panels,'restored_waist_source':'V24_Gate_Waist_Carving_Retained','header_geometry_preserved':True}
(D/'Prepared.json').write_text(json.dumps({'objects':rows,'proof':proof},ensure_ascii=False,indent=2),'utf8');print('PREPARED',len(rows),len(panels),flush=True)
