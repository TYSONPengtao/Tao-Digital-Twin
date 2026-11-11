# V26.12 原实现脚本

[技术文章](../../versions/v26-12.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 31 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 31 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v26_12_build.py`](project/Sources/v26_12_build.py)
- [`v26_12_eevee_compare.py`](project/Sources/v26_12_eevee_compare.py)
- [`v26_12_native_qa.py`](project/Sources/v26_12_native_qa.py)
- [`v26_12_probe.py`](project/Sources/v26_12_probe.py)
- [`v26_12_build_fast.py`](project/Sources/v26_12_build_fast.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [project/Roam/measure_tools.py](project/Roam/measure_tools.py) | 原字节 |
| [project/Roam/roam_controller.py](project/Roam/roam_controller.py) | 原字节 |
| [project/Roam/roam_controller_fast.py](project/Roam/roam_controller_fast.py) | 原字节 |
| [project/Roam/roam_physics.py](project/Roam/roam_physics.py) | 原字节 |
| [project/Roam/start_roam.py](project/Roam/start_roam.py) | 原字节 |
| [project/Roam/start_roam_fast.py](project/Roam/start_roam_fast.py) | 原字节 |
| [project/Sources/Performance/v26_8_build_fast.py](project/Sources/Performance/v26_8_build_fast.py) | 原字节 |
| [project/Sources/Performance/v26_8_make_fast_controller.py](project/Sources/Performance/v26_8_make_fast_controller.py) | 原字节 |
| [project/Sources/Performance/v26_8_perf_audit.py](project/Sources/Performance/v26_8_perf_audit.py) | 原字节 |
| [project/Sources/Performance/v26_8_perf_viewport_bench.py](project/Sources/Performance/v26_8_perf_viewport_bench.py) | 原字节 |
| [project/Sources/v24_06_common.py](project/Sources/v24_06_common.py) | 原字节 |
| [project/Sources/v24_qa_blender.py](project/Sources/v24_qa_blender.py) | 原字节 |
| [project/Sources/v26_12_apply_display.py](project/Sources/v26_12_apply_display.py) | 原字节 |
| [project/Sources/v26_12_build.py](project/Sources/v26_12_build.py) | 原字节 |
| [project/Sources/v26_12_build_fast.py](project/Sources/v26_12_build_fast.py) | 原字节 |
| [project/Sources/v26_12_eevee_compare.py](project/Sources/v26_12_eevee_compare.py) | 原字节 |
| [project/Sources/v26_12_fast_display.py](project/Sources/v26_12_fast_display.py) | 原字节 |
| [project/Sources/v26_12_gate_clearance_qa.py](project/Sources/v26_12_gate_clearance_qa.py) | 原字节 |
| [project/Sources/v26_12_make_helpers.py](project/Sources/v26_12_make_helpers.py) | 原字节 |
| [project/Sources/v26_12_native_qa.py](project/Sources/v26_12_native_qa.py) | 原字节 |
| [project/Sources/v26_12_package.py](project/Sources/v26_12_package.py) | 原字节 |
| [project/Sources/v26_12_physics_qa.py](project/Sources/v26_12_physics_qa.py) | 原字节 |
| [project/Sources/v26_12_probe.py](project/Sources/v26_12_probe.py) | 原字节 |
| [project/Sources/v26_12_render.py](project/Sources/v26_12_render.py) | 原字节 |
| [project/Sources/v26_12_run_remaining.py](project/Sources/v26_12_run_remaining.py) | 原字节 |
| [project/Sources/v26_12_verify_fast.py](project/Sources/v26_12_verify_fast.py) | 原字节 |
| [project/Sources/v26_12_verify_package.py](project/Sources/v26_12_verify_package.py) | 原字节 |
| [project/Sources/v26_12_view_flags.py](project/Sources/v26_12_view_flags.py) | 原字节 |
| [project/Sources/v26_12_viewport_review.py](project/Sources/v26_12_viewport_review.py) | 原字节 |
| [project/Sources/v26_8_fast_display.py](project/Sources/v26_8_fast_display.py) | 原字节 |
| [project/启动漫游.cmd](project/%E5%90%AF%E5%8A%A8%E6%BC%AB%E6%B8%B8.cmd) | 原字节 |
