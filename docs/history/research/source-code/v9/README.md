# V9 原实现脚本

[技术文章](../../versions/v9.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 43 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 42 项；站点坐标脱敏 1 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`check_v9_current_baseline.py`](history/check_v9_current_baseline.py)
- [`final_v9_audit.py`](project/07_Evidence/v9_reference_audit/final_v9_audit.py)
- [`mutation.py`](project/07_Evidence/Chinese_Eaves/mutation.py)
- [`audit_v8.py`](project/07_Evidence/v9_reference_audit/audit_v8.py)
- [`prepare_v9.py`](history/prepare_v9.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/align_editable_rhino_v9.py](history/align_editable_rhino_v9.py) | 原字节 |
| [history/blender_v9_hybrid.py](history/blender_v9_hybrid.py) | 原字节 |
| [history/build_v9_patch.py](history/build_v9_patch.py) | 原字节 |
| [history/check_v9_current_baseline.py](history/check_v9_current_baseline.py) | 原字节 |
| [history/check_v9_delivery.py](history/check_v9_delivery.py) | 原字节 |
| [history/check_v9_editable_closed.py](history/check_v9_editable_closed.py) | 原字节 |
| [history/check_v9_exchange_photos.py](history/check_v9_exchange_photos.py) | 原字节 |
| [history/configure_v9_exports.py](history/configure_v9_exports.py) | 原字节 |
| [history/debug_v9_native.py](history/debug_v9_native.py) | 原字节 |
| [history/export_v9_editable.py](history/export_v9_editable.py) | 原字节 |
| [history/export_v9_native.py](history/export_v9_native.py) | 站点坐标脱敏 |
| [history/finalize_v9_assets.py](history/finalize_v9_assets.py) | 原字节 |
| [history/finalize_v9_views.py](history/finalize_v9_views.py) | 原字节 |
| [history/finish_prepare_v9.py](history/finish_prepare_v9.py) | 原字节 |
| [history/merge_v9.py](history/merge_v9.py) | 原字节 |
| [history/package_v9_rhino.py](history/package_v9_rhino.py) | 原字节 |
| [history/prepare_v9.py](history/prepare_v9.py) | 原字节 |
| [history/rhino_validate_v9.py](history/rhino_validate_v9.py) | 原字节 |
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
| [project/07_Evidence/v9_eave_layers/mutation.py](project/07_Evidence/v9_eave_layers/mutation.py) | 原字节 |
| [project/07_Evidence/v9_reference_audit/audit_v8.py](project/07_Evidence/v9_reference_audit/audit_v8.py) | 原字节 |
| [project/07_Evidence/v9_reference_audit/final_v9_audit.py](project/07_Evidence/v9_reference_audit/final_v9_audit.py) | 原字节 |
| [project/07_Evidence/v9_roof_relation/final_review.py](project/07_Evidence/v9_roof_relation/final_review.py) | 原字节 |
| [project/07_Evidence/v9_roof_relation/mutation.py](project/07_Evidence/v9_roof_relation/mutation.py) | 原字节 |
| [project/07_Evidence/v9_roof_relation/roof_parameters.py](project/07_Evidence/v9_roof_relation/roof_parameters.py) | 原字节 |
