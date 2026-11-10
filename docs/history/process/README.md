# Codex 过程图档

[回到工作方法](../codex-methods.md) · [建筑重建逐版台账](../reconstruction.md) · [智慧家逐版台账](../smart-home.md)

收录 **3,080 张不同的过程图**，对应 **5,762 条出处**，排成 **76 个图页**。图上保留版本、坐标刻度、用户圈注和诊断标记；15 张公开预览对边缘画面或界面区域做了局部裁切。

每页都可点开看大图。通过图下方的 `P` 编号，在该页的 CSV 中可查到图页、行列、处理方式、原文件与同图副本。关键图另有独立大图。

## 图页目录

| 类别 | 图数 | 分页 |
| --- | ---: | --- |
| 问题标注、定位与剖切 | 933 | [1](locate-01.md) · [2](locate-02.md) · [3](locate-03.md) · [4](locate-04.md) · [5](locate-05.md) |
| 材质来源、取样与映射 | 150 | [1](materials-01.md) |
| 重建与 Blender / Rhino 复核 | 1,669 | [1](rebuild-01.md) · [2](rebuild-02.md) · [3](rebuild-03.md) · [4](rebuild-04.md) · [5](rebuild-05.md) · [6](rebuild-06.md) · [7](rebuild-07.md) · [8](rebuild-08.md) |
| Rhino、Datasmith 与重导入 | 60 | [1](handoff-01.md) |
| UE5 场景、交互与分析复核 | 268 | [1](ue-01.md) · [2](ue-02.md) |

## 关键图原始出处

| 图 | 编号与图页 | 原文件 |
| --- | --- | --- |
| [V24.22 修改前的三层 Z 水平切片](media/focus/v24-22-z-sections.png) | [P41EB375B](locate-03.md) · `locate-015.jpg` · 5 行 5 列 | 重建工作目录（work） · `v24_22/Wall_plans_Before.png` |
| [V24.22 修改前的六处 Y 定值剖面](media/focus/v24-22-y-sections.png) | [PE8F181B2](locate-03.md) · `locate-015.jpg` · 5 行 6 列 | 重建工作目录（work） · `v24_22/Wall_sections_Before.png` |
| [V24.36 北侧道路局部坐标、地面采样和候选路点](media/focus/v24-36-road-grid.webp) | [PF37D0919](locate-04.md) · `locate-016.jpg` · 5 行 6 列 | 重建工作目录（work） · `v24_36/Route_Local_Debug.png` |
| [V7 用户红线标出的山墙缺面](media/focus/v7-gable-mark.jpg) | [PD4C26291](locate-01.md) · `locate-001.jpg` · 3 行 3 列 | 重建交付（JIA） · `Rebuild_V7_Hybrid/07_Evidence/User_Annotations/屏幕截图 2026-10-08 211428.jpg` |
| [V7 山墙闭合后的原过程图](media/focus/v7-gable-saved.jpg) | [PFBFAB5F6](rebuild-01.md) · `rebuild-004.jpg` · 3 行 3 列 | 重建交付（JIA） · `Rebuild_V7_Hybrid/06_Report/V7_Closed_Gable.png` |
| [V24.16 原墙墙身中线与瓦顶截面对照](media/focus/v24-16-wall-centerline.jpg) | [P8DF4DD9E](locate-01.md) · `locate-003.jpg` · 7 行 3 列 | 重建交付（JIA） · `Rebuild_V24_16/Reports/V24_16_Screenwall_Alignment_Sections.png` |
| [V24.22 保存后的厨房内侧山墙视图](media/focus/v24-22-gable-review.jpg) | [PECF6A5E3](rebuild-03.md) · `rebuild-014.jpg` · 4 行 2 列 | 重建交付（JIA） · `Rebuild_V24_22/Reports/V24_22_Interior_Gable.png` |
| [V18 储藏房外墙的取样照片](media/focus/v18-material-photo.jpg) | [P6FC4CB91](locate-01.md) · `locate-002.jpg` · 5 行 2 列 | 重建交付（JIA） · `Rebuild_V18/07_Reference/屏幕截图 2026-10-12 180115.jpg` |
| [V18 透视校正和接边处理后的毛石颜色贴图](media/focus/v18-rubble-color.jpg) | [P954030FC](materials-01.md) · `materials-001.jpg` · 2 行 1 列 | 重建交付（JIA） · `Rebuild_V18/03_Textures/V18_Storage_AsBuilt/Photo_Rubble_Stone.png` |
| [V18 从毛石照片派生的微凹凸图](media/focus/v18-rubble-height.jpg) | [P8C51D276](materials-01.md) · `materials-001.jpg` · 1 行 6 列 | 重建交付（JIA） · `Rebuild_V18/03_Textures/V18_Storage_AsBuilt/Photo_Rubble_Microheight.png` |
| [V18 毛石、条石与石栏在同一构件场景的外观核对](media/focus/v18-material-result.jpg) | [PE913C1A5](materials-01.md) · `materials-001.jpg` · 2 行 6 列 | 重建交付（JIA） · `Rebuild_V18/06_Report/V18_Storage_Photo_Exterior.png` |
| [V26.11 浮雕参考到灰度高度图的过程对照](media/focus/v26-11-relief-reference.jpg) | [PF6DF6834](rebuild-05.md) · `rebuild-021.jpg` · 6 行 3 列 | 重建交付（JIA） · `Rebuild_V26_11/Reports/Reference_To_Gray_Overview.png` |
| [V26.11 保存后的石浮雕近景](media/focus/v26-11-relief-result.jpg) | [P84228D28](materials-01.md) · `materials-001.jpg` · 5 行 5 列 | 重建交付（JIA） · `Rebuild_V26_11/Reports/After_08_Gate_Gray_Relief_Close.png` |
| [V26.20 储藏房入口台阶的实际视口复核](media/focus/v26-20-blender-viewport.jpg) | [P591BCD43](rebuild-05.md) · `rebuild-025.jpg` · 2 行 1 列 | 重建交付（JIA） · `Rebuild_V26_20/Reports/Views/Viewport_02_02_Entry_Step_Close.png` |
| [V13 依据 Rhino 原生文件复核雨棚下侧](media/focus/v13-rhino-native.jpg) | [P0FE08B3C](handoff-01.md) · `handoff-001.jpg` · 1 行 2 列 | 重建交付（JIA） · `Rebuild_V13/06_Report/V13_Native_Canopy_Underside.png` |
| [UE5 储藏房材质修复所用的实景照片](media/focus/ue-storage-photo.jpg) | [PCBB18640](materials-01.md) · `materials-004.jpg` · 3 行 2 列 | 智慧家工作目录（Twin_Preparation） · `References/Storage_Real_Photo_20261026.jpg` |
| [UE5 储藏房在旧材质下的预览](media/focus/ue-storage-before.jpg) | [PEDAE363F](materials-01.md) · `materials-004.jpg` · 3 行 6 列 | 智慧家工作目录（Twin_Preparation） · `Reports/Storage_Photo_Before.png` |
| [UE5 修复照片材质后的檐下花格和梁柱](media/focus/ue-storage-after.jpg) | [P7A1C07F9](materials-01.md) · `materials-004.jpg` · 3 行 3 列 | 智慧家工作目录（Twin_Preparation） · `Reports/Storage_Photo_After_Detail.png` |
| [UE5 发布前核查厨房后墙源几何的截面图](media/focus/ue-wall-sections.jpg) | [P987E0E21](ue-01.md) · `ue-002.jpg` · 6 行 2 列 | 智慧家工作目录（Twin_Preparation） · `ModelRepair_FinalReview_20261028/Reports/kitchen_rear_wall_sections.png` |
| [UE5 厨房后墙原洞口的修改前截图](media/focus/ue-wall-before.jpg) | [P794FF1F7](ue-01.md) · `ue-002.jpg` · 4 行 6 列 | 智慧家工作目录（Twin_Preparation） · `ModelRepair_FinalReview_20261028/Reports/before_detail_厨房后墙原洞口.png` |
| [UE5 厨房后墙修复后关卡截图](media/focus/ue-wall-after.jpg) | [PD4C4DE98](ue-01.md) · `ue-002.jpg` · 4 行 1 列 | 智慧家工作目录（Twin_Preparation） · `ModelRepair_FinalReview_20261028/Reports/after_厨房后墙原洞口.png` |
| [UE5 主楼后外墙关闭 Nanite 的诊断图](media/focus/ue-nanite-off.jpg) | [P09285C7A](ue-01.md) · `ue-001.jpg` · 6 行 3 列 | 智慧家工作目录（Twin_Preparation） · `ModelRepair_Exterior_20261027/Reports/主楼后外墙_无Nanite对照.png` |

## 盘点范围

- 建筑重建检查了 `JIA` 的版本交付目录、原对话工作目录 `work` 和 `建筑项目历史压缩包_20261031` 下的 53 个历史包，重点保留报告视图、实景证据、诊断图与制作中的材质样本。
- 智慧家检查了 `Twin_Preparation` 的初次导入、ModelSync、专题修复、环境和交互验收资料。两条项目对话中的用户附件、本地工具视图与软件操作界面也纳入盘点。缺少明确文件名的对话图使用 UTC 时间、工具图序号或界面名称。
- 航拍与全景原片、ContextCapture 瓦片和缓存、批量生产贴图、电影逐帧输出按原工程路径管理。图档记录用于说明工作的画面，包括修改前、失败尝试、候选、界面参考和保存后的结果。是否通过以对应版本报告为准。
- 松散文件和对话图按原图内容哈希去重；历史压缩包的同路径副本以大小与 CRC 核对，其他归档图读取内容后比对哈希。CSV 中相同编号的多行是同图出处。
- 上传的 `download (1).png`、`download 1(1).png` 对应原工作目录的 V24.22 两张剖切原图，像素与原文件尺寸保留。`download.png` 对应 V24.36 的道路定位网格，公开单张图保留原始分辨率，转为 WebP。

本地索引另保留以下两张对话参考。
- `P8CF7E765` · 整理建筑重建资料（对话，UTC） · `2026-10-25 07:01:33Z/用户问题标注 02 · 9f9c5569c5833aecc0dad885cd970b2.jpg`。系统启动设备界面，项目图档以建模和 UE 验收过程为范围。
- `PCAFE5FCF` · 准备数学孪生智慧家庭模型（对话，UTC） · `2026-10-26 16:39:59Z/用户问题标注 02 · 屏幕截图 2026-10-27 003943.jpg`。外部游戏界面参考，原图随历史对话回查。
