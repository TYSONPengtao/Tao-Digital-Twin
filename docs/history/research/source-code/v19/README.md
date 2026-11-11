# V19 原实现脚本

[技术文章](../../versions/v19.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 16 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 16 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v19_design.py`](project/08_Editable_Source/V19_Scripts/v19_design.py)
- [`v19_coping_probe.py`](history/v19_coping_probe.py)
- [`v19_native_envelope_probe.py`](history/v19_native_envelope_probe.py)
- [`v19_probe.py`](history/v19_probe.py)
- [`v19_view_probe.py`](history/v19_view_probe.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v19_cleanup_probe.py](history/v19_cleanup_probe.py) | 原字节 |
| [history/v19_coping_probe.py](history/v19_coping_probe.py) | 原字节 |
| [history/v19_native_envelope_probe.py](history/v19_native_envelope_probe.py) | 原字节 |
| [history/v19_prepare_render.py](history/v19_prepare_render.py) | 原字节 |
| [history/v19_probe.py](history/v19_probe.py) | 原字节 |
| [history/v19_source_probe.py](history/v19_source_probe.py) | 原字节 |
| [history/v19_view_probe.py](history/v19_view_probe.py) | 原字节 |
| [project/08_Editable_Source/V19_Scripts/v19_assemble.py](project/08_Editable_Source/V19_Scripts/v19_assemble.py) | 原字节 |
| [project/08_Editable_Source/V19_Scripts/v19_design.py](project/08_Editable_Source/V19_Scripts/v19_design.py) | 原字节 |
| [project/08_Editable_Source/V19_Scripts/v19_detail_reference.py](project/08_Editable_Source/V19_Scripts/v19_detail_reference.py) | 原字节 |
| [project/08_Editable_Source/V19_Scripts/v19_native_drain_preserve.py](project/08_Editable_Source/V19_Scripts/v19_native_drain_preserve.py) | 原字节 |
| [project/08_Editable_Source/V19_Scripts/v19_native_final_corrections.py](project/08_Editable_Source/V19_Scripts/v19_native_final_corrections.py) | 原字节 |
| [project/08_Editable_Source/V19_Scripts/v19_package.py](project/08_Editable_Source/V19_Scripts/v19_package.py) | 原字节 |
| [project/08_Editable_Source/V19_Scripts/v19_readback_qa.py](project/08_Editable_Source/V19_Scripts/v19_readback_qa.py) | 原字节 |
| [project/08_Editable_Source/V19_Scripts/v19_reference.py](project/08_Editable_Source/V19_Scripts/v19_reference.py) | 原字节 |
| [project/08_Editable_Source/V19_Scripts/v19_render_native.py](project/08_Editable_Source/V19_Scripts/v19_render_native.py) | 原字节 |
