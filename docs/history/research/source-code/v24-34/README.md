# V24.34 原实现脚本

[技术文章](../../versions/v24-34.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 38 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 35 项；站点坐标脱敏 3 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v24_34_match.py`](project/Sources/v24_34_match.py)
- [`v24_34_register.py`](project/Sources/v24_34_register.py) · 坐标脱敏副本
- [`v24_34_clip.py`](project/Sources/v24_34_clip.py)
- [`v24_34_build.py`](project/Sources/v24_34_build.py)
- [`v24_34_plan_routes.py`](project/Sources/v24_34_plan_routes.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [project/Roam/measure_tools.py](project/Roam/measure_tools.py) | 原字节 |
| [project/Roam/roam_controller.py](project/Roam/roam_controller.py) | 原字节 |
| [project/Roam/roam_physics.py](project/Roam/roam_physics.py) | 原字节 |
| [project/Roam/start_roam.py](project/Roam/start_roam.py) | 原字节 |
| [project/Sources/v24_06_common.py](project/Sources/v24_06_common.py) | 原字节 |
| [project/Sources/v24_34_build.py](project/Sources/v24_34_build.py) | 原字节 |
| [project/Sources/v24_34_clip.py](project/Sources/v24_34_clip.py) | 原字节 |
| [project/Sources/v24_34_coordinate_seed.py](project/Sources/v24_34_coordinate_seed.py) | 站点坐标脱敏 |
| [project/Sources/v24_34_debug_support.py](project/Sources/v24_34_debug_support.py) | 原字节 |
| [project/Sources/v24_34_decode.py](project/Sources/v24_34_decode.py) | 原字节 |
| [project/Sources/v24_34_exterior_physics_qa.py](project/Sources/v24_34_exterior_physics_qa.py) | 原字节 |
| [project/Sources/v24_34_grid_plot.py](project/Sources/v24_34_grid_plot.py) | 原字节 |
| [project/Sources/v24_34_ground_grid.py](project/Sources/v24_34_ground_grid.py) | 原字节 |
| [project/Sources/v24_34_inspect.py](project/Sources/v24_34_inspect.py) | 原字节 |
| [project/Sources/v24_34_interior_physics_qa.py](project/Sources/v24_34_interior_physics_qa.py) | 原字节 |
| [project/Sources/v24_34_landmarks.py](project/Sources/v24_34_landmarks.py) | 原字节 |
| [project/Sources/v24_34_launcher_smoke.py](project/Sources/v24_34_launcher_smoke.py) | 原字节 |
| [project/Sources/v24_34_make_viewport_script.py](project/Sources/v24_34_make_viewport_script.py) | 原字节 |
| [project/Sources/v24_34_match.py](project/Sources/v24_34_match.py) | 原字节 |
| [project/Sources/v24_34_measure_math_qa.py](project/Sources/v24_34_measure_math_qa.py) | 原字节 |
| [project/Sources/v24_34_package.py](project/Sources/v24_34_package.py) | 站点坐标脱敏 |
| [project/Sources/v24_34_plan_routes.py](project/Sources/v24_34_plan_routes.py) | 原字节 |
| [project/Sources/v24_34_plan_walkable_routes.py](project/Sources/v24_34_plan_walkable_routes.py) | 原字节 |
| [project/Sources/v24_34_record_visual_review.py](project/Sources/v24_34_record_visual_review.py) | 原字节 |
| [project/Sources/v24_34_register.py](project/Sources/v24_34_register.py) | 站点坐标脱敏 |
| [project/Sources/v24_34_registration_views.py](project/Sources/v24_34_registration_views.py) | 原字节 |
| [project/Sources/v24_34_render.py](project/Sources/v24_34_render.py) | 原字节 |
| [project/Sources/v24_34_review_sheet.py](project/Sources/v24_34_review_sheet.py) | 原字节 |
| [project/Sources/v24_34_roam_controller.py](project/Sources/v24_34_roam_controller.py) | 原字节 |
| [project/Sources/v24_34_roam_physics.py](project/Sources/v24_34_roam_physics.py) | 原字节 |
| [project/Sources/v24_34_seam_weights.py](project/Sources/v24_34_seam_weights.py) | 原字节 |
| [project/Sources/v24_34_surface_qa.py](project/Sources/v24_34_surface_qa.py) | 原字节 |
| [project/Sources/v24_34_update_runtime.py](project/Sources/v24_34_update_runtime.py) | 原字节 |
| [project/Sources/v24_34_verify.py](project/Sources/v24_34_verify.py) | 原字节 |
| [project/Sources/v24_34_viewport_qa.py](project/Sources/v24_34_viewport_qa.py) | 原字节 |
| [project/Sources/v24_qa_blender.py](project/Sources/v24_qa_blender.py) | 原字节 |
| [project/启动漫游.cmd](project/%E5%90%AF%E5%8A%A8%E6%BC%AB%E6%B8%B8.cmd) | 原字节 |
| [project/打开修正版模型.cmd](project/%E6%89%93%E5%BC%80%E4%BF%AE%E6%AD%A3%E7%89%88%E6%A8%A1%E5%9E%8B.cmd) | 原字节 |
