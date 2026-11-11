# V26.6 原实现脚本

[技术文章](../../versions/v26-6.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 54 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 54 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`extract_terrace.py`](project/Sources/v26_6_asbuilt_audit/extract_terrace.py)
- [`v26_6_prepare.py`](project/Sources/v26_6_prepare.py)
- [`v26_6_geometry_qa.py`](project/Sources/v26_6_geometry_qa.py)
- [`v26_6_build.py`](project/Sources/v26_6_build.py)
- [`final_geometry_qa.py`](project/Sources/v26_6_ceiling_audit/final_geometry_qa.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v26_6_asbuilt_audit/probe_eave_inside.py](history/v26_6_asbuilt_audit/probe_eave_inside.py) | 原字节 |
| [history/v26_6_asbuilt_audit/probe_saved_deltas.py](history/v26_6_asbuilt_audit/probe_saved_deltas.py) | 原字节 |
| [history/v26_6_asbuilt_audit/probe_video.py](history/v26_6_asbuilt_audit/probe_video.py) | 原字节 |
| [history/v26_6_asbuilt_audit/probe_wall.py](history/v26_6_asbuilt_audit/probe_wall.py) | 原字节 |
| [history/v26_6_asbuilt_audit/write_findings.py](history/v26_6_asbuilt_audit/write_findings.py) | 原字节 |
| [history/v26_6_asbuilt_audit/write_visual_qa.py](history/v26_6_asbuilt_audit/write_visual_qa.py) | 原字节 |
| [history/v26_6_ceiling_audit/all_studio_probe.py](history/v26_6_ceiling_audit/all_studio_probe.py) | 原字节 |
| [history/v26_6_ceiling_audit/forest_probe.py](history/v26_6_ceiling_audit/forest_probe.py) | 原字节 |
| [history/v26_6_ceiling_audit/probes.py](history/v26_6_ceiling_audit/probes.py) | 原字节 |
| [history/v26_6_ceiling_audit/read_shading.py](history/v26_6_ceiling_audit/read_shading.py) | 原字节 |
| [history/v26_6_ceiling_audit/render.py](history/v26_6_ceiling_audit/render.py) | 原字节 |
| [history/v26_6_ceiling_audit/render_landing.py](history/v26_6_ceiling_audit/render_landing.py) | 原字节 |
| [history/v26_6_ceiling_audit/render_southwest.py](history/v26_6_ceiling_audit/render_southwest.py) | 原字节 |
| [history/v26_6_ceiling_audit/render_west_landing.py](history/v26_6_ceiling_audit/render_west_landing.py) | 原字节 |
| [history/v26_6_ceiling_audit/studio_comparison.py](history/v26_6_ceiling_audit/studio_comparison.py) | 原字节 |
| [history/v26_6_make_build.py](history/v26_6_make_build.py) | 原字节 |
| [history/v26_6_material_probe.py](history/v26_6_material_probe.py) | 原字节 |
| [history/v26_6_stair_audit/all_risers.py](history/v26_6_stair_audit/all_risers.py) | 原字节 |
| [history/v26_6_stair_audit/confirm_actual_profile.py](history/v26_6_stair_audit/confirm_actual_profile.py) | 原字节 |
| [history/v26_6_stair_audit/inspect_prepared_faces.py](history/v26_6_stair_audit/inspect_prepared_faces.py) | 原字节 |
| [history/v26_6_stair_audit/landing_faces.py](history/v26_6_stair_audit/landing_faces.py) | 原字节 |
| [history/v26_6_stair_audit/render_landing.py](history/v26_6_stair_audit/render_landing.py) | 原字节 |
| [history/v26_6_stair_audit/render_upper2.py](history/v26_6_stair_audit/render_upper2.py) | 原字节 |
| [history/v26_6_stair_audit/select_actual_references.py](history/v26_6_stair_audit/select_actual_references.py) | 原字节 |
| [history/v26_6_stair_audit/write_visual_qa.py](history/v26_6_stair_audit/write_visual_qa.py) | 原字节 |
| [history/v26_6_step_probe.py](history/v26_6_step_probe.py) | 原字节 |
| [history/v26_6_verify_package.py](history/v26_6_verify_package.py) | 原字节 |
| [project/Roam/measure_tools.py](project/Roam/measure_tools.py) | 原字节 |
| [project/Roam/roam_controller.py](project/Roam/roam_controller.py) | 原字节 |
| [project/Roam/roam_physics.py](project/Roam/roam_physics.py) | 原字节 |
| [project/Roam/start_roam.py](project/Roam/start_roam.py) | 原字节 |
| [project/Sources/v24_06_common.py](project/Sources/v24_06_common.py) | 原字节 |
| [project/Sources/v24_16_common.py](project/Sources/v24_16_common.py) | 原字节 |
| [project/Sources/v24_qa_blender.py](project/Sources/v24_qa_blender.py) | 原字节 |
| [project/Sources/v26_2_common.py](project/Sources/v26_2_common.py) | 原字节 |
| [project/Sources/v26_6_asbuilt_audit/extract_terrace.py](project/Sources/v26_6_asbuilt_audit/extract_terrace.py) | 原字节 |
| [project/Sources/v26_6_asbuilt_audit/saved_capsule_qa.py](project/Sources/v26_6_asbuilt_audit/saved_capsule_qa.py) | 原字节 |
| [project/Sources/v26_6_asbuilt_audit/saved_facade_band_qa.py](project/Sources/v26_6_asbuilt_audit/saved_facade_band_qa.py) | 原字节 |
| [project/Sources/v26_6_asbuilt_audit/saved_native_qa.py](project/Sources/v26_6_asbuilt_audit/saved_native_qa.py) | 原字节 |
| [project/Sources/v26_6_build.py](project/Sources/v26_6_build.py) | 原字节 |
| [project/Sources/v26_6_ceiling_audit/final_geometry_qa.py](project/Sources/v26_6_ceiling_audit/final_geometry_qa.py) | 原字节 |
| [project/Sources/v26_6_ceiling_audit/final_preview_qa.py](project/Sources/v26_6_ceiling_audit/final_preview_qa.py) | 原字节 |
| [project/Sources/v26_6_geometry_qa.py](project/Sources/v26_6_geometry_qa.py) | 原字节 |
| [project/Sources/v26_6_overlap_after.py](project/Sources/v26_6_overlap_after.py) | 原字节 |
| [project/Sources/v26_6_overlap_gate.py](project/Sources/v26_6_overlap_gate.py) | 原字节 |
| [project/Sources/v26_6_package.py](project/Sources/v26_6_package.py) | 原字节 |
| [project/Sources/v26_6_physics_qa.py](project/Sources/v26_6_physics_qa.py) | 原字节 |
| [project/Sources/v26_6_prepare.py](project/Sources/v26_6_prepare.py) | 原字节 |
| [project/Sources/v26_6_protection_qa.py](project/Sources/v26_6_protection_qa.py) | 原字节 |
| [project/Sources/v26_6_readback.py](project/Sources/v26_6_readback.py) | 原字节 |
| [project/Sources/v26_6_render.py](project/Sources/v26_6_render.py) | 原字节 |
| [project/Sources/v26_6_stair_audit/regression_saved.py](project/Sources/v26_6_stair_audit/regression_saved.py) | 原字节 |
| [project/Sources/v26_6_views.py](project/Sources/v26_6_views.py) | 原字节 |
| [project/启动漫游.cmd](project/%E5%90%AF%E5%8A%A8%E6%BC%AB%E6%B8%B8.cmd) | 原字节 |
