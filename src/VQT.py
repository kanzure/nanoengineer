"""Vectors, Quaternions, and Trackballs

Vectors are a simplified interface to the Numeric arrays.
A relatively full implementation of Quaternions.
Trackball produces incremental quaternions using a mapping of the screen
onto a sphere, tracking the cursor on the sphere.
"""

import math, types
from math import acos, sin, cos, sqrt, pi
from Numeric import *

intType = type(2)
floType = type(2.0)
numTypes = [intType, floType]

def V(*v): return array(v, Float)
def A(a):  return array(a, Float)

def cross(v1, v2):
    return V(v1[1]*v2[2] - v1[2]*v2[1],
             v1[2]*v2[0] - v1[0]*v2[2],
             v1[0]*v2[1] - v1[1]*v2[0])

def vlen(v1): return sqrt(dot(v1, v1))

def norm(v1):
    lng = vlen(v1)
    if lng: return v1 / vlen(v1)
    else: return v1+0

# p1 and p2 are points, v1 is a direction vector from p1.
# return (dist, wid) where dist is the distance from p1 to p2
#  measured in the direction of v1, and wid is the orthogonal
#  distance from p2 to the p1-v1 line.
# v1 should be a unit vector.
def orthodist(p1, v1, p2):
    dist = dot(v1, p2-p1)
    wid = vlen(p1+dist*v1-p2)
    return (dist, wid)

class Q:

    def __init__(self, x, y=None, z=None, w=None):
        # 4 numbers
        if w != None: self.vec=V(x,y,z,w)
        elif y and type(y) in numTypes:
            # axis vector and angle
            v = (x / vlen(x)) * sin(y*0.5)
            self.vec = V(cos(y*0.5), v[0], v[1], v[2])
        elif y:
            # rotation between 2 vectors
            x = norm(x)
            y = norm(y)
            v = cross(x, y)
            theta = acos(min(1.0,max(-1.0,dot(x, y))))
            if dot(y, cross(x, v)) > 0.0:
                theta = 2.0 * pi - theta
            w=cos(theta*0.5)
            if w==1.0: self.vec=V(1, 0, 0, 0)
            else:
                s=sqrt(1-w**2)/vlen(v)
                self.vec=V(w, v[0]*s, v[1]*s, v[2]*s)
        elif type(x) in numTypes:
            # just one number
            self.vec=V(1, 0, 0, 0)
        else:
            self.vec=V(x[0], x[1], x[2], x[3])
        self.counter = 50

    def __getattr__(self, name):
        if name == 'w':
            return self.vec[0]
        elif name in ('x', 'i'):
            return self.vec[1]
        elif name in ('y', 'j'):
            return self.vec[2]
        elif name in ('z', 'k'):
            return self.vec[3]
        elif name == 'angle':
            if -1.0<self.vec[0]<1.0: return 2.0*acos(self.vec[0])
            else: return 0.0
        elif name == 'axis':
            return V(self.vec[1], self.vec[2], self.vec[3])
        elif name == 'matrix3':
            self.__dict__['matrix3'] = array([\
                    [1.0 - 2.0*(self.y**2 + self.z**2),
                     2.0*(self.x*self.y - self.z*self.w),
                     2.0*(self.z*self.x + self.y*self.w)],
                    [2.0*(self.x*self.y + self.z*self.w),
                     1.0 - 2.0*(self.z**2 + self.x**2),
                     2.0*(self.y*self.z - self.x*self.w)],
                    [2.0*(self.z*self.x - self.y*self.w),
                     2.0*(self.y*self.z + self.x*self.w),
                     1.0 - 2.0 * (self.y**2 + self.x**2)]])
            return self.__dict__['matrix3']
        elif name == 'matrix4':
            self.__dict__['matrix4'] = array([\
                    [1.0 - 2.0*(self.y**2 + self.z**2),
                     2.0*(self.x*self.y - self.z*self.w),
                     2.0*(self.z*self.x + self.y*self.w),
                     0.0],
                    [2.0*(self.x*self.y + self.z*self.w),
                     1.0 - 2.0*(self.z**2 + self.x**2),
                     2.0*(self.y*self.z - self.x*self.w),
                     0.0],
                    [2.0*(self.z*self.x - self.y*self.w),
                     2.0*(self.y*self.z + self.x*self.w),
                     1.0 - 2.0 * (self.y**2 + self.x**2),
                     0.0],
                    [0.0, 0.0, 0.0, 1.0]])
            return self.__dict__['matrix4']
        else:
            raise AttributeError, 'Attribute "%s" not found' % name

    def setangle(self, theta):
        """Set the quaternion's rotation to theta (destructive modification).
        (In the same direction as before.)
        """
        theta = remainder(theta/2.0, pi)
        self.vec[1:] = norm(self.vec[1:]) * sin(theta)
        self.vec[0] = cos(theta)
        self.__reset()
        return self
        

    def __reset(self):
        if self.__dict__.has_key('matrix3'):
            del self.__dict__['matrix3']
        if self.__dict__.has_key('matrix4'):
            del self.__dict__['matrix4']


    def __setattr__(self, name, value):
        if name=="w": self.vec[0] = value
        elif name=="x": self.vec[1] = value
        elif name=="y": self.vec[2] = value
        elif name=="z": self.vec[3] = value
        else: self.__dict__[name] = value


    def __len__(self):
        return 4


    def __add__(self, q1):
        """Q + Q1 is the quaternion representing the rotation achieved
        by doing Q and then Q1.
        """
        return Q(q1.w*self.w - q1.x*self.x - q1.y*self.y - q1.z*self.z,
                 q1.w*self.x + q1.x*self.w + q1.y*self.z - q1.z*self.y,
                 q1.w*self.y - q1.x*self.z + q1.y*self.w + q1.z*self.x,
                 q1.w*self.z + q1.x*self.y - q1.y*self.x + q1.z*self.w)

    def __iadd__(self, q1):
        """this is self += q1
        """
        temp=V(q1.w*self.w - q1.x*self.x - q1.y*self.y - q1.z*self.z,
               q1.w*self.x + q1.x*self.w + q1.y*self.z - q1.z*self.y,
               q1.w*self.y - q1.x*self.z + q1.y*self.w + q1.z*self.x,
               q1.w*self.z + q1.x*self.y - q1.y*self.x + q1.z*self.w)
        self.vec=temp
        
        self.counter -= 1
        if self.counter <= 0:
            self.counter = 50
            self.normalize()
        self.__reset()

        return self

    def __sub__(self, q1):
        return self + (-q1)

    def __isub__(self, q1):
        return __iadd__(self, -q1)


    def __mul__(self, n):
        """multiplication by a scalar, i.e. Q1 * 1.3, defined so that
        e.g. Q1 * 2 == Q1 + Q1, or Q1 = Q1*0.5 + Q1*0.5
        Python syntax makes it hard to do n * Q, unfortunately.
        """
        if type(n) in numTypes:
            nq = +self
            nq.setangle(n*self.angle)
            return nq
        else:
            raise MulQuat

    def __imul__(self, q2):
        if type(n) in numTypes:
            self.setangle(n*self.angle)
            self.__reset()
            return self
        else:
            raise MulQuat



    def __div__(self, q2):
        return self*q2.conj()*(1.0/(q2*q2.conj()).w)


    def __repr__(self):
        return 'Q(%g, %g, %g, %g)' % (self.w, self.x, self.y, self.z)

    def __str__(self):
        a= "<q:%6.2f @ " % (2.0*acos(self.w)*360/pi)
        l = sqrt(self.x**2 + self.y**2 + self.z**2)
        if l:
            z=V(self.x, self.y, self.z)/l
            a += "[%4.3f, %4.3f, %4.3f] " % (z[0], z[1], z[2])
        else: a += "[%4.3f, %4.3f, %4.3f] " % (self.x, self.y, self.z)
        a += "|%8.6f|>" % vlen(self.vec)
        return a

    def __pos__(self):
        return Q(self.w, self.x, self.y, self.z)

    def __neg__(self):
        return Q(self.w, -self.x, -self.y, -self.z)

    def conj(self):
        return Q(self.w, -self.x, -self.y, -self.z)

    def normalize(self):
        w=self.vec[0]
        v=V(self.vec[1],self.vec[2],self.vec[3])
        length = vlen(v)
        if length:
            s=sqrt(1.0-w**2)/length
            self.vec = V(w, v[0]*s, v[1]*s, v[2]*s)
        else: self.vec = V(1,0,0,0)
        return self

    def rot(self,v):
        return matrixmultiply(self.matrix3,v)

# project a point from a tangent plane onto a unit sphere
def proj2sphere(x, y):
    d = sqrt(x*x + y*y)
    theta = pi * 0.5 * d
    s=sin(theta)
    if d>0.0001: return V(s*x/d, s*y/d, cos(theta))
    else: return V(0.0, 0.0, 1.0)

class Trackball:
    '''A trackball object.    The current transformation matrix
       can be retrieved using the "matrix" attribute.'''

    def __init__(self, wide, high):
        '''Create a Trackball object.
           "size" is the radius of the inner trackball
           sphere. '''
        self.w2=wide/2.0
        self.h2=high/2.0
        self.scale = 1.1 / min(wide/2.0, high/2.0)
        self.quat = Q(1,0,0,0)
        self.oldmouse = None

    def rescale(self, wide, high):
        self.w2=wide/2.0
        self.h2=high/2.0
        self.scale = 1.1 / min(wide/2.0, high/2.0)

    def start(self, px, py):
        self.oldmouse=proj2sphere((px-self.w2)*self.scale,
                                  (self.h2-py)*self.scale)

    def update(self, px, py, uq=None):
        newmouse = proj2sphere((px-self.w2)*self.scale,
                               (self.h2-py)*self.scale)
        if self.oldmouse and not uq:
            quat = Q(self.oldmouse, newmouse)
        elif self.oldmouse and uq:
            quat =  uq + Q(self.oldmouse, newmouse) - uq
        else:
            quat = Q(1,0,0,0)
        self.oldmouse = newmouse
        return quat

__author__ = "Josh"
