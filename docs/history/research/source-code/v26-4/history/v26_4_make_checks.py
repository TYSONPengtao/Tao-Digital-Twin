from pathlib import Path
W=Path(__file__).parent
s=(W/'v26_3_readback.py').read_text('utf8');a=s.index('# The recovered screenwall');b=s.index('# Export actual evaluated hinge matrices');s=s[:a]+s[b:]
s=s.replace('v26_3','v26_4').replace('V26_3','V26_4').replace('V26.2 source remains','V26.3 source remains').replace('V26_4_House_Connected_Walls_And_Stairs','V26_3_House_Connected_Walls_And_Stairs')
(W/'v26_4_readback.py').write_text(s,encoding='utf8')
s=(W/'v26_3_physics_qa.py').read_text('utf8').replace('V26_3','V26_4').replace('v26_3','v26_4')
(W/'v26_4_physics_qa.py').write_text(s,encoding='utf8')
s=(W/'v26_4_overlap_audit.py').read_text('utf8').replace("FD=W/'v26_3/Final'","FD=W/'v26_4/Final'").replace("D/'Overlap_Audit.json'","D/'Overlap_Audit_After.json'").replace('V26.3 actual saved mesh export','V26.4 actual saved mesh export')
(W/'v26_4_overlap_after.py').write_text(s,encoding='utf8')
