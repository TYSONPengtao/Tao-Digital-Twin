from pathlib import Path
W=Path(__file__).parent
s=(W/'v14_package.py').read_text(encoding='utf8').replace('Rebuild_V14','Rebuild_V15').replace('V14','V15').replace("len(g.get('cameras',[]))==8","len(g.get('cameras',[]))==10")
s=s.replace("assert 'V15_Valley_Detail' in views and 'V15_F3_Hall' in views","assert 'V15_Inner_Gate' in views and 'V15_F3_Bedroom' in views")
s=s.replace("assert len(g['images'])==5 and all('bufferView' in im and 'uri' not in im for im in g['images'])","assert len(g['images'])>=5 and all('bufferView' in im and 'uri' not in im for im in g['images']);assert sum('Tile_' in im.get('name','') for im in g['images'])==5")
s=s.replace("['Contact_QA','Opening_QA','Merge_Route_QA']","['V15_UV_Normal_QA','V15_Route_QA','V15_Bedroom_Roof_QA','V15_Tree_Pit_QA']")
s=s.replace("['Whole_Site','Top','Roof_Junction','Valley_Detail','Outer_Storage','F3_Hall','F3_Terrace','Terrace']","['Whole_Site','Top','Roof_Junction','Outer_Storage','Inner_Gate','Entry_Route','F3_Bedroom','F3_Vestibule','F3_Hall','South_Wall']")
s=s.replace("r['name'].startswith('SITE_V15_ORIGINAL_EXTERIOR')","r['name'].startswith('SITE_V14_ORIGINAL_EXTERIOR')")
s=s.replace("Production_1QK_Rhino_V15_Roof_Site_Storage.zip","Production_1QK_Rhino_V15_Model_Fixes.zip")
(W/'v15_package.py').write_text(s,encoding='utf8');print('package prepared')
