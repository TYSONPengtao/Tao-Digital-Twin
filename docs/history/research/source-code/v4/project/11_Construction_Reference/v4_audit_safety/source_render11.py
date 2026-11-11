import sys
sys.path.insert(0,r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work\libs')
import fitz
from pathlib import Path
p=next(Path(r'E:\jz\MUPDF').rglob('结施_05_楼梯配筋图二.pdf'))
d=fitz.open(p);pg=d[0]
pg.get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(pg.rect.width*.025,pg.rect.height*.10,pg.rect.width*.49,pg.rect.height*.55)).save(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work\v4_audit_safety\D11_1175_Hi.png')
