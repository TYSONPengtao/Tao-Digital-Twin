# V26.5 原实现脚本

[技术文章](../../versions/v26-5.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 46 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 46 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v26_5_precision_probe.py`](history/v26_5_precision_probe.py)
- [`v26_5_prepare.py`](project/Sources/v26_5_prepare.py)
- [`v26_5_geometry_qa.py`](project/Sources/v26_5_geometry_qa.py)
- [`v26_5_build.py`](project/Sources/v26_5_build.py)
- [`probe.py`](history/v26_5_left_audit/probe.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v26_5_facade_audit/diagnose.py](history/v26_5_facade_audit/diagnose.py) | 原字节 |
| [history/v26_5_facade_audit/docs.py](history/v26_5_facade_audit/docs.py) | 原字节 |
| [history/v26_5_facade_audit/precision_review.py](history/v26_5_facade_audit/precision_review.py) | 原字节 |
| [history/v26_5_facade_audit/saved_native_qa.py](history/v26_5_facade_audit/saved_native_qa.py) | 原字节 |
| [history/v26_5_facade_audit/test_native_patch.py](history/v26_5_facade_audit/test_native_patch.py) | 原字节 |
| [history/v26_5_facade_audit/test_patch.py](history/v26_5_facade_audit/test_patch.py) | 原字节 |
| [history/v26_5_left_audit/all5_bay_fins.py](history/v26_5_left_audit/all5_bay_fins.py) | 原字节 |
| [history/v26_5_left_audit/bay_probe.py](history/v26_5_left_audit/bay_probe.py) | 原字节 |
| [history/v26_5_left_audit/bay_sections.py](history/v26_5_left_audit/bay_sections.py) | 原字节 |
| [history/v26_5_left_audit/coping_float32_probe.py](history/v26_5_left_audit/coping_float32_probe.py) | 原字节 |
| [history/v26_5_left_audit/full_height_cut.py](history/v26_5_left_audit/full_height_cut.py) | 原字节 |
| [history/v26_5_left_audit/localized_cut.py](history/v26_5_left_audit/localized_cut.py) | 原字节 |
| [history/v26_5_left_audit/probe.py](history/v26_5_left_audit/probe.py) | 原字节 |
| [history/v26_5_left_audit/regression_saved.py](history/v26_5_left_audit/regression_saved.py) | 原字节 |
| [history/v26_5_left_audit/surface_deviation.py](history/v26_5_left_audit/surface_deviation.py) | 原字节 |
| [history/v26_5_left_audit/surface_deviation_refined.py](history/v26_5_left_audit/surface_deviation_refined.py) | 原字节 |
| [history/v26_5_make_checks.py](history/v26_5_make_checks.py) | 原字节 |
| [history/v26_5_precision_probe.py](history/v26_5_precision_probe.py) | 原字节 |
| [history/v26_5_wc_audit/regression.py](history/v26_5_wc_audit/regression.py) | 原字节 |
| [history/v26_5_wc_audit/render.py](history/v26_5_wc_audit/render.py) | 原字节 |
| [history/v26_5_wc_audit/render_head.py](history/v26_5_wc_audit/render_head.py) | 原字节 |
| [history/v26_5_wc_audit/render_left_head.py](history/v26_5_wc_audit/render_left_head.py) | 原字节 |
| [project/Roam/measure_tools.py](project/Roam/measure_tools.py) | 原字节 |
| [project/Roam/roam_controller.py](project/Roam/roam_controller.py) | 原字节 |
| [project/Roam/roam_physics.py](project/Roam/roam_physics.py) | 原字节 |
| [project/Roam/start_roam.py](project/Roam/start_roam.py) | 原字节 |
| [project/Sources/bay_regression_saved.py](project/Sources/bay_regression_saved.py) | 原字节 |
| [project/Sources/facade_regression_saved.py](project/Sources/facade_regression_saved.py) | 原字节 |
| [project/Sources/triangle_precision_review.py](project/Sources/triangle_precision_review.py) | 原字节 |
| [project/Sources/v24_06_common.py](project/Sources/v24_06_common.py) | 原字节 |
| [project/Sources/v24_16_common.py](project/Sources/v24_16_common.py) | 原字节 |
| [project/Sources/v24_qa_blender.py](project/Sources/v24_qa_blender.py) | 原字节 |
| [project/Sources/v26_2_common.py](project/Sources/v26_2_common.py) | 原字节 |
| [project/Sources/v26_5_build.py](project/Sources/v26_5_build.py) | 原字节 |
| [project/Sources/v26_5_facade_recipe.py](project/Sources/v26_5_facade_recipe.py) | 原字节 |
| [project/Sources/v26_5_geometry_qa.py](project/Sources/v26_5_geometry_qa.py) | 原字节 |
| [project/Sources/v26_5_overlap_after.py](project/Sources/v26_5_overlap_after.py) | 原字节 |
| [project/Sources/v26_5_overlap_gate.py](project/Sources/v26_5_overlap_gate.py) | 原字节 |
| [project/Sources/v26_5_package.py](project/Sources/v26_5_package.py) | 原字节 |
| [project/Sources/v26_5_physics_qa.py](project/Sources/v26_5_physics_qa.py) | 原字节 |
| [project/Sources/v26_5_prepare.py](project/Sources/v26_5_prepare.py) | 原字节 |
| [project/Sources/v26_5_protection_qa.py](project/Sources/v26_5_protection_qa.py) | 原字节 |
| [project/Sources/v26_5_readback.py](project/Sources/v26_5_readback.py) | 原字节 |
| [project/Sources/v26_5_render.py](project/Sources/v26_5_render.py) | 原字节 |
| [project/Sources/v26_5_views.py](project/Sources/v26_5_views.py) | 原字节 |
| [project/启动漫游.cmd](project/%E5%90%AF%E5%8A%A8%E6%BC%AB%E6%B8%B8.cmd) | 原字节 |
