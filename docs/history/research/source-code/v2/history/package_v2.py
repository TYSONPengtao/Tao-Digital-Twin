from pathlib import Path
import json,shutil,zipfile,hashlib,csv
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V2');outputs=W.parent/'outputs';dest=outputs/'Production_1QK_Rebuild_V2'
qa=json.loads((O/'09_Report/Native_Model_QA.json').read_text(encoding='utf-8'));exchange=json.loads((O/'09_Report/Exchange_Readback_QA.json').read_text(encoding='utf-8'));geom=json.loads((O/'09_Report/Geometry_QA_V2.json').read_text(encoding='utf-8'))
for mode,data in qa.items():assert not data['rhino']['invalid'] and not data['rhino']['unexpected_open_solids'] and not data['sketchup']['solid_failures']
for mode,formats in exchange.items():
 for ext,r in formats.items():assert r['import_success'] and not r['invalid_coordinates'] and r['degenerate_faces']==0 and r['complete_site_present'] and abs(r['known_door_width_m']-.9)<1e-5
assert not geom['nonmanifold_parts'] and not geom['nonpositive_signed_volume'] and not geom['exact_duplicate_solids']
def ignore(path,names):return [n for n in names if n.endswith('.blend1') or '_validated.' in n or n=='__pycache__']
shutil.copytree(O,dest,dirs_exist_ok=True,ignore=ignore)
rows=[]
for p in sorted(dest.rglob('*')):
 if not p.is_file():continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 rows.append([p.relative_to(dest).as_posix(),p.stat().st_size,h.hexdigest()])
with (dest/'09_Report/Deliverable_Manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['File','Bytes','SHA256']);w.writerows(rows)
zip_path=outputs/'Production_1QK_Rebuild_V2_Package.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(dest.rglob('*')):
  if p.is_file():z.write(p,'Production_1QK_Rebuild_V2/'+p.relative_to(dest).as_posix())
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
print(json.dumps({'output_directory':str(dest),'package':str(zip_path),'files':len(rows)+1,'package_mb':round(zip_path.stat().st_size/1024**2,1),'checks':'Native validity, solid volume, exchange readback, dimensions, zero degenerates, complete site, ZIP CRC passed'},ensure_ascii=False))
