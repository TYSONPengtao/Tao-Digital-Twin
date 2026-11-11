# V3 原实现脚本

[技术文章](../../versions/v3.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 34 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 30 项；站点坐标脱敏 4 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`gate_levels_v3.py`](project/05_Intermediate/Scripts/gate_levels_v3.py) · 坐标脱敏副本
- [`cc_reference_probe_v3.py`](history/cc_reference_probe_v3.py)
- [`prepare_scene_v3.py`](project/05_Intermediate/Scripts/prepare_scene_v3.py)
- [`geometry_qa_v3.py`](project/05_Intermediate/Scripts/geometry_qa_v3.py)
- [`v3_plan_preview.py`](project/05_Intermediate/Scripts/v3_plan_preview.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/case_obj_views_v3.py](history/case_obj_views_v3.py) | 站点坐标脱敏 |
| [history/cc_reference_probe_v3.py](history/cc_reference_probe_v3.py) | 原字节 |
| [history/inspect_3mx_v3.py](history/inspect_3mx_v3.py) | 原字节 |
| [history/prepare_cc_sdk_v3.py](history/prepare_cc_sdk_v3.py) | 原字节 |
| [history/site_measure_v3.py](history/site_measure_v3.py) | 站点坐标脱敏 |
| [history/source_crops_v3.py](history/source_crops_v3.py) | 原字节 |
| [history/source_views_v3.py](history/source_views_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/annotate_site_v3.py](project/05_Intermediate/Scripts/annotate_site_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/blender_v3.py](project/05_Intermediate/Scripts/blender_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/blender_v3_final.py](project/05_Intermediate/Scripts/blender_v3_final.py) | 原字节 |
| [project/05_Intermediate/Scripts/cc_sdk_inventory_v3.py](project/05_Intermediate/Scripts/cc_sdk_inventory_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/cc_sdk_photos_v3.py](project/05_Intermediate/Scripts/cc_sdk_photos_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/check_exchange_v3.py](project/05_Intermediate/Scripts/check_exchange_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/decode_3mx_v3.py](project/05_Intermediate/Scripts/decode_3mx_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/decoded_reference_views_v3.py](project/05_Intermediate/Scripts/decoded_reference_views_v3.py) | 站点坐标脱敏 |
| [project/05_Intermediate/Scripts/default_site_view_v3.py](project/05_Intermediate/Scripts/default_site_view_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/dji_inventory_v3.py](project/05_Intermediate/Scripts/dji_inventory_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/export_v3.py](project/05_Intermediate/Scripts/export_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/gate_levels_v3.py](project/05_Intermediate/Scripts/gate_levels_v3.py) | 站点坐标脱敏 |
| [project/05_Intermediate/Scripts/geometry_qa_v3.py](project/05_Intermediate/Scripts/geometry_qa_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/inventory_cases_v3.py](project/05_Intermediate/Scripts/inventory_cases_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/package_v3.py](project/05_Intermediate/Scripts/package_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/prepare_exports_v3.py](project/05_Intermediate/Scripts/prepare_exports_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/prepare_scene_v3.py](project/05_Intermediate/Scripts/prepare_scene_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/refine_scene_v2.py](project/05_Intermediate/Scripts/refine_scene_v2.py) | 原字节 |
| [project/05_Intermediate/Scripts/refine_scene_v3.py](project/05_Intermediate/Scripts/refine_scene_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/repair_exchange_v3.py](project/05_Intermediate/Scripts/repair_exchange_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/rhino_validate_v3.py](project/05_Intermediate/Scripts/rhino_validate_v3.py) | 原字节 |
| [project/05_Intermediate/Scripts/site_detail_v3.inc.py](project/05_Intermediate/Scripts/site_detail_v3.inc.py) | 原字节 |
| [project/05_Intermediate/Scripts/skp_api.py](project/05_Intermediate/Scripts/skp_api.py) | 原字节 |
| [project/05_Intermediate/Scripts/su_hole_fill.py](project/05_Intermediate/Scripts/su_hole_fill.py) | 原字节 |
| [project/05_Intermediate/Scripts/v2_geometry.py](project/05_Intermediate/Scripts/v2_geometry.py) | 原字节 |
| [project/05_Intermediate/Scripts/v3_plan_preview.py](project/05_Intermediate/Scripts/v3_plan_preview.py) | 原字节 |
| [project/05_Intermediate/Scripts/write_v3_reports.py](project/05_Intermediate/Scripts/write_v3_reports.py) | 原字节 |
