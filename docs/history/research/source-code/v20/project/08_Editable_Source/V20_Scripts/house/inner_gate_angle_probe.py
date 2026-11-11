from pathlib import Path
exec((Path(__file__).parent/'door_review.py').read_text().split("report={'status'")[0])
Q=json.loads((W/'v20/Mutation.json').read_text(encoding='utf8'));e=next(e for e in Q['add'] if e['name']=='SITE_V20_INNER_GATE__LEAF_R');pivot=np.array(e['pivot_world_m']);degree=e['open_angle_degrees'];m=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in e['parts']],mf.OpType.Add);closed=m.translate(-pivot).rotate([0,0,-degree]).translate(pivot)
names=['SITE_INNER_STONE_GATEHOUSE','SITE_KITCHEN_V12_GROUNDED_OUTER_COLUMN_STONE_BASES','SITE_KITCHEN_V12_BEFORE_WOOD_15','SITE_KITCHEN_STONE_FLOOR','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY'];colliders={n:get(n) for n in names};out=[]
for a in [65,64,63,62,61,60,59,58,57,56,55,54]:
 mm=closed.translate(-pivot).rotate([0,0,-a]).translate(pivot);hits={n:(mm^c).volume() for n,c in colliders.items()};out.append({'angle':-a,'volumes':hits});print(-a,hits,flush=True)
(D/'Inner_Gate_Angle_Probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
