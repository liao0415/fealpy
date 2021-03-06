import numpy as np
from scipy.sparse import coo_matrix, csc_matrix, csr_matrix, spdiags, eye

from ..quadrature import IntervalQuadrature
from ..functionspace.barycentric_coordinates import bc_to_point, grad_lambda


class DirichletBC:
    def __init__(self, V, g0, is_boundary_dof=None, dtype=np.float):
        self.V = V
        self.g0 = g0

        gdof = V.number_of_global_dofs()
        if is_boundary_dof == None:
            isBdDof = np.zeros(gdof, dtype=np.bool)
            edge2dof = V.edge_to_dof()
            isBdEdge = V.mesh.ds.boundary_edge_flag()
            isBdDof[edge2dof[isBdEdge]] = True
        else:
            ipoints = V.interpolation_points()
            isBdDof = is_boundary_dof(ipoints)

        self.isBdDof = isBdDof
        self.dtype = dtype

    def apply(self, A, b):
        """ Modify matrix A and b
        """
        g0 = self.g0
        V = self.V
        isBdDof = self.isBdDof

        gdof = V.number_of_global_dofs()

        x = np.zeros((gdof,), dtype=self.dtype)

        ipoints = V.interpolation_points()
        x[isBdDof] = g0(ipoints[isBdDof,:])
        b -= A@x

        bdIdx = np.zeros(gdof, dtype=np.int)
        bdIdx[isBdDof] = 1
        Tbd = spdiags(bdIdx, 0, gdof, gdof)
        T = spdiags(1-bdIdx, 0, gdof, gdof)
        A = T@A@T + Tbd

        b[isBdDof] = x[isBdDof] 
        return A, b

    def apply_on_matrix(self, A):

        V = self.V
        isBdDof = self.isBdDof
        gdof = V.number_of_global_dofs()

        bdIdx = np.zeros((A.shape[0], ), np.int)
        bdIdx[isBdDof] = 1
        Tbd = spdiags(bdIdx, 0, A.shape[0], A.shape[0])
        T = spdiags(1-bdIdx, 0, A.shape[0], A.shape[0])
        A = T@A@T + Tbd

        return A

    def apply_on_vector(self, b, A):
        
        g0 = self.g0
        V = self.V
        isBdDof = self.isBdDof

        gdof = V.number_of_global_dofs()
        x = np.zeros((gdof,), dtype=self.dtype)

        x[isBdDof] = g0(ipoints[isBdDof,:])
        b -= A@x

        b[isBdDof] = x[isBdDof] 

        return b



        


