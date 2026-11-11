import sys
sys.path.insert(0,r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work\libs')
from PIL import Image
p=r'E:\jz\JIA\Rebuild_V3\02_PDF_Reference\D10.png'
im=Image.open(p)
im.crop((340,200,790,550)).resize((1350,1050)).save(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work\v4_audit_safety\D10_1175_90_Source.png')
