VIEWS=[]
for fl,z in[(1,0.),(2,3.9000244),(3,7.5000002)]:
 for side in(['L','R']if fl<3 else['R']):
  x=2.3 if side=='L'else 10.7;end=3.8 if side=='L'else 9.2
  VIEWS.append((f'F{fl}_{side}_Full_Window_Jamb',(x,3.5,1.1+z),(end,2.0,1.7+z),24))
  if fl==1:VIEWS.append((f'F{fl}_{side}_Head_Joint',(x,3.0,1.95+z),(end,2.05,3.12+z),34))

VIEWS += [('F1_R_Entry_Exterior',(6.2,-1.7,1.3),(9.05,1.96,1.5),31),('F1_R_Outer_Column',(10.7,3.5,1.2),(12.9,1.95,1.9),26),('Front_Facade',(19,-13,8.5),(6.5,1.2,4.2),32)]
