from pathlib import Path
import json,hashlib
O=Path('E:/jz/JIA/Rebuild_V24_37');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_37.blend';path=R/'V24_37_Viewport_QA.json';q=json.loads(path.read_text('utf8'))
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
assert q['model_sha256']==h and len(q['captures'])==6 and not q['failures']
q['checks']=[
 {'check':'Native wall and eave A B previews show one coherent masonry and roof surface','pass':True,'note':'Both reviewed camera offsets show the same blue brick wall, tiled eave, flue and elbow without the annotated scan strips.'},
 {'check':'Original reconstructed house and courtyard remain recognizable and unchanged','pass':True,'note':'House A B pair preserves the white courtyard and original constructed facade; native preservation hashes also pass.'},
 {'check':'Original photographic materials load in all six native preview captures','pass':True,'note':'No missing-texture magenta surfaces are visible in the inspected captures.'},
 {'check':'PTJIA6 road and complete field show continuous useful surface features','pass':True,'note':'Road-eye and field previews retain the supplied photographs and terrain detail, consistent with successful capsule route tests.'},
 {'check':'Reviewed plan view removes the north extrapolation and broken outer scraps','pass':True,'note':'Root inspected the final full plan and coherent border; the large blurred north curtain and detached southern shards are absent.'},
 {'check':'Actual exterior tour screenshots show the person supported on original and added scan surfaces','pass':True,'note':'Root inspected both actual keyboard tour screenshots and the successful movement, jump and landing reports.'}]
q['status']='PASS_NATIVE_MATERIAL_PREVIEW_VISUALLY_REVIEWED';q['review_basis']='Root visually inspected six native material-preview frames, actual MB7 and PTJIA6 tour screenshots, final 2400px plan and kitchen close render.';q['source_quality_limits']='Natural scan occlusion gaps inside retained tree-canopy feature blocks remain visible. No unmeasured surface is invented; deleted outskirts are excluded from collision and unsupported movement is blocked.';path.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8');print('VISUAL_REVIEW_RECORDED',len(q['checks']),h)
