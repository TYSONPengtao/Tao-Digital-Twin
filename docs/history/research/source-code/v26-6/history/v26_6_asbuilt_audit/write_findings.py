from pathlib import Path
import json
O=Path(__file__).parent
findings={
 'status':'PHOTO_SUPPORTED_LOCAL_REPAIR',
 'screenshot':'D:/Desktop/屏幕截图 2026-10-24 005316.jpg',
 'model_source':'E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend',
 'location':'F3 west terrace north covered alcove, between terrace at Y<7.3 and double-window corner at Y7.3..9.8',
 'offending_object':'V26_3_House_Connected_Walls_And_Stairs',
 'offending_infill_model_bounds_m':[[.12,7.2,7.05],[2.2,7.4,9.9500246]],
 'original_added_recipe':'work/v26_4_house.py: P=P.union(box(.12,7.2,2.2,7.4)) runs for all floors',
 'finding':'The F3 crosswall blocks the full-width opening visible in actual video. It is an old laundry-front infill and must not be copied from the lower floors. The structural header and two columns remain.',
 'actual_evidence':[
  {'file':'Actual_F3Terrace_t175_Lens0_Yaw0_FOV110.jpg','seconds':175,'lens_stream':0,'observation':'From the double-window alcove toward the metal-covered terrace: full-width open connection with only the overhead beam, no infill or door.'},
  {'file':'Actual_F3Terrace_t180_Lens1_Yaw0_FOV110.jpg','seconds':180,'lens_stream':1,'observation':'From the tiled terrace-side doorway looking back toward window alcove: open connection and bed/table visible, no laundry crosswall.'},
  {'file':'Actual_F3Terrace_t170_Lens0_Yaw0_FOV110.jpg','seconds':170,'lens_stream':0,'observation':'Alcove has two adjacent black framed windows, plain white flat ceiling, light curtain rail and corner pillar. Visible furniture is not a wall.'},
  {'file':'Actual_F3Terrace_t200_Lens0_Yaw0_FOV110.jpg','seconds':200,'lens_stream':0,'observation':'Long view along terrace toward the north window alcove confirms open connection beneath a header.'},
  {'file':'Actual_F3Terrace_t205_Lens1_Yaw0_FOV110.jpg','seconds':205,'lens_stream':1,'observation':'Reverse terrace view confirms the same white alcove ceiling, paired windows and absence of blocking white partition.'}
 ],
 'source_video':'E:/jz/VID_20260507_152114_00_001.insv',
 'source_video_metadata':{'duration_seconds':1274.77,'lens_streams':[0,1],'native_resolution':[3840,3840],'nominal_fps':'29.97','creation_time_utc':'2026-05-07T07:21:14Z'},
 'projection':{'ffmpeg_v360_input':'fisheye','input_horizontal_fov_degrees':180,'input_vertical_fov_degrees':180,'output':'flat','output_horizontal_fov_degrees':110,'output_vertical_fov_degrees':110,'yaw_degrees':0,'dimensions':[1200,1200]},
 'retain_original_model_cores':[
  {'name':'BEAM_X_F3_7.3_0_Geometry','bounds_m':[[0,7.174999713897705,9.950024604797363],[3.9000000953674316,7.425000190734863,10.220044136047363]]},
  {'name':'KZ_1_2_F3_Geometry','bounds_m':[[-.20000022649765015,7.099999904632568,7.050000190734863],[.20000018179416656,7.5,10.220044136047363]]},
  {'name':'KZ_2_2_F3_Geometry','bounds_m':[[3.700000047683716,7.100000381469727,7.050000190734863],[4.099999904632568,7.500000476837158,10.220044136047363]]}
 ],
 'recommended_scope':'Remove only confirmed F3 infill below the original beam between original columns; retain original windows, frames, original core solids, lower-floor partitions, terrace masonry and secondary screenwall.',
 'ceiling_reference':'The alcove ceiling is plain white and flat; top of actual glazing is cleanly framed. No arbitrary additional partition or exposed beige roof underside is supported. Absolute heights and thickness are inherited model values, not measurements from these uncalibrated video projections.',
 'metric_limit':'Video frames support topology, surface colour and element relationships. Model coordinates identify the existing defect; they are not surveyed as-built dimensions.'
}
(O/'AsBuilt_F3_Terrace_Crosswall_Findings.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2),'utf8')
(O/'Findings_实景依据.txt').write_text('005316位置：三楼西露台北端双窗凹角。\n错误墙：主楼合并实体内X0.12..2.20、Y7.20..7.40、Z7.05..9.950m。\n原INSV 175秒Lens0和180秒Lens1互相印证，此处是整跨敞开连接，墙顶横梁和两侧柱保留；不能整跨删除梁柱，也不复制到其他楼层。\n170秒Lens0与205秒Lens1显示双窗凹角白色平顶和完整窗框，桌、床和窗帘并非隔墙。\n图片全部从E:/jz/VID_20260507_152114_00_001.insv即时解码，具体投影参数见Frame_Provenance.json。图片未做相机标定，不能当成精确尺寸测量。\n未修改任何模型。','utf8')
print('ASBUILT_FINDINGS_WRITTEN')
