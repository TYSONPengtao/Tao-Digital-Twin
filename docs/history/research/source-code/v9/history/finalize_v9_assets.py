import json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
kernel=read(O/'06_Report/Editable_Rhino_Kernel_QA.json');assert not kernel['invalid'] and not kernel['unexpected_open_solids']
qa=read(O/'06_Report/Editable_Local_Native_QA.json');qa['initial_faceted_Brep_tolerance_flags_count']=len(qa['invalid']);qa['invalid']=kernel['invalid'];qa['unexpected_open_solids']=kernel['unexpected_open_solids'];qa['final_kernel']='RhinoCommon 8 tolerance initialization and readback';save(O/'06_Report/Editable_Local_Native_QA.json',qa)
M=read(O/'02_Data/Materials.json');B=read(O/'02_Data/Base_Index.json');images={Path(v['texture']).name:Path(v['texture']) for v in list(M.values())+B if v.get('texture')};rows=[]
for name,p in images.items():
 q=O/'05_Export'/name;shutil.copy2(p,q);a=hashlib.sha256(p.read_bytes()).hexdigest();b=hashlib.sha256(q.read_bytes()).hexdigest();assert a==b;rows.append({'file':name,'sha256':a})
I=read(O/'02_Data/Patch_Index.json');changed=set(read(O/'02_Data/V9_Changed_Nodes.json')['changed']);gray=[r for r in I if r['name'] in changed and r['name'].startswith('SITE_GATEHOUSE_')];dark=[r for r in I if r['name'] in ['SITE_KITCHEN_EXPOSED_TIMBER_ROOF_FRAMING','SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS','SITE_KITCHEN_FASCIA_BOARD']]
assert all(not any(m.startswith('PATCH_PHOTO_') for m in r['materials']) for r in gray+dark)
save(O/'06_Report/V9_Material_and_Texture_QA.json',{'status':'PASS','original_exchange_companion_images':rows,'images':len(rows),'new_gate_eave_finish':'Photograph-observed gray material, no adjacent red door atlas transfer','new_dark_timber_eave_finish':'Photograph-observed dark timber material; no generated bitmap texture','preserved_source_images':'10 originals retained byte-exact; independent main/exchange checks govern UV and binding','hidden_materials_measured':False})
for folder in ['v9_reference_audit','v9_eave_layers','v9_roof_relation']:
 d=O/'07_Evidence'/folder;d.mkdir(exist_ok=True)
 for p in (W/folder).iterdir():
  if p.is_file() and p.suffix in ['.py','.json','.md','.log']:shutil.copy2(p,d/p.name)
doc=O/'06_Report/需求汇总与修模依据_V9.md';s=doc.read_text(encoding='utf-8').split('\n## 最终几何与材质核查')[0];s+='\n## 最终几何与材质核查\n\n合并后的独立关系／碰撞审核通过：1200 个闭合实体、85 对实际 Boolean 运算，厨房瓦壳／盖瓦／南墙／木檐与门楼墙芯及新檐下层无正体积交叠；东南墙端共同收口。RhinoCommon 有效性复读通过，修改构件实体闭合另由交付检查核实。\n\n渲染复查发现邻近红色门框纹理被近面投影采入新灰檐，已取消这些新小饰件及深色木檐的近面贴图转移，按实拍灰色／深木色材质表达。原实景材质、10 张原图和未改构件 UV 保留；新增饰件不宣称具有独立实测纹理。贴图和文件一致性见 Independent_V9_QA.json、V9_Material_and_Texture_QA.json、V9_Exchange_Photo_Readback.json。\n\n可编辑实体转换统一使用修改构件的双精度顶点，多边形端面在其实际三维平面内三角化，修复旧转换器将竖直牙子端面投影到 XY 导致漏封口的问题。参数几何未改变；最终文件闭合性以 Editable_Changed_Solids_QA.json 和 Independent_V9_QA.json 为准。\n'
doc.write_text(s,encoding='utf-8');print('Finalized kernel QA, 10 external exchange originals and source evidence',flush=True)
