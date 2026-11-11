from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import json, hashlib

O = Path('E:/jz/JIA/Rebuild_V26_11')
checks = []


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def ck(n, p, **kw):
    checks.append({'check': n, 'pass': bool(p), **kw})
    print('PACKAGE', n, bool(p), kw if not p else '', flush=True)


M = json.loads((O / 'Manifest_SHA256.json').read_text('utf8'))
bad = []
for r in M['files']:
    p = O / r['file']
    if not p.exists() or p.stat().st_size != r['bytes'] or sha(p) != r['sha256']:
        bad.append(r['file'])
ck('All packaged files match their recorded size and SHA256', not bad, files=len(M['files']), invalid=bad)
ck('V26.10 source file remains byte-identical', sha(M['source_model']) == M['source_sha256'])
ck('Both native models match verified model hashes', sha(O / 'Blender/Architecture_Complete_V26_11.blend') == M['model_sha256'] and sha(O / 'Blender/Architecture_Complete_V26_11_Fast.blend') == M['fast_model_sha256'])


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links += [v for k, v in attrs if k in ['src', 'href'] and v and not v.startswith(('#', 'https:', 'http:'))]


page = O / 'Reports/V26_11_实景与修正复核.html'
x = Links()
x.feed(page.read_text('utf8'))
self_report = (O / 'Reports/V26_11_Package_QA.json').resolve()
bad = [s for s in x.links if (page.parent / unquote(s)).resolve() != self_report and not (page.parent / unquote(s)).resolve().is_file()]
ck('Every local review-page image and link resolves', not bad, links=len(x.links), invalid=bad)
bad, count = [], 0
for r in M['checks']:
    q = json.loads((O / 'Reports' / r['file']).read_text('utf8'))
    count += len(q['checks'])
    if not q['status'].startswith('PASS') or q['failures'] or not all(c['pass'] for c in q['checks']):
        bad.append(r['file'])
    want = M['fast_model_sha256'] if 'Fast_Display_QA' in r['file'] else M['model_sha256']
    if q['model_sha256'] != want:
        bad.append(r['file'] + ' stale model hash')
ck('All saved-model and visual checks pass against delivered hashes', not bad, checks=count, invalid=bad)
ck('One default Fast roam launcher and no Rhino export', sorted(p.name for p in O.glob('*.cmd')) == ['启动漫游.cmd'] and not list(O.rglob('*.3dm')))
refs = json.loads((O / 'References/Reference_Index.json').read_text('utf8'))
bad = [q['name'] for q in refs if q['packaged_path'] and sha(O / q['packaged_path']) != q['sha256']]
ck('All available reference images copied unchanged', not bad and sum(bool(q['packaged_path']) for q in refs) >= 6, local_images=sum(bool(q['packaged_path']) for q in refs), invalid=bad)
views = list((O / 'Reports').glob('After_*.json'))
bad = [p.name for p in views if json.loads(p.read_text('utf8'))['model_sha256'] != M['model_sha256']]
ck('All twelve final review views correspond to delivered master', len(views) == 12 and not bad, views=len(views), invalid=bad)
fail = [q for q in checks if not q['pass']]
(O / 'Reports/V26_11_Package_QA.json').write_text(json.dumps({
    'status': 'PASS' if not fail else 'FAIL', 'model_sha256': M['model_sha256'],
    'fast_model_sha256': M['fast_model_sha256'], 'checks': checks, 'failures': fail,
    'files_verified': len(M['files']), 'saved_model_checks': count,
}, ensure_ascii=False, indent=2), 'utf8')
print('V26_11_PACKAGE_VERIFIED', len(M['files']), len(fail), flush=True)
assert all((page.parent / unquote(s)).resolve().is_file() for s in x.links)
if fail:
    raise AssertionError(fail)
