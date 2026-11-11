import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v4_audit_junction')]
import apply_junction_v4 as J
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');p=O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json';S=json.loads(p.read_text(encoding='utf-8'));e=next(e for e in S['elements'] if e['name']=='WINDOW_FRONT_CENTER_F3')
def b(x,y,z,w,d,h,m='M_Metal_Black'):return J._part(J._box(x,y,z,w,d,h),m)
w=4.8;h=1.95;r=.045;split=1.48;parts=[b(0,-.045,0,r,.09,h),b(w-r,-.045,0,r,.09,h),b(r,-.045,0,w-2*r,.09,r),b(r,-.045,h-r,w-2*r,.09,r),b(r,-.045,split,w-2*r,.09,r)]
for x in [1.6,3.2]:parts.append(b(x-r/2,-.045,r,r,.09,h-2*r))
for xa,xb in [(r,1.6-r/2),(1.6+r/2,3.2-r/2),(3.2+r/2,w-r)]:parts.append(b(xa,-.004,split+r,xb-xa,.008,h-r-(split+r),'M_Glass_Clear'))
# The two narrow lower panels are casements seen open in the photo; they are
# distinct from a full-height balcony exit door.
for xa,xb in [(r,1.05),(1.05,1.6-r/2),(1.6+r/2,3.2-r/2),(3.2+r/2,3.75),(3.75,w-r)]:
 if xa in [1.05,3.75]:parts.append(b(xa-r/2,-.045,r,r,.09,split-r))
 parts.append(b(xa+r/2,-.004,r,xb-xa-r,.008,split-r,'M_Glass_Clear'))
 for xx in [xa,xb-r]:parts.append(b(xx,-.052,r,r,.015,split-r))
key='V7_CENTER_F3_THREE_TRANSOMS_TWO_CASEMENTS';S['definitions'][key]=dict(parts=parts,parameters=dict(Width=w,Height=h,Three_Transoms=True,Two_Narrow_Lower_Casements=True,Role='WINDOW_NOT_DOOR',Profile_Metric_Status='PHOTO_ESTIMATED'),source='DJI 0002/DJI_0038.JPG; DJI_0429.JPG',confidence='MEDIUM');e.update(definition=key,source='DJI 0002 0038/0429: three transoms, two narrow casements; original opening dimensions retained',status='V7_PHOTO_CORRECTED_PANEL_TOPOLOGY')
S['v7_changes'].append(dict(id='V7_F3_CENTER_WINDOW_PANELS',elements=[e['name']],description='三层中央窗改为三格上亮、两个窄开启扇与下部大固定玻璃，保留窗下墙，出口设在西侧平台墙',evidence=['DJI 0002/DJI_0038.JPG','DJI 0002/DJI_0429.JPG'],metric_status='OPENING_SIZE_RETAINED; FRAME_PROFILES_PHOTO_ESTIMATED'))
p.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8');(O/'06_Report/Changes_V7.json').write_text(json.dumps(S['v7_changes'],ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['V7_Changed_Nodes.json','V7_Incremental_Nodes.json']:
 pp=O/'02_Data'/name;c=json.loads(pp.read_text());c['changed']=list(dict.fromkeys(c['changed']+[e['name']]));pp.write_text(json.dumps(c,indent=2),encoding='utf-8')
print('F3 centre glazing corrected',flush=True)
