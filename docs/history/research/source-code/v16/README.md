# V16 原实现脚本

[技术文章](../../versions/v16.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 16 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 16 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v16_soil_probe.py`](project/08_Editable_Source/V16_Scripts/v16_soil_probe.py)
- [`v16_geometry.py`](project/08_Editable_Source/V16_Scripts/v16_geometry.py)
- [`v16_probe.py`](project/08_Editable_Source/V16_Scripts/v16_probe.py)
- [`v16_source_probe.py`](project/08_Editable_Source/V16_Scripts/v16_source_probe.py)
- [`v16_compact.py`](project/08_Editable_Source/V16_Scripts/v16_compact.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [project/08_Editable_Source/V16_Scripts/v16_apply_junction.py](project/08_Editable_Source/V16_Scripts/v16_apply_junction.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_assemble.py](project/08_Editable_Source/V16_Scripts/v16_assemble.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_compact.py](project/08_Editable_Source/V16_Scripts/v16_compact.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_geometry.py](project/08_Editable_Source/V16_Scripts/v16_geometry.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_make_renderer.py](project/08_Editable_Source/V16_Scripts/v16_make_renderer.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_package.py](project/08_Editable_Source/V16_Scripts/v16_package.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_probe.py](project/08_Editable_Source/V16_Scripts/v16_probe.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_profile.py](project/08_Editable_Source/V16_Scripts/v16_profile.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_quality_soil.py](project/08_Editable_Source/V16_Scripts/v16_quality_soil.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_readback_qa.py](project/08_Editable_Source/V16_Scripts/v16_readback_qa.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_refresh_render.py](project/08_Editable_Source/V16_Scripts/v16_refresh_render.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_render_native.py](project/08_Editable_Source/V16_Scripts/v16_render_native.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_report_update.py](project/08_Editable_Source/V16_Scripts/v16_report_update.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_soil_probe.py](project/08_Editable_Source/V16_Scripts/v16_soil_probe.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_source_probe.py](project/08_Editable_Source/V16_Scripts/v16_source_probe.py) | 原字节 |
| [project/08_Editable_Source/V16_Scripts/v16_stitch_edge.py](project/08_Editable_Source/V16_Scripts/v16_stitch_edge.py) | 原字节 |
