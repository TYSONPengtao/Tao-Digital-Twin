# V7 原实现脚本

[技术文章](../../versions/v7.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 26 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 24 项；站点坐标脱敏 2 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`build_scene_v7.py`](history/build_scene_v7.py)
- [`build_v7_patch.py`](history/build_v7_patch.py)
- [`prepare_v7_final_qa.py`](history/prepare_v7_final_qa.py)
- [`prepare_v7_exports.py`](history/prepare_v7_exports.py)
- [`finish_v7_ridge.py`](history/finish_v7_ridge.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/align_editable_rhino_v7.py](history/align_editable_rhino_v7.py) | 原字节 |
| [history/blender_v7_hybrid.py](history/blender_v7_hybrid.py) | 原字节 |
| [history/build_scene_v7.py](history/build_scene_v7.py) | 原字节 |
| [history/build_v7_patch.py](history/build_v7_patch.py) | 原字节 |
| [history/check_v7_delivery.py](history/check_v7_delivery.py) | 原字节 |
| [history/check_v7_exchange_photos.py](history/check_v7_exchange_photos.py) | 原字节 |
| [history/clean_v7_white_finishes.py](history/clean_v7_white_finishes.py) | 原字节 |
| [history/export_v7_editable.py](history/export_v7_editable.py) | 原字节 |
| [history/export_v7_native.py](history/export_v7_native.py) | 站点坐标脱敏 |
| [history/finalize_v7_views.py](history/finalize_v7_views.py) | 原字节 |
| [history/finish_v7_ridge.py](history/finish_v7_ridge.py) | 原字节 |
| [history/fix_v7_gable_joint.py](history/fix_v7_gable_joint.py) | 原字节 |
| [history/index_v7_target_photos.py](history/index_v7_target_photos.py) | 原字节 |
| [history/inspect_v7_bounds.py](history/inspect_v7_bounds.py) | 原字节 |
| [history/inspect_v7_interior_camera.py](history/inspect_v7_interior_camera.py) | 原字节 |
| [history/inspect_v7_materials.py](history/inspect_v7_materials.py) | 原字节 |
| [history/inspect_v7_scene.py](history/inspect_v7_scene.py) | 原字节 |
| [history/map_v7_gable_photo.py](history/map_v7_gable_photo.py) | 原字节 |
| [history/package_v7_rhino.py](history/package_v7_rhino.py) | 原字节 |
| [history/prepare_v7_exports.py](history/prepare_v7_exports.py) | 原字节 |
| [history/prepare_v7_final_qa.py](history/prepare_v7_final_qa.py) | 原字节 |
| [history/refine_v7_center_glazing.py](history/refine_v7_center_glazing.py) | 原字节 |
| [history/refine_v7_visible_detail.py](history/refine_v7_visible_detail.py) | 原字节 |
| [history/rhino_validate_v7.py](history/rhino_validate_v7.py) | 原字节 |
| [history/v6_alignment_audit/check_rim_3d_v7.py](history/v6_alignment_audit/check_rim_3d_v7.py) | 原字节 |
| [history/write_v7_reports.py](history/write_v7_reports.py) | 站点坐标脱敏 |
