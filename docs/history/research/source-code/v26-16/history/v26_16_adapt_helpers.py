from pathlib import Path
W=Path(__file__).parent;D=W/'v26_16_perf';D.mkdir(exist_ok=True)
for name in['build_fast','verify_fast','fast_display','physics_qa']:
 (W/('v26_16_'+name+'.py')).write_text((W/('v26_15_'+name+'.py')).read_text('utf8').replace('V26_15','V26_16').replace('v26_15','v26_16').replace('V26.15','V26.16'),'utf8')
(D/'roam_controller_fast.py').write_text(Path('E:/jz/JIA/Rebuild_V26_15/Roam/roam_controller_fast.py').read_text('utf8').replace('V26.15','V26.16').replace('Rebuild_V26_15','Rebuild_V26_16'),'utf8')
s=(W/'v26_15_build.py').read_text('utf8').replace('V26_15','__NEW__').replace('v26_15','__new__').replace('V26.15','__newdot__').replace('V26_14','V26_15').replace('V26.14','V26.15').replace('__NEW__','V26_16').replace('__new__','v26_16').replace('__newdot__','V26.16');start=s.index("note=bpy.data.texts.new(");end=s.index("sc['Version']",start)
s=s[:start]+"note=bpy.data.texts.new('V26_16_窗边收口修正');note.write('五组前房间内侧窗边节点：局部替换破碎梁头、窄墙边与窗台收口，保留200mm窗下墙和240mm房间隔墙；按原黑框端面留0.4mm收口，清除横档及窗台附近多余白块。窗顶水平面统一使用原顶面材质，避免三角暗斑。原窗框、玻璃、开启扇动作、窗台高度、其他房间和V26.15已修正部位保持。尺寸为模型拟合，非新现场测量。')\n"+s[end:]
s=s.replace('V26_16_Four_Local_Geometry_Joins','V26_16_Continuous_Front_Window_Jamb_Nodes');(W/'v26_16_build.py').write_text(s,'utf8')
