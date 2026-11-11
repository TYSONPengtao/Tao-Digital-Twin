"""Reflect the locally installed RhinoCommon API; do not open a model."""
from pathlib import Path
import json
import sys
W = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / 'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id(r'D:\AJAVIS01\RHINO8\RUNING\System').load(rhinoinside.__parse_framework_id('net48'))
import clr
clr.AddReference('RhinoCommon')
import Rhino
import System

file_type = clr.GetClrType(Rhino.FileIO.File3dm)
table_type = file_type.GetProperty('InstanceDefinitions').PropertyType
flags = System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance
methods = table_type.GetMethods(flags)
interesting = [m for m in methods if any(word in m.Name.lower() for word in ['delete', 'remove', 'clear', 'purge'])]
assembly = file_type.Assembly
version = System.Diagnostics.FileVersionInfo.GetVersionInfo(assembly.Location)
report = {
    'assembly_path': assembly.Location,
    'assembly_version': str(assembly.GetName().Version),
    'file_version': version.FileVersion,
    'property_type': table_type.FullName,
    'base_type': table_type.BaseType.FullName if table_type.BaseType is not None else None,
    'deletion_methods': [{'declaring_type': m.DeclaringType.FullName, 'signature': str(m),
                          'parameters': [{'name': p.Name, 'type': p.ParameterType.FullName, 'optional': p.IsOptional} for p in m.GetParameters()]}
                         for m in interesting],
    'interfaces': [t.FullName for t in table_type.GetInterfaces()],
    'all_public_instance_method_signatures': sorted(set(str(m) for m in methods))
}
print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)

rows = []
for prop in file_type.GetProperties(flags):
    if 'InstanceDefinition' not in prop.Name:
        continue
    actual_type = prop.PropertyType
    inheritance = [actual_type] + list(actual_type.GetInterfaces())
    mm = [m for tp in inheritance for m in tp.GetMethods(flags)
          if any(word in m.Name.lower() for word in ['delete', 'remove', 'clear', 'purge'])]
    rows.append({'property': prop.Name, 'declared_type': prop.PropertyType.FullName,
                 'deletion_methods': sorted(set(str(m.DeclaringType.FullName) + ': ' + str(m) for m in mm)),
                 'all_public_instance_methods': sorted(set(str(m) for m in actual_type.GetMethods(flags)))})
print(json.dumps({'declared_file_instance_definition_tables': rows}, ensure_ascii=False, indent=2), flush=True)
