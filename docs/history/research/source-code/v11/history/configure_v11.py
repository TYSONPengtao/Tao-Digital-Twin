from pathlib import Path
W=Path(__file__).parent
def nextrev(s):return s.replace('V10','__NEXT_REV__').replace('V9','V10').replace('__NEXT_REV__','V11').replace('v10','__next_rev__').replace('v9','v10').replace('__next_rev__','v11')
for name in ['build_v10_patch.py','export_v10_changed_cad.py','validate_v10_changed_cad.py','merge_v10_cad.py','export_v10_native.py']:
 s=nextrev((W/name).read_text(encoding='utf-8'))
 if name=='merge_v10_cad.py':
  s=s.replace("wall_names=set(changed)|{'SITE_COURTYARD_WEST_TILE_WALL','SITE_COURTYARD_WEST_WHITE_INSIDE','SITE_GATE_EAST_FLANK','SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1'}", "wall_names={e['name'] for e in S['elements'] if e['layer']=='60_SITE' or e['name'].startswith('DOOR_OUTER_GATE')}")
  s=s.replace('Courtyard_Walls_V11_ALIGNED_ENU.3dm','Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm')
 if name=='export_v10_changed_cad.py':s=s.replace("mesh_solid=material=='M_Roof'", "mesh_solid=material in ['M_Roof','M_V11_Shingle','M_V11_Bamboo']")
 (W/nextrev(name)).write_text(s,encoding='utf-8')
print('V11 incremental exporters configured',flush=True)
