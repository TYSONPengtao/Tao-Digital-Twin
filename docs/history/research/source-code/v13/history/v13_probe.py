import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'libs'),str(W/'np1'),str(W)]
import rhino3dm as rh
P=Path(r'E:\jz\JIA\Rebuild_V12');S=json.loads((P/'08_Editable_Source/Architecture_Scene_V12.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']}
f=rh.File3dm.Read(str(P/'04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm'))
for name in ['FACADE_CONTINUOUS_F3','CONSTRUCTION_RAINWATER_RECEIVER_NE','TERRACE_STONE_PARAPET','UTILITY_PARAPET_WEST','CONSTRUCTION_SILL_BAY_WINDOW_F3_X0_L','TERRACE_CANOPY','TERRACE_CANOPY_VISIBLE_PURLINS']:
 if name not in E:continue
 e=E[name];print('\nSCENE',name,json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False),flush=True)
 print('PARTS',json.dumps(e.get('parts',[])[:3],ensure_ascii=False),flush=True)
 for ob in f.Objects:
  if ob.Attributes.Name==name+'__1':
   g=ob.Geometry;print('NATIVE',type(g).__name__,'profilecount',getattr(g,'ProfileCount',None),'path',getattr(g,'PathStart',None),getattr(g,'PathEnd',None),flush=True)
   if isinstance(g,rh.Extrusion):
    for i in range(g.ProfileCount):
     for t in [0,1]:
      c=g.Profile3d(i,t);bb=c.GetBoundingBox();print('PROFILE',i,t,[bb.Min.X,bb.Min.Y,bb.Min.Z],[bb.Max.X,bb.Max.Y,bb.Max.Z],flush=True)
for e in S['elements']:
 if any(s in e['name'] for s in ['TERRACE','CANOPY','UTILITY_PARAPET']):
  print('FOCUS',e['name'],'parts',len(e.get('parts',[])),json.dumps({k:v for k,v in e.items() if k not in ['parts','source']},ensure_ascii=False),flush=True)
