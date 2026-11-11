import json
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid')
q=json.loads((O/'06_Report/Final_V10_Wall_QA.json').read_text(encoding='utf-8'));assert q['status']=='PASS'
text='''# V10 围墙院墙独立核查

本轮共35个更新/新增节点、6917件封闭细部，保留4组原墙芯的顶点、材质和路线，以及65个门楼、照壁、厨房、附属构件。西南原断口、2.60米木门洞及原建筑连接保持；此前删除的西院铁门与棚屋不恢复。

919个当前实际花孔沿墙厚方向进行多点小实体 Boolean 检查，孔内没有邻墙、门柱、厨房墙或新增压顶遮挡；邻近实砖探针有正体积，确认是实际贯穿孔洞。全部新增构件拓扑闭合、顶点有限且体积为正，东侧墙饰件未进入厨房屋面。

原西北两墙链冠顶已有约64.012毫米错台。本轮原墙芯及标高不改，新饰件采用共同角平分线裁切，明确错台收头；转角与断口附近设置200毫米无孔收头区，实际删除易被邻段挡住的孔。两组新花脊的转角交集为零。院内西墙端部另裁切13件饰件到原门柱边界，门柱保持。

这是软件几何与源文件保留核查，参考图装饰比例和未实测尺寸不据此变为已核实施工尺寸。外周花脊为单独的暂定参考造型，现场照片仅明确低瓦帽；内院花脊与长短回纹框有 DJI_0161 的照片依据。

瓦件和花砖在Rhino采用独立双精度封闭网格实体，墙身、青砖和线脚保持原生Brep／挤出实体。转换没有抽稀原顶点与面，便于开模及逐件编辑。原实景10张贴图另按字节/绑定/UV核查。
'''
(O/'06_Report/Final_V10_Wall_QA.md').write_text(text,encoding='utf-8')
p=O/'06_Report/院墙深化依据与版本说明_V10.md'
if p.exists():p.write_text(p.read_text(encoding='utf-8')+'\n最终转角修复及919个实际花孔核查详见 Final_V10_Wall_QA.md。\n',encoding='utf-8')
print('V10 independent audit notes written',flush=True)
