from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_30';O=Path('E:/jz/JIA/Rebuild_V24_30');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_30.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);source=json.loads((D/'Source.json').read_text('utf8'));assert sha(source['model'])==source['sha256'];summaries={};prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'))
for stem in ['Native','Physics','Measure_Math','Launcher']:
 q=json.loads((R/f'V24_30_{stem}_QA.json').read_text('utf8'))
 assert q['status'].startswith('PASS')and not q['failures']and q['model_sha256']==h,(stem,q.get('status'),q.get('model_sha256'),h)
 summaries[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=[r[0]for r in json.loads((D/'Views.json').read_text('utf8'))]
for v in views:
 q=json.loads((R/f'V24_30_{v}_State.json').read_text('utf8'));assert q['model_sha256']==h and not q['draft'] and(R/q['file']).stat().st_size>10000
assert(R/'V24_30_Measure_UI.png').stat().st_size>10000
for name in ['启动漫游.cmd','打开修正版模型.cmd']:
 s=(Path('E:/jz/JIA/Rebuild_V24_29')/name).read_text('utf8').replace('Architecture_Complete_V24_29.blend','Architecture_Complete_V24_30.blend')
 (O/name).write_text(s,encoding='utf8',newline='\r\n')
readme='''V24.30 内院石铺、外院白色建模场地、渐变路沿与墙厚修正

打开修正版模型.cmd：打开可继续编辑的 Blender 原生模型。
启动漫游.cmd：进入 1.65 米人物漫游与长度/面积测量。

本版按 2026-10-20 晚间标注调整：
1. 内院铺装统一为灰色条石，采用同一组材质、1.12×0.62 米错缝模块；
   清除原来南半院深色斜纹地面、锯齿接缝及重叠的旧铺装。
2. 主院低区为 -0.60 米；厨房北侧高区、屋后内侧通道为 -0.45 米。
   三层楼各层室内地坪保持水平，入口为一个 15 厘米台阶。
   厨房原地坪约 -0.40 米保留，与高通道的小高差继续保留。
3. 外院空地为独立、水平、纯白色的可编辑场地，顶面 -0.60 米，
   与主院低区齐平，保留空地供后续建模。模型顶面面积约 399.24 平方米。
   场地对象名：V24_30_Outer_Yard_White_Building_Pad。
4. 沿聊天蓝线方向设置连续路沿石，长度约 15.71 米；外大门端露高，
   随道路坡度逐步减小并接向内侧平台。门扇开合范围留在道路侧，
   补齐平缓的混凝土门口过渡面，门扇不穿入白色场地。
5. 屋后加内外分隔墙：外侧接白色外院，内侧与高区铺装连通。
6. 外围原青砖挡墙、外侧轮廓和无关墙顶瓦保持原位。
   原来厨房后侧过宽的楔形白色补墙已收回，内侧沿原墙等厚跟随；
   原砌体厚度约 32 厘米，白色内饰面 16 毫米。
   该段瓦檐按外墙参照定位，统一为约 47 厘米宽，消除倒梯形观感。
7. 外院墙脚接水盒收至新地坪以下，补齐楼房西侧墙脚收口，防止露黑缝。

标高和尺寸按现有模型及用户标注图拟合。入口一步暂按 15 厘米处理，
本版没有新增现场测量；以上面积也为模型面积。
原 V24.29 未覆盖，本版另存。

漫游：WASD/方向键移动，空格跳跃，Shift 快走，右键拖动转向，
滚轮调距离，V 切换人眼与第三人称，Home 回院落，Esc 退出，F8 再进入。
直接打开 blend 不会自动接管键盘，请使用“启动漫游.cmd”。

测量：L 点两点测长度；P 沿边界点选后按 Enter 测面积。
Ctrl 点击吸附顶点，Backspace 撤销，Esc 返回漫游，顶栏可导出 CSV。
Ctrl+S 保存测量记录。测量值为模型尺寸。

Reports：本版最终检查图、原生几何与标高检查、通行检查、实机启动及测量检查。
References：本次七张原始标注图片；蓝色叠加线以聊天中的图片为准。
Sources：本版加工数据与重建/验证脚本。原生模型可独立打开编辑，
无需执行 Sources；重放重建脚本另需本机 V24.29 源文件及 Blender。
Manifest_SHA256.json：文件清单及校验值。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
dest=O/'Sources';dest.mkdir(exist_ok=True);data=dest/'v24_30';data.mkdir(exist_ok=True)
for n in ['build','verify','physics_qa','measure_math_qa','launcher_smoke','render','package']:
 p=W/f'v24_30_{n}.py';shutil.copy2(p,dest/p.name)
for n in ['v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,dest/n)
for n in ['Source.json','Views.json','Prepared_Geometry.json','Before_Snapshot.json']:shutil.copy2(D/n,data/n)
for row in prep['raw_objects']:shutil.copy2(D/row['file'],data/row['file'])
(R/'V24_30_Corrections.json').write_text(json.dumps(prep['proof'],ensure_ascii=False,indent=2),encoding='utf8')
(R/'V24_30_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':source['sha256'],'checks':summaries,'review_views':views,'model_levels_m':{'low_court':-.60,'white_outer_pad':-.60,'high_lane_and_rear':-.45,'house_F1':-.45,'entry_riser':.15},'outer_perimeter_masonry_unchanged':True,'gate_geometry_and_animation_unchanged':True,'dimensions_basis':'Existing model datums and marked photographs; no new field survey'},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix!='.blend1'and not p.name.startswith(('Draft_','Before_'))and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files}
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_30_Paved_Court_White_Pad_Curb_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_30')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,info in manifest.items():
  with z.open('Rebuild_V24_30/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==info['sha256'],rel
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':summaries},ensure_ascii=False),flush=True)
