import json,shutil
from pathlib import Path
W=Path(__file__).parent
OLD=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid')
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid')
for d in ['01_Source','02_Data','03_Textures/Base','03_Textures/Patch','04_Rhino','05_Export','06_Report','07_Evidence/Current_Annotations','08_Editable_Source/05_Intermediate','08_Editable_Source/06_Rhino']:(O/d).mkdir(parents=True,exist_ok=True)
for folder in ['01_Source','02_Data','03_Textures']:
    shutil.copytree(OLD/folder,O/folder,dirs_exist_ok=True)
for folder in ['05_Intermediate']:
    shutil.copytree(OLD/'08_Editable_Source'/folder,O/'08_Editable_Source'/folder,dirs_exist_ok=True)
for name in ['Materials.json','Base_Index.json']:
    p=O/'02_Data'/name
    d=json.loads(p.read_text(encoding='utf-8'))
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2).replace(str(OLD).replace('\\','\\\\'),str(O).replace('\\','\\\\')),encoding='utf-8')
for name in ['使用说明.md','06_Report/需求汇总与修模依据_V7.md','06_Report/前期需求汇总_V6留档.md']:
    src=OLD/name
    shutil.copy2(src,O/'07_Evidence'/('Prior_'+src.name))
for n in ['001244','001317','001423','001456','001538','001628','001738']:
    src=Path(r'D:\Desktop\新建文件夹')/('屏幕截图 2026-10-09 '+n+'.jpg')
    shutil.copy2(src,O/'07_Evidence/Current_Annotations'/src.name)
for n in ['0110','0046']:
    src=Path(r'D:\DJI\0002\DCIM\101MEDIA')/('DJI_'+n+'.JPG')
    shutil.copy2(src,O/'07_Evidence/Current_Annotations'/src.name)
print('V8 initialized separately; V7 and original sources untouched',flush=True)
