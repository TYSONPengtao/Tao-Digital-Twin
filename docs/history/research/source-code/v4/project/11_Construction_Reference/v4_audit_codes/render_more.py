import sys
from pathlib import Path
sys.path.insert(0,str(Path('work/libs').resolve()))
import fitz
for n,pgs in [('55031_full_0',[14,15]),('55030_full_official',[23]),('55032_full_official',[5,6,7,8])]:
 d=fitz.open('work/v4_audit_codes/'+n+'.pdf');print(n,len(d))
 for pg in pgs:d[pg-1].get_pixmap(matrix=fitz.Matrix(2,2)).save('work/v4_audit_codes/'+n+'_p'+str(pg)+'.png')
