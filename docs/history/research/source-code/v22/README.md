# V22 原实现脚本

[技术文章](../../versions/v22.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 27 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 27 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v22_finish_probe.py`](project/08_Editable_Source/V22_Scripts/v22_finish_probe.py)
- [`v22_native_qa.py`](project/08_Editable_Source/V22_Scripts/v22_native_qa.py)
- [`probe.py`](project/08_Editable_Source/V22_Scripts/pavilion/probe.py)
- [`v22_archive_prepare.py`](project/08_Editable_Source/V22_Scripts/v22_archive_prepare.py)
- [`probe_parts.py`](project/08_Editable_Source/V22_Scripts/pavilion/probe_parts.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v22_gate_rear/inspect_gate_parts.py](history/v22_gate_rear/inspect_gate_parts.py) | 原字节 |
| [history/v22_prepare_package.py](history/v22_prepare_package.py) | 原字节 |
| [history/v22_prepare_pipeline.py](history/v22_prepare_pipeline.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/kitchen/design.py](project/08_Editable_Source/V22_Scripts/kitchen/design.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/kitchen/preview.py](project/08_Editable_Source/V22_Scripts/kitchen/preview.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/pavilion/design.py](project/08_Editable_Source/V22_Scripts/pavilion/design.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/pavilion/probe.py](project/08_Editable_Source/V22_Scripts/pavilion/probe.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/pavilion/probe_parts.py](project/08_Editable_Source/V22_Scripts/pavilion/probe_parts.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/pavilion/render_preview.py](project/08_Editable_Source/V22_Scripts/pavilion/render_preview.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/pavilion/review.py](project/08_Editable_Source/V22_Scripts/pavilion/review.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_archive_prepare.py](project/08_Editable_Source/V22_Scripts/v22_archive_prepare.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_assemble.py](project/08_Editable_Source/V22_Scripts/v22_assemble.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_common.py](project/08_Editable_Source/V22_Scripts/v22_common.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_detail_source_qa.py](project/08_Editable_Source/V22_Scripts/v22_detail_source_qa.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_door_native_review.py](project/08_Editable_Source/V22_Scripts/v22_door_native_review.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_final_review.py](project/08_Editable_Source/V22_Scripts/v22_final_review.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_finish_joints.py](project/08_Editable_Source/V22_Scripts/v22_finish_joints.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_finish_probe.py](project/08_Editable_Source/V22_Scripts/v22_finish_probe.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_gate_detail.py](project/08_Editable_Source/V22_Scripts/v22_gate_detail.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_house_detail.py](project/08_Editable_Source/V22_Scripts/v22_house_detail.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_inventory.py](project/08_Editable_Source/V22_Scripts/v22_inventory.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_merge.py](project/08_Editable_Source/V22_Scripts/v22_merge.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_native_qa.py](project/08_Editable_Source/V22_Scripts/v22_native_qa.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_package.py](project/08_Editable_Source/V22_Scripts/v22_package.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_pavilion_finish.py](project/08_Editable_Source/V22_Scripts/v22_pavilion_finish.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_render_native.py](project/08_Editable_Source/V22_Scripts/v22_render_native.py) | 原字节 |
| [project/08_Editable_Source/V22_Scripts/v22_wall_contact.py](project/08_Editable_Source/V22_Scripts/v22_wall_contact.py) | 原字节 |
