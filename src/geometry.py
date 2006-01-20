# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
geometry.py -- miscellaneous purely geometric routines.

$Id$

History:

- Made by bruce 060119 from code (mostly by Josh) split out of other files.

'''
__author__ = "Josh"


# (If you think you need to import Atom, Chunk, etc, you're probably adding code to the wrong file.
#  The code here should only deal in points, not (for example) Atoms -- let the callers turn atoms
#  into their positions, generate history warnings, make up default axes based on the screen direction,
#  etc -- not the code in this file, which should remain purely geometric.)

import platform # for atom_debug
from VQT import *

def selection_polyhedron(basepos):
    """Given basepos (a Numeric array of 3d positions), compute and return [###doc the format]
    a simple bounding polyhedron, convenient for designating the approximate extent of this set of points.
    (This is used on the array of atom and open bond positions in a chunk to designate a selected chunk.)
    """
    #bruce 060119 split this out of shakedown_poly_eval_evec_axis() in chunk.py.
    # Note, it has always had some bad bugs for certain cases, like long diagonal rods.

    if not len(basepos):
        return [] # a guess
    
    # find extrema in many directions
    xtab = dot(basepos, polyXmat)
    mins = minimum.reduce(xtab) - 1.8
    maxs = maximum.reduce(xtab) + 1.8

    polyhedron = makePolyList(cat(maxs,mins))

    return polyhedron

# == helper definitions for selection_polyhedron [moved here from drawer.py by bruce 060119]

# mat mult by rowvector list and max/min reduce to find extrema
D = sqrt(2.0)/2.0
T = sqrt(3.0)/3.0
#              0  1  2  3   4  5   6  7   8  9  10  11  12
#             13 14 15 16  17 18  19 20  21 22  23  24  25
polyXmat = A([[1, 0, 0, D,  D, D,  D,  0,   0, T,  T,  T,  T],
                       [0, 1, 0, D, -D, 0,   0,  D,  D, T,  T, -T, -T],
                       [0, 0, 1, 0,  0,  D, -D,  D, -D, T, -T,  T, -T]])

del D, T

polyMat = cat(transpose(polyXmat),transpose(polyXmat))

polyTab = [( 9, (0,7,3), [3,0,5,2,7,1,3]),
           (10, (0,1,4), [3,1,8,15,6,0,3]),#(10, (0,4,1), [3,0,6,15,8,1,3]),
           (11, (8,11,7), [4,14,21,2,5,0,4]),
           (12, (8,4,9), [4,0,6,15,20,14,4]),
           (22, (5,10,9), [18,13,16,14,20,15,18]),
           (23, (10,6,11), [16,13,19,2,21,14,16]),
           (24, (1,2,5), [8,1,17,13,18,15,8]),
           (25, (3,6,2), [7,2,19,13,17,1,7])]
           #( 9, (0,7,3), [3,0,5,2,7,1,3]),
           #(10, (0,1,4), [3,1,8,15,6,0,3]),
           #(11, (8,11,7), [4,14,21,2,5,0,4]),
           #(12, (8,4,9), [4,0,6,15,20,14,4]),
           #(22, (5,10,9), [18,13,16,14,20,15,18]),
           #(23, (10,6,11), [16,13,19,2,21,14,16]),
           #(24, (1,2,5), [8,1,17,13,18,15,8]),
           #(25, (3,6,2), [7,2,19,13,17,1,7])]
           ##(22, (10,5,9), [16,13,18,15,20,14,16]), 
           #(23, (10,6,11), [16,13,19,2,21,14,16]), 
           #(24, (2, 5, 1), [17,13,18,15,8,1,17]),   
           #(25, (2,3,6), [17,1,7,2,19,13,17])]      

def planepoint(v,i,j,k):
    mat = V(polyMat[i],polyMat[j],polyMat[k])
    vec = V(v[i],v[j],v[k])
    return solve_linear_equations(mat, vec)


def makePolyList(v):
    xlines = [[],[],[],[],[],[],[],[],[],[],[],[]]
    segs = []
    for corner, edges, planes in polyTab:
        linx = []
        for i in range(3):
            l,s,r = planes[2*i:2*i+3]
            e = remainder(i+1,3)
            p1 = planepoint(v,corner,l,r)
            if abs(dot(p1,polyMat[s])) <= abs(v[s]):
                p2 = planepoint(v,l,s,r)
                linx += [p1]
                xlines[edges[i]] += [p2]
                xlines[edges[e]] += [p2]
                segs += [p1,p2]
            else:
                p1 = planepoint(v,corner,l,s)
                p2 = planepoint(v,corner,r,s)
                linx += [p1,p2]
                xlines[edges[i]] += [p1]
                xlines[edges[e]] += [p2]
        e=edges[0]
        xlines[e] = xlines[e][:-2] + [xlines[e][-1],xlines[e][-2]]
        for p1,p2 in zip(linx, linx[1:]+[linx[0]]):
            segs += [p1,p2]
    
    ctl = 12
    for lis in xlines[:ctl]:
        segs += [lis[0],lis[3],lis[1],lis[2]]

    assert type(segs) == type([]) #bruce 041119
    return segs


def trialMakePolyList(v): # [i think this is experimental code by Huaicai, never called, perhaps never tested. -- bruce 051117]
    pMat = []
    for i in range(size(v)):
        pMat += [polyMat[i] * v[i]]
    
    segs = []
    for corner, edges, planes in polyTab:
      pts = size(planes)
      for i in range(pts):
          segs += [pMat[corner], pMat[planes[i]]]
          segs += [pMat[planes[i]], pMat[planes[(i+1)%pts]]]
    
    return segs

# ==

def inertia_eigenvectors(basepos, already_centered = False):
    """Given basepos (an array of positions),
    compute and return (as a 2-tuple) the lists of eigenvalues and
    eigenvectors of the inertia tensor (computed as if all points had the same
    mass). These lists are always length 3, even for len(basepos) of 0,1, or 2,
    overlapping or colinear points, etc, though some evals will be 0 in these cases.
       Optional small speedup: if caller knows basepos is centered at the origin, it can say so.
    """
    #bruce 060119 split this out of shakedown_poly_eval_evec_axis() in chunk.py
    basepos = A(basepos) # make sure it's a Numeric array
    if not already_centered and len(basepos):
        center = add.reduce(basepos)/len(basepos)
        basepos = basepos - center
    # compute inertia tensor
    tensor = zeros((3,3),Float)
    for p in basepos:
        rsq = dot(p, p)
        m= - multiply.outer(p, p)
        m[0,0] += rsq
        m[1,1] += rsq
        m[2,2] += rsq
        tensor += m
    evals, evec = eigenvectors(tensor)
    assert len(evals) == len(evec) == 3
    return evals, evec

if 0: # self-test; works fine as of 060119
    def testie(points):
        print "ie( %r ) is %r" % ( points, inertia_eigenvectors(points) )

    map( testie, [
        [],
        [V(0,0,0)],
        [V(0,0,1)], # not centered
        [V(0,0,-1), V(0,0,1)],
        [V(0,0,-1), V(0,0,0), V(0,0,1)],
        [V(0,1,1), V(0,-1,-1), V(0,1,-1), V(0,-1,1)],
        [V(1,4,9), V(1,4,-9), V(1,-4,9), V(1,-4,-9),
         V(-1,4,9), V(-1,4,-9), V(-1,-4,9), V(-1,-4,-9)],
     ])

# ==

def unzip(pairs):
    "inverse of zip, for a list of pairs. [#e should generalize.] [#e probably there's a simple general implem - transpose?]"
    return [pair[0] for pair in pairs], [pair[1] for pair in pairs]

def compute_heuristic_axis( basepos, type,
                            evals_evec = None, already_centered = False,
                            aspect_threshhold = 0.95, numeric_threshhold = 0.0001,
                            near1 = None, near2 = None, dflt = None ):
    """Given basepos (an array of positions),
    compute and return an axis in one of various ways according to 'type' (choices are listed below),
    optionally adjusting the algorithm using aspect_threshhold (when are two dimensions close enough to count as circular),
    and numeric_threshhold (roughly, precision of coordinate values) (numeric_threshhold might be partly nim ###).
       Optional speed optimizations: if you know basepos is already_centered, you can say so;
    if (even better) you have the value of inertia_eigenvectors(basepos, already_centered = already_centered),
    you can pass that value so it doesn't have to be recomputed. (Computing it is the only way basepos is used in this routine.)
       The answer is always arbitrary in sign, so try to disambiguate it using (in order) whichever of near1, near2, and dflt
    is provided (by making it have positive dot product with the first one possible);
    but if none of those are provided and helpful (not perpendicular), return the answer with an arbitrary sign.
       If the positions require an arbitrary choice within a plane, and near1 is provided, try to choose the direction
    in that plane closest to near1; if they're all equally close (using numeric_threshhold), try near2 in the same way
    (ideally near2 should be perpendicular to near1).
       If the positions require a completely arbitrary choice, return dflt.
       Typical calls from the UI pass near1 = out of screen, near2 = up (parallel to screen), dflt = out of screen or None
    (depending on whether caller wants to detect the need to use dflt in order to print a warning). [#k guesses]
       Typical calls with no UI pass near1 = V(0,0,1), near2 = V(0,1,0), dflt = V(0,0,1).
       Choices of type (required argument) are:
    'normal' - try to return the shortest axis; if ambiguous, use near directions to choose within a plane,
       or return dflt for a blob. Works for 2 or more points; treats single point (or no points) as a blob.
       This should be used by rotary and linear motors, since they want to connect to atoms on a surface (intention as of 060119),
       and by setViewNormalTo.
    'parallel' - try to return the longest axis; otherwise like 'normal'. This should be used by setViewParallelTo.
    'chunk' - for slabs close enough to circles or squares (using aspect_threshhold), like 'normal', otherwise like 'parallel'.
       This is used for computing axes of chunks for purposes of how they interactively slide in certain UI modes.
       (Note that setViewParallelTo and setViewNormalTo, applied to a chunk or perhaps to jigs containing sets of atoms,
       should compute their own values as if applied to the same atoms, since the chunk or jig will compute its axis in
       a different way, both in choice of type argument, and in values of near1, near2, and dflt.)
    """
    #bruce 060119 split this out of shakedown_poly_eval_evec_axis() in chunk.py, added some options.
    # Could clean it up by requiring caller to pass evals_evec (no longer needing args basepos and already_centered).

    # According to tested behavior of inertia_eigenvectors, we don't need any special cases for
    # len(basepos) in [0,1,2], or points overlapping or colinear, etc!

    if evals_evec is None:
        evals_evec = inertia_eigenvectors( basepos, already_centered = already_centered)
    del basepos
    
    evals, evecs = evals_evec

    # evals[i] tells you moment of inertia when rotating around axis evec[i], which is larger if points are farther from axis.
    # So for a slab of dims 1x4x9, for axis '1' we see dims '4' and '9' and eval is the highest in that case.

    valvecs = zip(evals, evecs)
    valvecs.sort()
    
    evals, evecs = unzip(valvecs) # (custom helper function, inverse of zip in this case)
    
    assert evals[0] <= evals[1] <= evals[2]
    
    # evals[0] is now the lowest-valued evals[i] (i.e. longest axis, heuristically), evals[2] the highest.
    # (The heuristic relating this to axis-length assumes a uniform density of points
    #  over some volume or its smooth-enough surface.)

    if type == 'chunk':
        if aspect_too_close( evals[0], evals[1], aspect_threshhold ):
            # sufficiently circular-or-square pancake/disk/slab/plane
            type = 'normal' # return the axle of a wheel
        else:
            # anything else
            type = 'parallel' # return the long axis
        pass
    
    if type == 'normal':
        # we want the shortest axis == largest eval; try axis (evec) with largest eval first:
        evals.reverse()
        evecs.reverse()
    elif type == 'parallel':
        # we want longest axis == shortest eval; order is already correct
        pass
    else:
        assert 0, "unrecognized type %r" % (type,)
    
    axes = [ evecs[0] ]
    for i in [1,2]: # order of these matters, I think
        if aspect_too_close( evals[0], evals[i], aspect_threshhold ):
            axes.append( evecs[i] )

    del evals,evecs

    # len(axes) now tells us how ambiguous the answer is, and axes are the vectors to make it from.
    if len(axes) == 1:
        # we know it up to a sign.
        answer = best_sign_on_vector( axes[0], [near1, near2, dflt], numeric_threshhold )
    elif len(axes) == 2:
        # the answer is arbitrary within a plane.
        answer = best_vector_in_plane( axes, [near1, near2], numeric_threshhold )
        # (this could be None if caller didn't provide orthogonal near1 and near2)
    else:
        assert len(axes) == 3
        # the answer is completely arbitrary
        answer = dflt
    return answer # end of compute_heuristic_axis


# == helper functions for compute_heuristic_axis (likely to also be generally useful)

def aspect_too_close( dim1, dim2, aspect_threshhold ):
    "Are dim1 and dim2 (positive or zero real numbers) as close to 1:1 ratio as aspect_threshhold is to 1.0?"
    # make sure it doesn't matter whether aspect_threshhold or 1/aspect_threshhold is passed
    aspect_threshhold = float(aspect_threshhold)
    if aspect_threshhold > 1:
        aspect_threshhold = 1.0 / aspect_threshhold
    if dim2 < dim1:
        dim2, dim1 = dim1, dim2
    return dim1 >= (dim2 * aspect_threshhold)

def best_sign_on_vector(vec, goodvecs, numeric_threshhold):
    """vec is an arbitrary vector, and goodvecs is a list of unit vectors or Nones;
    return vec or - vec, whichever is more in the same direction as the first non-None goodvec
    which helps determine this (i.e. which is not perpendicular to vec, using numeric_threshhold
    to determine what's too close to call). If none of the goodvecs help, just return vec
    (this always happens if vec itself is too small).
    """
    for good in goodvecs:
        if good is not None:
            d = dot(vec, good)
            s = sign_with_threshhold(d, numeric_threshhold)
            if s:
                # it helps!
                return s * vec
    return vec

def sign_with_threshhold( num, thresh ):
    """Return -1, 0, or 1 as num is << 0, close to 0, or >> 0,
    where "close to 0" means abs(num) <= thresh.
    """
    if abs(num) <= thresh:
        return 0
    return sign(num)

def best_vector_in_plane( axes, goodvecs, numeric_threshhold ):
    """axes is a list of two orthonormal vectors defining a plane,
    and goodvecs is a list of unit vectors or Nones;
    return whichever unit vector in the plane defined by axes is closest in direction
    to the first non-None goodvec which helps determine this (i.e. which is not
    perpendicular to the plane, using numeric_threshhold to determine what's too
    close to call). If none of the goodvecs help, return None.
    """
    x,y = axes
    for good in goodvecs:
        if good is not None:
            dx = dot(x,good)
            dy = dot(y,good)
            if abs(dx) < numeric_threshhold and abs(dy) < numeric_threshhold:
                continue # good is perpendicular to the plane
            return norm(dx * x + dy * y)
    return None
    

'''
notes, 060119, probably can be removed soon:

motor axis - use 'view normal to' algorithm

chunk axis - weirdest case - ### - for 1x4x9 take 9, but for 1x9x9 take 1.

view normal to - for 1x4x9, take the short '1' dim; if answer ambiguous w/in a plane (atoms are in a sausage; aspect_threshhold?),
  prefer axis w/in that plane near the current one

view parallel to - for 1x4x9, take the long '9' dim; 
 if answer is ambiguous w/in a plane (atom plane is circular) (use aspect_threshhold to decide it's ambiguous)
 prefer an axis w/in that plane near the current one

those work fine for 2 atoms (in different posns), as if 1x1x9 slab;

for single atom or blob or 1x1x1 slab, in those cases, just return None (let caller do noop), or could return exact current axis...

so the options are:
- normal, parallel, or chunk
- aspect_threshhold 0.95
- numeric_threshhold 0.0001
'''

#end
