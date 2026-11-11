"""Reversible V4 safety geometry proposals; does not write files.

Usage: changes = apply(scene, layout={...})
The scene is modified in memory.  This is a construction-review proposal,
not a structural design, a measured existing-condition record or approval.
All dimensions are metres.  Original V3 files must be retained separately.
"""
import math

SOURCE = 'D02 section 6.5; D03/D04 floor plans; D10/D11 stair drawings; V4 construction proposal'


def _part(g, material):
    return {'geometry': g, 'material': material}


def _box(x, y, z, w, d, h):
    return {'type': 'box', 'origin': [x, y, z], 'size': [w, d, h]}


def _beam(a, b, w=.05, d=.05):
    """Closed rectangular beam with its section normal to the centreline."""
    dv = [b[i] - a[i] for i in range(3)]
    length = math.sqrt(sum(v*v for v in dv))
    if length <= 1e-10:
        raise ValueError('zero length beam')
    unit = [v/length for v in dv]
    horizontal = math.hypot(unit[0], unit[1])
    side = [-unit[1]/horizontal, unit[0]/horizontal, 0] if horizontal > 1e-8 else [1, 0, 0]
    up = [unit[1]*side[2]-unit[2]*side[1], unit[2]*side[0]-unit[0]*side[2], unit[0]*side[1]-unit[1]*side[0]]
    profile = [[a[i] + sw*w/2*side[i] + su*d/2*up[i] for i in range(3)]
               for sw, su in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return {'type': 'prism', 'profile': profile, 'vector': dv}


def _element(name, parts, layer='41_RAILING', **metadata):
    return {'name': name, 'parts': parts, 'layer': layer, 'family': 'ARCH_MODEL',
            'source': SOURCE, 'confidence': 'MEDIUM',
            'status': 'CONSTRUCTION_REVIEW_PROPOSAL', **metadata}


def apply(S, layout=None):
    """Apply suggestions and return a reviewable list of changes.

    layout can set lower_y, width, well, run_x_low, run_x_high,
    landing_x, landing_width.  Default is the reviewed construction proposal:
    two 1100 slabs, a 20 well, between Y7.440 and 9.660 after beam and
    15 mm finish clearances. D10 marks 1175 / 50 / 1275 between axes,
    not two clear 1175 flights plus a 90 well. This is NOT a code or
    clearance approval. Nominal slab widths and useful clear widths differ.
    """
    options = {'lower_y': 7.44, 'width': 1.100, 'well': .020,
               'run_x_low': 5.2, 'run_x_high': 7.8,
               'landing_x': 3.9, 'landing_width': 1.3}
    if layout:
        options.update(layout)
    lower_y = float(options['lower_y'])
    width = float(options['width'])
    well = float(options['well'])
    upper_y = lower_y+width+well
    xlow = float(options['run_x_low'])
    xhigh = float(options['run_x_high'])
    run = xhigh-xlow
    tread = run/10
    land_x = float(options['landing_x'])
    land_w = float(options['landing_width'])
    land_d = 2*width+well
    if min(width, well, tread, land_w) <= 0:
        raise ValueError('invalid stair layout')
    changes = []
    elements = S['elements']
    by_name = {e['name']:e for e in elements}

    # Use the top of the finished guard, not its bounding box plus floor base.
    e = by_name.get('BALCONY_STONE_JOINED')
    cap = by_name.get('BALCONY_STONE_COPING_JOINED')
    if e and cap:
        for p in e['parts']:
            g=p['geometry']
            if g['type']=='prism_holes':g['height']=1.17
        for p in cap['parts']:
            g=p['geometry']
            if g['type']=='prism_holes':g['z']=5.07;g['height']=.13
        for q in [e,cap]:
            q.update(status='CONSTRUCTION_REVIEW_PROPOSAL',proposal_guard_height=1.3,
                     useful_guard_height_at_highest_finish=1.22,finish_raise_allowance=.08,
                     previous_guard_height=1.05,source=SOURCE,
                     structural_review='Raised masonry/stone guard changes dead load; verify support and fixings separately')
        changes.append({'id':'S01','part':'F2 balcony guard','before_m':1.05,'after_m':1.3,
                        'after_useful_height_over_highest_finish_m':1.22,'finish_raise_allowance_m':.08,'source':'D02 6.5',
                        'note':'Stone body and coping changed; V3 existing-condition record remains separate'})
    terrace = by_name.get('TERRACE_STONE_PARAPET')
    if terrace:
        for p in terrace['parts']:
            if p['geometry']['type']=='prism_holes':p['geometry']['height']=1.3
        terrace.update(status='CONSTRUCTION_REVIEW_PROPOSAL',proposal_guard_height=1.3,
                       useful_guard_height_at_highest_finish=1.22,finish_raise_allowance=.08,
                       previous_guard_height=.9,source=SOURCE,
                       structural_review='Raised masonry/stone guard changes dead load; verify support and fixings separately')
        changes.append({'id':'S02','part':'F3 terrace guard','before_m':.9,'after_m':1.3,
                        'after_useful_height_over_highest_finish_m':1.22,'finish_raise_allowance_m':.08,'source':'D02 6.5'})

    # Replace the four sloping rails and 44 fixed-height isolated balusters.
    S['elements']=[e for e in elements if not e['name'].startswith(('STAIR_HANDRAIL_','STAIR_BALUSTER_','STAIR_V4_'))]
    elements=S['elements']
    by_name={e['name']:e for e in elements}
    for storey,(floor,mid,top) in enumerate([(0,1.95,3.9),(3.9,5.7,7.5)],1):
        rise=(top-floor)/22
        slope=rise/tread
        vertical_waist=.14*math.sqrt(1+slope*slope)
        rail_vertical_half=.025*math.sqrt(1+slope*slope)
        end_rail_centres=[]
        for flight in [0,1]:
            bz=floor if flight==0 else mid
            final=mid if flight==0 else top
            direction=-1 if flight==0 else 1
            xs=xhigh if flight==0 else xlow
            xe=xlow if flight==0 else xhigh
            yy=lower_y if flight==0 else upper_y
            end_thickness=.14 if flight==0 else .13
            # Parallel waist underside is a true 140 mm offset from the
            # inclined line through the re-entrant corners of the steps.
            # Continue that waist under the terminal landing.  It reaches
            # the platform/slab underside before a short horizontal tongue.
            merge=(rise+vertical_waist-end_thickness)/slope
            tongue=max(.35,merge+.025)
            profile=[[xs,yy,bz-vertical_waist],[xs,yy,bz+rise]]
            for k in range(1,11):
                xx=xs+direction*k*tread
                profile.append([xx,yy,bz+k*rise])
                if k<10:profile.append([xx,yy,bz+(k+1)*rise])
            profile.extend([[xe,yy,final],
                            [xe+direction*tongue,yy,final],
                            [xe+direction*tongue,yy,final-end_thickness],
                            [xe+direction*merge,yy,final-end_thickness]])
            name=f'STAIR_F{storey}_FLIGHT{flight+1}'
            e=by_name[name]
            old_rises=e.get('rises',[])
            e['parts']=[_part({'type':'prism','profile':profile,'vector':[0,width,0]},'M_Concrete')]
            e.update(rises=[rise]*11,tread=tread,width=width,slab=.14,
                     slab_thickness_direction='NORMAL_TO_INCLINED_WAIST',vertical_waist_thickness=vertical_waist,
                     finish_added_as_geometry=False,
                     z_from=bz,z_to=final,status='CONSTRUCTION_REVIEW_PROPOSAL',source=SOURCE,
                     terminal_tongue_length=tongue,terminal_undermerge_length=merge,
                     terminal_joint='Same-material monolithic cast-in-place proposal; tongue shares volume with platform/slab',
                     reinforcement='Not inferred or added; connection reinforcement requires design review')
            # Both rails protect the central stairwell edge.  Upper-flight
            # railing previously followed the outer/back-wall side.
            rail_y=lower_y+width if flight==0 else upper_y
            zc0=bz+rise+.9-rail_vertical_half
            zc1=final+.9-rail_vertical_half
            a=[xs,rail_y,zc0];b=[xe,rail_y,zc1]
            # Extend beyond both endpoint posts so a perpendicular end cap
            # cannot truncate the top surface at the endpoint nose plane.
            ra=[xs-direction*.05,rail_y,zc0-slope*.05]
            rb=[xe+direction*.05,rail_y,zc1+slope*.05]
            parts=[_part(_beam(ra,rb,.05,.05),'M_Wood')]
            # One post every half tread; 130 pitch and 30 post gives 100 clear.
            # Posts are individually fitted to the lower face of the rail.
            for k in range(21):
                dist=run*k/20
                xx=xs+direction*dist
                index=min(11,int(math.floor((dist+1e-9)/tread))+1)
                base=bz+index*rise-.01
                centre=zc0+(zc1-zc0)*dist/run
                post_top=centre-rail_vertical_half+.003
                parts.append(_part(_box(xx-.015,rail_y-.015,base,.03,.03,post_top-base),'M_Wood'))
            elements.append(_element(f'STAIR_V4_RAIL_F{storey}_{flight+1}',parts,
                            actual_nose_handrail_top=.9,post_pitch=tread/2,post_width=.03,
                            post_clear_gap=tread/2-.03,flight_clear_width_before_rail=width,
                            flight_clear_width_after_rail=width-.025,
                            statement='Nose-line top height; closed rail/end-post contact; hardware and strength require review'))
            end_rail_centres.append((a,b))
            changes.append({'id':f'S03_F{storey}_{flight+1}','part':name,
                            'before_rises_m':old_rises,'after_uniform_rise_m':rise,'rise_count':11,
                            'tread_m':tread,'nominal_flight_width_m':width,
                            'normal_waist_thickness_m':.14,'vertical_waist_m':vertical_waist,
                            'bearing_tongue_m':tongue,'underside_merge_m':merge,
                            'handrail_top_above_nose_m':.9,'baluster_clear_m':tread/2-.03,
                            'source':'D10/D11 longitudinal dimensions; D02 6.5',
                            'note':'Uniform heights and waist/tongue are proposed geometry; retain original source rise labels in evidence'})

        landing=by_name[f'STAIR_LANDING_F{storey}']
        landing['parts']=[_part(_box(land_x,lower_y,mid-.14,land_w,land_d,.14),'M_Concrete')]
        landing.update(status='CONSTRUCTION_REVIEW_PROPOSAL',source=SOURCE,
                       terminal_joint='Monolithic shared-volume terminal tongues; no detached riser cover')
        # Fit a continuous return and end support over the narrow central
        # well at the turning platform.  Its height rises smoothly to the
        # first nose of the upper flight rather than a detached vertical cap.
        low_end=end_rail_centres[0][1]
        high_start=end_rail_centres[1][0]
        # A horizontal return has a different vertical half-depth than the
        # sloping rail. Keep its top at least 900 over the landing as well.
        low_end=[low_end[0],low_end[1],max(low_end[2],mid+.9-.025)]
        xreturn=xlow-.12
        pts=[low_end,[xreturn,low_end[1],low_end[2]],
             [xreturn,high_start[1],high_start[2]],high_start]
        turn_parts=[_part(_beam(a,b),'M_Wood') for a,b in zip(pts[:-1],pts[1:])]
        turn_parts.append(_part(_box(xreturn-.035,(low_end[1]+high_start[1])/2-(well+.05)/2,
                                     mid-.01,.07,well+.05,1.11),'M_Wood'))
        elements.append(_element(f'STAIR_V4_RETURN_F{storey}',turn_parts,
                                 guard_min_top_above_platform=.9,central_well_width=well,
                                 node='Timber return and full-height end support proposed, not a measured historical detail'))

        # The front edge of a half-level landing is open above the hall.
        guard_y=lower_y+.025
        gx0=land_x+.16;gx1=xlow-.07
        if gx1>gx0:
            parts=[_part(_beam([gx0,guard_y,mid+1.075],[gx1,guard_y,mid+1.075]),'M_Wood')]
            n=max(1,math.ceil((gx1-gx0)/.13))
            for k in range(n+1):
                xx=gx0+(gx1-gx0)*k/n
                parts.append(_part(_box(xx-.015,guard_y-.015,mid-.01,.03,.03,1.065),'M_Wood'))
            elements.append(_element(f'STAIR_V4_PLATFORM_FRONT_F{storey}',parts,
                                     guard_top_above_platform=1.1,post_clear_gap=(gx1-gx0)/n-.03,
                                     source=SOURCE+'; previously unprotected open half-level edge'))
        # End support closes the central well at each storey floor.
        ymiddle=(lower_y+width+upper_y)/2
        for label,z in [('BASE',floor),('TOP',top)]:
            # Owner convention avoids an identical shared F2 floor newel.
            if storey==2 and label=='BASE':continue
            elements.append(_element(f'STAIR_V4_FLOOR_END_{storey}_{label}',
                                     [_part(_box(xhigh-.03,ymiddle-(well+.04)/2,z-.01,.06,well+.04,1.11),'M_Wood')],
                                     guard_top_above_floor=1.1,node='Closed stairwell end support proposal'))

    # Door leaf/frame position changes are paired with a wall opening edit by
    # the junction module; preserve the door count and original door type.
    for floor,z in [(2,3.9),(3,7.5)]:
        name=f'DOOR_BACKROOM_F{floor}_R'
        e=by_name.get(name)
        if e:
            previous=e.get('origin')
            e.update(name=f'DOOR_BATH_F{floor}_R',origin=[10.8,7.65,z],angle=math.pi/2,
                     source=f'D{3 if floor==2 else 4:02d} right bathroom/wardrobe partition M0821; longitudinal placement mirrored from left bathroom',
                     confidence='MEDIUM',status='CONSTRUCTION_REVIEW_PROPOSAL',
                     previous_name=name,previous_origin=previous,
                     wall_opening_edit_required={'close':{'axis':'Y','coordinate':7.3,'range':[11.9,12.7]},
                                                 'open':{'axis':'X','coordinate':10.8,'range':[7.65,8.45],'bottom':z,'height':2.1}},
                     dimensional_note='800 is scheduled rough opening; 45 mm side frames imply approximate 710 mm frame-inside passage, leaf/hardware not measured')
            changes.append({'id':f'S04_F{floor}','part':e['name'],'before_origin':previous,
                            'after_origin':e['origin'],'opening_width_m':.8,
                            'source':f'D{3 if floor==2 else 4:02d} floor plan',
                            'note':'Coordinate proposal requires paired wall repair; exact jamb offsets not dimensioned in source'})

    review={'layout':options,'D10_transverse_annotation_m':[1.175,.05,1.275],
            'D10_transverse_annotation_kind':'Axis divisions; not asserted to be finished clear flight widths',
            'source_axis_separation_m':2.5,
            'stair_finish_added_as_geometry':False,'central_stairwell_width_m':.020,
            'actual_transverse_layout_requires_coordination':True,
            'minimum_post_clearance_m':tread/2-.03,
            'width_measurement_note':'Report finished wall/beam-face to inner handrail face; nominal slab width alone is insufficient',
            'unresolved':['Source transverse divisions versus finished width and beam encroachment',
                          'First-storey uniform 3.9/22=177.273 mm rise needs current-code review',
                          'Raised solid guards require load/support/fixing review',
                          'Tongue geometry shares material with landing but is not a reinforcement/anchorage design',
                          'Bathroom door rough openings versus useful clear passage'],
            'change_register':changes}
    S['v4_safety_review']=review
    return changes
