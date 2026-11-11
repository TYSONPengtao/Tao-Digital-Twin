import sys
from pathlib import Path
sys.path.insert(0,str(Path('work/libs').resolve()))
import fitz
for n,pgs in [('55030_full_official',[20,21,22]),('55031_full_0',[20,21]),('55038_full_official',[12,13,14,15,16])]:
 d=fitz.open('work/v4_audit_codes/'+n+'.pdf')
 for pg in pgs:d[pg-1].get_pixmap(matrix=fitz.Matrix(2,2)).save('work/v4_audit_codes/'+n+'_p'+str(pg)+'.png')
