from v26_2_common import *
import v26_2_common as C
D=W/'v26_11';C.D=D;FD=W/'v26_10/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
def get(n):
 r=J[n];a=np.load(FD/r['file']);return r,a,tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],n)
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';r,a,wall=get(n);_,_,roof=get('SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry');ys=[-16.479,-15.23];tops=[]
for y in ys:
 hs=roof.ray_cast([13.48,y,2.0],[13.48,y,4.0]);assert hs,(y,'No actual storage roof above closure');tops.append(min(h.position[2]for h in hs)+.004)
t=a['v'][a['f']];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-30);point=np.array([13.204999923706055,-15.1,3.2]);candidates=np.flatnonzero((abs(t[:,:,0].mean(1)-point[0])<.00002)&(nn[:,0]<-.9));pick=None
for i in candidates:
 A,B=t[i,1]-t[i,0],t[i,2]-t[i,0];q=point-t[i,0];ab=A@B;aa=A@A;bb=B@B;det=aa*bb-ab*ab
 if det<1e-15:continue
 u=(bb*(A@q)-ab*(B@q))/det;v=(aa*(B@q)-ab*(A@q))/det
 if min(u,v)>=-.00001 and u+v<=1.00001:pick=int(i);break
assert pick is not None,'No matching existing west-wall brick face';mat=r['materials'][int(a['mi'][pick])];print('MATCH_EXISTING_BRICK',mat,pick,flush=True)
# A true trapezoidal masonry extension replaces the exposed decorative
# eave board and the unsupported low white gable skin. Its top follows
# the actual roof underside, with4mm concealed seating.
profile=[(ys[0],2.80),(ys[1],2.80),(ys[1],tops[1]),(ys[0],tops[0])];cap=section(profile,.342).transform([[0,0,1,13.205],[1,0,0,0],[0,1,0,0]])
ca=cap.to_mesh64();cv=np.array(ca.vert_properties[:,:3]);cf=np.array(ca.tri_verts);cu=uv_project(cv,cf);cn=np.cross(cv[cf][:,1]-cv[cf][:,0],cv[cf][:,2]-cv[cf][:,0]);side=abs(cn[:,0])>.00001
# Continue the original outside wall's UV projection and brick-course
# phase onto both new side faces, rather than restarting its pattern.
cu[side]=bary_uv(cv[cf[side]],np.repeat(t[pick][None],side.sum(),axis=0),np.repeat(a['uv'][pick][None],side.sum(),axis=0));cap=tracked(cv,cf,[mat],np.zeros(len(cf),int),cu,'Photo-marked trapezoid masonry eave closure with matching brick courses');new=wall+cap;row,new=export(n,new,'Bond trapezoidal brick eave closure to existing west gable; top fits roof; preserve original timber and roof meshes')
wn='V24_17_Storage_West_Inner_Gable_Limewash';wr,wa,white=get(wn);mask=cube([13.10,-16.60,2.0],[13.65,-15.23999,5.0]);white-=finish(mask,mat,'Remove unsupported low white gable skin under the new trapezoidal brick closure');wrow,white=export(wn,white,'Remove only the unsupported front overhang of the limewash skin, leaving the interior wall finish')
proof={'y_span_m':ys,'bottom_z_m':2.80,'roof_top_z_m':tops,'x_span_m':[13.205,13.547],'source_roof_sample_x_m':13.48,'hidden_roof_seating_m':.004,'matching_existing_brick_material':mat,'matching_existing_uv_source_triangle':pick,'timber_and_roof_original_meshes_unchanged':True,'white_skin_removal_bounds_m':[[13.10,-16.60,2.0],[13.65,-15.23999,5.0]],'decorative_eave_board_replaced':'V24_23_Storage_Outer_Gable_Wood_Edge'}
(D/'Prepared_Storage.json').write_text(json.dumps({'objects':[row,wrow],'archive':['V24_23_Storage_Outer_Gable_Wood_Edge'],'proof':proof},ensure_ascii=False,indent=2),'utf8');print('STORAGE_READY',profile,len(new.decompose()),flush=True)
