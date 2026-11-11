# V11 原实现脚本

[技术文章](../../versions/v11.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 50 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 47 项；站点坐标脱敏 3 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`scan_levels.py`](project/07_Evidence/v11_outer_gate/scan_levels.py) · 坐标脱敏副本
- [`profile_gate.py`](project/07_Evidence/v11_outer_gate/profile_gate.py) · 坐标脱敏副本
- [`build_pavilion.py`](project/07_Evidence/v11_pavilion/build_pavilion.py)
- [`prepare.py`](project/07_Evidence/v11_ground_gap/prepare.py)
- [`mutation.py`](project/07_Evidence/v11_kitchen_interface/mutation.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/append_v11_ground_repair.py](history/append_v11_ground_repair.py) | 原字节 |
| [history/blender_v11_hybrid.py](history/blender_v11_hybrid.py) | 原字节 |
| [history/build_v11_full_site.py](history/build_v11_full_site.py) | 原字节 |
| [history/build_v11_patch.py](history/build_v11_patch.py) | 原字节 |
| [history/check_v11_delivery.py](history/check_v11_delivery.py) | 原字节 |
| [history/check_v11_exchange_photos.py](history/check_v11_exchange_photos.py) | 原字节 |
| [history/clean_v11_companion_definitions.py](history/clean_v11_companion_definitions.py) | 原字节 |
| [history/configure_v11.py](history/configure_v11.py) | 原字节 |
| [history/configure_v11_reviews.py](history/configure_v11_reviews.py) | 原字节 |
| [history/export_v11_changed_cad.py](history/export_v11_changed_cad.py) | 原字节 |
| [history/export_v11_native.py](history/export_v11_native.py) | 站点坐标脱敏 |
| [history/final_v11_site_qa.py](history/final_v11_site_qa.py) | 原字节 |
| [history/finalize_v11.py](history/finalize_v11.py) | 原字节 |
| [history/finish_v11_ground_repair.py](history/finish_v11_ground_repair.py) | 原字节 |
| [history/merge_v11.py](history/merge_v11.py) | 原字节 |
| [history/merge_v11_cad.py](history/merge_v11_cad.py) | 原字节 |
| [history/package_v11.py](history/package_v11.py) | 原字节 |
| [history/prepare_v11.py](history/prepare_v11.py) | 原字节 |
| [history/repair_v11_gate_solids.py](history/repair_v11_gate_solids.py) | 原字节 |
| [history/v11_delivery_independent/audit.py](history/v11_delivery_independent/audit.py) | 原字节 |
| [history/v11_delivery_independent/audit_companion.py](history/v11_delivery_independent/audit_companion.py) | 原字节 |
| [history/v11_delivery_independent/audit_glb.py](history/v11_delivery_independent/audit_glb.py) | 原字节 |
| [history/v11_delivery_independent/reflect_definition_api.py](history/v11_delivery_independent/reflect_definition_api.py) | 原字节 |
| [history/v11_reference_audit/deps/rawpy/__init__.py](history/v11_reference_audit/deps/rawpy/__init__.py) | 原字节 |
| [history/v11_reference_audit/deps/rawpy/_version.py](history/v11_reference_audit/deps/rawpy/_version.py) | 原字节 |
| [history/v11_reference_audit/deps/rawpy/enhance.py](history/v11_reference_audit/deps/rawpy/enhance.py) | 原字节 |
| [history/validate_v11_changed_cad.py](history/validate_v11_changed_cad.py) | 原字节 |
| [project/07_Evidence/v11_ground_gap/diagnose.py](project/07_Evidence/v11_ground_gap/diagnose.py) | 原字节 |
| [project/07_Evidence/v11_ground_gap/kernel_validate.py](project/07_Evidence/v11_ground_gap/kernel_validate.py) | 原字节 |
| [project/07_Evidence/v11_ground_gap/prepare.py](project/07_Evidence/v11_ground_gap/prepare.py) | 原字节 |
| [project/07_Evidence/v11_kitchen_interface/correct_interface.py](project/07_Evidence/v11_kitchen_interface/correct_interface.py) | 原字节 |
| [project/07_Evidence/v11_kitchen_interface/frozen_audit.py](project/07_Evidence/v11_kitchen_interface/frozen_audit.py) | 原字节 |
| [project/07_Evidence/v11_kitchen_interface/mutation.py](project/07_Evidence/v11_kitchen_interface/mutation.py) | 原字节 |
| [project/07_Evidence/v11_kitchen_interface/sample_ground.py](project/07_Evidence/v11_kitchen_interface/sample_ground.py) | 原字节 |
| [project/07_Evidence/v11_kitchen_interface/scan_section.py](project/07_Evidence/v11_kitchen_interface/scan_section.py) | 原字节 |
| [project/07_Evidence/v11_outer_gate/freeze_audit.py](project/07_Evidence/v11_outer_gate/freeze_audit.py) | 原字节 |
| [project/07_Evidence/v11_outer_gate/inspect_current.py](project/07_Evidence/v11_outer_gate/inspect_current.py) | 原字节 |
| [project/07_Evidence/v11_outer_gate/mutation.py](project/07_Evidence/v11_outer_gate/mutation.py) | 原字节 |
| [project/07_Evidence/v11_outer_gate/preview.py](project/07_Evidence/v11_outer_gate/preview.py) | 原字节 |
| [project/07_Evidence/v11_outer_gate/profile_gate.py](project/07_Evidence/v11_outer_gate/profile_gate.py) | 站点坐标脱敏 |
| [project/07_Evidence/v11_outer_gate/scan_levels.py](project/07_Evidence/v11_outer_gate/scan_levels.py) | 站点坐标脱敏 |
| [project/07_Evidence/v11_pavilion/build_pavilion.py](project/07_Evidence/v11_pavilion/build_pavilion.py) | 原字节 |
| [project/07_Evidence/v11_pavilion/preview_and_native.py](project/07_Evidence/v11_pavilion/preview_and_native.py) | 原字节 |
| [project/07_Evidence/v11_pavilion/render_preview.py](project/07_Evidence/v11_pavilion/render_preview.py) | 原字节 |
| [project/07_Evidence/v11_pavilion/validate_native.py](project/07_Evidence/v11_pavilion/validate_native.py) | 原字节 |
| [project/07_Evidence/v11_wall_junction/audit.py](project/07_Evidence/v11_wall_junction/audit.py) | 原字节 |
| [project/07_Evidence/v11_wall_junction/configure.py](project/07_Evidence/v11_wall_junction/configure.py) | 原字节 |
| [project/07_Evidence/v11_wall_junction/mutation.py](project/07_Evidence/v11_wall_junction/mutation.py) | 原字节 |
| [project/07_Evidence/v11_wall_junction/preview.py](project/07_Evidence/v11_wall_junction/preview.py) | 原字节 |
| [project/07_Evidence/v11_wall_junction/render_preview.py](project/07_Evidence/v11_wall_junction/render_preview.py) | 原字节 |
