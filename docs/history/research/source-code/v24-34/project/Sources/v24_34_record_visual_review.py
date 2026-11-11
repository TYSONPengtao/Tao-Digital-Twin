from pathlib import Path
import json,hashlib
R=Path('E:/jz/JIA/Rebuild_V24_34/Reports');P=R/'V24_34_Viewport_QA.json';q=json.loads(P.read_text('utf8'));assert len(q['captures'])==6 and not q['failures'];q['checks']=[
 {'check':'Expanded site A B material-preview comparison is stable','pass':True,'note':'The 5 cm camera shift shows one coherent exterior; no alternating duplicate LOD surfaces are visible.'},
 {'check':'Existing central architecture and white courtyard remain clear','pass':True,'note':'No MB7 source buildings are superimposed inside the protected reconstructed site.'},
 {'check':'Added road A B material-preview comparison retains the same continuous source surface','pass':True,'note':'The road surface and source UV remain continuous in the reviewed pair.'},
 {'check':'Added and existing photo textures load in native Blender preview','pass':True,'note':'No missing-image magenta surfaces are present in the six captures.'},
 {'check':'East exterior and source road connection are visually coherent','pass':True,'note':'The existing detailed house and neighbouring photographed street remain visible without an added facade overlay.'},
 {'check':'Actual exterior roam screenshot shows person on the included scan surface','pass':True,'note':'Reviewed V24_34_Exterior_Roam_UI.png together with the successful real keyboard route and jump reports.'}]
q['status']='PASS_NATIVE_MATERIAL_PREVIEW_VISUALLY_REVIEWED';q['review_basis']='Root agent inspected the six-capture contact sheet, exterior review sheet, and actual exterior roam screenshot.';q['source_quality_limits']='The supplied photogrammetry retains foliage holes, stretched tree textures and finite survey edges. They are not fabricated or replaced with unmeasured scenery; physics blocks unsupported edges.';P.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8');print('VISUAL_REVIEW_RECORDED',len(q['checks']))
