from pathlib import Path
W=Path(__file__).parent
s=(W/'v19_render_native.py').read_text(encoding='utf8')
s=s.replace('V19','TEMPNEW').replace('V18','V19').replace('TEMPNEW','V20')
s=s.replace("m['Appearance_Source']='V20 actual native 3DM bitmap material and readback UV'","m['Appearance_Source']='V20 actual native 3DM bitmap material and readback UV'")
s=s.replace("sc.render.engine='CYCLES';sc.cycles.samples=24", "sc.render.engine='CYCLES';sc.cycles.samples=20")
insert='''
# Each leaf has a genuine pivot transform, an inward animation and a default open pose.
DM=json.loads((O/'02_Data/Door_Manifest_V20.json').read_text(encoding='utf8'))
for row in DM['doors']:
    n=row['name'];par=bpy.data.objects[n];ob=bpy.data.objects[n+'_Geometry'];pivot=Vector(row['hinge_local_m'])
    par.location=(0,0,0);par.rotation_euler=(0,0,0);par.scale=(1,1,1)
    for v in ob.data.vertices:v.co-=pivot
    par.location=pivot
    for k,v in row.items():par[k]=json.dumps(v) if isinstance(v,(dict,list)) or v is None else v
    par['UE_Interaction']='HINGED_INWARD';par['DefaultPose']='OPEN_INWARD';par['HingeCoordinateSystem']='LOCAL metres'
bpy.context.view_layer.update()
for row in DM['doors']:
    if row.get('parent_door_id'):
        ob=bpy.data.objects[row['name']];world=ob.matrix_world.copy();ob.parent=bpy.data.objects[row['parent_door_id']];ob.matrix_world=world
bpy.context.view_layer.update()
for row in DM['doors']:
    if row.get('parent_door_id'):continue
    par=bpy.data.objects[row['name']];deg=row['open_angle_deg'];par.rotation_mode='XYZ';par.rotation_euler.z=-math.radians(deg);par.keyframe_insert(data_path='rotation_euler',frame=1,index=2);par.rotation_euler.z=0;par.keyframe_insert(data_path='rotation_euler',frame=40,index=2)
    act=par.animation_data.action;act.name='Inward_'+row['name'];track=par.animation_data.nla_tracks.new();track.name=act.name;strip=track.strips.new(act.name,1,act);par.animation_data.action=None
sc.frame_end=40;sc.frame_set(40)
'''
s=s.replace("sc.render.engine='CYCLES'",insert+"\nsc.render.engine='CYCLES'",1)
s=s.replace("export_cameras=True,export_extras=True)","export_cameras=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_current_frame=True)")
(W/'v20_render_native.py').write_text(s,encoding='utf8')
print('V20 renderer ready')
