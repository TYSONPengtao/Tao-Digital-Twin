import json,csv
from pathlib import Path
O=Path(__file__).resolve().parent
changes=[]
def add(id,kind,target,coords,evidence,finding,limits,confidence='MEDIUM'):
 changes.append(dict(id=id,kind=kind,target=target,proposed=coords,source_video=r'E:\jz\VID_20260507_152114_00_001.insv',seconds=evidence,observation=finding,confidence=confidence,metric_confidence='LOW_NOT_SURVEYED',limits=limits))
for floor,level in [(1,0),(2,3.9)]:
 for side,x in [('L',3.9),('R',9.1)]:
  times=([510,515,520,525,550] if side=='L' else [510,515,570,585,590]) if floor==1 else ([315,325,338,350,375] if side=='L' else [375,400,410,425,480,485,490])
  add(f'VP-{floor}{side}-FRONT-DOOR','move_opening',f'DOOR_BED_F{floor}_X{x}',dict(origin=[x,2.4,level],angle=1.5707963267948966,width=.9,height=2.1,position_band_y=[2.3,3.5],host=f'PARTITION_BED_F{floor}_X{x}',old_origin=[x,6.1,level],swing='observed into bedroom; hinge and exact angle not verified'),times,'客厅与门、正面入口或阳台同框，木门位于正面端，原模型后端门位不符。','新位置沿设计轴网暂定，仅足以改前后端及连通；每扇门独立保存参数，不能视为尺寸实测。','HIGH_TOPOLOGY_MEDIUM_POSITION')
add('VP-3R-STAIR-DOOR','move_opening','DOOR_BED_F3_X9.1',dict(origin=[9.1,7.55,7.5],angle=1.5707963267948966,width=.9,height=2.1,position_band_y=[7.45,8.65],old_origin=[9.1,6.1,7.5],host='x9.1 rear partition extension between y7.4..9.6'),[160,210,228,232,237,265,268,270],'红木门在上部平台侧，与浅色木门转角相邻；穿门进多床房，回望可见平台栏杆及浅木门。','0.9×2.1m 门洞和楼面高程保留设计估值；后段隔墙需补足并避免与结构柱相交。','HIGH_TOPOLOGY_MEDIUM_POSITION')
add('VP-3-CENTER-USE','rename_use','DOOR_STUDY_F3',dict(origin=[8.0,7.3,7.5],room_use='sleeping_room_observed',material='light_natural_wood',width=.9,height=2.1),[210,212,215,218,223,228,230],'浅木门进入摆床的中心房，不能继续当作仅有书桌的设计书房。','位置与宽高保留设计候选，图像确认独立房间及木门材质，不确认尺寸。','HIGH_TOPOLOGY')
add('VP-3-STUDY-WINDOW','retire_design_window_and_fill_wall','WINDOW_STUDY_C3620_F3',dict(host='PARTITION_STUDY_F3',retain_opening_only=[4.1,.9,0,2.1],note='actual kept door starts x8.0; close 3.6m window in y7.3 wall'),[155,160,162,205,210,228,270],'平台通向西侧露台的长墙可见连续实墙，未见设计所放的 3.6m 室内长窗。','关闭设计窗为影像支持的候选，应保留原对象的设计版本和来源；原墙门数据需单独设为 x8.0。','MEDIUM')
for floor,level in [(1,0),(2,3.9),(3,7.5)]:
 add(f'VP-{floor}R-RECESS','remove_spurious_partition_segment',f'PARTITION_BACK_F{floor}_R',dict(cut_xy=[9.3,7.2,10.71,7.4],retain_bath_front_x=[10.89,12.8],retain_bath_side_x=10.8,level=level),{1:[550,570,575,580,588],2:[338,350,355,410,440,455],3:[232,235,237,245,255,260]}[floor],'主床区直接连通后部窄凹段，凹段侧玻璃门通向独立空间；现横墙封住凹段入口不符影像。','仅移除凹段口的封堵，不整条删除浴室前墙；宽度沿设计轴网暂定。上部玻璃门后空间未进入，保留用途待核。','HIGH_TOPOLOGY_MEDIUM_POSITION')
add('VP-1R-GLASS-DOOR','replace_and_move_candidate','DOOR_BACKROOM_F1_R',dict(new_name='DOOR_BATH_F1_R',origin=[10.8,7.65,0],angle=1.5707963267948966,width=.8,height=2.1,material='frosted_glass_red_frame'),[575,580,588],'入口层第二床区后凹段可见红框磨砂玻璃门；当前后横墙木门外观和拓扑不符。','侧门平面位置属于设计约束下候选；没有进入此门，不应将浴室用途和确切偏距列为已测。','MEDIUM')
add('VP-1-STAIR-BATH','change_use_and_door_finish','DOOR_KITCHEN_F1',dict(origin=[7.8,8.6,0],angle=1.5707963267948966,width=.8,height=2.1,material='frosted_glass_red_frame',room_use='washroom_observed'),[100,110,505,510],'入口层楼梯旁空间有洗面盆与卫生间墙砖，出入口为红框磨砂玻璃门。','房间用途与门材质可确认，原门位置仍是设计尺度候选。','HIGH_USE_MEDIUM_POSITION')
out=dict(scope='video-supported topology and appearance candidates, not surveyed as-built',units='metres',origin_frame='existing V4 drawing shell coordinate',new_extracts=56,changes=changes,preserved_unknowns=['门洞偏距、门宽高与墙厚未实测','楼层标高沿用设计','未进入的卫生间和储物空间不以邻层替代','未知墙与门继续保留但标记待核','多张照片中床及衣柜不可当作固定隔墙'])
(O/'V5_Video_Plan_Proposal.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'V5_Video_Plan_Proposal.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=['id','kind','target','proposed','seconds','observation','confidence','metric_confidence','limits']);wr.writeheader()
 for r in changes:wr.writerow({k:json.dumps(r[k],ensure_ascii=False) if isinstance(r[k],(dict,list)) else r[k] for k in wr.fieldnames})
(O/'Video_Plan_Analysis.md').write_text('''# 全景视频逐层门位与布局改模提案

审查来源是原始双鱼眼 INSV。本轮独立补 56 张 110°与 ±40°透视，另使用既有 118 张抽帧；这些透视没有相机标定，不能产生精确米制尺寸。提案单位 m，坐标沿用 V4 的设计外壳，候选坐标是用于空间调整的参数，不是实测竣工坐标。主场景未被本分析脚本修改。

## 楼层对应

- F1：入口层，在 100/110 秒与 505/510 秒可见楼梯旁卫生间，在 510/515/600 秒可见正面外门和院子。
- F2：中间层，在 295 秒从楼梯出来，325/375/400 秒可到带石栏杆的阳台，495 秒开始下楼。
- F3：上部层，在 160 秒到平台，170/205 秒连接带金属棚的西侧露台，280 秒开始下楼。

楼层层序由路线、外阳台及露台共同支持，绝对标高仍沿用设计值。

## 四个前端门和一个平台门

F1/F2 两侧卧室门与正面外门/阳台同框。原模型放在 y6.1 的后端；建议每扇门独立设 y2.4 候选，候选区间约 y2.3..3.5。F1 510/515/520/585/590 和 F2 315/325/375/485/490 支持这一改变。

F3 两扇门不能复制上述位置：212 秒从平台打开浅木门，218 秒中心房有床，223 秒返回，228/230 秒关浅木门，232/237 秒从转角的红木门进入右翼多床房，265 秒回望可见浅木门和平台栏杆。建议保留浅木门 x8,y7.3，中心房改为影像所见睡眠用途；红木门从 x9.1,y6.1 移至 x9.1,y7.55 候选。视频确认转角两门与两个独立空间，未测门洞偏距。

## 后部凹段与浴室侧门

F2 第一翼 338/350/355 秒与第二翼 410/440/455 秒，F1 530/550 与 570/575/580/588 秒，F3 232/235/237/255/260 秒都支持主床区无门通到后窄段。右翼当前 y7.3 横墙封住 x9.3..10.71 的后凹段入口，应仅删此封堵，保留浴室前墙 x10.89..12.8 及侧墙 x10.8。左翼现模型的前墙本来只到 x2.2，x2.3..3.7 凹段口已开放，无需再拆。

F2 455 秒进入真实卫生间并从门内回望贴画床区，足以确认此侧玻璃门与右翼房间连通。F1/F3 的某些玻璃门后没有进入，不根据门材质强行认定全部为浴室。F1 100/110 秒楼梯旁洗手间确定，当前 KITCHEN 用途和木门材质应修正为洗手间与红框磨砂玻璃门。

## 限制与保留

候选门宽高保留设计 0.9×2.1m 或 0.8×2.1m。门开向在多处可见向卧室内部开启，但每门铰链端、最大角及墙角距离须独立验证；不能从统一组件自动认定相同。F3 3.6m 设计室内窗与平台长实墙影像冲突，建议关闭并保存为设计参考对象。家具不是隔墙。未见空间保留待核，用途和尺寸不自动跨层复制。

精确提案及源时间见 V5_Video_Plan_Proposal.json/CSV。证据联系表是 Wide_Contact_01..04.jpg，各帧均可由 View_Index.json 追溯。
''',encoding='utf-8')
print('wrote',len(changes),'changes')
