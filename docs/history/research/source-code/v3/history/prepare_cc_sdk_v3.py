import zipfile,urllib.request,json
from pathlib import Path
W=Path(__file__).parent;target=W/'cc_python39';target.mkdir(exist_ok=True)
archive=W/'python-3.9.13-embed-amd64.zip'
if not archive.exists():urllib.request.urlretrieve('https://www.python.org/ftp/python/3.9.13/python-3.9.13-embed-amd64.zip',archive)
with zipfile.ZipFile(archive) as z:z.extractall(target)
wheel=Path(r'C:\Program Files\Bentley\ContextCapture Center\sdk\dist\ccmasterkernel-10.20.1.5562-cp39-cp39-win_amd64.whl')
with zipfile.ZipFile(wheel) as z:
 z.extractall(target)
 for name in z.namelist():
  if name.endswith('METADATA'):print(z.read(name).decode()[:4000])
(target/'python39._pth').write_text('python39.zip\n.\nimport site\n',encoding='ascii')
print(target/'python.exe')
