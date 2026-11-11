import sys
from pathlib import Path
W=Path(__file__).resolve().parent.parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import manifold3d as mf
print(mf.Manifold.slice.__doc__);print(mf.CrossSection.to_polygons.__doc__)
