from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W),str(W/'v26_8_windows')]
from v26_2_common import *
import v26_2_common as C
from apply_house_recipe import apply_window_sills
BASE=W/'v26_8_windows';D=BASE/'Preview';D.mkdir(exist_ok=True);C.D=D
FD=W/'v26_7/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';a=np.load(FD/J[HN]['file']);house=tracked(a['v'],a['f'],J[HN]['materials'],a['mi'],a['uv'],HN)
house=apply_window_sills(house).simplify(1e-6)
r,_=export(HN,house,'Temporary isolated window-sill candidate for review only; not a final merged house')
(D/'Preview_House.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8')
