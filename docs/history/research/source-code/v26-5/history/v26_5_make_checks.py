from pathlib import Path
W=Path(__file__).parent
for suffix in ['readback','protection_qa','geometry_qa','physics_qa','overlap_after','overlap_gate']:
 src=W/f'v26_4_{suffix}.py';code=src.read_text('utf8').replace('v26_4','v26_5').replace('V26_4','V26_5')
 if suffix=='readback':code=code.replace('V26.3 source remains byte identical','V26.4 source remains byte identical')
 (W/f'v26_5_{suffix}.py').write_text(code,encoding='utf8')
print('V26_5_CHECK_SCRIPTS_READY')
