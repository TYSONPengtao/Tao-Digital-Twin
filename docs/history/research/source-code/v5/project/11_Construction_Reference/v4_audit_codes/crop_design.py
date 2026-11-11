import sys
from pathlib import Path
sys.path.insert(0,str(Path('work/libs').resolve()))
import fitz
for n,rel,rect in [('D07_Material','02_结构/结施_01_结构设计说明.pdf',(115,220,411,531)),('D02_Envelope','01_建筑/建施_01_建筑设计说明及图纸目录.pdf',(140,270,592,516))]:
 p=fitz.open(Path(r'E:\jz\MUPDF')/rel)[0];p.get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(*rect)).save('work/v4_audit_codes/'+n+'.png')
