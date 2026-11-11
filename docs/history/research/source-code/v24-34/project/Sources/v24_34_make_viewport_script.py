from pathlib import Path
W=Path(__file__).parent;s=(W/'v24_33_viewport_qa.py').read_text('utf8').replace('V24_33','V24_34');start=s.index('jobs=');end=s.index('\n',start)
s=s[:start]+"jobs=[('01_Expanded_Site','A'),('01_Expanded_Site','B'),('02_Original_House_And_Context','A'),('03_Added_South_Road','A'),('03_Added_South_Road','B'),('05_East_Context','A')]"+s[end:];(W/'v24_34_viewport_qa.py').write_text(s,encoding='utf8')
