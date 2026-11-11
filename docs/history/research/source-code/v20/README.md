# V20 原实现脚本

[技术文章](../../versions/v20.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 41 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 41 项；站点坐标脱敏 0 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`v20_door_check.py`](project/08_Editable_Source/V20_Scripts/v20_door_check.py)
- [`v20_native_qa.py`](project/08_Editable_Source/V20_Scripts/v20_native_qa.py)
- [`plan.py`](project/08_Editable_Source/V20_Scripts/house/plan.py)
- [`build_patch.py`](project/08_Editable_Source/V20_Scripts/house/build_patch.py)
- [`grade_probe.py`](project/08_Editable_Source/V20_Scripts/house/grade_probe.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v20_door_probe.py](history/v20_door_probe.py) | 原字节 |
| [history/v20_glb_probe.py](history/v20_glb_probe.py) | 原字节 |
| [history/v20_inventory.py](history/v20_inventory.py) | 原字节 |
| [history/v20_native_probe.py](history/v20_native_probe.py) | 原字节 |
| [history/v20_prepare_render.py](history/v20_prepare_render.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/gate_pavilion/mutation.py](project/08_Editable_Source/V20_Scripts/gate_pavilion/mutation.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/gate_pavilion/probe.py](project/08_Editable_Source/V20_Scripts/gate_pavilion/probe.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/gate_pavilion/qa.py](project/08_Editable_Source/V20_Scripts/gate_pavilion/qa.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/gate_pavilion/reference.py](project/08_Editable_Source/V20_Scripts/gate_pavilion/reference.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/build_patch.py](project/08_Editable_Source/V20_Scripts/house/build_patch.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/door_proposed_review.py](project/08_Editable_Source/V20_Scripts/house/door_proposed_review.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/door_review.py](project/08_Editable_Source/V20_Scripts/house/door_review.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/f2_head_review.py](project/08_Editable_Source/V20_Scripts/house/f2_head_review.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/gate_bottom_probe.py](project/08_Editable_Source/V20_Scripts/house/gate_bottom_probe.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/grade_probe.py](project/08_Editable_Source/V20_Scripts/house/grade_probe.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/inner_gate_angle_probe.py](project/08_Editable_Source/V20_Scripts/house/inner_gate_angle_probe.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/inventory.py](project/08_Editable_Source/V20_Scripts/house/inventory.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/outer_gate_bottom_fix.py](project/08_Editable_Source/V20_Scripts/house/outer_gate_bottom_fix.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/pavilion_probe.py](project/08_Editable_Source/V20_Scripts/house/pavilion_probe.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/plan.py](project/08_Editable_Source/V20_Scripts/house/plan.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/qa_patch.py](project/08_Editable_Source/V20_Scripts/house/qa_patch.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/house/source_digest.py](project/08_Editable_Source/V20_Scripts/house/source_digest.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/storage/design.py](project/08_Editable_Source/V20_Scripts/storage/design.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/storage/final_native_seam.py](project/08_Editable_Source/V20_Scripts/storage/final_native_seam.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/storage/inventory.py](project/08_Editable_Source/V20_Scripts/storage/inventory.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/storage/reference.py](project/08_Editable_Source/V20_Scripts/storage/reference.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/storage/seam_audit.py](project/08_Editable_Source/V20_Scripts/storage/seam_audit.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/storage/seam_correct.py](project/08_Editable_Source/V20_Scripts/storage/seam_correct.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/storage/seam_validate.py](project/08_Editable_Source/V20_Scripts/storage/seam_validate.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_assemble.py](project/08_Editable_Source/V20_Scripts/v20_assemble.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_door_check.py](project/08_Editable_Source/V20_Scripts/v20_door_check.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_door_design.py](project/08_Editable_Source/V20_Scripts/v20_door_design.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_gallery_review.py](project/08_Editable_Source/V20_Scripts/v20_gallery_review.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_gate_review.py](project/08_Editable_Source/V20_Scripts/v20_gate_review.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_inspection_lighting.py](project/08_Editable_Source/V20_Scripts/v20_inspection_lighting.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_merge.py](project/08_Editable_Source/V20_Scripts/v20_merge.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_native_qa.py](project/08_Editable_Source/V20_Scripts/v20_native_qa.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_package.py](project/08_Editable_Source/V20_Scripts/v20_package.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_render_native.py](project/08_Editable_Source/V20_Scripts/v20_render_native.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_review_views.py](project/08_Editable_Source/V20_Scripts/v20_review_views.py) | 原字节 |
| [project/08_Editable_Source/V20_Scripts/v20_storage_door_clearance.py](project/08_Editable_Source/V20_Scripts/v20_storage_door_clearance.py) | 原字节 |
