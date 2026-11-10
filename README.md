# TAO 家庭数字孪生

同一套家庭住宅从实景资料和可编辑模型开始，经 Blender、Rhino 和 Datasmith 进入 UE5，逐轮完善漫游、门窗、日照、夜间照明与风环境。设备登记与本地软件灯作为接入准备，Web 端用于模拟遥测。

原有设计图纸提供轴网与尺寸基线。DJI Mini 2 采集的航拍照片经 ContextCapture（CC）生成倾斜摄影实景模型，Insta360 地面全景视频与实景照片补足室内和近地面细节，再按现场证据和逐轮指令修订可编辑模型。[采集资料与空地融合](docs/history/reconstruction.md#源资料与建模基线)

结构看不清时，用 GPT Image 根据实景照片制作整体设计图和构件分解图。具体建模尺寸结合倾斜摄影模型量取与 AI 辅助测算，再将图、尺寸和改动要求整理成 Codex 改模指令。[大门改模示例](docs/case-studies/residential-reconstruction.zh-CN.md#大门结构推敲与改模)

| 建筑重建 | 智慧家场景 |
| --- | --- |
| ![V24.26 内院围墙瓦顶转角的 Blender 渲染](docs/case-studies/media/reconstruction-to-smart-home/blender-v24-26-courtyard-wall.jpg) | ![UE5 人物在住宅木构檐廊下漫游](docs/case-studies/media/reconstruction-to-smart-home/ue-day-walkthrough.jpg) |

## 迭代与日常更新

| 入口 | 内容 |
| --- | --- |
| [项目总台账](docs/history/README.md) | 两个过程项目在同一条住宅数字孪生时间线中的衔接与来源。 |
| [建筑重建逐版记录](docs/history/reconstruction.md) | 从首版到 V26.20，82 个版本各有可展开的过程图。 |
| [智慧家逐版记录](docs/history/smart-home.md) | 从 Rhino / Datasmith 转换到 UE5 交互与环境分析，共 42 条带图记录。 |
| [Codex 改模方法与过程图档](docs/history/codex-methods.md) | 用户圈画如何定位到坐标和对象，如何取样与制作材质，以及 Blender、Rhino、UE5 的操作和保存后核验。 |
| [按迭代查研究方法](docs/history/research/README.md) | 82 个建筑版本与 42 条智慧家记录的输入、算法、出图和核验。凉亭散点图有原数据复算。 |
| [日常更新](docs/history/updates.md) | 按实际过程文件和对应图源续记，统一更新 `main`。 |
| [图文案例](docs/case-studies/reconstruction-to-smart-home.zh-CN.md) | 台阶前后、构件交接、昼夜场景、三工况和三向风场切片。 |

## 当前进度

- **建筑与场景**。V26.20 是住宅重建交付基线。UE5 当前模型发布号 `20261030_025240_41748228`，登记 819 个构件，处于编辑器与 PIE 迭代阶段。
- **环境**。可切换门窗关闭、厨房四窗双门开启、全场地门窗全开，查看 OpenFOAM 代表风与三个方向的切片。日照是场景预览，CFD 用于对照和交互。
- **设备**。本地已验证设备目录与软件灯路径。真实灯具、电机、传感器和监控码流处于绑定准备阶段。 [智慧家领域](domains/smart_home/README.md)
- **Web**。React/Three.js 场景和 FastAPI 提供模拟设备与 WebSocket 遥测。 [本地演示](frontend/README.md)

## 工程文档

| 内容 | 文档 |
| --- | --- |
| 资料、构件和漫游 | [住宅建模方法](docs/case-studies/residential-reconstruction.zh-CN.md) |
| Datasmith 重导入、UE5 交互与 CFD | [建筑数字孪生制作实战](docs/case-studies/ue5-building-twin.zh-CN.md) |
| 场景、状态、命令和设备接入 | [家庭孪生架构](docs/architecture.md) · [UE 客户端](clients/unreal/README.md) · [领域模型](docs/domain-model.md) |
| 协议、设备闭环与安全 | [协议](docs/protocols.md) · [安全](docs/security.md) · [家庭路线图](docs/roadmap.md) |
| 下一轮建模与发布 | [发布与核验模板](docs/templates/building-twin-release.zh-CN.md) |

项目过程来源为“整理建筑重建资料”和“准备数学孪生智慧家庭模型”。公开仓库记录精选图文、核验摘要与 Web 模拟原型。 [来源索引](docs/history/README.md#过程来源)

维护者 TYSON Pengtao
