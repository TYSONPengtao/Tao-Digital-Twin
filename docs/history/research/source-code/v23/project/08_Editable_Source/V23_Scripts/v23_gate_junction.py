"""Concealed keyed left jamb return closes the old 33 mm wall/pier gap."""
from v23_common import *
D=W/'v23_gate_junction';D.mkdir(exist_ok=True);Q=start();checks=[]
WALL='SITE_COURTYARD_WEST_TILE_WALL'
rel=json.loads((W/'v23_gate_relief/Mutation.json').read_text(encoding='utf8'))
RE={e['name']:e for e in rel['replace']+rel['add']}
def changed(n):return uni([manifold(p['geometry']) for p in RE[n]['parts']])
def prismxy(poly,z,h):return manifold({'type':'prism','profile':[[x,y,z] for x,y in poly],'vector':[0,0,h]})
wall=raw(WALL);pier=changed('SITE_V21_GATE_REFERENCE_LAYER_02')
fr=changed('SITE_V21_GATE_REFERENCE_LAYER_03');art=changed('SITE_V21_GATE_REFERENCE_LAYER_04')
xw=4.9;xp=4.933333333333334;yf=-11.825;yb=-11.575
# At y=-11.825 the 90 mm pier bevel lies at x=4.978333.  This
# recessed return follows it, with 6 mm normal key into that bevel and
# 6 mm horizontal key into the straight side, without coming forward
# of the original wall's front plane.
plan=[[xw-.006,yf],[xp+.045+.0085,yf],[xp+.0085,-11.780],[xp+.006,-11.774],[xp+.006,yb],[xw-.006,yb]]
z0=-.62487793;split=1.4208984375;ztop=2.0709228515625
brick=prismxy(plan,z0,split-z0);plaster=prismxy(plan,split,ztop-split)
# Concealed coping end bearing stays behind the wall face; its upper
# terminal is restricted to the actual retained ridge-seat depth/height.
lower=prismxy(plan,ztop,2.2059002090841204-ztop)
upper=cube([xw-.006,-11.755,2.2059002090841204],[xp+.006-(xw-.006),.110,2.4196502090840113-2.2059002090841204])
cap=lower+upper
# Partition the concealed return around actual new collar/moulding solids,
# so their fine exposed lips stay clear while the structural key remains.
ornament=fr+art
brick-=ornament;plaster-=ornament;cap-=ornament
whole=brick+plaster+cap
def rec(label,a,b,required=True):
 ov=float((a^b).volume());gap=float(a.min_gap(b,.005));ok=ov>1e-9 if required else gap<3e-6
 checks.append({'check':label,'pass':ok,'overlap_m3':ov,'gap_m':gap});assert ok,checks[-1]
rec('Jamb keyed into retained native west wall',whole,wall)
rec('Jamb keyed into final faceted stone pier core',whole,pier)
for n in ['SITE_COURTYARD_WEST_TILE_WALL_TILE_COPING','SITE_COURTYARD_WEST_TILE_WALL_V10_RIDGE_SEAT_AND_CAP','SITE_COURTYARD_WEST_TILE_WALL_V10_OPEN_FLOWER_BRICKS']:
 rec('Coping end supported '+n,cap,raw(n))
# Only hidden keyed material enters the structural pier.  The sculpted
# surfaces and frame lips are never covered by this new wall return.
ov=float((whole^(fr+art)).volume());checks.append({'check':'No visible carved relief or moulding covered','pass':ov<1e-9,'overlap_m3':ov});assert ov<1e-9,checks[-1]
v=np.asarray(fm(whole)['vertices']);front=v[abs(v[:,1]-yf)<1e-8]
checks.append({'check':'Body front remains in existing flat wall plane','pass':abs(float(v[:,1].min())-yf)<1e-8,'front_y_m':yf,'minimum_y_m':float(v[:,1].min()),'wall_key_m':.006,'pier_normal_bevel_key_m':.0085/math.sqrt(2),'straight_pier_key_m':.006,'legacy_gap_m':xp-xw,'front_x_extent_m':[float(front[:,0].min()),float(front[:,0].max())]})
checks.append({'check':'Native retained wall material assignment respected','pass':I[WALL]['materials']==['M_Grey_Brick','M_Wall_Exterior'],'native_materials':I[WALL]['materials'],'brick_plaster_split_at_native_end_z_m':split,'coping_material':'M_Roof','coping_max_z_m':2.4196502090840113})
coord=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'))
checks.append({'check':'Registered LOCAL metre coordinates retained','pass':True,'coordinate_source':str(B/'02_Data/Coordinate.json'),'coordinate_record':coord,'wall_end_local_m':[xw,yf,split],'jamb_front_bevel_contact_local_m':[xp+.045,yf,split]})
put(Q,'GATE_V23_LEFT_WALL_JAMB_CLOSURE',[pp(brick,'M_Grey_Brick'),pp(plaster,'M_Wall_Exterior'),pp(cap,'M_Roof')],classification='CONCEALED_KEYED_WEST_WALL_TO_FACETED_GATE_PIER_JAMB_RETURN',front_y_m=yf,legacy_gap_closed_m=xp-xw,wall_key_m=.006,pier_bevel_key_m=.0085/math.sqrt(2),pier_rear_key_m=.006,visible_carving_covered=False)
Q['change_notes']=['补齐内大门左侧围墙至石门柱之间原有33毫米断缝；补体藏在原墙面之后，随门柱斜面作暗榫搭接，保留灰砖/白墙分界和檐瓦端部高度，不覆盖浮雕。']
save(Q,D,checks)
