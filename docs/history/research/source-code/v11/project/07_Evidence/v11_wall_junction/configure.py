from pathlib import Path
O=Path(__file__).parent
src=O.parent/'v10_courtyard_wall'/'mutation.py'
s=src.read_text(encoding='utf8')
s=s.replace("Rebuild_V9_Hybrid", "Rebuild_V10_Hybrid")
s=s.replace("V10_PHOTO_SUPPORTED_WALL_DETAILS; DETAIL_DIMENSIONS_ESTIMATED", "V11_USER_CONFIRMED_RIGHT_ANGLE_WALL; PHOTO_RELATIONS_AND_REFERENCE_DETAILS")
s=s.replace("R=[];A=[];checks=[];hole_probes=[];clipped_parts=[];layer_records=[]", "R=[];A=[];checks=[];hole_probes=[];clipped_parts=[];layer_records=[];all_holes=[]\nBASE_E=copy.deepcopy(E)")
s=s.replace("REFS=['C:/Users/PENG/AppData/Local/Temp/codex-clipboard-9c94e772-aef6-49e7-8ca8-408562170f8a.png',", "REFS=['D:/Desktop/屏幕截图 2026-10-09 115821.jpg', 'D:/Desktop/屏幕截图 2026-10-09 120147.jpg', 'D:/Desktop/d15a543f-dee1-492a-8cbb-cb87cb3bffa1.png', 'D:/Desktop/DJI_0511.DNG', 'D:/Desktop/DJI_0513.DNG',")
s=s.replace("def crown(self,s):return self.za+(self.zb-self.za)*s/self.L", '''def crown(self,s):
        # A 250 mm level corner collar gives both miter faces the same elevation.
        if self.chain=='SITE_COURTYARD_WEST_TILE_WALL':
            if self.j==0:
                return self.zb if s>=self.L-.25 else self.za+(self.zb-self.za)*s/(self.L-.25)
            if self.j==1:
                return self.za if s<=.25 else self.za+(self.zb-self.za)*(s-.25)/(self.L-.25)
        return self.za+(self.zb-self.za)*s/self.L''')
s=s.replace("def base(self,s):return self.ba+(self.bb-self.ba)*s/self.L", '''def base(self,s):
        if self.chain=='SITE_COURTYARD_WEST_TILE_WALL':
            if self.j==0:
                return self.bb if s>=self.L-.25 else self.ba+(self.bb-self.ba)*s/(self.L-.25)
            if self.j==1:
                return self.ba if s<=.25 else self.ba+(self.bb-self.ba)*(s-.25)/(self.L-.25)
        return self.ba+(self.bb-self.ba)*s/self.L''')
s=s.replace("cx=float(cx);cy=.0725", "cx=float(cx);cy=.0725\n        if (seg.j==0 and cx>seg.L-.120) or (seg.j==1 and cx<.120):continue")
s=s.replace("if outer.buffer(-.008).contains(hole):holes.append(hole);probe=(cx,cy,hole.bounds)", "if outer.buffer(-.008).contains(hole):\n            holes.append(hole);probe=(cx,cy,hole.bounds)\n            all_holes.append(dict(node=seg.chain+'_V10_OPEN_FLOWER_BRICKS',segment=seg.j,station_local_m=cx,segment_length_m=seg.L,point_local_m=seg.xyz(cx,0,seg.crown(cx)+.2425),normal_local=[*seg.n,0],hole_width_m=.105,hole_height_m=.105,through_depth_m=.068,drill_diameter_m=.012,drill_depth_m=.1))")
s=s.replace('def strip_solid(seg, poly, top, bottom):','def strip_piece(seg, poly, top, bottom):')
s=s.replace('def tile(seg,center,side,cover):', '''def strip_solid(seg,poly,top,bottom):
    if seg.chain!='SITE_COURTYARD_WEST_TILE_WALL':return strip_piece(seg,poly,top,bottom)
    knee=seg.L-.25 if seg.j==0 else .25
    stations=[seg.local(p)[0] for p in list(poly.exterior.coords)]
    lo,hi=min(stations),max(stations)
    if not lo+1e-8<knee<hi-1e-8:return strip_piece(seg,poly,top,bottom)
    pieces=[]
    for a,b in [(lo-1,knee),(knee,hi+1)]:
        cut=Polygon([seg.xyz(a,-5,0)[:2],seg.xyz(b,-5,0)[:2],seg.xyz(b,5,0)[:2],seg.xyz(a,5,0)[:2]])
        q=poly.intersection(cut)
        for pp in getattr(q,'geoms',[q]):
            if pp.area>1e-12:pieces.append(manifold(strip_piece(seg,pp,top,bottom)))
    return fromman(mf.Manifold.batch_boolean(pieces,mf.OpType.Add))

def tile(seg,center,side,cover):''')
start=s.index("CHAINS=[")
end=s.index("# The longer existing east flank",start)
s=s[:start]+'''# Only the inner west courtyard return changes; the door jamb and main-building
# endpoints stay fixed. User corrected the previous inferred oblique link.
CHAIN='SITE_COURTYARD_WEST_TILE_WALL'
OLD_ROUTE=[[0,1.9],[0,-10.7],[4.9,-11.7]]
NEW_ROUTE=[[0,1.9],[0,-11.7],[4.9,-11.7]]
oldv=[np.asarray(p['geometry']['vertices']) for p in E[CHAIN]['parts']]
bz=[float(oldv[0][0,2]),float(oldv[0][1,2]),float(oldv[2][1,2])]
tz=[float(oldv[1][4,2]),float(oldv[1][5,2]),float(oldv[3][5,2])]
# Keep established endpoint/joint heights rather than inventing a new survey datum.
seeds=[Segment([0,1.9],[0,-11.7],tz[0],tz[1],bz[0],bz[1],[1,0],[1,1],0,CHAIN),
       Segment([0,-11.7],[4.9,-11.7],tz[1],tz[2],bz[1],bz[2],[1,1],[0,1],1,CHAIN)]
core=[]
for seg in seeds:
    # Split at the level corner collar. Each resulting solid has planar triangles,
    # shared 45-degree corner seams, and matched top/bottom elevations.
    intervals=[(0,seg.L-.25),(seg.L-.25,seg.L+.125)] if seg.j==0 else [(-.125,.25),(.25,seg.L)]
    for s0,s1 in intervals:
        xy=Polygon([seg.xyz(s0,-1,0)[:2],seg.xyz(s1,-1,0)[:2],seg.xyz(s1,1,0)[:2],seg.xyz(s0,1,0)[:2]])
        q=seg.xystrip(.125).intersection(xy)
        core.append(part(strip_solid(seg,q,lambda s,d:seg.base(s)+2.,lambda s,d:seg.base(s)),'M_Grey_Brick'))
        core.append(part(strip_solid(seg,q,lambda s,d:seg.crown(s),lambda s,d:seg.base(s)+2.),'M_Wall_Exterior'))
E[CHAIN]=copy.deepcopy(E[CHAIN]);E[CHAIN]['parts']=core
put(CHAIN,core,'RIGHT_ANGLE_CHINESE_TILE_TOP_MASONRY_WALL',wall_route_local_m=NEW_ROUTE,previous_inferred_route_local_m=OLD_ROUTE,plan_width=.25,corner_angle_degrees=90.,corner_collar_length_m=.25,corner_height_datum_preserved=True,user_confirmed_plan_relation=True)
CHAINS=[(CHAIN,NEW_ROUTE),('SITE_GATE_EAST_FLANK',[[8.3,-11.7],[13.3,-11.7]])]
core_hashes={n:hashlib.sha256(json.dumps(BASE_E[n],sort_keys=True,separators=(',',':')).encode()).hexdigest() for n,_ in CHAINS}
allseg={n:segments(n,pts) for n,pts in CHAINS}
''' +s[end:]
s=s.replace("for chain,pts in CHAINS:\n    segs", "for chain,pts in CHAINS[:1]:\n    segs")
s=s.replace("masonry_core_unchanged=True", "masonry_core_unchanged=False")
s=s.replace("original_masonry_core_preserved=True", "original_masonry_core_preserved=False")
s=s.replace("masonry_crown_unchanged=True", "masonry_crown_unchanged=False")
a=s.index("changes=[dict(id=")
b=s.index("\ndef verify():",a)
s=s[:a]+'''changes=[dict(id='V11_COURTYARD_RIGHT_ANGLE',description='用户115821俯视截图确认院墙直角。将旧[0,-10.7]斜接[4.9,-11.7]改为[0,-11.7]水平接门柱，墙芯/白内面/错缝砖饰/回纹框/双面瓦/真实花孔/压顶在45度角平分面收口。转角250mm冠高平段防止瓦帽错层，孔离转角至少120mm；主楼端与门柱端、门洞、厨房及外周墙保持。',source=REFS,dimension_status='USER_CONFIRMED_PLAN_RELATION; LOCAL_DIMENSIONS_FITTED_NOT_FIELD_SURVEY',wall_core_exactly_preserved=False,unchanged_gate_opening_local_m=[5.3,7.9],reference_iron_gate_not_generated=True,buried_foundation_not_generated=True)]
mutation=dict(replace=R,add=A,remove=[],definitions={},materials={},changes=changes,source_scene_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),old_node_sha256={e['name']:hashlib.sha256(json.dumps(BASE_E[e['name']],sort_keys=True,separators=(',',':')).encode()).hexdigest() for e in R},wall_core_hashes_before=core_hashes,layer_dimensions=layer_records,hole_probes=hole_probes,kitchen_gable_ornament_stop_x=east_finish_stop_x,kitchen_solids_preserved=True,gatepost_solids_preserved=True,new_west_terminal_details_trimmed_to_actual_gatepost=True,old_route_local_m=OLD_ROUTE,new_route_local_m=NEW_ROUTE,wall_changed_only_inside_explicit_user_correction_scope=True)
''' +s[b:]
s=s.replace("check('no_wall_core_mutation',not {n for n,_ in CHAINS}.intersection({e['name'] for e in R+A}))", "check('only_user_confirmed_west_wall_core_mutated',{n for n,_ in CHAINS}.intersection({e['name'] for e in R+A})=={CHAIN})\n    check('right_angle_corner',abs(float((seeds[0].u)@(seeds[1].u)))<1e-12)\n    check('untouched_east_flank_and_detail_nodes',not any(e['name'].startswith('SITE_GATE_EAST') for e in R+A))")
s=s.replace("wall_core_hashes_unchanged=core_hashes", "wall_core_hashes_before=core_hashes")
s=s.replace("    (OUT/'Parameters.md').write_text(", "    (OUT/'All_Actual_Hole_Probes.json').write_text(json.dumps(dict(status='PASS',mutation_sha256=hashlib.sha256((OUT/'Mutation.json').read_bytes()).hexdigest(),count=len(all_holes),all_holes=all_holes),ensure_ascii=False,indent=2),encoding='utf8')\n    (OUT/'Parameters.md').write_text(")
params=s.index("'''# V10内院围墙细节参数")
s=s[:params]+"'''# V11院墙直角连接\n\n中心线 [0,1.9]→[0,-11.7]→[4.9,-11.7]，转角90度，250mm墙芯和18mm白内面在45度角平分面连续闭合。接主楼端/左门柱端原坐标和已登记高度保持，门洞X5.3~7.9不变。\n\n转角瓦帽、双面筒瓦/板瓦、莲瓣滴水瓦当、花砖和压顶依墙线重新裁切；角点两侧250mm冠高平段使共享角平分面高程一致，孔距转角至少120mm。所有参考尺寸仍为图示拟合，没有宣称实测施工尺寸。原外周墙、东门侧、厨房/门楼/照壁与不涉及本拐角的对象原样保留。\n\n亭全边界需在X>.22、Y>-11.48的院内，亭代理按150mm间距及完整顶点核查。\n''',encoding='utf8')\n"
(O/'mutation.py').write_text(s,encoding='utf8')
print('configured',O/'mutation.py')
