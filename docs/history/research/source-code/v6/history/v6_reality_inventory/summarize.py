import sys,json,hashlib,os,collections,csv
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'libs'));import rhino3dm as r
O=Path(__file__).resolve().parent
R=json.loads((O/'New_Rhino_Inventory.json').read_text(encoding='utf-8'))
rows=[]
for rec in R:
 f=r.File3dm.Read(rec['path'])
 s={k:rec[k] for k in ['path','bytes','units','objects']};s['meshes']=sum(g['type']=='ObjectType.Mesh' for g in rec['geometry']);s['vertices']=sum(g.get('vertices',0) for g in rec['geometry']);s['faces']=sum(g.get('faces',0) for g in rec['geometry']);s['uv']=sum(g.get('uv',0) for g in rec['geometry']);s['all_meshes_have_vertex_uv']=all(g.get('uv',0)==g.get('vertices',0) for g in rec['geometry'] if g['type']=='ObjectType.Mesh')
 bounds=[g['bbox'] for g in rec['geometry'] if 'bbox' in g];s['bbox']=[[min(b[0][i] for b in bounds) for i in range(3)],[max(b[1][i] for b in bounds) for i in range(3)]]
 tt=sorted(set(t['file'] for m in rec['materials'] for t in m['textures']));s['unique_textures']=[dict(path=t,exists=Path(t).is_file(),bytes=Path(t).stat().st_size if Path(t).is_file() else None) for t in tt]
 for method in ['EmbeddedFilePaths','EmbeddedFilePaths2']:
  try:
   v=getattr(f,method)();s[method]=list(v)
  except Exception as e:s[method]=str(e)
 s['embedded_count_api']=len(f.EmbeddedFiles) if hasattr(f.EmbeddedFiles,'__len__') else str(f.EmbeddedFiles)
 try:
  s['embedded_files']=[dict(filename=a.Filename) for a in f.EmbeddedFiles]
 except Exception as e:s['embedded_files_error']=str(e)
 print(json.dumps(s,ensure_ascii=False)[:6000],flush=True);rows.append(s)
(O/'New_Rhino_Summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
allfiles=[]
exts={'.obj','.mtl','.fbx','.glb','.3dm','.ccm','.3mx','.3mxb','.osgb','.ply','.las','.laz'}
for root,dirs,files in os.walk(r'E:\jz'):
 dirs[:]=[d for d in dirs if not d.startswith('Rebuild')]
 for name in files:
  p=Path(root)/name
  if p.suffix.lower() in exts:allfiles.append(dict(path=str(p),extension=p.suffix.lower(),bytes=p.stat().st_size,mtime=p.stat().st_mtime))
with (O/'All_Reality_Model_Files.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['path','extension','bytes','mtime']);w.writeheader();w.writerows(allfiles)
(O/'Extension_Counts.json').write_text(json.dumps(dict(collections.Counter(a['extension'] for a in allfiles)),indent=2),encoding='utf-8')
print('inventory',len(allfiles),flush=True)
