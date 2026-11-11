from pathlib import Path
W=Path(__file__).parent
def converted(name):return (W/('v26_16_'+name+'.py')).read_text('utf8').replace('V26_16','V26_17').replace('v26_16','v26_17').replace('V26.16','V26.17')
for name in['render','views','build_fast','verify_fast','fast_display','physics_qa','window_motion_qa','native_viewport_review']:
 (W/('v26_17_'+name+'.py')).write_text(converted(name),'utf8')
perf=W/'v26_17_perf';perf.mkdir(exist_ok=True)
(perf/'roam_controller_fast.py').write_text((W/'v26_16_perf/roam_controller_fast.py').read_text('utf8').replace('V26.16','V26.17'),'utf8')
build=converted('build').replace('V26_15','V26_16').replace('v26_15','v26_16').replace('V26.15','V26.16')
start=build.index("note=bpy.data.texts.new(");end=build.index("sc['Version']",start)
build=build[:start]+"note=bpy.data.texts.new('V26_17_梁柱板与斜窗节点');note.write('按本次轴线图的3.9+5.2+3.9米开间核对梁柱板。恢复原模型400mm柱、250mm梁的完整节点；十处固定斜窗止于柱前，不再让窗框反切梁柱。中央开启扇、后窗、窗台标高及其他房间保留。窗脚与板边在原标高并合，保留四边阳台及既有阴天流畅显示。柱梁截面沿用原模型定义，非新增现场实测。')\n"+build[end:]
build=build.replace("(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')","assert (D/'Before_Snapshot.json').exists(), 'The frozen source snapshot must exist before building'")
(W/'v26_17_build.py').write_text(build,'utf8')
views=(W/'v26_17_views.py').read_text('utf8')+"\nVIEWS += [('F1_R_Entry_Exterior',(6.2,-1.7,1.3),(9.05,1.96,1.5),31),('F1_R_Outer_Column',(10.7,3.5,1.2),(12.9,1.95,1.9),26),('Front_Facade',(19,-13,8.5),(6.5,1.2,4.2),32)]\n"
(W/'v26_17_views.py').write_text(views,'utf8')
print('ADAPTED_HELPERS',flush=True)
