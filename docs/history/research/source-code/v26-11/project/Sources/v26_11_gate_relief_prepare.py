"""User-requested photo -> rectified grayscale -> signed, baked stone relief."""
from v26_2_common import *
import v26_2_common as C
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import gaussian_filter
from v24_relief_blender import _panel_mesh_arrays,_sample
import hashlib
D=W/'v26_11';C.D=D;H=D/'Heightmaps';H.mkdir(exist_ok=True);FD=W/'v26_10/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};SRC=Path('D:/Desktop/609fc65b-b63d-4278-bd18-72c45c32925f.png');im=Image.open(SRC).convert('RGB');assert im.size==(1302,1208)
# Quads are TL,TR,BR,BL in the unchanged1302x1208 reference. Borders and
# architecture outside each carved field are excluded before rectification.
Q={
 'P1_front_upper':[[399,355],[446,369],[447,424],[399,415]],
 'P1_front_middle':[[398,442],[449,452],[449,748],[398,750]],
 'P1_front_lower':[[397,804],[449,802],[449,1033],[396,1045]],
 'P1_side_upper':[[348,345],[376,350],[376,411],[346,407]],
 'P1_side_middle':[[346,435],[376,438],[375,750],[343,750]],
 'P1_side_lower':[[341,803],[375,804],[374,1042],[335,1034]],
 'P2_front_upper':[[856,376],[919,355],[923,419],[857,433]],
 'P2_front_middle':[[857,448],[926,437],[956,750],[863,751]],
 'P2_front_lower':[[866,804],[960,803],[983,1034],[869,1032]],
 'P2_side_upper':[[941,350],[961,357],[966,420],[943,416]],
 'P2_side_middle':[[944,442],[971,445],[1000,751],[964,750]],
 'P2_side_lower':[[968,806],[1004,805],[1027,1038],[990,1036]],
 'Header_1':[[470,362],[585,365],[585,393],[470,391]],
 'Header_2':[[603,366],[703,366],[703,393],[603,393]],
 'Header_3':[[719,364],[827,360],[828,391],[719,393]],
}
CW,CH=256,768;aw,ah=CW*4,CH*4;atlas=np.full((ah,aw),32768,np.uint16);layout={};crops=[]
def rectify(quad):
 dst=[[0,0],[CW-1,0],[CW-1,CH-1],[0,CH-1]];A=[];B=[]
 for (x,y),(u,v)in zip(dst,quad):A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
 coeff=np.linalg.solve(np.asarray(A,float),np.asarray(B,float));return im.transform((CW,CH),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
for k,(name,quad)in enumerate(Q.items()):
 crop=rectify(quad);crop.save(H/(name+'_Rectified.png'));rgb=np.asarray(crop,float)/255.;gray=rgb@np.array([.2126,.7152,.0722]);yy,xx=np.mgrid[-1:1:complex(CH),-1:1:complex(CW)];plane=np.c_[xx.ravel(),yy.ravel(),np.ones(CW*CH)];fit=plane@np.linalg.lstsq(plane,gray.ravel(),rcond=None)[0];flat=gray-fit.reshape(gray.shape)+np.median(gray);flat=gaussian_filter(flat,.55);low,high=np.quantile(flat,[.025,.975]);g=np.clip((flat-low)/max(high-low,.01),0,1);g=np.clip(.5+(g-.5)*.94,0,1);gx=k%4;gy=k//4;atlas[gy*CH:(gy+1)*CH,gx*CW:(gx+1)*CW]=np.rint(g*65535).astype(np.uint16);layout[name]=[gx/4,1-(gy+1)/4,(gx+1)/4,1-gy/4];crops.append({'name':name,'source_quad_pixels':quad,'uv_rect':layout[name],'gray_percentiles':[float(low),float(high)],'illumination_removed':'Best-fit linear brightness plane only; no invented motif or AI reconstruction'})
atlas_path=H/'Gate_Reference_Gray_Height_Atlas.png';Image.fromarray(atlas).save(atlas_path);gray=np.flipud(atlas.astype(float)/65535.)
preview=Image.new('RGB',(1050,1580),'#e8edf0');draw=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18);draw.text((20,12),'用户参考图 → 透视校正 → 灰度高度图（亮部隆起，暗部下凹）',font=font,fill='#243944')
for k,row in enumerate(crops):
 x=(k%5)*210;y=60+(k//5)*500;crop=Image.open(H/(row['name']+'_Rectified.png'));crop.thumbnail((92,430));preview.paste(crop,(x+8,y+30));gx=k%4;gy=k//4;g=Image.fromarray((atlas[gy*CH:(gy+1)*CH,gx*CW:(gx+1)*CW]/257).astype(np.uint8)).convert('RGB');g.thumbnail((92,430));preview.paste(g,(x+106,y+30));draw.text((x+8,y),row['name'],font=font,fill='#314d5c')
preview.save(H/'Reference_To_Gray_Overview.png')
def source(n):
 r=J[n];a=np.load(FD/r['file']);return tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],n)
PN='V26_10_Inner_Gate_Rectangular_Stone_Piers';HN='SITE_V21_GATE_REFERENCE_LAYER_05_Geometry';pier=source(PN);head=source(HN);rows=[];panels=[];MAT='M_V26_11_Reference_Gray_Carved_Stone'
def panel(name,key,a,b,z0,z1,nx,nz,amp):
 global pier,head
 tangent=(np.array(b)-a);tangent=tangent/np.linalg.norm(tangent);inside=np.array([-tangent[1],tangent[0]]);outside=-inside;w=np.linalg.norm(np.array(b)-a);rect=layout[key];vv,polys,uv,stats=_panel_mesh_arrays(gray,rect,a,b,z0,z1,nx,nz,0.,front=-.003,back=.016);v=np.asarray(vv);f=np.array([[q[0],q[j],q[j+1]]for q in polys for j in range(1,len(q)-1)],np.int32);uv=np.asarray(uv)[f];g,_=_sample(gray,rect,nx,nz);fx=np.minimum(np.arange(nx+1),np.arange(nx,-1,-1))/4.;fz=np.minimum(np.arange(nz+1),np.arange(nz,-1,-1))/4.;fade=np.sin(np.minimum(1,np.minimum(fz[:,None],fx[None,:]))*np.pi/2)**2;disp=amp*(2*g-1)*fade;count=(nx+1)*(nz+1);v[:count,:2]+=disp.ravel()[:,None]*outside
 # Backing remains seated2mm into the core, beyond the14mm recess.
 cutter=cube([0,-.001,z0],[w,.014,z1]).transform([[tangent[0],inside[0],0,a[0]],[tangent[1],inside[1],0,a[1]],[0,0,1,0]])
 if key.startswith('Header'):head-=finish(cutter,'M_V21_GATE_REF_03','A real recess behind the signed header relief')
 else:pier-=finish(cutter,'M_V21_GATE_REF_02','A real recess behind raised and incised photo-derived stone carving')
 rr,m=export(name,tracked(v,f,[MAT],np.zeros(len(f),int),uv,name),'Perspective-corrected source photograph grayscale drives both raised and recessed closed stone geometry',new=True,smooth_stone=True,non_collision_detail=True);rows.append(rr);heights=.003+disp;panels.append({'name':name,'source_cell':key,'base_segment_m':[a,b],'z_m':[z0,z1],'outward_height_min_m':float(heights.min()),'outward_height_max_m':float(heights.max()),'geometry_faces':len(f),'signed_raised_and_recessed':bool(heights.min()<0 and heights.max()>0),'core_recess_depth_m':.014,'seated_back_depth_m':.016,'source_texture':str(atlas_path),'uv_rect':rect})
for i,(x0,x1)in enumerate([(4.9333333969,5.4571428571),(7.7428571429,8.2666664124)],1):
 for face,a,b,nx in [('front',[(x0+x1)/2-.1409,-11.87],[(x0+x1)/2+.1409,-11.87],64),('left',[x0,-11.6275],[x0,-11.7125],28),('right',[x1,-11.7125],[x1,-11.6275],28)]:
  for band,z0,z1,nz,amp in[('lower',-.283,.553,180,.009),('middle',.8,2.29,300,.008),('upper',2.42,3.0,128,.006)]:panel(f'V26_11_Gate_Gray_Relief_P{i}_{face}_{band}',f'P{i}_{"front"if face=="front"else"side"}_{band}',a,b,z0,z1,nx,nz,amp if face=='front'else amp*.7)
for i,(x0,x1)in enumerate([(5.440000057,6.119999885),(6.260000229,6.940000057),(7.079999924,7.760000229)],1):panel(f'V26_11_Gate_Gray_Relief_Header_{i}',f'Header_{i}',[x0,-11.80300045],[x1,-11.80300045],2.887999916,3.045999908,180,44,.006)
for n,m in[(PN,pier),(HN,head)]:
 rr,m=export(n,m,'Fourteen-millimetre seated recesses expose the real negative relief, while original frames, waist and bases remain');rows.append(rr)
oldpic=[f'V24_Gate_Reference_Relief_Header_{i}'for i in[1,2,3]]+[f'V24_Gate_Reference_Relief_P{i}_{face}_{band}'for i in[1,2]for face in['front','left_bevel','right_bevel']for band in[1,2]]+[f'V26_10_Gate_Upper_Relief_P{i}_{face}'for i in[1,2]for face in['front','left','right']]
meta={'source_image':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'height_atlas':str(atlas_path),'height_atlas_sha256':hashlib.sha256(atlas_path.read_bytes()).hexdigest(),'bit_depth':16,'crops':crops,'panels':panels,'height_is_inferred_from_reference_luminance_not_measured_depth':True,'unseen_column_side_faces':'Repeat the corresponding visible narrow side-face motif; the source photograph does not show both side faces','old_pictures_retained_in_archived_editable_objects':True,'new_modifiers':0}
(H/'Heightmap_Layout_And_Provenance.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),'utf8');(D/'Prepared_Gate_Relief.json').write_text(json.dumps({'objects':rows,'archive':oldpic,'proof':meta},ensure_ascii=False,indent=2),'utf8');print('PHOTO_RELIEF_READY',len(panels),sum(p['geometry_faces']for p in panels),len(oldpic),flush=True)
