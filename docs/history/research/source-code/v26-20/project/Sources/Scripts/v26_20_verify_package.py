"""Verify the delivered V26.20 package, its evidence and both native file hashes."""
from pathlib import Path
import json, hashlib, re, urllib.parse
from PIL import Image

O = Path('E:/jz/JIA/Rebuild_V26_20')
R, S = O / 'Reports', O / 'Sources'
checks = []


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf8'))


def ck(name, yes, **details):
    checks.append({'check': name, 'pass': bool(yes), **details})
    print('PACKAGE_QA', name, bool(yes), details if not yes else '', flush=True)


manifest = read(R / 'V26_20_Manifest.json')
invalid = []
for row in manifest['files']:
    path = O / row['path']
    if not path.is_file() or path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
        invalid.append(row['path'])
ck('Every delivered file matches its manifest SHA256 and size', not invalid,
   files=len(manifest['files']), invalid=invalid)
text = (R / 'V26_20_储藏房150mm台阶与厨房关系复核.html').read_text('utf8')
missing = []
for url in re.findall(r'(?:href|src)="([^"]+)"', text):
    if url.startswith(('http:', 'https:', '#', 'data:')):
        continue
    if not (R / urllib.parse.unquote(url)).exists():
        missing.append(url)
ck('All report images and artifact links resolve', not missing, missing=missing)

mh = sha(O / 'Blender/Architecture_Complete_V26_20.blend')
fh = sha(O / 'Blender/Architecture_Complete_V26_20_Fast.blend')
qa_names = ['Native_QA', 'Geometry_QA', 'Fast_Display_QA', 'Interior_Physics_QA',
            'Runtime_Viewport_QA', 'Door_Clearance_QA']
stale, failed = [], []
for name in qa_names:
    path = R / ('V26_20_' + name + '.json')
    if not path.is_file():
        failed.append(path.name)
        continue
    q = read(path)
    expected = fh if name in ['Fast_Display_QA', 'Runtime_Viewport_QA'] else mh
    if q.get('model_sha256') != expected:
        stale.append(path.name)
    if not q['status'].startswith('PASS') or q.get('failures'):
        failed.append(path.name)
ck('All six required QA reports pass against the delivered master or Fast hashes',
   not stale and not failed, reports=qa_names, stale=stale, failed=failed)

summary = read(R / 'V26_20_Delivery_Summary.json')
tags = summary['cases']
runtime = read(R / 'V26_20_Runtime_Viewport_QA.json')
expected_png = {version + '_' + tag + '.png' for version in ['V26_19', 'V26_20'] for tag in tags}
expected_png |= {Path(row['image']).name for row in runtime['captures']}
actual_png = {path.name for path in (R / 'Views').glob('*.png')}
decode_errors = []
for name in sorted(actual_png):
    try:
        with Image.open(R / 'Views' / name) as im:
            im.verify()
    except Exception as error:
        decode_errors.append({'image': name, 'error': str(error)})
ck('Six before-after pairs and four actual viewport images decode with no stale extra image',
   len(tags) == 6 and len(expected_png) == 16 and actual_png == expected_png and not decode_errors,
   image_count=len(actual_png), missing=sorted(expected_png - actual_png),
   extra=sorted(actual_png - expected_png), decode_errors=decode_errors)

changes = read(R / 'V26_20_Changes.json')
source_index = read(S / 'Input/Source_Index.json')
pairs = []
for tag in tags:
    before = read(R / 'Views' / ('V26_19_' + tag + '.json'))
    after = read(R / 'Views' / ('V26_20_' + tag + '.json'))
    good = (before['model_sha256'] == changes['source_sha256'] == source_index['sha256']
            and after['model_sha256'] == mh and before['camera'] == after['camera']
            and before['world'] == after['world'] and before['engine'] == after['engine']
            and before['temporary_lights'] == after['temporary_lights'] == 0)
    pairs.append({'tag': tag, 'pass': good})
ck('All six pairs use matching cameras and lighting with the frozen source and current master',
   len(pairs) == 6 and all(row['pass'] for row in pairs), pairs=pairs)
ck('All four actual Fast viewport captures use the delivered file without extra lights',
   len(runtime['captures']) == 4 and all(row['model_sha256'] == fh and row['actual_viewport']
   and row['extra_lights'] == 0 for row in runtime['captures']))
tour = runtime['captures'][0]
person = tour.get('person_m', [])
ck('First actual viewport runs the human tour outside the storage west entrance',
   tour.get('tour_running') and tour.get('grounded') and len(person) == 3
   and abs(person[0] - 12.85) < .01 and abs(person[1] + 15.7) < .01 and abs(person[2] + .4) < .02,
   person_m=person)
cmd = (O / '启动漫游.cmd').read_text('utf8')
ck('One launcher selects V26.20 Fast and all current runtime modules are present',
   sorted(path.name for path in O.glob('*.cmd')) == ['启动漫游.cmd']
   and 'Architecture_Complete_V26_20_Fast.blend' in cmd
   and all((O / 'Roam' / name).is_file() for name in
           ['start_roam_fast.py', 'roam_controller_fast.py', 'roam_physics.py']))
ck('The current V26.19 source is preserved byte for byte and matches the frozen source index',
   sha(Path(changes['source'])) == changes['source_sha256'] == source_index['sha256']
   and str(Path(changes['source']).resolve()) == str(Path(source_index['model']).resolve()))

run = read(S / 'Check_Run.json')
expected_steps = ['prepared_geometry', 'build', 'native_qa', 'geometry_qa', 'render',
                  'build_fast', 'verify_fast', 'physics_qa']
ck('All eight build and validation steps completed successfully',
   [row['step'] for row in run] == expected_steps and all(row['successful_process'] for row in run),
   steps=run)
door_qa = read(R / 'V26_20_Door_Clearance_QA.json')
ck('The explicit additional storage door clearance QA passes for the current master',
   door_qa['status'].startswith('PASS') and not door_qa.get('failures')
   and door_qa['model_sha256'] == mh and bool(door_qa['checks']))
required = ['Before_Snapshot.json', 'Native_After_Snapshot.json', 'Native_Snapshot_Source_SHA256.txt',
            'Protected_Object_State.json', 'Kitchen_Overlap_Audit.json', 'Prepared_Floor.json',
            'Prepared_Doors.json', 'Prepared.json', 'Prepared_Geometry_QA.json', 'Check_Run.json',
            'Input/Source_Index.json', 'Final/Geometry_Index.json', 'Performance/Fast_Build.json',
            'Scripts/v26_20_package.py', 'Scripts/v26_20_verify_package.py',
            'Scripts/v26_20_prepare_doors.py', 'Scripts/v26_20_door_clearance_qa.py',
            'Scripts/v26_20_materials.py']
ck('Inputs, preparations, readback, frozen snapshots, kitchen audit, door proof and scripts are retained',
   all((S / name).is_file() for name in required),
   missing=[name for name in required if not (S / name).is_file()])
ck('Current material authoring script is retained and the superseded one-off generator is excluded',
   (S / 'Scripts/v26_20_materials.py').is_file()
   and not (S / 'Scripts/v26_20_make_helpers.py').exists())
floor = read(S / 'Prepared_Floor.json')['proof']
doors = read(S / 'Prepared_Doors.json')['proof']['doors']
ck('Packaged proof retains the150mm rise, kitchen cutoff and both original door tops and rigs',
   abs(floor['rise_m'] - .15) < 1e-6 and abs(floor['entry_x_m'] - 13.421809196472168) < 1e-8
   and floor['wall_movement_m'] == floor['kitchen_movement_m'] == 0 and len(doors) == 2
   and all(abs(row['trimmed_height_m'] - .15) < 1e-6
           and row['old_top_z_m'] == row['new_top_z_m'] and not row['root_and_animation_changes']
           and not row['fixed_frame_changes'] and .008 < row['floor_clearance_m'] < .009
           and row['uv_proof']['missing_source_corner_uv_pairs'] == 0 for row in doors))
refs = read(R / 'V26_20_Reference_Index.json')
ck('Available user reference files retain their original SHA256',
   all((O / row['path']).is_file() and sha(O / row['path']) == row['sha256'] for row in refs),
   copied_references=len(refs), unavailable_reference_tokens=summary.get('missing_reference_tokens', []))
ck('Delivery summary records current model hashes and makes no new FPS measurement claim',
   summary['master_sha256'] == mh and summary['fast_sha256'] == fh
   and summary['reports'] == qa_names and summary['before_after_pairs'] == 6
   and summary['actual_viewport_captures'] == 4 and summary['png_count'] == 16
   and summary['new_fps_measurement'] is False)

failures = [row for row in checks if not row['pass']]
result = {'status': 'PASS' if not failures else 'FAIL', 'master_sha256': mh, 'fast_sha256': fh,
          'source_sha256': source_index['sha256'], 'checks': checks, 'failures': failures}
(R / 'V26_20_Package_QA.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf8')
print('PACKAGE_VERIFIED', len(checks), len(failures), flush=True)
if failures:
    raise AssertionError(failures)
