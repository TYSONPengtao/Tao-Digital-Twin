from pathlib import Path
W=Path(__file__).parent
for name in['build','build_fast','fast_display','verify_fast','physics_qa']:
 s=(W/('v26_17_'+name+'.py')).read_text('utf8').replace('v26_17','v26_18').replace('V26_17','V26_18').replace('V26.17','V26.18')
 if name=='build':
  s=s.replace('v26_16','v26_17').replace('V26_16','V26_17').replace('V26.16','V26.17')
  lines=s.splitlines();lines=[("note=bpy.data.texts.new('V26_18_楼梯板底与内门后收口');note.write('清理旧楼梯连接片向楼板底部突出的65mm错台，顺接原斜板底与楼板底；同类二至三楼接缝同步检查修正。两处半层平台侧面使用原白墙材质，踏步石材保持。归档移除内大门后固定红色装饰板，保留活动门扇与前部雕刻石柱。踏步、楼板、窗台标高和阴天柔光保持。')"if x.startswith('note=bpy.data.texts.new(')else x)for x in lines];s='\n'.join(lines)+'\n';s=s.replace('V26_18_Continuous_Front_Window_Jamb_Nodes','V26_18_Stair_Soffit_And_Gate_Rear')
 (W/('v26_18_'+name+'.py')).write_text(s,'utf8')
perf=W/'v26_18_perf';perf.mkdir(exist_ok=True);(perf/'roam_controller_fast.py').write_text((W/'v26_17_perf/roam_controller_fast.py').read_text('utf8').replace('V26.17','V26.18'),'utf8')
print('HELPERS_CREATED')
