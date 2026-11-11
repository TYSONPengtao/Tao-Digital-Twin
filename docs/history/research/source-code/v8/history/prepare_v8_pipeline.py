from pathlib import Path
W=Path(__file__).parent
def edit(source,target,replace):
    s=(W/source).read_text(encoding='utf-8')
    for a,b in replace:s=s.replace(a,b)
    (W/target).write_text(s,encoding='utf-8')
edit('build_v7_patch.py','build_v8_patch.py',[
 ('Rebuild_V7_Hybrid','Rebuild_V8_Hybrid'),('Rebuild_V6_Hybrid','Rebuild_V7_Hybrid'),
 ("incremental='--incremental' in sys.argv","incremental=True"),
 ("('V7_Incremental_Nodes.json' if incremental else 'V7_Changed_Nodes.json')","'V8_Changed_Nodes.json'"),
 ("H=Polygon(hp['local']['outer'],hp['local']['holes'])","\nfrom shapely.ops import unary_union\nscope=json.loads((O/'02_Data/V8_Allowed_Repair_Scope.json').read_text(encoding='utf-8'))\nH=unary_union([Polygon(p['outer'],p.get('holes',[])) for p in scope['polygons']])"),
 ("'M_Ceramic_Warm']","'M_Ceramic_Warm','M_Wall_Exterior','M_Stone','M_Wall_Interior']"),
 ("fn='V7_'","fn='V8_'"),('V7_CORRECTED','V8_CORRECTED'),('Patch_Incremental_Revision_V7','Patch_Incremental_Revision_V8')])
edit('export_v7_native.py','export_v8_native.py',[
 ('Rebuild_V7_Hybrid','Rebuild_V8_Hybrid'),('Reality_Hybrid_V7','Reality_Hybrid_V8'),
 ("r'E:\\jz\\纯场地版本.3dm'","r'E:\\jz\\JIA\\Rebuild_V8_Hybrid\\01_Source\\Pure_Site_WORKING_V8.3dm'"),
 ('V7 corrected','V8 corrected'),('Original five photogrammetry meshes, original ENU vertices/faces/UV/normals preserved','Original source file retained; working derivative locally clipped only in user-authorized terrain/roof/contact repair regions'),
 ('Only main missing-area polygon, excluding preserved interior source islands','V8 original missing-area plus explicitly authorized west terrain clearance and local roof/column repair regions'),
 ("'base_materials_unmodified':True","'base_materials_unmodified':True,'original_source_file_unmodified':True,'working_geometry_has_authorized_local_edits':True")])
edit('export_v7_editable.py','export_v8_editable.py',[('Rebuild_V7_Hybrid','Rebuild_V8_Hybrid')])
edit('rhino_validate_v7.py','rhino_validate_v8.py',[('Rebuild_V7_Hybrid','Rebuild_V8_Hybrid')])
edit('align_editable_rhino_v7.py','align_editable_rhino_v8.py',[('Rebuild_V7_Hybrid','Rebuild_V8_Hybrid'),('Reality_Hybrid_V7','Reality_Hybrid_V8'),('Architecture_Edit_V7','Architecture_Edit_V8'),('V7 LOCAL','V8 LOCAL')])
edit('finalize_v7_views.py','finalize_v8_views.py',[('Rebuild_V7_Hybrid','Rebuild_V8_Hybrid'),('Reality_Hybrid_V7','Reality_Hybrid_V8'),('V7_','V8_')])
edit('check_v7_exchange_photos.py','check_v8_exchange_photos.py',[('Rebuild_V7_Hybrid','Rebuild_V8_Hybrid'),('Reality_Hybrid_V7','Reality_Hybrid_V8'),('V7_Exchange','V8_Exchange')])
print('V8 export/build/kernel/readback pipeline prepared')
