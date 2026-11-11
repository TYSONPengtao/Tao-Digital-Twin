exec((__import__('pathlib').Path(__file__).parent/'probe.py').read_text('utf8').split('for n in [')[0])
a=np.load(D/I['BAY_WINDOW_F1_L_0_Geometry']['file']);G=solid(a['v'],a['f'],'bay assembly');Glass=solid(a['v'],a['f'][a['mi']==1],'bay glass');n=np.array([0.8111365302967483,0.5848568450639461]);limit=1.1723606549172076
poly=[[(limit-n[1]*y)/n[0],y] for y in [.7,2.3]]+[[1.,2.3],[1.,.7]];cut=section(poly,3.5).translate([0,0,-.7])
rows=[]
for nm in [x for x in I if x.startswith('SITE_COURTYARD_WEST_TILE_WALL_')]+['V26_1_Courtyard_West_Wall_Single_Surface']:
 ar=np.load(D/I[nm]['file']);m=solid(ar['v'],ar['f'],nm);inter=m^G;gl=m^Glass;removed=m^cut
 if not (inter.volume()>1e-12 or removed.volume()>1e-12):continue
 iv=np.array(inter.to_mesh64().vert_properties)[:,:3];r={'name':nm,'old_bay_assembly_overlap_m3':inter.volume(),'old_glass_only_overlap_m3':gl.volume(),'overlap_bounds':[] if not len(iv) else [iv.min(0).tolist(),iv.max(0).tolist()],'removed_volume_m3':removed.volume(),'new_assembly_overlap_m3':((m-cut)^G).volume()};rows.append(r);print(r,flush=True)
(Path(__file__).parent/'full_height_cut_report.json').write_text(json.dumps({'normal':n.tolist(),'c':limit,'xy_polygon':poly,'z_range':[-.7,2.8],'rows':rows},indent=2),'utf8')
