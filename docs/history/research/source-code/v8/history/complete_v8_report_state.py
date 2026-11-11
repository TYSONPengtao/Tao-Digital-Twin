import json,hashlib
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid')
def read(n):return json.loads((O/'06_Report'/n).read_text(encoding='utf-8'))
ind=read('Independent_V8_QA.json');assert ind['status']=='PASS' and all(c['status']=='PASS' for c in ind['checks'])
assert hashlib.sha256((O/'04_Rhino/Reality_Hybrid_V8.3dm').read_bytes()).hexdigest()==ind['native_sha256']
assert read('V8_Exchange_Photo_Readback.json')['passed']
q=read('Contact_Gap_Ground_Integration_QA.json');q['status']='PASS';q['final_native_independent_qa']='Independent_V8_QA.json';q['final_native_sha256']=ind['native_sha256'];q['final_original_void_projection_residual_m2']=ind['original_void_projection_residual_m2'];q['precision_note']='Support at unobserved east strips is nearby measured ground, not direct measured gap surface; elevation extension remains inferred.'
(O/'06_Report/Contact_Gap_Ground_Integration_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
embed={'status':'PASS','embedded_file_count':len(ind['embedded_original_images']),'embedded_files':ind['embedded_original_images'],'verification':'Every embedded image compared byte-for-byte to original file in Independent_V8_QA.json','limits':'Original image bytes retained; inferred surface geometry and photo projection are separate from field survey precision'}
(O/'06_Report/Native_Embedded_Texture_QA.json').write_text(json.dumps(embed,ensure_ascii=False,indent=2),encoding='utf-8')
p=O/'06_Report/需求汇总与修模依据_V8.md';text=p.read_text(encoding='utf-8')
old='**主模型最终独立 QA 由主任务在最终 3dm 写出后完成，结果以最终独立核查报告为准，本报告不提前给出全模型 PASS 结论。**'
new=f"**最终独立文件与几何检查通过 {len(ind['checks'])} 项，详见 Independent_V8_QA.json；94 项室内复核及 FBX/GLB/OBJ 原图和 UV 读回检查通过。其范围是当前文件与几何数据核查，不是施工精度或 UE5 实际运行验收。**"
assert old in text;text=text.replace(old,new)
text+='''

## 最终局部地面收口

最终覆盖检查定位了厨房东檐边及院墙端共约0.31035㎡的地面投影缺口，已仅在这四个缺口补入地表，不恢复旧屋顶。约0.000475㎡有原地表照片 UV；其余约0.309874㎡从邻近实景低地表延伸，使用暂定土色。东侧参考地表距缺口约0.13～0.40m，包含分级高差，补面按邻近实景的分级参考建立暂定地表；分级线位置缺乏直接观测，仍须实测。没有缺口处的直接摄影测量，不能当作实测地形或施工放样依据。原始实景基底没有因该补缝再修改。

新增补面数据、支撑点和本地核查见 07_Evidence/Final_Contact_Ground_Repair 及 Contact_Gap_Ground_Integration_QA.json；整体空洞投影剩余仅数值细缝，面积见最终独立报告。投影覆盖检查不等于全场景全部网格焊接成一个封闭体。
'''
p.write_text(text,encoding='utf-8')
print('V8 final report state completed',len(ind['checks']),flush=True)
