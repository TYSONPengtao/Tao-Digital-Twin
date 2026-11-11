# V14 原实现脚本

[技术文章](../../versions/v14.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 24 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 24 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v14_building.py`](project/08_Editable_Source/V14_Scripts/v14_building.py)
- [`v14_contact_audit.py`](project/08_Editable_Source/V14_Scripts/v14_contact_audit.py)
- [`v14_merge_route_audit.py`](project/08_Editable_Source/V14_Scripts/v14_merge_route_audit.py)
- [`v14_kernel_probe.py`](history/v14_kernel_probe.py)
- [`v14_relief_probe.py`](history/v14_relief_probe.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v14_brief.py](history/v14_brief.py) | 原字节 |
| [history/v14_door_wall_probe.py](history/v14_door_wall_probe.py) | 原字节 |
| [history/v14_inspect.py](history/v14_inspect.py) | 原字节 |
| [history/v14_kernel_probe.py](history/v14_kernel_probe.py) | 原字节 |
| [history/v14_mesh_preflight.py](history/v14_mesh_preflight.py) | 原字节 |
| [history/v14_package.py](history/v14_package.py) | 原字节 |
| [history/v14_relief_probe.py](history/v14_relief_probe.py) | 原字节 |
| [history/v14_target_digest.py](history/v14_target_digest.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_assemble.py](project/08_Editable_Source/V14_Scripts/v14_assemble.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_building.py](project/08_Editable_Source/V14_Scripts/v14_building.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_contact_audit.py](project/08_Editable_Source/V14_Scripts/v14_contact_audit.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_extract.py](project/08_Editable_Source/V14_Scripts/v14_extract.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_f3_column_clearance.py](project/08_Editable_Source/V14_Scripts/v14_f3_column_clearance.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_finalize.py](project/08_Editable_Source/V14_Scripts/v14_finalize.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_finish_opening.py](project/08_Editable_Source/V14_Scripts/v14_finish_opening.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_merge_route_audit.py](project/08_Editable_Source/V14_Scripts/v14_merge_route_audit.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_opening_qa.py](project/08_Editable_Source/V14_Scripts/v14_opening_qa.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_readback.py](project/08_Editable_Source/V14_Scripts/v14_readback.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_relief_repair.py](project/08_Editable_Source/V14_Scripts/v14_relief_repair.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_render_native.py](project/08_Editable_Source/V14_Scripts/v14_render_native.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_review_fixes.py](project/08_Editable_Source/V14_Scripts/v14_review_fixes.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_roof_junction.py](project/08_Editable_Source/V14_Scripts/v14_roof_junction.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_roof_survey.py](project/08_Editable_Source/V14_Scripts/v14_roof_survey.py) | 原字节 |
| [project/08_Editable_Source/V14_Scripts/v14_terrain.py](project/08_Editable_Source/V14_Scripts/v14_terrain.py) | 原字节 |
