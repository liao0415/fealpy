
import numpy as np
from .TriangleMesh import TriangleMesh, TriangleMeshWithInfinityPoint
from .QuadrangleMesh import QuadrangleMesh 
from .HexahedronMesh import HexahedronMesh 
from .PolygonMesh import PolygonMesh 

from .level_set_function import DistDomain2d, DistDomain3d
from .level_set_function import dcircle, drectangle
from .level_set_function import ddiff 
from .sizing_function import huniform
from .distmesh import DistMesh2d 



def squaremesh(x0, x1, y0, y1, r=3, dtype=np.float):
    points = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=dtype)
    cells = np.array([[1, 2, 0], [3, 0, 2]], dtype=np.int)
    mesh = TriangleMesh(points, cells, dtype=dtype)
    mesh.uniform_refine(r)
    return mesh 

def rectangledomainmesh(box, nx=10, ny=10, meshtype='tri', dtype=np.float):
    N = (nx+1)*(ny+1)
    NC = nx*ny
    point = np.zeros((N,2))
    X, Y = np.mgrid[box[0]:box[1]:complex(0,nx+1), box[2]:box[3]:complex(0,ny+1)]
    point[:,0] = X.flatten()
    point[:,1] = Y.flatten()

    idx = np.arange(N).reshape(nx+1, ny+1)
    if meshtype=='tri':
        cell = np.zeros((2*NC, 3), dtype=np.int)
        cell[:NC, 0] = idx[1:,0:-1].flatten(order='F')
        cell[:NC, 1] = idx[1:,1:].flatten(order='F')
        cell[:NC, 2] = idx[0:-1, 0:-1].flatten(order='F')
        cell[NC:, 0] = idx[0:-1, 1:].flatten(order='F')
        cell[NC:, 1] = idx[0:-1, 0:-1].flatten(order='F')
        cell[NC:, 2] = idx[1:, 1:].flatten(order='F')
        return TriangleMesh(point, cell)
    elif meshtype == 'quad':
        cell = np.zeros((NC,4), dtype=np.int)
        cell[:,0] = idx[0:-1, 0:-1].flatten()
        cell[:,1] = idx[1:, 0:-1].flatten()
        cell[:,2] = idx[1:, 1:].flatten()
        cell[:,3] = idx[0:-1, 1:].flatten()
        return QuadrangleMesh(point, cell)
    elif meshtype == 'polygon':
        cell = np.zeros((NC,4), dtype=np.int)
        cell[:,0] = idx[0:-1, 0:-1].flatten()
        cell[:,1] = idx[1:, 0:-1].flatten()
        cell[:,2] = idx[1:, 1:].flatten()
        cell[:,3] = idx[0:-1, 1:].flatten()
        return PolygonMesh(point, cell)

def triangle(box, h):
    from meshpy.triangle import MeshInfo, build
    mesh_info = MeshInfo()
    mesh_info.set_points([(box[0], box[2]), (box[1], box[2]), (box[1], box[3]), (box[0], box[3])])
    mesh_info.set_facets([[0,1], [1,2], [2,3], [3,0]])  
    mesh = build(mesh_info, max_volume=h**2)
    point = np.array(mesh.points, dtype=np.float)
    cell = np.array(mesh.elements, dtype=np.int)
    return TriangleMesh(point, cell)

def unitsquaredomainmesh(h0, meshtype='tri', dtype=np.float):
    fd = lambda p: drectangle(p, [0, 1, 0, 1])
    fh = huniform
    bbox = [-0.2, 1.2, -0.2, 1.2]
    pfix = np.array([[0,0],[1,0],[1,1],[0,1]], dtype=dtype) 
    domain = DistDomain2d(fd, fh, bbox, pfix)
    distmesh2d = DistMesh2d(domain, h0)
    distmesh2d.run()
    if meshtype is 'tri':
        return distmesh2d.mesh
    elif meshtype is 'polygon':
        mesh = TriangleMeshWithInfinityPoint(distmesh2d.mesh)
        ppoint, pcell, pcellLocation = mesh.to_polygonmesh()
        return PolygonMesh(ppoint, pcell, pcellLocation) 

def unitcircledomainmesh(h0, meshtype='tri', dtype=np.float):
    fd = lambda p: dcircle(p,(0,0),1)
    fh = huniform
    bbox = [-1.2, 1.2, -1.2, 1.2]
    pfix = None 
    domain = DistDomain2d(fd, fh, bbox, pfix)
    distmesh2d = DistMesh2d(domain, h0)
    distmesh2d.run()
    if meshtype is 'tri':
        return distmesh2d.mesh
    elif meshtype is 'polygon':
        mesh = TriangleMeshWithInfinityPoint(distmesh2d.mesh)
        ppoint, pcell, pcellLocation = mesh.to_polygonmesh()
        return PolygonMesh(ppoint, pcell, pcellLocation) 

def cubehexmesh(cube, nx=10, ny=10, nz=10):
    N = (nx+1)*(ny+1)*(nz+1)
    NC = nx*ny*nz
    point = np.zeros((N, 3), dtype=np.float)
    X, Y, Z = np.mgrid[
            cube[0]:cube[1]:complex(0, nx+1), 
            cube[2]:cube[3]:complex(0, ny+1),
            cube[4]:cube[5]:complex(0, nz+1)
            ]
    point[:, 0] = X.flatten()
    point[:, 1] = Y.flatten()
    point[:, 2] = Z.flatten()

    idx = np.arange(N).reshape(nx+1, ny+1, nz+1)
    c = idx[:-1, :-1, :-1]

    cell = np.zeros((NC, 8), dtype=np.int)
    nyz = (ny + 1)*(nz + 1)
    cell[:, 0] = c.flatten()
    cell[:, 1] = cell[:, 0] + nyz
    cell[:, 2] = cell[:, 1] + nz + 1
    cell[:, 3] = cell[:, 0] + nz + 1
    cell[:, 4] = cell[:, 0] + 1
    cell[:, 5] = cell[:, 4] + nyz
    cell[:, 6] = cell[:, 5] + nz + 1
    cell[:, 7] = cell[:, 4] + nz + 1

    return HexahedronMesh(point, cell)
