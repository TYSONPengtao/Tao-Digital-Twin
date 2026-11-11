exec((__import__('pathlib').Path(__file__).parent/'saved_native_qa.py').read_text('utf8').split('checks=[]')[0]+'checks=[]')
def bounds(m):
 q=m.to_mesh64();v=np.array(q.vert_properties[:,:3]);return[v.min(0).tolist(),v.max(0).tolist()]if len(v)else None
def details(m):return[{'volume_m3':p.volume(),'bounds':bounds(p)}for p in sorted(m.decompose(),key=lambda p:-p.volume())if p.volume()>1e-12]
PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))};q=np.load(PD/PI['ROOF_EAVE_FASCIA_Geometry']['file']);roof=solid(q['v'],q['f']);print('REMOVED_ROOF',json.dumps(details((roof^old)-m),indent=1))
region=cube([-1.,0.,-1.],[15.,11.,7.049]);print('LOWER_REMOVED',json.dumps(details((old-m)^region)[:20],indent=1));print('LOWER_ADDED',json.dumps(details((m-old)^region)[:20],indent=1))
print('HEAD')
for x in [2.6,2.95,3.,3.05,3.1,3.15,3.3,3.5]:
 for z in [9.945,9.965,9.985,10.005,10.015]:
  vals=[]
  for o in [old,m]:vals.append([h.position for h in o.ray_cast([x,9.4,z],[x,10.1,z])])
  print(x,z,vals)
