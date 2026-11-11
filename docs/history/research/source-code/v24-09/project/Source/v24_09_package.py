import json,shutil,hashlib,zipfile
from pathlib import Path
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V24_09');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_09.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
qa=json.loads((R/'V24_09_Fresh_Blend_QA.json').read_text());view=json.loads((R/'V24_09_Preview_States.json').read_text());build=json.loads((R/'V24_09_Build.json').read_text());roof=json.loads((R/'V24_09_Forked_Roof.json').read_text());fac=json.loads((R/'V24_09_Facade_and_Soffit.json').read_text());h=sha(P)
assert qa['status'].startswith('PASS')and not qa['failures']and qa['model_sha256']==view['model_sha256']==build['sha256']==h
assert len(view['views'])==6 and all((R/v['file']).is_file()for v in view['views'])
for n in['v24_09_common.py','v24_09_build.py','v24_09_roof.py','v24_09_facade.py','v24_09_verify.py','v24_09_render.py','v24_09_package.py','v24_06_common.py','v24_03_junction_blender.py','v24_qa_blender.py']:shutil.copy2(W/n,O/'Source'/n)
for f in['v12_screenwall_reference/Mutation.json','v19/Facade_Segments.json']:
 dst=O/'Source'/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/f,dst)
refs=[('D:/Desktop/问题/屏幕截图 2026-10-11 110121.jpg','01_Real_Screenwall_Underside.jpg'),('D:/Desktop/问题/屏幕截图 2026-10-11 101424.jpg','02_Real_Screenwall_Outside.jpg'),('D:/Desktop/问题/屏幕截图 2026-10-11 101327.jpg','03_Real_Screenwall_Inside.jpg'),('D:/DJI/0003/DCIM/101MEDIA/DJI_0086.JPG','04_Real_Screenwall_Roof.JPG'),('D:/Desktop/屏幕截图 2026-10-17 135801.jpg','05_Real_Bifurcating_Ridge_Plan.jpg')]
for src,n in refs:
 assert Path(src).is_file(),src
 shutil.copy2(src,O/'References'/n)
for n in['V24_08_Fresh_Blend_QA.json','V24_08_Kitchen_Setback.json']:shutil.copy2(Path('E:/jz/JIA/Rebuild_V24_08/Reports')/n,O/'Source'/n)
note=f'''# V24.09 照壁分叉瓦顶与底部结构

完整模型：Blender/Architecture_Complete_V24_09.blend，米制，贴图已内嵌，完整场地保留。默认40帧开门，1帧关闭，20帧半开。V24.08旧版保留。

按135801俯视图：长脊在两端墙端处分成前后两条斜脊，共四条分叉脊、四个翘角。替换原端部中央的独立锥形脊饰；分叉不是在原直脊上叠两根装饰杆，端部基底与瓦面也同步改成短向端坡。两端横向瓦排随分叉边界转向，形成真实扇铺关系。四条分叉脊均有闭合梯形脊座嵌入屋面，中央镂空脊带也有连续实体承座；避免曲线盖脊悬空在瓦面上。原瓦顶平面X2.950—11.100、Y−17.640—−16.160保留，长脊分叉点X3.250、10.800与墙端对应。

长坡50条瓦垄，{roof['long_cover_tile_units']}块有厚度的筒瓦，另有{roof['hip_fan_cover_tile_units']}块端坡筒瓦及板瓦。脊带有52格真实镂空菱格与隔格小圆环；100个莲花瓦当沿用原有八瓣实体模板，配合新的瓦垄位置。四个翘角末端为连续收尖陶质构件，与分叉脊相接。

按110121仰视图：底部为一个闭合的连续曲面承托，三道薄叠涩线脚及闭合封檐随屋面起伏；不再由互相拼接的矩形框条承担可见底面。端部各补一块白色框内芯及灰色边框。内外两面均有七组长短相间的框饰，顺着曲线墙头布置，上缘有克制的三角纹带。

外侧沿用实景灰砖、深色条石和毛石墙基；内侧白灰墙使用用户101327实景照片作原生网格投影UV，保留真实斑驳、裂纹和底部潮痕。JPEG原字节已内嵌，无位图裁切、修图或重绘。照片SHA256：{fac['plaster']['source_unmodified_sha256']}。原UV通道保留，贴图通过显式新增UV通道使用；其他围墙白墙材质槽保持。瓦件有五档低幅灰色差异及细微粗糙度，线脚与框芯有克制的灰白表面变化。

照壁墙体XY、下部墙基和外围场地位置保持。两端屋面转折只在墙外的短端坡内完成；墙冠按同一曲面复核。厨房0.450m退让、内大门最低檐底3.100m、原细化门板和铜把手、15块石浮雕、26扇门动作、院墙中线及铺地继续保留。

此版为依据现有注册场地与用户照片的细化模型，瓦件数量、脊饰与线脚尺寸属于照片拟合，不作为现场实测尺寸。

保存后重新打开校验{len(qa['checks'])}项，失败0项。原{qa['original_materials']}套材质、{qa['original_images']}张图像及26扇门动作保留；新的照壁构件均封闭、无非流形边且体积为正。实际射线逐格穿过52个菱格开口；四角脊饰和两个真实分叉节点、原屋面平面、墙体下部位置均复核。六张彩色预览来自同一最终模型，包含外侧、内侧、分叉俯视、斜俯视、檐底仰视、全场地。

本版模型SHA256：{h}
输入V24.08模型SHA256：{build['source_sha256']}

Source包含构造与校验脚本，瓦当模板及已注册墙线数据。重建顺序：v24_09_build.py → v24_09_verify.py → v24_09_render.py → v24_09_package.py。重建需本机保留的V24.08；交付blend本身独立完整。
'''
(R/'V24_09_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for f in sorted(O.rglob('*')):
 if not f.is_file()or f.suffix=='.blend1'or f.name.startswith('Draft_')or f.name.endswith('_Draft_States.json')or f.name in['V24_09_Manifest.json','V24_09_Bundle_QA.json']:continue
 files.append({'file':f.relative_to(O).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
(O/'V24_09_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_09_Screenwall_Forked_Roof_Curved_Soffit.zip';Z.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for row in files:z.write(O/row['file'],arcname='Rebuild_V24_09/'+row['file'])
 z.write(O/'V24_09_Manifest.json',arcname='Rebuild_V24_09/V24_09_Manifest.json')
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
out={'status':'PASS_BUNDLE_CRC_AND_MODEL_SHA','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_09_Bundle_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
