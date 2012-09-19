# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
geometry_exprs.py -- time-varying geometric primitives that can know their units & coordinate system.

$Id$

About this module's filename:

I might have just called it geometry.py, but that name is taken in cad/src
(though perhaps that file deserves to be relegated to a more specific name).

==

About data representation: raw data is represented using Numeric Python arrays of convenient shape,
containing floats, or ints or longs treated the same as floats,
the same as would be commonly used in cad/src files. But I might decide to represent some
points/vectors/matrices as 4d, so that translation can be matrix multiplication too
(as in OpenGL, for example). Perhaps routines for asking for coords (or, coord systems
themselves) will come in 3d and 4d forms.

==

About style and conventions of this code:

Simpler method and attr names should access and accept self-describing objects
(e.g. Points which know their space & coordsystem, not just 3-tuples),
but for convenience should also accept raw objects (unless asked not to),
interpreting them in a coordsystem that's an attr of the base object.

Fancier method and attr names should be used to ask for raw coordinates, either in any specified
coordsystem, or by default in one known to the object (as an attr or in its env).

These objects have mutable public attrs in general, but when their attr values are arrays
of high-level objects, elementwise-mutability of those arrays
(with change tracking) may not be universal -- but it is encouraged and should be assumed
unless documented otherwise. But individual raw coordinates (e.g. x,y, and z in a Point's coords)
are *never* individually mutable or tracked.

Methods that accept numbers should always accept either
floats or ints or longs, treating ints or longs as if they were converted to floats,
but not guaranteeing to actually convert them unless necessary for correctness of arithmetic in this module.
That is, raw data saved or computed here and passed outside might in principle still contain int coordinates.
On the other hand, it's not guaranteed to, even if all inputs were ints and all computed values could have
been correctly represented as ints.

Any issue about whether mutable arrays are shared or not
needs to be documented in each case, until a general pattern emerges and can become the standard-
unless-otherwise-specified.

Watch out for the Numeric Array == bug, and for Numeric arrays being shared with other ones
(even if they are "extracted elements" from larger arrays). All methods which accept or return
Numeric arrays should try to protect naive callers from these bugs.

==

About optimization:

One useful geometric primitive is a collection of little prims of a variety of types
(points, vecs, unit vecs, dual vecs, matrices, quats, etc) (or of a single type?)
all in the same coordinate system. E.g. a point & vec array object...
then its coordinate-system-checking overhead can be handled once for the whole collection,
so it can be reasonably efficient w/o compiling. (For more general compiling, see below.)

Then any HL geometric object can be expressed as something that owns some of these geom-prim-arrays,
and maybe knows about special subsets of indices of its elements. This is sort of like a GeometricArray
or GeometricStateArray -- unless the element coords are formulas... ##e

==

About this code's future relation to externally written geometric utility libraries
(e.g. constructive solid geometry code, or Oleksander's code, or that trimesh-generating package
that Huaicai once interfaced to), and/or about expressing some of this in C, or Pyrex,
or even in Numeric Python or numarray:

- There is none of that now [070313], but someday there should be, as an important optimization.

- But the classes here are probably higher-level than will be found in any external code --
maybe in handling units & coord systems, and certainly in their Expr aspects.

- So the most basic ones might deserve direct translation into C/Pyrex, but that will require
translating an Expr framework (e.g. for inval/update)...

- And most of them should be viewed as examples of what glue code to external library functions
ought to look like, much like drawing exprs can be thought of as glue code to OpenGL.

==

About compiling as the ultimate optimization:

[###e maybe refile some of this comment into a new file about compiling or optim, even if it's a stub file]

- We're likely someday to implement compiling features which let the application programmer
use exprs to designate connected networks of objects/methods/attrs to be compiled, and which reexpress
them as glue code exprs to automatically generated C or Pyrex code, which implements the understood subset
of their state & methods in a very efficient way. In practice, many of the primitives involved would
need special purpose "compiling instructions", but the higher-level objects (defined in terms of those
primitives) often would not, nor would we need the C code we made to be itself optimized in order
to see a huge speedup from doing this. If we taught the basic OpenGL, State/StateArray, formula OpExpr,
internal Expr, instantiation, and geometric primitives how to be compiled, that would cover most code
that needs to be fast.

- That means we can think of these high-level geometric formula-bundles as if they will become compiling
instructions for geometric calculations, rather than as ever-present overhead -- since someday they will.

"""

from Numeric import dot

from geometry.VQT import planeXline
from geometry.VQT import norm
from geometry.VQT import cross
from geometry.VQT import vlen

# ==

# See also:
# demo-polygon.py
# ../VQT.py
# ../geometry.py
# ../*bond*.py has some vector math utils too

# ==

#e refile into a non-expr geom utils file? maybe even cad/src/geometry.py?
#k also I was pretty sure I already wrote this under some other name...

def project_onto_unit_vector(vec, unit): ###UNTESTED
    "project vec onto a unit-length vector unit"
    return dot(vec, unit) * unit

# ==

# line_closest_pt_to_line( p1, v1, p2, v2) -> point on line1
# line_closest_pt_params_to_line -> params of that point using p1,v1 (a single number)

class Ray: ##e (InstanceOrExpr): #k revise super to something about 3d geom. #e add coordsys/units features # not fully tested
    """Represent an infinite line, and a map from real numbers to points on it,
    by a point and vector (of any length), so that 0 and 1 map to p and p+v respectively.
    WARNING: in this initial kluge implem, p and v themselves are passed as bare 3-tuples.
    WARNING: should be an expr, but isn't yet!
    """
    #e should it be drawable? if so, is there a synonym for a non-ray line which is identical except for the draw method?
    #e and, how would its draw method know how far to draw, anyway? it might need an estimate of viewing volume...
    def __init__(self, p, v):
        self.p = p
            #### note: p and v themselves are stored as 3-tuples, and in this initial kluge implem, are also passed that way!!
            # OTOH in future we might *permit* passing them as that, even if we also permit passing fancier objects for them.
            #e But then we'll have to decide, for example, whether they can be time-varying (meaning this class is really an Instance).
            # Answer: they can be, and what we store should ultimately be able to include optimizedly-chosen methods
            # for recomputing them in our local coords! Unless that's relegated entirely to "compiling code" separate from this code...
        self.v = v
        self.params = (p, v) ##e change to a property so mutability works as expected
    def closest_pt_params_to_ray(self, ray):
        ""
        p2, v2 = ray.params # note: at first I wrote self.params() (using method not attr)
        p1, v1 = self.params
        # do some math, solve for k in p1 + k * v1 = that point (remember that the vecs can be of any length):
        # way 1: express p2-p1 as a weighted sum of v1, v2, cross(v1,v2), then take the v1 term in that sum and add it to p1.
        # way 2: There must be a NumPy function that would just do this in about one step...
        # way 3: or maybe we can mess around with dot(v1,v2) sort of like in corner_analyzer in demo_polygon...
        # way 4: or we could google for "closest points on two lines" or so...
        # way 5: or we could call it the intersection of self with the plane containing p2, and directions v2 and the cross prod,
        # and use a formula in VQT. Yes, that may not be self-contained but it's fastest to code!
        v1n = norm(v1)
        v2n = norm(v2)
        perp0 = cross(v1n, v2n)
        if vlen(perp0) < 0.01:
            ##k btw what if the lines are parallel, in what way should we fail?
            # and for that matter what if they are *almost* parallel so that we're too sensitive -- do we use an env param
            # to decide whether to fail in that case too? If we're an Instance we could do that from self.env... #e
            print "closest_pt_params_to_ray: too sensitive, returning None" ###### teach caller to handle this; let 0.01 be option
            return None
        perpn = norm(perp0)
        perpperp = cross(perpn,v2n)
        inter = planeXline(p2, perpperp, p1, v1n) # intersect plane (as plane point and normal) with line (as point and vector)
        if inter is None:
            print "inter is None (unexpected); data:",p1,v1,p2,v2,perp0
            return None
        # inter is the retval for a variant which just wants the closest point itself, i.e. closest_pt_to_ray
        return dot(inter - p1, v1n) / vlen(v1)
    def posn_from_params(self, k):
        ""
        # return a point on self whose param is k -- as a Point or a 3-tuple? how does method name say, if both can be done?
        # best answer someday: just return a Point and let it be asked for raw data if needed. Its default coordsys can be ours.
        # or maybe can be specified by self.env.
        ###k does the method name 'posn' imply we return a 3-tuple not a Point?
        if k is None:
            return None
        p1, v1 = self.params
        return p1 + k * v1
    def closest_pt_to_ray(self, ray): ### NOT USED
        ""
        k = self.closest_pt_params_to_ray(ray)
        return self.posn_from_params(k)
    def __add__(self, other):
        ##### assume other is a Numeric array vector 3-tuple -- should verify! and someday permit a Vector object too.
        p1, v1 = self.params
        return self.__class__(p1 + other, v1)
            ###REVIEW: will this work once we're an InstanceOrExpr? (p1 and/or other might be an expr then)
    pass
