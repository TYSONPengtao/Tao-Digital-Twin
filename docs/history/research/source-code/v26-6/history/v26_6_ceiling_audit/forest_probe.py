from pathlib import Path
import bpy,json,numpy as np
P=Path('D:/AJAVIS01/RHINO7.12/PLUGINS/BLENDER/RUNING/5.1/datafiles/studiolights/world/forest.exr');im=bpy.data.images.load(str(P),check_existing=True);w,h=im.size;px=np.array(im.pixels[:],dtype=np.float64).reshape(h,w,4)[:,:,:3];v=(np.arange(h)+.5)/h;z=-np.cos(v*np.pi);omega=np.sin(v*np.pi);out={}
for name,s in [('down',-1),('up',1)]:
 wt=omega*np.maximum(s*z,0);rgb=(px*wt[:,None,None]).sum((0,1))/(wt.sum()*w);out[name]={'linear_hemisphere_irradiance':rgb.tolist(),'rgb_normalized_to_max1':(rgb/rgb.max()).tolist()}
Path(__file__).with_name('Forest_Hemisphere_Irradiance.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
