import sys
from pathlib import Path
sys.path.insert(0,str(Path('work/libs').resolve()))
import fitz
jobs=[('D04_Roof_Rain','建施_03_三层及屋顶平面图及大样.pdf',(628,86,984,425)),('D04_F3_Bath','建施_03_三层及屋顶平面图及大样.pdf',(195,133,497,240)),('D03_F1_Bath','建施_02_一二层平面图及大样.pdf',(195,133,500,247)),('D03_F2_Bath','建施_02_一二层平面图及大样.pdf',(617,133,976,265)),('D06_Section','建施_05_剖面装修门窗及大样.pdf',(123,125,580,610))]
for n,filename,rect in jobs:
 d=fitz.open(Path(r'E:\jz\MUPDF\01_建筑')/filename);d[0].get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(*rect)).save('work/v4_audit_codes/'+n+'.png')
