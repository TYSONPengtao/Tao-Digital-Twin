import sys,json,collections,math,time
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
P=Path(r'E:\jz\JIA\Rebuild_V12');O=W/'v13_structure';O.mkdir(exist_ok=True)
S=json.loads((P/'08_Editable_Source/Architecture_Scene_V12.json').read_text(encoding='utf8'))
C=json.loads((P/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
scene={e['name']:e for e in S['elements']};f=rh.File3dm.Read(str(P/'04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm'))
print('loaded',len(f.Objects),flush=True)
rows=[];defs=[];counts=collections.Counter();matched=collections.Counter()
for d in f.InstanceDefinitions:
 defs.append({'name':d.Name,'id':str(d.Id),'objects':[str(x) for x in d.GetObjectIds()]})
definition_members={x for d in defs for x in d['objects']}
for ob in f.Objects:
 at=ob.Attributes;g=ob.Geometry;n=at.Name;kind=type(g).__name__;base=n.rsplit('__',1)[0] if '__' in n and n.rsplit('__',1)[1].isdigit() else n
 if base in scene:matched[base]+=1
 counts[(kind,at.IsInstanceDefinitionObject,base in scene)]+=1
 try:
  b=g.GetBoundingBox();q=np.array([[x,y,z] for x in [b.Min.X,b.Max.X] for y in [b.Min.Y,b.Max.Y] for z in [b.Min.Z,b.Max.Z]]);ql=(q-origin)@R
  bb=[ql.min(0).tolist(),ql.max(0).tolist()]
 except Exception as ex:bb=None
 row={'id':str(at.Id),'name':n,'base':base,'type':kind,'definition_flag':at.IsInstanceDefinitionObject,'in_definition':str(at.Id) in definition_members,'mode':str(at.Mode),'visible':at.Visible,'layer':f.Layers.FindIndex(at.LayerIndex).Name,'layer_index':at.LayerIndex,'material':f.Materials.FindIndex(at.MaterialIndex).Name if at.MaterialIndex>=0 else str(at.MaterialIndex),'material_source':str(at.MaterialSource),'groups':list(at.GetGroupList()),'bbox_local':bb,'matched_scene':base in scene,'v12_element':at.GetUserString('V12_Element'),'userstrings':list(at.GetUserStrings())}
 if kind=='InstanceReference':row['parent_definition']=str(g.ParentIdefId)
 rows.append(row)
(O/'Native_Object_Inventory_V12.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8')
(O/'Definitions_V12.json').write_text(json.dumps(defs,ensure_ascii=False,indent=2),encoding='utf8')
unmatched=[r for r in rows if not r['matched_scene'] and not r['definition_flag']]
badflags=[r for r in rows if r['in_definition']!=r['definition_flag']]
report={'objects':len(rows),'definitions':len(defs),'counts':[{ 'type':k[0],'definition':k[1],'matched':k[2],'count':v} for k,v in counts.items()],'unmatched_objects':len(unmatched),'unmatched_prefixes':dict(collections.Counter(r['base'] for r in unmatched)),'bad_definition_flags':len(badflags),'missing_scene_names':[n for n in scene if n not in matched],'definition_examples':defs[:5],'unmatched_examples':unmatched[:20],'bad_flag_examples':badflags[:10]}
(O/'Inventory_Summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
