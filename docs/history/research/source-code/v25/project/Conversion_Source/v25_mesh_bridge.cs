using System;
using System.IO;
using System.Security.Cryptography;
using Rhino.Geometry;
using Rhino.Render;

public static class V25MeshBridge {
 public static Mesh Read(string path) {
  using (BinaryReader r = new BinaryReader(File.OpenRead(path))) {
   if (new string(r.ReadChars(4)) != "R25M" || r.ReadUInt32() != 1) throw new Exception("Unsupported V25 geometry file");
   int nv=r.ReadInt32(), nf=r.ReadInt32();
   Mesh m=new Mesh(); m.Vertices.UseDoublePrecisionVertices=true; m.Vertices.Capacity=nv; m.Faces.Capacity=nf;
   for(int i=0;i<nv;i++) m.Vertices.Add(r.ReadDouble(),r.ReadDouble(),r.ReadDouble());
   Vector3f[] normals=new Vector3f[nv];
   for(int i=0;i<nv;i++) normals[i]=new Vector3f(r.ReadSingle(),r.ReadSingle(),r.ReadSingle());
   Point2f[] uv=new Point2f[nv];
   for(int i=0;i<nv;i++) uv[i]=new Point2f(r.ReadSingle(),r.ReadSingle());
   for(int i=0;i<nf;i++) m.Faces.AddFace(r.ReadInt32(),r.ReadInt32(),r.ReadInt32());
   m.SetTextureCoordinates(TextureMapping.CreatePlaneMapping(Plane.WorldXY,new Interval(0,1),new Interval(0,1),new Interval(0,1)),Transform.Identity,false);
   m.TextureCoordinates.SetTextureCoordinates(uv); m.Normals.SetNormals(normals); m.FaceNormals.ComputeFaceNormals();
   if (r.BaseStream.Position != r.BaseStream.Length) throw new Exception("Unexpected bytes in V25 mesh");
   return m;
  }
 }
 public static string Hash(Mesh m) {
  using(SHA256 s=SHA256.Create()) using(CryptoStream stream=new CryptoStream(Stream.Null,s,CryptoStreamMode.Write)) using(BinaryWriter w=new BinaryWriter(stream)) {
   w.Write(new byte[]{82,50,53,77});w.Write((uint)1);w.Write(m.Vertices.Count);w.Write(m.Faces.Count);
   for(int i=0;i<m.Vertices.Count;i++){Point3d p=m.Vertices.Point3dAt(i);w.Write(p.X);w.Write(p.Y);w.Write(p.Z);}
   for(int i=0;i<m.Normals.Count;i++){Vector3f n=m.Normals[i];w.Write(n.X);w.Write(n.Y);w.Write(n.Z);}
   for(int i=0;i<m.TextureCoordinates.Count;i++){Point2f p=m.TextureCoordinates[i];w.Write(p.X);w.Write(p.Y);}
   for(int i=0;i<m.Faces.Count;i++){MeshFace f=m.Faces[i];if(!f.IsTriangle)throw new Exception("Unexpected quad");w.Write(f.A);w.Write(f.B);w.Write(f.C);}
   w.Flush();stream.FlushFinalBlock();return BitConverter.ToString(s.Hash).Replace("-","").ToLowerInvariant();
  }
 }
 public static double Area(Mesh m) {
  double a=0;
  for(int i=0;i<m.Faces.Count;i++){MeshFace f=m.Faces[i];Point3d p=m.Vertices.Point3dAt(f.A), q=m.Vertices.Point3dAt(f.B), r=m.Vertices.Point3dAt(f.C);a+=Vector3d.CrossProduct(q-p,r-p).Length*0.5;}
  return a;
 }
 public static double[] Bounds(Mesh m) {BoundingBox b=m.GetBoundingBox(true);return new double[]{b.Min.X,b.Min.Y,b.Min.Z,b.Max.X,b.Max.Y,b.Max.Z};}
 public static double[] CompareTransformed(Mesh m, string reference, Transform transform) {
  using(Mesh r=Read(reference)) {
   if(m.Vertices.Count!=r.Vertices.Count || m.Faces.Count!=r.Faces.Count || m.TextureCoordinates.Count!=r.TextureCoordinates.Count || m.Normals.Count!=r.Normals.Count) throw new Exception("Different topology");
   double pos=0,normal=0,uv=0,faces=0;
   for(int i=0;i<m.Vertices.Count;i++) {Point3d p=r.Vertices.Point3dAt(i);p.Transform(transform);pos=Math.Max(pos,p.DistanceTo(m.Vertices.Point3dAt(i)));Vector3d n=new Vector3d(r.Normals[i]);n.Transform(transform);Vector3d q=new Vector3d(m.Normals[i]);normal=Math.Max(normal,(n-q).Length);Point2f a=r.TextureCoordinates[i],z=m.TextureCoordinates[i];uv=Math.Max(uv,Math.Abs(a.X-z.X)+Math.Abs(a.Y-z.Y));}
   for(int i=0;i<m.Faces.Count;i++){MeshFace x=m.Faces[i],y=r.Faces[i];if(x.A!=y.A||x.B!=y.B||x.C!=y.C||x.D!=y.D)faces++;}
   return new double[]{pos,normal,uv,faces};
  }
 }
}
