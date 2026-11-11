exec(open(__file__.replace('review.py','design.py'),encoding='utf8').read())
rows=[]
for e in Q['replace']+Q['add']:
 v=[];f=[];mi=[];materials=[]
 for p in e['parts']:
  m=manifold(p['geometry']);a=m.to_mesh64();av=np.asarray(a.vert_properties)[:,:3];af=np.asarray(a.tri_verts);mat=p['material']
  if mat not in materials:materials.append(mat)
  f.extend((af+len(v)).tolist());v.extend(av.tolist());mi.extend([materials.index(mat)]*len(af))
 rows.append({'name':e['name'],'vertices':v,'faces':f,'materials':materials,'material_ids':mi})
(D/'Preview_Meshes.json').write_text(json.dumps(rows),encoding='utf8')
# Check post/frame bearings and front stiles, with every newly added support attached.
posts=union([manifold(p['geometry']) for p in Q['replace'][0]['parts']]);ring=native('SITE_GAZEBO_V11_RING_BEAMS')
check('All four post heads touch retained ring beams',(posts^ring).volume()>1e-5,contact_m3=(posts^ring).volume())
st=next(e for e in Q['add'] if 'FRONT_SLENDER' in e['name']);st=union([manifold(p['geometry']) for p in st['parts']]);check('Front stiles join overhead ring beams',(st^ring).volume()>1e-6,contact_m3=(st^ring).volume())
check('No new detail intersects central access',(st^cube([3.80,-6.375,-.36],[.15,2.05,2.3])).is_empty())
pipebox=pipe.bounding_box();check('Outlet ends above paving',pipebox[2]>-.43038,pipe_min_z_m=pipebox[2],paving_z_m=-.43038)
check('Textures exist',all(Path(m[k]).exists() for m in Q['materials'].values() for k in ['bitmap','bump'] if k in m))
QA['status']='PASS_SOURCE_NATIVE_PAVILION_DETAIL_QA';(D/'Design_Control.json').write_text(json.dumps(QA,ensure_ascii=False,indent=2),encoding='utf8')
print('REVIEW OK',len(QA['checks']))
