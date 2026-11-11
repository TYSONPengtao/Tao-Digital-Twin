from pathlib import Path
W=Path(__file__).parent
s=(W/'v15_render_native.py').read_text(encoding='utf8').replace('V15','V16')
a=s.index('cameras=');b=s.index('\nfor name,pos,tar,fov,ortho in cameras:',a)
cameras=[('V16_Native_Whole_Site',[50,-66,42],[-3,-4,2],49,None),('V16_Native_Top',[-1,-3,75],[-1,-3,0],50,64),('V16_Native_Graded_Courtyard',[-22,-5,3.8],[-6,1,-.48],74,None),('V16_Native_Screenwall_Inside',[10.5,-14.8,1.0],[3,-16.35,-.05],74,None),('V16_Native_West_Wall_Drain',[-19.3,-9.3,.30],[-21.6,-4.2,-.85],71,None),('V16_Native_South_Wall_Drain',[-3.8,-19.2,-.6],[6,-17.2,-2.1],73,None),('V16_Native_Outer_Storage_Base',[24.5,-18.8,-1.5],[20.2,-15.5,-2.35],65,None),('V16_Native_Entry_Route',[-10,-11.22,1.3],[6.6,-11.95,1.0],63,None)]
s=s[:a]+'cameras='+repr(cameras)+s[b:]
s=s.replace("('SITE_V12_REBUILT_EARTH','SITE_V12_REBUILT_ROAD','SITE_V14_ORIGINAL_EXTERIOR')","('SITE_V12_REBUILT_EARTH','SITE_V16_GRADED_INTERIOR_SOIL','SITE_V12_REBUILT_ROAD','SITE_V14_ORIGINAL_EXTERIOR')")
s=s.replace("sc.cycles.samples=12","sc.cycles.samples=16")
s=s.replace("Fresh V16 native 3DM readback; retained geometry verified against V14 native kernel meshes","Fresh V16 native Mesh readback; unchanged Brep/block geometry verified against V15 by full native hash")
s=s.replace("for i,p in enumerate([[5.4,6.80,9.4]","for i,p in enumerate([[5.4,6.80,9.4]")
(W/'v16_render_native.py').write_text(s,encoding='utf8')
print('V16 renderer ready',len(cameras))
