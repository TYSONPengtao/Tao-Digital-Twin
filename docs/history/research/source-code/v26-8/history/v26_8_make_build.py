from pathlib import Path
import json,shutil
W=Path(__file__).parent;D=W/'v26_8'
s=(W/'v26_7_build.py').read_text('utf8').replace('v26_7','v26_8').replace('V26_7','V26_8').replace('Rebuild_V26_6','Rebuild_V26_7').replace('Architecture_Complete_V26_6.blend','Architecture_Complete_V26_7.blend').replace('ea7cd20cb3c30cf2b5984c1e262ca182fa3c168a8a16fd7201ef428267bf05b7','ae36eb7abde8241465d4d6707fa19c8a9ccd74aaebc025565f2843ee9be5711e').replace('V26_6_Collision_Index.json','V26_7_Collision_Index.json')
a=s.index("sys.path.insert(0,str(W/'v26_8_site_audit'))");b=s.index('# Collision cache',a)
s=s[:a]+"archived=prep.get('remove',[])\nfor n in archived:\n o=bpy.data.objects[n];o.hide_render=True;o.hide_set(True);changed.append(n)\n"+s[b:]
s=s.replace('need=set(geom);vv=[]','need=set(geom);vv=[]').replace("if r['name']in need:continue", "if r['name']in need or r['name']in archived:continue")
s=s.replace("'archived':[]", "'archived':archived")
s=s.replace("'geometry_changed':geom", "'geometry_changed':geom")
s=s.replace("t.write('按实景", "t.write('楼梯井按实景留空、梯段贴墙，三层前湾窗误加铁栏移除；一楼台30cm、上层等高石栏；按用户要求阴天柔光。前版已按实景")
lighting='''
# The user asked for overcast, soft and even display lighting.
world=bpy.data.worlds.new('V26_8_Overcast_Soft_Even_Daylight');world.use_nodes=True
ns=world.node_tree.nodes;ns.clear();bg=ns.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.78,.79,.80,1.);bg.inputs['Strength'].default_value=.75;out=ns.new('ShaderNodeOutputWorld');world.node_tree.links.new(bg.outputs['Background'],out.inputs['Surface']);sc.world=world
light_rows=[]
for o in list(sc.objects):
 if o.type!='LIGHT':continue
 changed.append(o.name);prior=o.data.energy
 if o.data.type=='SUN':o.data.energy=0.;o.data.angle=1.2
 elif o.data.type=='POINT':o.data.energy=min(o.data.energy,100.);o.data.shadow_soft_size=1.4
 elif o.data.type=='AREA':o.data.size=max(getattr(o.data,'size',1.),2.5)
 light_rows.append({'object':o.name,'type':o.data.type,'before_energy':prior,'after_energy':o.data.energy})
for fl,z in[(1,-.45),(2,3.45),(3,7.05)]:
 for part,x,y in[('left',2.,5.),('hall',6.5,5.),('right',11.,5.),('stair',6.,8.5)]:
  ld=bpy.data.lights.new(f'V26_8_Overcast_Interior_F{fl}_{part}','AREA');ld.energy=90 if part!='stair'else 55;ld.shape='DISK';ld.size=2.8
  ob=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(ob);ob.location=(x,y,z+2.82);added.append(ob.name);changed.append(ob.name)
sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.preview_samples=16
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium Low Contrast';sc.view_settings.exposure=0.;sc.view_settings.gamma=1.
spaces=0
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type!='VIEW_3D':continue
  shade=ar.spaces.active.shading;shade.type='MATERIAL';shade.use_scene_world=True;shade.use_scene_lights=True;shade.studiolight_background_alpha=1.;shade.studiolight_background_blur=1.;spaces+=1
write('V26_8_Overcast_Lighting_Setup.json',{'world':world.name,'uniform_neutral_ambient_strength':.75,'direct_sun_energy':0,'light_changes':light_rows,'soft_interior_area_lights':12,'area_diameter_m':2.8,'material_preview_scene_world':True,'material_preview_scene_lights':True,'configured_spaces':spaces,'color_transform':'AgX - Medium Low Contrast','lighting_is_user_display_preference_not_measured_site_light':True})
'''
s=s.replace("sc['Version']=",lighting+"\nsc['Version']=")
# Text written by the previous build is context only; the new detailed notes
# and QA refer to actual V26.8 changes and the current source file.
s=s.replace("'V26_8_Photo_Referenced_Wall_Column_Railing_Gate_And_Site_Repairs'", "'V26_8_Stair_Well_And_User_Confirmed_Window_Sills_Overcast'")
(W/'v26_8_build.py').write_text(s,'utf8')
for tag in['readback','protection_qa','geometry_qa','physics_qa','overlap_after','overlap_gate']:
 t=(W/f'v26_7_{tag}.py').read_text('utf8').replace('v26_7','v26_8').replace('V26_7','V26_8')
 if tag=='readback':t=t.replace('V26.6 source remains byte identical','V26.7 source remains byte identical')
 if tag=='protection_qa':t=t.replace("'V26_8_Source_Affine_Material'","'V26_7_Source_Affine_Material'")
 (W/f'v26_8_{tag}.py').write_text(t,'utf8')
print('BUILD_AND_QA_READY')
