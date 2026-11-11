"""Read-only instance-definition dependency audit for the wall/site companion."""
from pathlib import Path
import collections
import hashlib
import json
import sys

W = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / 'libs'))
import rhino3dm as rh

OUT = Path(__file__).parent
P = Path(r'E:\jz\JIA\Rebuild_V11_Hybrid\04_Rhino\Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm')
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()
before = sha(P)
F = rh.File3dm.Read(str(P))
assert F is not None
obs = {str(o.Attributes.Id): o for o in F.Objects}
defs = {str(d.Id): d for d in F.InstanceDefinitions}
layers = {l.Index: l for l in F.Layers}
top = [o for o in F.Objects if not o.Attributes.IsInstanceDefinitionObject]
top_instances = [o for o in top if isinstance(o.Geometry, rh.InstanceReference)]
visible_instances = [o for o in top_instances if o.Attributes.Visible and layers[o.Attributes.LayerIndex].Visible]
invalid = [o.Attributes.Name for o in F.Objects if not o.Geometry.IsValid]
checks = []
def ck(name, ok, detail=None):
    checks.append({'id': name, 'status': 'PASS' if bool(ok) else 'FAIL', 'detail': detail})
ck('companion_all_geometry_valid', not invalid, {'objects': len(obs), 'invalid': invalid, 'geometry_types': dict(collections.Counter(type(o.Geometry).__name__ for o in F.Objects))})
ck('companion_units_metres', F.Settings.ModelUnitSystem == rh.UnitSystem.Meters)
definition_rows = []
for did, d in defs.items():
    ids = [str(x) for x in d.GetObjectIds()]
    missing = [x for x in ids if x not in obs]
    definition_rows.append({'definition_id': did, 'name': d.Name, 'object_ids_count': len(ids), 'missing_object_ids': missing, 'definition_is_valid': bool(d.IsValid)})

visited = set()
dependency_failures = []
def traverse(did, stack, source):
    if did in stack:
        dependency_failures.append({'source': source, 'definition_id': did, 'reason': 'CYCLE', 'chain': stack + [did]})
        return
    if did not in defs:
        dependency_failures.append({'source': source, 'definition_id': did, 'reason': 'MISSING_DEFINITION'})
        return
    if did in visited:
        return
    visited.add(did)
    d = defs[did]
    ids = [str(x) for x in d.GetObjectIds()]
    if not ids:
        dependency_failures.append({'source': source, 'definition_id': did, 'reason': 'EMPTY_REFERENCED_DEFINITION'})
    for oid in ids:
        o = obs.get(oid)
        if o is None:
            dependency_failures.append({'source': source, 'definition_id': did, 'object_id': oid, 'reason': 'MISSING_DEFINITION_GEOMETRY'})
            continue
        if not o.Attributes.IsInstanceDefinitionObject:
            dependency_failures.append({'source': source, 'definition_id': did, 'object_id': oid, 'reason': 'REFERENCED_MEMBER_NOT_DEFINITION_OBJECT'})
        if not o.Geometry.IsValid:
            dependency_failures.append({'source': source, 'definition_id': did, 'object_id': oid, 'reason': 'INVALID_REFERENCED_GEOMETRY'})
        if isinstance(o.Geometry, rh.InstanceReference):
            traverse(str(o.Geometry.ParentIdefId), stack + [did], source)

instance_rows = []
for o in top_instances:
    did = str(o.Geometry.ParentIdefId)
    source = o.Attributes.Name
    traverse(did, [], source)
    instance_rows.append({'object_id': str(o.Attributes.Id), 'name': source, 'visible': bool(o.Attributes.Visible and layers[o.Attributes.LayerIndex].Visible), 'definition_id': did, 'definition_exists': did in defs, 'definition_object_ids_count': len(defs[did].GetObjectIds()) if did in defs else 0})
ck('companion_all_top_level_instance_dependencies_resolve', not dependency_failures, {'top_level_instances': len(top_instances), 'visible_instances': len(visible_instances), 'reachable_definitions': len(visited), 'failures': dependency_failures})
unused_incomplete = [r for r in definition_rows if r['definition_id'] not in visited and (r['missing_object_ids'] or not r['object_ids_count'])]
after = sha(P)
ck('companion_stable_during_read_only_audit', before == after)
report = {'status': 'PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL', 'path': str(P), 'sha256': after,
          'actual_objects': len(obs), 'top_level_objects': len(top), 'definition_geometry_objects': len(obs) - len(top),
          'actual_top_level_instances': len(top_instances), 'actual_visible_instances': len(visible_instances),
          'definitions': len(defs), 'reachable_definitions': len(visited), 'dependency_failures': dependency_failures,
          'instance_references': instance_rows, 'definition_inventory': definition_rows,
          'unused_incomplete_definition_count': len(unused_incomplete),
          'unused_incomplete_definitions': unused_incomplete,
          'method': 'Inspect actual InstanceReference objects; recursively resolve ParentIdefId and every instance-definition GetObjectIds against the file object table, including nested references and cycles. Also inspect actual visibility, member definition flags, geometry validity, and all retained definitions.',
          'checks': checks}
(OUT / 'Companion_QA.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
main_path = OUT / 'QA.json'
if main_path.exists():
    main = json.loads(main_path.read_text(encoding='utf8'))
    main['checks'] = [c for c in main['checks'] if not c['id'].startswith('companion_')] + checks
    main['courtyard_pavilion_gate_companion'] = {k: v for k, v in report.items() if k != 'checks'}
    main['input_sha256']['courtyard_companion'] = after
    main['passed_checks'] = sum(c['status'] == 'PASS' for c in main['checks'])
    main['failed_checks'] = sum(c['status'] == 'FAIL' for c in main['checks'])
    main['status'] = 'PASS' if main['failed_checks'] == 0 else 'FAIL'
    main_path.write_text(json.dumps(main, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({k: report[k] for k in ['status', 'actual_objects', 'top_level_objects', 'definition_geometry_objects', 'actual_top_level_instances', 'actual_visible_instances', 'definitions', 'reachable_definitions', 'dependency_failures', 'unused_incomplete_definition_count']}, ensure_ascii=False), flush=True)
if report['status'] != 'PASS':
    raise SystemExit(1)
