from pathlib import Path
W=Path(__file__).parent
s=(W/'v26_18_verify_package.py').read_text('utf8').replace('V26_18','V26_19').replace('V26.18','V26.19').replace('V26_17','V26_18').replace('V26.17','V26.18')
s=s.replace('楼梯板底与内门后部复核','梁端窗角与院内构件复核')
s=s.replace('Eight before-after pairs and four actual viewport images decode','Seven before-after pairs and four actual viewport images decode').replace('len(ps)==20','len(ps)==18')
s=s.replace('All eight pairs use matching cameras and lighting with current model hashes','All seven pairs use matching cameras and lighting with current model hashes').replace('len(pairs)==8','len(pairs)==7')
s=s.replace('First actual viewport runs the human tour on the stair','First actual viewport runs the human tour on the third-floor landing')
(W/'v26_19_verify_package.py').write_text(s,'utf8');print('PACKAGE_QA_READY')
