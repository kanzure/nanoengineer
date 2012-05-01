# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
shape_vertices.py - Geometric constructions of vertex lists used
                    by the drawing functions.

This includes vertices for the shapes of primitives that will go into display
lists in the setup_drawer function in setup_draw.py .

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

Originated by Josh as drawer.py .

Various developers extended it since then.

Brad G. added ColorSorter features.

At some point Bruce partly cleaned up the use of display lists.

071030 bruce split some functions and globals into draw_grid_lines.py
and removed some obsolete functions.

080210 russ Split the single display-list into two second-level lists (with and
without color) and a set of per-color sublists so selection and hover-highlight
can over-ride Chunk base colors.  ColorSortedDisplayList is now a class in the
parent's displist attr to keep track of all that stuff.

080311 piotr Added a "drawpolycone_multicolor" function for drawing polycone
tubes with per-vertex colors (necessary for DNA display style)

080313 russ Added triangle-strip icosa-sphere constructor, "getSphereTriStrips".

080420 piotr Solved highlighting and selection problems for multi-colored
objects (e.g. rainbow colored DNA structures).

080519 russ pulled the globals into a drawing_globals module and broke drawer.py
into 10 smaller chunks: glprefs.py setup_draw.py shape_vertices.py
ColorSorter.py CS_workers.py c_renderer.py CS_draw_primitives.py drawers.py
gl_lighting.py gl_buffers.py
"""

# the imports from math vs. Numeric are as discovered in existing code
# as of 2007/06/25.  It's not clear why acos is coming from math...
from math import atan2
from numpy import sin, cos, sqrt, pi
degreesPerRadian = 180.0 / pi

from geometry.VQT import norm, vlen, V, Q, A
from utilities.constants import DIAMOND_BOND_LENGTH
import graphics.drawing.drawing_globals as drawing_globals
    # REVIEW: probably we should refactor so we don't depend on assignments
    # into drawing_globals as a side effect of importing this module.
    # [bruce 081001 comment]

def init_icos():
    global icosa, icosix

    # the golden ratio
    global phi
    phi = (1.0+sqrt(5.0))/2.0
    vert = norm(V(phi,0,1))
    a = vert[0]
    b = vert[1]
    c = vert[2]

    # vertices of an icosahedron
    icosa = ((-a,b,c), (b,c,-a), (b,c,a), (a,b,-c), (-c,-a,b), (-c,a,b),
             (b,-c,a), (c,a,b), (b,-c,-a), (a,b,c), (c,-a,b), (-a,b,-c))
    icosix = ((9, 2, 6), (1, 11, 5), (11, 1, 8), (0, 11, 4), (3, 1, 7),
              (3, 8, 1), (9, 3, 7), (0, 6, 2), (4, 10, 6), (1, 5, 7),
              (7, 5, 2), (8, 3, 10), (4, 11, 8), (9, 7, 2), (10, 9, 6),
              (0, 5, 11), (0, 2, 5), (8, 10, 4), (3, 9, 10), (6, 0, 4))
    return
init_icos()

# generate geodesic spheres by subdividing the faces of an icosahedron
# recursively:
#          /\              /\
#         /  \            /  \
#        /    \          /____\
#       /      \   =>   /\    /\
#      /        \      /  \  /  \
#     /__________\    /____\/____\
#
# and normalizing the resulting vectors to the surface of a sphere

def subdivide(tri,deep):
    if deep:
        a = tri[0]
        b = tri[1]
        c = tri[2]
        a1 = norm(A(tri[0]))
        b1 = norm(A(tri[1]))
        c1 = norm(A(tri[2]))
        d = tuple(norm(a1+b1))
        e = tuple(norm(b1+c1))
        f = tuple(norm(c1+a1))
        return subdivide((a,d,f), deep-1) + subdivide((d,e,f), deep-1) +\
               subdivide((d,b,e), deep-1) + subdivide((f,e,c), deep-1)
    else: return [tri]

## Get the specific detail level of triangles approximation of a sphere 
def getSphereTriangles(level):
    ocdec = []
    for i in icosix:
        ocdec += subdivide((icosa[i[0]],icosa[i[1]],icosa[i[2]]),level)
    return ocdec

# ==

# Instead of the above recursive scheme that orients the icosahedron with the
# midpoints of six edges perpendicular to the major axes, use a ring approach
# to make subdivided icosa-spheres for Triangle Strips.  The vertices are
# grouped in rings from the North Pole to the South Pole.  Each strip zig-zags
# between two rings, and the poles are surrounded by pentagonal Triangle Fans.
#
# ----------------
#
# The pattern of five-fold vertices in a "twisted orange-slice" segment
# covering one-fifth of the icosahedron is:
#
#               ... [3,0] ... (North Pole)
#                   / | \
#                 /   |  ...
#               /     |
#       ... [2,1]---[2,0] ...
#            / \     / \
#         ...   \   /   \  ...
#                \ /     \ /
#           ... [1,1]---[1,0] ...
#                 |     /
#             ... |   /
#               \ | /
#           ... [0,0] ...     (South Pole)
#
# ----------------
#
# Higher subdivision levels step the strip verts along the icos edges,
# interpolating intermediate points on the icos and projecting each onto the
# sphere.  Note: sphere vertex normals are the same as their coords.
#
#    The "*"s show approximate vertex locations at each subdivision level.
#    Bands are numbered from South to North.  (Reason explained below.)
#    Sub-band numbers are in angle-brackets, "<>".
#
#    Level 0   [3*0]      Level 1   [6*0]         Level 2  [12*0] _<3>
#              / |       (2 steps)  / |  <1>     (4 steps)  *-*   _<2>
#  Band 2    /   |                * - *                   *-*-*   _<1>
#          /     |              / | / |  <0>            *-*-*-*   _<0>
#      [2*1]- -[2*0]   =>   [4*2]-*-[4*0]     =>    [8*4]***[8*0] _<3>
#         \     / \            \ / \ / \  <1>          *-*-*-*-*  _<2>
#  Band 1  \   /   \            * - * - *               *-*-*-*-* _<1>
#           \ /     \            \ / \ / \  <0>           *-*-*-*-* _<0>
#          [1*1]---[1*0]        [2*2]-*-[2*0]            [4*4]***[4*0]_<3>
#            |     /              | \ | /  <1>             *-*-*-* _<2>
#  Band 0    |   /                * - *                    *-*-* _<1>
#            | /                  | /  <0>                 *-* _<0>
#          [0*0]                [0*0]                    [0*0]
#
# ----------------
#
# The reason for rotating east, then going west along the latitude lines, is
# that the "grain" of triangle strip diagonals runs that way in the middle
# band of the icos:
#
#     Triangle Strip triangles
#
#        6 ----- 4 ----- 2
#         \5,4,6/ \3,2,4/ \
#     ...  \   /   \   /   \
#           \ /3,4,5\ /1,2,3\
#            5 ----- 3 ----- 1  <- Vertex order
#
# This draws triangles 1-2-3, 3-2-4, 3-4-5, and 5-4-6, all counter-clockwise
# so the normal directions don't flip-flop.
#
# ----------------
#
# This version optimizes by concatenating vertices for separate Triangle Fan
# and Triangle Strip calls into a single long Triangle Strip to minimize calls.
#
# In the "pentagon cap" band at the top of the icos, points 2, 4, and 6 in the
# above example are collapsed to the North Pole; at the bottom, points 1, 3,
# and 5 are collapsed to the South Pole.  This makes "null triangles" with one
# zero-length edge, and the other two edges echoing one of the other triangle
# edges (5,4,6 and 3,2,4 at the top, and 3,4,5 and 1,2,3 at the bottom.)
#
# In the subdivided caps, the icosahedron bands are split into horizontal
# sub-bands.  In the tapering-in sub-bands in the North cap, there is one less
# vertex on the top edges of sub-bands, so we collapse the *LAST* triangle
# there (e.g. 5,4,6 above)  On the bottom edges of the South cap bands there
# is one less vertex, so we collapse the *FIRST* triangle (e.g. 1,2,3.)
#
# Similarly, moving from the end of each sub-band to the beginning of the next
# requires a *pair* of null triangles.  We get that by simply concatenating the
# wrapped triangle strips.  We orient point pairs in the triangle strip from
# south to north, so this works as long as we jog northward between (sub-)bands.
# This is the reason we start the Triangle Strip with the South Pole band.
#
def getSphereTriStrips(level):
    steps = 2**level
    points = []                         # Triangle Strip vertices o be returned.

    # Construct an icosahedron with two vertices at the North and South Poles,
    # +-1 on the Y axis, as you look toward the X-Y plane with the Z axis
    # pointing out at you.  The "middle ring" vertices are all at the same
    # +-latitudes, on the intersection circles of the globe with a polar-axis
    # cylinder of the proper radius.
    #
    # The third "master vertex" of the icosahedron is placed on the X-Y plane,
    # which intersects the globe at the Greenwich Meridian (the semi-circle at
    # longitude 0, through Greenwich Observatory, 5 miles south-east of London.)
    #
    # The X (distance from the polar axis) and Y (height above the equatorial
    # plane) of the master vertex make a "golden rectangle", one unit high by
    # "phi" (1.6180339887498949) wide.  We normalize this to put it on the
    # unit-radius sphere, and take the distance from the axis as the cylinder
    # radius used to generate the rest of the vertices of the two middle rings.
    #
    # Plotted on the globe, the master vertex (first vertex of the North ring)
    # is lat-long 31.72,0 due south of London in Africa, about 45 miles
    # south-southwest of Benoud, Algeria.  The first vertex of the south ring is
    # rotated 1/10 of a circle east, at lat-long -31.72,36 in the south end of
    # the Indian Ocean, about 350 miles east-southeast of Durban, South Africa.
    #
    vert0 = norm(V(phi,1,0))   # Project the "master vertex" onto a unit sphere.
    cylRad = vert0[0]          # Icos vertex distance from the Y axis.
    ringLat = atan2(vert0[1], vert0[0]) * degreesPerRadian  # Latitude +-31.72 .

    # Basic triangle-strip icosahedron vertices.  Start and end with the Poles.
    # Reflect the master vertex into the southern hemisphere and rotate 5 copies
    # to make the middle rings of 5 vertices at North and South latitudes.
    p2_5 = 2*pi / 5.0
    # Simplify indexing by replicating the Poles, so everything is in fives.
    icosRings = [ 5 * [V(0.0, -1.0, 0.0)], # South Pole.

                  # South ring, first edge *centered on* the Greenwich Meridian.
                  [V(cylRad*cos((i-.5)*p2_5),-vert0[1], cylRad*sin((i-.5)*p2_5))
                   for i in range(5)],

                  # North ring, first vertex *on* the Greenwich Meridian.
                  [V(cylRad*cos(i*p2_5 ), vert0[1], cylRad*sin(i*p2_5))
                   for i in range(5)],

                  5 * [V(0.0, 1.0, 0.0)] ] # North Pole.


    # Three bands, going from bottom to top (South to North.)
    for band in range(3):
        lowerRing = icosRings[band]
        upperRing = icosRings[band+1]

        # Subdivide bands into sub-bands.  When level == 0, steps == 1,
        # subBand == 0, and we get just the icosahedron out.  (Really!)
        for subBand in range(steps):

            # Account for the tapering-in at the poles, making less points on
            # one edge of a sub-band than there are on the other edge.
            botOffset = 0
            if band is 0:      # South.
                botSteps = max(subBand, 1) # Don't divide by zero.
                topSteps = subBand + 1
                # Collapse the *first* triangle of south sub-band bottom edges.
                botOffset = -1
            elif band is 1:    # Middle.
                botSteps = topSteps = steps
            else:              # band is 2: North.
                botSteps = steps - subBand
                topSteps = max(steps - (subBand+1), 1)
                pass
            subBandSteps = max(botSteps, topSteps)

            # Do five segments, clockwise around the North Pole (East to West.)
            for seg in range(5):
                nextseg = (seg+1) % 5 # Wrap-around.

                # Interpolate ends of bottom & top edges of a sub-band segment.
                fractBot = float(subBand)/float(steps)
                fractTop = float(subBand+1)/float(steps)
                sbBotRight = fractBot * upperRing[seg] + \
                           (1.0-fractBot) * lowerRing[seg]
                sbTopRight = fractTop * upperRing[seg] + \
                           (1.0-fractTop) * lowerRing[seg]
                sbBotLeft = fractBot * upperRing[nextseg] + \
                          (1.0-fractBot) * lowerRing[nextseg]
                sbTopLeft = fractTop * upperRing[nextseg] + \
                          (1.0-fractTop) * lowerRing[nextseg]

                # Output the right end of the first segment of the sub-band.
                # We'll end up wrapping around to this same pair of points at
                # the left end of the last segment of the sub-band.
                if seg == 0:
                    # Project verts from icosahedron faces onto the unit sphere.
                    points += [norm(sbBotRight), norm(sbTopRight)]

                # Step across the sub-band edges from right to left,
                # stitching triangle pairs from their lower to upper edges.
                for step in range(1, subBandSteps+1):

                    # Interpolate step point pairs along the sub-band edges.
                    fractLower = float(step+botOffset)/float(botSteps)
                    lower = fractLower * sbBotLeft + \
                          (1.0-fractLower) * sbBotRight
                    # Collapse the *last* triangle of north sub-band top edges.
                    fractUpper = float(min(step, topSteps))/float(topSteps)
                    upper = fractUpper * sbTopLeft + \
                          (1.0-fractUpper) * sbTopRight

                    # Output verts, projected from icos faces onto unit sphere.
                    points += [norm(lower), norm(upper)]

                    continue # step
                continue # seg
            continue # subBand
        continue # band
    return points

def indexVerts(verts, close):
    """
    Compress a vertex array into an array of unique vertices, and an array of
    index values into the unique vertices.  This is good for converting input
    for glDrawArrays into input for glDrawElements.

    The second arg is 'close', the distance between vertices which are close
    enough to be considered a single vertex.

    The return value is a pair of arrays (index, verts).
    """
    unique = []
    index = []
    for v in verts:
        for i in range(len(unique)):
            if vlen(unique[i] - v) < close:
                index += [i]
                break
            pass
        else:
            index += [len(unique)]
            unique += [v]
            pass
        continue
    return (index, unique)

# ==

def init_cyls():
    # generate two circles in space as 13-gons, one rotated half a segment with
    # respect to the other these are used as cylinder ends [not quite true
    # anymore, see comments just below]
    slices = 13
    circ1 = map((lambda n: n*2.0*pi/slices), range(slices+1))
    circ2 = map((lambda a: a+pi/slices), circ1)
    drawing_globals.drum0 = drum0 = map((lambda a: (cos(a), sin(a), 0.0)),
                                        circ1)
    drum1 = map((lambda a: (cos(a), sin(a), 1.0)), circ2)
    drum1n = map((lambda a: (cos(a), sin(a), 0.0)), circ2)

    #grantham 20051213 I finally decided the look of the oddly twisted cylinder
    # bonds was not pretty enough, so I made a "drum2" which is just drum0 with
    # a 1.0 Z coordinate, a la drum1.
    #bruce 060609: this apparently introduced the bug of the drum1 end-cap of a
    # cylinder being "ragged" (letting empty space show through), which I fixed
    # by using drum2 for that cap rather than drum1.  drum1 is no longer used
    # except as an intermediate value in the next few lines.
    drawing_globals.drum2 = drum2 = map((lambda a: (cos(a), sin(a), 1.0)),
                                        circ1)

    # This edge list zips up the "top" vertex and normal and then the "bottom"
    # vertex and normal.  Thus each tuple in the sequence would be (vtop, ntop,
    # vbot, nbot) [grantham 20051213]
    # (bruce 051215 simplified the python usage in a way which should create the
    # same list.)
    drawing_globals.cylinderEdges = zip(drum0, drum0, drum2, drum0)

    circle = zip(drum0[:-1],drum0[1:],drum1[:-1]) +\
           zip(drum1[:-1],drum0[1:],drum1[1:])
    circlen = zip(drum0[:-1],drum0[1:],drum1n[:-1]) +\
            zip(drum1n[:-1],drum0[1:],drum1n[1:])

    drawing_globals.cap0n = (0.0, 0.0, -1.0)
    drawing_globals.cap1n = (0.0, 0.0, 1.0)
    drum0.reverse()
    return
init_cyls()

def init_motors():
    ###data structure to construct the rotation sign for rotary motor
    numSeg = 20
    rotS = map((lambda n: pi/2+n*2.0*pi/numSeg), range(numSeg*3/4 + 1))
    zOffset = 0.005
    scaleS = 0.4
    drawing_globals.rotS0n = rotS0n = map(
        (lambda a: (scaleS*cos(a), scaleS*sin(a), 0.0 - zOffset)), rotS)
    drawing_globals.rotS1n = rotS1n = map(
        (lambda a: (scaleS*cos(a), scaleS*sin(a), 1.0 + zOffset)), rotS)

    ###Linear motor arrow sign data structure
    drawing_globals.halfHeight = 0.45
    drawing_globals.halfEdge = halfEdge = 3.0 * scaleS * sin(pi/numSeg)

    arrow0Vertices = [
        (rotS0n[-1][0]-halfEdge, rotS0n[-1][1], rotS0n[-1][2]), 
        (rotS0n[-1][0]+halfEdge, rotS0n[-1][1], rotS0n[-1][2]), 
        (rotS0n[-1][0], rotS0n[-1][1] + 2.0*halfEdge, rotS0n[-1][2])]
    arrow0Vertices.reverse()
    drawing_globals.arrow0Vertices = arrow0Vertices

    drawing_globals.arrow1Vertices = [
        (rotS1n[-1][0]-halfEdge, rotS1n[-1][1], rotS1n[-1][2]), 
        (rotS1n[-1][0]+halfEdge, rotS1n[-1][1], rotS1n[-1][2]), 
        (rotS1n[-1][0], rotS1n[-1][1] + 2.0*halfEdge, rotS1n[-1][2])]

    drawing_globals.halfEdge = halfEdge = 1.0/3.0 ##1.0/8.0
    drawing_globals.linearArrowVertices = [
        (0.0, -halfEdge, 0.0), (0.0, halfEdge, 0.0), (0.0, 0.0,2*halfEdge)]

    return
init_motors()

def init_diamond():
    # a chunk of diamond grid, to be tiled out in 3d
    drawing_globals.sp0 = sp0 = 0.0
    #bruce 051102 replaced 1.52 with this constant (1.544),
    #  re bug 900 (partial fix.)
    drawing_globals.sp1 = sp1 = DIAMOND_BOND_LENGTH / sqrt(3.0)
    sp2 = 2.0*sp1
    sp3 = 3.0*sp1
    drawing_globals.sp4 = sp4 = 4.0*sp1

    digrid=[[[sp0, sp0, sp0], [sp1, sp1, sp1]],
            [[sp1, sp1, sp1], [sp2, sp2, sp0]],
            [[sp2, sp2, sp0], [sp3, sp3, sp1]],
            [[sp3, sp3, sp1], [sp4, sp4, sp0]],
            [[sp2, sp0, sp2], [sp3, sp1, sp3]],
            [[sp3, sp1, sp3], [sp4, sp2, sp2]],
            [[sp2, sp0, sp2], [sp1, sp1, sp1]],
            [[sp1, sp1, sp1], [sp0, sp2, sp2]],
            [[sp0, sp2, sp2], [sp1, sp3, sp3]],
            [[sp1, sp3, sp3], [sp2, sp4, sp2]],
            [[sp2, sp4, sp2], [sp3, sp3, sp1]],
            [[sp3, sp3, sp1], [sp4, sp2, sp2]],
            [[sp4, sp0, sp4], [sp3, sp1, sp3]],
            [[sp3, sp1, sp3], [sp2, sp2, sp4]],
            [[sp2, sp2, sp4], [sp1, sp3, sp3]],
            [[sp1, sp3, sp3], [sp0, sp4, sp4]]]
    drawing_globals.digrid = A(digrid)
    drawing_globals.DiGridSp = sp4
    return
init_diamond()

def init_cube():
    drawing_globals.cubeVertices = cubeVertices = [
        [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0], [1.0, 1.0, -1.0],
        [-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0],
        [1.0, -1.0, 1.0], [1.0, -1.0, -1.0]]

    #bruce 051117: compute this rather than letting a subroutine hardcode it as
    # a redundant constant
    flatCubeVertices = []
    for threemore in cubeVertices:
        flatCubeVertices.extend(threemore)
    flatCubeVertices = list(flatCubeVertices) #k probably not needed
    drawing_globals.flatCubeVertices = flatCubeVertices

    if 1: # remove this when it works
        flatCubeVertices_hardcoded = [-1.0, 1.0, -1.0,
                                      -1.0, 1.0, 1.0,
                                      1.0, 1.0, 1.0,
                                      1.0, 1.0, -1.0,
                                      -1.0, -1.0, -1.0,
                                      -1.0, -1.0, 1.0,
                                      1.0, -1.0, 1.0,
                                      1.0, -1.0, -1.0]
        assert flatCubeVertices == flatCubeVertices_hardcoded

    sq3 = sqrt(3.0)/3.0
    drawing_globals.cubeNormals = [
        [-sq3, sq3, -sq3], [-sq3, sq3, sq3],
        [sq3, sq3, sq3], [sq3, sq3, -sq3],
        [-sq3, -sq3, -sq3], [-sq3, -sq3, sq3],
        [sq3, -sq3, sq3], [sq3, -sq3, -sq3]]
    drawing_globals.cubeIndices = [
        [0, 1, 2, 3], [0, 4, 5, 1], [1, 5, 6, 2],
        [2, 6, 7, 3], [0, 3, 7, 4], [4, 7, 6, 5]]

    return
init_cube()


# Some variables used by the Lonsdaleite lattice construction.
ux = 1.262
uy = 0.729
dz = 0.5153
ul = 1.544
drawing_globals.XLen = XLen = 2*ux
drawing_globals.YLen = YLen = 6*uy
drawing_globals.ZLen = ZLen = 2*(ul + dz)

def _makeLonsCell():
    """
    Data structure to construct a Lonsdaleite lattice cell
    """
    lVp = [# 2 outward vertices
           [-ux, -2*uy, 0.0], [0.0, uy, 0.0],
           # Layer 1: 7 vertices
           [ux, -2*uy, ul],   [-ux, -2*uy, ul],   [0.0, uy, ul], 
           [ux, 2*uy, ul+dz], [-ux, 2*uy, ul+dz], [0.0, -uy, ul+dz],
           [-ux, 4*uy, ul],
           # Layer 2: 7 vertices
           [ux, -2*uy, 2*(ul+dz)], [-ux, -2*uy, 2*(ul+dz)],
           [0.0, uy, 2*(ul+dz)], [ux, 2*uy, 2*ul+dz], [-ux, 2*uy, 2*ul+dz],
           [0.0, -uy, 2*ul+dz], [-ux, 4*uy, 2*(ul+dz)]
           ]

    res = [ # 2 outward vertical edges for layer 1
            [lVp[0], lVp[3]], [lVp[1], lVp[4]],
            #  6 xy Edges for layer 1
            [lVp[2], lVp[7]], [lVp[3], lVp[7]], [lVp[7], lVp[4]],
            [lVp[4], lVp[6]], [lVp[4], lVp[5]],
            [lVp[6], lVp[8]],        
            #  2 outward vertical edges for layer 2
            [lVp[14], lVp[7]],  [lVp[13], lVp[6]], 
            # 6 xy Edges for layer 2
            [lVp[14], lVp[9]], [lVp[14], lVp[10]], [lVp[14], lVp[11]],
            [lVp[11], lVp[13]], [lVp[11], lVp[12]],
            [lVp[13], lVp[15]]
            ]
    return res
drawing_globals.lonsEdges = _makeLonsCell()
