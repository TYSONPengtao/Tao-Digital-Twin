from v26_2_common import *
import html
D=W/'v26_17';O=Path('E:/jz/JIA/Rebuild_V26_17/Reports');O.mkdir(parents=True,exist_ok=True);p=json.loads((D/'Prepared.json').read_text('utf8'))['proof']
def points(ps):return' '.join(f'{x:.7f},{y:.7f}'for x,y in ps)
def rect(lo,hi,fill,**props):return f'<rect x="{lo[0]}" y="{lo[1]}" width="{hi[0]-lo[0]}" height="{hi[1]-lo[1]}" fill="{fill}" '+ ' '.join(f'{k.replace("_","-")}="{v}"'for k,v in props.items())+'/>'
style='<style>text{font-family:Microsoft YaHei,sans-serif;fill:#233f45}.small{font-size:16px}.title{font-size:25px;font-weight:600}</style>'
parts=[]
for q in[p for p in p['parts']if p['floor']==1 and p['type']=='slab'and p['tag']=='floor']:
 parts.append(f'<polygon points="{points(q["plan"]["coordinates"][0])}" fill="#e4ecef"/>')
parts.append(rect([0,1.9747],[13,2.2253],'#dfb25f'))
for x in p['axes_x_m']:parts.append(rect([x-.2,1.9],[x+.2,2.3],'#667581'))
for b in[q for q in p['bays']if q['floor']==1]:
 x0=b['axis_span_m'][0];old=[(x0,2.1),(x0+.72,1.1),(x0+3.18,1.1),(x0+3.9,2.1)];new=b['new_bay_plan']['coordinates'][0][:4]
 parts.append(f'<polyline points="{points(old)}" fill="none" stroke="#bf4a44" stroke-width=".045" stroke-dasharray=".09,.055"/>');parts.append(f'<polyline points="{points(new)}" fill="none" stroke="#117b9d" stroke-width=".045"/>')
labels=[]
for i,x in enumerate(p['axes_x_m'],1):
 xx=75+x*80;labels.append(f'<line x1="{xx}" y1="158" x2="{xx}" y2="330" stroke="#98a8ac" stroke-dasharray="4 5"/><circle cx="{xx}" cy="352" r="17" fill="white" stroke="#748b91"/><text x="{xx}" y="358" text-anchor="middle">{i}</text>')
for a,b,txt in[(0,3.9,'3900'),(3.9,9.1,'5200'),(9.1,13,'3900')]:
 labels.append(f'<line x1="{75+a*80}" y1="320" x2="{75+b*80}" y2="320" stroke="#7c9095"/><text class="small" x="{75+(a+b)*40}" y="311" text-anchor="middle">{txt}</text>')
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="430" viewBox="0 0 1200 430">{style}<rect width="1200" height="430" fill="#fff"/><text class="title" x="35" y="43">原柱轴与固定斜窗的接合关系</text><text class="small" x="35" y="75">轴线尺寸依据本次图纸：3900＋5200＋3900＝13000 mm</text><g transform="translate(75,340) scale(80,-80)">{"".join(parts)}</g>{"".join(labels)}<text class="small" x="35" y="405">灰：原柱芯　金：梁　浅灰：板边　红虚线：原斜窗　蓝：修正后固定窗（中央开启扇不变）</text></svg>'
(O/'V26_17_轴线与梁柱板平面.svg').write_text(svg,'utf8')
source=json.loads((D/'Input/Source_Index.json').read_text('utf8'));ix={r['name']:r for r in source['objects']};name='BAY_WINDOW_F1_R_0_Geometry';sa=np.load(D/'Input'/ix[name]['file']);na=np.load(D/'Prepared'/(name+'.npz'))
def section_path(a):
 m=solid(a['v'],a['f']);rings=m.slice(2.5).to_polygons();return' '.join('M'+' L'.join(f'{x:.8f},{y:.8f}'for x,y in ring)+' Z'for ring in rings)
details=rect([8.9,1.9],[9.3,2.3],'#84919b')+rect([8.6,1.9747],[10.1,2.2253],'#dfb25f',fill_opacity='.5')
details+=f'<path d="{section_path(sa)}" fill="#c75c53" fill-opacity=".65" fill-rule="evenodd"/><path d="{section_path(na)}" fill="#16829f" fill-opacity=".85" fill-rule="evenodd"/>'
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="680" viewBox="0 0 800 680">{style}<rect width="800" height="680" fill="white"/><text class="title" x="30" y="43">节点放大：窗止于柱前，梁柱不再被窗反切</text><text class="small" x="30" y="77">来自实际修改前后窗框在 Z＝2.50m 的剖切；灰色为原模型400mm柱基准</text><g transform="translate(-2820,955) scale(350,-350)">{details}</g><text class="small" x="30" y="625">红：原窗框/玻璃剖面（进入柱范围）　蓝：修正剖面（柱前净距约20mm）</text><text class="small" x="30" y="653">截面沿用原文件定义；净距为模型拟合值，未作为新增现场实测尺寸。</text></svg>'
(O/'V26_17_窗框柱前节点.svg').write_text(svg,'utf8');print('DIAGRAMS_SAVED',flush=True)
