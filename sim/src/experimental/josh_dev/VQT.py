# Copyright 2004-2005 Nanorex, Inc.  See LICENSE file for details.
"""
VQT.py

Vectors, Quaternions, and Trackballs

Vectors are a simplified interface to the Numeric arrays.
A relatively full implementation of Quaternions.
Trackball produces incremental quaternions using a mapping of the screen
onto a sphere, tracking the cursor on the sphere.

$Id$
"""

__author__ = "Josh"

import math, types
from math import *
from Numeric import *
from LinearAlgebra import *
import platform
debug_quats = 1 #bruce 050518; I'll leave this turned on in the main sources for awhile

intType = type(2)
floType = type(2.0)
numTypes = [intType, floType]

def V(*v): return array(v, Float)
def A(a):  return array(a, Float)

def cross(v1, v2):
    #bruce 050518 comment: for int vectors, this presumably gives an int vector result
    # (which is correct, and unlikely to cause bugs even in calling code unaware of it,
    #  but ideally all calling code would be checked).
    return V(v1[1]*v2[2] - v1[2]*v2[1],
             v1[2]*v2[0] - v1[0]*v2[2],
             v1[0]*v2[1] - v1[1]*v2[0])

def vlen(v1):
    #bruce 050518 question: is vlen correct for int vectors, not only float ones?
    # In theory it should be, since sqrt works for int args and always gives float answers.
    # And is it correct for Numeric arrays of vectors? I don't know; norm is definitely not.
    return sqrt(dot(v1, v1))

def norm(v1):
    #bruce 050518 questions:
    # - Is this correct for int vectors, not only float ones?
    # In theory it should be, since vlen is always a float (see above).
    # - Is it correct for Numeric arrays of vectors (doing norm on each one alone)?
    # No... clearly the "if" makes the same choice for all of them, but even ignoring that,
    # it gives an alignment exception for any vector-array rather than working at all.
    # I don't know how hard that would be to fix.
    lng = vlen(v1)
    if lng:
        return v1 / lng
        # bruce 041012 optimized this by using lng instead of
        # recomputing vlen(v1) -- code was v1 / vlen(v1)
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

#bruce 050518 added these:
X_AXIS = V(1,0,0)
Y_AXIS = V(0,1,0)
Z_AXIS = V(0,0,1)

class Q: # by Josh; some comments and docstring revised by bruce 050518
    """Q(W, x, y, z) is the quaternion with axis vector x,y,z
    and sin(theta/2) = W
    (e.g. Q(1,0,0,0) is no rotation [used a lot])
    [Warning: the python argument names are not in the same order as in
     the usage-form above! This is not a bug, just possibly confusing.]

    Q(x, y, z) where x, y, and z are three orthonormal vectors
    is the quaternion that rotates the standard axes into that
    reference frame [this was first used, and first made correct, by bruce 050518]
    (the frame has to be right handed, or there's no quaternion that can do it!)

    Q(V(x,y,z), theta) is what you probably want [axis vector and angle]. [used widely]

    Q(vector, vector) gives the quat that rotates between them [used widely]
    [bruce 050518 asks: which such quat? presumably the one that does the least rotation in all]

    [undocumented until 050518: Q(number) gives Q(1,0,0,0) [perhaps never used, not sure];
     Q(quat) gives a copy of that quat [used fairly often];
     Q([W,x,y,z]) (for any sequence type) gives the same quat as Q(W, x, y, z)
     [used for parsing csys records, maybe in other places].]
    """
    counter = 50 # initial value of instance variable
        # [bruce 050518 moved it here, fixing bug in which it sometimes didn't get inited]
    def __init__(self, x, y=None, z=None, w=None):
        if w is not None: # 4 numbers
            # [bruce comment 050518: note than ints are not turned to floats,
            #  and no checking (of types or values) or normalization is done,
            #  and that these arg names don't correspond to their meanings,
            #  which are W,x,y,z (as documented) rather than x,y,z,w.]
            self.vec = V(x,y,z,w)

        elif z is not None: # three axis vectors
            # Just use first two
            # [bruce comments 050518:
            #  - bugfix/optim: test z for None, not for truth value
            #    (only fixes z = V(0,0,0) which is not allowed here anyway, so not very important)
            #  - This case was not used until now, and was wrong for some or all inputs
            #    (not just returning the inverse quat as I initially thought);
            #    so I fixed it.
            #  - The old code sometimes used 'z' but the new code never does
            #    (except to decide to use this case, and when debug_quats to check the results).

            # Q(x, y, z) where x, y, and z are three orthonormal vectors
            # is the quaternion that rotates the standard axes into that
            # reference frame
            ##e could have a debug check for vlen(x), y,z, and ortho and right-handed...
            # but when this is false (due to caller bugs), the check_posns_near below should catch it.
            xfixer = Q( X_AXIS, x)
            y_axis_2 = xfixer.rot(Y_AXIS)
            yfixer = twistor( x, y_axis_2, y)
            res = xfixer
            res += yfixer # warning: modifies res -- xfixer is no longer what it was
            if debug_quats:
                check_posns_near( res.rot(X_AXIS), x, "x" )
                check_posns_near( res.rot(Y_AXIS), y, "y" )
                check_posns_near( res.rot(Z_AXIS), z, "z" )
            self.vec = res.vec
            if debug_quats:
                res = self # sanity check
                check_posns_near( res.rot(X_AXIS), x, "sx" )
                check_posns_near( res.rot(Y_AXIS), y, "sy" )
                check_posns_near( res.rot(Z_AXIS), z, "sz" )
            return
##            # the old code (incorrect, and was not used):
##            a100 = V(1,0,0)
##            c1 = cross(a100,x)
##            if vlen(c1)<0.000001:
##                if debug_quats or platform.atom_debug: #bruce 050518
##                    # i suspect it's wrong, always giving a 90 degree rotation, and not setting self.counter
##                    print "debug_quats: using Q(y,z).vec case"
##                self.vec = Q(y,z).vec
##                return
##            ax1 = norm((a100+x)/2.0)
##            x2 = cross(ax1,c1)
##            a010 = V(0,1,0)
##            c2 = cross(a010,y)
##            if vlen(c2)<0.000001:
##                if debug_quats or platform.atom_debug: #bruce 050518 -- same comment as above
##                    print "debug_quats: using Q(x,z).vec case"
##                self.vec = Q(x,z).vec
##                return
##            ay1 = norm((a010+y)/2.0)
##            y2 = cross(ay1,c2)
##            axis = cross(x2, y2)
##            nw = sqrt(1.0 + x[0] + y[1] + z[2])/2.0
##            axis = norm(axis)*sqrt(1.0-nw**2)
##            self.vec = V(nw, axis[0], axis[1], axis[2])

        elif type(y) in numTypes:
            # axis vector and angle [used often]
            v = (x / vlen(x)) * sin(y*0.5)
            self.vec = V(cos(y*0.5), v[0], v[1], v[2])

        elif y is not None:
            # rotation between 2 vectors [used often]
            #bruce 050518 bugfix/optim: test y for None, not for truth value
            # (only fixes y = V(0,0,0) which is not allowed here anyway, so not very important)
            # [I didn't yet verify it does this in correct order; could do that from its use
            # in bonds.py or maybe the new indirect use in jigs.py (if I checked iadd too). ###@@@]
            #bruce 050730 bugfix: when x and y are very close to equal, original code treats them as opposite.
            # Rewriting it to fix that, though not yet in an ideal way (just returns identity).
            # Also, when they're close but not that close, original code might be numerically unstable.
            # I didn't fix that problem.
            x = norm(x)
            y = norm(y)
            dotxy = dot(x, y)
            v = cross(x, y)
            vl = vlen(v)
            if vl<0.000001:
                # x,y are very close, or very close to opposite, or one of them is zero
                if dotxy < 0:
                    # close to opposite; treat as actually opposite (same as pre-050730 code)
                    ax1 = cross(x,V(1,0,0))
                    ax2 = cross(x,V(0,1,0))
                    if vlen(ax1)>vlen(ax2):
                        self.vec = norm(V(0, ax1[0],ax1[1],ax1[2]))
                    else:
                        self.vec = norm(V(0, ax2[0],ax2[1],ax2[2]))
                else:
                    # very close, or one is zero -- we could pretend they're equal, but let's be a little
                    # more accurate than that -- vl is sin of desired theta, so vl/2 is approximately sin(theta/2)
                    # (##e could improve this further by using a better formula to relate sin(theta/2) to sin(theta)),
                    # so formula for xyz part is v/vl * vl/2 == v/2 [bruce 050730]
                    xyz = v/2.0
                    sintheta2 = vl/2.0 # sin(theta/2)
                    costheta2 = sqrt(1-sintheta2**2) # cos(theta/2)
                    self.vec = V(costheta2, xyz[0], xyz[1], xyz[2])
            else:
                # old code's method is numerically unstable if abs(dotxy) is close to 1. I didn't fix this.
                # I also didn't review this code (unchanged from old code) for correctness. [bruce 050730]
                theta = acos(min(1.0,max(-1.0,dotxy)))
                if dot(y, cross(x, v)) > 0.0:
                    theta = 2.0 * pi - theta
                w=cos(theta*0.5)
                s=sqrt(1-w**2)/vl
                self.vec=V(w, v[0]*s, v[1]*s, v[2]*s)
            pass

        elif type(x) in numTypes:
            # just one number [#k is this ever used?]
            self.vec=V(1, 0, 0, 0)

        else:
            #bruce 050518 comment: a copy of the quat x, or of any length-4 sequence [both forms are used]
            self.vec=V(x[0], x[1], x[2], x[3])
        return # from Q.__init__

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
        elif name == 'matrix':
            # this the transpose of the normal form
            # so we can use it on matrices of row vectors
            # [bruce comment 050518: there is a comment on self.vunrot()
            #  which seems to contradict the above old comment by Josh.
            #  Josh says he revised the transpose situation later than he wrote the rest,
            #  so he's not surprised if some comments (or perhaps even rarely-used
            #  code cases?? not sure) are out of date.
            #  I didn't yet investigate the true situation.
            #     To clarify the code, I'll introduce local vars w,x,y,z, mat.
            #  This will optimize it too (avoiding 42 __getattr__ calls!).
            # ]
            w, x, y, z = self.vec
            self.__dict__['matrix'] = mat = array([\
                    [1.0 - 2.0*(y**2 + z**2),
                     2.0*(x*y + z*w),
                     2.0*(z*x - y*w)],
                    [2.0*(x*y - z*w),
                     1.0 - 2.0*(z**2 + x**2),
                     2.0*(y*z + x*w)],
                    [2.0*(z*x + y*w),
                     2.0*(y*z - x*w),
                     1.0 - 2.0 * (y**2 + x**2)]])
            return mat
        else:
            raise AttributeError, 'No "%s" in Quaternion' % name

    def __getitem__(self, num):
        return self.vec[num]

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
        if self.__dict__.has_key('matrix'):
            del self.__dict__['matrix']


    def __setattr__(self, name, value):
        #bruce comment 050518: possible bug (depends on usage, unknown): this doesn't call __reset
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
        a= "<q:%6.2f @ " % (2.0*acos(self.w)*180/pi)
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

    def unrot(self,v):
        return matrixmultiply(self.matrix,v)

    def vunrot(self,v):
        # for use with row vectors
        # [bruce comment 050518: the above old comment by Josh seems to contradict
        #  the comment about 'matrix' in __getattr__ (also old and by Josh)
        #  that it's the transpose of the normal form so it can be used for row vectors.
        #  See the other comment for more info.]
        return matrixmultiply(v,transpose(self.matrix))

    def rot(self,v):
        return matrixmultiply(v,self.matrix)

def twistor(axis, pt1, pt2): #bruce 050724 revised code (should not change the result)
    """return the quaternion that, rotating around axis, will bring pt1 closest to pt2.
    """
    #bruce 050518 comment: now using this in some cases of Q.__init__; not the ones this uses!
    theta = twistor_angle(axis, pt1, pt2)
    return Q(axis, theta)

def twistor_angle(axis, pt1, pt2): #bruce 050724 split this out of twistor()
    q = Q(axis, V(0,0,1))
    pt1 = q.rot(pt1)
    pt2 = q.rot(pt2)
    a1 = atan2(pt1[1],pt1[0])
    a2 = atan2(pt2[1],pt2[0])
    theta = a2-a1
    return theta

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

def ptonline(xpt, lpt, ldr):
    """return the point on a line (point lpt, direction ldr)
    nearest to point xpt
    """
    ldr = norm(ldr)
    return dot(xpt-lpt,ldr)*ldr + lpt

def planeXline(ppt, pv, lpt, lv):
    """find the intersection of a line (point lpt, vector lv)
    with a plane (point ppt, normal pv)
    return None if (almost) parallel
    (warning to callers: retvals other than None might still be false,
     e.g. V(0,0,0) -- untested, but likely; so don't use retval as boolean)
    """
    d=dot(lv,pv)
    if abs(d)<0.000001: return None
    return lpt+lv*(dot(ppt-lpt,pv)/d)

def cat(a,b):
    """concatenate two arrays (the NumPy version is a mess)
    """
    #bruce comment 050518: these boolean tests look like bugs!
    # I bet they should be testing the number of entries being 0, or so.
    # So I added some debug code to warn us if this happens.
    if not a:
        if (debug_quats or platform.atom_debug):
            print "debug_quats: cat(a,b) with false a -- is it right?",a
        return b
    if not b:
        if (debug_quats or platform.atom_debug):
            print "debug_quats: cat(a,b) with false b -- is it right?",b
        return a
    r1 = shape(a)
    r2 = shape(b)
    if len(r1) == len(r2): return concatenate((a,b))
    if len(r1)<len(r2):
        return concatenate((reshape(a,(1,)+r1), b))
    else: return concatenate((a,reshape(b,(1,)+r2)))

def Veq(v1, v2):
    "tells if v1 is all equal to v2"
    return logical_and.reduce(v1==v2)
    #bruce comment 050518: I guess that not (v1 != v2) would also work (and be slightly faster)
    # (in principle it would work, based on my current understanding of Numeric...)

# == bruce 050518 moved the following here from extrudeMode.py (and bugfixed/docstringed them)

def floats_near(f1,f2): #bruce, circa 040924, revised 050518 to be relative, 050520 to be absolute for small numbers.
    """Say whether two floats are "near" in value (just for use in sanity-check assertions).
    """
    ## return abs( f1-f2 ) <= 0.0000001
    ## return abs( f1-f2 ) <= 0.000001 * max(abs(f1),abs(f2))
    return abs( f1-f2 ) <= 0.000001 * max( abs(f1), abs(f2), 0.1) #e maybe let callers pass a different "scale" than 0.1?

def check_floats_near(f1,f2,msg = ""): #bruce, circa 040924
    "Complain to stdout if two floats are not near; return whether they are."
    if floats_near(f1,f2):
        return True # means good (they were near)
    if msg:
        fmt = "not near (%s):" % msg
    else:
        fmt = "not near:"
    # fmt is not a format but a prefix
    print fmt,f1,f2
    return False # means bad

def check_posns_near(p1,p2,msg=""): #bruce, circa 040924
    "Complain to stdout if two length-3 float vectors are not near; return whether they are."
    res = True #bruce 050518 bugfix -- was False (which totally disabled this)
    for i in [0,1,2]:
        res = res and check_floats_near(p1[i],p2[i],msg+"[%d]"%i)
    return res

def check_quats_near(q1,q2,msg=""): #bruce, circa 040924
    "Complain to stdout if two quats are not near; return whether they are."
    res = True #bruce 050518 bugfix -- was False (which totally disabled this)
    for i in [0,1,2,3]:
        res = res and check_floats_near(q1[i],q2[i],msg+"[%d]"%i)
    return res

# end
