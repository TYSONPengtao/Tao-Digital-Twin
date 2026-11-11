from pathlib import Path
import json,collections
O=Path(r'E:\jz\JIA\Rebuild_V4');a=json.loads((O/'09_Report/Construction_Geometry_QA_V4.json').read_text(encoding='utf-8'))
for name in ['guard_height','stair_rise_uniformity','stair_geometric_width_and_rail_occupancy','stair_pair_gap','low_window_guard_height','site_paving_slope']:
 rr=[r for r in a['checks'] if r['check']==name]
 print(name,[(r['status'],r['measured']) for r in rr][:4])
lines=['# V4 待专业复核清单','','以下事项没有计作通过；均来自实体核查和资料缺口。施工协调模型不能代替这些确认。','']
for r in a['checks']:
 if r['status']!='needs-design':continue
 lines+=['- '+r['check']+'：'+', '.join(r['elements'])+'。'+r['note']+'；核查值 '+json.dumps(r['measured'],ensure_ascii=False)]
lines+=['','额外资料缺口：厨卫沉板/完成面及地漏准确标高；基础承载与配筋；木构节点/瓦顶抗风连接；摄影高程与控制点；院界权属；新增屋面雨水管容量及排入外部管网的井底高程；西侧太阳能屋面上人条件。']
(O/'09_Report/PENDING_ITEMS_V4.md').write_text('\n'.join(lines),encoding='utf-8')
