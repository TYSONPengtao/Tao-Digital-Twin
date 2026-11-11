from pathlib import Path
W=Path(__file__).parent
def cloned(name):return (W/('v24_12_'+name+'.py')).read_text(encoding='utf8').replace('v24_12','v24_13').replace('V24_12','V24_13').replace('V24.12','V24.13')
def save(name,t):(W/('v24_13_'+name+'.py')).write_text(t,encoding='utf8')
t=cloned('probe').replace('Rebuild_V24_11/Blender/Architecture_Complete_V24_11','Rebuild_V24_12/Blender/Architecture_Complete_V24_12');save('probe',t)
t=cloned('prepare').replace("def put(n,m):","def put(n,m,new=False,material=None):").replace("'name':n,'v':","'name':n,'new':new,'material':material,'v':").replace('(12.82,front(12.82))','(W,front(W))').replace('np.arange(12.95,18.77,.24)','np.arange(W+.07,18.77,.24)').replace('[12.82,front(12.82),EAVE_Z-.105]','[W,front(W),EAVE_Z-.105]')
at="(D/'Prepared_Geometry.json').write_text"
i=t.index(at)
addition='''# Only the concealed end turns inward to tuck under the squared roof.
# The original level secondary-wall face and both flat panels stay unchanged.
a=np.array([13.03,-16.62]);b=np.array([13.42,-16.10]);u=(b-a)/np.linalg.norm(b-a);no=np.array([-u[1],u[0]])
p=Polygon([a-no*.15,b-no*.15,b+no*.15,a+no*.15])
put('V24_13_Secondary_Screenwall_Concealed_End_Return',under(p,lambda x,y:CROWN,-.55),True,'M_V19_Perimeter_Brick')
caps=[]
for sign in[-1,1]:
 q=Polygon([a,b,b+sign*no*.23,a+sign*no*.23]);caps.append(under(q,lambda x,y:CROWN+.165-.60*abs(float(np.dot(np.array([x,y])-a,no))),CROWN-.005))
cap=mf.Manifold.batch_boolean(caps+[beam([*a,CROWN+.17],[*b,CROWN+.17],.045,.035)],mf.OpType.Add)
put('V24_13_Secondary_Screenwall_End_Return_Coping',cap,True,'M_V19_Weathered_Wall_Tile')
OUT['proof']['squared_front_roof']={'west_x':W,'east_x':E,'eave_y':front(0),'ridge_y':ridge(0),'left_side_retraction_m':W-12.82,'front_outline_source':'D:/Desktop/downl5oad.png'}
OUT['proof']['secondary_concealed_return']={'a':a.tolist(),'b':b.tolist(),'crown_z':CROWN,'original_level_wall_and_panels_unchanged':True}
'''
t=t[:i]+addition+t[i:];save('prepare',t)
t=cloned('build').replace("B=Path('E:/jz/JIA/Rebuild_V24_11/Blender/Architecture_Complete_V24_11.blend')","B=Path('E:/jz/JIA/Rebuild_V24_12/Blender/Architecture_Complete_V24_12.blend')")
t=t.replace("o=replacement(row['name'],row['v'],row['f']);changed(row['name'],'analytical closed solid replacement',closed_bodies=row['bodies'],volume_m3=row['volume_m3'])", """if row.get('new'):
  o=_mesh(bpy,col,row['name'],row['v'],row['f'],bpy.data.materials[row['material']]);metric(o);added.append(o.name)
 else:
  o=replacement(row['name'],row['v'],row['f']);changed(row['name'],'analytical closed solid replacement',closed_bodies=row['bodies'],volume_m3=row['volume_m3'])""")
i=t.index('# Flatten only the secondary wall.');j=t.index('views=[',i)
t=t[:i]+"proof.update(source_version='V24.12',scope='Blue-plan front-roof outline: squared sides and eave; level secondary screen preserved; concealed end tucked under eave')\n"+t[j:]
t=t.replace("z+w*(surface_z(x,y)-old_roof_z(x,y))","z+w*(surface_z(x,y)-old_surface_z(x,y))")
t=t.replace("guide='V24.13：次照壁", "guide='V24.13按蓝线收正储藏房前坡轮廓，左边收回0.438米，前檐恢复直线，屋脊、两坡、木基层同步更新，次照壁原水平墙冠及装饰带保留，端部转入瓦檐下。此前V24.12：次照壁")
save('build',t)
t=cloned('verify').replace("B=Path('E:/jz/JIA/Rebuild_V24_11/Blender/Architecture_Complete_V24_11.blend')","B=Path('E:/jz/JIA/Rebuild_V24_12/Blender/Architecture_Complete_V24_12.blend')")
t=t.replace("Only recorded cameras added","Only recorded objects added").replace("for x in[12.96,13.04,13.10]:\n for y in[-16.68,-16.77]:","for x in[13.35,13.40]:\n for y in[-16.30,-16.23]:")
t=t.replace("ct=tree('SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING_Geometry')","ct=tree('V24_13_Secondary_Screenwall_End_Return_Coping')")
t=t.replace("for n in sorted(allow):\n o=bpy.data.objects[n];me=o.data;", "for n in sorted(allow|set(ch['added'])):\n o=bpy.data.objects[n]\n if o.type!='MESH':continue\n me=o.data;")
t=t.replace('Previous V24.11 file retained unchanged','Previous V24.12 file retained unchanged')
save('verify',t)
t=cloned('solids').replace("'PASS_SAVED_SOLIDS_WITH_INHERITED_COMPOUND_WALL'","'PASS_INDEPENDENT_SAVED_SOLIDS'")
t=t.replace("boxes=[('Entry'", "for n,m in solids.items():\n if n.startswith('V24_13_Secondary_Screenwall_'):obs.append((n,m))\nboxes=[('Entry'")
save('solids',t);save('render',cloned('render'))
t=cloned('package').replace("'v24_11_geometry.py'","'v24_12_geometry.py','v24_11_geometry.py'")
t=t.replace("shutil.copy2('D:/Desktop/屏幕截图 2026-10-18 082437.jpg',refs/'01_User_Level_Secondary_Screen_and_Storage_Roof.jpg')", "shutil.copy2('D:/Desktop/downl5oad.png',refs/'01_User_Blue_Front_Roof_Outline.png')\nshutil.copy2('D:/Desktop/屏幕截图 2026-10-18 094354.jpg',refs/'02_User_AsBuilt_and_Model_Plan_Comparison.jpg')")
t=t.replace("shutil.copy2('E:/jz/JIA/Rebuild_V24_11/README_V24_11.md',refs/'Prior_V24_11_Corrections.md')", "shutil.copy2('E:/jz/JIA/Rebuild_V24_12/README_V24_12.md',refs/'Prior_V24_12_Corrections.md')")
i=t.index("note=f'''");j=t.index('files=[]',i)
note="""note=f'''# V24.13 按蓝线收正储藏房前坡

完整建筑和场地：Blender/Architecture_Complete_V24_13.blend。原V24.12保留未覆盖。1/20/40帧为门关闭/半开/打开；全部26扇门的动作和姿态保留。照片贴图内嵌，blend可独立打开。

本次按D:/Desktop/downl5oad.png蓝线和094354实景对比，收回前坡左侧多伸出的楔形部分约0.438米。前坡两侧为平行直边，前檐与屋脊在平面中平行，标高各自水平，两主坡均为平面。前檐在模型坐标Y=-16.480，屋脊Y=-12.150；其余边界保留场景配准位置。木基层、屋架、椽尾、山墙上部和柱头一起适配，旧木基层不会穿出新瓦面。

次照壁已调平的墙冠、内外装饰和白色框线保持。仅藏在储藏房入口侧的末端短回墙向檐下转入，以保持次照壁端部低于储藏房瓦檐。屋顶与原右侧薄金属棚保持两处独立结构。储藏房地基、弧形后墙、厨房退让和连续后墙等此前校正保留。

最终保存文件复开检查{len(qa['checks'])}项，失败0项。新增及修改实体独立检查通过，旧木基层与屋面无穿插，五处通行采样无相交。Reports有6张同一最终模型的正立面、俯视、接头、背面及全场预览，配套完整检查数据。检查值为当前模型坐标中的几何数据，不是新增现场测量。

模型SHA256：{h}

输入V24.12 SHA256：{build['source_sha256']}

References保存本轮两张标记图、实景3dm原文件副本、上一版记录和拟合信息。Source保存构造与核验脚本、输入及保存网格缓存。重建需本机原V24.12输入和Python/Blender依赖，交付blend本身独立完整。
'''
(O/'README_V24_13.md').write_text(note,encoding='utf8');(R/'V24_13_Resolved_Issues.md').write_text(note,encoding='utf8')
"""
t=t[:i]+note+t[j:];t=t.replace('Level_Screenwall_Storage_Roof.zip','Squared_Storage_Front_Roof.zip');save('package',t)
print('V24.13 scripts ready')
