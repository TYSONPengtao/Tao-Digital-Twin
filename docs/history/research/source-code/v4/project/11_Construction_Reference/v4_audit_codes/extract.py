import sys
from pathlib import Path
sys.path.insert(0,str(Path('work/libs').resolve()))
import fitz
p=fitz.open(r'E:\jz\MUPDF\01_建筑\建施_01_建筑设计说明及图纸目录.pdf')[0]
p.get_pixmap(matrix=fitz.Matrix(5,5),clip=fitz.Rect(598,138,1010,459)).save('work/v4_audit_codes/D02_Right_Notes.png')
