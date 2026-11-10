# 研究图与生成脚本索引

[研究方法总表](README.md) · [原过程图档](../process/README.md)

以下图均可按 `P` 图号回到过程图档和逐图 CSV。单张图保留更清晰的坐标刻度和轮廓。

| 单张图 | 原图与图号 | 发布处理 |
| --- | --- | --- |
| [首版实景屋顶局部高度分布](media/early-roof-height.png) | `work/Roof_Local_Height.png` · [P0D746ECE](../process/rebuild-05.md) · 025 页 6 行 5 列 | 原文件 |
| [V5 核对门位和连通时使用的 V4 三层基线平面](media/v5-f3-baseline-plan.png) | `JIA/Rebuild_V5/12_Video_Layout_Evidence/V4_F3_Plan.png` · [P13918969](../process/rebuild-01.md) · 002 页 6 行 2 列 | 原文件 |
| [V6 主空洞平面栅格掩码](media/v6-hole-mask.png) | `JIA/Rebuild_V6_Hybrid/06_Report/Main_Hole_Raster_Mask.png` · [P3076FBE5](../process/locate-01.md) · 001 页 3 行 1 列 | 原文件 |
| [V24.10 实景剖面与重建定位](media/v24-10-scan-sections.png) | `JIA/Rebuild_V24_10/Reports/Evidence_AsBuilt_Sections.png` · [P0F23E697](../process/materials-01.md) · 001 页 4 行 6 列 | 原文件 |
| [V24.34 新旧航测正射图的特征匹配](media/v24-34-registration.jpg) | `work/v24_34/Registration_Matches.jpg` · [PB023865C](../process/rebuild-07.md) · 032 页 5 行 4 列 | 保留匹配线与两幅底图，缩放发布 |
| [V26.3 保存模型的首层卫生间剖面](media/v26-3-wc-section.png) | `JIA/Rebuild_V26_3/Reports/F1_WC_Native_Section.png` · [P76281F7D](../process/locate-02.md) · 008 页 2 行 5 列 | 原文件 |
| [V26.10 保存前后墙角剖面](media/v26-10-wall-sections.png) | `JIA/Rebuild_V26_10/Reports/Wall_Sections_Before_After.png` · [PCC05430D](../process/locate-03.md) · 011 页 3 行 5 列 | 原文件 |
| [凉亭局部高度散点和当时平台的红框](media/pavilion-roof-plan.png) | `Twin_Preparation/ModelRepair_PavilionRail_20261027/Reports/photogrammetry_pavilion_plan.png` · [P669230BA](../process/materials-01.md) · 004 页 1 行 5 列 | 原文件 |
| [带色三角面投影与旧平台、目标平台对照](media/pavilion-roof-overlay.png) | `Twin_Preparation/ModelRepair_PavilionRail_20261027/Reports/reference_roof_textured_plan.png` · [P0438091D](../process/materials-01.md) · 004 页 1 行 6 列 | 原文件 |
| [保存模型的平台尺寸和主楼柱间距复核](media/pavilion-size-check.png) | `Twin_Preparation/ModelRepair_PavilionRail_20261027/Reports/亭子尺寸复核.png` · [P55BD49C0](../process/ue-01.md) · 003 页 1 行 5 列 | 原文件 |
| [同轮阳台石栏浮雕落位及承托复核](media/balcony-relief-check.png) | `Twin_Preparation/ModelRepair_PavilionRail_20261027/Reports/石栏杆浮雕复核.png` · [P2A1BB804](../process/materials-01.md) · 004 页 2 行 1 列 | 原文件 |

## 源码中明确写出图名的记录

本表按迭代顺序列出脚本保存调用与图档同名的结果。更多图来自同轮诊断、过程日志或保存后截图，详见逐版方法表。逐字节复算已单独登记在凉亭案例。

| 迭代 | 脚本保存调用 | 已归档原图 |
| --- | --- | --- |
| `V4` | `JIA/Rebuild_V4/11_Construction_Reference/v4_audit_safety/source_render.py` | `JIA/Rebuild_V4/11_Construction_Reference/v4_audit_safety/D10_1175_Hi.png` · [PBA86EFA6](../process/rebuild-01.md) |
| `V4` | `JIA/Rebuild_V4/11_Construction_Reference/v4_audit_safety/source_render11.py` | `JIA/Rebuild_V4/11_Construction_Reference/v4_audit_safety/D11_1175_Hi.png` · [P78A000DF](../process/rebuild-01.md) |
| `V5` | `work/v5_model_audit/audit.py` | `work/v5_model_audit/V4_All_Floors_Door_Plans.jpg` · [PFD768449](../process/rebuild-06.md) |
| `V5` | `work/v5_model_audit/render_v5_comparison.py` | `JIA/Rebuild_V5/09_Report/V5_All_Floors_Before_After.jpg` · [P76DC3E21](../process/locate-01.md) |
| `V8` | `JIA/Rebuild_V8_Hybrid/07_Evidence/Terrain_Clearance/plot_v8_top.py` | `JIA/Rebuild_V8_Hybrid/07_Evidence/Terrain_Clearance/V8_West_Terrain_Only_Plan.png` · [P5B17C15A](../process/rebuild-01.md) |
| `V8` | `work/v8_interior/preview.py` | `JIA/Rebuild_V8_Hybrid/07_Evidence/Interior/V8_Interior_Plan_Review.png` · [P8B9DB39E](../process/locate-01.md) |
| `V8` | `work/v8_interior/preview.py` | `JIA/Rebuild_V8_Hybrid/07_Evidence/Interior/V8_Stair_Door_Candidate_Top.png` · [P7DB06045](../process/rebuild-01.md) |
| `V8` | `work/v8_interior/preview.py` | `JIA/Rebuild_V8_Hybrid/07_Evidence/Interior/V8_Stair_Geometry_Review.png` · [P723EEE4C](../process/locate-01.md) |
| `V8` | `work/v8_terrain_clear/plot_top.py` | `JIA/Rebuild_V8_Hybrid/07_Evidence/Terrain_Clearance/V7_Plan_Local_Initial.png` · [PCA9AA68F](../process/rebuild-01.md) |
| `V8` | `work/v8_terrain_clear/plot_ground_class.py` | `JIA/Rebuild_V8_Hybrid/07_Evidence/Terrain_Clearance/V8_West_Terrain_Ground_Classification.png` · [PCB7AB3AF](../process/rebuild-01.md) |
| `V11` | `JIA/Rebuild_V11_Hybrid/07_Evidence/v11_outer_gate/preview.py` | `JIA/Rebuild_V11_Hybrid/07_Evidence/v11_outer_gate/Gate_and_Wall_Review.png` · [P44FC228D](../process/locate-01.md) |
| `V16` | `JIA/Rebuild_V16/08_Editable_Source/V16_Scripts/v16_probe.py` | `work/v16/Before_Height_Map.png` · [P37474ACD](../process/locate-03.md) |
| `V17` | `JIA/Rebuild_V17/08_Editable_Source/V17_Scripts/v17_local_audit.py` | `work/v17/Local_Wall_Plan_Before.png` · [P847266AD](../process/locate-03.md) |
| `V17` | `JIA/Rebuild_V17/08_Editable_Source/V17_Scripts/v17_probe.py` | `work/v17/Junction_Plan_Before.png` · [P777C8A8B](../process/locate-03.md) |
| `V18` | `JIA/Rebuild_V18/08_Editable_Source/V18_Scripts/v18_design.py` | `JIA/Rebuild_V18/03_Textures/V18_Storage_AsBuilt/Photo_Dark_Stone_Microheight.png` · [P891B80A4](../process/materials-01.md) |
| `V18` | `JIA/Rebuild_V18/08_Editable_Source/V18_Scripts/v18_design.py` | `JIA/Rebuild_V18/03_Textures/V18_Storage_AsBuilt/Photo_Rubble_Microheight.png` · [P8C51D276](../process/materials-01.md) |
| `V18` | `JIA/Rebuild_V18/08_Editable_Source/V18_Scripts/v18_design.py` | `JIA/Rebuild_V18/03_Textures/V18_Storage_AsBuilt/Stone_Guard_Photo_Atlas.png` · [PA50BB4E9](../process/materials-01.md) |
| `V18` | `JIA/Rebuild_V18/08_Editable_Source/V18_Scripts/v18_design.py` | `JIA/Rebuild_V18/03_Textures/V18_Storage_AsBuilt/Stone_Guard_Photo_Height.png` · [PDA6D7E24](../process/materials-01.md) |
| `V20` | `JIA/Rebuild_V20/08_Editable_Source/V20_Scripts/house/plan.py` | `work/v20_house/House_Plans.png` · [PB61CBEB6](../process/rebuild-06.md) |
| `V21` | `JIA/Rebuild_V21/08_Editable_Source/V21_Scripts/house/plan_compare.py` | `work/v21_house/F3_Door_Position_Comparison.png` · [PE3E9BAA7](../process/locate-03.md) |
| `V24.10` | `JIA/Rebuild_V24_10/Source/v24_10_sections.py` | `work/v24_10/AsBuilt_Sections.png` · [P0F23E697](../process/materials-01.md) |
| `V24.10` | `JIA/Rebuild_V24_10/Source/v24_10_plan.py` | `work/v24_10/Plot_Boundary_Comparison.png` · [PE4AA6AB6](../process/locate-01.md) |
| `V24.11` | `JIA/Rebuild_V24_11/Source/v24_11_plan.py` | `JIA/Rebuild_V24_11/Reports/V24_11_Veranda_and_Rear_Wall_Plan.png` · [P3DB89A35](../process/rebuild-03.md) |
| `V24.11` | `JIA/Rebuild_V24_11/Source/v24_11_analyze.py` | `work/v24_11/Existing_Storage_Masonry_Plan.png` · [P63A39505](../process/rebuild-06.md) |
| `V24.11` | `JIA/Rebuild_V24_11/Source/v24_11_analyze.py` | `work/v24_11/Existing_Veranda_Column_Plan.png` · [P6062F5F2](../process/rebuild-06.md) |
| `V24.16` | `JIA/Rebuild_V24_16/Source/v24_16_analyse.py` | `work/v24_16/Screen_Crosssections_Before.png` · [PD93C59A6](../process/locate-03.md) |
| `V24.16` | `JIA/Rebuild_V24_16/Source/v24_16_analyse.py` | `work/v24_16/Storage_Entry_Plan_Before.png` · [P93CE2732](../process/locate-03.md) |
| `V24.20` | `work/v24_20_plan.py` | `work/v24_20/F1_Before_Plan.png` · [P6487B981](../process/locate-03.md) |
| `V24.20` | `work/v24_20_plot_kitchen.py` | `work/v24_20/Kitchen_Before_Plan.png` · [P078ED48A](../process/locate-03.md) |
| `V24.30` | `work/v24_30_plan.py` | `work/v24_30/Plan.png` · [P08542CFB](../process/rebuild-07.md) |
| `V24.30` | `work/v24_30_preview_plan.py` | `work/v24_30/Plan_After.png` · [P99018EFB](../process/locate-03.md) |
| `V24.31` | `work/v24_31_draw_plan.py` | `work/v24_31/Plan.png` · [P476B9751](../process/rebuild-07.md) |
| `V24.33` | `JIA/Rebuild_V24_33/Sources/v24_33_plan.py` | `work/v24_33/Wall_Plan_Z1.png` · [PF6D1F2EB](../process/rebuild-07.md) |
| `V24.34` | `JIA/Rebuild_V24_34/Sources/v24_34_match.py` | `work/v24_34/Registration_Matches.jpg` · [PB023865C](../process/rebuild-07.md) |
| `V24.34` | `JIA/Rebuild_V24_34/Sources/v24_34_grid_plot.py` | `JIA/Rebuild_V24_34/Source_Metadata/Route_Support_Map.png` · [PC04671EE](../process/locate-02.md) |
| `V24.36` | `work/v24_36_route_debug_plot.py` | `work/v24_36/Route_Local_Debug.png` · [PF37D0919](../process/locate-04.md) |
| `V24.37` | `work/v24_37_review_crop.py` | `JIA/Rebuild_V24_37/Source_Metadata/North_Skirt_Review.png` · [P6E821E6B](../process/locate-02.md) |
| `V24.37` | `work/v24_37_plot_retention.py` | `JIA/Rebuild_V24_37/Source_Metadata/Retention_Overlay.png` · [P312794E5](../process/locate-02.md) |
| `V26` | `work/v26_analysis_views.py` | `work/v26/Original_Gate_Top.jpg` · [P58579115](../process/rebuild-07.md) |
| `V26` | `work/v26_analysis_views.py` | `work/v26/Structure_Before_Plans.png` · [P18E5F815](../process/locate-04.md) |
| `V26.4` | `JIA/Rebuild_V26_4/Sources/v26_4_draw_plan.py` | `JIA/Rebuild_V26_4/Reports/V26_4_F1_Room_Relationships.png` · [P490BD196](../process/rebuild-05.md) |
| `V26.4` | `work/v26_4_plan.py` | `work/v26_4/F1_Plan_Before.png` · [PDA914B13](../process/locate-04.md) |
| `V26.5` | `work/v26_5_left_audit/bay_sections.py` | `work/v26_5_left_audit/front_bay_corner_sections.png` · [P1BC815C7](../process/locate-04.md) |
| `V26.10` | `JIA/Rebuild_V26_10/Sources/v26_10_plot_sections.py` | `JIA/Rebuild_V26_10/Reports/Wall_Sections_Before_After.png` · [PCC05430D](../process/locate-03.md) |
| `V26.11` | `JIA/Rebuild_V26_11/Sources/v26_11_gate_relief_prepare.py` | `JIA/Rebuild_V26_11/Reports/Reference_To_Gray_Overview.png` · [PF6DF6834](../process/rebuild-05.md) |
| `V26.14` | `JIA/Rebuild_V26_14/Sources/v26_14_sections.py` | `JIA/Rebuild_V26_14/Sources/Geometry_Archive/Wall_Sections_Before.png` · [P8DB3D361](../process/locate-03.md) |
| `20261027_205418_6569f3a8` | `Twin_Preparation/ModelRepair_PavilionRail_20261027/analyze_reference.py` | `Twin_Preparation/ModelRepair_PavilionRail_20261027/Reports/photogrammetry_pavilion_plan.png` · [P669230BA](../process/materials-01.md) |
| `20261027_205418_6569f3a8` | `Twin_Preparation/ModelRepair_PavilionRail_20261027/reference_roof.py` | `Twin_Preparation/ModelRepair_PavilionRail_20261027/Reports/reference_roof_textured_plan.png` · [P0438091D](../process/materials-01.md) |
| `20261029_193755_baa174db` | `Twin_Preparation/ModelRepair_WindowPhoto_20261029/prepare_textures.py` | `Twin_Preparation/ModelRepair_WindowPhoto_20261029/Textures/carved_panel_height.png` · [P249D7DD8](../process/materials-01.md) |
| `20261029_193755_baa174db` | `Twin_Preparation/ModelRepair_WindowPhoto_20261029/prepare_textures.py` | `Twin_Preparation/ModelRepair_WindowPhoto_20261029/Textures/carved_panel_photo.png` · [P9C70E12F](../process/materials-01.md) |
| `20261029_193755_baa174db` | `Twin_Preparation/ModelRepair_WindowPhoto_20261029/prepare_textures.py` | `Twin_Preparation/ModelRepair_WindowPhoto_20261029/Textures/window_wood_satin.png` · [PFC98A304](../process/materials-01.md) |
| `20261029_221502_3273826c` | `Twin_Preparation/ModelRepair_CarvedRelief_20261029/prepare_assets.py` | `Twin_Preparation/ModelRepair_CarvedRelief_20261029/Textures/carving_height_preview.png` · [P12263089](../process/materials-01.md) |
