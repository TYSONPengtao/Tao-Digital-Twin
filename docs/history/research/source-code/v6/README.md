# V6 原实现脚本

[技术文章](../../versions/v6.md) · [全部版本源码](../README.md) · [逐文件校验清单](manifest.json)

本目录附上 32 个原过程脚本与启动文件。同名且内容一致的工程／历史副本合并保存，所有原路径保留在清单中。包括随工程保留的前序模块、漫游和性能工具；文件存在不表示全部在本轮重新执行，实际本轮入口以技术文章与过程报告为准。

代码对应当轮保存的实施与核验过程，原有输入路径、输出路径和软件调用方式予以保留。运行会写入原脚本指定的工程位置；复现应先复制模型、配置隔离目录并核对软件依赖。完整生产模型、原始照片、私有坐标数据与设备配置在本机管理。

**原字节保存 29 项；站点坐标脱敏 3 项。** 脱敏文件使用 `TAO_PRIVATE_SITE_*` 标记并加入执行阻断，需依据本机原件恢复私有常量后才能运行。清单同时记录原件与公开副本的 SHA-256、原行号和全部来源路径。

## 本轮阅读入口

- [`prepare_v6_base.py`](history/prepare_v6_base.py)
- [`build_v6_patch.py`](history/build_v6_patch.py)
- [`stitch_v6_rim.py`](history/stitch_v6_rim.py)
- [`probe_v6_embed.py`](history/probe_v6_embed.py)
- [`export_v6_native.py`](history/export_v6_native.py) · 坐标脱敏副本

## 全部附带文件

| 原文件 | 公开状态 |
| --- | --- |
| [history/align_editable_rhino_v6.py](history/align_editable_rhino_v6.py) | 原字节 |
| [history/blender_v6_hybrid.py](history/blender_v6_hybrid.py) | 原字节 |
| [history/build_v6_patch.py](history/build_v6_patch.py) | 原字节 |
| [history/export_v6_native.py](history/export_v6_native.py) | 站点坐标脱敏 |
| [history/inspect_v6_terrain.py](history/inspect_v6_terrain.py) | 原字节 |
| [history/package_v6_rhino.py](history/package_v6_rhino.py) | 原字节 |
| [history/prepare_v6_base.py](history/prepare_v6_base.py) | 原字节 |
| [history/probe_v6_embed.py](history/probe_v6_embed.py) | 原字节 |
| [history/repair_v6_ground.py](history/repair_v6_ground.py) | 原字节 |
| [history/repair_v6_roof_photos.py](history/repair_v6_roof_photos.py) | 原字节 |
| [history/stitch_v6_rim.py](history/stitch_v6_rim.py) | 原字节 |
| [history/v6_alignment_audit/check_boundary_height_fast_v6.py](history/v6_alignment_audit/check_boundary_height_fast_v6.py) | 原字节 |
| [history/v6_alignment_audit/check_hybrid_v6.py](history/v6_alignment_audit/check_hybrid_v6.py) | 原字节 |
| [history/v6_alignment_audit/check_rim_3d_v6.py](history/v6_alignment_audit/check_rim_3d_v6.py) | 原字节 |
| [history/v6_alignment_audit/check_rim_3d_v7.py](history/v6_alignment_audit/check_rim_3d_v7.py) | 原字节 |
| [history/v6_alignment_audit/identify_hole_topology.py](history/v6_alignment_audit/identify_hole_topology.py) | 原字节 |
| [history/v6_alignment_audit/identify_main_hole.py](history/v6_alignment_audit/identify_main_hole.py) | 原字节 |
| [history/v6_alignment_audit/inspect_existing_alignment.py](history/v6_alignment_audit/inspect_existing_alignment.py) | 原字节 |
| [history/v6_alignment_audit/inspect_pure_alignment.py](history/v6_alignment_audit/inspect_pure_alignment.py) | 站点坐标脱敏 |
| [history/v6_alignment_audit/refine_main_hole.py](history/v6_alignment_audit/refine_main_hole.py) | 原字节 |
| [history/v6_reality_inventory/check_fbx_patch_uv.py](history/v6_reality_inventory/check_fbx_patch_uv.py) | 原字节 |
| [history/v6_reality_inventory/check_old_textures.py](history/v6_reality_inventory/check_old_textures.py) | 原字节 |
| [history/v6_reality_inventory/check_reference.py](history/v6_reality_inventory/check_reference.py) | 原字节 |
| [history/v6_reality_inventory/check_v6_exchange_photos.py](history/v6_reality_inventory/check_v6_exchange_photos.py) | 原字节 |
| [history/v6_reality_inventory/hash_pure.py](history/v6_reality_inventory/hash_pure.py) | 站点坐标脱敏 |
| [history/v6_reality_inventory/inspect_new_rhino.py](history/v6_reality_inventory/inspect_new_rhino.py) | 原字节 |
| [history/v6_reality_inventory/nearest_photo_projection.py](history/v6_reality_inventory/nearest_photo_projection.py) | 原字节 |
| [history/v6_reality_inventory/refresh_obj_photo_links.py](history/v6_reality_inventory/refresh_obj_photo_links.py) | 原字节 |
| [history/v6_reality_inventory/snapshot_readback_sources.py](history/v6_reality_inventory/snapshot_readback_sources.py) | 原字节 |
| [history/v6_reality_inventory/summarize.py](history/v6_reality_inventory/summarize.py) | 原字节 |
| [history/v6_reality_inventory/test_projection_reference.py](history/v6_reality_inventory/test_projection_reference.py) | 原字节 |
| [history/v6_reality_inventory/verify_embedded.py](history/v6_reality_inventory/verify_embedded.py) | 原字节 |
