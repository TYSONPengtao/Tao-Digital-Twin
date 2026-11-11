# V5 原实现脚本

[技术文章](../../versions/v5.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 55 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 55 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`extract_views.py`](history/v5_video_plan/extract_views.py)
- [`build_scene_v5.py`](project/05_Intermediate/Scripts/build_scene_v5.py)
- [`prepare_v5.py`](project/05_Intermediate/Scripts/prepare_v5.py)
- [`geometry_qa_v5.py`](project/05_Intermediate/Scripts/geometry_qa_v5.py)
- [`audit.py`](history/v5_model_audit/audit.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/inspect_v5_inputs.py](history/inspect_v5_inputs.py) | 原字节 |
| [history/v5_delivery_review/audit_scene_doors.py](history/v5_delivery_review/audit_scene_doors.py) | 原字节 |
| [history/v5_delivery_review/door_pivot_helper.py](history/v5_delivery_review/door_pivot_helper.py) | 原字节 |
| [history/v5_delivery_review/export_door_leaf_assets.py](history/v5_delivery_review/export_door_leaf_assets.py) | 原字节 |
| [history/v5_delivery_review/pivot_export_smoke.py](history/v5_delivery_review/pivot_export_smoke.py) | 原字节 |
| [history/v5_delivery_review/produce_leaf_assets_v5.py](history/v5_delivery_review/produce_leaf_assets_v5.py) | 原字节 |
| [history/v5_delivery_review/readback_final_v5.py](history/v5_delivery_review/readback_final_v5.py) | 原字节 |
| [history/v5_delivery_review/readback_native_v5.py](history/v5_delivery_review/readback_native_v5.py) | 原字节 |
| [history/v5_model_audit/audit.py](history/v5_model_audit/audit.py) | 原字节 |
| [history/v5_model_audit/check_patch_helper.py](history/v5_model_audit/check_patch_helper.py) | 原字节 |
| [history/v5_model_audit/check_v5_layout.py](history/v5_model_audit/check_v5_layout.py) | 原字节 |
| [history/v5_model_audit/inspect_front.py](history/v5_model_audit/inspect_front.py) | 原字节 |
| [history/v5_model_audit/inspect_scene_data.py](history/v5_model_audit/inspect_scene_data.py) | 原字节 |
| [history/v5_model_audit/render_v5_comparison.py](history/v5_model_audit/render_v5_comparison.py) | 原字节 |
| [history/v5_model_audit/wall_opening_patch.py](history/v5_model_audit/wall_opening_patch.py) | 原字节 |
| [history/v5_video_plan/extract_views.py](history/v5_video_plan/extract_views.py) | 原字节 |
| [history/v5_video_plan/inspect_scene.py](history/v5_video_plan/inspect_scene.py) | 原字节 |
| [history/v5_video_plan/write_proposal.py](history/v5_video_plan/write_proposal.py) | 原字节 |
| [project/05_Intermediate/Scripts/blender_v5.py](project/05_Intermediate/Scripts/blender_v5.py) | 原字节 |
| [project/05_Intermediate/Scripts/build_scene_v5.py](project/05_Intermediate/Scripts/build_scene_v5.py) | 原字节 |
| [project/05_Intermediate/Scripts/check_exchange_v5.py](project/05_Intermediate/Scripts/check_exchange_v5.py) | 原字节 |
| [project/05_Intermediate/Scripts/default_site_view_v5.py](project/05_Intermediate/Scripts/default_site_view_v5.py) | 原字节 |
| [project/05_Intermediate/Scripts/export_v5.py](project/05_Intermediate/Scripts/export_v5.py) | 原字节 |
| [project/05_Intermediate/Scripts/geometry_qa_v5.py](project/05_Intermediate/Scripts/geometry_qa_v5.py) | 原字节 |
| [project/05_Intermediate/Scripts/prepare_v5.py](project/05_Intermediate/Scripts/prepare_v5.py) | 原字节 |
| [project/05_Intermediate/Scripts/preview_v5_interiors.py](project/05_Intermediate/Scripts/preview_v5_interiors.py) | 原字节 |
| [project/05_Intermediate/Scripts/repair_exchange_v5.py](project/05_Intermediate/Scripts/repair_exchange_v5.py) | 原字节 |
| [project/05_Intermediate/Scripts/rhino_validate_v5.py](project/05_Intermediate/Scripts/rhino_validate_v5.py) | 原字节 |
| [project/05_Intermediate/Scripts/write_v5_report.py](project/05_Intermediate/Scripts/write_v5_report.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/append_findings.py](project/11_Construction_Reference/v4_audit_codes/append_findings.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/check_construction_v4.py](project/11_Construction_Reference/v4_audit_codes/check_construction_v4.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/crop_design.py](project/11_Construction_Reference/v4_audit_codes/crop_design.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/crop_levels.py](project/11_Construction_Reference/v4_audit_codes/crop_levels.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/extract.py](project/11_Construction_Reference/v4_audit_codes/extract.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/extract_codes.py](project/11_Construction_Reference/v4_audit_codes/extract_codes.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/get_official.py](project/11_Construction_Reference/v4_audit_codes/get_official.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/render_codes.py](project/11_Construction_Reference/v4_audit_codes/render_codes.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/render_more.py](project/11_Construction_Reference/v4_audit_codes/render_more.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/render_selected.py](project/11_Construction_Reference/v4_audit_codes/render_selected.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_codes/write_audit.py](project/11_Construction_Reference/v4_audit_codes/write_audit.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_junction/apply_junction_v4.py](project/11_Construction_Reference/v4_audit_junction/apply_junction_v4.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_junction/audit.py](project/11_Construction_Reference/v4_audit_junction/audit.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_junction/bbox.py](project/11_Construction_Reference/v4_audit_junction/bbox.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_junction/check_final_v4.py](project/11_Construction_Reference/v4_audit_junction/check_final_v4.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_junction/fix_screen_relief_backing.py](project/11_Construction_Reference/v4_audit_junction/fix_screen_relief_backing.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_junction/test_apply.py](project/11_Construction_Reference/v4_audit_junction/test_apply.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_junction/test_screen_relief.py](project/11_Construction_Reference/v4_audit_junction/test_screen_relief.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_junction/verify_apply.py](project/11_Construction_Reference/v4_audit_junction/verify_apply.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_junction/write_report.py](project/11_Construction_Reference/v4_audit_junction/write_report.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_safety/apply_safety_v4.py](project/11_Construction_Reference/v4_audit_safety/apply_safety_v4.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_safety/bounds.py](project/11_Construction_Reference/v4_audit_safety/bounds.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_safety/crop.py](project/11_Construction_Reference/v4_audit_safety/crop.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_safety/qa_apply_safety_v4.py](project/11_Construction_Reference/v4_audit_safety/qa_apply_safety_v4.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_safety/source_render.py](project/11_Construction_Reference/v4_audit_safety/source_render.py) | 原字节 |
| [project/11_Construction_Reference/v4_audit_safety/source_render11.py](project/11_Construction_Reference/v4_audit_safety/source_render11.py) | 原字节 |
