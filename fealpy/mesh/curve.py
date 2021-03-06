
import numpy as np

def msign(x):
    flag = np.sign(x)
    flag[np.abs(x) < 1e-8] = 0
    return flag

class CircleCurve():

    def __init__(self, cx, cy, r):
        self.cx = cx
        self.cy = cy
        self.r = r
        self.box = [cx - r - 0.1, cx + r + 0.1, cy - r - 0.1, cy + r + 0.1]


    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")


        return (x - self.cx)**2 + (y - self.cy)**2 - self.r**2 



class Curve1():
    def __init__(self, a=6):
        self.a = a
        self.box = [-1, 1, -1, 1]

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        a = self.a
        anu = 0.02*np.sqrt(5)
        theta = np.arctan2(y- anu, x - anu)

        return (x - anu)**2 + (y - anu)**2 - (0.5 + 0.2 * np.sin(a*theta))**2 


class Curve2():
    def __init__(self, r0=0.60125, r1=0.24012):
        self.r0 = r0
        self.r1 = r1
        self.box = [-1, 1, -1, 1]

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        r0 = self.r0
        r1 = self.r1
        pi = np.pi

        x1 = np.arccos(-1/4)/4
        x0 = pi/2 - x1 - np.sin(4*x1)
         
        theta = np.arctan2(y, x)
        isNeg = theta < 0
        theta[isNeg] = theta[isNeg] + 2*pi

        z = np.zeros(len(x), dtype=np.float)
        rp = np.sqrt(x**2 + y**2)

        isSingle0 = (theta >= 0) & (theta < x0) # [0,x0]
        isSingle1 = (theta > pi/2 - x0) & (theta < pi/2 + x0) # [pi/2 - x0, pi/2 + x0]
        isSingle2 = (theta > pi - x0) & (theta < pi + x0) # [pi - x0, pi + x0]
        isSingle3 = (theta > 3*pi/2 - x0) & (theta < 3*pi/2 +x0) # [3*pi/2 - x0, 3*pi/2 + x0]
        isSingle4 = (theta > 2*pi - x0) & (theta <= 2*pi) # [2*pi - x0, 2*pi]

        isThree0 = (theta >= x0) & (theta <= pi/2 - x0) # [x0,x1], [x1,pi/2-x1],[pi/2 - x1,pi/2-x0]
        isThree1 = (theta >= pi/2 + x0) & (theta <= pi - x0) # [pi/2 + x0, pi/2 + x1], [ pi/2 + x1, pi - x1],[pi - x1, pi - x0]
        isThree2 = (theta >= pi + x0) & (theta <= 3*pi/2 - x0) # [pi + x0, pi + x1],[pi + x1, 3*pi/2 - x1],[3*pi/2 - x1,3*pi/2 - x0]
        isThree3 = (theta >= 3*pi/2 + x0) & (theta <= 2*pi - x0) # [3*pi/2 + x0, 3*pi/2 + x1], [ 3*pi/2 + x1, 2*pi - x1],[2*pi - x1, 2*pi - x0]

        isSingle = (isSingle0 | isSingle1 | isSingle2 | isSingle3 | isSingle4)
        theta1 = theta[isSingle]
        t0 = np.zeros(len(x), dtype=np.float)
        t0[isSingle0] = x0/2
        t0[isSingle1] = pi/2
        t0[isSingle2] = pi
        t0[isSingle3] = 3*pi/2
        t0[isSingle4] = 2*pi - x0/2

        if len(theta1)>0:
           t = self.get_T(theta1.reshape(-1, 1), t0[isSingle])
           r = r0 + r1*np.cos(4*t + pi/2)
           z[isSingle] = rp[isSingle]**2 - r**2

        isThree = (isThree0 | isThree1 | isThree2 | isThree3)
        theta1 = theta[isThree]
        z1 = np.zeros(len(theta1), dtype=np.float)

        t0[isThree0, 0] = (x0 + x1)/2
        t0[isThree0, 1] = pi/4
        t0[isThree0, 2] = pi/2 - (x0 + x1)/2

        t0[isThree1, 0] = pi/2 + (x0 + x1)/2
        t0[isThree1, 1] = 3*pi/4
        t0[isThree1, 2] = pi - (x0 + x1)/2

        t0[isThree2, 0] = pi + (x0 + x1)/2
        t0[isThree2, 1] = 5*pi/4
        t0[isThree2, 2] = 3*pi/2 - (x0 + x1)/2

        t0[isThree3, 0] = 3*pi/2 + (x0 + x1)/2
        t0[isThree3, 1] = 7*pi/4
        t0[isThree3, 2] = 2*pi - (x0 + x1)/2

        if np.any(isThree):
           t = self.get_T(theta1.reshape(-1, 1), t0[isThree])
           r = r0 + r1*np.cos(4*t + pi/2) 
           rt = rp[isThree]
           flag1 = (rt < (r[:,0] + r[:,1])/2)
           flag2 = (rt >= (r[:,0] + r[:,1])/2) & (rt < (r[:, 1] + r[:,2])/2)
           flag3 = (rt >= (r[:,1] + r[:,2])/2)
           if np.any(flag1):
               z1[flag1] = rt[flag1]**2 - r[flag1, 0]**2

           if np.any(flag2):
               z1[flag2] = r[flag2, 1]**2 - rt[flag2]**2

           if np.any(flag3):
               z1[flag3] = rt[flag3]**2- r[flag3, 2]**2

           z[isThree] = z1

        tt = np.array([x1, 2*pi - x1, pi/2 - x1, pi/2 + x1, pi - x1, pi + x1, 3*pi/2 - x1, 3*pi/2 + x1], dtype=np.float)
        rt = r0 + r1 * np.cos(4*tt + pi/2);
        xt = rt*np.cos( tt + np.sin(4*tt));
        yt = rt*np.sin( tt + np.sin(4*tt));
        rt = np.zeros((len(x), 8), dtype=np.float)
        for i in range(8): 
            rt[:,i] = np.sqrt((x - xt[i])**2 + (y - yt[i])**2)    

        rt = np.min(rt, axis=1)

        s = np.sign(z)
        u = np.abs(z)
        isBigger = u > rt

        u[isBigger] = rt[isBigger]
        return s*u

    def get_T(self, theta, t0):
        eps = 1e-8
        f = t0 + np.sin(4*t0) - theta
        fprime = 1 + 4*np.cos(4*t0)
        t = t0 - f/fprime
        err = np.sqrt(sum(sum(f**2)))
        while err > eps:
            t0 = t
            f = t0 + np.sin(4*t0) - theta
            fprime = 1 + 4*np.cos(4*t0)
            t = t0 - f/fprime
            err = np.sqrt(np.sum(f**2))
    
class Curve3():

    def __init__(self):
        self.box = [-25, 25, -25, 25]

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        r = x**2 + y**2
        theta = np.arctan2(y,x)
        isNeg = theta < 0
        theta[isNeg] = theta[isNeg] + 2*np.pi
        x1 = 16*np.sin(theta)**3
        y1 = 13*np.cos(theta) - 5*np.cos(2*theta) - 2*np.cos(3*theta) - np.cos(4*theta)
        return r - (x1**2 + y1**2)

class BicornCurve():
    '''
        http://www-gap.dcs.st-and.ac.uk/~history/Curves/Bicorn.html
    '''
    def __init__(self, a):
        self.a = a

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        a = self.a

        return y**2*(a**2 - x**2) - (x**2 + 2*a*y - a**2)**2

class CardioidCurve():
    '''
        http://www-gap.dcs.st-and.ac.uk/~history/Curves/Cardioid.html
        r = 2*a*(1 + cos(theta))
    '''
    def __init__(self, a):
        self.a = a

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        a = self.a
        r2 = x**2 + y**2

        return (r2- 2*a*x)**2 - 4*a**2*r2

class CartesianOvalCurve():
    '''
        http://www-gap.dcs.st-and.ac.uk/~history/Curves/Cartesian.html
    '''
    def __init__(self, a, c, m):
        self.a = a
        self.c = c
        self.m = m

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        a = self.a
        c = self.c
        m = self.m
        r2 = x**2 + y**2
        l = (1-m**2)*r2 + 2*m**2*c*x + a**2 - m**2*c**2

        return l**2 - 4*a**2*r2 

class CassinianOvalsCurve():
    '''
        http://www-gap.dcs.st-and.ac.uk/~history/Curves/Cassinian.html
    '''
    def __init__(self, a, c):
        self.a = a
        self.c = c

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        a = self.a
        c = self.c
        r2 = x**2 + y**2
        m2 = x**2 - y**2

        return r2**2 - 2*a**2*m2 + a**4 - c**2 

class FoliumCurve():
    '''
        http://www-gap.dcs.st-and.ac.uk/~history/Curves/Folium.html
        r = -b*cos(theta) + 4*a*cos(theta)*sin^2(theta)
    '''
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        a = self.a
        b = self.b
        r2 = x**2 + y**2

        return r2*(r2 + x*b) - 4*a*x*y**2

class LameCurve():
    '''
        http://www-gap.dcs.st-and.ac.uk/~history/Curves/Lame.html
        r = -b*cos(theta) + 4*a*cos(theta)*sin^2(theta)
    '''
    def __init__(self, a, b, n):
        self.a = a
        self.b = b
        self.n = n

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        a = self.a
        b = self.b
        n = self.n

        return (x/a)**n + (y/b)**n - 1 

class PearShapedCurve():
    '''
        http://www-gap.dcs.st-and.ac.uk/~history/Curves/PearShaped.html
    '''
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        a = self.a
        b = self.b

        return  b**2*y**2 - x**3*(a - x)

class SpiricSectionsCurve():
    '''
        http://www-gap.dcs.st-and.ac.uk/~history/Curves/Spiric.html
    '''
    def __init__(self, a, c, r):
        self.a = a
        self.c = c
        self.r = r

    def __call__(self, *args):
        if len(args) == 1:
            p, = args
            x = p[:, 0]
            y = p[:, 1]
        elif len(args) == 2:
            x, y = args
        else:
            raise ValueError("the args must be a N*2 or (X, Y)")

        a = self.a
        c = self.c
        r = self.r

        return (r**2 - a**2 + c**2 + x**2 + y**2)**2 - 4*r**2*(x**2 + c**2)
        

        return  b**2*y**2 - x**3*(a - x)
