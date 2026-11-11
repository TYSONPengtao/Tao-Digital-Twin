# V24.37 原实现脚本

[技术文章](../../versions/v24-37.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 36 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 36 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v24_37_quality_probe.py`](project/Sources/v24_37_quality_probe.py)
- [`v24_37_prepare.py`](project/Sources/v24_37_prepare.py)
- [`v24_37_build.py`](project/Sources/v24_37_build.py)
- [`v24_37_prepare_qa.py`](history/v24_37_prepare_qa.py)
- [`v24_37_quality_analysis.py`](history/v24_37_quality_analysis.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v24_37_check_shared_walker.py](history/v24_37_check_shared_walker.py) | 原字节 |
| [history/v24_37_fix_gui_jump_timing.py](history/v24_37_fix_gui_jump_timing.py) | 原字节 |
| [history/v24_37_plot_retention.py](history/v24_37_plot_retention.py) | 原字节 |
| [history/v24_37_prepare_exterior_qa.py](history/v24_37_prepare_exterior_qa.py) | 原字节 |
| [history/v24_37_prepare_qa.py](history/v24_37_prepare_qa.py) | 原字节 |
| [history/v24_37_prepare_viewport_qa.py](history/v24_37_prepare_viewport_qa.py) | 原字节 |
| [history/v24_37_quality_analysis.py](history/v24_37_quality_analysis.py) | 原字节 |
| [history/v24_37_review_crop.py](history/v24_37_review_crop.py) | 原字节 |
| [history/v24_37_review_sheets.py](history/v24_37_review_sheets.py) | 原字节 |
| [history/v24_37_texture_quality_probe.py](history/v24_37_texture_quality_probe.py) | 原字节 |
| [project/Roam/measure_tools.py](project/Roam/measure_tools.py) | 原字节 |
| [project/Roam/roam_controller.py](project/Roam/roam_controller.py) | 原字节 |
| [project/Roam/roam_physics.py](project/Roam/roam_physics.py) | 原字节 |
| [project/Roam/start_roam.py](project/Roam/start_roam.py) | 原字节 |
| [project/Sources/v24_06_common.py](project/Sources/v24_06_common.py) | 原字节 |
| [project/Sources/v24_37_build.py](project/Sources/v24_37_build.py) | 原字节 |
| [project/Sources/v24_37_clip_collision.py](project/Sources/v24_37_clip_collision.py) | 原字节 |
| [project/Sources/v24_37_export.py](project/Sources/v24_37_export.py) | 原字节 |
| [project/Sources/v24_37_exterior_physics_qa.py](project/Sources/v24_37_exterior_physics_qa.py) | 原字节 |
| [project/Sources/v24_37_finalize_collision.py](project/Sources/v24_37_finalize_collision.py) | 原字节 |
| [project/Sources/v24_37_interior_physics_qa.py](project/Sources/v24_37_interior_physics_qa.py) | 原字节 |
| [project/Sources/v24_37_launcher_smoke.py](project/Sources/v24_37_launcher_smoke.py) | 原字节 |
| [project/Sources/v24_37_measure_math_qa.py](project/Sources/v24_37_measure_math_qa.py) | 原字节 |
| [project/Sources/v24_37_package.py](project/Sources/v24_37_package.py) | 原字节 |
| [project/Sources/v24_37_prepare.py](project/Sources/v24_37_prepare.py) | 原字节 |
| [project/Sources/v24_37_quality_mask.py](project/Sources/v24_37_quality_mask.py) | 原字节 |
| [project/Sources/v24_37_quality_probe.py](project/Sources/v24_37_quality_probe.py) | 原字节 |
| [project/Sources/v24_37_record_visual_review.py](project/Sources/v24_37_record_visual_review.py) | 原字节 |
| [project/Sources/v24_37_refine_complete_border.py](project/Sources/v24_37_refine_complete_border.py) | 原字节 |
| [project/Sources/v24_37_render.py](project/Sources/v24_37_render.py) | 原字节 |
| [project/Sources/v24_37_surface_qa.py](project/Sources/v24_37_surface_qa.py) | 原字节 |
| [project/Sources/v24_37_verify.py](project/Sources/v24_37_verify.py) | 原字节 |
| [project/Sources/v24_37_viewport_qa.py](project/Sources/v24_37_viewport_qa.py) | 原字节 |
| [project/Sources/v24_qa_blender.py](project/Sources/v24_qa_blender.py) | 原字节 |
| [project/启动漫游.cmd](project/%E5%90%AF%E5%8A%A8%E6%BC%AB%E6%B8%B8.cmd) | 原字节 |
| [project/打开修正版模型.cmd](project/%E6%89%93%E5%BC%80%E4%BF%AE%E6%AD%A3%E7%89%88%E6%A8%A1%E5%9E%8B.cmd) | 原字节 |
