import json,hashlib,shutil,zipfile,sys
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_21';O=Path('E:/jz/JIA/Rebuild_V24_21');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_21.blend'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);build=read(R/'V24_21_Build.json');native=read(R/'V24_21_Native_QA.json');physics=read(R/'V24_21_Physics_QA.json');solid=read(R/'V24_21_Exterior_Solid_QA.json')
assert h==build['sha256']==native['model_sha256']==physics['model_sha256']==solid['model_sha256']
assert sha(build['source'])==build['source_sha256']=='78fb5a309e2be158557fb6f129cd87ed1b403f0a0d59ce39e9223a195794329a'
for qa in [native,physics,solid]:assert qa['status'].startswith('PASS')and not qa['failures']
cmd='''@echo off
chcp 65001 >nul
setlocal
set "ROAM_BLENDER_EXE=D:\\AJAVIS01\\RHINO7.12\\PLUGINS\\BLENDER\\RUNING\\blender.exe"
if not exist "%ROAM_BLENDER_EXE%" set "ROAM_BLENDER_EXE="
if not defined ROAM_BLENDER_EXE for /f "delims=" %%B in ('where blender.exe 2^>nul') do if not defined ROAM_BLENDER_EXE set "ROAM_BLENDER_EXE=%%B"
if not defined ROAM_BLENDER_EXE (
  echo 找不到 Blender。请修改本启动文件中的 Blender 路径。
  pause
  exit /b 1
)
start "" "%ROAM_BLENDER_EXE%" --factory-startup "%~dp0Blender\\Architecture_Complete_V24_21.blend" --python "%~dp0Roam\\start_roam.py"
'''
(O/'启动漫游.cmd').write_text(cmd,encoding='utf8',newline='\r\n')
S=O/'Source';S.mkdir(exist_ok=True)
for n in ['v24_21_probe.py','v24_21_details.py','v24_21_build.py','v24_21_roam_physics.py','v24_21_roam_controller.py','v24_21_start_roam.py','v24_21_physics_qa.py','v24_21_ui_smoke.py','v24_21_launcher_smoke.py','v24_21_verify.py','v24_21_details_qa.py','v24_21_render.py','v24_21_package.py','v24_16_common.py','v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,S/n)
for folder,names in [('v24_21',['Source.json','Inventory.json','Prepared_Geometry.json','Before_Snapshot.json','Saved_Detail_Index.json']),('v24_16',['Inventory.json']),('v19',['Facade_Segments.json'])]:
 target=S/folder;target.mkdir(exist_ok=True)
 for n in names:shutil.copy2(W/folder/n,target/n)
for p in D.glob('DETAIL_*.npz'):shutil.copy2(p,S/'v24_21'/p.name)
refs=O/'References';refs.mkdir(exist_ok=True);ref=Path('D:/Desktop/屏幕截图 2026-10-19 025022.jpg');shutil.copy2(ref,refs/ref.name);(refs/'Reference_Index.json').write_text(json.dumps({'source':str(ref),'sha256':sha(ref),'use':'Exterior white frieze, long/short stepped outlines, cornice courses; reference image unchanged.'},ensure_ascii=False,indent=2))
note=f'''# V24.21 建筑人物漫游与完整外墙装饰

双击本目录的 **启动漫游.cmd**，等待 Blender 打开并显示“1.65m 漫游人物”提示后，即可操作。启动文件明确加载控制器，并进入专用三维画面，隐藏时间轴。默认是人物第三人称跟随视角。人物站立身高 **1.65m**，人眼视角高度 **1.53m**。

**请通过启动漫游.cmd进入。** 直接打开blend不会自动恢复上一回的漫游运行状态；出现“此方向再无可供跳转的关键帧”说明还在普通建模/动画操作中。F8只在控制器已经加载后有效。此时使用启动文件，或按下文在文本编辑器运行内嵌启动脚本。

| 操作 | 功能 |
| --- | --- |
| ↑ / ↓ | 沿视线前进 / 后退 |
| ← / → | 向左 / 向右移动 |
| WASD | 同方向键 |
| 空格 | 跳跃，重力下落并落地 |
| Shift | 快走 |
| 鼠标右键拖动 | 转向及上下观察 |
| 鼠标滚轮 | 调整第三人称跟随距离 |
| V | 切换第三人称 / 人眼视角 |
| M | 切换带贴图的材质预览 / 流畅显示 |
| Home | 返回院落起点 |
| Esc | 退出漫游，恢复普通建模操作 |
| F8 | 再次开始漫游；也可点画面顶部“进入人物漫游” |

在 N 侧栏的“建筑漫游”页，可开始漫游、调整跟随距离，或直接选择院落、一楼、二楼、三楼。视角朝向决定方向键的前进方向；先用鼠标右键转向，再走楼梯。漫游时原门窗采用第40帧的打开状态，原26扇门和12扇外开窗的动画保留。

## 上下楼梯与人物碰撞

人物使用1.65m高、0.215m半径的胶囊碰撞，按实际建筑三角面行走。可连续沿一楼至三楼的两跑楼梯上下；重力、踏步抬升、墙体阻挡、门洞通过、跳跃落地与跟随相机避墙均已测试。默认行走速度1.85m/s，快走3.10m/s，平地跳跃约0.59m。建筑、地面和栏杆参与碰撞。Home可随时返回院落。

首次启动漫游会准备碰撞数据和视窗材质。显示较慢时按M切换流畅显示；模型几何保持完整。

## 外墙照片中的细节

按025022实景补齐外院围墙的连续白色装饰带、长短相间的阶角双框线、下口线脚和上部叠涩檐口。装饰是有厚度的可编辑网格，共98组长短框，沿既有墙体曲线和高差连续布置；原瓦当、瓦顶和特殊照壁保留。

V24.20的所有原对象、原材质、贴图、门窗动作和建筑位置均保留。本版新增人物、跟随摄像机、外墙装饰和隐藏的漫游碰撞数据；原V24.20文件未覆盖。外墙细部尺寸按照片与既有模型拟合。

## 文件与核验

- Blender/Architecture_Complete_V24_21.blend：完整可编辑场景，图片与漫游脚本内嵌。
- 启动漫游.cmd：本机一键启动，不需安装额外游戏引擎。
- Roam/start_roam.py：由启动文件明确运行内嵌控制器，不改全局脚本信任设置。
- Reports：外墙近景、人物预览、实际运行视窗，以及核验报告。
- Source：本轮建模、控制、核验脚本与外墙几何数据；重建需原V24.20及相应Python几何环境。漫游运行只需Blender。

直接打开blend后，也可在Blender文本编辑器选择 **V24_21_启动漫游.py**，按Alt+P执行，再使用F8或N侧栏按钮。

本机启动文件使用已验证的Blender路径。迁移到其他电脑后，可修改启动文件中的Blender路径，或把blender.exe加入PATH。

保存后重新打开核验{len(native['checks'])}项；实际模型运动核验{len(physics['checks'])}项；外墙装饰闭合实体核验{len(solid['checks'])}项，均通过。实际视窗另测试方向键、空格、V、M、Home和Esc，报告为V24_21_UI_Smoke_QA.json。专用启动入口另通过8项实际按键核验，覆盖方向键不再跳关键帧、V双向切换、Esc退出和F8恢复，报告为V24_21_Launcher_QA.json。

模型SHA256：{h}
'''
(O/'README_漫游使用说明.md').write_text(note,encoding='utf8')
if '--stage'in sys.argv:print('V21_STAGED',h,flush=True);sys.exit(0)
ui=read(R/'V24_21_UI_Smoke_QA.json');assert ui['status'].startswith('PASS')and not ui['errors']and not ui['failures']and ui['model_sha256']==h
launcher=read(R/'V24_21_Launcher_QA.json');assert launcher['status']=='PASS_REAL_LAUNCHER_ENTRY'and not launcher['errors']and not launcher['failures']and launcher['model_sha256']==h and launcher['bootstrap_sha256']==sha(O/'Roam/start_roam.py')
states=[]
for p in sorted(R.glob('V24_21_*_State.json')):
 s=read(p);assert s['model_sha256']==h;assert not s.get('draft',False);s['image_sha256']=sha(R/s['file']);states.append(s)
assert len(states)==6,len(states)
(R/'V24_21_Preview_Index.json').write_text(json.dumps({'model_sha256':h,'views':states},ensure_ascii=False,indent=2))
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or p.name in ['V24_21_Manifest.json','V24_21_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
manifest=O/'V24_21_Manifest.json';manifest.write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2));Z=W.parent/'outputs/Production_1QK_Blender_V24_21_165cm_Roam_Exterior_Detail.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_21/'+r['file'])
 z.write(manifest,'Rebuild_V24_21/V24_21_Manifest.json')
print('V21_ZIP_WRITTEN',Z.stat().st_size,flush=True)
with zipfile.ZipFile(Z)as z:
 assert z.testzip()is None
 for r in files:
  with z.open('Rebuild_V24_21/'+r['file'])as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256'],r['file']
out={'status':'PASS_ZIP_CRC_AND_ALL_HASHES','zip':str(Z),'model_sha256':h,'sha256':sha(Z),'files':len(files)+1,'bytes':Z.stat().st_size};(O/'V24_21_Bundle_QA.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
