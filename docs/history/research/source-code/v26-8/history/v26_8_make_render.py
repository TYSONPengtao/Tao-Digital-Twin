from pathlib import Path
import json,sys
W=Path(__file__).parent;sys.path.insert(0,str(W))
s=(W/'v26_7_render.py').read_text('utf8').replace('v26_7','v26_8').replace("ver='V26_6'if before else'V26_7'", "ver='V26_7'if before else'V26_8'")
a=s.index(" ld=bpy.data.lights.new('Temporary_review_fill'");b=s.index(" fn=",a);s=s[:a]+s[b:];s=s.replace("'temporary_review_fill_watts':75", "'temporary_review_fill_watts':0").replace(";bpy.data.objects.remove(light,do_unlink=True)", "")
s=s.replace("sc.cycles.samples=24", "sc.cycles.samples=32").replace("sc.view_settings.view_transform='AgX';", "sc.view_settings.view_transform='AgX';")
(W/'v26_8_render.py').write_text(s,'utf8')
views=[
('01_F1_Thin_Door_Jamb',(6.7,-.9,1.25),(9.12,2.03,1.30),30),
('02_F2_Window_Sill_Stone_Rail',(6.5,-4.,4.9),(6.5,1.8,4.45),25),
('03_F1_Low_Sill',(5.4,-3.0,.7),(2.,1.25,-.1),30),
('04_F3_Window_Sill_Inside',(10.6,4.1,8.6),(10.9,1.1,8.45),22),
('05_F1_Step_To_Wall',(6.45,8.95,1.65),(6.2,9.65,.85),24),
('06_F1_Open_Well',(8.25,8.55,2.75),(6.2,8.55,.85),23),
('07_F2_Open_Well',(8.3,8.55,6.1),(5.7,8.55,4.45),23),
('08_Half_Landing_Turn',(4.45,7.85,3.0),(5.0,8.55,2.4),28),
('09_Upper_Turn',(8.65,7.7,5.15),(7.8,8.55,4.45),28),
('10_F3_Guard_And_Well',(8.65,8.5,8.5),(7.6,8.7,7.75),24),
('11_Overcast_Exterior',(23.,-25.,11.),(6.,3.,4.2),35),
('12_Overcast_Interior',(6.6,6.5,1.2),(6.6,1.8,1.1),24),
]
(W/'v26_8_views.py').write_text('VIEWS='+repr(views)+'\n','utf8')
print('RENDER_SCRIPT_READY')
