# V26.8 原实现脚本

[技术文章](../../versions/v26-8.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 65 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 65 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v26_8_prepare.py`](project/Sources/v26_8_prepare.py)
- [`v26_8_build_fast.py`](project/Sources/Performance/v26_8_build_fast.py)
- [`v26_8_perf_audit.py`](project/Sources/Performance/v26_8_perf_audit.py)
- [`v26_8_build.py`](project/Sources/v26_8_build.py)
- [`v26_8_geometry_qa.py`](project/Sources/v26_8_geometry_qa.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v26_8_lighting_probe.py](history/v26_8_lighting_probe.py) | 原字节 |
| [history/v26_8_make_build.py](history/v26_8_make_build.py) | 原字节 |
| [history/v26_8_make_cleanup.py](history/v26_8_make_cleanup.py) | 原字节 |
| [history/v26_8_make_extra_qa.py](history/v26_8_make_extra_qa.py) | 原字节 |
| [history/v26_8_make_render.py](history/v26_8_make_render.py) | 原字节 |
| [history/v26_8_prepare_verify.py](history/v26_8_prepare_verify.py) | 原字节 |
| [history/v26_8_small_corner_probe.py](history/v26_8_small_corner_probe.py) | 原字节 |
| [history/v26_8_stair_probe.py](history/v26_8_stair_probe.py) | 原字节 |
| [project/Roam/measure_tools.py](project/Roam/measure_tools.py) | 原字节 |
| [project/Roam/roam_controller.py](project/Roam/roam_controller.py) | 原字节 |
| [project/Roam/roam_controller_fast.py](project/Roam/roam_controller_fast.py) | 原字节 |
| [project/Roam/roam_physics.py](project/Roam/roam_physics.py) | 原字节 |
| [project/Roam/start_roam.py](project/Roam/start_roam.py) | 原字节 |
| [project/Roam/start_roam_fast.py](project/Roam/start_roam_fast.py) | 原字节 |
| [project/Sources/Performance/v26_8_build_fast.py](project/Sources/Performance/v26_8_build_fast.py) | 原字节 |
| [project/Sources/Performance/v26_8_fast_display.py](project/Sources/Performance/v26_8_fast_display.py) | 原字节 |
| [project/Sources/Performance/v26_8_make_fast_controller.py](project/Sources/Performance/v26_8_make_fast_controller.py) | 原字节 |
| [project/Sources/Performance/v26_8_package_fast.py](project/Sources/Performance/v26_8_package_fast.py) | 原字节 |
| [project/Sources/Performance/v26_8_perf_audit.py](project/Sources/Performance/v26_8_perf_audit.py) | 原字节 |
| [project/Sources/Performance/v26_8_perf_viewport_bench.py](project/Sources/Performance/v26_8_perf_viewport_bench.py) | 原字节 |
| [project/Sources/Performance/v26_8_verify_fast.py](project/Sources/Performance/v26_8_verify_fast.py) | 原字节 |
| [project/Sources/Performance/v26_8_verify_package.py](project/Sources/Performance/v26_8_verify_package.py) | 原字节 |
| [project/Sources/v24_06_common.py](project/Sources/v24_06_common.py) | 原字节 |
| [project/Sources/v24_16_common.py](project/Sources/v24_16_common.py) | 原字节 |
| [project/Sources/v24_qa_blender.py](project/Sources/v24_qa_blender.py) | 原字节 |
| [project/Sources/v26_2_common.py](project/Sources/v26_2_common.py) | 原字节 |
| [project/Sources/v26_8_build.py](project/Sources/v26_8_build.py) | 原字节 |
| [project/Sources/v26_8_dynamic_render.py](project/Sources/v26_8_dynamic_render.py) | 原字节 |
| [project/Sources/v26_8_entry_jambs/apply_recipe.py](project/Sources/v26_8_entry_jambs/apply_recipe.py) | 原字节 |
| [project/Sources/v26_8_entry_jambs/prepare.py](project/Sources/v26_8_entry_jambs/prepare.py) | 原字节 |
| [project/Sources/v26_8_entry_jambs/prepare_95.py](project/Sources/v26_8_entry_jambs/prepare_95.py) | 原字节 |
| [project/Sources/v26_8_entry_jambs/render_95.py](project/Sources/v26_8_entry_jambs/render_95.py) | 原字节 |
| [project/Sources/v26_8_entry_jambs/render_candidate.py](project/Sources/v26_8_entry_jambs/render_candidate.py) | 原字节 |
| [project/Sources/v26_8_entry_jambs/render_recommended.py](project/Sources/v26_8_entry_jambs/render_recommended.py) | 原字节 |
| [project/Sources/v26_8_geometry_qa.py](project/Sources/v26_8_geometry_qa.py) | 原字节 |
| [project/Sources/v26_8_make_railing.py](project/Sources/v26_8_make_railing.py) | 原字节 |
| [project/Sources/v26_8_native_cleanup.py](project/Sources/v26_8_native_cleanup.py) | 原字节 |
| [project/Sources/v26_8_overcast_qa.py](project/Sources/v26_8_overcast_qa.py) | 原字节 |
| [project/Sources/v26_8_overlap_after.py](project/Sources/v26_8_overlap_after.py) | 原字节 |
| [project/Sources/v26_8_overlap_gate.py](project/Sources/v26_8_overlap_gate.py) | 原字节 |
| [project/Sources/v26_8_package.py](project/Sources/v26_8_package.py) | 原字节 |
| [project/Sources/v26_8_physics_qa.py](project/Sources/v26_8_physics_qa.py) | 原字节 |
| [project/Sources/v26_8_prepare.py](project/Sources/v26_8_prepare.py) | 原字节 |
| [project/Sources/v26_8_protection_qa.py](project/Sources/v26_8_protection_qa.py) | 原字节 |
| [project/Sources/v26_8_railing/build_candidate.py](project/Sources/v26_8_railing/build_candidate.py) | 原字节 |
| [project/Sources/v26_8_railing/saved_native_qa.py](project/Sources/v26_8_railing/saved_native_qa.py) | 原字节 |
| [project/Sources/v26_8_readback.py](project/Sources/v26_8_readback.py) | 原字节 |
| [project/Sources/v26_8_render.py](project/Sources/v26_8_render.py) | 原字节 |
| [project/Sources/v26_8_stair_audit/actual_low_views.py](project/Sources/v26_8_stair_audit/actual_low_views.py) | 原字节 |
| [project/Sources/v26_8_stair_audit/diagnose.py](project/Sources/v26_8_stair_audit/diagnose.py) | 原字节 |
| [project/Sources/v26_8_stair_audit/saved_native_qa.py](project/Sources/v26_8_stair_audit/saved_native_qa.py) | 原字节 |
| [project/Sources/v26_8_stair_audit/select_references.py](project/Sources/v26_8_stair_audit/select_references.py) | 原字节 |
| [project/Sources/v26_8_stair_audit/source_loss.py](project/Sources/v26_8_stair_audit/source_loss.py) | 原字节 |
| [project/Sources/v26_8_stair_audit/step_wall_gap.py](project/Sources/v26_8_stair_audit/step_wall_gap.py) | 原字节 |
| [project/Sources/v26_8_stair_audit/wall_edge_probe.py](project/Sources/v26_8_stair_audit/wall_edge_probe.py) | 原字节 |
| [project/Sources/v26_8_views.py](project/Sources/v26_8_views.py) | 原字节 |
| [project/Sources/v26_8_visual_qa.py](project/Sources/v26_8_visual_qa.py) | 原字节 |
| [project/Sources/v26_8_windows/apply_house_recipe.py](project/Sources/v26_8_windows/apply_house_recipe.py) | 原字节 |
| [project/Sources/v26_8_windows/prepare.py](project/Sources/v26_8_windows/prepare.py) | 原字节 |
| [project/Sources/v26_8_windows/prepare_foot_closure.py](project/Sources/v26_8_windows/prepare_foot_closure.py) | 原字节 |
| [project/Sources/v26_8_windows/preview_prepare.py](project/Sources/v26_8_windows/preview_prepare.py) | 原字节 |
| [project/Sources/v26_8_windows/preview_render.py](project/Sources/v26_8_windows/preview_render.py) | 原字节 |
| [project/Sources/v26_8_windows/qa.py](project/Sources/v26_8_windows/qa.py) | 原字节 |
| [project/Sources/v26_8_windows/saved_native_qa.py](project/Sources/v26_8_windows/saved_native_qa.py) | 原字节 |
| [project/启动漫游.cmd](project/%E5%90%AF%E5%8A%A8%E6%BC%AB%E6%B8%B8.cmd) | 原字节 |
