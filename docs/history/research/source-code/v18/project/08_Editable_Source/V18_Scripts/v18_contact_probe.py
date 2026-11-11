import ast
from pathlib import Path
p=Path('work/v18_readback_qa.py');t=ast.parse(p.read_text(encoding='utf8'));prefix=[]
for n in t.body:
 if isinstance(n,ast.For):break
 prefix.append(n)
exec(compile(ast.Module(prefix,type_ignores=[]),'<native contact helpers>','exec'))
f=man_node('SITE_V14_OUTER_STORAGE_FLOOR');m=man_node('SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY');print('NATIVE EXTRUSION FLOOR',f.volume(),'ROOF FLOOR CONTACT',(f^m).volume(),flush=True)
w=man_node('SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY')
for ob in node('SITE_V18_PHOTO_EXTERIOR_WHITE_PIPE_LINES'):
 a=man_ob(ob);print(ob.Attributes.Name,'WOOD CONTACT',(a^w).volume(),'CANOPY CONTACT',(a^m).volume(),flush=True)
