# V24.22 原实现脚本

[技术文章](../../versions/v24-22.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 19 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 19 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v24_22_analyze.py`](history/v24_22_analyze.py)
- [`v24_22_plot.py`](history/v24_22_plot.py)
- [`v24_22_geometry.py`](history/v24_22_geometry.py)
- [`v24_22_build.py`](history/v24_22_build.py)
- [`v24_22_probe.py`](history/v24_22_probe.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v24_22_analyze.py](history/v24_22_analyze.py) | 原字节 |
| [history/v24_22_build.py](history/v24_22_build.py) | 原字节 |
| [history/v24_22_common.py](history/v24_22_common.py) | 原字节 |
| [history/v24_22_geometry.py](history/v24_22_geometry.py) | 原字节 |
| [history/v24_22_launcher_smoke.py](history/v24_22_launcher_smoke.py) | 原字节 |
| [history/v24_22_package.py](history/v24_22_package.py) | 原字节 |
| [history/v24_22_physics_qa.py](history/v24_22_physics_qa.py) | 原字节 |
| [history/v24_22_plot.py](history/v24_22_plot.py) | 原字节 |
| [history/v24_22_probe.py](history/v24_22_probe.py) | 原字节 |
| [history/v24_22_rays.py](history/v24_22_rays.py) | 原字节 |
| [history/v24_22_render.py](history/v24_22_render.py) | 原字节 |
| [history/v24_22_shared_gable_probe.py](history/v24_22_shared_gable_probe.py) | 原字节 |
| [history/v24_22_solid_qa.py](history/v24_22_solid_qa.py) | 原字节 |
| [history/v24_22_verify.py](history/v24_22_verify.py) | 原字节 |
| [project/Roam/roam_controller.py](project/Roam/roam_controller.py) | 原字节 |
| [project/Roam/roam_physics.py](project/Roam/roam_physics.py) | 原字节 |
| [project/Roam/start_roam.py](project/Roam/start_roam.py) | 原字节 |
| [project/启动漫游.cmd](project/%E5%90%AF%E5%8A%A8%E6%BC%AB%E6%B8%B8.cmd) | 原字节 |
| [project/打开修正版模型.cmd](project/%E6%89%93%E5%BC%80%E4%BF%AE%E6%AD%A3%E7%89%88%E6%A8%A1%E5%9E%8B.cmd) | 原字节 |
