# 日常更新

按实际过程记录续写，最新一轮放在最上面。家庭数字孪生的建模、UE 场景、环境分析与设备准备统一记在仓库 `main`。

## 2026-11-10 · 补录 Codex 的定位、材质和软件操作

- 补记 V7 用户圈画、V24.22 纵向与水平剖面、V24.36 道路坐标网格，以及从诊断到读回核验的步骤。 [定位与剖切](codex-methods.md#从圈画定位到模型坐标)
- 按原报告串起实景取样、照片贴图、灰度浮雕、Blender 局部编辑、Rhino 原生读回及 UE5 重导入。 [Codex 改模方法](codex-methods.md)
- 按工序归档用户标注、诊断图、材质图、工具视图和验收图。每张图可按编号回查版本或历史对话中的出处。 [过程图档与索引](process/README.md)

## 2026-11-09 · 建立家庭数字孪生总台账

- 整理首版到 V26.20 的 82 条建筑重建记录，注明 V24.02 归档与 V26 的来源底稿。[建筑重建台账](reconstruction.md)
- 根据采集者补记，标明 Insta360 全景相机用于地面细节视频，DJI Mini 2 无人机用于地理信息和屋顶鸟瞰照片。[采集资料与建模基线](reconstruction.md#源资料与建模基线)
- 补记原设计图纸、ContextCapture 航拍实景和地面资料各自的用途，记录从 V5 室内校正到 V6 空地配准的过程。[空地融合建模](reconstruction.md#空地融合建模)
- 补记大门等不清晰结构的处理流程，包括实景参考、GPT Image 整体与分解图、倾斜摄影模型量取与 AI 测算，以及整理为 Codex 改模指令。[结构参考与尺寸来源](reconstruction.md#结构参考与尺寸来源)
- 从 Rhino/Datasmith 首次导入接到 22 个 ModelSync 目录，分开记录 21 次保存通过和 1 个候选。另登记门窗、日照、风场与软件设备准备的本地验收。[智慧家台账](smart-home.md)
- 记录全开风场与三向切片的已核验范围。主工程安装的切片蓝图与隔离 PIE 候选文件校验一致。[风环境与三向切片](../case-studies/reconstruction-to-smart-home.zh-CN.md#4-风环境与三向切片)
- 给 82 个重建版本、5 条资料来源和 39 条智慧家记录逐项配图，补齐原图与核验记录的出处。[台账配图出处](media/README.md)

| 门楼与厨房交接 | 储藏房入口台阶 | UE5 三向切片 |
| --- | --- | --- |
| [<img src="media/reconstruction/v24-03.jpg" width="166" alt="V24.03 门楼与厨房接合">](media/reconstruction/v24-03.jpg) | [<img src="media/reconstruction/v26-20.jpg" width="166" alt="V26.20 储藏房入口台阶同机位前后对照">](media/reconstruction/v26-20.jpg) | [<img src="../case-studies/media/reconstruction-to-smart-home/ue-three-slice-panel.png" width="166" alt="UE5 三向切片位置控制">](../case-studies/media/reconstruction-to-smart-home/ue-three-slice-panel.png) |

## 每次更新怎么记

1. **从原工程找变更**。读取当轮交付说明、ModelSync 请求与结果、保存后核验或分析报告。按原编号区分新版本、同版补记、候选和备份。
2. **记录差异与证据**。写实际发生日期、前后版本、对象、单位和依据、结果及局限。新增的现场测量、照片估算、建模目标、模拟和物理反馈分别标明。
3. **准备公开内容**。向相应版本台账增加一行，补本页日期条目并附图。过程图按问题标注、坐标或剖切、材质取样与映射、软件操作、保存后结果补进图档，注明模型或发布号、单位、坐标基准和原文件。只有过程报告时可按记录数据制作核验图，并标明类型。原始场地信息、生产模型、完整日志和设备连接配置在本地管理。
4. **核对后更新主分支**。检查相对链接、图源、报告与摘要一致性。读取最新远端 `main`，以其为父提交，使用快进更新。若远端已前进，先按最新内容整合再提交。没有新证据时以已有台账为准。

每轮较复杂的交付可沿用已有核验模板。 [发布与核验模板](../templates/building-twin-release.zh-CN.md)
