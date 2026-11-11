"""Deliver the final native Blender scene and current reference/verification evidence."""
import json,hashlib,shutil,zipfile,csv
from pathlib import Path
import numpy as np
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V24_03');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_03.blend'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);build=json.loads((R/'V24_03_Build.json').read_text(encoding='utf8'));qa=json.loads((R/'V24_03_Fresh_Blend_QA.json').read_text(encoding='utf8'));views=json.loads((R/'V24_03_Preview_States.json').read_text(encoding='utf8'))
assert h==build['model_sha256']==qa['model_sha256']==views['model_sha256'];assert qa['status'].startswith('PASS') and not qa['failures'];assert qa['door_roots']==26
for v in views['views']:assert (R/v['file']).stat().st_size>10000
D=W/'v24_03_dimension_audit';reg=json.loads((D/'V24_03_Dimension_Audit.json').read_text(encoding='utf8'));reg['reference_sha256']=sha(Path(reg['reference']));reg['whole_scene_reference_read']=True
(R/'V24_03_Dimension_Audit.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf8')
inventory=json.loads((R/'V24_03_Whole_Site_Inventory.json').read_text(encoding='utf8'));byname={r['name']:r for r in inventory};p=np.load(D/'reference2_LOCAL_points.npz')['p'];rows=[]
groups=[('三层建筑屋顶',['ROOF_MAIN_JOINED_Geometry']),('厨房屋顶',['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry']),('储藏房屋顶',['SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry']),('亭子屋顶',['SITE_GAZEBO_ROOF_Geometry']),('照壁屋顶',['SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL_Geometry']),('内大门屋顶',[r['name'] for r in inventory if r['name'].startswith('V24_XIESHAN_')])]
for label,names in groups:
 bb=np.array([byname[n]['bbox'] for n in names if n in byname]);lo=bb[:,0].min(0);hi=bb[:,1].max(0);sample=p[(p[:,0]>=lo[0]-.3)&(p[:,0]<=hi[0]+.3)&(p[:,1]>=lo[1]-.3)&(p[:,1]<=hi[1]+.3)];rows.append({'group':label,'model_bbox_LOCAL_m':[lo.tolist(),hi.tolist()],'model_width_depth_height_m':(hi-lo).tolist(),'reference_points_in_plan_region':len(sample),'reference_region_top_z_P95_m':float(np.quantile(sample[:,2],.95))if len(sample)else None})
(R/'V24_03_Whole_Site_Dimension_Comparison.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
section=[]
for y in np.arange(-14.,-9.8,.2):
 q=p[(abs(p[:,0]-6.6)<.22)&(abs(p[:,1]-y)<.1)&(p[:,2]>2.5)&(p[:,2]<5.5)]
 if len(q)>20:section.append([round(float(y),2),len(q),*np.quantile(q[:,2],[.1,.5,.9]).tolist()])
with (R/'V24_03_Gate_Scan_Section.csv').open('w',newline='',encoding='utf-8-sig')as f:wr=csv.writer(f);wr.writerow(['LOCAL_Y_m','point_count','Z_P10_m','Z_P50_m','Z_P90_m']);wr.writerows(section)
text='''# V24.03 实景尺寸对照

参考文件为 `E:/jz/实景三维场景模型2.3dm`，只读加载；整场地的三层建筑、厨房、储藏房、亭子、照壁、道路与院墙形态一致。

两版影像重建的坐标和高程不同。通过分布在场地上下文中的9组纹理/顶面特征拟合，再用现有纯场地保留区域进行三维配准。拟合尺度约1.0187；末轮近邻残差约0.32米。矩阵、源文件SHA和迭代记录见同名JSON。该精度用于体量、屋顶剖面复核；接头与门扇以照片、实体网格和运动检查为准。

内大门中部参考剖面的高点集中在LOCAL Y约-12.0至-11.8、Z约4.1至4.4。上一版屋面进深与高度不足；本轮屋顶中心Y=-11.90，普通檐口进深2.60米，主脊顶约4.284米，保持收敛的檐口宽度，重建歇山和层叠承接。

|分区|模型屋顶外接宽×深（米）|模型屋顶最高LOCAL Z|参考区覆盖点数|
|---|---:|---:|---:|
'''
for r in rows:
 a=r['model_width_depth_height_m'];text+=f"|{r['group']}|{a[0]:.3f} × {a[1]:.3f}|{r['model_bbox_LOCAL_m'][1][2]:.3f}|{r['reference_points_in_plan_region']}|\n"
text+='\n参考区点数包括邻接构件，不能直接当作单体净尺寸。完整场地原有对象保留检查见Fresh_Blend_QA；本轮实际修改集中于门楼、厨房后部/柱列和两侧接头。\n'
(R/'V24_03_Dimension_Audit.md').write_text(text,encoding='utf8')
resolved='''# 本轮对照发现并解决的问题

- 厨房后部及屋顶下三角区未封：补闭合灰砖后墙，接墙脚石基。
- 檐廊独立柱列/柱础重复：移除原重复实例，改为一根中部独立木柱，配柱头和斜撑。
- 后端檐梁距新后墙仍约49毫米：梁端延伸并嵌入后墙，消除悬空端头。
- 门楼为两坡浅板、层次不足：重做两主坡、两山花、四面披檐、九脊、连续五级承接及封闭檐底；按参考剖面恢复进深和高度。
- 门楼与厨房穿插：按完整新屋顶作有厚度的实体收口，逐组三角交叉检查归零。
- 左围墙与门柱斜面接头碎口、重复填体：改原墙端部连续回接石柱侧后，保留雕花露面。
- 补厨房后部落水与墙脚排水收口；保留原实景材质、15块浮雕、26扇门动画。

参照：用户220256问题截图、两张厨房目标/实景对照、124258门楼图、DJI_0101/0103及2号实景3dm。
''';(R/'V24_03_Problems_Resolved.md').write_text(resolved,encoding='utf8')
S=O/'Source';T=O/'Textures';F=O/'References'
for folder in [S,T,F]:folder.mkdir(exist_ok=True)
for n in ['v24_03_build.py','v24_03_kitchen_fix.py','v24_xieshan_roof_blender.py','v24_03_junction_blender.py','v24_03_finish_cuts.py','v24_03_finish_intersection.py','v24_03_finish_rear_bearing.py','v24_03_expose_eave_steps.py','v24_03_present.py','v24_03_verify.py','v24_03_render.py','v24_03_package.py','v24_qa_blender.py','v24_relief_blender.py','v24_sculpt_blender.py','v24_register_feature_sweep.py','v24_register_3d_features.py','v24_register_icp.py']:
 shutil.copy2(W/n,S/n)
shutil.copy2('E:/jz/JIA/Rebuild_V24/Source/ImageGen_Prompt.txt',S/'ImageGen_Prompt.txt')
for q in Path('E:/jz/JIA/Rebuild_V24/Textures').iterdir():
 if q.is_file():shutil.copy2(q,T/q.name)
for n in ['DJI_0101.JPG','DJI_0102.JPG','DJI_0103.JPG']:
 shutil.copy2(Path('D:/DJI/0002/DCIM/101MEDIA')/n,F/n)
for src,dest in [('D:/Desktop/屏幕截图 2026-10-16 220256.jpg','Kitchen_Problem_220256.jpg'),('D:/Desktop/dee25fed-2a01-4d56-a898-f44155e0a2aa (1).png','Kitchen_Reference_Color.png'),('D:/Desktop/be5cd059-8a82-4610-9dc1-ee5064ff7e1d.png','Kitchen_Reference_Structure.png'),('D:/Desktop/屏幕截图 2026-10-16 124258.jpg','Gate_Reference_124258.jpg')]:shutil.copy2(src,F/dest)
for n in ['Registration_3D_Seed.json','reference2_top.png','current_site_top.png']:
 shutil.copy2(D/n,R/('Reference_'+n))
files=[P,O/'README_V24_03.txt']+[q for f in [R,S,T,F]for q in f.rglob('*')if q.is_file()and q.suffix not in ['.pyc','.blend1']];assert not any(q.suffix.lower()in ['.3dm','.glb','.fbx']for q in files)
manifest={'version':'V24.03','model':'Blender/'+P.name,'model_sha256':h,'files':[{'path':q.relative_to(O).as_posix(),'bytes':q.stat().st_size,'sha256':sha(q)}for q in sorted(files)]};mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
Z=W.parent/'outputs/Production_1QK_Blender_V24_03_Xieshan_Kitchen.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True)as z:
 for q in files:z.write(q,Path('Rebuild_V24_03')/q.relative_to(O))
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
result={'status':'PASS_FINAL_BLENDER_DELIVERY','model':str(P),'model_sha256':h,'zip':str(Z),'zip_sha256':sha(Z),'zip_bytes':Z.stat().st_size,'files':len(files),'qa_checks':len(qa['checks']),'retained_materials':qa['retained_materials'],'retained_images':qa['retained_images'],'door_roots':26,'crc_verified':True};(O/'Bundle_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
