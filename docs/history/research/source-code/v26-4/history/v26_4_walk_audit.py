from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_4';R=D/'Before';R.mkdir(parents=True,exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V26_3/Blender/Architecture_Complete_V26_3.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
def nodeinfo(n):
 return {'type':n.type,'name':n.name,'inputs':{i.name:list(i.default_value)if hasattr(i.default_value,'__len__')and not isinstance(i.default_value,str)else i.default_value for i in n.inputs if hasattr(i,'default_value')and isinstance(i.default_value,(float,int,str))},'image':n.image.name if n.type=='TEX_IMAGE'and n.image else None}
di={}
for m in bpy.data.materials:
 if any(k in m.name.lower()for k in ['floor','marble','glass','wall_interior']):di[m.name]={'diffuse':list(m.diffuse_color),'nodes':[nodeinfo(n)for n in m.node_tree.nodes]if m.use_nodes else[],'links':[[l.from_node.type,l.from_socket.name,l.to_node.type,l.to_socket.name]for l in m.node_tree.links]if m.use_nodes else[]}
(D/'Material_Audit.json').write_text(json.dumps(di,ensure_ascii=False,indent=2),encoding='utf8')
poses=[]
for fl,z in [(1,-.45),(2,3.45),(3,7.05)]:
 for tag,pos,aim in [('Right_Room',(11.4,4.4,1.6),(9.1,7.3,2.6)),('Left_Room',(1.9,4.4,1.6),(3.9,7.3,2.6)),('Hall',(6.5,4.3,1.6),(9.1,5.95,2.8)),('Stair_West',(4.7,8.7,1.6),(7.5,7.3,2.8)),('Stair_East',(8.35,8.6,1.6),(4.4,9.7,2.9)),('Right_WC',(11.8,8.6,1.6),(10.65,7.3,2.5))]:poses.append((f'F{fl}_{tag}',(pos[0],pos[1],pos[2]+z),(aim[0],aim[1],aim[2]+z)))
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1000;sc.render.resolution_y=850;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard';sh=sc.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=False;sh.background_type='WORLD';sc.world.color=(.12,.12,.12);sc.display.render_aa='16'
records=[]
for tag,pos,aim in poses:
 c=bpy.data.objects.new('Audit_'+tag,bpy.data.cameras.new('Audit_'+tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=18.;c.data.clip_start=.025;c.data.clip_end=600;sc.camera=c;sc.render.filepath=str(R/(tag+'.png'));bpy.ops.render.render(write_still=True);records.append({'tag':tag,'position':pos,'aim':aim});print('AUDIT_VIEW',tag,flush=True);bpy.data.objects.remove(c,do_unlink=True)
(D/'Audit_Views.json').write_text(json.dumps(records,indent=2),encoding='utf8')
print('AUDIT_COMPLETE',len(records),flush=True)
