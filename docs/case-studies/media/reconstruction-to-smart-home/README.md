# 配图来源与生成记录

图号对应 [从建筑重建到智慧家数字孪生](../../reconstruction-to-smart-home.zh-CN.md)。公开文件使用原画面的缩放或局部裁切，导出时去除了源文件元数据。

| 图号 | 仓库文件 | 来源及处理 |
| --- | --- | --- |
| 01 | [cover-concept.jpg](cover-concept.jpg) | AI 生成封面，虚构院落，转换为 JPEG |
| 02 | [blender-v24-26-brick-closure.jpg](blender-v24-26-brick-closure.jpg) | Blender V24.26 交付渲染 `V24_26_Brick_Closure_Porch.png` |
| 03 | [blender-v24-26-kitchen-verge.jpg](blender-v24-26-kitchen-verge.jpg) | Blender V24.26 交付渲染 `V24_26_Kitchen_Short_Verge.png` |
| 04 | [blender-v24-26-courtyard-wall.jpg](blender-v24-26-courtyard-wall.jpg) | Blender V24.26 交付渲染 `V24_26_Courtyard_Mitre.png` |
| 05 | [blender-v26-19-entry-before.jpg](blender-v26-19-entry-before.jpg) | V26.20 交付报告中的改前渲染 `V26_19_02_Entry_Step_Close.png` |
| 06 | [blender-v26-20-entry-after.jpg](blender-v26-20-entry-after.jpg) | 同机位改后渲染 `V26_20_02_Entry_Step_Close.png` |
| 07 | [datasmith-handoff-concept.jpg](datasmith-handoff-concept.jpg) | AI 生成章节过渡图，虚构门廊，转换为 JPEG |
| 08 | [blender-timber-relief.jpg](blender-timber-relief.jpg) | 雕花工作台 `sculpt_detail.png` 的图文副本 `relief_detail.png` |
| 09 | [ue-day-walkthrough.jpg](ue-day-walkthrough.jpg) | UE5 项目漫游截图 `OurHome1.png` |
| 10 | [ue-night-lighting.jpg](ue-night-lighting.jpg) | UE5 夜间照明截图 `night_white.png`，裁去外围暗区 |
| 11 | [cfd-opening-comparison.png](cfd-opening-comparison.png) | 全开风场核验报告 `三工况同标尺_全年主导风.png`，保留原图尺寸 |
| 12 | [ue-three-slice-panel.png](ue-three-slice-panel.png) | 隔离 PIE 核验 `wind_three_slice_panel.png`，裁取风场与三向切片控制 |

## 两张生成图的原始提示词

封面与过渡图使用 Codex 内置图像生成工具制作。图中建筑均为虚构示意，模型、软件和数值证据见上表相应图号。

<details>
<summary>图 01 · 资料轮廓到数字模型</summary>

> Use case: stylized-concept. Asset type: wide editorial cover image for a Chinese GitHub case study about a real Blender-to-Rhino-to-Unreal courtyard house workflow. Render a single coherent horizontal 2.4:1 illustration on a warm ivory studio background, with generous safe margins and a precise architectural model-making feel. One fictional small southwestern Chinese courtyard house, blue-gray brick, charcoal clay tile roof and warm timber veranda, seen from a calm elevated three-quarter viewpoint. In the left third the house emerges from a few pale survey dots and fine contour pencil lines, the center resolves into a tactile clay/bricked architectural massing model, and the right third of the same coherent courtyard softly transitions to desaturated petrol-teal digital mesh and a few fine luminous guide arcs. Keep the courtyard legible and the architectural character grounded. restrained ink gray, light limestone, soft teal, quiet diffuse light, subtle paper grain, elegant technical editorial art direction. Meaning reads as archival reconstruction becoming a virtual model. This is a fictional concept, no literal address, georeference, real floor plan, UI widgets, scientific numbers, logos, people, text, labels, letters or watermark. Keep major content near central band so image also crops well to 2.4:1.

</details>

<details>
<summary>图 07 · 分解构件到场景装配</summary>

> Use case: stylized-concept. Asset type: horizontal 2.4:1 chapter-divider illustration for a Chinese GitHub architectural digital twin case study, visualizing the handoff from CAD construction parts to a realtime scene. Warm ivory paper studio background, blue-gray brick, charcoal tile, honey timber, muted petrol-teal linework, soft diffuse lighting and subtle grain. A fictional, small courtyard-house bay across one continuous oblique view. Left side shows an exploded roof section, wall module, timber door leaf and hinge axis arranged neatly on an architectural drafting plane. Thin teal alignment lines and a few understated node circles carry the same parts across the center to a fully assembled bay and softly lit timber courtyard doorway at right. Show a distinct architectural section handoff as the editorial idea. No panels or graphic boxes, hardware telemetry, numerical legends, wind data, real floor plan, logos, letters, text, watermark or people. Keep the dominant shapes centered vertically with generous margins. Treat the illustration as a conceptual bridge, not as a screenshot or a photoreal exterior.

</details>
