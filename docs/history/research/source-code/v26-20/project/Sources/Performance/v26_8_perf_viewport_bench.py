"""Measured native window redraws; no change to the user's existing Blender process."""
import bpy, time, json, sys, traceback, statistics, math, importlib.util, types
from pathlib import Path
from mathutils import Vector

W=Path(__file__).parent
D=W/'v26_8_perf'
D.mkdir(exist_ok=True)
result={'method':'Native DRAW_WIN_SWAP timing with moving view, shader warmup excluded',
        'conditions':'Separate 1920x1080 full-area Blender test window; existing applications continue running',
        'blender':bpy.app.version_string,'measurements':[]}
spec=importlib.util.spec_from_file_location('fast_display',W/'v26_8_fast_display.py')
display=importlib.util.module_from_spec(spec);spec.loader.exec_module(display)


def run():
    try:
        win=bpy.context.window_manager.windows[0]
        area=max((a for a in win.screen.areas if a.type=='VIEW_3D'),key=lambda a:a.width*a.height)
        region=next(r for r in area.regions if r.type=='WINDOW')
        with bpy.context.temp_override(window=win,area=area,region=region):
            bpy.ops.screen.screen_full_area(use_hide_panels=False)
        area=max((a for a in win.screen.areas if a.type=='VIEW_3D'),key=lambda a:a.width*a.height)
        region=next(r for r in area.regions if r.type=='WINDOW')
        sp=area.spaces.active
        bpy.context.scene.frame_set(40)
        views=[('court',(6.5,-6.,1.1),(6.5,2.,1.1)),
               ('stairs',(7.6,9.12,2.6),(5.3,8.5,1.6))]
        for mode in ['baseline','fast']:
            if mode=='fast':result['settings']=display.apply()
            for label,eye,at in views:
                eye=Vector(eye);at=Vector(at);rv=sp.region_3d
                rv.view_perspective='PERSP';rv.view_rotation=(at-eye).to_track_quat('-Z','Y')
                rv.view_distance=(at-eye).length;rv.view_location=at;sp.lens=24.
                sp.overlay.show_overlays=False
                with bpy.context.temp_override(window=win,area=area,region=region):
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=5)
                    spans=[]
                    for i in range(16):
                        rv.view_location=at+Vector((.015*math.sin(i*.55),0,0))
                        t=time.perf_counter()
                        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=1)
                        spans.append(time.perf_counter()-t)
                    row={'profile':mode,'view':label,'area_pixels':[area.width,area.height],
                         'frames':len(spans),'median_ms':statistics.median(spans)*1000,
                         'p95_ms':sorted(spans)[int(.95*(len(spans)-1))]*1000,
                         'effective_fps':len(spans)/sum(spans)}
                    result['measurements'].append(row)
                    print('VIEWPORT_BENCH',json.dumps(row),flush=True)
                    sc=bpy.context.scene;sc.render.resolution_x=1000;sc.render.resolution_y=700
                    sc.render.resolution_percentage=100
                    sc.render.filepath=str(D/f'{mode}_{label}.png')
                    sc.render.image_settings.file_format='PNG'
                    bpy.ops.render.opengl(write_still=True,view_context=True)
        result['viewport_status']='PASS'
        for name,code in [('architecture_roam_physics',bpy.data.texts['V24_21_碰撞控制.py'].as_string()),
                          ('architecture_roam_measure',bpy.data.texts['V24_25_测量工具.py'].as_string()),
                          ('architecture_roam_controller',(D/'roam_controller_fast.py').read_text('utf8'))]:
            mod=types.ModuleType(name);sys.modules[name]=mod
            exec(compile(code,name,'exec'),mod.__dict__)
        ctrl=sys.modules['architecture_roam_controller'];ctrl.register()
        with bpy.context.temp_override(window=win,area=area,region=region):
            started=bpy.ops.arch_roam.start('INVOKE_DEFAULT')
        if 'RUNNING_MODAL'not in started:raise RuntimeError(str(started))
        result['controller_tests']=[]
        bpy.app.timers.register(controller_test,first_interval=1.)
        return None
    except Exception:
        result['status']='ERROR';result['error']=traceback.format_exc()
        print(result['error'],flush=True)
    (D/'Viewport_Benchmark.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
    bpy.ops.wm.quit_blender()
    return None


phase=0
previous_counts=None
origin=None


def controller_test():
    global phase,previous_counts,origin
    try:
        ctrl=sys.modules['architecture_roam_controller'];r=ctrl._running
        if r is None:raise RuntimeError('Native modal tour did not stay running')
        if phase==0:
            previous_counts=r.perf_counts.copy();phase=1
            return .8
        if phase==1:
            skipped=r.perf_counts['idle_skips']-previous_counts['idle_skips']
            updates=r.perf_counts['simulation_updates']-previous_counts['simulation_updates']
            result['controller_tests'].append({'check':'Stationary avatar skips repeated pose, physics and redraw updates',
                                               'pass':skipped>8 and updates<=1,'idle_skips':skipped,'updates':updates})
            origin=r.walker.p.copy();r.keys={'W'};r._focus_active=True;phase=2
            return .8
        if phase==2:
            distance=(r.walker.p-origin).length;r.keys.clear()
            result['controller_tests'].append({'check':'Native timer resumes real walking on movement input',
                                               'pass':distance>.4,'actual_distance_m':distance})
            # Directly exercise the native operator's focus-loss event branch.
            ev=types.SimpleNamespace(type='WINDOW_DEACTIVATE',value='PRESS',ctrl=False)
            r.modal(bpy.context,ev)
            previous_counts=r.perf_counts.copy();phase=3
            return .4
        if phase==3:
            skipped=r.perf_counts['focus_skips']-previous_counts['focus_skips']
            result['controller_tests'].append({'check':'Focus loss pauses simulation and repeated drawing',
                                               'pass':skipped>4,'focus_skips':skipped})
            r.finish(bpy.context)
            result['status']='PASS'if all(c['pass']for c in result['controller_tests'])else'FAIL'
            (D/'Viewport_Benchmark.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
            print('CONTROLLER_QA',json.dumps(result['controller_tests']),flush=True)
    except Exception:
        result['status']='ERROR';result['error']=traceback.format_exc()
        (D/'Viewport_Benchmark.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
        print(result['error'],flush=True)
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(run,first_interval=2.)
