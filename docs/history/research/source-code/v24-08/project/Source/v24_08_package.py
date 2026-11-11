import json,shutil,hashlib,zipfile
from pathlib import Path
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V24_08');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_08.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
qa=json.loads((R/'V24_08_Fresh_Blend_QA.json').read_text());view=json.loads((R/'V24_08_Preview_States.json').read_text());build=json.loads((R/'V24_08_Build.json').read_text());h=sha(P)
assert qa['status'].startswith('PASS')and not qa['failures']and qa['model_sha256']==view['model_sha256']==build['sha256']==h
assert len(view['views'])==6 and all((R/v['file']).is_file()for v in view['views'])
for n in['v24_08_common.py','v24_08_build.py','v24_08_geometry.py','v24_08_verify.py','v24_08_render.py','v24_08_package.py','v24_06_common.py','v24_06_roof.py','v24_03_junction_blender.py','v24_qa_blender.py']:shutil.copy2(W/n,O/'Source'/n)
refs=[('D:/Desktop/屏幕截图 2026-10-17 114129.jpg','01_User_Exterior_Before.jpg'),('D:/DJI/0002/DCIM/101MEDIA/DJI_0523.JPG','02_Real_Kitchen_Exterior.jpg'),('D:/Desktop/问题/屏幕截图 2026-10-12 001208.jpg','03_Reference_Scanned_Exterior.jpg'),('D:/DJI/0002/DCIM/101MEDIA/DJI_0513.JPG','04_Real_Exhaust_Wall.jpg'),('D:/DJI/0002/DCIM/101MEDIA/DJI_0516.JPG','05_Real_Perimeter_Wall.jpg'),('D:/DJI/0002/DCIM/101MEDIA/DJI_0515.JPG','06_Real_Perimeter_Return.jpg'),('D:/Desktop/屏幕截图 2026-10-17 114951.jpg','07_Real_Courtyard_Width.jpg'),('D:/Desktop/屏幕截图 2026-10-17 115048.jpg','08_User_Court_Before.jpg'),('D:/Desktop/DJI_0011.JPG','09_Real_Overhead_Courtyard.JPG')]
for src,n in refs:
 assert Path(src).is_file(),src
 shutil.copy2(src,O/'References'/n)
for n in['V24_07_Fresh_Blend_QA.json','V24_07_Marked_Height.json','V24_07_Doors.json']:shutil.copy2(Path('E:/jz/JIA/Rebuild_V24_07/Reports')/n,O/'Source'/n)
shutil.copy2(W/'v24_03_dimension_audit/V24_03_Dimension_Audit.json',O/'Source/Existing_Reference_Registration.json')
note=f'''# V24.08 厨房退让、外墙与厨房外立面

完整独立Blender模型：Blender/Architecture_Complete_V24_08.blend。单位米，原实景贴图已内嵌，旧版本保留。

厨房向内院挤压的边缘向外侧LOCAL +X退让0.450m：基础前沿X7.700→8.150，木立面基准X9.050→9.500。X≤9.400的檐廊、柱子、门窗及构件刚性平移；至外侧X14.100线逐步消减位移，外侧围墙、挡土基础和场地边界完全保留。厨房进深相应收小，没有将整个基础直接向场外平移。屋面、椽檩梁架、连接储物间的谷线同步衔接，门楼右侧闭合墙端留在原门柱连接点，另一端接至退让后的厨房立面。

内院侧通行宽度因此增加0.450m。新增释放的长条面积约4.17平方米，沿用相邻内院原有石材及灰缝材质补铺；门口处另有短段同材质收口。此退让量依据用户“往后退一点”的要求与提供的地面、俯视照片作模型比例校正，并非新增现场实测尺寸。既有2.3dm配准资料仅作为场地背景，存在摄影测量误差。

厨房两扇门连同铰轴向外平移0.450m，门扇几何及旋转动画不变。所有26扇原动作曲线保持。1帧关闭，20帧半开，40帧全开（默认）。

外墙依据DJI_0513、0515、0516、0523：删除外侧多余檐下白色宽带及对应外侧线框，使实景灰砖直达瓦口；内侧白墙及内侧线框、正门照壁装饰保留。保留原毛石挡墙、深色条石过渡与压顶瓦的注册轮廓和贴图；厨房山墙与连接墙使用已有实景灰砖纹理、米制UV；原实体单块砖改为灰砖自身的风化表面，避免每块砖内再次叠出一套小砖缝。内院厨房后墙及檐廊后立面跟随同一灰砖色系。

注册东檐原裸露延伸坡面补178块有厚度的筒瓦、板瓦，随原坡面和不规则边界收口。依据照片补圆形开口烟管、下弯柔性排气弯管、抱箍、支架与穿墙圈；管壁有内外表面，开口可见。排气细部位置为照片拟合，未冒称测量数据。原外储物间金属雨棚和院内亭子的屋顶保留。

门楼保持最后“1到2”确认的最低檐底Z3.100m、居中短檐及薄歇山结构。原15块实体石浮雕、细化红木门板和铜把手、院墙中线调整、南过道同材质铺地、指定两树删除与厨房单根独立檐廊柱均保留。厨房接门楼屋面恢复未裁切端部后按当前檐位复核，本次退让后屋面无相交，接缝预览已检查。

最终保存后重新打开：{len(qa['checks'])}项校验，失败0项。原{qa['original_materials']}套材质、{qa['original_images']}张图像、26扇门动作、其他场地对象及UV逐项核对。新建构件全部封闭且体积为正；主要外侧墙基及围墙几何摘要与上一版一致。彩色预览6张使用同一份模型及原材质，记录SHA256以供复核。

原模型SHA256：{build['source_sha256']}
本版模型SHA256：{h}

Source包含修改脚本与校验资料。脚本执行：v24_08_build.py → v24_08_verify.py → v24_08_render.py → v24_08_package.py。重建脚本需本机旧版输入文件；交付blend不依赖旧版。
'''
(R/'V24_08_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for f in sorted(O.rglob('*')):
 if not f.is_file()or f.suffix=='.blend1'or f.name.startswith('Draft_')or f.name.endswith('_Draft_States.json')or f.name in['V24_08_Manifest.json','V24_08_Bundle_QA.json']:continue
 files.append({'file':f.relative_to(O).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
(O/'V24_08_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_08_Kitchen_Setback_AsBuilt_Exterior.zip';Z.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for row in files:z.write(O/row['file'],arcname='Rebuild_V24_08/'+row['file'])
 z.write(O/'V24_08_Manifest.json',arcname='Rebuild_V24_08/V24_08_Manifest.json')
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
out={'status':'PASS_BUNDLE_CRC_AND_MODEL_SHA','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_08_Bundle_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
