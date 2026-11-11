"""Independent read-only merged V9 reference and solid-intersection review."""
import sys,json,hashlib,copy,math,importlib.util
from pathlib import Path
from collections import Counter
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
import manifold3d as md
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
import export_v5 as ex
O=Path(__file__).parent
PTH=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
paths=[W/'v9_roof_relation/Mutation.json',W/'v9_eave_layers/Mutation.json']
source_bytes=PTH.read_bytes(); S=json.loads(source_bytes); patches=[json.loads(p.read_bytes()) for p in paths]
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
checks=[]
def check(name,ok,**extra):checks.append(dict(name=name,passed=bool(ok),**extra))
sets=[set(e['name'] for e in m['replace']+m['add']) for m in patches]
check('patch_replacements_and_additions_have_disjoint_names',not sets[0]&sets[1],conflicts=sorted(sets[0]&sets[1]))
E={e['name']:e for e in S['elements']}
check('merged_element_names_unique',len(E)==len(S['elements']))
staged={e['name']:e for m in patches for e in m['replace']+m['add']}
check('all_18_frozen_patch_geometries_are_exactly_the_final_scene_parts',all(n in E and E[n]['parts']==e['parts'] for n,e in staged.items()),changed_object_count=len(staged),mismatches=[n for n,e in staged.items() if n not in E or E[n]['parts']!=e['parts']])
cache={}; failures=[]
def body(name,i):
    key=(name,i)
    if key in cache:return cache[key]
    g=E[name]['parts'][i]['geometry'];v,fs,_,_=ex.solid_data(g)
    tri=[]
    for f in fs:
        ids=ex.triangulate(v[f]) if len(f)>3 else [[0,1,2]]
        tri.extend([[f[a] for a in t] for t in ids])
    ss=md.Manifold(md.Mesh64(np.asarray(v,np.float64),np.asarray(tri,np.uint64)))
    if ss.status()!=md.Error.NoError:failures.append({'name':name,'part':i,'status':str(ss.status())})
    b=(ss,np.asarray(v).min(0),np.asarray(v).max(0));cache[key]=b;return b
gate_names=['SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE']+[e['name'] for e in patches[1]['add'] if e['name'].startswith('SITE_GATEHOUSE_')]
source_names=['SITE_KITCHEN_CHINESE_TILE_ROOF','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_1']+[e['name'] for e in patches[0]['add'] if e['name'].startswith('SITE_KITCHEN_')]
source_names+=['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES','SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS','SITE_KITCHEN_EXPOSED_TIMBER_ROOF_FRAMING','SITE_KITCHEN_STONE_FLOOR']+[e['name'] for e in patches[1]['add'] if e['name'].startswith('SITE_KITCHEN_')]
source_names=list(dict.fromkeys(source_names))
for n in gate_names+source_names:
    for i in range(len(E[n]['parts'])):body(n,i)
check('all_combined_joint_parts_convert_to_valid_closed_manifolds',not failures,converted_parts=len(cache),failures=failures)
rows=[];positive=[];tol=1e-9;tested=0;pruned=0
for n in source_names:
    sis=[0] if n=='SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES' else range(len(E[n]['parts']))
    for gn in gate_names:
        total=0.;maximum=0.;pairs=[];calls=0
        for i in sis:
            ss,slo,shi=body(n,i)
            for j in range(len(E[gn]['parts'])):
                gs,glo,ghi=body(gn,j)
                if np.any(np.minimum(shi,ghi)-np.maximum(slo,glo)<=1e-10):pruned+=1;continue
                vv=(ss^gs).volume();calls+=1;tested+=1
                if vv>tol:pairs.append({'source_part':i,'gate_part':j,'overlap_volume_m3':vv})
                total+=max(0.,vv);maximum=max(maximum,vv)
        row=dict(kitchen=n,gate=gn,kitchen_parts=len(sis),gate_parts=len(E[gn]['parts']),boolean_calls=calls,overlap_volume_m3=total,maximum_part_overlap_m3=maximum,positive_pairs=pairs)
        rows.append(row)
        if maximum>tol:positive.append(row)
check('kitchen_roof_tiles_south_wall_and_visible_layers_do_not_enter_gate_wall_core_or_eave_layers',not positive,tolerance_m3=tol,positive_group_count=len(positive),tested_pair_booleans=tested,bounds_disjoint_pair_count=pruned)
rv,rf,_,_=ex.solid_data(E['SITE_KITCHEN_CHINESE_TILE_ROOF']['parts'][0]['geometry'])
polys=[]
for f in rf:
    p=Polygon(np.asarray(rv)[f,:2]);
    if p.area>1e-12 and p.is_valid:polys.append(p)
foot=unary_union(polys);gateplan=box(4.05,-13.02,9.05,-10.22)
under=foot.intersection(gateplan)
sp=importlib.util.spec_from_file_location('roof_params',W/'v9_roof_relation/roof_parameters.py');P=importlib.util.module_from_spec(sp);sp.loader.exec_module(P)
expected=Polygon(P.KITCHEN_FOOTPRINT)
coordinate_tolerance=1e-8
area_tolerance=expected.length*coordinate_tolerance+math.pi*coordinate_tolerance**2
projection_residual=foot.symmetric_difference(expected).area
projection_distance=foot.boundary.hausdorff_distance(expected.boundary)
check('actual_roof_projection_matches_shared_joint_footprint',projection_residual<=area_tolerance and projection_distance<=coordinate_tolerance,actual_area_m2=foot.area,expected_area_m2=expected.area,residual_area_m2=projection_residual,boundary_hausdorff_m=projection_distance,numerical_coordinate_tolerance_m=coordinate_tolerance,derived_area_tolerance_m2=area_tolerance,tolerance_reason='Mesh Boolean quantized cut vertices differ around 3 nanometres; area tolerance derives from actual perimeter times 1e-8 m numeric coordinate tolerance, not field accuracy.')
check('kitchen_still_projects_under_gate_roof',under.area>0,underlap_area_m2=under.area,underlap_polygon=under.__geo_interface__)
check('gate_wall_core_does_not_swallow_kitchen_roof_plan',foot.intersection(box(4.9,-11.95,8.3,-11.45)).area<1e-9,intersection_area_m2=foot.intersection(box(4.9,-11.95,8.3,-11.45)).area)
samples=[]
for x in np.linspace(6.98,9.05,101):
    for y in np.linspace(-12.05,-10.22,101):
        if under.covers(__import__('shapely.geometry',fromlist=['Point']).Point(x,y)):
            samples.append([x,y,P.zgate(x,y)-.075-P.zkitchen(x,y)-.10])
q=np.array(samples)
check('ordinary_gate_roof_is_above_lower_kitchen_roof_in_underlap',len(q)>0 and q[:,2].min()>0,roof_only_sampled_min_clearance_m=float(q[:,2].min()),sample_count=len(q),interpretation='Ordinary ceramic roof-shell envelope sampled separately; full wall/eave solids verified by actual Boolean rows above')
wall=E['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES']['parts'];south_v=ex.solid_data(wall[0]['geometry'])[0];east_v=ex.solid_data(wall[2]['geometry'])[0]
south_ym=float(np.asarray(south_v)[:,1].min());east_ym=float(np.asarray(east_v)[:,1].min())
corner_expected=P.kitchen_ymin(13.13)+.18+.22
check('south_gable_and_east_wall_share_corner_plane',abs(east_ym-corner_expected)<1e-9,east_wall_south_y=east_ym,south_wall_north_y_at_east_corner=corner_expected,absolute_gap_m=abs(east_ym-corner_expected))
refs=[Path(r'D:\Desktop\1aeb5b24-97ff-45f0-a8e3-f2916523ffb3.png'),Path(r'D:\Desktop\4daa4b13-ab29-4a24-81ca-0a7345c7eecb.png')]
photo_refs=[(Path(r'D:\DJI\0002\DCIM\101MEDIA')/f'DJI_{n:04}.JPG',t) for n,t in [(46,'两组普通屋面及正交交接，木房低檐在门楼檐下。'),(47,'门楼正面瓦口、灰饰檐下挂落与左侧木房端檐。'),(48,'门楼檐口相对低木房屋面高度，门洞位置。'),(101,'近仰视灰饰椽头状块、封檐线脚、回纹饰带、下挂牙子；内部材质未测。')]]
photo_refs +=[(Path(r'D:\DJI\0003\DCIM\101MEDIA\DJI_0113.JPG'),'木房前檐银色金属檐沟/包边，木色檐下梁及花格。'),(Path(r'D:\DJI\0003\DCIM\101MEDIA\DJI_0117.JPG'),'同视点展示低木房檐在高门楼檐下，门楼封檐/牙子；照片逆光。')]
evidence=[{'path':str(p),'exists':p.exists(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else '', 'observation':t} for p,t in photo_refs]
check('all_cited_observed_source_photos_exist',all(r['exists'] for r in evidence),count=len(evidence))
limitations=['两幅用户示意图注明依据照片推断、非实测施工图；表达层次和搭接关系，不作为尺寸或结构设计依据。','本次高差、端线、封檐断面、椽头间距及牙子形状为照片和已配准模型估算；不能据此声明施工测绘精度。','门楼灰饰椽头状构件表面可见，但内部是否实木不能从照片认证；木房可见木架另行分类。','隐蔽挂瓦条、顺水条和防水层只记录关系，不制造已实测的隐藏构件。','排水箭头仅作视觉坡向参考；金属檐沟/包边按实拍保留简化可见边，不认证完整隐蔽排水节点。']
for p in paths:check('staged_patch_unchanged_during_audit_'+p.parent.name,hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p)],sha256=hashes[str(p)])
check('source_scene_read_only',PTH.read_bytes()==source_bytes,sha256=hashlib.sha256(source_bytes).hexdigest())
result=dict(status='PASS' if all(c['passed'] for c in checks) else 'FAIL',checks=checks,source_scene=str(PTH),source_scene_sha256=hashlib.sha256(source_bytes).hexdigest(),mutation_sha256=hashes,method='Final merged scene read directly and checked against all 18 frozen patch part geometries; native polygonal solids triangulated with exporter triangulation and Mesh64 double coordinates; no source edits.',joint_boolean_volume_table=rows,positive_intersections=positive,photo_support=evidence,user_diagram_sources=[str(p) for p in refs],limitations=limitations)
(O/'Final_V9_Reference_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
lines=['# V9 屋檐关系独立核查','',f'结果：**{result["status"]}**。直接只读最终合并场景，核对 18 个节点几何与冻结补丁一致；本报告不修改模型。','',f'共 {len(checks)} 条核查；{len(cache)} 个实体构件转换为双精度闭合流形，实际 Boolean 相交 {tested} 对，包围盒无相交排除 {pruned} 对。','', '## 来源图与模型对应','', '| 核查项 | 实拍支持 / 未知 | 合并后模型 |','|---|---|---|',f'| 前低后高、木房端檐伸入门檐下 | 0046、0047、0048、0003_0117 支持；具体标高未实测 | 实际屋面平面重叠 {under.area:.4f} m²；普通瓦面抽样最小净距 {q[:,2].min():.4f} m |',f'| 门楼墙芯不能吞掉木房瓦端 | 图示说明搭接；需要实际实体复核 | 厨房壳/全盖瓦/南墙/新增木檐层，对门楼墙芯及新增6组檐下实体：{len(positive)} 组正体积交叠 |','| 封檐、饰带、牙子分别表达 | 0101 可见灰饰块、回纹带、牙子；内部材料未知 | 分立实体；灰饰层不认证为木架，隐蔽瓦条未虚构 |','| 木房金属檐边 | 0003_0113 明确见银色檐沟/包边 | 独立可见金属收边层保留 |',f'| 南山墙与东墙接头 | 原端线调整需要闭合 | 共同 Y={corner_expected:.5f} m；端面间隙 {abs(east_ym-corner_expected):.9f} m |','', '## 实体交叉结果','', '| 厨房构件 | 门楼构件 | 实际交叠体积 m³ |','|---|---|---|']
for r in rows:
    if r['boolean_calls'] or r['overlap_volume_m3']>tol:lines.append(f'| {r["kitchen"]} | {r["gate"]} | {r["overlap_volume_m3"]:.12g} |')
if positive:lines+=['','**未通过项需修复：**']+[f'- {r["kitchen"]} / {r["gate"]}：{r["overlap_volume_m3"]:.12g} m³' for r in positive]
lines+=['','## 依据照片','']+[f'- [{p.name}]({str(p).replace(chr(92),"/")})：{t}' for p,t in photo_refs]+['','## 精度和来源限制','']+['- '+x for x in limitations]
(O/'Final_V9_Reference_QA.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps({'status':result['status'],'checks':len(checks),'positive_intersections':positive,'patch_hashes':hashes},ensure_ascii=False,indent=2))
