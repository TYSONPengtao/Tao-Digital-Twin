"""Read-only photo-UV query helper. Never edits source vertices or images.

Coordinate frame must already match: Local_REFERENCE is V5 local metres;
raw JIA OBJ is ENU survey metres. Candidate KD search is approximate, then
closest point on each candidate triangle is exact. A miss stays untextured.
"""
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

def closest_on_triangles(points, triangles):
    p=np.asarray(points,float);t=np.asarray(triangles,float)
    a,b,c=t[:,0],t[:,1],t[:,2]
    ab=b-a;ac=c-a;ap=p-a
    d00=np.einsum('ij,ij->i',ab,ab);d01=np.einsum('ij,ij->i',ab,ac);d11=np.einsum('ij,ij->i',ac,ac)
    d20=np.einsum('ij,ij->i',ap,ab);d21=np.einsum('ij,ij->i',ap,ac)
    den=d00*d11-d01*d01
    v=(d11*d20-d01*d21)/np.maximum(den,1e-30)
    w=(d00*d21-d01*d20)/np.maximum(den,1e-30)
    plane=np.column_stack((1-v-w,v,w));weights=[plane]
    for i,j in [(0,1),(1,2),(2,0)]:
        edge=t[:,j]-t[:,i];v2=p-t[:,i]
        frac=np.clip(np.einsum('ij,ij->i',v2,edge)/np.maximum(np.einsum('ij,ij->i',edge,edge),1e-30),0,1)
        q=np.zeros((len(t),3));q[:,i]=1-frac;q[:,j]=frac;weights.append(q)
    ww=np.stack(weights,axis=1)
    cp=np.einsum('nik,nkj->nij',ww,t)
    d2=np.einsum('nij,nij->ni',cp-p[:,None,:],cp-p[:,None,:])
    d2[:,0]=np.where((plane>=-1e-10).all(axis=1)&(den>1e-25),d2[:,0],np.inf)
    pick=np.argmin(d2,axis=1);idx=np.arange(len(t))
    return cp[idx,pick],ww[idx,pick],np.sqrt(d2[idx,pick])

class PhotoProjector:
    def __init__(self,triangles,triangle_uv,material_ids,material_table):
        t=np.asarray(triangles,float);uv=np.asarray(triangle_uv,float);mi=np.asarray(material_ids,np.int32)
        n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(n,axis=1)
        du=uv[:,1]-uv[:,0];dv=uv[:,2]-uv[:,0];uvarea=np.abs(du[:,0]*dv[:,1]-du[:,1]*dv[:,0])
        keep=(length>1e-12)&(uvarea>1e-14)&np.isfinite(t).all(axis=(1,2))&np.isfinite(uv).all(axis=(1,2))
        self.original_triangle_ids=np.flatnonzero(keep);self.triangles=t[keep];self.uv=uv[keep];self.material_ids=mi[keep];self.normals=n[keep]/length[keep,None]
        self.materials=material_table;self.tree=cKDTree(self.triangles.mean(axis=1))

    @classmethod
    def from_objs(cls,paths,coordinate_transform=None):
        """Original OBJ preserves usemtl untextured-face exclusion.

        transform maps source survey XYZ to target local XYZ. No files change.
        """
        ts=[];us=[];ms=[];table={};material_keys={}
        for path in paths:
            path=Path(path);vv=[];uv=[];faces=[];local_maps={};current=None
            with path.open('r',encoding='utf-8',errors='replace') as f:
                for line in f:
                    if line.startswith('mtllib '):
                        mtl=path.parent/line[7:].strip();mat=None
                        with mtl.open('r',encoding='utf-8',errors='replace') as mf:
                            for ml in mf:
                                if ml.startswith('newmtl '):mat=ml[7:].strip()
                                elif ml.startswith('map_Kd '):
                                    tx=mtl.parent/ml[7:].strip()
                                    if tx.is_file():
                                        key=(str(mtl),mat)
                                        if key not in material_keys:
                                            mi=len(table);material_keys[key]=mi;table[mi]=dict(name=mat,texture=str(tx),source_obj=str(path))
                                        local_maps[mat]=material_keys[key]
                    elif line.startswith('v '):vv.append(list(map(float,line.split()[1:4])))
                    elif line.startswith('vt '):uv.append(list(map(float,line.split()[1:3])))
                    elif line.startswith('usemtl '):current=local_maps.get(line[7:].strip())
                    elif line.startswith('f ') and current is not None:
                        toks=[a.split('/') for a in line.split()[1:]]
                        if not all(len(a)>=2 and a[1] for a in toks):continue
                        vi=[int(a[0])-1 if int(a[0])>0 else len(vv)+int(a[0]) for a in toks]
                        ti=[int(a[1])-1 if int(a[1])>0 else len(uv)+int(a[1]) for a in toks]
                        for j in range(1,len(toks)-1):faces.append(([vi[0],vi[j],vi[j+1]],[ti[0],ti[j],ti[j+1]],current))
            if not faces:continue
            va=np.asarray(vv,float);ua=np.asarray(uv,float)
            if coordinate_transform is not None:
                M=np.asarray(coordinate_transform,float);va=va@M[:3,:3].T+M[:3,3]
            fi=np.array([a[0] for a in faces],np.int32);ui=np.array([a[1] for a in faces],np.int32)
            ts.append(va[fi]);us.append(ua[ui]);ms.append(np.array([a[2] for a in faces],np.int32))
        if not ts:raise ValueError('No textured OBJ triangles with usable face UV')
        return cls(np.concatenate(ts),np.concatenate(us),np.concatenate(ms),table)

    @classmethod
    def from_reference_3dm(cls,path):
        import rhino3dm
        model=rhino3dm.File3dm.Read(str(path));ts=[];us=[];ms=[];table={}
        for i,mat in enumerate(model.Materials):
            tx=mat.GetBitmapTexture()
            if tx and tx.Enabled and Path(tx.FileName).is_file():table[i]=dict(name=mat.Name,texture=tx.FileName)
        for obj in model.Objects:
            g=obj.Geometry;mi=obj.Attributes.MaterialIndex
            if not isinstance(g,rhino3dm.Mesh) or mi not in table or len(g.TextureCoordinates)!=len(g.Vertices):continue
            vv=np.array([[p.X,p.Y,p.Z] for p in g.Vertices],float);uv=np.array([[p.X,p.Y] for p in g.TextureCoordinates],float)
            fi=[]
            for a,b,c,d in g.Faces:
                fi.append([a,b,c])
                if c!=d:fi.append([a,c,d])
            fi=np.asarray(fi,np.int32);ts.append(vv[fi]);us.append(uv[fi]);ms.append(np.full(len(fi),mi,np.int32))
        if not ts:raise ValueError('No textured triangles with usable per-vertex UV')
        return cls(np.concatenate(ts),np.concatenate(us),np.concatenate(ms),table)

    def query(self,points,normals=None,max_distance=.35,min_normal_dot=.5,k=32,batch_size=4096,allow_reversed_normals=False):
        p=np.asarray(points,float);norm=np.asarray(normals,float) if normals is not None else None
        out=dict(matched=np.zeros(len(p),bool),uv=np.full((len(p),2),np.nan),source_triangle=np.full(len(p),-1,np.int64),material_id=np.full(len(p),-1,np.int32),distance=np.full(len(p),np.inf),normal_dot=np.full(len(p),np.nan),barycentric=np.full((len(p),3),np.nan),search='nearest centroid candidates; exact closest point within candidates')
        kk=min(k,len(self.triangles))
        for start in range(0,len(p),batch_size):
            stop=min(start+batch_size,len(p));q=p[start:stop];_,ids=self.tree.query(q,k=kk)
            ids=np.asarray(ids).reshape(len(q),kk);flat=ids.ravel()
            _,bary,dist=closest_on_triangles(np.repeat(q,kk,axis=0),self.triangles[flat]);dist=dist.reshape(len(q),kk)
            nd=np.full_like(dist,np.nan)
            if norm is not None:
                nn=norm[start:stop];nn=nn/np.maximum(np.linalg.norm(nn,axis=1,keepdims=True),1e-30)
                nd=np.einsum('ijk,ik->ij',self.normals[ids],nn)
                score=np.abs(nd) if allow_reversed_normals else nd
                dist=np.where(score>=min_normal_dot,dist,np.inf)
            best=np.argmin(dist,axis=1);ri=np.arange(len(q));chosen=ids[ri,best];dd=dist[ri,best];bb=bary.reshape(len(q),kk,3)[ri,best]
            match=np.isfinite(dd)&(dd<=max_distance);idx=start+ri[match];ci=chosen[match];bw=bb[match]
            out['matched'][idx]=True;out['distance'][idx]=dd[match];out['normal_dot'][idx]=nd[ri,best][match];out['barycentric'][idx]=bw
            out['uv'][idx]=np.einsum('ni,nij->nj',bw,self.uv[ci]);out['source_triangle'][idx]=self.original_triangle_ids[ci];out['material_id'][idx]=self.material_ids[ci]
        return out

def _test():
    t=np.array([[[0,0,0],[1,0,0],[0,1,0]]]);uv=t[:,:,:2]
    proj=PhotoProjector(t,uv,[0],{0:{'texture':'test_only'}})
    q=proj.query([[.2,.3,.1],[2,2,0]],[[0,0,1],[0,0,1]],max_distance=.2)
    assert q['matched'].tolist()==[True,False]
    assert np.allclose(q['uv'][0],[.2,.3])
    rev=proj.query([[.2,.3,.1]],[[0,0,-1]],max_distance=.2)
    assert not rev['matched'][0]
    _,b,d=closest_on_triangles(np.array([[.8,.8,0]]),t)
    assert np.allclose(b[0],[0,.5,.5]) and abs(d[0]-np.sqrt(.18))<1e-12
    return {'passed':True,'checks':['inside barycentric UV','distance reject','opposite normal reject','edge closest point']}

if __name__=='__main__':
    import json
    print(json.dumps(_test()))
