# V8 原实现脚本

[技术文章](../../versions/v8.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 56 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 54 项；站点坐标脱敏 2 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`prepare_v8.py`](history/prepare_v8.py)
- [`build_v8_patch.py`](history/build_v8_patch.py)
- [`export_v8_interaction_registry.py`](history/export_v8_interaction_registry.py)
- [`prepare_v8_render.py`](history/prepare_v8_render.py)
- [`prepare_v8_pipeline.py`](history/prepare_v8_pipeline.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/align_editable_rhino_v8.py](history/align_editable_rhino_v8.py) | 原字节 |
| [history/apply_v8_ground_seams.py](history/apply_v8_ground_seams.py) | 原字节 |
| [history/blender_v8_hybrid.py](history/blender_v8_hybrid.py) | 原字节 |
| [history/build_v8_patch.py](history/build_v8_patch.py) | 原字节 |
| [history/check_v8_delivery.py](history/check_v8_delivery.py) | 原字节 |
| [history/check_v8_exchange_photos.py](history/check_v8_exchange_photos.py) | 原字节 |
| [history/clean_v8_white_finishes.py](history/clean_v8_white_finishes.py) | 原字节 |
| [history/complete_v8_report_state.py](history/complete_v8_report_state.py) | 原字节 |
| [history/diagnose_v8_normals.py](history/diagnose_v8_normals.py) | 原字节 |
| [history/export_v8_editable.py](history/export_v8_editable.py) | 原字节 |
| [history/export_v8_interaction_registry.py](history/export_v8_interaction_registry.py) | 原字节 |
| [history/export_v8_native.py](history/export_v8_native.py) | 站点坐标脱敏 |
| [history/finalize_v8_reports.py](history/finalize_v8_reports.py) | 站点坐标脱敏 |
| [history/finalize_v8_views.py](history/finalize_v8_views.py) | 原字节 |
| [history/inspect_v8_coverage.py](history/inspect_v8_coverage.py) | 原字节 |
| [history/merge_v8_scene.py](history/merge_v8_scene.py) | 原字节 |
| [history/package_v8_rhino.py](history/package_v8_rhino.py) | 原字节 |
| [history/prepare_v8.py](history/prepare_v8.py) | 原字节 |
| [history/prepare_v8_pipeline.py](history/prepare_v8_pipeline.py) | 原字节 |
| [history/prepare_v8_render.py](history/prepare_v8_render.py) | 原字节 |
| [history/render_v8_stair_preview.py](history/render_v8_stair_preview.py) | 原字节 |
| [history/rhino_validate_v8.py](history/rhino_validate_v8.py) | 原字节 |
| [history/update_v8_blender_ground.py](history/update_v8_blender_ground.py) | 原字节 |
| [history/v8_column_arch.py](history/v8_column_arch.py) | 原字节 |
| [history/v8_final_timber_nodes.py](history/v8_final_timber_nodes.py) | 原字节 |
| [history/v8_scope_and_cleanup.py](history/v8_scope_and_cleanup.py) | 原字节 |
| [history/v8_terrain_clear/check_contact_ground_continuity.py](history/v8_terrain_clear/check_contact_ground_continuity.py) | 原字节 |
| [history/v8_terrain_clear/check_contact_ground_stable.py](history/v8_terrain_clear/check_contact_ground_stable.py) | 原字节 |
| [history/v8_terrain_clear/check_contact_support.py](history/v8_terrain_clear/check_contact_support.py) | 原字节 |
| [history/v8_terrain_clear/contact_base_ground.py](history/v8_terrain_clear/contact_base_ground.py) | 原字节 |
| [history/v8_terrain_clear/contact_ground_inspect.py](history/v8_terrain_clear/contact_ground_inspect.py) | 原字节 |
| [history/v8_terrain_clear/inspect_contact_base_support.py](history/v8_terrain_clear/inspect_contact_base_support.py) | 原字节 |
| [history/v8_terrain_clear/inspect_projection_switch.py](history/v8_terrain_clear/inspect_projection_switch.py) | 原字节 |
| [history/v8_terrain_clear/prepare_contact_ground_gap.py](history/v8_terrain_clear/prepare_contact_ground_gap.py) | 原字节 |
| [history/v8_terrain_clear/prepare_contact_ground_gap_stable.py](history/v8_terrain_clear/prepare_contact_ground_gap_stable.py) | 原字节 |
| [history/v9_reference_audit/audit_v8.py](history/v9_reference_audit/audit_v8.py) | 原字节 |
| [history/write_v8_working_base.py](history/write_v8_working_base.py) | 原字节 |
| [project/07_Evidence/Chinese_Eaves/mutation.py](project/07_Evidence/Chinese_Eaves/mutation.py) | 原字节 |
| [project/07_Evidence/Chinese_Eaves/preview_blender.py](project/07_Evidence/Chinese_Eaves/preview_blender.py) | 原字节 |
| [project/07_Evidence/Chinese_Eaves/preview_geometry.py](project/07_Evidence/Chinese_Eaves/preview_geometry.py) | 原字节 |
| [project/07_Evidence/Interior/final_merged_audit.py](project/07_Evidence/Interior/final_merged_audit.py) | 原字节 |
| [project/07_Evidence/Interior/mutation.py](project/07_Evidence/Interior/mutation.py) | 原字节 |
| [project/07_Evidence/Interior/preview.py](project/07_Evidence/Interior/preview.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/analyze.py](project/07_Evidence/Terrain_Clearance/analyze.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/apply_to_v8.py](project/07_Evidence/Terrain_Clearance/apply_to_v8.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/base_counts.py](project/07_Evidence/Terrain_Clearance/base_counts.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/calibrate.py](project/07_Evidence/Terrain_Clearance/calibrate.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/check_clearance.py](project/07_Evidence/Terrain_Clearance/check_clearance.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/hulls.py](project/07_Evidence/Terrain_Clearance/hulls.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/inventory.py](project/07_Evidence/Terrain_Clearance/inventory.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/mask_scope.py](project/07_Evidence/Terrain_Clearance/mask_scope.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/plot_ground_class.py](project/07_Evidence/Terrain_Clearance/plot_ground_class.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/plot_top.py](project/07_Evidence/Terrain_Clearance/plot_top.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/plot_v8_top.py](project/07_Evidence/Terrain_Clearance/plot_v8_top.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/prepare_clearance.py](project/07_Evidence/Terrain_Clearance/prepare_clearance.py) | 原字节 |
| [project/07_Evidence/Terrain_Clearance/quad_count.py](project/07_Evidence/Terrain_Clearance/quad_count.py) | 原字节 |
