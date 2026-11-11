from pathlib import Path
W=Path(__file__).parent
s=(W/'check_exchange.py').read_text(encoding='utf-8').replace("OUT=Path(r'E:\\jz\\JIA\\Rebuild')", "OUT=Path(r'E:\\jz\\JIA\\Rebuild_V2')")
s=s.replace("'LOW_context_excluded':not any('SITE_TERRAIN_SIMPLIFIED' in o.name or 'COURTYARD_WALL_' in o.name for o in meshes)","'complete_site_present':all(any(key in o.name for o in meshes) for key in ['SITE_MAIN_COURTYARD_PAVING','SITE_KITCHEN','SITE_PERIMETER_JOINED_RETAINING_WALL','SITE_CURVED_PUBLIC_ROAD'])")
(W/'check_exchange_v2.py').write_text(s,encoding='utf-8')
