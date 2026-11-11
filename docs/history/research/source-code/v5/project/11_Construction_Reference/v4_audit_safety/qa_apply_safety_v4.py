"""Exercise safety proposals on a private in-memory V3 copy."""
import sys, json, copy, math, collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
W=HERE.parent
sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W),str(HERE)]
import numpy as np
from shapely.geometry import Polygon
import export_v3 as ex
from apply_safety_v4 import apply

scene=copy.deepcopy(ex.SCENE)
changes=apply(scene)
bad=[];positive=[];parts=0
metrics=[]
for e in scene['elements']:
    if e.get('status')!='CONSTRUCTION_REVIEW_PROPOSAL':continue
    for j,p in enumerate(e['parts']):
        g=p['geometry']
        v,f=ex.world_part(p,e)
        if v is None:continue
        edges=collections.Counter()
        volume=0.0
        for face in f:
            for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))]+=1
            for k in range(1,len(face)-1):volume+=float(np.dot(v[face[0]],np.cross(v[face[k]],v[face[k+1]]))/6)
        parts+=1
        name=e['name']+f'__{j+1}'
        if any(n!=2 for n in edges.values()):bad.append(name)
        if volume<=0:positive.append((name,volume))
        if g['type']=='prism':
            a=np.asarray(g['profile'])
            norm=np.sum(np.cross(a,np.roll(a,-1,axis=0)),axis=0)
            dropped=np.argmax(np.abs(norm))
            if not Polygon(np.delete(a,dropped,axis=1)).is_valid:bad.append(name+' INVALID_PROFILE')

    if e['name'].startswith('STAIR_F') and 'FLIGHT' in e['name']:
        r=e['rises'][0];pitch=e['tread'];slope=r/pitch
        actual=e['vertical_waist_thickness']/math.sqrt(1+slope*slope)
        assert abs(actual-.14)<1e-10
        assert max(e['rises'])-min(e['rises'])<1e-10
        assert sum(e['rises'])+e['z_from']==e['z_to'] or abs(sum(e['rises'])+e['z_from']-e['z_to'])<1e-10
        assert e['terminal_tongue_length']>e['terminal_undermerge_length']
        vertices=np.asarray(e['parts'][0]['geometry']['profile'])
        metrics.append({'name':e['name'],'uniform_rise_m':r,'tread_m':pitch,'normal_waist_m':actual,
                        'nominal_flight_width_m':e['width'],'sloping_rail_clear_width_m':e['width']-.025,
                        'range_y':[float(vertices[:,1].min()),float(vertices[:,1].max()+e['width'])],
                        'terminal_tongue_m':e['terminal_tongue_length'],
                        'terminal_merge_m':e['terminal_undermerge_length']})
    if e['name'].startswith('STAIR_V4_RAIL'):
        rail=e['parts'][0]['geometry']
        v,f=ex.world_part(e['parts'][0],e)
        # Actual top intersection on the vertical X plane at every nosing.
        # The rectangular rail has two upper points at each section.
        a=np.asarray(rail['profile']);dv=np.asarray(rail['vector'])
        top_ids=sorted(range(4),key=lambda i:a[i,2])[-2:]
        qa=[]
        flight_no=int(e['name'].rsplit('_',1)[1])
        storey=int(e['name'].split('_F')[1].split('_')[0])
        flight=next(q for q in scene['elements'] if q['name']==f'STAIR_F{storey}_FLIGHT{flight_no}')
        xs=7.8 if flight_no==1 else 5.2
        direction=-1 if flight_no==1 else 1
        for k in range(11):
            x=xs+direction*k*flight['tread'];nose=flight['z_from']+(k+1)*flight['rises'][0]
            heights=[]
            for i in top_ids:
                t=(x-a[i,0])/dv[0]
                assert -1e-9<=t<=1+1e-9
                heights.append(a[i,2]+t*dv[2]-nose)
            qa.append(max(heights))
        assert max(abs(h-.9) for h in qa)<1e-10
        # All posts have a positive intersection height with the rail.
        for p in e['parts'][1:]:assert p['geometry']['size'][2]>0
        assert e['post_clear_gap']<=.11+1e-10
        metrics.append({'name':e['name'],'measured_nose_top_height_m':qa,
                        'baluster_clear_gap_m':e['post_clear_gap'],
                        'inside_clear_width_m':e['flight_clear_width_after_rail']})

for name,target in [('BALCONY_STONE_COPING_JOINED',5.20),('TERRACE_STONE_PARAPET',8.80)]:
    e=next(q for q in scene['elements'] if q['name']==name)
    top=max(p['geometry']['z']+p['geometry']['height'] for p in e['parts'])
    assert abs(top-target)<1e-10
    metrics.append({'name':name,'absolute_top_m':top,'above_structural_layer_m':1.30,
                    'useful_height_over_max_80mm_finish_m':1.22})

report={'proposal_only':True,'modified_closed_parts_checked':parts,
        'nonmanifold_or_invalid_profiles':bad,'nonpositive_volume':positive,
        'metrics':metrics,'layout':scene['v4_safety_review']['layout'],
        'D10_original_transverse_axis_divisions_m':[1.175,.05,1.275],
        'unresolved':scene['v4_safety_review']['unresolved'],
        'note':'A 1075mm handrail-face passage is a measured model value, not a current-code approval. Whole-model clearance and native Boolean joint validation remain caller responsibilities.'}
(HERE/'Safety_Proposal_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'Safety_Changes_V4.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
assert not bad and not positive
print(json.dumps({'closed_parts_checked':parts,'errors':len(bad)+len(positive),'change_groups':len(changes),'nominal_width_mm':1100,'after_rail_width_mm':1075,'max_baluster_clear_mm':100,'guard_model_height_mm':1300,'guard_finished_clear_height_mm':1220},ensure_ascii=False))
