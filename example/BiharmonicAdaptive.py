
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import sys

from fealpy.mesh.meshio import load_mat_mesh
from fealpy.mesh.simple_mesh_generator import rectangledomainmesh  
from fealpy.mesh.simple_mesh_generator import triangle, unitsquaredomainmesh

from fealpy.functionspace.tools import function_space 
from fealpy.femmodel.BiharmonicFEMModel import BiharmonicRecoveryFEMModel
from fealpy.boundarycondition.BoundaryCondition import DirichletBC
from fealpy.solver import solve
from fealpy.functionspace.function import FiniteElementFunction
from fealpy.erroranalysis.PrioriError import L2_error, div_error, H1_semi_error
from fealpy.model.BiharmonicModel2d import BiharmonicData4, BiharmonicData5, BiharmonicData6, BiharmonicData7, BiharmonicData8

from fealpy.quadrature.TriangleQuadrature import TriangleQuadrature 

from fealpy.tools.show import showmultirate

from fealpy.mesh.adaptive_tools import mark


def smooth_eta(mesh, eta):
    m = np.max(eta)
    eta /= m
    area = mesh.area()
    q2c = mesh.ds.point_to_cell()
    cell = mesh.ds.cell
    w = q2c@area
    for i in range(10): 
        beta = q2c@(eta*area)/w
        eta = np.sum(beta[cell], axis=1)/3 
    return eta
        


m = int(sys.argv[1])
theta = float(sys.argv[2])
maxit = int(sys.argv[3])

if m == 1:
    model = BiharmonicData5(a=0.01)
    mesh = model.init_mesh()
elif m == 2:
    model = BiharmonicData6()
    mesh = model.init_mesh(n=4)
elif m == 3:
    model = BiharmonicData7()
    mesh = model.init_mesh(n=4)
elif m == 4:
    model = BiharmonicData8()
    mesh = model.init_mesh(n=4)
else:
    raise ValueError("error!")


sigma = 1
k = maxit -20  
degree = 1


idx = [0, 9, 19, 29, 39]

errorType = ['$\| u - u_h\|$',
         '$\|\\nabla u - \\nabla u_h\|$',
         '$\|\\nabla u_h - G(\\nabla u_h) \|$',
         '$\|\\nabla u - G(\\nabla u_h)\|$',
         '$\|\Delta u - \\nabla\cdot G(\\nabla u_h)\|$',
         '$\|\Delta u -  G(\\nabla\cdot G(\\nabla u_h))\|$'
         ]
Ndof = np.zeros((maxit,), dtype=np.int)
errorMatrix = np.zeros((len(errorType), maxit), dtype=np.float)


for i in range(maxit):
    print(i, 'step:')
    V = function_space(mesh, 'Lagrange', degree)
    V2 = function_space(mesh, 'Lagrange_2', degree)
    uh = FiniteElementFunction(V)
    rgh = FiniteElementFunction(V2)
    rlh = FiniteElementFunction(V)

    fem = BiharmonicRecoveryFEMModel(V, model, sigma=sigma, rtype='inv_area')
    bc = DirichletBC(V, model.dirichlet)
    solve(fem, uh, dirichlet=bc, solver='direct')
    fem.recover_grad(uh, rgh)
    fem.recover_laplace(rgh, rlh)

    eta = fem.recover_estimate(uh, rgh)

    Ndof[i] = V.number_of_global_dofs() 
    errorMatrix[0, i] = L2_error(model.solution, uh, order=8)
    errorMatrix[1, i] = H1_semi_error(model.gradient, uh, order=8)
    errorMatrix[2, i] = np.sqrt(np.sum(eta**2))
    errorMatrix[3, i] = L2_error(model.gradient, rgh, order=8)
    errorMatrix[4, i] = div_error(model.laplace, rgh, order=8)
    errorMatrix[5, i] = L2_error(model.laplace, rlh, order=8)

    if i in idx:
        fig = plt.figure()
        fig.set_facecolor('white')
        axes = fig.gca() 
        mesh.add_plot(axes, cellcolor='w')
        fig.savefig('mesh'+str(m-2)+'-'+str(i)+'.pdf')


    markedCell = mark(eta, theta)
    if i < maxit - 1:
        mesh.bisect(markedCell)


fig2 = plt.figure()
fig2.set_facecolor('white')
axes = fig2.gca(projection='3d')
x = mesh.point[:, 0]
y = mesh.point[:, 1]
s = axes.plot_trisurf(x, y, uh, triangles=mesh.ds.cell, cmap=plt.cm.jet, lw=0.0)
fig2.colorbar(s)
fig2.savefig('solution.pdf')

fig3 = plt.figure()
fig3.set_facecolor('white')
axes = fig3.gca()
optionlist = ['k-*', 'b-o', 'r--^', 'g->', 'm-8', 'c-D']
showmultirate(axes, k, Ndof, errorMatrix, optionlist, errorType, ls=20)
fig3.savefig('error.pdf')
plt.show()
