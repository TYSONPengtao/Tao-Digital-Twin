from pathlib import Path
import bpy,json,hashlib,numpy as np
D=Path('D:/AJAVIS01/RHINO7.12/PLUGINS/BLENDER/RUNING/5.1/datafiles/studiolights/world')
result={}
for nm in ['forest.exr','studio.exr']:
 P=D/nm
 with P.open('rb')as f:hsh=hashlib.file_digest(f,'sha256').hexdigest()
 im=bpy.data.images.load(str(P),check_existing=True);w,h=im.size
 px=np.array(im.pixels[:],dtype=np.float64).reshape(h,w,4)[:,:,:3]
 # Blender image rows start at bottom. Equirectangular low rows look down.
 v=(np.arange(h)+.5)/h;z=-np.cos(v*np.pi);omega=np.sin(v*np.pi)
 out={'path':str(P),'sha256':hsh,'resolution':[w,h]}
 for name,s in [('down',-1),('up',1)]:
  wt=omega*np.maximum(s*z,0)
  rgb=(px*wt[:,None,None]).sum((0,1))/(wt.sum()*w)
  normalized=rgb/rgb.max()
  out[name]={'linear_hemisphere_irradiance':rgb.tolist(),'rgb_normalized_to_max1':normalized.tolist(),'maximum_relative_channel_spread':float((rgb.max()-rgb.min())/rgb.mean())}
 result[nm]=out
fore=result['forest.exr']['down'];studio=result['studio.exr']['down']
result['comparison']={'studio_down_neutral_within_1_percent':studio['maximum_relative_channel_spread']<.01,'forest_down_spread':fore['maximum_relative_channel_spread'],'studio_down_spread':studio['maximum_relative_channel_spread'],'method':'Cosine weighted equirectangular hemisphere integration in linear scene RGB from native Blender image float pixels; not a model render or geometric change.'}
P=Path(__file__).with_name('Forest_Studio_Hemisphere_Comparison.json');P.write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result['comparison']),flush=True)
print('STUDIO_DOWN',result['studio.exr']['down'],flush=True)
