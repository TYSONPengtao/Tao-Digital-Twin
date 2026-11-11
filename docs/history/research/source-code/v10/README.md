# V10 原实现脚本

[技术文章](../../versions/v10.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 36 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 34 项；站点坐标脱敏 2 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v10_wall_audit_faces.py`](history/v10_wall_audit_faces.py)
- [`v10_wall_audit_openings.py`](history/v10_wall_audit_openings.py)
- [`export_v10_changed_cad.py`](history/export_v10_changed_cad.py)
- [`mutation.py`](project/07_Evidence/v10_courtyard_wall/mutation.py)
- [`extend_audit.py`](project/07_Evidence/v10_wall_audit/extend_audit.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/blender_v10_hybrid.py](history/blender_v10_hybrid.py) | 原字节 |
| [history/build_v10_full_walls.py](history/build_v10_full_walls.py) | 原字节 |
| [history/build_v10_patch.py](history/build_v10_patch.py) | 原字节 |
| [history/check_v10_delivery.py](history/check_v10_delivery.py) | 原字节 |
| [history/check_v10_exchange_photos.py](history/check_v10_exchange_photos.py) | 原字节 |
| [history/configure_v10.py](history/configure_v10.py) | 原字节 |
| [history/configure_v10_render.py](history/configure_v10_render.py) | 原字节 |
| [history/export_v10_changed_cad.py](history/export_v10_changed_cad.py) | 原字节 |
| [history/export_v10_native.py](history/export_v10_native.py) | 站点坐标脱敏 |
| [history/finalize_v10.py](history/finalize_v10.py) | 原字节 |
| [history/merge_v10.py](history/merge_v10.py) | 原字节 |
| [history/merge_v10_cad.py](history/merge_v10_cad.py) | 原字节 |
| [history/package_v10.py](history/package_v10.py) | 原字节 |
| [history/prepare_v10.py](history/prepare_v10.py) | 原字节 |
| [history/render_v10_complete_wall.py](history/render_v10_complete_wall.py) | 原字节 |
| [history/v10_wall_audit_faces.py](history/v10_wall_audit_faces.py) | 原字节 |
| [history/v10_wall_audit_inventory.py](history/v10_wall_audit_inventory.py) | 原字节 |
| [history/v10_wall_audit_lengths.py](history/v10_wall_audit_lengths.py) | 原字节 |
| [history/v10_wall_audit_meta.py](history/v10_wall_audit_meta.py) | 原字节 |
| [history/v10_wall_audit_openings.py](history/v10_wall_audit_openings.py) | 原字节 |
| [history/validate_v10_changed_cad.py](history/validate_v10_changed_cad.py) | 原字节 |
| [history/write_v10_audit_notes.py](history/write_v10_audit_notes.py) | 原字节 |
| [project/07_Evidence/v10_courtyard_wall/mutation.py](project/07_Evidence/v10_courtyard_wall/mutation.py) | 原字节 |
| [project/07_Evidence/v10_courtyard_wall/preview.py](project/07_Evidence/v10_courtyard_wall/preview.py) | 原字节 |
| [project/07_Evidence/v10_courtyard_wall/render_preview.py](project/07_Evidence/v10_courtyard_wall/render_preview.py) | 原字节 |
| [project/07_Evidence/v10_courtyard_wall/write_hole_probes.py](project/07_Evidence/v10_courtyard_wall/write_hole_probes.py) | 原字节 |
| [project/07_Evidence/v10_perimeter_detail/mutation.py](project/07_Evidence/v10_perimeter_detail/mutation.py) | 原字节 |
| [project/07_Evidence/v10_perimeter_detail/preview.py](project/07_Evidence/v10_perimeter_detail/preview.py) | 原字节 |
| [project/07_Evidence/v10_wall_audit/audit_mutations.py](project/07_Evidence/v10_wall_audit/audit_mutations.py) | 原字节 |
| [project/07_Evidence/v10_wall_audit/extend_audit.py](project/07_Evidence/v10_wall_audit/extend_audit.py) | 原字节 |
| [project/07_Evidence/v10_wall_audit/extend_full_holes.py](project/07_Evidence/v10_wall_audit/extend_full_holes.py) | 原字节 |
| [project/07_Evidence/v10_wall_audit/inspect_cannopy.py](project/07_Evidence/v10_wall_audit/inspect_cannopy.py) | 原字节 |
| [project/07_Evidence/v10_wall_audit/inspect_corner_bounds.py](project/07_Evidence/v10_wall_audit/inspect_corner_bounds.py) | 原字节 |
| [project/07_Evidence/v10_wall_audit/inspect_corner_probe.py](project/07_Evidence/v10_wall_audit/inspect_corner_probe.py) | 原字节 |
| [project/07_Evidence/v10_wall_audit/inspect_pier.py](project/07_Evidence/v10_wall_audit/inspect_pier.py) | 原字节 |
| [project/07_Evidence/v10_wall_audit/make_report.py](project/07_Evidence/v10_wall_audit/make_report.py) | 站点坐标脱敏 |
