from pathlib import Path
W=Path(__file__).parent;s=(W/'refine_scene_v2.py').read_text(encoding='utf-8')
s=s.replace("OUT=Path(r'E:\\jz\\JIA\\Rebuild_V2')","OUT=Path(r'E:\\jz\\JIA\\Rebuild_V3')")
s=s.replace("(423,936),(496,1007)","(442,873),(496,1007)")
s=s.replace(".difference(rect(4,-17.6,10,-12))","")
s=s.replace("terrain('SITE_MAIN_COURTYARD_PAVING',maincourt.difference(footprints),'M_Site_Paving',.9,flat=-.45)","entry_A=np.array([-14.65,-8.37]);entry_B=np.array([-12.88,-12.7275]);entry_vec=entry_B-entry_A;entry_line=LineString([entry_A,entry_B])\ndef gate_datum_v3(x,y):\n t=float(np.clip(np.dot(np.array([x,y])-entry_A,entry_vec)/np.dot(entry_vec,entry_vec),0,1));return -.85-.35*t\ndef courtyard_datum_v3(x,y):\n if x>=0:return -.45\n t=min(1,Point(x,y).distance(entry_line)/13.0);return gate_datum_v3(x,y)*(1-t)-.45*t\nterrain('SITE_MAIN_COURTYARD_PAVING',maincourt.difference(footprints),'M_Site_Paving',.9,height_function=courtyard_datum_v3)")
s=s.replace("terrain('SITE_CURVED_PUBLIC_ROAD',road,'M_Asphalt',1.3)","entry_approach_v3=Polygon([[-16.2,-8.7],[-14.65,-8.37],[-12.88,-12.7275],[-14.3,-13.5],[-17.0,-11.4]])\nterrain('SITE_CURVED_PUBLIC_ROAD',road.difference(entry_approach_v3),'M_Asphalt',1.3)")
s=s.replace("terrain('SITE_CONTEXT_TERRAIN',context,'M_Grass',2.0)","terrain('SITE_CONTEXT_TERRAIN',context.difference(entry_approach_v3),'M_Grass',2.0)")
s=s.replace("def terrain(name,poly,mat,step=1.2,flat=None):","def terrain(name,poly,mat,step=1.2,flat=None,height_function=None):")
s=s.replace("float(flat if flat is not None else gz(*key))","float(height_function(*key) if height_function is not None else flat if flat is not None else gz(*key))")
s=s.replace("zz=np.array([[rawz","zgrid=np.array([[rawz").replace("zz=gaussian_filter(zz,.85)","zgrid=gaussian_filter(zgrid,.85)").replace("zz[iy","zgrid[iy")
s=s.replace("paintheights=[min(.9,(tt-zz)*.6) for tt,zz in zip(ztop,zbase)]","paintheights=[(tt-zz)*.57 if stone else min(.65,(tt-zz)*.28) for tt,zz in zip(ztop,zbase)]")
s=s.replace("if height is None:ztop=gaussian_filter1d(np.array(ztop),1.4).tolist()","if height is None:ztop=gaussian_filter1d(np.array(ztop),1.4).tolist()\n for k,(xx,yy) in enumerate(pts):\n  if name.startswith('SITE_PERIMETER') and 3.1<xx<10.96 and yy<-16.0:ztop[k]=2.15")
s=s.replace("caps.append(part({'type':'polyhedron','vertices':va+vb,'faces':[[2,1,0],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]]},'M_Roof'))","if not (name.startswith('SITE_PERIMETER') and 3.1<(a[0]+b[0])/2<10.95 and (a[1]+b[1])/2<-16.0):caps.append(part({'type':'polyhedron','vertices':va+vb,'faces':[[2,1,0],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]]},'M_Roof'))")
start=s.index('perimeter_line=linemerge(');end=s.index('# Buildings are clean',start)
s=s[:start]+"perimeter_line=LineString(outline+[outline[0]]).difference(LineString([[-14.635,-8.3725],[-12.88,-12.7275]]).buffer(.30,cap_style=3))\nfor j,line in enumerate([perimeter_line] if perimeter_line.geom_type=='LineString' else list(perimeter_line.geoms)):\n wallchain('SITE_PERIMETER_JOINED_RETAINING_WALL_'+str(j),list(line.coords))\n"+s[end:]
start=s.index('# Inner red gate and outer tiled portal');end=s.index('# Observable vegetation',start)
s=s[:start]+s[end:]
# Place new evidence-backed site before the camera list, then add detailed review cameras afterwards.
marker="S['name']='Production_1QK_Rebuild_V2'"
s=s.replace(marker,(W/'site_detail_v3.inc.py').read_text(encoding='utf-8')+"\nS['name']='Production_1QK_Rebuild_V3'")
s=s.replace("S['status']='V2_BUILDING_AND_SITE_RECONSTRUCTION; DESIGN_DIMENSIONS_AND_REALITY_TRACED_SITE; NOT_SURVEY_CERTIFIED'","S['status']='V3_PHOTO_REFERENCED_ARCHITECTURE_AND_SITE; NOT_SURVEY_CERTIFIED'")
s=s.replace("[(0,3.50),(3.9,3.20)]","[(0,2.65),(3.9,2.90)]")
s=s.replace("top=z+H+.27;xx=np.linspace(3.9,9.1,49);under=[z+H+.23*math.sin((x-3.9)/5.2*math.pi) for x in xx]","top=3.77 if z==0 else 7.37;xx=np.linspace(3.9,9.1,49);under=[z+H+(.65 if z==0 else .4)*math.sin((x-3.9)/5.2*math.pi) for x in xx]")
s=s.replace("CCM entrance arch; PDF level datum, arch rise visually estimated","DJI_0862, source CCM underside samples; PDF floor levels retained, deep curved porch beam")
s=s.replace("video79s/377s flutes and mouldings; finish dimensions estimated","DJI_0862 + video79s/377s; visible fluted shaft and mouldings, finish dimensions estimated")
s=s.replace("print('V2'","print('V3'")
(W/'refine_scene_v3.py').write_text(s,encoding='utf-8')
print('V3 generator prepared')
