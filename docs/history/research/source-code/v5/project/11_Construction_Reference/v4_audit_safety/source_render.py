import sys
sys.path.insert(0,r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work\libs')
import fitz
from pathlib import Path
p=next(Path(r'E:\jz\MUPDF').rglob('结施_04_楼梯配筋图一.pdf'))
d=fitz.open(p); pg=d[0]
print(pg.rect)
rect=fitz.Rect(pg.rect.width*.17,pg.rect.height*.13,pg.rect.width*.425,pg.rect.height*.34)
pg.get_pixmap(matrix=fitz.Matrix(6,6),clip=rect).save(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work\v4_audit_safety\D10_1175_Hi.png')
