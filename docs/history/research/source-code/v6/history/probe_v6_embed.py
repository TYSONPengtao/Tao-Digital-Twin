import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'libs'));import rhino3dm as r
f=r.File3dm.Read(r'E:\jz\纯场地版本.3dm')
for n in ['EmbeddedFiles','Bitmaps']:
 a=getattr(f,n,None);print(n,type(a),dir(a))
print('File3dmWriteOptions',dir(r.File3dmWriteOptions()))
print('Add embedded',f.EmbeddedFiles.Add.__doc__)
print('Embedded class',dir(r.EmbeddedFile))
print('Embedded init',r.EmbeddedFile.__init__.__doc__)
print('Embedded doc',r.EmbeddedFile.Read.__doc__)
print('FileReference',dir(r.FileReference))
print('FileReferenceCreate',r.FileReference.CreateFromFullAndRelativePaths.__doc__)
