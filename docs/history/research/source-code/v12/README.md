# V12 原实现脚本

[技术文章](../../versions/v12.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 42 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 40 项；站点坐标脱敏 2 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`extract_v12.py`](history/v12_panorama_reference/extract_v12.py)
- [`export_v5.py`](project/08_Editable_Source/Build_Scripts/export_v5.py)
- [`validate_v12_native.py`](project/08_Editable_Source/Build_Scripts/validate_v12_native.py)
- [`rebuild.py`](project/07_Reference/v12_terrain/rebuild.py) · 坐标脱敏副本
- [`audit_seams.py`](project/07_Reference/v12_terrain/audit_seams.py)

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/v12_panorama_reference/annotate.py](history/v12_panorama_reference/annotate.py) | 原字节 |
| [history/v12_panorama_reference/extract_v12.py](history/v12_panorama_reference/extract_v12.py) | 原字节 |
| [history/v12_panorama_reference/verify_prior_provenance.py](history/v12_panorama_reference/verify_prior_provenance.py) | 原字节 |
| [project/07_Reference/Before/厨房/build_kitchen_V14.py](project/07_Reference/Before/%E5%8E%A8%E6%88%BF/build_kitchen_V14.py) | 原字节 |
| [project/07_Reference/Before/厨房/build_kitchen_V15.py](project/07_Reference/Before/%E5%8E%A8%E6%88%BF/build_kitchen_V15.py) | 原字节 |
| [project/07_Reference/Before/厨房/build_kitchen_V16.py](project/07_Reference/Before/%E5%8E%A8%E6%88%BF/build_kitchen_V16.py) | 原字节 |
| [project/07_Reference/Before/厨房/build_kitchen_V17.py](project/07_Reference/Before/%E5%8E%A8%E6%88%BF/build_kitchen_V17.py) | 原字节 |
| [project/07_Reference/Before/照壁/Fusion_照壁_三个版本_v4.py](project/07_Reference/Before/%E7%85%A7%E5%A3%81/Fusion_%E7%85%A7%E5%A3%81_%E4%B8%89%E4%B8%AA%E7%89%88%E6%9C%AC_v4.py) | 原字节 |
| [project/07_Reference/Before/照壁/Generate_照壁_native_3dm.py](project/07_Reference/Before/%E7%85%A7%E5%A3%81/Generate_%E7%85%A7%E5%A3%81_native_3dm.py) | 原字节 |
| [project/07_Reference/Before/照壁/Improve_照壁_侧面构造.py](project/07_Reference/Before/%E7%85%A7%E5%A3%81/Improve_%E7%85%A7%E5%A3%81_%E4%BE%A7%E9%9D%A2%E6%9E%84%E9%80%A0.py) | 原字节 |
| [project/07_Reference/Before/照壁/Improve_照壁_屋面脊吻_v3.py](project/07_Reference/Before/%E7%85%A7%E5%A3%81/Improve_%E7%85%A7%E5%A3%81_%E5%B1%8B%E9%9D%A2%E8%84%8A%E5%90%BB_v3.py) | 原字节 |
| [project/07_Reference/v12_kitchen/build_kitchen.py](project/07_Reference/v12_kitchen/build_kitchen.py) | 原字节 |
| [project/07_Reference/v12_kitchen/extract_before.py](project/07_Reference/v12_kitchen/extract_before.py) | 原字节 |
| [project/07_Reference/v12_kitchen/freeze.py](project/07_Reference/v12_kitchen/freeze.py) | 原字节 |
| [project/07_Reference/v12_kitchen/preview_data.py](project/07_Reference/v12_kitchen/preview_data.py) | 原字节 |
| [project/07_Reference/v12_kitchen/render.py](project/07_Reference/v12_kitchen/render.py) | 原字节 |
| [project/07_Reference/v12_screenwall_reference/build_detail.py](project/07_Reference/v12_screenwall_reference/build_detail.py) | 原字节 |
| [project/07_Reference/v12_screenwall_reference/contact_qa.py](project/07_Reference/v12_screenwall_reference/contact_qa.py) | 原字节 |
| [project/07_Reference/v12_screenwall_reference/freeze.py](project/07_Reference/v12_screenwall_reference/freeze.py) | 原字节 |
| [project/07_Reference/v12_screenwall_reference/render.py](project/07_Reference/v12_screenwall_reference/render.py) | 原字节 |
| [project/07_Reference/v12_terrain/audit_seams.py](project/07_Reference/v12_terrain/audit_seams.py) | 原字节 |
| [project/07_Reference/v12_terrain/brief_scene.py](project/07_Reference/v12_terrain/brief_scene.py) | 原字节 |
| [project/07_Reference/v12_terrain/ground_bounds.py](project/07_Reference/v12_terrain/ground_bounds.py) | 原字节 |
| [project/07_Reference/v12_terrain/inventory_source.py](project/07_Reference/v12_terrain/inventory_source.py) | 站点坐标脱敏 |
| [project/07_Reference/v12_terrain/raw_ground.py](project/07_Reference/v12_terrain/raw_ground.py) | 原字节 |
| [project/07_Reference/v12_terrain/raycast_render.py](project/07_Reference/v12_terrain/raycast_render.py) | 原字节 |
| [project/07_Reference/v12_terrain/rebuild.py](project/07_Reference/v12_terrain/rebuild.py) | 站点坐标脱敏 |
| [project/07_Reference/v12_terrain/render_repaired.py](project/07_Reference/v12_terrain/render_repaired.py) | 原字节 |
| [project/07_Reference/v12_terrain/verify_and_companions.py](project/07_Reference/v12_terrain/verify_and_companions.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/assemble_v12.py](project/08_Editable_Source/Build_Scripts/assemble_v12.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/blender_v12_modeled.py](project/08_Editable_Source/Build_Scripts/blender_v12_modeled.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/export_v5.py](project/08_Editable_Source/Build_Scripts/export_v5.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/harmonize_v12_native_ground_normals.py](project/08_Editable_Source/Build_Scripts/harmonize_v12_native_ground_normals.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/prepare_v12.py](project/08_Editable_Source/Build_Scripts/prepare_v12.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/record_v12_visual_review.py](project/08_Editable_Source/Build_Scripts/record_v12_visual_review.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/v12_finishing.py](project/08_Editable_Source/Build_Scripts/v12_finishing.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/v12_inventory.py](project/08_Editable_Source/Build_Scripts/v12_inventory.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/validate_v12_native.py](project/08_Editable_Source/Build_Scripts/validate_v12_native.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/verify_v12_exchange.py](project/08_Editable_Source/Build_Scripts/verify_v12_exchange.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/verify_v12_fbx.py](project/08_Editable_Source/Build_Scripts/verify_v12_fbx.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/verify_v12_sources.py](project/08_Editable_Source/Build_Scripts/verify_v12_sources.py) | 原字节 |
| [project/08_Editable_Source/Build_Scripts/write_v12_delivery.py](project/08_Editable_Source/Build_Scripts/write_v12_delivery.py) | 原字节 |
