import Rhino,json
d=Rhino.RhinoDoc.ActiveDoc;rows=[]
for o in d.Objects:
 a=o.Attributes
 if 'Brick' in (a.Name or '') or 'Masonry' in (a.Name or '') or 'CLEAN' in (a.Name or '').upper():
  m=d.Materials[a.MaterialIndex];tx=m.GetBitmapTexture();r=o.RenderMaterial
  rows.append({'name':a.Name,'material_index':a.MaterialIndex,'material_name':m.Name,'bitmap':tx.FileName if tx else None,'render_name':r.Name if r else None,'pbr':m.IsPhysicallyBased,'pbr_base':str(m.PhysicallyBased.BaseColor) if m.IsPhysicallyBased else None,'render_id':str(m.RenderMaterialInstanceId)})
with open('E:/jz/JIA/Rebuild_V25/Reports/V25_Desktop_Material_Probe.json','w') as f:json.dump({'objects':rows,'materials':d.Materials.Count},f,ensure_ascii=True,indent=2)
