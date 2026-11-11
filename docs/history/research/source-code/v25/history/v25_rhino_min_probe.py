from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v25_rhino_common import *
core=start()
try:
 b=bridge();f=Rhino.FileIO.File3dm();m=Rhino.DocObjects.Material();m.Name='V25_Test';m.ToPhysicallyBased();m.PhysicallyBased.BaseColor=Rhino.Display.Color4f(.8,.6,.4,1.);m.PhysicallyBased.Roughness=.8;m.PhysicallyBased.SynchronizeLegacyMaterial();mi=f.Materials.Add(m);l=Rhino.DocObjects.Layer();l.Name='Test';li=f.Layers.Add(l)
 vi=Rhino.DocObjects.ViewInfo();vi.Name='V25_Test';vp=vi.Viewport
 data={'bridge_compiled':bool(b),'material_add_index':mi,'layer_add_index':li,'ViewInfo':[s for s in dir(vi)if not s.startswith('_')],'ViewportInfo':[s for s in dir(vp)if not s.startswith('_')],'embedded_type':str(type(f.EmbeddedFiles)),'material_PBR_texture_types':[str(k)for k in System.Enum.GetValues(Rhino.DocObjects.TextureType)]}
 (W/'v25/Rhino_Builder_API.json').write_text(json.dumps(data,indent=2));print('RHINO_BUILDER_API_OK',mi,li,flush=True)
finally:core.Dispose()
