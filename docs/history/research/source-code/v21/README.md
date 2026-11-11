# V21 原实现脚本

[技术文章](../../versions/v21.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 36 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 36 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v21_door_native_review.py`](project/08_Editable_Source/V21_Scripts/v21_door_native_review.py)
- [`v21_prepare_package.py`](history/v21_prepare_package.py)
- [`build.py`](project/08_Editable_Source/V21_Scripts/house/build.py)
- [`planes.py`](project/08_Editable_Source/V21_Scripts/house/planes.py)
- [`floor_probe.py`](project/08_Editable_Source/V21_Scripts/house/floor_probe.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v21_prepare_package.py](history/v21_prepare_package.py) | 原字节 |
| [history/v21_prepare_pipeline.py](history/v21_prepare_pipeline.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/gate/design.py](project/08_Editable_Source/V21_Scripts/gate/design.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/gate/qa.py](project/08_Editable_Source/V21_Scripts/gate/qa.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/build.py](project/08_Editable_Source/V21_Scripts/house/build.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/details.py](project/08_Editable_Source/V21_Scripts/house/details.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/diagnostic_reveal.py](project/08_Editable_Source/V21_Scripts/house/diagnostic_reveal.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/diagnostic_sliding_light.py](project/08_Editable_Source/V21_Scripts/house/diagnostic_sliding_light.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/diagnostic_sliding_light_100w.py](project/08_Editable_Source/V21_Scripts/house/diagnostic_sliding_light_100w.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/floor_probe.py](project/08_Editable_Source/V21_Scripts/house/floor_probe.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/infill_fullheight.py](project/08_Editable_Source/V21_Scripts/house/infill_fullheight.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/inspect_house.py](project/08_Editable_Source/V21_Scripts/house/inspect_house.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/plan_compare.py](project/08_Editable_Source/V21_Scripts/house/plan_compare.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/planes.py](project/08_Editable_Source/V21_Scripts/house/planes.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/preview_review.py](project/08_Editable_Source/V21_Scripts/house/preview_review.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/preview_review_final.py](project/08_Editable_Source/V21_Scripts/house/preview_review_final.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/qa.py](project/08_Editable_Source/V21_Scripts/house/qa.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/qa_native.py](project/08_Editable_Source/V21_Scripts/house/qa_native.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/raycast_jamb.py](project/08_Editable_Source/V21_Scripts/house/raycast_jamb.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/reference.py](project/08_Editable_Source/V21_Scripts/house/reference.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/reference_base.py](project/08_Editable_Source/V21_Scripts/house/reference_base.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/house/reference_ground.py](project/08_Editable_Source/V21_Scripts/house/reference_ground.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/site/design.py](project/08_Editable_Source/V21_Scripts/site/design.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/site/final_review.py](project/08_Editable_Source/V21_Scripts/site/final_review.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/site/finalize_review.py](project/08_Editable_Source/V21_Scripts/site/finalize_review.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/site/inventory.py](project/08_Editable_Source/V21_Scripts/site/inventory.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/site/preview_review.py](project/08_Editable_Source/V21_Scripts/site/preview_review.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/site/reference.py](project/08_Editable_Source/V21_Scripts/site/reference.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/v21_assemble.py](project/08_Editable_Source/V21_Scripts/v21_assemble.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/v21_door_native_review.py](project/08_Editable_Source/V21_Scripts/v21_door_native_review.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/v21_final_lighting.py](project/08_Editable_Source/V21_Scripts/v21_final_lighting.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/v21_finalize_review.py](project/08_Editable_Source/V21_Scripts/v21_finalize_review.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/v21_merge.py](project/08_Editable_Source/V21_Scripts/v21_merge.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/v21_native_qa.py](project/08_Editable_Source/V21_Scripts/v21_native_qa.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/v21_package.py](project/08_Editable_Source/V21_Scripts/v21_package.py) | 原字节 |
| [project/08_Editable_Source/V21_Scripts/v21_render_native.py](project/08_Editable_Source/V21_Scripts/v21_render_native.py) | 原字节 |
