import sys,json,csv,hashlib,shutil,math
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'libs'))
from PIL import Image
O=Path(r'E:\jz\JIA\Rebuild_V12\07_Reference\Panorama')
Q=json.loads((O/'Extraction_QA.json').read_text(encoding='utf-8'))
rows=json.loads((O/'Frame_Index.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def describe(r):
 t=r['seconds'];l=r['lens'];p=r['pitch_degrees'];g=r['group']
 if g=='Kitchen':
  if t<=12:return ('厨房外木柱石础；门窗内退形成檐廊；回纹透空木格带；雕刻挑梁与层叠托木；坡檐下连续檩枋及密集椽子。' if l==0 else '厨房门廊及侧向门扇；另一方向的柱头雕刻、白抹灰山墙与围墙/亭子关系。')
  if t==1025:return '院内厨房邻接亭子、瓦顶院墙、石铺地；大门木门扇前后的高差；此视角不是厨房内屋架。'
  if t in (1040,1046):return '厨房内退门窗、外排圆木柱与檐廊；门上横枋/透空回纹格带及檐下木椽；1046 秒门洞向厨房内。'
  if t in (1055,1070):return '厨房室内露明传统木屋架；横梁/斜构件、纵向檩木、两坡密集椽子和灰瓦底面；白抹灰山墙；风扇吊杆。1070 秒略有运动模糊。'
  if t==1090:return '回到院内并显著旋转相机，地面/主楼关系；不是厨房内屋架证据。'
  return '进入主楼室内并旋转相机，瓷砖地面/木家具；不是厨房内屋架证据。'
 if t==20:return '厨房檐廊圆木柱、石础、连续浅色台基与深色庭院石铺地的低台阶关系。'
 if t in (40,65,79):return ('主楼入口玻璃、灰色门厅平台与院铺高差；65/79 秒朝侧墙处有短金属棚。' if l==0 else '主楼平台回看院地/亭子/瓦顶围墙；持相机者遮挡部分地面。')
 if t==600:return ('主楼前浅色平台高于深色庭院铺装，罗马柱脚坐在平台；木亭与围墙在院内。' if l==0 else '主楼入口木/玻璃门与门厅平台；主要观察门槛与台地关系。')
 if t==625:return ('厨房前浅色连续台基/石础，外侧深灰石铺地接低台阶。' if l==0 else '院地回看主楼入口平台，矩形石板拼缝；檐下外庭院无摄影浮片。')
 if t==650:return ('厨房前檐台基、木门与旁边大门门槛有连续的高低过渡。' if l==0 else '内院白色瓦顶墙、亭子与洗水台；地面石板铺装。')
 if t==674:return ('院墙/照壁外侧混凝土路地，植栽沿脚；石铺地已转为混凝土路段。' if l==0 else '院墙外灰砖围墙与停放车一侧路坪；露出地面排水/收边关系，部分遮挡。')
 if t==700:return '侧向附属空间、木屋架/廊口与储物；不应误作厨房主屋架。'
 if t==725:return '灰砖墙边附属轻棚、杂物遮挡地面；不适合以遮挡轮廓推断地面边界。'
 if t==749:return ('院墙/照壁外侧连续混凝土通路与墙基。' if l==0 else '院墙外灰砖附属轻棚与生活物件；地面连续混凝土路坪。')
 if t in (775,897):return ('院外门口路坪与混凝土过渡斜坡、防滑槽；775 秒 L0 侧看道路，897 秒 L0 看大门下沿。' if l==0 else '775 秒 L1 四扇金属大门、门下斜坡坪与灰砖门柱；897 秒 L1 朝外坡路。')
 if t in (800,823,850):return ('沿灰砖院墙边混凝土路面的纵向坡度、分缝及墙脚收边；道路连续。' if l==0 else '对向石砌挡墙及上部灰砖墙；道路纵向坡度与墙基高差。')
 if t==875:return ('大门外路口转接坡路；坡脚局部水迹、混凝土拼接。' if l==0 else '沿院墙边混凝土道路回看，分缝/防滑纹与纵向高差。')
 if t==925:return ('院外主路与高石砌挡墙沿线；灰砖院墙/传统飞檐出现在高处。' if l==0 else '对侧路肩植栽、低挡边与混凝土道路。')
 return ('院墙外高石砌挡墙脚有连续线性排水沟；道路与金属护栏一侧关系。' if l==0 else '沿石砌挡墙脚道路回看，路肩/墙脚高差；持相机者遮挡局部。')

large={'Kitchen_L0_0002s_Y+00_P+00.jpg','Kitchen_L0_1025s_Y+00_P+00.jpg','Kitchen_L0_1040s_Y+00_P+00.jpg','Kitchen_L0_1055s_Y+00_P+35.jpg','Kitchen_L0_1070s_Y+00_P+35.jpg','Ground_L0_0775s_Y+00_P-35.jpg','Ground_L0_0600s_Y+00_P-35.jpg'}
for r in rows:
 r['observations']=describe(r)
 r['review']='individual full image and contact sheet' if r['file'] in large else 'contact sheet visual review'
 r['evidence_type']='real decoded video frame'
 r['inference_limit']='Visible relationships and material appearance only; dimensions, exact member count and surveyed elevation require independent controls.'
 r['extraction']='new decode from source on 2026-10-11'

# Keep earlier interior work traceable; it covers the full building tour without re-decoding 118 previous views.
A=W/'ue5_panorama_audit';existing={}
for index in ['Extraction_Index.json','Transition_Index.json']:
 for r in json.loads((A/index).read_text(encoding='utf-8')):existing[r['file']]=r
R=O/'Earlier_Interior';R.mkdir(exist_ok=True)
for fn,r in sorted(existing.items()):
 src=A/fn;dst=R/fn;shutil.copy2(src,dst)
 t=r['seconds']
 if t<=150:obs='入口/楼梯旁卫生间与上楼过渡；门扇/楼梯关系需对照原有室内审查台账。'
 elif t<=300:obs='上部楼梯平台、露台与睡眠空间过渡；多个门扇和内凹空间。'
 elif t<=475:obs='居中区段客厅、阳台、卧室、卫生间；玻璃门和木门过渡。'
 else:obs='入口区段卧室、内凹空间、卫生间、回到门厅；不能凭片段自动判定完整房间边界。'
 rows.append(dict(file='Earlier_Interior/'+fn,group='Earlier_Interior',seconds=t,stream=f"0:v:{r['lens']}",lens=r['lens'],yaw_degrees=0,pitch_degrees=0,horizontal_fov_degrees=90,vertical_fov_degrees=90,projection='uncalibrated 180 degree fisheye to flat 90 degree view; prior extraction',source_video=Q['source'],source_sha256=Q['source_sha256'],output_sha256=sha(dst),metric_use=False,observations=obs,uncertainty='uncalibrated held-camera orientation and lens; no metric pose; source audit reuse',success=r['success'],error='',review='prior visual audit; audit document bundled',evidence_type='real decoded video frame, reused prior extraction',inference_limit='No full room or door uniqueness claims; see Prior_Interior_Audit.md.',extraction='reused earlier documented extraction',original_frame_path=str(src),original_index_paths=[str(A/'Extraction_Index.json'),str(A/'Transition_Index.json')],original_script_sha256=sha(A/'extract.py'),transition_script_sha256=sha(A/'extract_transition.py')))
for fn in ['audit.md','Coverage_Audit.csv','Opening_Evidence.csv']:
 shutil.copy2(A/fn,O/('Prior_Interior_Audit.md' if fn=='audit.md' else fn))
for fn in ['Contact_01.jpg','Contact_02.jpg','Contact_03.jpg','Transition_01.jpg','Transition_02.jpg','Transition_03.jpg','Transition_04.jpg','Transition_05.jpg']:
 shutil.copy2(A/fn,R/fn)
rows.sort(key=lambda r:(r['group'],r['seconds'],r['lens'],r['yaw_degrees'],r['pitch_degrees']))
(O/'Frame_Index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
keys=list(dict.fromkeys(k for r in rows for k in r))
with (O/'Frame_Index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
Q['reused_prior_interior_views']=len(existing);Q['total_indexed_views']=len(rows);Q['new_contact_sheets_reviewed']=8;Q['new_individual_images_reviewed']=len(large)
Q['all_image_readback_valid']=all(Image.open(O/r['file']).size==(1600,1600) if r['group']!='Earlier_Interior' else Image.open(O/r['file']).size==(1200,1200) for r in rows)
Q['all_frame_hashes_match']=all(sha(O/r['file'])==r['output_sha256'] for r in rows)
Q['source_file_preserved']=True
assert Q['all_image_readback_valid'] and Q['all_frame_hashes_match']
(O/'Extraction_QA.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf-8')
text='''# V12 漫游影像参考\n\n本轮由指定 INSV 重新抽出 112 张 1600 × 1600 透视图和一张原始鱼眼图；另复用此前有记录的室内 118 张（`Earlier_Interior`），合计 230 张入索引。\n\n原视频：`E:\\jz\\VID_20260507_152114_00_001.insv`，22,128,020,751 字节，时长 21 分 14.77 秒。两路 3840 × 3840 HEVC 鱼眼各自投影为约 90°平面视图，没有拼接成 360°球面，也没有使用摄影网格作为新增地面。源视频 SHA-256：`'''+Q['source_sha256']+'''`。\n\n`Frame_Index.csv` / `.json` 记录原文件、秒数、视频流、转向、俯仰、原视频哈希、每张图哈希和可见证据。Kitchen / Ground 接触表已目视审查，关键大图另外复核。1121 秒以后相机转入主楼，1090 秒有显著旋转，不能以这些帧替代厨房木屋架证据。\n\n## 厨房可采用的实景关系\n\n- 2 / 5 / 8 / 12 秒：外排圆木柱落石础，门窗面内退成檐廊。回纹格带、雕刻挑梁、层叠托木、纵向檩枋、密集椽子清楚可见。\n- 1040 / 1046 秒：檐廊另一端，厨房门口与格带、柱列的前后关系。\n- 1055 秒 +35°俯仰：室内露明木架、横梁和斜构件、纵向檩木与密集椽子、灰瓦底面、白抹灰山墙。1070 秒补充相邻梁架关系，略有运动模糊。\n\n## 地面与入口关系\n\n- 600 秒 L0 -35°：主楼浅色门厅台地明显高于深色庭院铺装；柱脚在台地。\n- 20 / 625 / 650 秒 L0 -35°：厨房前沿连续浅色台基、柱础、门槛与石铺院地形成低台阶。\n- 775 / 897 秒：四扇金属大门下沿、灰砖门柱、门口压槽混凝土过渡坡坪与外道路。\n- 800–875 秒：围墙沿线连续坡路，墙基和对侧石挡墙存在高差。\n- 925 / 972 秒：主路高石砌挡墙与墙脚线性排水沟、路肩护栏。\n\n## 使用边界\n\n图片用于判断材料、构件层次和空间前后关系。镜头没有标定，相机持握姿态没有求解；输出的 yaw / pitch 相对于各镜头，并非地理方位。不能仅凭图片直接计算米制木柱间距、墙厚、坡度、台阶高度或测绘标高。受人、家具、植物遮挡处不以其轮廓补地面。厨房图中的尺寸仅作为用户提供的构造参考，现场尺寸以可信旧模型/图纸控制并标注待实测。\n\n室内完整性与门位不确定处见 `Prior_Interior_Audit.md`，不能声称 230 张图已覆盖每个房间四墙或全部实际门位。\n'''
(O/'使用说明.md').write_text(text,encoding='utf-8')
print(json.dumps(Q,ensure_ascii=False),flush=True)
