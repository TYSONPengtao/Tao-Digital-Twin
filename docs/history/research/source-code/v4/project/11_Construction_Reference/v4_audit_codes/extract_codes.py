import sys
from pathlib import Path
sys.path.insert(0,str(Path('work/libs').resolve()))
import fitz
for p in Path('work/v4_audit_codes').glob('*.pdf'):
 try:
  d=fitz.open(p); t='\n'.join('--- PAGE '+str(i+1)+' ---\n'+x.get_text() for i,x in enumerate(d));p.with_suffix('.txt').write_text(t,encoding='utf-8');print(p.name,len(d),len(t))
 except Exception as e:print(p.name,e)
