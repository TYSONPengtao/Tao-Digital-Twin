import ctypes as C, os, json
from pathlib import Path
class Ref(C.Structure):_fields_=[('ptr',C.c_void_p)]
class Point(C.Structure):_fields_=[('x',C.c_double),('y',C.c_double),('z',C.c_double)]
class Bounds(C.Structure):_fields_=[('min_point',Point),('max_point',Point)]
class Transform(C.Structure):_fields_=[('values',C.c_double*16)]
class Color(C.Structure):_fields_=[('r',C.c_ubyte),('g',C.c_ubyte),('b',C.c_ubyte),('a',C.c_ubyte)]
PRef=C.POINTER(Ref);SZ=C.c_size_t
SDK=Path(r'D:\AJAVIS01\ContextCapture\PLUGINS\SU19\RUNING')
_dir=os.add_dll_directory(str(SDK));dll=C.CDLL(str(SDK/'SketchUpAPI.dll'))
def bind(n,args,ret=C.c_int):
 fn=getattr(dll,n);fn.argtypes=args;fn.restype=ret;globals()[n]=fn;return fn
for n,args in {
 'SUInitialize':[], 'SUTerminate':[], 'SUModelCreate':[PRef], 'SUModelCreateFromFile':[PRef,C.c_char_p], 'SUModelRelease':[PRef], 'SUModelSaveToFile':[Ref,C.c_char_p],
 'SUModelGetEntities':[Ref,PRef],'SUModelSetName':[Ref,C.c_char_p],'SUModelSetDescription':[Ref,C.c_char_p],
 'SUGroupCreate':[PRef],'SUGroupSetName':[Ref,C.c_char_p],'SUGroupGetEntities':[Ref,PRef],'SUEntitiesAddGroup':[Ref,Ref],'SUGroupSetTransform':[Ref,C.POINTER(Transform)],
 'SUComponentDefinitionCreate':[PRef],'SUComponentDefinitionSetName':[Ref,C.c_char_p],'SUComponentDefinitionSetDescription':[Ref,C.c_char_p],'SUComponentDefinitionGetEntities':[Ref,PRef],
 'SUModelAddComponentDefinitions':[Ref,SZ,PRef],'SUComponentDefinitionCreateInstance':[Ref,PRef],'SUComponentInstanceSetName':[Ref,C.c_char_p], 'SUComponentInstanceSetTransform':[Ref,C.POINTER(Transform)],'SUEntitiesAddInstance':[Ref,Ref,PRef],
 'SULayerCreate':[PRef],'SULayerSetName':[Ref,C.c_char_p],'SULayerSetVisibility':[Ref,C.c_bool],'SUModelAddLayers':[Ref,SZ,PRef], 'SUDrawingElementSetLayer':[Ref,Ref],'SUDrawingElementSetMaterial':[Ref,Ref],
 'SUMaterialCreate':[PRef],'SUMaterialSetName':[Ref,C.c_char_p],'SUMaterialSetColor':[Ref,C.POINTER(Color)],'SUMaterialSetOpacity':[Ref,C.c_double],'SUMaterialSetUseOpacity':[Ref,C.c_bool],'SUModelAddMaterials':[Ref,SZ,PRef],
 'SUGeometryInputCreate':[PRef],'SUGeometryInputSetVertices':[Ref,SZ,C.POINTER(Point)],'SUGeometryInputAddFace':[Ref,PRef,C.POINTER(SZ)], 'SUGeometryInputRelease':[PRef], 'SULoopInputCreate':[PRef],'SULoopInputAddVertexIndex':[Ref,SZ], 'SUEntitiesFill':[Ref,Ref,C.c_bool],
 'SUEntitiesGetNumFaces':[Ref,C.POINTER(SZ)],'SUEntitiesGetFaces':[Ref,SZ,PRef,C.POINTER(SZ)],'SUFaceSetFrontMaterial':[Ref,Ref],'SUFaceSetBackMaterial':[Ref,Ref],
 'SUEntitiesGetNumGroups':[Ref,C.POINTER(SZ)],'SUEntitiesGetGroups':[Ref,SZ,PRef,C.POINTER(SZ)],'SUEntitiesGetNumInstances':[Ref,C.POINTER(SZ)],'SUEntitiesGetInstances':[Ref,SZ,PRef,C.POINTER(SZ)],'SUEntitiesGetNumEdges':[Ref,C.c_bool,C.POINTER(SZ)],
 'SUComponentInstanceGetDefinition':[Ref,PRef],'SUComponentInstanceComputeVolume':[Ref,C.POINTER(Transform),C.POINTER(C.c_double)],'SUModelGetNumComponentDefinitions':[Ref,C.POINTER(SZ)], 'SUModelGetNumLayers':[Ref,C.POINTER(SZ)],
 }.items():bind(n,args)
for n in ['SUGroupToDrawingElement','SUComponentInstanceToDrawingElement','SUGroupToComponentInstance']:bind(n,[Ref],Ref)
def ck(result,action=''):
 if result!=0:raise RuntimeError(f'{action}: SketchUp API error {result}')
def new(n,*a):
 r=Ref();ck(globals()[n](C.byref(r),*a) if n=='SUModelCreateFromFile' else globals()[n](*a,C.byref(r)),n);return r
def count(n,r,*a):
 v=SZ();ck(globals()[n](r,*a,C.byref(v)),n);return v.value
def fill(ents,verts,faces,material=None):
 geom=new('SUGeometryInputCreate');vs=(Point*len(verts))(*[Point(*[v/0.0254 for v in p]) for p in verts]);ck(SUGeometryInputSetVertices(geom,len(verts),vs),'vertices')
 for f in faces:
  loop=new('SULoopInputCreate')
  for i in f:ck(SULoopInputAddVertexIndex(loop,i),'loop vertex')
  idx=SZ();ck(SUGeometryInputAddFace(geom,C.byref(loop),C.byref(idx)),'add face')
 ck(SUEntitiesFill(ents,geom,True),'fill');ck(SUGeometryInputRelease(C.byref(geom)),'release geometry')
 if material:
  n=count('SUEntitiesGetNumFaces',ents);fs=(Ref*n)();got=SZ();ck(SUEntitiesGetFaces(ents,n,fs,C.byref(got)))
  for f in fs:ck(SUFaceSetFrontMaterial(f,material));ck(SUFaceSetBackMaterial(f,material))
def transform(origin=(0,0,0),angle=0):
 import math
 c=math.cos(angle);s=math.sin(angle);x,y,z=[v/0.0254 for v in origin];return Transform((C.c_double*16)(c,s,0,0,-s,c,0,0,0,0,1,0,x,y,z,1))
def fill_edges(ents,verts):
 bind('SUGeometryInputAddEdge',[Ref,SZ,SZ,C.POINTER(SZ)])
 geom=new('SUGeometryInputCreate');vs=(Point*len(verts))(*[Point(*[v/.0254 for v in p]) for p in verts]);ck(SUGeometryInputSetVertices(geom,len(verts),vs))
 for i in range(len(verts)-1):idx=SZ();ck(SUGeometryInputAddEdge(geom,i,i+1,C.byref(idx)))
 ck(SUEntitiesFill(ents,geom,True));ck(SUGeometryInputRelease(C.byref(geom)))
def group(parent,name,layer=None):
 g=new('SUGroupCreate');ck(SUEntitiesAddGroup(parent,g));ck(SUGroupSetName(g,name.encode('utf-8')));ents=new('SUGroupGetEntities',g)
 if layer:ck(SUDrawingElementSetLayer(SUGroupToDrawingElement(g),layer))
 return g,ents
def readback_door_width(model):
 for n,args in {'SUModelGetComponentDefinitions':[Ref,SZ,PRef,C.POINTER(SZ)],'SUComponentDefinitionGetName':[Ref,PRef],'SUStringCreate':[PRef],'SUStringGetUTF8Length':[Ref,C.POINTER(SZ)],'SUStringGetUTF8':[Ref,SZ,C.c_void_p,C.POINTER(SZ)],'SUStringRelease':[PRef],'SUEntitiesGetBoundingBox':[Ref,C.POINTER(Bounds)]}.items():bind(n,args)
 countdefs=count('SUModelGetNumComponentDefinitions',model);arr=(Ref*countdefs)();got=SZ();ck(SUModelGetComponentDefinitions(model,countdefs,arr,C.byref(got)))
 for d in arr:
  sr=new('SUStringCreate');ck(SUComponentDefinitionGetName(d,C.byref(sr)));l=SZ();ck(SUStringGetUTF8Length(sr,C.byref(l)));buf=C.create_string_buffer(l.value+1);wrote=SZ();ck(SUStringGetUTF8(sr,l.value+1,buf,C.byref(wrote)));name=buf.value.decode();SUStringRelease(C.byref(sr))
  if name=='DOOR_W900_H2100_WOOD':
   bb=Bounds();ck(SUEntitiesGetBoundingBox(new('SUComponentDefinitionGetEntities',d),C.byref(bb)));return (bb.max_point.x-bb.min_point.x)*.0254
 raise ValueError('900mm door definition missing after reopening SKP')
if __name__=='__main__':
 SUInitialize();m=new('SUModelCreate');e=new('SUModelGetEntities',m);g,ge=group(e,'SDK_TEST_CUBE')
 v=[(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)];f=[[3,2,1,0],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]];fill(ge,v,f)
 vol=C.c_double();ck(SUComponentInstanceComputeVolume(SUGroupToComponentInstance(g),None,C.byref(vol)),'cube volume');print('Cube m3',vol.value*0.0254**3)
 ck(SUModelSaveToFile(m,str(Path(__file__).parent/'sdk_test.skp').encode()));ck(SUModelRelease(C.byref(m)));m=new('SUModelCreateFromFile',str(Path(__file__).parent/'sdk_test.skp').encode());print('Reloaded groups',count('SUEntitiesGetNumGroups',new('SUModelGetEntities',m)));SUModelRelease(C.byref(m));SUTerminate()
