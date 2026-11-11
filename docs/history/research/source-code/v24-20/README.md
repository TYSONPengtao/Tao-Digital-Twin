# V24.20 原实现脚本

[技术文章](../../versions/v24-20.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 27 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 27 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v24_20_plans.py`](project/Source/v24_20_plans.py)
- [`v24_20_probe.py`](project/Source/v24_20_probe.py)
- [`v24_20_prepare.py`](project/Source/v24_20_prepare.py)
- [`v24_20_build.py`](project/Source/v24_20_build.py)
- [`v24_20_plan.py`](history/v24_20_plan.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v24_20_diagnostics.py](history/v24_20_diagnostics.py) | 原字节 |
| [history/v24_20_junction_probe.py](history/v24_20_junction_probe.py) | 原字节 |
| [history/v24_20_layout_data.py](history/v24_20_layout_data.py) | 原字节 |
| [history/v24_20_plan.py](history/v24_20_plan.py) | 原字节 |
| [history/v24_20_plot_kitchen.py](history/v24_20_plot_kitchen.py) | 原字节 |
| [history/v24_20_pre18_walls.py](history/v24_20_pre18_walls.py) | 原字节 |
| [history/v24_20_ray_probe.py](history/v24_20_ray_probe.py) | 原字节 |
| [history/v24_20_roof_analysis.py](history/v24_20_roof_analysis.py) | 原字节 |
| [history/v24_20_uv_probe.py](history/v24_20_uv_probe.py) | 原字节 |
| [project/Source/v24_03_junction_blender.py](project/Source/v24_03_junction_blender.py) | 原字节 |
| [project/Source/v24_06_common.py](project/Source/v24_06_common.py) | 原字节 |
| [project/Source/v24_11_geometry.py](project/Source/v24_11_geometry.py) | 原字节 |
| [project/Source/v24_16_common.py](project/Source/v24_16_common.py) | 原字节 |
| [project/Source/v24_18_finish.py](project/Source/v24_18_finish.py) | 原字节 |
| [project/Source/v24_20_build.py](project/Source/v24_20_build.py) | 原字节 |
| [project/Source/v24_20_common.py](project/Source/v24_20_common.py) | 原字节 |
| [project/Source/v24_20_package.py](project/Source/v24_20_package.py) | 原字节 |
| [project/Source/v24_20_plans.py](project/Source/v24_20_plans.py) | 原字节 |
| [project/Source/v24_20_posts.py](project/Source/v24_20_posts.py) | 原字节 |
| [project/Source/v24_20_prepare.py](project/Source/v24_20_prepare.py) | 原字节 |
| [project/Source/v24_20_probe.py](project/Source/v24_20_probe.py) | 原字节 |
| [project/Source/v24_20_render.py](project/Source/v24_20_render.py) | 原字节 |
| [project/Source/v24_20_roofs.py](project/Source/v24_20_roofs.py) | 原字节 |
| [project/Source/v24_20_solids.py](project/Source/v24_20_solids.py) | 原字节 |
| [project/Source/v24_20_verify.py](project/Source/v24_20_verify.py) | 原字节 |
| [project/Source/v24_20_wc.py](project/Source/v24_20_wc.py) | 原字节 |
| [project/Source/v24_qa_blender.py](project/Source/v24_qa_blender.py) | 原字节 |
