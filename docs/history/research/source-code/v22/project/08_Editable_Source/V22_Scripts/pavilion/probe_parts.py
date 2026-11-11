exec(open(__file__.replace('probe_parts.py','probe.py'),encoding='utf8').read().split('for e in S')[0])
import export_v5 as ex
ex.SCENE=S
for e in S['elements']:
 if e['name'] in ['SITE_GAZEBO_V11_BAMBOO_ROLLER_BLINDS','SITE_GAZEBO_V11_KNEE_BRACES','SITE_GAZEBO_V11_METAL_GUTTERS','SITE_GAZEBO_V11_TIMBER_RAILS']:
  print(e['name'])
  for j,p in enumerate(e['parts']):
   if j<15 or j%30==0:
    v,f=ex.world_part(p,e);print(j,v.min(0).round(4),v.max(0).round(4),p['material'])
