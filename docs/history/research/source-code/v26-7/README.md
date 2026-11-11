# V26.7 原实现脚本

[技术文章](../../versions/v26-7.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 62 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 62 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v26_7_gate_prepare.py`](project/Sources/v26_7_gate_prepare.py)
- [`v26_7_probe.py`](history/v26_7_probe.py)
- [`v26_7_geometry_qa.py`](project/Sources/v26_7_geometry_qa.py)
- [`v26_7_build.py`](project/Sources/v26_7_build.py)
- [`build_candidate.py`](project/Sources/v26_7_railing_audit/build_candidate.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v26_7_column_audit/all_columns_audit.py](history/v26_7_column_audit/all_columns_audit.py) | 原字节 |
| [history/v26_7_column_audit/candidate_qa.py](history/v26_7_column_audit/candidate_qa.py) | 原字节 |
| [history/v26_7_column_audit/profiles.py](history/v26_7_column_audit/profiles.py) | 原字节 |
| [history/v26_7_column_audit/render.py](history/v26_7_column_audit/render.py) | 原字节 |
| [history/v26_7_degenerate_probe.py](history/v26_7_degenerate_probe.py) | 原字节 |
| [history/v26_7_delta_probe.py](history/v26_7_delta_probe.py) | 原字节 |
| [history/v26_7_door_corner_diagnostic.py](history/v26_7_door_corner_diagnostic.py) | 原字节 |
| [history/v26_7_duplicate_probe.py](history/v26_7_duplicate_probe.py) | 原字节 |
| [history/v26_7_final_diagnostics.py](history/v26_7_final_diagnostics.py) | 原字节 |
| [history/v26_7_gate_components.py](history/v26_7_gate_components.py) | 原字节 |
| [history/v26_7_gate_fine.py](history/v26_7_gate_fine.py) | 原字节 |
| [history/v26_7_gate_probe.py](history/v26_7_gate_probe.py) | 原字节 |
| [history/v26_7_gate_video.py](history/v26_7_gate_video.py) | 原字节 |
| [history/v26_7_prepare_verify.py](history/v26_7_prepare_verify.py) | 原字节 |
| [history/v26_7_probe.py](history/v26_7_probe.py) | 原字节 |
| [history/v26_7_railing_audit/add_end_infills.py](history/v26_7_railing_audit/add_end_infills.py) | 原字节 |
| [history/v26_7_railing_audit/fix_candidate_seats.py](history/v26_7_railing_audit/fix_candidate_seats.py) | 原字节 |
| [history/v26_7_railing_audit/make_candidate_script.py](history/v26_7_railing_audit/make_candidate_script.py) | 原字节 |
| [history/v26_7_railing_audit/qa_candidate.py](history/v26_7_railing_audit/qa_candidate.py) | 原字节 |
| [history/v26_7_railing_audit/recipe_probe.py](history/v26_7_railing_audit/recipe_probe.py) | 原字节 |
| [history/v26_7_railing_audit/render_preview.py](history/v26_7_railing_audit/render_preview.py) | 原字节 |
| [history/v26_7_site_audit/inspect_site.py](history/v26_7_site_audit/inspect_site.py) | 原字节 |
| [history/v26_7_site_audit/lower_mapping.py](history/v26_7_site_audit/lower_mapping.py) | 原字节 |
| [history/v26_7_site_audit/prepare_site.py](history/v26_7_site_audit/prepare_site.py) | 原字节 |
| [history/v26_7_site_audit/test_materials_blender.py](history/v26_7_site_audit/test_materials_blender.py) | 原字节 |
| [history/v26_7_stair_audit/probe_corners.py](history/v26_7_stair_audit/probe_corners.py) | 原字节 |
| [history/v26_7_stair_audit/probe_planes.py](history/v26_7_stair_audit/probe_planes.py) | 原字节 |
| [history/v26_7_stair_audit/write_findings.py](history/v26_7_stair_audit/write_findings.py) | 原字节 |
| [history/v26_7_verify_package.py](history/v26_7_verify_package.py) | 原字节 |
| [history/v26_7_visual_probe.py](history/v26_7_visual_probe.py) | 原字节 |
| [project/Roam/measure_tools.py](project/Roam/measure_tools.py) | 原字节 |
| [project/Roam/roam_controller.py](project/Roam/roam_controller.py) | 原字节 |
| [project/Roam/roam_physics.py](project/Roam/roam_physics.py) | 原字节 |
| [project/Roam/start_roam.py](project/Roam/start_roam.py) | 原字节 |
| [project/Sources/v24_06_common.py](project/Sources/v24_06_common.py) | 原字节 |
| [project/Sources/v24_16_common.py](project/Sources/v24_16_common.py) | 原字节 |
| [project/Sources/v24_qa_blender.py](project/Sources/v24_qa_blender.py) | 原字节 |
| [project/Sources/v26_2_common.py](project/Sources/v26_2_common.py) | 原字节 |
| [project/Sources/v26_7_build.py](project/Sources/v26_7_build.py) | 原字节 |
| [project/Sources/v26_7_collect.py](project/Sources/v26_7_collect.py) | 原字节 |
| [project/Sources/v26_7_column_audit/prepare_candidate.py](project/Sources/v26_7_column_audit/prepare_candidate.py) | 原字节 |
| [project/Sources/v26_7_column_audit/saved_native_qa.py](project/Sources/v26_7_column_audit/saved_native_qa.py) | 原字节 |
| [project/Sources/v26_7_extra_checks.py](project/Sources/v26_7_extra_checks.py) | 原字节 |
| [project/Sources/v26_7_finalize_house.py](project/Sources/v26_7_finalize_house.py) | 原字节 |
| [project/Sources/v26_7_gate_prepare.py](project/Sources/v26_7_gate_prepare.py) | 原字节 |
| [project/Sources/v26_7_gate_qa.py](project/Sources/v26_7_gate_qa.py) | 原字节 |
| [project/Sources/v26_7_geometry_qa.py](project/Sources/v26_7_geometry_qa.py) | 原字节 |
| [project/Sources/v26_7_make_checks.py](project/Sources/v26_7_make_checks.py) | 原字节 |
| [project/Sources/v26_7_overlap_after.py](project/Sources/v26_7_overlap_after.py) | 原字节 |
| [project/Sources/v26_7_overlap_gate.py](project/Sources/v26_7_overlap_gate.py) | 原字节 |
| [project/Sources/v26_7_package.py](project/Sources/v26_7_package.py) | 原字节 |
| [project/Sources/v26_7_physics_qa.py](project/Sources/v26_7_physics_qa.py) | 原字节 |
| [project/Sources/v26_7_protection_qa.py](project/Sources/v26_7_protection_qa.py) | 原字节 |
| [project/Sources/v26_7_railing_audit/build_candidate.py](project/Sources/v26_7_railing_audit/build_candidate.py) | 原字节 |
| [project/Sources/v26_7_railing_audit/saved_native_qa.py](project/Sources/v26_7_railing_audit/saved_native_qa.py) | 原字节 |
| [project/Sources/v26_7_readback.py](project/Sources/v26_7_readback.py) | 原字节 |
| [project/Sources/v26_7_render.py](project/Sources/v26_7_render.py) | 原字节 |
| [project/Sources/v26_7_site_audit/apply_site_materials.py](project/Sources/v26_7_site_audit/apply_site_materials.py) | 原字节 |
| [project/Sources/v26_7_site_audit/saved_material_qa.py](project/Sources/v26_7_site_audit/saved_material_qa.py) | 原字节 |
| [project/Sources/v26_7_views.py](project/Sources/v26_7_views.py) | 原字节 |
| [project/Sources/v26_7_visual_qa.py](project/Sources/v26_7_visual_qa.py) | 原字节 |
| [project/启动漫游.cmd](project/%E5%90%AF%E5%8A%A8%E6%BC%AB%E6%B8%B8.cmd) | 原字节 |
