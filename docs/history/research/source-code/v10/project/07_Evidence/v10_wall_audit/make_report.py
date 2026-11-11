# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import json,hashlib,math
from pathlib import Path
SPath=Path(r'E:/jz/JIA/Rebuild_V9_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json')
S=json.loads(SPath.read_text(encoding='utf-8'));E={e['name']:e for e in S['elements']};W=Path('work/v10_wall_audit')
wall_names=['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1','SITE_COURTYARD_WEST_TILE_WALL','SITE_GATE_EAST_FLANK']
records=[]
for n in wall_names:
 e=E[n]
 if n=='SITE_GATE_EAST_FLANK': points=[[8.3,-11.7],[13.3,-11.7]]
 else:
  points=[]
  for p in e['parts'][::2]:
   v=p['geometry']['vertices'];a=[(v[0][i]+v[3][i])/2 for i in range(2)];b=[(v[1][i]+v[2][i])/2 for i in range(2)]
   if not points:points.append(a)
   points.append(b)
 vs=[v for p in e['parts'] for v in p['geometry']['vertices']]
 crown=[]
 for p in e['parts'][1::2]:crown.extend(v[2] for v in p['geometry']['vertices'][4:8])
 coping=E[n+'_TILE_COPING']
 cap_vs=[v for p in coping['parts'] for v in p['geometry']['vertices']]
 records.append({'name':n,'source':e.get('source'),'classification':e.get('classification','PHOTO_TRACED_RETAINING_PERIMETER'),'centerline_xy_local_m':points,'length_m':sum(math.dist(a,b) for a,b in zip(points,points[1:])),'segments':len(points)-1,'width_m':e.get('plan_width'),'core_bounds_local_m':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'crown_z_range_m':[min(crown),max(crown)],'existing_materials':sorted(set(p['material'] for p in e['parts'])),'coping_name':coping['name'],'coping_parts':len(coping['parts']),'coping_bounds_local_m':[[min(v[i] for v in cap_vs) for i in range(3)],[max(v[i] for v in cap_vs) for i in range(3)]],'recommended_change':'Develop actual cover/pan/drip tiles, real pierced ornamental ridge and moulding bands within repair scope; retain centerline, slope, opening endpoints and retaining core.'})
preserve=[e['name'] for e in S['elements'] if e['name'].startswith(('SITE_INNER_STONE_GATEHOUSE','SITE_INNER_DARK_TIMBER_DOORS','SITE_INNER_GATEHOUSE','SITE_GATEHOUSE','SITE_KITCHEN','SITE_SOUTH_SCREENWALL','SITE_SCREENWALL','SITE_SOUTH_EAST_ANNEX'))]
opening_start=[-14.97732094598484,-8.325656081075762];opening_end=[-12.501865173706502,-12.863215399690171]
report={'audit_type':'READ_ONLY_REFERENCE_AND_SCOPE','scene_file':str(SPath),'scene_sha256':hashlib.sha256(SPath.read_bytes()).hexdigest(),'model_file':'E:/jz/JIA/Rebuild_V9_Hybrid/04_Rhino/Reality_Hybrid_V9.3dm','coordinates':'LOCAL meters Z-up; do not apply ENU directly. ENU Rz +19.65 deg and origin [-3.45191261,-3.90043098,TAO_PRIVATE_SITE_002].','user_reference_image':'C:/Users/PENG/AppData/Local/Temp/codex-clipboard-9c94e772-aef6-49e7-8ca8-408562170f8a.png','reference_dimensions_m':{'overall_height':2.7,'body_to_eave':1.95,'plinth':.45,'upper_body':1.5,'tile_zone':.3,'pierced_ridge_and_cap':.45,'standard_bay':3.,'wall_thickness':.24,'reference_gate_width':3.5,'detail_cover_pitch':.12,'drip_projection':.08,'nominal_brick':[.24,.115,.053]},'dimension_status':'REFERENCE_STYLE_ONLY_NOT_FIELD_MEASURED; image shows simplified dimensions and material construction suggestions. Actual site wall centerline widths .25/.32 and varying crown/datum take priority. Hidden footing/reinforcement/mortar strengths unverified.','wall_records':records,'openings_to_preserve':[{'name':'SOUTHWEST_PERIMETER_GAP','wall_1_start':opening_start,'wall_0_end':opening_end,'endpoint_centerline_distance_m':math.dist(opening_start,opening_end),'note':'V9 metal gate node absent after V8 red-line earth-only clearance. Never create reference 3.5m iron gate, gateposts or new roof in this opening. Existing V3 source gate panel span approximately4.46m is historical and not present geometry.'},{'name':'INNER_GATEHOUSE_TIMBER_OPENING','door_clear_width_m':E['SITE_INNER_STONE_GATEHOUSE']['clear_width_m'],'door_clear_height_m':2.5,'x_interval_m':[5.3,7.9],'wall_center_y_m':-11.7,'floor_z_m':-.45,'note':'Keep timber doors and V9 raised gate roof; reference iron gate must not replace actual doors.'},{'name':'SCREENWALL_IS_SOLID','x_interval_m':[3.25,10.8],'y_interval_m':[-17.1,-16.72],'note':'No door in screenwall. Maintain solid perimeter wall under raised body.'}],'protected_existing_elements':preserve,'protected_original_reality_meshes':'All 5 existing base meshes and their UVs/normals/faces/material references outside existing allowed holes; do not remesh/replace original textured retaining stones with artificial brick.','sibling_wall_finish_nodes':['SITE_COURTYARD_WEST_WHITE_INSIDE']+['SITE_WEST_TILE_WALL_PANEL_'+str(i) for i in range(10)],'finish_placement_warning':'Existing WEST_TILE_WALL_PANEL_* x=-.145 are on west face; courtyard east-face white finish spans x=.125..143. DJI_0161 supports ornament on white courtyard face. New east-face panel rear must seat at x=.143 and only new ornamental width/depth extend east; preserve gray farmyard face where photo-supported.','photo_evidence_viewed':[{'path':'D:/DJI/0002/DCIM/101MEDIA/DJI_0025.JPG','finding':'Kitchen ceramic ridge, white rendered adjacent courtyard wall with capped roof; close relation to actual glazed main facade.'},{'path':'D:/DJI/0002/DCIM/101MEDIA/DJI_0073.JPG','finding':'Long exterior perimeter: white inner face with low double-sloped tile cap; actual diagonal vehicle-gate opening. Photo also shows low timber farmyard fence which is removed by later explicit red-line clearance.'},{'path':'D:/DJI/0002/DCIM/101MEDIA/DJI_0156.JPG','finding':'Kitchen timber front must remain timber, silver eave gutter is real; rear visible rendered wall with decorative frames.'},{'path':'D:/DJI/0002/DCIM/101MEDIA/DJI_0161.JPG','finding':'Clear courtyard wall: actual pierced quatrefoil/diamond ridge, cover-tile fronts with floral end discs, alternate wide and narrow stepped plaster frames, true roof miter at inside corner. White wall/gray weathered lower portion.'},{'path':'D:/DJI/0002/DCIM/101MEDIA/DJI_0107.JPG','finding':'Screenwall specific molding/open ridge + highly weathered plaster; preserve its raised flying-eave body and source color.'}],'joint_rules':['Honor the same offset/miter at all wall centerline turns; no independently overlapped perpendicular coping slabs.','Build corner tiles to the angle bisector and clip barrel/pan modules at true seam; flower ridge motif should stop/join, not protrude into adjacent tiles.','At X0/Y1.9 terminate west courtyard wall at solid KZ_1_1_F1 front face, keeping facade bay glazing intact.','At west wall endpoint [4.9,-11.7] stop decorative ridge/caps at gatehouse post face; do not span door opening [5.3,7.9].','East flank endpoint [8.3,-11.7] joins gatehouse post; other end [13.3,-11.7] meets kitchen masonry back/gable. Preserve V9 kitchen/gate underlap.','Do not introduce standard-coping pieces in omitted perimeter cap gap below screenwall (center x3.1..10.95,y<-16). Existing nine segments intentionally use raised screenwall roof.','Retain sloping crown and existing base heights. Reference body/cap proportions may be fit inside available local zones, not used to flatten entire perimeter.','Use separate closed solids or reusable instances for cover tile, pan tile, end disc, real pierced flower brick, mortar backing and plaster frames. Keep actual holes in flower brick, not opaque texture.','Do not add buried C20/C25 footings or steel connections as verified construction; record as conceptual layer if necessary.'],'material_rules':{'gray_roof':'M_Roof or new separate gray clay-tile material matched to DJI, roughness around.82; never wood material','plaster':'M_Wall_Exterior; gray border M_Stone_Frame distinct from roof tile','interior_or_courtyard_brick':'M_Grey_Brick where actual brick is photo supported; use modeled individual brick joints only on repair/add geometry','retaining_stone':'Keep M_Stone_Rubble + original reality texel color. User reference 450mm gray brick plinth does not mean all retaining stones become brick.','real_texture':'Preserve original UV images. Photo projection onto new detail only where actual donor correspondence exists; clean tiled material for unmatched new parts with estimate status.'},'final_validation_recommendations':['Verify every unchanged original native object geometry hash and material bindings remain exactly same except allowed newly detailed wall nodes.','Check all roof/cap parts closed, positive volume, outward normals, finite UV; actual pierced openings open in negative space, solid bars watertight.','Recompute wall terminus/post/window clearance and jamb opening occupancy to avoid recurring enclosure/opening errors.','Compare all centerline and crown endpoints to above baseline; no wall in southwest opening, inner doorway or red-line cleared earth plot.','Review clay tile + ornament miter in top and ground-level corner renders.','Keep measured/as-built uncertainty flags; no construction-code compliance claims from inferred diagram alone.']}
(W/'Reference_Scope.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
md='''# V10 围墙院墙参考范围（只读审核）

新图可以用于瓦帽、花脊、滴水瓦当、长短框线脚与青灰材料的深化。现场墙线、开口、挡土高差与 V9 门楼/照壁飞檐优先保留，示意图的 2700 mm 总高、3000 mm 开间、3500 mm 铁门并非现场尺寸。

| 当前节点 | 墙线长度 | 当前墙厚 | 墙顶 Z 范围 | 处理 |
|---|---:|---:|---:|---|
'''
for r in records:md+=f"| `{r['name']}` | {r['length_m']:.4f} m | {r['width_m']:.2f} m | {r['crown_z_range_m'][0]:.4f}～{r['crown_z_range_m'][1]:.4f} m | 保留墙芯与线形，深化对应瓦帽/花脊/线脚 |\n"
md+='''
## 必须保留的边界

- 周界两组墙线分别有 117、22 段，合计 121.8848 m。斜坡墙顶随源模型起伏，不按示意总高拉齐。
- 西南断口：wall 1 起点 `[-14.97732095,-8.32565608]`，wall 0 终点 `[-12.50186517,-12.86321540]`；端点中心线距离 **5.16888 m**。这是几何断口跨度，不是实测门洞净宽。V9 铁门节点已因 V8 红线清场而删除，不得按新图重新添加铁门、门柱或门屋顶。
- 内木门洞：X **5.30～7.90**、墙中线 Y **-11.70**、净宽 **2.60 m**、净高 **2.50 m**，保留木门与石/灰塑门柱。
- 西内院瓦墙：`[0,1.9] → [0,-10.7] → [4.9,-11.7]`。上端顶到 `KZ_1_1_F1` 实柱前面 Y 1.90，保留玻璃。
- 东门楼侧墙：`[8.3,-11.7] → [13.3,-11.7]`，接门柱与厨房砌体后/山墙。
- 南照壁是实墙，不能新增门洞。下方周界瓦帽缺失的九段为刻意避开照壁飞檐，不应补普通双坡瓦帽。

## 对照照片与材质

本次实际查看 DJI_0025、0073、0156、0161、0107。**DJI_0161** 清楚支持新图的花脊真镂空、长框/短框交替、筒瓦瓦当以及阴角瓦帽交接；**DJI_0073** 支持周墙白色内面和较低的双坡瓦帽，也显示西南实际门区。**DJI_0107** 是照壁特殊飞檐/线脚与风化灰塑，应保留其单独造型。

外侧石砌挡墙原材质和实景贴图保留，不能统一变为示意 450 mm 青砖勒脚。厨房木架与真实银灰金属檐沟也保留。屋瓦采用青灰陶瓦、墙面白灰、框脚灰色，分层实体表达；新细节没有匹配照片时使用估计材料并保留状态。

当前西墙框节点 `SITE_WEST_TILE_WALL_PANEL_0..9` 位于 X -0.145 西面；内院白色抹灰面位于 X 0.125～0.143。DJI_0161 支持白色院内面上的框脚。若增加院内框脚，后背应贴 X 0.143，不应漂浮或伸穿原墙芯。

## 交接规则

转角瓦帽沿角平分线闭合并裁切筒瓦，花脊在真实接缝收头；不把两个完整矩形瓦帽互相穿插。内门楼门洞不得被横向瓦帽、花砖或饰框跨越。各段维持同一源墙顶起伏与端点，整体叠加屋顶应与墙芯共同连续。

新图中的 240 mm 墙厚、120 mm 瓦距、80 mm 出檐、240×115×53 mm 青砖可以作为参数参考，但现场/源模型已有墙厚是 250/320 mm。C20/C25、M7.5、隐蔽基础和钢筋尚无实测证据，本次不按已核实施工构造写入。

具体全坐标墙线、保护节点及材质/测试建议见 `Reference_Scope.json`。本次未编辑 Scene 或任何模型。
'''
(W/'Reference_Scope.md').write_text(md,encoding='utf-8')
print('report',W/'Reference_Scope.json','walls',len(records),'protected',len(preserve))
