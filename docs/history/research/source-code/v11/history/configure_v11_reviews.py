from pathlib import Path
W=Path(__file__).parent
s=(W/'blender_v10_hybrid.py').read_text(encoding='utf8').replace('V10','V11')
s=s.replace("if e.get('definition'):","if e.get('definition') or (e.get('role')=='LEAF' and e.get('door_id')):")
s=s.replace("cameras=[('V11_Whole_Site',[54,-68,56],[0,0,3],54),('V11_Courtyard_Corner',[4,-15,6],[.2,-10.7,2.25],48),('V11_Wall_Detail',[4,-5.8,3.7],[0,-6,2.1],48),('V11_Perimeter_Detail',[-27,1,7],[-23,1,2.6],48)]","cameras=[('V11_Whole_Site',[54,-68,56],[0,0,3],54),('V11_Right_Angle',[7,-17,8],[.2,-11.5,1.9],48),('V11_Pavilion',[6,-10,4.3],[2.5,-5.35,1.1],56),('V11_Outer_Gate',[-23,-17,6],[-14,-10.5,1.3],52)]")
s=s.replace('sc.cycles.samples=16','sc.cycles.samples=12')
(W/'blender_v11_hybrid.py').write_text(s,encoding='utf8')
(W/'check_v11_exchange_photos.py').write_text((W/'check_v10_exchange_photos.py').read_text(encoding='utf8').replace('V10','V11'),encoding='utf8')
# Preserve all V10 interior entries and their actual hinge blocks; only gate
# records can be added. New faceted/analytic parts must be closed solids.
s=(W/'check_v10_delivery.py').read_text(encoding='utf8').replace('V10','__NEXT__').replace('V9','V10').replace('__NEXT__','V11')
s=s.replace("for k in ['door_registry','rooms','room_connectivity','definitions']:ck('unchanged_'+k,S[k]==oldS[k])", "for k in ['rooms','room_connectivity','definitions']:ck('unchanged_'+k,S[k]==oldS[k])\nck('old_door_registry_preserved',S['door_registry'][:len(oldS['door_registry'])]==oldS['door_registry'])")
s=s.replace("audit=read(O/'06_Report/Final_V11_Wall_QA.json');ck('independent_wall_reference_geometry',audit['status']=='PASS')", "audit=read(O/'06_Report/Final_V11_Site_QA.json');ck('independent_site_geometry',audit['status']=='PASS')")
s=s.replace("ck('13_hinged_doors',hinges==13)","ck('13_original_hinged_doors',hinges==13)\nfor d in S['door_registry'][len(oldS['door_registry']):]:\n ck('exterior_gate_registry_'+d['door_id'],bool(d.get('hinge_world_m') and d.get('leaf_element')))\nck('registry_door_entries',read(O/'02_Data/Interaction_Registry_V11.json')['door_registry']==S['door_registry'])")
(W/'check_v11_delivery.py').write_text(s,encoding='utf8')
print('V11 visual/exchange/preservation checks configured')
