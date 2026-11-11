from v26_1_common import *
WHITE='M_Wall_Interior';CEILING='M_V24_31_White_Painted_Ceiling';GRAY='M_V24_31_Stair_Gray_Marble'
names=[n for n in I if n.startswith(('KZ_','BEAM_','SLAB_JOINED','FACADE_CONTINUOUS','PARTITIONS_JOINED','STAIR_F','STAIR_LANDING','V26_Stair_','V24_31_F'))or(n.startswith('HOUSE_V21_')and'GREY_WHITE'in n)]
names += ['HOUSE_V22_FRONT_BAY_TILE_FACES_Geometry','ROOF_MAIN_JOINED_Geometry','ROOF_EAVE_FASCIA_Geometry','UTILITY_FLAT_ROOF_WEST_Geometry']
names=sorted(set(names));pieces=[];proof={'beam_notches':[],'surface_extensions':[]}
for n in names:
 m=load(n)
 if n.startswith('V26_Stair_Landing_Bearing_Beam_'):
  fl=int(n[-1]);flight=f'STAIR_F{fl}_FLIGHT1_Geometry';a=arr(flight);t=a['v'][a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);tr=t[(no[:,2]>1e-5)&(t[:,:,0].mean(1)>5.20001)&(t[:,:,0].mean(1)<5.46)];z=float(tr[:,:,2].max());cut=cube([5.199999,8.54,z-.006],[5.31,9.83,z+.3]);before=m.volume();m-=cut;proof['beam_notches'].append({'name':n,'last_tread_height_m':z,'beam_cap_below_tread_m':.006,'removed_protrusion_m3':before-m.volume()})
 pieces.append(m)
print('HOUSE_UNION_INPUT',len(pieces),flush=True);body=union(pieces);print('HOUSE_UNION_BASE',body.num_tri(),body.volume(),flush=True)
# Extend only opaque, existing wall faces. Openings and glazed panels keep
# their original X/Z or Y/Z outlines; no plane is added across a window.
a=body.to_mesh64();v=np.array(a.vert_properties[:,:3]);f=np.array(a.tri_verts);t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(no,axis=1);no/=np.maximum(length[:,None],1e-30);c=t.mean(1)
targets=[('stair_rear',1,9.588,(no[:,1]<-.9999)&(c[:,1]>=9.599)&(c[:,1]<9.78)&(c[:,0]>3.69)&(c[:,0]<9.31)&(c[:,2]>-.45)&(c[:,2]<10.221)),('stair_front',1,7.512,(no[:,1]>.9999)&(c[:,1]>7.38)&(c[:,1]<7.501)&(c[:,0]>3.69)&(c[:,0]<9.31)&(c[:,2]>-.45)&(c[:,2]<10.221)),('stair_west',0,4.112,(no[:,0]>.9999)&(c[:,0]>4.0)&(c[:,0]<4.111)&(c[:,1]>7.19)&(c[:,1]<9.901)&(c[:,2]>-.45)),('terrace_wall',0,3.680,(no[:,0]<-.9999)&(c[:,0]>3.681)&(c[:,0]<3.805)&(c[:,1]>1.89)&(c[:,1]<9.901)&(c[:,2]>=7.049))]
for label,axis,plane,mask in targets:
 adds=[extrude_tri(tr,axis,plane)for tr in t[mask]];adds=[m for m in adds if m is not None]
 if adds:
  m=finish(union(adds),WHITE,label+' continuous plaster');body+=m;proof['surface_extensions'].append({'location':label,'axis':axis,'finished_plane_m':plane,'triangles_extended':int(mask.sum()),'added_skin_volume_m3':m.volume(),'aperture_outlines_retained':True})
 print('FLUSH_FACE',label,len(adds),flush=True)
tiny=[p for p in body.decompose()if p.volume()<.001];proof['legacy_detached_window_head_slivers_removed']=[{'bounds':list(p.bounding_box()),'volume_m3':p.volume()}for p in tiny];body=union([p for p in body.decompose()if p.volume()>=.001])
row,body=export('V26_1_House_Continuous_Opaque_Shell',body,'Boolean union of the actual structural envelope and finishes; no overlapping display cores; finite stair bearing retained')
# Explicit finish ownership on horizontal floor tops and stair risers prevents
# white beam/column faces appearing as stripes on an otherwise grey floor.
a=np.load(D/row['file']);v=a['v'];f=a['f'];mi=a['mi'].copy();uv=a['uv'];t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-30);c=t.mean(1);mats=row['materials']
for name in ['M_Floor',WHITE,CEILING,GRAY]:
 if name not in mats:mats.append(name)
for z in [-.4499999881,3.450024414,7.050000191]:mi[(no[:,2]>.999)&(abs(c[:,2]-z)<.0002)]=mats.index('M_Floor')
mi[(no[:,2]<-.7)&(c[:,2]>-.4)]=mats.index(CEILING)
for axis,z,axmin,axmax in [(1,9.588,3.7,9.3),(1,7.512,3.7,9.3),(0,4.112,7.2,9.9)]:
 dim=0 if axis==1 else 1;mask=(abs(c[:,axis]-z)<2e-5)&(c[:,dim]>axmin)&(c[:,dim]<axmax)&(abs(no[:,axis])>.999);mi[mask]=mats.index(WHITE)
np.savez_compressed(D/row['file'],v=v,f=f,mi=mi,uv=uv)
raw=[row];move=[]
for n in ['TERRACE_SIDE_CERAMIC_PANEL_GRID_Geometry','V24_32_F3_Terrace_Panel_Recessed_Grout','HOUSE_V21_F3_TERRACE_RECTANGULAR_TILE_FINISH_Geometry','HOUSE_V21_F3_TERRACE_TILE_GROUT_Geometry']:
 a=arr(n);vv=a['v'].copy();vv[:,0]-=.12;fn='MOVED_'+n+'.npz';np.savez_compressed(D/fn,v=vv,f=a['f'],mi=a['mi'],uv=a['uv']);raw.append({'name':n,'file':fn,'materials':I[n]['materials'],'reason':'Continuous ceramic finish moved in front of the restored column and wall face; retains tile joints, photo-derived material and apertures'});move.append(n)
out={'objects':raw,'archive':names,'proof':proof,'tile_finish_repositioned':move};(D/'Prepared_House.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('HOUSE_PREPARED',len(names),len(f),flush=True)
