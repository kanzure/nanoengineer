# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
VQT.py - Vectors, Quaternions, and [no longer in this file] Trackballs

Vectors are a simplified interface to the Numeric arrays.

A relatively full implementation of Quaternions
(but note that we use the addition operator to multiply them).

@author: Josh
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

Note: bruce 071216 moved class Trackball into its own file,
so the remaining part of this module can be classified as "geometry"
(though it also contains some plain old "math").
"""

import math
from utilities import debug_flags
from foundation.state_utils import DataMixin

#update by kirka
#import Numeric 
import numpy.oldnumeric as Numeric


_DEBUG_QUATS = False
    #bruce 050518; I'll leave this turned on in the main sources for awhile
    #bruce 080401 update: good to leave this on for now, but turn it off soon
    # as an optimization -- no problems turned up so far, but the upcoming
    # PAM3+5 code is about to use it a lot more.
    #bruce 090306 turned this off

intType = type(2)
floType = type(2.0)
numTypes = [intType, floType]

def V(*v):
    return Numeric.array(v, Numeric.Float)

def A(a):
    return Numeric.array(a, Numeric.Float)

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
    return Numeric.dot(v1, v1) ** 0.5

def norm(v1):
    #bruce 050518 questions:
    # - Is this correct for int vectors, not only float ones?
    # In theory it should be, since vlen is always a float (see above).
    # - Is it correct for Numeric arrays of vectors (doing norm on each one alone)?
    # No... clearly the "if" makes the same choice for all of them, but even ignoring that,
    # it gives an alignment exception for any vector-array rather than working at all.
    # I don't know how hard that would be to fix.
    lng = Numeric.dot(v1, v1) ** 0.5
    if lng:
        return v1 / lng
        # bruce 041012 optimized this by using lng instead of
        # recomputing vlen(v1) -- code was v1 / vlen(v1)
    else:
        return v1 + 0

def angleBetween(vec1, vec2):
    """
    Return the angle between two vectors, in degrees,
    but try to cover all the weird cases where numerical
    anomalies could pop up.
    """
    # paranoid acos(dotproduct) function, wware 051103
    # [TODO: should merge with threepoint_angle_in_radians]
    TEENY = 1.0e-10
    lensq1 = Numeric.dot(vec1, vec1)
    if lensq1 < TEENY:
        return 0.0
    lensq2 = Numeric.dot(vec2, vec2)
    if lensq2 < TEENY:
        return 0.0
    
    #Replaced earlier formula "vec1 /= lensq1 ** .5" to fix the 
    #following bug:  
    #The above formula was modifying the arguments using the /= statement. 
    #Numeric.array objects (V objects) are mutable, and op= operators modify 
    #them so replacing  [--ninad 20070614 comments, based on an email 
    #conversation with Bruce where he noticed the real problem.] 
    
    vec1 = vec1 / lensq1 ** .5
    vec2 = vec2 / lensq2 ** .5
    # The case of nearly-equal vectors will be covered by the >= 1.0 clause.
    #diff = vec1 - vec2
    #if dot(diff, diff) < TEENY:
    #    return 0.0
    dprod = Numeric.dot(vec1, vec2)
    if dprod >= 1.0:
        return 0.0
    if dprod <= -1.0:
        return 180.0
    return (180 / math.pi) * math.acos(dprod)

def threepoint_angle_in_radians(p1, p2, p3):
    """
    Given three points (Numeric arrays of floats),
    return the angle p1-p2-p3 in radians.
    """
    #bruce 071030 made this from chem.atom_angle_radians.
    # TODO: It ought to be merged with angleBetween.
    # (I don't know whether that one is actually better.)
    # Also compare with def angle in jigs_motors.
    v1 = norm(p1 - p2)
    v2 = norm(p3 - p2)
    dotprod = Numeric.dot(v1, v2)
    if dotprod > 1.0:
        #bruce 050414 investigating bugs 361 and 498 (probably the same underlying bug);
        # though (btw) it would probably be better to skip this [now caller's] angle-printing entirely ###e
        # if angle obviously 0 since atoms 1 and 3 are the same.
        # This case (dotprod > 1.0) can happen due to numeric roundoff in norm();
        # e.g. I've seen this be 1.0000000000000002 (as printed by '%r').
        # If not corrected, it can make acos() return nan or have an exception!
        dotprod = 1.0
    elif dotprod < -1.0:
        dotprod = -1.0
    ang = math.acos(dotprod)
    return ang

def atom_angle_radians(atom1, atom2, atom3):
    """
    Return the angle between the positions of atom1-atom2-atom3, in radians.
    These "atoms" can be any objects with a .posn() method which returns a
    Numeric array of three floats. If these atoms are bonded, this is the
    angle between the atom2-atom1 and atom2-atom3 bonds,
    but this function does not assume they are bonded.
       Warning: current implementation is inaccurate for angles near
    0.0 or pi (0 or 180 degrees).
    """
    res = threepoint_angle_in_radians( atom1.posn(),
                                       atom2.posn(),
                                       atom3.posn() )
    return res

# p1 and p2 are points, v1 is a direction vector from p1.
# return (dist, wid) where dist is the distance from p1 to p2
#  measured in the direction of v1, and wid is the orthogonal
#  distance from p2 to the p1-v1 line.
# v1 should be a unit vector.
def orthodist(p1, v1, p2):
    dist = Numeric.dot(v1, p2 - p1)
    wid = vlen(p1 + dist * v1 - p2)
    return (dist, wid)

#bruce 050518 added these:
X_AXIS = V(1, 0, 0)
Y_AXIS = V(0, 1, 0)
Z_AXIS = V(0, 0, 1)

# ==

class Q(DataMixin):
    """
    Quaternion class. Many constructor forms:
    
    Q(W, x, y, z) is the quaternion with axis vector x,y,z
    and cos(theta/2) = W
    (e.g. Q(1,0,0,0) is no rotation [used a lot])
    [Warning: the python argument names are not in the same order as in
     the usage-form above! This is not a bug, just possibly confusing.]
    
    Q(x, y, z), where x, y, and z are three orthonormal vectors describing a
    right-handed coordinate frame, is the quaternion that rotates the standard
    axes into that reference frame (the frame has to be right handed, or there's
    no quaternion that can do it!)
    
    Q(V(x,y,z), theta) is what you probably want [axis vector and angle]. [used widely]
    #doc -- units of theta? (guess: radians)
    
    Q(vector, vector) gives the quat that rotates between them [used widely]
    [which such quat? presumably the one that does the least rotation in all]
    
    [remaining forms were undocumented until 050518:]

    Q(number) gives Q(1,0,0,0) [perhaps never used, not sure]
    
    Q(quat) gives a copy of that quat [used fairly often]
    
    Q([W,x,y,z]) (for any sequence type) gives the same quat as Q(W, x, y, z)
     [used for parsing csys records, maybe in other places].

    @warning: These quaternion objects use "+" for multiply and
              "*" for exponentiation, relative to "textbook" quaternions.
              This is not a bug, but might cause confusion if not understood,
              especially when making use of external reference info about
              quaternions.
    """
    # History:
    # class by Josh.
    # bruce 050518 revised and extended docstring, revised some comments,
    # and fixed some bugs:
    # - added first use of constructor form "Q(x, y, z) where x, y, and z are
    #   three orthonormal vectors", and bugfixed it (it had never worked before)
    # - other fixes listed below
    # a few other bugfixes since then, and new features for copy_val
    # manoj fixed a typo in the docstring, sin -> cos
    # bruce 080401 revised docstring, added warning about 'use "+" for multiply'
    #  (issue was pointed out long ago by wware)
    counter = 50 # initial value of instance variable
        # [bruce 050518 moved it here, fixing bug in which it sometimes didn't get inited]
    def __init__(self, x, y = None, z = None, w = None):
        if w is not None: # 4 numbers
            # [bruce comment 050518: note than ints are not turned to floats,
            #  and no checking (of types or values) or normalization is done,
            #  and that these arg names don't correspond to their meanings,
            #  which are W,x,y,z (as documented) rather than x,y,z,w.]
            self.vec = V(x, y, z, w)
        
        elif z is not None: # three axis vectors
            # Just use first two
            # [bruce comments 050518:
            #  - bugfix/optim: test z for None, not for truth value
            #    (only fixes z = V(0,0,0) which is not allowed here anyway, so not very important)
            #  - This case was not used until now, and was wrong for some or all inputs
            #    (not just returning the inverse quat as I initially thought);
            #    so I fixed it.
            #  - The old code sometimes used 'z' but the new code never does
            #    (except to decide to use this case, and when _DEBUG_QUATS to check the results).
            
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
            if _DEBUG_QUATS:
                check_posns_near( res.rot(X_AXIS), x, "x" )
                check_posns_near( res.rot(Y_AXIS), y, "y" )
                check_posns_near( res.rot(Z_AXIS), z, "z" )
            self.vec = res.vec
            if _DEBUG_QUATS:
                res = self # sanity check
                check_posns_near( res.rot(X_AXIS), x, "sx" )
                check_posns_near( res.rot(Y_AXIS), y, "sy" )
                check_posns_near( res.rot(Z_AXIS), z, "sz" )
            return
            # old code (incorrect and i think never called) commented out long ago, removed in rev. 1.27 [bruce 060228]
            
        elif type(y) in numTypes:
            # axis vector and angle [used often]
            v = (x / vlen(x)) * Numeric.sin(y * 0.5)
            self.vec = V(Numeric.cos(y * 0.5), v[0], v[1], v[2])
            
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
            dotxy = Numeric.dot(x, y)
            v = cross(x, y)
            vl = Numeric.dot(v, v) ** .5
            if vl<0.000001:
                # x, y are very close, or very close to opposite, or one of them is zero
                if dotxy < 0:
                    # close to opposite; treat as actually opposite (same as pre-050730 code)
                    ax1 = cross(x, V(1, 0, 0))
                    ax2 = cross(x, V(0, 1, 0))
                    if vlen(ax1)>vlen(ax2):
                        self.vec = norm(V(0, ax1[0],ax1[1],ax1[2]))
                    else:
                        self.vec = norm(V(0, ax2[0],ax2[1],ax2[2]))
                else:
                    # very close, or one is zero -- we could pretend they're equal, but let's be a little
                    # more accurate than that -- vl is sin of desired theta, so vl/2 is approximately sin(theta/2)
                    # (##e could improve this further by using a better formula to relate sin(theta/2) to sin(theta)),
                    # so formula for xyz part is v/vl * vl/2 == v/2 [bruce 050730]
                    xyz = v / 2.0
                    sintheta2 = vl / 2.0 # sin(theta/2)
                    costheta2 = (1 - sintheta2**2) ** .5 # cos(theta/2)
                    self.vec = V(costheta2, xyz[0], xyz[1], xyz[2])
            else:
                # old code's method is numerically unstable if abs(dotxy) is close to 1. I didn't fix this.
                # I also didn't review this code (unchanged from old code) for correctness. [bruce 050730]
                theta = math.acos(min(1.0, max(-1.0, dotxy)))
                if Numeric.dot(y, cross(x, v)) > 0.0:
                    theta = 2.0 * math.pi - theta
                w = Numeric.cos(theta * 0.5)
                s = ((1 - w**2)**.5) / vl
                self.vec = V(w, v[0]*s, v[1]*s, v[2]*s)
            pass
        
        elif type(x) in numTypes:
            # just one number [#k is this ever used?]
            self.vec = V(1, 0, 0, 0)
        
        else:
            #bruce 050518 comment: a copy of the quat x, or of any length-4 sequence [both forms are used]
            self.vec = V(x[0], x[1], x[2], x[3])
        return # from Q.__init__
    
    def __getattr__(self, attr): # in class Q
        if attr.startswith('_'):
            raise AttributeError, attr #bruce 060228 optim (also done at end)
        if attr == 'w':
            return self.vec[0]
        elif attr in ('x', 'i'):
            return self.vec[1]
        elif attr in ('y', 'j'):
            return self.vec[2]
        elif attr in ('z', 'k'):
            return self.vec[3]
        elif attr == 'angle':
            if -1.0 < self.vec[0] < 1.0:
                return 2.0 * math.acos(self.vec[0])
            else:
                return 0.0
        elif attr == 'axis':
            return V(self.vec[1], self.vec[2], self.vec[3])
        elif attr == 'matrix':
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
            self.__dict__['matrix'] = mat = Numeric.array([
                    [1.0 - 2.0 * (y**2 + z**2),
                     2.0 * (x*y + z*w),
                     2.0 * (z*x - y*w)],
                    [2.0 * (x*y - z*w),
                     1.0 - 2.0 * (z**2 + x**2),
                     2.0 * (y*z + x*w)],
                    [2.0 * (z*x + y*w),
                     2.0 * (y*z - x*w),
                     1.0 - 2.0 * (y**2 + x**2)]])
            return mat
        raise AttributeError, 'No %r in Quaternion' % (attr,)

    #bruce 060209 defining __eq__ and __ne__ for efficient state comparisons
    # given presence of __getattr__ (desirable for Undo).
    # (I don't think it needs a __nonzero__ method, and if it had one 
    # I don't know if Q(1,0,0,0) should be False or True.)
    #bruce 060222 note that it also now needs __eq__ and __ne__ to be 
    # compatible with its _copyOfObject (they are).
    # later, __ne__ no longer needed since defined in DataMixin.

    # override abstract method of DataMixin
    def _copyOfObject(self): 
        #bruce 051003, for use by state_utils.copy_val (in class Q)
        return self.__class__(self)
    
    # override abstract method of DataMixin
    def __eq__(self, other): #bruce 070227 revised this
        try:
            if self.__class__ is not other.__class__:
                return False
        except AttributeError:
            # some objects have no __class__ (e.g. Numeric arrays)
            return False
        return not (self.vec.any() != other.vec.any()) # assumes all quats have .vec; true except for bugs
            #bruce 070227 fixed "Numeric array == bug" encountered by this line (when it said "self.vec == other.vec"),
            # which made Q(1, 0, 0, 0) == Q(0.877583, 0.287655, 0.38354, 0) (since they're equal in at least one component)!!
            # Apparently it was my own bug, since it says above that I wrote this method on 060209.
        pass
        
    def __getitem__(self, num):
        return self.vec[num]

    def setangle(self, theta):
        """
        Set the quaternion's rotation to theta (destructive modification).
        (In the same direction as before.)
        """
        theta = Numeric.remainder(theta / 2.0, math.pi)
        self.vec[1:] = norm(self.vec[1:]) * Numeric.sin(theta)
        self.vec[0] = Numeric.cos(theta)
        self.__reset()
        return self

    def __reset(self):
        if self.__dict__.has_key('matrix'):
            del self.__dict__['matrix']

    def __setattr__(self, attr, value):
        #bruce comment 050518:
        # - possible bug (depends on usage, unknown): this doesn't call __reset
        #bruce comments 080417:
        # - note that the x,y,z used here are *not* the same as the ones
        #   that would normally be passed to the constructor form Q(W, x, y, z).
        # - it is likely that this is never used (though it is often called).
        # - the existence of this method might be a significant slowdown,
        #   because it runs (uselessly) every time methods in this class
        #   set any attributes of self, such as vec or counter.
        #   If we can determine that it is never used, we should remove it.
        #   Alternatively we could reimplement it using properties of a
        #   new-style class.
        if attr == "w":
            self.vec[0] = value
        elif attr == "x":
            self.vec[1] = value
        elif attr == "y":
            self.vec[2] = value
        elif attr == "z":
            self.vec[3] = value
        else:
            self.__dict__[attr] = value

    def __len__(self):
        return 4

    def __add__(self, q1): # TODO: optimize using self.vec, q1.vec
        """
        Q + Q1 is the quaternion representing the rotation achieved
        by doing Q and then Q1.
        """
        return Q(q1.w*self.w - q1.x*self.x - q1.y*self.y - q1.z*self.z,
                 q1.w*self.x + q1.x*self.w + q1.y*self.z - q1.z*self.y,
                 q1.w*self.y - q1.x*self.z + q1.y*self.w + q1.z*self.x,
                 q1.w*self.z + q1.x*self.y - q1.y*self.x + q1.z*self.w)

    def __iadd__(self, q1): # TODO: optimize using self.vec, q1.vec
        """
        this is self += q1
        """
        temp = V(q1.w*self.w - q1.x*self.x - q1.y*self.y - q1.z*self.z,
                 q1.w*self.x + q1.x*self.w + q1.y*self.z - q1.z*self.y,
                 q1.w*self.y - q1.x*self.z + q1.y*self.w + q1.z*self.x,
                 q1.w*self.z + q1.x*self.y - q1.y*self.x + q1.z*self.w)
        self.vec = temp
        
        self.counter -= 1
        if self.counter <= 0:
            self.counter = 50
            self.normalize()
        self.__reset()

        return self

    def __sub__(self, q1):
        return self + (-q1)

    def __isub__(self, q1):
        return self.__iadd__(-q1)

    def __mul__(self, n):
        """
        multiplication by a scalar, i.e. Q1 * 1.3, defined so that
        e.g. Q1 * 2 == Q1 + Q1, or Q1 = Q1 * 0.5 + Q1 * 0.5
        Python syntax makes it hard to do n * Q, unfortunately.
        """
        # review: couldn't __rmul__ be used to do n * Q? in theory yes,
        # but was some other problem referred to, e.g. in precedence? I don't know. [bruce 070227 comment]
        # [update, bruce 071216: I think n * Q has been found to work by test -- not sure.
        # Maybe Python now uses this def to do it?]
        if type(n) in numTypes:
            nq = + self # scalar '+' to copy self
            nq.setangle(n * self.angle)
            return nq
        else:
            raise ValueError, "can't multiply %r by %r" % (self, n) #bruce 070619 revised this (untested)

    def __imul__(self, n):
        #bruce 051107 bugfix (untested): replace arg q2 with n, since body used n (old code must have never been tested either)
        if type(n) in numTypes:
            self.setangle(n * self.angle)
            self.__reset()
            return self
        else:
            raise ValueError, "can't multiply %r by %r" % (self, n) #bruce 070619 revised this (untested)

    def __div__(self, q2):
        """
        Return this quat divided by a number, or (untested, might not work) another quat.
        """
        #bruce 051107: revised docstring. permit q2 to be a number (new feature).
        # Warning: the old code (for q2 a quat) is suspicious, since it appears to multiply two quats,
        # but that multiplication is not presently implemented, if I understand the __mul__ implem above!
        # This should be analyzed and cleaned up.
        if type(q2) in numTypes:
            #bruce 051107 new feature
            return self * (1.0 / q2)
        # old code (looks like it never could have worked, but this is not verified [bruce 051107]):
        return self * q2.conj()*(1.0/(q2 * q2.conj()).w)

    def __repr__(self):
        return 'Q(%g, %g, %g, %g)' % (self.w, self.x, self.y, self.z)

    def __str__(self):
        a= "<q:%6.2f @ " % (2.0 * math.acos(self.w) * 180 / math.pi)
        l = Numeric.sqrt(self.x**2 + self.y**2 + self.z**2)
        if l:
            z = V(self.x, self.y, self.z) / l
            a += "[%4.3f, %4.3f, %4.3f] " % (z[0], z[1], z[2])
        else:
            a += "[%4.3f, %4.3f, %4.3f] " % (self.x, self.y, self.z)
        a += "|%8.6f|>" % vlen(self.vec)
        return a

    def __pos__(self):
        ## return Q(self.w, self.x, self.y, self.z)
        # [optimized by bruce 090306, not carefully tested]
        return Q(self.vec)

    def __neg__(self):
        return Q(self.w, -self.x, -self.y, -self.z)

    def conj(self):
        return Q(self.w, -self.x, -self.y, -self.z)

    def normalize(self):
        w = self.vec[0]
        v = V(self.vec[1],self.vec[2],self.vec[3])
        length = Numeric.dot(v, v) ** .5
        if length:
            s = ((1.0 - w**2)**0.5) / length
            self.vec = V(w, v[0]*s, v[1]*s, v[2]*s)
        else:
            self.vec = V(1, 0, 0, 0)
        return self

    def unrot(self, v):
        return Numeric.matrixmultiply(self.matrix, v)

    def vunrot(self, v):
        # for use with row vectors
        # [bruce comment 050518: the above old comment by Josh seems to contradict
        #  the comment about 'matrix' in __getattr__ (also old and by Josh)
        #  that it's the transpose of the normal form so it can be used for row vectors.
        #  See the other comment for more info.]
        return Numeric.matrixmultiply(v, Numeric.transpose(self.matrix))

    def rot(self, v):
        return Numeric.matrixmultiply(v, self.matrix)

    pass # end of class Q

# ==

def twistor(axis, pt1, pt2): #bruce 050724 revised code (should not change the result)
    """
    Return the quaternion that, rotating around axis, will bring pt1 closest to pt2.
    """
    #bruce 050518 comment: now using this in some cases of Q.__init__; not the ones this uses!
    theta = twistor_angle(axis, pt1, pt2)
    return Q(axis, theta)

def twistor_angle(axis, pt1, pt2): #bruce 050724 split this out of twistor()
    q = Q(axis, V(0, 0, 1))
    pt1 = q.rot(pt1)
    pt2 = q.rot(pt2)
    a1 = math.atan2(pt1[1],pt1[0])
    a2 = math.atan2(pt2[1],pt2[0])
    theta = a2 - a1
    return theta

def proj2sphere(x, y):
    """
    project a point from a tangent plane onto a unit sphere
    """
    d = (x*x + y*y) ** .5
    theta = math.pi * 0.5 * d
    s = Numeric.sin(theta)
    if d > 0.0001:
        return V(s*x/d, s*y/d, Numeric.cos(theta))
    else:
        return V(0.0, 0.0, 1.0)

def ptonline(xpt, lpt, ldr):
    """
    return the point on a line (point lpt, direction ldr)
    nearest to point xpt
    """
    ldr = norm(ldr)
    return Numeric.dot(xpt - lpt, ldr) * ldr + lpt

def planeXline(ppt, pv, lpt, lv):
    """
    Find the intersection of a line (point lpt on line, unit vector lv along line)
    with a plane (point ppt on plane, unit vector pv perpendicular to plane).
    Return the intersection point, or None if the line and plane are (almost) parallel.
       WARNING: don't use a boolean test on the return value, since V(0,0,0) is a real point
    but has boolean value False. Use "point is not None" instead.
    """
    d = Numeric.dot(lv, pv)
    if abs(d) < 0.000001:
        return None
    return lpt + lv * (Numeric.dot(ppt - lpt, pv) / d)

def cat(a, b):
    """
    concatenate two arrays (the Numeric Python version is a mess)
    """
    #bruce comment 050518: these boolean tests look like bugs!
    # I bet they should be testing the number of entries being 0, or so.
    # So I added some debug code to warn us if this happens.
    if not a.any():
        if (_DEBUG_QUATS or debug_flags.atom_debug):
            print "_DEBUG_QUATS: cat(a, b) with false a -- is it right?", a
        return b
    if not b.any():
        if (_DEBUG_QUATS or debug_flags.atom_debug):
            print "_DEBUG_QUATS: cat(a, b) with false b -- is it right?", b
        return a
    r1 = Numeric.shape(a)
    r2 = Numeric.shape(b)
    if len(r1) == len(r2):
        return Numeric.concatenate((a, b))
    if len(r1) < len(r2):
        return Numeric.concatenate((Numeric.reshape(a,(1,) + r1), b))
    else:
        return Numeric.concatenate((a, Numeric.reshape(b,(1,) + r2)))

def Veq(v1, v2):
    """
    tells if v1 is all equal to v2
    """
    return Numeric.logical_and.reduce(v1 == v2)
    #bruce comment 050518: I guess that not (v1 != v2) would also work (and be slightly faster)
    # (in principle it would work, based on my current understanding of Numeric...)

# == bruce 050518 moved the following here from extrudeMode.py (and bugfixed/docstringed them)
    
def floats_near(f1, f2): #bruce, circa 040924, revised 050518 to be relative, 050520 to be absolute for small numbers.
    """
    Say whether two floats are "near" in value (just for use in sanity-check assertions).
    """
    ## return abs( f1 - f2 ) <= 0.0000001
    ## return abs( f1 - f2 ) <= 0.000001 * max(abs(f1),abs(f2))
    return abs( f1 - f2 ) <= 0.000001 * max( abs(f1), abs(f2), 0.1) #e maybe let callers pass a different "scale" than 0.1?

def check_floats_near(f1, f2, msg = ""): #bruce, circa 040924
    """
    Complain to stdout if two floats are not near; return whether they are.
    """
    if floats_near(f1, f2):
        return True # means good (they were near)
    if msg:
        fmt = "not near (%s):" % msg
    else:
        fmt = "not near:"
    # fmt is not a format but a prefix
    print fmt, f1, f2
    return False # means bad

def check_posns_near(p1, p2, msg=""): #bruce, circa 040924
    """
    Complain to stdout if two length-3 float vectors are not near; return whether they are.
    """
    res = True #bruce 050518 bugfix -- was False (which totally disabled this)
    for i in [0, 1, 2]:
        res = res and check_floats_near(p1[i],p2[i],msg+"[%d]"%i)
    return res

def check_quats_near(q1, q2, msg=""): #bruce, circa 040924
    """
    Complain to stdout if two quats are not near; return whether they are.
    """
    res = True #bruce 050518 bugfix -- was False (which totally disabled this)
    for i in [0, 1, 2, 3]:
        res = res and check_floats_near(q1[i],q2[i],msg+"[%d]"%i)
    return res


# == test code [bruce 070227]

if __name__ == '__main__':
    print "tests started"
    q1 = Q(1, 0, 0, 0)
    print q1, `q1`
    q2 = Q(V(0.6, 0.8, 0), 1)
    print q2, `q2`
    assert not (q1 == q2), "different quats equal!" # this bug was fixed on 070227
    assert q1 != V(0, 0, 0) # this did print_compact_traceback after that was fixed; now that's fixed too
    # can't work yet: assert q2 * 2 == 2 * q2

    # this means you have to run this from cad/src as ./ExecSubDir.py geometry/VQT.py
    from utilities.Comparison import same_vals
    q3 = Q(1, 0, 0, 0)
    assert same_vals( q1, q3 ), "BUG: not same_vals( Q(1,0,0,0), Q(1,0,0,0) )"
    print "tests done"
    
# end
