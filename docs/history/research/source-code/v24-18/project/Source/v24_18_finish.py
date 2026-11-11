"""Metre-based, shared exterior finish; no geometric offset skin."""
import bpy,numpy as np,math
from mathutils import Vector
BRICK='M_V24_18_Continuous_Blue_Brick';DARK='M_V24_18_Continuous_Dark_Courses';RUBBLE='M_V24_18_Continuous_Rubble'
def materials(route):
 L=route['length_m'];out={}
 for n,src,kind in [(BRICK,'M_V19_Perimeter_Brick','brick'),(DARK,'M_V18_Storage_Dark_Courses','stone'),(RUBBLE,'M_V18_Storage_Rubble','rubble')]:
  old=bpy.data.materials[src];m=bpy.data.materials.new(n);m.use_nodes=True;m.use_fake_user=True;nodes=m.node_tree.nodes;links=m.node_tree.links;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.94;bs.inputs['Specular IOR Level'].default_value=.18;output=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs['BSDF'],output.inputs['Surface']);uv=nodes.new('ShaderNodeTexCoord')
  # Reuse the embedded as-built colour/height photographs with continuous
  # mirrored sampling. Straight brick/coursed mortar is generated in metres.
  mapn=nodes.new('ShaderNodeVectorMath');mapn.operation='MULTIPLY';mapn.inputs[1].default_value=(2*max(1,round(L/5.2))/L,1/1.95,1);links.new(uv.outputs['UV'],mapn.inputs[0]);sep=nodes.new('ShaderNodeSeparateXYZ');links.new(mapn.outputs[0],sep.inputs[0]);comb=nodes.new('ShaderNodeCombineXYZ')
  for ax in ['X','Y']:
   pp=nodes.new('ShaderNodeMath');pp.operation='PINGPONG';pp.inputs[1].default_value=1;links.new(sep.outputs[ax],pp.inputs[0]);links.new(pp.outputs[0],comb.inputs[ax])
  images=[nd.image for nd in old.node_tree.nodes if nd.type=='TEX_IMAGE'and nd.image];color=nodes.new('ShaderNodeTexImage');color.image=images[0];color.interpolation='Linear';color.extension='EXTEND';links.new(comb.outputs[0],color.inputs['Vector']);bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.001;links.new(bump.outputs[0],bs.inputs['Normal'])
  if kind!='rubble':
   scaled=nodes.new('ShaderNodeVectorMath');scaled.operation='MULTIPLY';w=.24 if kind=='brick'else .54;scaled.inputs[1].default_value=(round(L/w)*w/L,1,1);links.new(uv.outputs['UV'],scaled.inputs[0]);tile=nodes.new('ShaderNodeTexBrick');tile.offset=.5;tile.offset_frequency=2;tile.inputs['Scale'].default_value=1;tile.inputs['Brick Width'].default_value=w;tile.inputs['Row Height'].default_value=.06 if kind=='brick'else .335;tile.inputs['Mortar Size'].default_value=.003 if kind=='brick'else .006;tile.inputs['Mortar Smooth'].default_value=.005;tile.inputs['Bias'].default_value=0
   tile.inputs['Color1'].default_value=(.145,.165,.18,1)if kind=='brick'else(.13,.15,.17,1);tile.inputs['Color2'].default_value=(.22,.235,.245,1)if kind=='brick'else(.23,.25,.27,1);tile.inputs['Mortar'].default_value=(.43,.44,.41,1)if kind=='brick'else(.37,.38,.36,1);links.new(scaled.outputs[0],tile.inputs['Vector']);mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.18;links.new(tile.outputs['Color'],mix.inputs[1]);links.new(color.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color']);links.new(tile.outputs['Fac'],bump.inputs['Height']);bump.invert=True
  else:
   links.new(color.outputs['Color'],bs.inputs['Base Color']);height=nodes.new('ShaderNodeTexImage');height.image=images[1];height.extension='EXTEND';height.interpolation='Linear';links.new(comb.outputs[0],height.inputs['Vector']);links.new(height.outputs['Color'],bump.inputs['Height']);bump.inputs['Distance'].default_value=.002
  out[n]=m
 return out
def subdivide(v,f,cuts):
 V=v.tolist();F=f.tolist()
 for cut in cuts:
  cache={};new=[]
  def crossing(a,b):
   if abs(V[a][2]-cut)<1e-9:return a
   if abs(V[b][2]-cut)<1e-9:return b
   key=tuple(sorted([a,b]))
   if key not in cache:
    A=np.array(V[a]);B=np.array(V[b]);p=A+(B-A)*(cut-A[2])/(B[2]-A[2]);p[2]=cut;cache[key]=len(V);V.append(p.tolist())
   return cache[key]
  for ids in F:
   z=[V[i][2]for i in ids]
   if min(z)>=cut-1e-9 or max(z)<=cut+1e-9:new.append(ids);continue
   for side in [0,1]:
    p=[]
    for a,b in zip(ids,ids[1:]+ids[:1]):
     aa=V[a][2]<=cut if side==0 else V[a][2]>=cut;bb=V[b][2]<=cut if side==0 else V[b][2]>=cut
     if aa and bb:p.append(b)
     elif aa:p.append(crossing(a,b))
     elif bb:p.extend([crossing(a,b),b])
    p=[x for j,x in enumerate(p)if x!=p[j-1]]
    for j in range(1,len(p)-1):
     t=[p[0],p[j],p[j+1]]
     if len(set(t))==3:new.append(t)
  F=new
 return np.array(V),np.array(F)
class ArcMap:
 def __init__(self,route):
  self.p=np.array(route['xy']);self.a=self.p[:-1];self.d=np.diff(self.p,axis=0);self.l=np.linalg.norm(self.d,axis=1);good=self.l>1e-7;self.a=self.a[good];self.d=self.d[good];self.l=self.l[good];self.u=self.d/self.l[:,None];self.n=np.c_[self.u[:,1],-self.u[:,0]];self.s=np.r_[0,np.cumsum(self.l)[:-1]];self.planes={}
 def triangle(self,t):
  normal=np.cross(t[1]-t[0],t[2]-t[0]);nn=np.linalg.norm(normal)
  if nn<1e-12:return t[:,[0,2]]
  normal/=nn
  if abs(normal[2])>.85:return t[:,[0,1]]
  q=t[:,:2].mean(0);nh=normal[:2]/max(np.linalg.norm(normal[:2]),1e-15);key=(*np.round(nh,4),round(float(q@nh),3))
  if key not in self.planes:
   r=q-self.a;proj=(r*self.u).sum(1);closest=self.a+self.u*np.clip(proj,0,self.l)[:,None];dist=np.linalg.norm(closest-q,axis=1);align=self.n@nh;score=dist+np.maximum(0,.70-align)*5;i=int(np.argmin(score));tangent=np.array([-nh[1],nh[0]])
   if tangent@self.u[i]<0:tangent=-tangent
   offset=self.s[i]+float((q-self.a[i])@self.u[i])-float(q@tangent);self.planes[key]=(tangent,offset)
  tangent,offset=self.planes[key];return np.c_[t[:,:2]@tangent+offset,t[:,2]]
def apply_exterior(o,route,mats,mapper=None):
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles]);old_area=float(np.linalg.norm(np.cross(v[f][:,1]-v[f][:,0],v[f][:,2]-v[f][:,0]),axis=1).sum()/2);v,f=subdivide(v,f,[-1.05,-.38]);tri=v[f];area=float(np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1).sum()/2);old=me;iv=o.matrix_world.inverted();me=bpy.data.meshes.new(o.name+'_Continuous_Metre_Finish');me.from_pydata([iv@Vector(p)for p in v],[],f);me.update();o.data=me
 for n in [RUBBLE,DARK,BRICK]:me.materials.append(mats[n])
 uv=me.uv_layers.new(name='V24_18_ArcLength_Metres');mapper=mapper or ArcMap(route)
 for i,face in enumerate(me.polygons):
  z=tri[i,:,2].mean();face.material_index=0 if z<-1.05-1e-7 else 1 if z<-.38-1e-7 else 2;coords=mapper.triangle(tri[i])
  for li,q in zip(face.loop_indices,coords):uv.data[li].uv=q
 if not old.users:bpy.data.meshes.remove(old)
 return {'object':o.name,'original_surface_area_m2':old_area,'final_surface_area_m2':area,'absolute_area_change_m2':abs(area-old_area),'material_datum_z':[-1.05,-.38],'uv_layer':'V24_18_ArcLength_Metres','geometry_split_only':True}
