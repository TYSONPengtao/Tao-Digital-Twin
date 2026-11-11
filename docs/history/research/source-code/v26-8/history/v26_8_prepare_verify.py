from pathlib import Path
W=Path(__file__).parent
s=(W/'v26_7_verify_package.py').read_text('utf8').replace('Rebuild_V26_7','Rebuild_V26_8').replace('Architecture_Complete_V26_7.blend','Architecture_Complete_V26_8.blend').replace('V26_7_实景与修正复核.html','V26_8_实景与修正复核.html').replace("glob('After_*_Cycles.png')))==14","glob('After_*_Cycles.png')))==13")
(W/'v26_8_verify_package.py').write_text(s,'utf8')
