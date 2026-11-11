from pathlib import Path
p=Path(__file__).with_name('blender_v3.py');s=p.read_text(encoding='utf-8')
old="['CAM_02_Front','CAM_03_Back','CAM_05_Aerial','CAM_06_Whole_Site','CAM_07_Column','CAM_08_Junction','CAM_01_Entrance','CAM_09_SW_Gate','CAM_10_Screenwall','CAM_11_Chinese_Kitchen','CAM_12_Inner_Gate']"
new="['CAM_06_Whole_Site','CAM_09_SW_Gate','CAM_11_Chinese_Kitchen']"
assert old in s;s=s.replace(old,new)
exec(compile(s,str(p),'exec'))
