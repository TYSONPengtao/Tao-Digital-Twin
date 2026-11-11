from pathlib import Path
W=Path(__file__).parent
s=(W/'v18_render_native.py').read_text(encoding='utf8').replace('V18','V19').replace('V17','V18')
s=s.replace("+['V19_Native_Storage_Eave_Gallery','V19_Native_Storage_Timber_Interior','V19_Native_Concave_Corner','V19_Native_Whole_Site','V19_Native_Top']","+['V19_Native_Whole_Site','V19_Native_Top']")
s=s.replace("sc.cycles.samples=24","sc.cycles.samples=24;sc.cycles.use_denoising=True")
(W/'v19_render_native.py').write_text(s,encoding='utf8')
print('V19_RENDER_SCRIPT_READY')
