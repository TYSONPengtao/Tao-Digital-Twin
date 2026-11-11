from v26_2_common import *
import html,re,xml.etree.ElementTree as ET
D=W/'v26_3';O=Path('E:/jz/JIA/Rebuild_V26_3');R=O/'Reports'
source=(W/'v26_3_package.py').read_text('utf8');exec(source[source.index('# The plan is'):source.index("proof={'model':")])
print('NATIVE_PLAN_READY')
