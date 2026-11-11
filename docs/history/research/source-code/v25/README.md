# V25 原实现脚本

[技术文章](../../versions/v25.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 46 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 41 项；站点坐标脱敏 5 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v25_build_rhino.py`](project/Conversion_Source/v25_build_rhino.py) · 坐标脱敏副本
- [`v25_material_probe.py`](history/v25_material_probe.py)
- [`v25_prepare_delivery.py`](project/Conversion_Source/v25_prepare_delivery.py) · 坐标脱敏副本
- [`v25_clean_coplanar_backfaces.py`](project/Conversion_Source/v25_clean_coplanar_backfaces.py)
- [`v25_gui_probe.py`](history/v25_gui_probe.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v25_adopt_native_temp.py](history/v25_adopt_native_temp.py) | 原字节 |
| [history/v25_attach_rhino.py](history/v25_attach_rhino.py) | 原字节 |
| [history/v25_attribute_probe.py](history/v25_attribute_probe.py) | 原字节 |
| [history/v25_blender_probe.py](history/v25_blender_probe.py) | 原字节 |
| [history/v25_gui_material_probe.py](history/v25_gui_material_probe.py) | 原字节 |
| [history/v25_gui_probe.py](history/v25_gui_probe.py) | 原字节 |
| [history/v25_material_probe.py](history/v25_material_probe.py) | 原字节 |
| [history/v25_native_ray_probe.py](history/v25_native_ray_probe.py) | 原字节 |
| [history/v25_object_material_probe.py](history/v25_object_material_probe.py) | 原字节 |
| [history/v25_open_final_in_rhino.py](history/v25_open_final_in_rhino.py) | 原字节 |
| [history/v25_probe_saved_views.py](history/v25_probe_saved_views.py) | 原字节 |
| [history/v25_probe_wall_pixels.py](history/v25_probe_wall_pixels.py) | 原字节 |
| [history/v25_record_visual_review.py](history/v25_record_visual_review.py) | 原字节 |
| [history/v25_release_preview.py](history/v25_release_preview.py) | 原字节 |
| [history/v25_rhino_api_probe.py](history/v25_rhino_api_probe.py) | 原字节 |
| [history/v25_rhino_min_probe.py](history/v25_rhino_min_probe.py) | 原字节 |
| [history/v25_rhino_persistence_smoke.py](history/v25_rhino_persistence_smoke.py) | 站点坐标脱敏 |
| [history/v25_rhino_smoke.py](history/v25_rhino_smoke.py) | 原字节 |
| [history/v25_specific_materials.py](history/v25_specific_materials.py) | 原字节 |
| [history/v25_tidy_delivery.py](history/v25_tidy_delivery.py) | 原字节 |
| [history/v25_view_constructor_probe.py](history/v25_view_constructor_probe.py) | 原字节 |
| [history/v25_visibility_probe.py](history/v25_visibility_probe.py) | 原字节 |
| [project/Conversion_Source/v24_qa_blender.py](project/Conversion_Source/v24_qa_blender.py) | 原字节 |
| [project/Conversion_Source/v25_build_rhino.py](project/Conversion_Source/v25_build_rhino.py) | 站点坐标脱敏 |
| [project/Conversion_Source/v25_clean_coplanar_backfaces.py](project/Conversion_Source/v25_clean_coplanar_backfaces.py) | 原字节 |
| [project/Conversion_Source/v25_clean_covered_wall_foot.py](project/Conversion_Source/v25_clean_covered_wall_foot.py) | 原字节 |
| [project/Conversion_Source/v25_export_blender.py](project/Conversion_Source/v25_export_blender.py) | 原字节 |
| [project/Conversion_Source/v25_finalize_texture_names.py](project/Conversion_Source/v25_finalize_texture_names.py) | 原字节 |
| [project/Conversion_Source/v25_mesh_bridge.cs](project/Conversion_Source/v25_mesh_bridge.cs) | 原字节 |
| [project/Conversion_Source/v25_package.py](project/Conversion_Source/v25_package.py) | 原字节 |
| [project/Conversion_Source/v25_patch_native_local.py](project/Conversion_Source/v25_patch_native_local.py) | 原字节 |
| [project/Conversion_Source/v25_prepare_delivery.py](project/Conversion_Source/v25_prepare_delivery.py) | 站点坐标脱敏 |
| [project/Conversion_Source/v25_resume_enu.py](project/Conversion_Source/v25_resume_enu.py) | 站点坐标脱敏 |
| [project/Conversion_Source/v25_rhino_common.py](project/Conversion_Source/v25_rhino_common.py) | 原字节 |
| [project/Conversion_Source/v25_verify_companion.py](project/Conversion_Source/v25_verify_companion.py) | 原字节 |
| [project/Conversion_Source/v25_verify_material_faces.py](project/Conversion_Source/v25_verify_material_faces.py) | 原字节 |
| [project/Conversion_Source/v25_verify_rhino.py](project/Conversion_Source/v25_verify_rhino.py) | 站点坐标脱敏 |
| [project/Conversion_Source/v25_viewport.py](project/Conversion_Source/v25_viewport.py) | 原字节 |
| [project/Roam/measure_tools.py](project/Roam/measure_tools.py) | 原字节 |
| [project/Roam/roam_controller.py](project/Roam/roam_controller.py) | 原字节 |
| [project/Roam/roam_physics.py](project/Roam/roam_physics.py) | 原字节 |
| [project/Roam/start_roam.py](project/Roam/start_roam.py) | 原字节 |
| [project/启动漫游.cmd](project/%E5%90%AF%E5%8A%A8%E6%BC%AB%E6%B8%B8.cmd) | 原字节 |
| [project/打开ENU坐标模型.cmd](project/%E6%89%93%E5%BC%80ENU%E5%9D%90%E6%A0%87%E6%A8%A1%E5%9E%8B.cmd) | 原字节 |
| [project/打开Rhino模型.cmd](project/%E6%89%93%E5%BC%80Rhino%E6%A8%A1%E5%9E%8B.cmd) | 原字节 |
| [project/打开修正版模型.cmd](project/%E6%89%93%E5%BC%80%E4%BF%AE%E6%AD%A3%E7%89%88%E6%A8%A1%E5%9E%8B.cmd) | 原字节 |
