from pathlib import Path
from PIL import Image
W=Path(__file__).parent;im=Image.open('E:/jz/JIA/Rebuild_V24_36/Reports/V24_36_Context_Top.png')
im.crop((1130,120,1660,520)).save(W/'v24_37/North_Skirt_Review.png')
