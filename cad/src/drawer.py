# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
drawer.py - OpenGL drawing utilities.

$Id$

TODO:

This module is too large. It needs to be split into
several smaller files. Don't add new functions to it --
add them in new files whose names start with "draw".

History:

Originated by Josh.

Various developers extended it since then.

Brad G. added ColorSorter features.

At some point Bruce partly cleaned up the use of display lists.

071030 bruce split some functions and globals into draw_grid_lines.py
and removed some obsolete functions.
"""

import os
import sys

# the imports from math vs. Numeric are as discovered in existing code
# as of 2007/06/25.  It's not clear why acos is coming from math...
from math import acos, floor, ceil
from math import asin


import Numeric
from Numeric import sin, cos, sqrt, pi
ONE_RADIAN = 180.0 / pi
HALF_PI  = pi/2.0
TWICE_PI = 2*pi

from OpenGL.GL import GL_AMBIENT
from OpenGL.GL import GL_AMBIENT_AND_DIFFUSE
from OpenGL.GL import glAreTexturesResident
from OpenGL.GL import GL_BACK
from OpenGL.GL import glBegin
from OpenGL.GL import glBindTexture
from OpenGL.GL import GL_BLEND
from OpenGL.GL import glBlendFunc
from OpenGL.GL import glCallList
from OpenGL.GL import glColor3f
from OpenGL.GL import glColor3fv
from OpenGL.GL import glColor4fv
from OpenGL.GL import GL_COMPILE
from OpenGL.GL import GL_CONSTANT_ATTENUATION
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import glDeleteTextures
from OpenGL.GL import glDepthMask
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_DIFFUSE
from OpenGL.GL import glDisable
from OpenGL.GL import glDisableClientState
from OpenGL.GL import glDrawElements
from OpenGL.GL import glEnable
from OpenGL.GL import glEnableClientState
from OpenGL.GL import glEnd
from OpenGL.GL import glEndList
from OpenGL.GL import GL_EXTENSIONS
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_FILL
from OpenGL.GL import glFinish
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FOG
from OpenGL.GL import GL_FOG_COLOR
from OpenGL.GL import GL_FOG_END
from OpenGL.GL import GL_FOG_MODE
from OpenGL.GL import GL_FOG_START
from OpenGL.GL import GL_FRONT
from OpenGL.GL import GL_FRONT_AND_BACK
from OpenGL.GL import glGenLists
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGetString
from OpenGL.GL import GL_LIGHT0
from OpenGL.GL import GL_LIGHT1
from OpenGL.GL import GL_LIGHT2
from OpenGL.GL import glLightf
from OpenGL.GL import glLightfv
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LINE
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_LINE_LOOP
from OpenGL.GL import GL_LINES
from OpenGL.GL import GL_LINE_SMOOTH
from OpenGL.GL import glLineStipple
from OpenGL.GL import GL_LINE_STIPPLE
from OpenGL.GL import GL_LINE_STRIP
from OpenGL.GL import glLineWidth
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import glMaterialf
from OpenGL.GL import glMaterialfv
from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import glNewList
from OpenGL.GL import glNormal3fv
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import GL_POLYGON
from OpenGL.GL import glPolygonMode
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPopName
from OpenGL.GL import GL_POSITION
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPushName
from OpenGL.GL import GL_QUADS
from OpenGL.GL import GL_QUAD_STRIP
from OpenGL.GL import GL_RENDERER
from OpenGL.GL import GL_RGBA
from OpenGL.GL import glRotate
from OpenGL.GL import glRotatef
from OpenGL.GL import GL_SHININESS
from OpenGL.GL import GL_SPECULAR
from OpenGL.GL import GL_SRC_ALPHA
from OpenGL.GL import glTexCoord2f
from OpenGL.GL import glTexCoord2fv
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import glTranslate
from OpenGL.GL import glTranslatef
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_TRIANGLE_STRIP
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import GL_VENDOR
from OpenGL.GL import GL_VERSION
from OpenGL.GL import glVertex
from OpenGL.GL import glVertex2f
from OpenGL.GL import glVertex3f
from OpenGL.GL import glVertex3fv
from OpenGL.GL import GL_VERTEX_ARRAY
from OpenGL.GL import glVertexPointer
from OpenGL.GL import glPointSize
from OpenGL.GL import GL_POINTS
from OpenGL.GL import GL_POINT_SMOOTH
from OpenGL.GLU import gluBuild2DMipmaps

try:
    from OpenGL.GLE import glePolyCone, gleGetNumSides, gleSetNumSides
except:
    print "GLE module can't be imported. Now trying _GLE"
    from OpenGL._GLE import glePolyCone, gleGetNumSides, gleSetNumSides

# Check if the gleGet/SetNumSides function is working on this install, and if
# not, alias it to an effective no-op. Checking method is as recommended in
# an OpenGL exception reported by Brian [070622]:
#   OpenGL.error.NullFunctionError: Attempt to call an
#   undefined function gleGetNumSides, check for
#   bool(gleGetNumSides) before calling
# The underlying cause of this (described by Brian) is that the computer's OpenGL
# has the older gleGetNumSlices (so it supports the functionality), but PyOpenGL
# binds (only) to the newer gleGetNumSides. Given the PyOpenGL we're using,
# there's no way to access gleGetNumSlices, but in the future we might patch it
# to let us do that when this happens. I [bruce 070629] think Brian said this is
# only an issue on Macs.
if not bool(gleGetNumSides):
    print "fyi: gleGetNumSides is not supported by the OpenGL pre-installed on this computer."
    gleGetNumSides = int
    gleSetNumSides = int

try:
    from OpenGL.GL import glScale
except:
    # The installed version of OpenGL requires argument-typed glScale calls.
    from OpenGL.GL import glScalef as glScale

from OpenGL.GL import glScalef
    # Note: this is NOT redundant with the above import of glScale --
    # without it, displaying an ESP Image gives a NameError traceback
    # and doesn't work. [Fixed by bruce 070703; bug caught by Eric M using
    # PyChecker; bug introduced sometime after A9.1 went out.]

try:
    from OpenGL.GL import glFog
except:
    # The installed version of OpenGL requires argument-typed glFog calls.
    from OpenGL.GL import glFogf as glFog	

from geometry.VQT import norm, vlen, V, Q, A, cross
import env #bruce 051126

from constants import DIAMOND_BOND_LENGTH, white
from prefs_constants import material_specular_highlights_prefs_key
from prefs_constants import material_specular_shininess_prefs_key
from prefs_constants import material_specular_finish_prefs_key
from prefs_constants import material_specular_brightness_prefs_key

import debug # for debug.print_compact_traceback

# this can't be done at toplevel due to a recursive import issue.
# TODO: fix by splitting this module (drawer) into smaller files.
## from Font3D import Font3D

import EndUser

# ==

# ColorSorter control
allow_color_sorting = allow_color_sorting_default = False #bruce 060323 changed this to False for A7 release
allow_color_sorting_prefs_key = "allow_color_sorting_rev2" #bruce 060323 changed this to disconnect it from old pref setting

# Experimental native C renderer (quux module in cad/src/experimental/pyrex-opengl)
use_c_renderer = use_c_renderer_default = False
use_c_renderer_prefs_key = "use_c_renderer_rev2" #bruce 060323 changed this to disconnect it from old pref setting

if EndUser.getAlternateSourcePath() != None:
    sys.path.append(os.path.join( EndUser.getAlternateSourcePath(), "experimental/pyrex-opengl"))
else:
    sys.path.append("./experimental/pyrex-opengl")

binPath = os.path.normpath(os.path.dirname(os.path.abspath(sys.argv[0])) + '/../bin')
if binPath not in sys.path:
    sys.path.append(binPath)

try:
    import quux
    quux_module_import_succeeded = True
    if "experimental" in os.path.dirname(quux.__file__):
        # should never happen for end users, but if it does we want to print the warning
        if env.debug() or not EndUser.enableDeveloperFeatures():
            print "debug: fyi: Using experimental version of C rendering code:", quux.__file__
except:
    use_c_renderer = False
    quux_module_import_succeeded = False
    if env.debug(): #bruce 060323 added condition
        print "WARNING: unable to import C rendering code (quux module). Only Python rendering will be available."
    pass

# ==

# the golden ratio
phi = (1.0+sqrt(5.0))/2.0
vert = norm(V(phi,0,1))
a = vert[0]
    # I wonder if this is or was creating the global 'a' in chem.py that I once complained about in there...
    # it's certainly very bad as the name of a global in any module (like a lot of short global names in this module).
    # [bruce 060613 comment]
b = vert[1]
c = vert[2]

# vertices of an icosahedron

icosa = ((-a,b,c), (b,c,-a), (b,c,a), (a,b,-c), (-c,-a,b), (-c,a,b),
         (b,-c,a), (c,a,b), (b,-c,-a), (a,b,c), (c,-a,b), (-a,b,-c))

icosix = ((9, 2, 6), (1, 11, 5), (11, 1, 8), (0, 11, 4), (3, 1, 7),
          (3, 8, 1), (9, 3, 7), (0, 6, 2), (4, 10, 6), (1, 5, 7),
          (7, 5, 2), (8, 3, 10), (4, 11, 8), (9, 7, 2), (10, 9, 6),
          (0, 5, 11), (0, 2, 5), (8, 10, 4), (3, 9, 10), (6, 0, 4))

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

# generate two circles in space as 13-gons,
# one rotated half a segment with respect to the other
# these are used as cylinder ends [not quite true anymore, see comments just below]
slices = 13
circ1 = map((lambda n: n*2.0*pi/slices), range(slices+1))
circ2 = map((lambda a: a+pi/slices), circ1)
drum0 = map((lambda a: (cos(a), sin(a), 0.0)), circ1)
drum1 = map((lambda a: (cos(a), sin(a), 1.0)), circ2)
drum1n = map((lambda a: (cos(a), sin(a), 0.0)), circ2)

# grantham 20051213 I finally decided the look of the oddly twisted
# cylinder bonds was not pretty enough, so I made a "drum2" which is just
# drum0 with a 1.0 Z coordinate, a la drum1.
#bruce 060609: this apparently introduced the bug of the drum1 end-cap of a cylinder being "ragged"
# (letting empty space show through), which I fixed by using drum2 for that cap rather than drum1.
# drum1 is no longer used except as an intermediate value in the next few lines.
drum2 = map((lambda a: (cos(a), sin(a), 1.0)), circ1)

# This edge list zips up the "top" vertex and normal and then
# the "bottom" vertex and normal.
# Thus each tuple in the sequence would be (vtop, ntop, vbot, nbot) [grantham 20051213]
# (bruce 051215 simplified the python usage in a way which should create the same list.)
cylinderEdges = zip(drum0, drum0, drum2, drum0)

circle = zip(drum0[:-1],drum0[1:],drum1[:-1]) +\
       zip(drum1[:-1],drum0[1:],drum1[1:])
circlen = zip(drum0[:-1],drum0[1:],drum1n[:-1]) +\
        zip(drum1n[:-1],drum0[1:],drum1n[1:])

cap0n = (0.0, 0.0, -1.0)
cap1n = (0.0, 0.0, 1.0)
drum0.reverse()

###data structure to construct the rotation sign for rotary motor
numSeg = 20
rotS = map((lambda n: pi/2+n*2.0*pi/numSeg), range(numSeg*3/4 + 1))
zOffset = 0.005; scaleS = 0.4
rotS0n = map((lambda a: (scaleS*cos(a), scaleS*sin(a), 0.0 - zOffset)), rotS)
rotS1n = map((lambda a: (scaleS*cos(a), scaleS*sin(a), 1.0 + zOffset)), rotS)
halfEdge = 3.0 * scaleS * sin(pi/numSeg)
arrow0Vertices = [(rotS0n[-1][0]-halfEdge, rotS0n[-1][1], rotS0n[-1][2]), 
                  (rotS0n[-1][0]+halfEdge, rotS0n[-1][1], rotS0n[-1][2]), 
                  (rotS0n[-1][0], rotS0n[-1][1] + 2.0*halfEdge, rotS0n[-1][2])] 
arrow0Vertices.reverse()                            
arrow1Vertices = [(rotS1n[-1][0]-halfEdge, rotS1n[-1][1], rotS1n[-1][2]), 
                  (rotS1n[-1][0]+halfEdge, rotS1n[-1][1], rotS1n[-1][2]), 
                  (rotS1n[-1][0], rotS1n[-1][1] + 2.0*halfEdge, rotS1n[-1][2])]                             

###Linear motor arrow sign data structure
halfEdge = 1.0/3.0 ##1.0/8.0
linearArrowVertices = [(0.0, -halfEdge, 0.0), (0.0, halfEdge, 0.0), (0.0, 0.0,2*halfEdge)]

# a chunk of diamond grid, to be tiled out in 3d

sp0 = 0.0
sp1 = DIAMOND_BOND_LENGTH / sqrt(3.0) #bruce 051102 replaced 1.52 with this constant (1.544), re bug 900 (partial fix)
sp2 = 2.0*sp1
sp3 = 3.0*sp1
sp4 = 4.0*sp1

digrid=[[[sp0, sp0, sp0], [sp1, sp1, sp1]], [[sp1, sp1, sp1], [sp2, sp2, sp0]],
        [[sp2, sp2, sp0], [sp3, sp3, sp1]], [[sp3, sp3, sp1], [sp4, sp4, sp0]],
        [[sp2, sp0, sp2], [sp3, sp1, sp3]], [[sp3, sp1, sp3], [sp4, sp2, sp2]],
        [[sp2, sp0, sp2], [sp1, sp1, sp1]], [[sp1, sp1, sp1], [sp0, sp2, sp2]],
        [[sp0, sp2, sp2], [sp1, sp3, sp3]], [[sp1, sp3, sp3], [sp2, sp4, sp2]],
        [[sp2, sp4, sp2], [sp3, sp3, sp1]], [[sp3, sp3, sp1], [sp4, sp2, sp2]],
        [[sp4, sp0, sp4], [sp3, sp1, sp3]], [[sp3, sp1, sp3], [sp2, sp2, sp4]],
        [[sp2, sp2, sp4], [sp1, sp3, sp3]], [[sp1, sp3, sp3], [sp0, sp4, sp4]]]

cubeVertices = [[-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0], [1.0, 1.0, -1.0],
                [-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0],
                [1.0, -1.0, 1.0], [1.0, -1.0, -1.0]]

flatCubeVertices = []  #bruce 051117: compute this rather than letting a subroutine hardcode it as a redundant constant
for threemore in cubeVertices:
    flatCubeVertices.extend(threemore)
flatCubeVertices = list(flatCubeVertices) #k probably not needed

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
cubeNormals = [[-sq3, sq3, -sq3], [-sq3, sq3, sq3],
               [sq3, sq3, sq3], [sq3, sq3, -sq3],
               [-sq3, -sq3, -sq3], [-sq3, -sq3, sq3],
               [sq3, -sq3, sq3], [sq3, -sq3, -sq3]]
cubeIndices = [[0, 1, 2, 3], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [0, 3, 7, 4], [4, 7, 6, 5]]        

digrid = A(digrid)

DiGridSp = sp4

sphereList = []
numSphereSizes = 3
CylList = diamondGridList = CapList = CubeList = solidCubeList = lineCubeList = None
rotSignList = linearLineList = linearArrowList = circleList = lonsGridList = None

# grantham 20051118; revised by bruce 051126
class glprefs:

    def __init__(self):
##	self.override_material_specular = None
##	    # set to 4-element sequence to override material specular component
##	self.override_shininess = None
##	    # if exists, overrides shininess
##	self.override_light_specular = None
##	    # set to 4-element sequence to override light specular component
        import preferences #bruce 051126 KLUGE: make sure env.prefs exists (could use cleanup, but that's not trivial)
        self.update()

    def update(self): #bruce 051126 added this method
        """Update attributes from current drawing-related prefs stored in prefs db cache.
           This should be called at the start of each complete redraw, or whenever the user changes these global prefs values
        (whichever is more convenient).
           (Note: When this is called during redraw, its prefs db accesses (like any others)
        record those prefs as potentially affecting what should be drawn, so that subsequent
        changes to those prefs values cause an automatic gl_update.)
           Using these attributes in drawing code (rather than directly accessing prefs db cache)
        is desirable for efficiency, since direct access to prefs db cache is a bit slow.
        (Our drawing code still does that in other places -- those might also benefit from this system,
         though this will soon be moot when low-level drawing code gets rewritten in C.)
        """
        global use_c_renderer, allow_color_sorting
        self.enable_specular_highlights = not not env.prefs[material_specular_highlights_prefs_key] # boolean
        if self.enable_specular_highlights:
            self.override_light_specular = None # used in glpane
            # self.specular_shininess: float; shininess exponent for all specular highlights
            self.specular_shininess = float(env.prefs[material_specular_shininess_prefs_key])
            # self.specular_whiteness: float; whiteness for all material specular colors
            self.specular_whiteness = float(env.prefs[material_specular_finish_prefs_key])
            # self.specular_brightness: float; for all material specular colors
            self.specular_brightness = float(env.prefs[material_specular_brightness_prefs_key])
        else:
            self.override_light_specular = (0.0, 0.0, 0.0, 0.0) # used in glpane
            # Set these to reasonable values, though these attributes are presumably never used in this case.
            # Don't access the prefs db in this case, since that would cause UI prefs changes to do unnecessary gl_updates.
            # (If we ever add a scenegraph node which can enable specular highlights but use outside values for these parameters,
            #  then to make it work correctly we'll need to revise this code.)
            self.specular_shininess = 20.0
            self.specular_whiteness = 1.0
            self.specular_brightness = 1.0

        allow_color_sorting = env.prefs.get(allow_color_sorting_prefs_key,
                                            allow_color_sorting_default)

        use_c_renderer = quux_module_import_succeeded and \
                       env.prefs.get(use_c_renderer_prefs_key, use_c_renderer_default)

        if use_c_renderer:
            quux.shapeRendererSetMaterialParameters(self.specular_whiteness,
                                                    self.specular_brightness, self.specular_shininess);
        return

    def materialprefs_summary(self): #bruce 051126
        """Return a Python data object summarizing our prefs which affect chunk display lists,
        so that memoized display lists should become invalid (due to changes in this object)
        if and only if this value becomes different.
        """
        res = (self.enable_specular_highlights,)
        if self.enable_specular_highlights:
            res = res + ( self.specular_shininess, self.specular_whiteness, self.specular_brightness)

        # grantham 20060314
        res += (quux_module_import_succeeded and 
                env.prefs.get(use_c_renderer_prefs_key, use_c_renderer_default),)

        # grantham 20060314 - Not too sure this next addition is
        # really necessary, but it seems to me that for testing
        # purposes it is important to rebuild display lists if the
        # color sorting pref is changed.
        res += (env.prefs.get(allow_color_sorting_prefs_key,
                              allow_color_sorting_default),)

        return res

    pass # end of class glprefs

_glprefs = glprefs()

# ==

# helper functions for use by GL widgets wanting to set up lighting

#bruce 051212 made these from the code in GLPane which now calls them, so they can also be used in ThumbView

# Default lights tuples (format is as used by setup_standard_lights; perhaps also assumed by other code).
#grantham 20051121 comment - Light should probably be a class.  Right now,
# changing the behavior of lights requires changing a bunch of
# ambiguous tuples and tuple packing/unpacking.
#bruce 051212 moved this here from GLPane; maybe it belongs in prefs_constants instead?
# Note: I'm not sure whether this is the only place where this data is coded.
_default_lights = ((white, 0.1, 0.5, 0.5, -50, 70, 30, True),
                   (white, 0.1, 0.5, 0.5, -20, 20, 20, True),
                   (white, 0.1, 0.1, 0.1, 0, 0, 100, False))
        # for each of 3 lights, this stores ((r,g,b),a,d,s,x,y,z,e)
        # revised format to include s,x,y,z.  Mark 051202.
        # revised format to include c (r,g,b). Mark 051204.
        # Be sure to keep the lightColor prefs keys and _lights colors synchronized.
        # Mark 051204. [a comment from when this was located in GLPane]

def glprefs_data_used_by_setup_standard_lights( glprefs = None): #bruce 051212
    """Return a summary of the glprefs data used by setup_standard_lights,
    for use in later deciding whether it needs to be called again due to changes in glprefs.
    """
    global _glprefs
    if glprefs is None:
        glprefs = _glprefs
    return (glprefs.override_light_specular,) # this must be kept in sync with what's used by setup_standard_lights()

def setup_standard_lights( lights, glprefs = None):
    """Set up lighting in the current GL context using the supplied "lights" tuple (in the format used by GLPane's prefs)
    and the optional glprefs object (which defaults to drawer._glprefs).
       Note: the glprefs data used can be summarized by the related function glprefs_data_used_by_setup_standard_lights (which see).
       Warning: has side effects on GL_MODELVIEW matrix.
       Note: If GL_NORMALIZE needs to be enabled, callers should do that themselves,
    since this depends on what they will draw and might slow down drawing.
    """
    #e not sure whether projection matrix also needs to be reset here [bruce 051212]
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    global _glprefs
    if glprefs is None:
        glprefs = _glprefs
        # note: whatever glprefs data is used below must also be present
        # in the return value of glprefs_data_used_by_setup_standard_lights(). [bruce 051212]

    try:
        # new code
        (((r0,g0,b0),a0,d0,s0,x0,y0,z0,e0), \
         ( (r1,g1,b1),a1,d1,s1,x1,y1,z1,e1), \
         ( (r2,g2,b2),a2,d2,s2,x2,y2,z2,e2)) = lights

        # Great place for a print statement for debugging lights.  Keep this.  Mark 051204. [revised by bruce 051212]
        #print "-------------------------------------------------------------"
        #print "setup_standard_lights: lights[0]=", lights[0]
        #print "setup_standard_lights: lights[1]=", lights[1]
        #print "setup_standard_lights: lights[2]=", lights[2]

        glLightfv(GL_LIGHT0, GL_POSITION, (x0, y0, z0, 0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (r0*a0, g0*a0, b0*a0, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (r0*d0, g0*d0, b0*d0, 1.0))
        if glprefs.override_light_specular is not None:
            glLightfv(GL_LIGHT0, GL_SPECULAR, glprefs.override_light_specular)
        else:
            # grantham 20051121 - this should be a component on its own
            # not replicating the diffuse color.
            # Added specular (s0) as its own component.  mark 051202.
            glLightfv(GL_LIGHT0, GL_SPECULAR, (r0*s0, g0*s0, b0*s0, 1.0))
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)

        glLightfv(GL_LIGHT1, GL_POSITION, (x1, y1, z1, 0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (r1*a1, g1*a1, b1*a1, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (r1*d1, g1*d1, b1*d1, 1.0))
        if glprefs.override_light_specular is not None:
            glLightfv(GL_LIGHT1, GL_SPECULAR, glprefs.override_light_specular)
        else:
            glLightfv(GL_LIGHT1, GL_SPECULAR, (r1*s1, g1*s1, b1*s1, 1.0))
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)

        glLightfv(GL_LIGHT2, GL_POSITION, (x2, y2, z2, 0))
        glLightfv(GL_LIGHT2, GL_AMBIENT, (r2*a2, g2*a2, b2*a2, 1.0))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (r2*d2, g2*d2, b2*d2, 1.0))
        if glprefs.override_light_specular is not None:
            glLightfv(GL_LIGHT2, GL_SPECULAR, glprefs.override_light_specular)
        else:
            glLightfv(GL_LIGHT2, GL_SPECULAR, (r2*s2, g2*s2, b2*s2, 1.0))
        glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)

        glEnable(GL_LIGHTING)

        if e0:
            glEnable(GL_LIGHT0)
        else:
            glDisable(GL_LIGHT0)

        if e1:
            glEnable(GL_LIGHT1)
        else:
            glDisable(GL_LIGHT1)

        if e2:
            glEnable(GL_LIGHT2)
        else:
            glDisable(GL_LIGHT2)
    except:
        debug.print_compact_traceback("bug (worked around): setup_standard_lights reverting to old code, because: ")
        # old code, used only to set up some sort of workable lighting in case of bugs
        # (this is not necessarily using the same values as _default_lights; doesn't matter since never used unless there are bugs)
        glLightfv(GL_LIGHT0, GL_POSITION, (-50, 70, 30, 0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)

        glLightfv(GL_LIGHT1, GL_POSITION, (-20, 20, 20, 0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.4, 0.4, 0.4, 1.0))
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)

        glLightfv(GL_LIGHT2, GL_POSITION, (0, 0, 100, 0))
        glLightfv(GL_LIGHT2, GL_AMBIENT, (1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)

        glEnable(GL_LIGHTING)

        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glDisable(GL_LIGHT2)
    return # from setup_standard_lights

# ==

def setup_fog(fog_start, fog_end, fog_color):

    glFog(GL_FOG_MODE, GL_LINEAR)
    glFog(GL_FOG_START, fog_start)
    glFog(GL_FOG_END, fog_end)
    if len(fog_color) == 3:
        fog_color = (fog_color[0], fog_color[1], fog_color[2], 1.0)
    glFog(GL_FOG_COLOR, fog_color)

def enable_fog():
    glEnable(GL_FOG)

def disable_fog():
    glDisable(GL_FOG)


def apply_material(color): # grantham 20051121, renamed 20051201; revised by bruce 051126, 051203 (added specular_brightness), 051215
    "Set OpenGL material parameters based on the given color (length 3 or 4) and the material-related prefs values in _glprefs."

    #bruce 051215: make sure color is a tuple, and has length exactly 4, for all uses inside this function,
    # assuming callers pass sequences of length 3 or 4. Needed because glMaterial requires four-component
    # vector and PyOpenGL doesn't check. [If this is useful elsewhere, we can split it into a separate function.]
    color = tuple(color)
    if len(color) == 3:
        color = color + (1.0,) # usual case
    elif len(color) != 4:
        # should never happen; if it does, this assert will always fail
        assert len(color) in [3,4], "color tuples must have length 3 or 4, unlike %r" % (color,)

    if not _glprefs.enable_specular_highlights:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)
        # glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0,0,0,1))
        return

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)

    whiteness = _glprefs.specular_whiteness
    brightness = _glprefs.specular_brightness
    if whiteness == 1.0:
        specular = (1.0, 1.0, 1.0, 1.0) # optimization
    else:
        if whiteness == 0.0:
            specular = color # optimization
        else:
            # assume color[3] (alpha) is not passed or is always 1.0
            c1 = 1.0 - whiteness
            specular = ( c1 * color[0] + whiteness, c1 * color[1] + whiteness, c1 * color[2] + whiteness, 1.0 )
    if brightness != 1.0:
        specular = ( specular[0] * brightness, specular[1] * brightness, specular[2] * brightness, 1.0 )
            #e could optimize by merging this with above 3 cases (or, of course, by doing it in C, which we'll do eventually)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular)

    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, _glprefs.specular_shininess)
    return

def get_gl_info_string(glpane): # grantham 20051129
    """Return a string containing some useful information about the OpenGL implementation.
    Use the GL context from the given QGLWidget glpane (by calling glpane.makeCurrent()).
    """

    glpane.makeCurrent() #bruce 070308 added glpane arg and makeCurrent call

    gl_info_string = ''

    gl_info_string += 'GL_VENDOR : "%s"\n' % glGetString(GL_VENDOR)
    gl_info_string += 'GL_VERSION : "%s"\n' % glGetString(GL_VERSION)
    gl_info_string += 'GL_RENDERER : "%s"\n' % glGetString(GL_RENDERER)
    gl_info_string += 'GL_EXTENSIONS : "%s"\n' % glGetString(GL_EXTENSIONS)

    from debug_prefs import debug_pref, Choice_boolean_False
    if debug_pref("get_gl_info_string call glAreTexturesResident?", Choice_boolean_False):
        # Give a practical indication of how much video memory is available.
        # Should also do this with VBOs.

        # I'm pretty sure this code is right, but PyOpenGL seg faults in
        # glAreTexturesResident, so it's disabled until I can figure that
        # out. [grantham] [bruce 070308 added the debug_pref]

        all_tex_in = True
        tex_bytes = '\0' * (512 * 512 * 4)
        tex_names = []
        tex_count = 0
        tex_names = glGenTextures(1024)
        glEnable(GL_TEXTURE_2D)
        while all_tex_in:
            glBindTexture(GL_TEXTURE_2D, tex_names[tex_count])
            gluBuild2DMipmaps(GL_TEXTURE_2D, 4, 512, 512, GL_RGBA,
                              GL_UNSIGNED_BYTE, tex_bytes)
            tex_count += 1

            glTexCoord2f(0.0, 0.0)
            glBegin(GL_QUADS)
            glVertex2f(0.0, 0.0)
            glVertex2f(1.0, 0.0)
            glVertex2f(1.0, 1.0)
            glVertex2f(0.0, 1.0)
            glEnd()
            glFinish()

            residences = glAreTexturesResident(tex_names[:tex_count])
            all_tex_in = reduce(lambda a,b: a and b, residences)
                # bruce 070308 sees this exception from this line:
                # TypeError: reduce() arg 2 must support iteration

        glDisable(GL_TEXTURE_2D)
        glDeleteTextures(tex_names)

        gl_info_string += "Could create %d 512x512 RGBA resident textures\n", tex_count
    return gl_info_string

def drawsphere_worker(params):
    """Draw a sphere.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see below)"""

    (pos, radius, detailLevel) = params
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    glCallList(sphereList[detailLevel])
    glPopMatrix()
    return

def drawcylinder_worker(params):
    """
    Draw a cylinder.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see below)

    WARNING: our circular cross-section is approximated by a 13-gon
    whose alignment around the axis is chosen arbitrary, in a way
    which depends on the direction of the axis; negating the axis usually
    causes a different alignment of that 13-gon. This effect can cause
    visual bugs when drawing one cylinder over an identical or slightly
    smaller one (e.g. when highlighting a bond), unless the axes are kept
    parallel as opposed to antiparallel.
    """

    global CylList, CapList
    (pos1, pos2, radius, capped) = params

    glPushMatrix()
    vec = pos2-pos1
    axis = norm(vec)
    glTranslatef(pos1[0], pos1[1], pos1[2])

    ##Huaicai 1/17/05: To avoid rotate around (0, 0, 0), which causes 
    ## display problem on some platforms
    angle = -acos(axis[2])*180.0/pi
    if (axis[2]*axis[2] >= 1.0):
        glRotate(angle, 0.0, 1.0, 0.0)
    else:
        glRotate(angle, axis[1], -axis[0], 0.0)

    glScale(radius,radius,Numeric.dot(vec,vec)**.5)
    glCallList(CylList)
    if capped: glCallList(CapList)

    glPopMatrix()

    return

def drawsurface_worker(params):
    """Draw a surface.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see below)"""

    (pos, radius, tm, nm) = params
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    renderSurface(tm, nm)
    glPopMatrix()
    return

# 20060208 grantham - The following classes, ShapeList_inplace, ShapeList and
# ColorSorter, should probably be in their own file.  But Bruce
# cautions me against doing it on my own since I haven't done that
# before and there are subtleties.

class ShapeList_inplace:

    """\
    Records sphere and cylinder data and invokes it through the native C++
    rendering system.

    This has the benefit over ShapeList that shapes aren't first stored in
    lots of Python lists, and then turned into lots of Numeric arrays.
    Instead, it stores directly in a list of fixed-size Numeric arrays.
    It shows some speedup, but not a lot.  And tons of memory is being
    used.  I'm not sure where. -grantham

    """

    __author__ = "grantham@plunk.org"

    _blocking = 512     # balance between memory zeroing and drawing efficiency

    def __init__(self):

        #
        # Lists of lists, each list containing a Numeric array and the
        # number of objects in that array.  E.g. Each element in
        # sphere is [l, n], where l is array((m, 9), 'f'), n is the
        # number of valid 9 element slices in l that represent
        # spheres, and m is equal to or more than n+1.
        #
        self.spheres = []
        self.cylinders = []

        # If this is true, disallow future adds.
        self.petrified = False


    def draw(self):

        """\
        Draw all the objects represented in this shape list.
        """

        for (spheres, count) in self.spheres:
            quux.shapeRendererDrawSpheresIlvd(count, spheres)
        for (cylinders, count) in self.cylinders:
            quux.shapeRendererDrawCylindersIlvd(count, cylinders)


    def add_sphere(self, color4, pos, radius, name = 0):
        """\
        Add a sphere to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        if self.petrified:
            raise ValueError, "Tried to add a sphere to a petrified ShapeList_inplace"

        # struct Sphere {
        #     float m_color[4];
        #     float m_nameUInt;
        #     float m_center[3];
        #     float m_radius;
        # };

        if len(self.spheres) == 0 or self.spheres[-1][1] == ShapeList_inplace._blocking:
            # size of struct Sphere in floats is 9
            block = Numeric.zeros((ShapeList_inplace._blocking, 9), 'f')
            self.spheres.append([block, 0])

        (block, count) = self.spheres[-1]

        block[count] = (\
            color4[0], color4[1], color4[2], color4[3],
            float(name),
            pos[0], pos[1], pos[2],
            radius)

        self.spheres[-1][1] += 1


    def add_cylinder(self, color4, pos1, pos2, radius, name = 0, capped=0):
        """\
        Add a cylinder to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        if self.petrified:
            raise ValueError, "Tried to add a cylinder to a petrified ShapeList_inplace"

        # struct Cylinder {
        #     float m_color[4];
        #     float m_nameUInt;
        #     float m_cappedBool;
        #     float m_pos1[3];
        #     float m_pos2[3];
        #     float m_radius; 
        # };

        if len(self.cylinders) == 0 or self.cylinders[-1][1] == ShapeList_inplace._blocking:
            # size of struct Cylinder in floats is 13
            block = Numeric.zeros((ShapeList_inplace._blocking, 13), 'f')
            self.cylinders.append([block, 0])

        (block, count) = self.cylinders[-1]

        block[count] = (\
            color4[0], color4[1], color4[2], color4[3],
            float(name),
            float(capped),
            pos1[0], pos1[1], pos1[2],
            pos2[0], pos2[1], pos2[2],
            radius)

        self.cylinders[-1][1] += 1


    def petrify(self):
        """\
        Make this object

        Since the last block of shapes might not be full, this
        function copies them to a new block exactly big enough to hold
        the shapes in that block.  The gc has a chance to release the
        old block and reduce memory use.  After this point, shapes
        must not be added to this ShapeList.
        """

        self.petrified = True

        if len(self.spheres) > 0:
            count = self.spheres[-1][1]
            if count < ShapeList_inplace._blocking:
                block = self.spheres[-1][0]
                newblock = Numeric.array(block[0:count], 'f')
                self.spheres[-1][0] = newblock

        if len(self.cylinders) > 0:
            count = self.cylinders[-1][1]
            if count < ShapeList_inplace._blocking:
                block = self.cylinders[-1][0]
                newblock = Numeric.array(block[0:count], 'f')
                self.cylinders[-1][0] = newblock


class ShapeList:

    """\
    Records sphere and cylinder data and invokes it through the native C++
    rendering system.

    Probably better to use "ShapeList_inplace".
    """

    __author__ = "grantham@plunk.org"

    def __init__(self):

        self.memoized = False

        self.sphere_colors = []
        self.sphere_radii = []
        self.sphere_centers = []
        self.sphere_names = []

        self.cylinder_colors = []
        self.cylinder_radii = []
        self.cylinder_pos1 = []
        self.cylinder_pos2 = []
        self.cylinder_cappings = []
        self.cylinder_names = []


    def _memoize(self):

        """\
        Internal function that creates Numeric arrays from the data stored
        in add_sphere and add-cylinder.
        """

        self.memoized = True

        # GL Names are uint32.  Numeric.array appears to have only
        # int32.  Winging it...

        self.sphere_colors_array = Numeric.array(self.sphere_colors, 'f')
        self.sphere_radii_array = Numeric.array(self.sphere_radii, 'f')
        self.sphere_centers_array = Numeric.array(self.sphere_centers, 'f')
        self.sphere_names_array = Numeric.array(self.sphere_names, 'i')

        self.cylinder_colors_array = Numeric.array(self.cylinder_colors, 'f')
        self.cylinder_radii_array = Numeric.array(self.cylinder_radii, 'f')
        self.cylinder_pos1_array = Numeric.array(self.cylinder_pos1, 'f')
        self.cylinder_pos2_array = Numeric.array(self.cylinder_pos2, 'f')
        self.cylinder_cappings_array = Numeric.array(self.cylinder_cappings, 'f')
        self.cylinder_names_array = Numeric.array(self.cylinder_names, 'i')


    def draw(self):

        """\
        Draw all the objects represented in this shape list.
        """

        # ICK - SLOW - Probably no big deal in a display list.

        if len(self.sphere_radii) > 0:
            if not self.memoized:
                self._memoize()
            quux.shapeRendererDrawSpheres(len(self.sphere_radii),
                                          self.sphere_centers_array,
                                          self.sphere_radii_array,
                                          self.sphere_colors_array,
                                          self.sphere_names_array)

        if len(self.cylinder_radii) > 0:
            if not self.memoized:
                self._memoize()
            quux.shapeRendererDrawCylinders(len(self.cylinder_radii),
                                            self.cylinder_pos1_array,
                                            self.cylinder_pos2_array,
                                            self.cylinder_radii_array,
                                            self.cylinder_cappings_array,
                                            self.cylinder_colors_array,
                                            self.cylinder_names_array)


    def add_sphere(self, color4, pos, radius, name = 0):
        """\
        Add a sphere to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        self.sphere_colors.append(color4)
        self.sphere_centers.append(list(pos))
        self.sphere_radii.append(radius)
        self.sphere_names.append(name)
        self.memoized = False


    def add_cylinder(self, color4, pos1, pos2, radius, name = 0, capped=0):
        """\
        Add a cylinder to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        self.cylinder_colors.append(color4)
        self.cylinder_radii.append(radius)
        self.cylinder_pos1.append(list(pos1))
        self.cylinder_pos2.append(list(pos2))
        self.cylinder_cappings.append(capped)
        self.cylinder_names.append(name)
        self.memoized = False


    def petrify(self):
        """\
        Delete all but the cached Numeric arrays.

        Call this when you're sure you don't have any more shapes to store
        in the shape list and you want to release the python lists of data
        back to the heap.  Additional shapes must not be added to this shape
        list.
        """
        if not self.memoized:
            self._memoize()

        del self.sphere_colors
        del self.sphere_radii
        del self.sphere_centers
        del self.sphere_names

        del self.cylinder_colors
        del self.cylinder_radii
        del self.cylinder_pos1
        del self.cylinder_pos2
        del self.cylinder_cappings
        del self.cylinder_names


class ColorSorter:

    """\
    State Sorter specializing in color (Really any object that can be
    passed to apply_material, which on 20051204 is only color 4-tuples)

    Invoke start() to begin sorting.
    Call finish() to complete sorting and draw all sorted objects.

    Call schedule() with any function and parameters to be sorted by color.
    If not sorting, schedule() will invoke the function immediately.  If
    sorting, then the function will not be called until "finish()".

    In any function which will take part in sorting which previously did
    not, create a worker function from the old function except the call to
    apply_material.  Then create a wrapper which calls
    ColorSorter.schedule with the worker function and its params.

    Also an app can call schedule_sphere and schedule_cylinder to
    schedule a sphere or a cylinder.  Right now this is the only way
    to directly access the native C++ rendering engine.
    """
    __author__ = "grantham@plunk.org"

    # For now, these are class globals.  As long as OpenGL drawing is
    # serialized and Sorting isn't nested, this is okay.  When/if
    # OpenGL drawing becomes multi-threaded, sorters will have to
    # become instances.  This is probably okay because objects and
    # materials will probably become objects of their own about that
    # time so the whole system will get a redesign and
    # reimplementation.

    sorting = False     # Guard against nested sorting
    _sorted = 0         # Number of calls to _add_to_sorter since last
                        # _printstats
    _immediate = 0      # Number of calls to _invoke_immediately since last
                        # _printstats
    _gl_name_stack = [0]       # internal record of GL name stack; 0 is a sentinel

    def pushName(glname):
        """\
        Record the current pushed GL name, which must not be 0.
        """
        assert glname, "glname of 0 is illegal (used as sentinel)" #bruce 060217 added this assert
        ColorSorter._gl_name_stack.append(glname)

    pushName = staticmethod(pushName)


    def popName():
        """\
        Record a pop of the GL name.
        """
        del ColorSorter._gl_name_stack[-1]

    popName = staticmethod(popName)


    def _printstats():
        """\
        Internal function for developers to call to print stats on number of
        sorted and immediately-called objects.
        """
        print "Since previous 'stats', %d sorted, %d immediate: " % (ColorSorter._sorted, ColorSorter._immediate)
        ColorSorter._sorted = 0
        ColorSorter._immediate = 0

    _printstats = staticmethod(_printstats)


    def _add_to_sorter(color, func, params):
        """\
        Internal function that stores 'scheduled' operations for a later
        sort, between a start/finish
        """
        ColorSorter._sorted += 1
        color = tuple(color)
        if not ColorSorter.sorted_by_color.has_key(color):
            ColorSorter.sorted_by_color[color] = []
        ColorSorter.sorted_by_color[color].append((func, params,
                                                   ColorSorter._gl_name_stack[-1]))

    _add_to_sorter = staticmethod(_add_to_sorter)


    def schedule(color, func, params):
        if ColorSorter.sorting and allow_color_sorting:

            ColorSorter._add_to_sorter(color, func, params)

        else:

            ColorSorter._immediate += 1 # for benchmark/debug stats, mostly

            # 20060216 We know we can do this here because the stack is
            # only ever one element deep
            name = ColorSorter._gl_name_stack[-1]
            if name:
                glPushName(name)

            #Apply appropriate opacity for the object if it is specified
            #in the 'color' param. (Also do necessary things such as 
            #call glBlendFunc it. -- Ninad 20071009

            if len(color) == 4:
                opacity = color[3]
            else:
                opacity = 1.0

            if opacity != 1.0:	
                glDepthMask(GL_FALSE)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            apply_material(color)
            func(params)

            if opacity != 1.0:	
                glDisable(GL_BLEND)
                glDepthMask(GL_TRUE)


            if name:
                glPopName()
        return

    schedule = staticmethod(schedule)

    def schedule_sphere(color, pos, radius, detailLevel, opacity = 1.0):
        """\
        Schedule a sphere for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color
            ColorSorter._cur_shapelist.add_sphere(lcolor, pos, radius,
                                                  ColorSorter._gl_name_stack[-1])
            # 20060208 grantham - I happen to know that one detailLevel
            # is chosen for all spheres, I just record it over and
            # over here, and use the last one for the render
            if ColorSorter.sphereLevel > -1 and ColorSorter.sphereLevel != detailLevel:
                raise ValueError, "unexpected different sphere LOD levels within same frame"
            ColorSorter.sphereLevel = detailLevel
        else: # Older sorted material rendering
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color	
            ColorSorter.schedule(lcolor, drawsphere_worker, (pos, radius, detailLevel))

    schedule_sphere = staticmethod(schedule_sphere)


    def schedule_cylinder(color, pos1, pos2, radius, capped = 0, opacity = 1.0 ):
        """\
        Schedule a cylinder for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            ColorSorter._cur_shapelist.add_cylinder(lcolor, pos1, pos2, radius,
                                                    ColorSorter._gl_name_stack[-1], capped)
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor, drawcylinder_worker, (pos1, pos2, radius, capped))

    schedule_cylinder = staticmethod(schedule_cylinder)

    def schedule_surface(color, pos, radius, tm, nm):
        """\
        Schedule a surface for rendering whenever ColorSorter thinks is
        appropriate.
        """
        ColorSorter.schedule(color, drawsurface_worker, (pos, radius, tm, nm))

    schedule_surface = staticmethod(schedule_surface)


    def start():
        """\
        Start sorting - objects provided to "schedule", "schedule_sphere", and
        "schedule_cylinder" will be stored for a sort at the time "finish" is called.
        """
        assert not ColorSorter.sorting, "Called ColorSorter.start but already sorting?!"
        ColorSorter.sorting = True
        if use_c_renderer and ColorSorter.sorting:
            ColorSorter._cur_shapelist = ShapeList_inplace()
            ColorSorter.sphereLevel = -1
        else:
            ColorSorter.sorted_by_color = {}

    start = staticmethod(start)


    def finish():
        """\
        Finish sorting - objects recorded since "start" will
        be sorted and invoked now.
        """
        from debug_prefs import debug_pref, Choice_boolean_False
        debug_which_renderer = debug_pref("debug print which renderer", Choice_boolean_False) #bruce 060314, imperfect but tolerable
        if use_c_renderer:
            quux.shapeRendererInit()
            if debug_which_renderer:
                #bruce 060314 uncommented/revised the next line; it might have to come after shapeRendererInit (not sure);
                # it definitely has to come after a graphics context is created and initialized.
                # 20060314 grantham - yes, has to come after quux.shapeRendererInit
                print "using C renderer: VBO %s enabled" % (('is NOT', 'is')[quux.shapeRendererGetInteger(quux.IS_VBO_ENABLED)])
            quux.shapeRendererSetUseDynamicLOD(0)
            if ColorSorter.sphereLevel != -1:
                quux.shapeRendererSetStaticLODLevels(ColorSorter.sphereLevel, 1)
            quux.shapeRendererStartDrawing()
            ColorSorter._cur_shapelist.draw()
            quux.shapeRendererFinishDrawing()
            ColorSorter.sorting = False

            # So chunks can actually record their shapelist
            # at some point if they want to
            # ColorSorter._cur_shapelist.petrify()
            # return ColorSorter._cur_shapelist      

        else:
            if debug_which_renderer:
                print "using Python renderer"
            color_groups = len(ColorSorter.sorted_by_color)
            objects_drawn = 0
            for color, funcs in ColorSorter.sorted_by_color.iteritems():
                apply_material(color)
                for func, params, name in funcs:
                    objects_drawn += 1
                    if name != 0:
                        glPushName(name)
                    func(params)
                    if name != 0:
                        glPopName()
            ColorSorter.sorted_by_color = None
            ColorSorter.sorting = False

    finish = staticmethod(finish)


halfHeight = 0.45

##Some variable used by the Lonsdaleite lattice construction
ux = 1.262; uy = 0.729; dz = 0.5153; ul = 1.544
XLen = 2*ux
YLen = 6*uy
ZLen = 2*(ul + dz)
lonsEdges = None

def _makeLonsCell():
    """Data structure to construct a Lonsdaleite lattice cell"""
    lVp = [# 2 outward vertices
           [-ux, -2*uy, 0.0], [0.0, uy, 0.0],
           # Layer 1: 7 vertices
           [ux, -2*uy, ul],      [-ux, -2*uy, ul],     [0.0, uy, ul], 
           [ux, 2*uy, ul+dz], [-ux, 2*uy, ul+dz], [0.0, -uy, ul+dz],
           [-ux, 4*uy, ul],
           # Layer 2: 7 vertices
           [ux, -2*uy, 2*(ul+dz)], [-ux, -2*uy, 2*(ul+dz)], [0.0, uy, 2*(ul+dz)],
           [ux, 2*uy, 2*ul+dz],    [-ux, 2*uy, 2*ul+dz],     [0.0, -uy, 2*ul+dz],
           [-ux, 4*uy, 2*(ul+dz)]
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

wiresphere1list = None

# ==

def setup_drawer():
    """
    Set up the usual constant display lists in the current OpenGL context.

    WARNING: THIS IS ONLY CORRECT IF ONLY ONE GL CONTEXT CONTAINS DISPLAY LISTS --
    or more precisely, only the GL context this has last been called in
    (or one which shares its display lists) will work properly with the routines in drawer.py,
    since the allocated display list names are stored in globals set by this function,
    but in general those names might differ if this was called in different GL contexts.
    """
        #bruce 060613 added docstring, cleaned up display list name allocation
    # bruce 071030 renamed from setup to setup_drawer
    spherelistbase = glGenLists(numSphereSizes)
    global sphereList
    sphereList = []
    for i in range(numSphereSizes):
        sphereList += [spherelistbase+i]
        glNewList(sphereList[i], GL_COMPILE)
        glBegin(GL_TRIANGLES)
        ocdec = getSphereTriangles(i)
        for tri in ocdec:
            glNormal3fv(tri[0])
            glVertex3fv(tri[0])
            glNormal3fv(tri[1])
            glVertex3fv(tri[1])
            glNormal3fv(tri[2])
            glVertex3fv(tri[2])
        glEnd()
        glEndList()

    global wiresphere1list
    wiresphere1list = glGenLists(1) #bruce 060415
    glNewList(wiresphere1list, GL_COMPILE)
    didlines = {} # don't draw each triangle edge more than once
    def shoulddoline(v1,v2):
        v1 = tuple(v1) # make sure not list (unhashable) or Numeric array (bug in __eq__)
        v2 = tuple(v2)
        if (v1,v2) not in didlines:
            didlines[(v1,v2)] = didlines[(v2,v1)] = None
            return True
        return False
    def doline(v1,v2):
        if shoulddoline(v1,v2):
            glVertex3fv(v1)
            glVertex3fv(v2)
        return
    glBegin(GL_LINES)
    ocdec = getSphereTriangles(1)
    for tri in ocdec:
        #e could probably optim this more, e.g. using a vertex array or VBO or maybe GL_LINE_STRIP
        doline(tri[0], tri[1])
        doline(tri[1], tri[2])
        doline(tri[2], tri[0])
    glEnd()
    glEndList()

    global CylList
    CylList = glGenLists(1)
    glNewList(CylList, GL_COMPILE)
    glBegin(GL_TRIANGLE_STRIP)
    for (vtop, ntop, vbot, nbot) in cylinderEdges:
        glNormal3fv(nbot)
        glVertex3fv(vbot)
        glNormal3fv(ntop)
        glVertex3fv(vtop)
    glEnd()
    glEndList()

    global CapList
    CapList = glGenLists(1)
    glNewList(CapList, GL_COMPILE)
    glNormal3fv(cap0n)
    glBegin(GL_POLYGON)
    for p in drum0:
        glVertex3fv(p)
    glEnd()
    glNormal3fv(cap1n)
    glBegin(GL_POLYGON)
    for p in drum2: #bruce 060609 fix "ragged edge" bug in this endcap: drum1 -> drum2
        glVertex3fv(p)
    glEnd()
    glEndList()

    global diamondGridList
    diamondGridList = glGenLists(1)
    glNewList(diamondGridList, GL_COMPILE)
    glBegin(GL_LINES)
    for p in digrid:
        glVertex(p[0])
        glVertex(p[1])
    glEnd()
    glEndList()

    global lonsGridList
    lonsGridList = glGenLists(1)
    glNewList(lonsGridList, GL_COMPILE)
    glBegin(GL_LINES)
    global lonsEdges
    lonsEdges = _makeLonsCell()
    for p in lonsEdges:
        glVertex(p[0])
        glVertex(p[1])
    glEnd()
    glEndList()

    global CubeList
    CubeList = glGenLists(1)
    glNewList(CubeList, GL_COMPILE)
    glBegin(GL_QUAD_STRIP)
    # note: CubeList has only 4 faces of the cube; only suitable for use in wireframes;
    # see also solidCubeList [bruce 051215 comment reporting grantham 20051213 observation]
    glVertex((-1,-1,-1))
    glVertex(( 1,-1,-1))
    glVertex((-1, 1,-1))
    glVertex(( 1, 1,-1))
    glVertex((-1, 1, 1))
    glVertex(( 1, 1, 1))
    glVertex((-1,-1, 1))
    glVertex(( 1,-1, 1))
    glVertex((-1,-1,-1))
    glVertex(( 1,-1,-1))
    glEnd()
    glEndList()

    global solidCubeList
    solidCubeList = glGenLists(1)
    glNewList(solidCubeList, GL_COMPILE)
    glBegin(GL_QUADS)
    for i in xrange(len(cubeIndices)):
        avenormals = V(0,0,0) #bruce 060302 fixed normals for flat shading 
        for j in xrange(4) :    
            nTuple = tuple(cubeNormals[cubeIndices[i][j]])
            avenormals += A(nTuple)
        avenormals = norm(avenormals)
        for j in xrange(4) :    
            ## nTuple = tuple(cubeNormals[cubeIndices[i][j]])
            vTuple = tuple(cubeVertices[cubeIndices[i][j]])
            vTuple = A(vTuple) * 0.5 #bruce 060302 made size compatible with glut.glutSolidCube(1.0)
            glNormal3fv(avenormals)
            glVertex3fv(vTuple)
    glEnd()
    glEndList()                

    global rotSignList
    rotSignList = glGenLists(1)
    glNewList(rotSignList, GL_COMPILE)
    glBegin(GL_LINE_STRIP)
    for ii in xrange(len(rotS0n)):
        glVertex3fv(tuple(rotS0n[ii]))
    glEnd()
    glBegin(GL_LINE_STRIP)
    for ii in xrange(len(rotS1n)):
        glVertex3fv(tuple(rotS1n[ii]))
    glEnd()
    glBegin(GL_TRIANGLES)
    for v in arrow0Vertices + arrow1Vertices:
        glVertex3f(v[0], v[1], v[2])
    glEnd()
    glEndList()

    global linearArrowList
    linearArrowList = glGenLists(1)
    glNewList(linearArrowList, GL_COMPILE)
    glBegin(GL_TRIANGLES)
    for v in linearArrowVertices:
        glVertex3f(v[0], v[1], v[2])
    glEnd()
    glEndList()

    global linearLineList
    linearLineList = glGenLists(1)
    glNewList(linearLineList, GL_COMPILE)
    glEnable(GL_LINE_SMOOTH)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, -halfHeight)
    glVertex3f(0.0, 0.0, halfHeight)
    glEnd()
    glDisable(GL_LINE_SMOOTH)
    glEndList()

    global circleList
    circleList = glGenLists(1)
    glNewList(circleList, GL_COMPILE)
    glBegin(GL_LINE_LOOP)
    for ii in range(60):
        x = cos(ii*2.0*pi/60)
        y = sin(ii*2.0*pi/60)
        glVertex3f(x, y, 0.0)
    glEnd()    
    glEndList()

    global lineCubeList
    lineCubeList = glGenLists(1)
    glNewList(lineCubeList, GL_COMPILE)
    glBegin(GL_LINES)
    cvIndices = [0,1, 2,3, 4,5, 6,7, 0,3, 1,2, 5,6, 4,7, 0,4, 1,5, 2,6, 3,7]
    for i in cvIndices:
        glVertex3fv(tuple(cubeVertices[i]))
    glEnd()    
    glEndList()

    # Debug Preferences
    from debug_prefs import debug_pref, Choice_boolean_True
    from debug_prefs import Choice_boolean_False
    choices = [Choice_boolean_False, Choice_boolean_True]

    # 20060314 grantham
    initial_choice = choices[allow_color_sorting_default]
    allow_color_sorting_pref = debug_pref("Use Color Sorting?",
                                          initial_choice, prefs_key = allow_color_sorting_prefs_key)
        #bruce 060323 removed non_debug = True for A7 release, changed default value to False (far above),
        # and changed its prefs_key so developers start with the new default value.

    # 20060313 grantham Added use_c_renderer debug pref, can
    # take out when C renderer used by default.
    global use_c_renderer
    if quux_module_import_succeeded:
        initial_choice = choices[use_c_renderer_default]
        use_c_renderer = debug_pref("Use native C renderer?",
                                    initial_choice, prefs_key = use_c_renderer_prefs_key)
            #bruce 060323 removed non_debug = True for A7 release,
            # and changed its prefs_key so developers start over with the default value.

    #initTexture('C:\\Huaicai\\atom\\temp\\newSample.png', 128,128)
    return # from setup_drawer

def drawCircle(color, center, radius, normal):
    """Scale, rotate/translate the unit circle properly """
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix() 
    glColor3fv(color)
    glDisable(GL_LIGHTING)

    glTranslatef(center[0], center[1], center[2])
    rQ = Q(V(0, 0, 1), normal)
    rotAngle = rQ.angle*180.0/pi

    #This may cause problems as proved before in Linear motor display.
    #rotation around (0, 0, 0)
    #if vlen(V(rQ.x, rQ.y, rQ.z)) < 0.00005:
    #      rQ.x = 1.0

    glRotatef(rotAngle, rQ.x, rQ.y, rQ.z)
    glScalef(radius, radius, 1.0)
    glCallList(circleList)
    glEnable(GL_LIGHTING)
    glPopMatrix()
    return

def drawLinearArrows(longScale):   
    glCallList(linearArrowList)
    newPos = halfHeight*longScale
    glPushMatrix()
    glTranslate(0.0, 0.0, -newPos)
    glCallList(linearArrowList)
    glPopMatrix()
    glPushMatrix()
    glTranslate(0.0, 0.0, newPos -2.0*halfEdge)
    glCallList(linearArrowList)
    glPopMatrix()
    return

def drawLinearSign(color, center, axis, l, h, w):
    """Linear motion sign on the side of squa-linder """
    depthOffset = 0.005
    glPushMatrix()
    glColor3fv(color)
    glDisable(GL_LIGHTING)
    glTranslatef(center[0], center[1], center[2])

    ##Huaicai 1/17/05: To avoid rotate around (0, 0, 0), which causes 
    ## display problem on some platforms
    angle = -acos(axis[2])*180.0/pi
    if (axis[2]*axis[2] >= 1.0):
        glRotate(angle, 0.0, 1.0, 0.0)
    else:
        glRotate(angle, axis[1], -axis[0], 0.0)

    glPushMatrix()
    glTranslate(h/2.0 + depthOffset, 0.0, 0.0)
    glPushMatrix()
    glScale(1.0, 1.0, l)
    glCallList(linearLineList)
    glPopMatrix()
    if l < 2.6:
        sl = l/2.7
        glScale(1.0, sl, sl)
    if w < 1.0:
        glScale(1.0, w, w)
    drawLinearArrows(l)
    glPopMatrix()

    glPushMatrix()
    glTranslate(-h/2.0 - depthOffset, 0.0, 0.0)
    glRotate(180.0, 0.0, 0.0, 1.0)
    glPushMatrix()
    glScale(1.0, 1.0, l)
    glCallList(linearLineList)
    glPopMatrix()
    if l < 2.6:
        glScale(1.0, sl, sl)
    if w < 1.0:
        glScale(1.0, w, w)
    drawLinearArrows(l)
    glPopMatrix()

    glPushMatrix()
    glTranslate(0.0, w/2.0 + depthOffset, 0.0)
    glRotate(90.0, 0.0, 0.0, 1.0)
    glPushMatrix()
    glScale(1.0, 1.0, l)
    glCallList(linearLineList)
    glPopMatrix()
    if l < 2.6:
        glScale(1.0, sl, sl)
    if w < 1.0:
        glScale(1.0, w, w)
    drawLinearArrows(l)
    glPopMatrix()

    glPushMatrix()
    glTranslate(0.0, -w/2.0 - depthOffset, 0.0 )
    glRotate(-90.0, 0.0, 0.0, 1.0)
    glPushMatrix()
    glScale(1.0, 1.0, l)
    glCallList(linearLineList)
    glPopMatrix()
    if l < 2.6:
        glScale(1.0, sl, sl)
    if w < 1.0:
        glScale(1.0, w, w)
    drawLinearArrows(l)
    glPopMatrix()

    glEnable(GL_LIGHTING)
    glPopMatrix()
    return

def drawRotateSign(color, pos1, pos2, radius, rotation = 0.0):
    """Rotate sign on top of the caps of the cylinder """
    glPushMatrix()
    glColor3fv(color)
    vec = pos2-pos1
    axis = norm(vec)
    glTranslatef(pos1[0], pos1[1], pos1[2])

    ##Huaicai 1/17/05: To avoid rotate around (0, 0, 0), which causes 
    ## display problem on some platforms
    angle = -acos(axis[2])*180.0/pi
    if (axis[2]*axis[2] >= 1.0):
        glRotate(angle, 0.0, 1.0, 0.0)
    else:
        glRotate(angle, axis[1], -axis[0], 0.0)
    glRotate(rotation, 0.0, 0.0, 1.0) #bruce 050518
    glScale(radius,radius,Numeric.dot(vec,vec)**.5)

    glLineWidth(2.0)
    glDisable(GL_LIGHTING)
    glCallList(rotSignList)
    glEnable(GL_LIGHTING)
    glLineWidth(1.0)

    glPopMatrix()
    return

def drawsphere(color, pos, radius, detailLevel, opacity = 1.0):
    """Schedule a sphere for rendering whenever ColorSorter thinks is
    appropriate."""
    ColorSorter.schedule_sphere(color, 
                                pos, 
                                radius, 
                                detailLevel, 
                                opacity = opacity)

def drawwiresphere(color, pos, radius, detailLevel = 1):
    ## assert detailLevel == 1 # true, but leave out for speed
    from debug_prefs import debug_pref, Choice_boolean_True
    newway = debug_pref("new wirespheres?", Choice_boolean_True) #bruce 060415 experiment, re iMac G4 wiresphere bug; fixes it!
    oldway = not newway
    glColor3fv(color)
    glDisable(GL_LIGHTING)
    if oldway:
        glPolygonMode(GL_FRONT, GL_LINE)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    if oldway:
        glCallList(sphereList[detailLevel])
    else:
        glCallList(wiresphere1list)
    glEnable(GL_LIGHTING)
    glPopMatrix()
    if oldway:
        glPolygonMode(GL_FRONT, GL_FILL)
    return

def drawcylinder(color, pos1, pos2, radius, capped = 0, opacity = 1.0):
    """Schedule a cylinder for rendering whenever ColorSorter thinks is
    appropriate."""
    if 1:
        #bruce 060304 optimization: don't draw zero-length or almost-zero-length cylinders.
        # (This happens a lot, apparently for both long-bond indicators and for open bonds.
        #  The callers hitting this should be fixed directly! That might provide a further
        #  optim by making a lot more single bonds draw as single cylinders.)
        # The reason the threshhold depends on capped is in case someone draws a very thin
        # cylinder as a way of drawing a disk. But they have to use some positive length
        # (or the direction would be undefined), so we still won't permit zero-length then.
        cyllen = vlen(pos1 - pos2)
        if cyllen < (capped and 0.000000000001 or 0.0001):
            # uncomment this to find the callers that ought to be optimized
##            if env.debug(): #e optim or remove this test; until then it's commented out
##                print "skipping drawcylinder since length is only %5g" % (cyllen,), \
##                      "  (color is (%0.2f, %0.2f, %0.2f))" % (color[0], color[1], color[2])
            return
    ColorSorter.schedule_cylinder(color, pos1, pos2, radius, 
                                  capped = capped, opacity = opacity)

def drawsurface(color, pos, radius, tm, nm):
    """
    Schedule a surface for rendering whenever ColorSorter thinks is
    appropriate.
    """
    ColorSorter.schedule_surface(color, pos, radius, tm, nm)

def drawSineWave(color, startPoint, endPoint, numberOfPoints, phaseAngle):
    """
    """
    pass    

def drawLadder(endCenter1,  
               endCenter2,
               stepSize, 
               glpaneScale,
               lineOfSightVector,
               ladderWidth = 17.0,
               beamThickness = 2.0,
               beam1Color = None, 
               beam2Color = None,
               stepColor = None
               ):
    """
    Draw a ladder.      
    @param endCenter1: Ladder center at end 1
    @type endCenter1: B{V}
    @param endCenter2: Ladder center at end 2
    @type endCenter2: B{V}
    @param stepSize: Center to center distance between consecutive steps
    @type stepSize: float
    @param glpaneScale: GLPane scale used in scaling arrow head drawing 
    @type glpaneScale: float
    @param lineOfSightVector: Glpane lineOfSight vector, used to compute the 
                              the vector along the ladder step. 
    @type: B{V}    
    @param ladderWidth: width of the ladder
    @type ladderWidth: float
    @param beamThickness: Thickness of the two ladder beams
    @type beamThickness: float
    @param beam1Color: Color of beam1
    @param beam2Color: Color of beam2
    @see: B{DnaLineMode.Draw } (where it is used) for comments on color 
          convention
    """    
    
    arrowLengthVector  = V(0, 0, 0)
    arrowHeightVector = V(0, 0, 0)
            
    #Should this method be moved to DnaLineMode class? Don't know. Okay if it 
    #stays here in drawer.py
    
    ladderLength = vlen(endCenter1 - endCenter2)
    
    #Don't draw the vertical line (step) passing through the startpoint unless 
    #the ladderLength is atleast equal to the stepSize. 
    # i.e. do the drawing only when there are atleast two ladder steps. 
    # This prevents a 'revolving line' effect due to the single ladder step at 
    # the first endpoint 
    if ladderLength < stepSize:
        return
    
    unitVector = norm(endCenter2 - endCenter1)
    
    glDisable(GL_LIGHTING) 
    glPushMatrix()
    glTranslatef(endCenter1[0], endCenter1[1], endCenter1[2]) 
    pointOnAxis = V(0, 0, 0)
        
    vectorAlongLadderStep =  cross(-lineOfSightVector, unitVector)
    unitVectorAlongLadderStep = norm(vectorAlongLadderStep)
       
    ladderBeam1Point = pointOnAxis + unitVectorAlongLadderStep*0.5*ladderWidth    
    ladderBeam2Point = pointOnAxis - unitVectorAlongLadderStep*0.5*ladderWidth
    
    #Following limits the arrowHead Size to the given value. When you zoom out, 
    #the rest of ladder drawing becomes smaller (expected) and the following
    #check ensures that the arrowheads are drawn proportinately. 
    # (Not using a 'constant' to do this as using glpaneScale gives better 
    #results)
    if glpaneScale > 40:
        arrowDrawingScale = 40
    else:
        arrowDrawingScale = glpaneScale
     #Draw the arrow head on beam1  
    drawArrowHead(beam2Color, 
                  ladderBeam2Point, 
                  arrowDrawingScale,
                  -unitVectorAlongLadderStep, 
                  - unitVector)
            
    x = 0.0
    while x < ladderLength:        
        drawPoint(stepColor, pointOnAxis)
        
        previousPoint = pointOnAxis        
        previousLadderBeam1Point = ladderBeam1Point
        previousLadderBeam2Point = ladderBeam2Point

        pointOnAxis = pointOnAxis + unitVector*stepSize		
        x += stepSize

        ladderBeam1Point = previousPoint + unitVectorAlongLadderStep*0.5*ladderWidth
        ladderBeam2Point = previousPoint - unitVectorAlongLadderStep*0.5*ladderWidth
        
        if previousLadderBeam1Point:
            drawline(beam1Color, 
                     previousLadderBeam1Point, 
                     ladderBeam1Point, 
                     width = beamThickness,
                     isSmooth = True )

            drawline(beam2Color, 
                     previousLadderBeam2Point, 
                     ladderBeam2Point, 
                     width = beamThickness, 
                     isSmooth = True )
            
            drawline(stepColor, ladderBeam1Point, ladderBeam2Point)
            
    drawArrowHead(beam1Color, 
                  ladderBeam1Point,
                  arrowDrawingScale,
                  unitVectorAlongLadderStep, 
                  unitVector)                       
    glPopMatrix()
    glEnable(GL_LIGHTING)



def drawRibbons(endCenter1,  
               endCenter2,
               stepSize, 
               glpaneScale,
               lineOfSightVector,
               peakDeviationFromCenter = 9.5,
               ribbonThickness = 2.0,
               ribbon1Color = None, 
               ribbon2Color = None,
               stepColor = None):
    """
    Draw dna ribbons. (each strand represented as a ribbon) The dna ribbons are 
    drawn as sine waves with appropriate phase angles. (phase angles computed
    in this method)
    
    @param endCenter1: Axis end 1
    @type endCenter1: B{V}
    @param endCenter2: Axis end 2
    @type endCenter2: B{V}
    @param stepSize: Center to center distance between consecutive steps
    @type stepSize: float
    @param glpaneScale: GLPane scale used in scaling arrow head drawing 
    @type glpaneScale: float
    @param lineOfSightVector: Glpane lineOfSight vector, used to compute the 
                              the vector along the ladder step. 
    @type: B{V}    
    @param peakDeviationFromCenter: Distance of a peak from the axis 
                                    Also known as 'Amplitude' of a sine wave. 
    @type peakDeviationFromCenter: float
    @param ribbonThickness: Thickness of each of the the two ribbons
    @type ribbonThickness: float
    @param ribbon1Color: Color of ribbon1
    @param ribbon2Color: Color of ribbon2
    @see: B{DnaLineMode.Draw } (where it is used) for comments on color 
          convention
          
    TODO: 
      - See if a direct formula for a helix can be used. May not be necessary 
      -  This method is long mainly because of a number of custom drawing 
         See if that can be refactored e.g. methods like _drawRibbon1/strand1, 
         drawRibbon2 / strand2 etc. 
      - Further optimization / refactoring (low priority) 
      - Should this method be moved to something like 'dna_srawer.py' ? 
    """
    #Should this method be moved to DnaLineMode class or a new dna_drawer.py?
    #Okay if it stays here in drawer.py    
    ribbonLength = vlen(endCenter1 - endCenter2)
    
    #Don't draw the vertical line (step) passing through the startpoint unless 
    #the ribbonLength is atleast equal to the stepSize. 
    # i.e. do the drawing only when there are atleast two ladder steps. 
    # This prevents a 'revolving line' effect due to the single ladder step at 
    # the first endpoint 
    if ribbonLength < stepSize:
        return
    
    unitVectorAlongLength = norm(endCenter2 - endCenter1)
         
    glDisable(GL_LIGHTING) 
    glPushMatrix()
    glTranslatef(endCenter1[0], endCenter1[1], endCenter1[2]) 
    pointOnAxis = V(0, 0, 0)
        
    vectorAlongLadderStep =  cross(-lineOfSightVector, unitVectorAlongLength)
    unitVectorAlongLadderStep = norm(vectorAlongLadderStep)    
   
    #Following limits the arrowHead Size to the given value. When you zoom out, 
    #the rest of ladder drawing becomes smaller (expected) and the following
    #check ensures that the arrowheads are drawn proportinately. 
    # (Not using a 'constant' to do this as using glpaneScale gives better 
    #results)
    if glpaneScale > 40:
        arrowDrawingScale = 40
    else:
        arrowDrawingScale = glpaneScale
    
    #Formula .. Its a Sine Wave.
    # y(x) = A.sin(2*pi*f*x + phase_angle)  ------[1]
    # where --
    #      f = 1/T 
    #      A = Amplitude of the sine wave (or 'peak deviation from center') 
    #      y = y coordinate  of the sine wave -- distance is in Angstroms
    #      x = the x coordinate
    # phase_angle is computed for each wave. We know y at x =0. For example, 
    # for ribbon_1, , at x = 0, y = A. Putting these values in equation [1] 
    # we get the phase_angle. Similarly, for ribbon_2, at x = 0, y = -6 
    # Putting these values will give use the phase_angle_2. 
    # Note that for ribbon2_point, we subtract the value of equation [1] from 
    # the point on axis. 
                      
    x = 0.0
    T =  stepSize * 10 # The 'Period' of the sine wave (i.e.peak to peak 
                       # distance between consecutive crests)
              
    amplitude = peakDeviationFromCenter
    amplitudeVector = unitVectorAlongLadderStep*amplitude
              
    phase_angle_ribbon_1 = HALF_PI    
    theta_ribbon_1 = (TWICE_PI*x/T) + phase_angle_ribbon_1
    
    phase_angle_ribbon_2 = asin(-6.0/(amplitude))
    theta_ribbon_2 = (TWICE_PI*x/T) - phase_angle_ribbon_2    
    
    #Initialize ribbon1_point and ribbon2_point
    ribbon1_point = pointOnAxis + amplitudeVector*sin(theta_ribbon_1)    
    ribbon2_point = pointOnAxis - amplitudeVector*sin(theta_ribbon_2)
    
    #Constants for drawing the ribbon points as spheres.
    SPHERE_RADIUS = 1.0
    SPHERE_DRAWLEVEL = 2
    SPHERE_OPACITY = 1.0
    
    #Constants for drawing the second axis end point (as a sphere). 
    AXIS_ENDPOINT_SPHERE_COLOR = white
    AXIS_ENDPOINT_SPHERE_RADIUS = 1.0
    AXIS_ENDPOINT_SPHERE_DRAWLEVEL = 2
    AXIS_ENDPOINT_SPHERE_OPACITY = 0.5
    
    while x < ribbonLength:          
        #Draw the axis point.
        drawPoint(stepColor, pointOnAxis)       
        
        previousPointOnAxis = pointOnAxis        
        previous_ribbon1_point = ribbon1_point
        previous_ribbon2_point = ribbon2_point
        
        theta_ribbon_1 = (TWICE_PI*x/T) + phase_angle_ribbon_1
        theta_ribbon_2 = (TWICE_PI*x/T) - phase_angle_ribbon_2
        
        ribbon1_point = previousPointOnAxis + amplitudeVector*sin(theta_ribbon_1)
        ribbon2_point = previousPointOnAxis - amplitudeVector*sin(theta_ribbon_2)
        
        #Use previous_ribbon1_point and not ribbon1_point. This ensures that 
        # the 'last point' on ribbon1 is not drawn as a sphere but is drawn as 
        #an arrowhead. (that arrow head is drawn later , after the while loop) 
        drawsphere(ribbon1Color, 
                   previous_ribbon1_point, 
                   SPHERE_RADIUS,
                   SPHERE_DRAWLEVEL,
                   opacity = SPHERE_OPACITY)       
               
        if x != 0.0:
            # For ribbon_2 , don't draw the first sphere (when x = 0) , instead 
            # an arrow head will be drawnfor y at x = 0 
            # (see condition x == stepSize )
            drawsphere(ribbon2Color, 
                       ribbon2_point, 
                       SPHERE_RADIUS,
                       SPHERE_DRAWLEVEL,
                       opacity = SPHERE_OPACITY)
            
        if x == stepSize:   
            # For ribbon_2 we need to draw an arrow head for y at x = 0. 
            # To do this, we need the 'next ribbon_2' point in order to 
            # compute the appropriate vectors. So when x = stepSize, the 
            # previous_ribbon2_point is nothing but y at x = 0. 
            arrowLengthVector2  = norm(ribbon2_point - previous_ribbon2_point )              
            arrowHeightVector2  = cross(-lineOfSightVector, arrowLengthVector2)            
            drawArrowHead( ribbon2Color, 
                           previous_ribbon2_point,
                           arrowDrawingScale,
                           - arrowHeightVector2, 
                           - arrowLengthVector2)
            
        #Increament the pointOnAxis and x
        pointOnAxis = pointOnAxis + unitVectorAlongLength*stepSize        
        x += stepSize
  
        if previous_ribbon1_point:
            drawline(ribbon1Color, 
                     previous_ribbon1_point, 
                     ribbon1_point,
                     width = ribbonThickness,
                     isSmooth = True )
            arrowLengthVector1  = norm(ribbon1_point - previous_ribbon1_point)
            arrowHeightVector1 = cross(-lineOfSightVector, arrowLengthVector1)
            
            drawline(ribbon2Color, 
                     previous_ribbon2_point, 
                     ribbon2_point,
                     width = ribbonThickness,
                     isSmooth = True )            
            
            drawline(stepColor, ribbon1_point, ribbon2_point)
           
    #Arrow head for endpoint of ribbon_1. 
    drawArrowHead(ribbon1Color, 
                  ribbon1_point,
                  arrowDrawingScale,
                  arrowHeightVector1, 
                  arrowLengthVector1) 
    
    #The second axis endpoint of the dna is drawn as a transparent sphere. 
    #Note that the second axis endpoint is NOT NECESSARILY endCenter2 . In fact 
    # those two are equal only at the ladder steps. In other case (when the
    # ladder step is not completed, the endCenter1 is ahead of the 
    #'second axis endpoint of the dna' 
    drawsphere(AXIS_ENDPOINT_SPHERE_COLOR, 
               previousPointOnAxis, 
               AXIS_ENDPOINT_SPHERE_RADIUS,
               AXIS_ENDPOINT_SPHERE_DRAWLEVEL,
               opacity = AXIS_ENDPOINT_SPHERE_OPACITY)

                  
    glPopMatrix()
    glEnable(GL_LIGHTING)
        
    
def drawArrowHead(color, 
                  basePoint, 
                  drawingScale, 
                  unitBaseVector, 
                  unitHeightVector):
    
    arrowBase = drawingScale*0.08
    arrowHeight = drawingScale*0.12
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glTranslatef(basePoint[0],basePoint[1],basePoint[2])
    point1 = V(0, 0, 0)
    point1 = point1 + unitHeightVector*arrowHeight    
    point2 =  unitBaseVector*arrowBase    
    point3 = - unitBaseVector*arrowBase
    #Draw the arrowheads as filled triangles
    glColor3fv(color)
    glBegin(GL_POLYGON)
    glVertex3fv(point1)
    glVertex3fv(point2)
    glVertex3fv(point3)
    glEnd()    
    glPopMatrix()
    glEnable(GL_LIGHTING)

def drawline(color, 
             endpt1, 
             endpt2, 
             dashEnabled = False, 
             stipleFactor = 1,
             width = 1, 
             isSmooth = False):
    """
    Draw a line from endpt1 to endpt2 in the given color. 
    
    If endpt1 and endpt2 are the same point, nothing is drawn. This is 
    considered and used as a feature.
    
    @param endpt1: First endpoint.
    @type  endpt1: Triple tuple.
    
    @param endpt2: Second endpoint.
    @type  endpt2: Triple tuple.

    @param dashEnabled: If dashEnabled is True, it will be dashed.
    @type  dashEnabled: boolean
    
    @param stipleFactor: The stiple factor.
    @param stipleFactor: int
    
    @param width: The line width in pixels. The default is 1.0.
    @type  width: float
    
    @param isSmooth: Enables GL_LINE_SMOOTH. The default is False.
    @type  isSmooth: boolean
    
    @note: Whether the line is antialiased is determined by GL state variables
    which are not set in this function.
    """
    # WARNING: some callers pass dashEnabled as a positional argument rather than a named argument.
    # [bruce 050831 added docstring, this comment, and the width argument.]
    
    if endpt1 is endpt2:
        return
    
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    if dashEnabled: 
        glLineStipple(stipleFactor, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
    if width != 1:
        glLineWidth(width)
    if isSmooth:
        glEnable(GL_LINE_SMOOTH)
    glBegin(GL_LINES)
    glVertex(endpt1[0], endpt1[1], endpt1[2])
    glVertex(endpt2[0], endpt2[1], endpt2[2])
    glEnd()
    if isSmooth:
        glDisable(GL_LINE_SMOOTH)
    if width != 1:
        glLineWidth(1.0) # restore default state
    if dashEnabled: 
        glDisable(GL_LINE_STIPPLE)
    glEnable(GL_LIGHTING)
    return

def drawPolyLine(color, points):
    '''Draws a poly line passing through the given list of points'''
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINE_STRIP)
    for v in points:
        glVertex3fv(v)
    glEnd()

    glEnable(GL_LIGHTING)
    return

def drawPoint(color, 
              point, 
              pointSize = 3.0,
              isRound = True):
    """
    Draw a point using GL_POINTS. 
    @param point: The x,y,z coordinate array/ vector of the point 
    @type point: A or V
    @param pointSize: The point size to be used by glPointSize
    @type pointSize: float
    @param isRound: If True, the point will be drawn round otherwise square
    @type isRound: boolean
    """
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glPointSize(float(pointSize))
    if isRound:
        glEnable(GL_POINT_SMOOTH)
    glBegin(GL_POINTS)
    glVertex3fv(point)       
    glEnd()
    if isRound:
        glDisable(GL_POINT_SMOOTH)

    glEnable(GL_LIGHTING)
    if pointSize != 1.0:
        glPointSize(1.0)
    return

def drawTag(color, basePoint, endPoint, pointSize = 20.0):
    """
    Draw a tag (or a 'flag') as a line ending with a circle (like a balloon 
    with a string). Note: The word 'Flag' is intentionally not used in the 
    method nameto avoid potential confusion with a boolean flag.
    
    @param color: color of the tag 
    @type color: A
    @param basePoint: The base point of the tag 
    @type basePoint: V
    @param endPoint: The end point of the tag 
    @type endPoint: V
    @param pointSize: The pointSize of the point to be drawin at the <endPoint>
    @type  pointSize: float
    
    @see: GraphicsMode._drawTags where it is called (an example)
    
    """
    drawline(color, basePoint, endPoint)
    drawPoint(color, endPoint, pointSize = 20.0)

def drawLineCube(color, pos, radius):
    vtIndices = [0,1,2,3, 0,4,5,1, 5,4,7,6, 6,7,3,2]
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, flatCubeVertices) #bruce 051117 revised this
        #grantham 20051213 observations, reported/paraphrased by bruce 051215:
        # - should verify PyOpenGL turns Python float (i.e. C double) into C float
        #   for OpenGL's GL_FLOAT array element type.
        # - note that GPUs are optimized for DrawElements types GL_UNSIGNED_INT and GL_UNSIGNED_SHORT.
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    glDrawElements(GL_LINE_LOOP, 4, GL_UNSIGNED_BYTE, vtIndices)
    #glDrawElements(GL_LINE_LOOP, 4, GL_UNSIGNED_BYTE, vtIndices[4])
    #glDrawElements(GL_LINE_LOOP, 4, GL_UNSIGNED_BYTE, vtIndices[8])
    #glDrawElements(GL_LINE_LOOP, 4, GL_UNSIGNED_BYTE, vtIndices[12])
    glPopMatrix()
    glEnable(GL_LIGHTING)
    glDisableClientState(GL_VERTEX_ARRAY)
    return    

def drawwirecube(color, pos, radius, lineWidth=3.0):
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    if type(radius) == type(1.0):
        glScale(radius,radius,radius)
    else: 
        glScale(radius[0], radius[1], radius[2])
    glLineWidth(lineWidth)
    glCallList(lineCubeList)
    glLineWidth(1.0) ## restore its state
    glPopMatrix()
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)
    glPolygonMode(GL_BACK, GL_FILL) #bruce 050729 to help fix bug 835 or related bugs
    return

def drawwirebox(color, pos, len):
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(len[0], len[1], len[2])
    glCallList(CubeList)
    glPopMatrix()
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)
    glPolygonMode(GL_BACK, GL_FILL) #bruce 050729 to help fix bug 835 or related bugs
    return

def segstart(color):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINES)
    return

def drawsegment(pos1,pos2):
    glVertex3fv(pos1)
    glVertex3fv(pos2)
    return

def segend():
    glEnd()
    glEnable(GL_LIGHTING)
    return

def drawRulers(glpane):
    """
    Draws a vertical ruler on the left side of the 3D graphics area.
    
    @param glpane: the 3D graphics area.
    @type  glpane: L{GLPane)
    
    @note: tickmarks are not rendered as 1 pixel wide lines. I believe this
    is a bug in drawline(). Mark 2008-02-04.
    """    
    from constants import GL_NEAR_Z
    from constants import darkgray
    
    color = darkgray
    
    scale = glpane.scale
    aspect = glpane.aspect
    
    font_size = 8
    short_tickmark_threshold = 150
    angstrom_tickmark_range = 25 # tickmarks
    
    num_horz_ticks = 2 * int(scale) + 1
    
    if num_horz_ticks < angstrom_tickmark_range:
        units_text = "A" # Angstroms
        units_scale = 1.0
    else:
        units_text = "nm" # nanometers
        units_scale = 0.1
        
    horz_tick_inc = 1.0 / scale
    horz_long_tick_len = .05
    vert_long_tick_len = horz_long_tick_len * aspect
    horz_short_tick_len = .02
    vert_short_tick_len = horz_short_tick_len * aspect
    
    horz_ruler_offset = vert_long_tick_len
    vert_ruler_offset = horz_long_tick_len
    
    if 0:
        print "number of ticks=", num_horz_ticks, "scale=", scale
    
    units_text_origin = V(-1.0 + .01,
                           1.0 - (vert_long_tick_len *.75),
                           GL_NEAR_Z)
    
    # Draw unit of measurement in upper left corner (A or nm).
    drawtext(units_text, darkgray, units_text_origin, font_size, glpane)
    
    pt1 = V(-1.0, 1.0 - vert_long_tick_len, GL_NEAR_Z)
    pt2 = pt1 + (horz_long_tick_len, 0.0, 0.0)
    
    tick_num = 0
    
    # Draw horizontal ruler tickmarks and numberic unit labels
    for i in range(num_horz_ticks):
        
        drawline(darkgray, pt1, pt2)
        
        # Draw units number below tickmark.
        if not tick_num % 5:
            units_num_origin = pt1 + (0.025, -0.03, 0.0)
            if units_text == "nm":
                if num_horz_ticks <= 100:
                    units_num = "%-4.1f" % (tick_num * units_scale)
                else:
                    units_num = "%2d" % (tick_num * units_scale)
                    if tick_num % 2:
                        # Only display even unit numbers.
                        units_num = ""
            else:
                units_num = "%2d" % tick_num
            drawtext(units_num, darkgray, units_num_origin, font_size, glpane)
        
        # Update tickmark endpoints for next tickmark.
        pt1 += (0.0, -horz_tick_inc, 0.0)
        
        if (tick_num + 1) % 5:
            # pt2 will be the endpoint of a short tickmark.
            if num_horz_ticks > short_tickmark_threshold:
                # Setting pt2 to pt1 results in no tickmark being rendered.
                pt2 = pt1
            else:
                pt2 = pt1 + (horz_short_tick_len, 0.0, 0.0)
        else:
            if (num_horz_ticks > short_tickmark_threshold) and ((tick_num + 1) % 2):
                pt2 = pt1 + (horz_short_tick_len, 0.0, 0.0)
            else:
                pt2 = pt1 + (horz_long_tick_len, 0.0, 0.0)
        
        tick_num += 1
    
    return # from drawRulers
    
def drawAxis(color, pos1, pos2, width = 2): #Ninad 060907
    '''Draw chunk or jig axis'''
    #ninad060907 Note that this is different than draw 
    #I may need this function to draw axis line. see its current implementation in 
    #branch "ninad_060908_drawAxis_notAsAPropOfObject"
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glLineStipple(3, 0x1C47) # dash-dot-dash line
    glEnable(GL_LINE_STIPPLE)
    if width != 1:
        glLineWidth(width)
    glBegin(GL_LINES)
    glVertex(pos1[0], pos1[1], pos1[2])
    glVertex(pos2[0], pos2[1], pos2[2])
    glEnd()
    if width != 1:
        glLineWidth(1.0) # restore default state
    glDisable(GL_LINE_STIPPLE)
    glEnable(GL_LIGHTING)
    return

def drawaxes(n,point,coloraxes=False, dashEnabled = False):
    from constants import blue, red, darkgreen

    n *= 0.5
    glPushMatrix()
    glTranslate(point[0], point[1], point[2])
    glDisable(GL_LIGHTING)

    if coloraxes: 
        glColor3f(red[0], red[1], red[2])
        if dashEnabled:
            #ninad060921 Note that we will only support dotted origin axis 
            #(hidden lines)but not POV axis. (as it could be annoying)
            glLineStipple(5, 0xAAAA)
            glEnable(GL_LINE_STIPPLE)
            glDisable(GL_DEPTH_TEST)
    else:
        glColor3f(darkgreen[0], darkgreen[1], darkgreen[2])

    glBegin(GL_LINES)
    glVertex(n,0,0)
    glVertex(-n,0,0)
    glColor3f(darkgreen[0], darkgreen[1], darkgreen[2])
    glVertex(0,n,0)
    glVertex(0,-n,0)
    if coloraxes: glColor3f(blue[0], blue[1], blue[2])
    else: glColor3f(darkgreen[0], darkgreen[1], darkgreen[2])
    glVertex(0,0,n)
    glVertex(0,0,-n)
    glEnd()

    if coloraxes:
        if dashEnabled:
            glDisable(GL_LINE_STIPPLE)
            glEnable(GL_DEPTH_TEST)

    glEnable(GL_LIGHTING)
    glPopMatrix()
    return
    
def drawOriginAsSmallAxis(scale, origin, dashEnabled = False):
    """
    Draws a small wireframe version of the origin. It is rendered as a 
    3D point at (0, 0, 0) with 3 small axes extending from it the positive
    X, Y, Z directions.
    """
    #Perhaps we should split this method into smaller methods? ninad060920
    #Notes:
    #1. drawing arrowheads implemented on 060918
    #2. ninad060921 Show the origin axes as dotted if behind the mode. 
    #3. ninad060922 The arrow heads are drawn as wireframe cones if behind the object
    # the arrowhead size is slightly smaller (otherwise some portion of the 
    # the wireframe arrow shows up!
    #3.Making origin non-zoomable is acheived by replacing 
    #hardcoded 'n' with glpane's scale - ninad060922

    from constants import blue, red, darkgreen, black, lightblue

    #ninad060922 in future , the following could be user preferences. 
    if (dashEnabled):
        dashShrinkage = 0.9
    else:
        dashShrinkage=1
    x1, y1, z1 = scale * 0.01, scale * 0.01, scale * 0.01
    xEnd, yEnd, zEnd = scale * 0.04, scale * 0.09, scale * 0.025
    arrowBase = scale * 0.0075 * dashShrinkage
    arrowHeight = scale * 0.035 * dashShrinkage
    lineWidth = 1.0

    glPushMatrix()

    glTranslate(origin[0], origin[1], origin[2])
    glDisable(GL_LIGHTING)
    glLineWidth(lineWidth)

    gleNumSides = gleGetNumSides()
    #Code to show hidden lines of the origin if some model obscures it  ninad060921
    if dashEnabled:
        glLineStipple(2, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
        glDisable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        gleSetNumSides(5)   
    else:   
        gleSetNumSides(10)

    glBegin(GL_LINES)

    #glColor3f(black)
    glColor3fv(lightblue)

    #start draw a point at origin . 
    #ninad060922 is thinking about using GL_POINTS here

    glVertex(-x1, 0.0, 0.0)
    glVertex( x1, 0.0, 0.0)
    glVertex(0.0, -y1, 0.0)
    glVertex(0.0,  y1, 0.0)
    glVertex(-x1,  y1,  z1)
    glVertex( x1, -y1, -z1)    
    glVertex(x1,   y1,  z1)
    glVertex(-x1, -y1, -z1)    
    glVertex(x1,   y1, -z1)
    glVertex(-x1, -y1,  z1)    
    glVertex(-x1,  y1, -z1)
    glVertex(x1,  -y1,  z1)   
    #end draw a point at origin 

    #start draw small origin axes
    #glColor3fv(darkred)
    glColor3fv(lightblue)
    glVertex(xEnd, 0.0, 0.0)
    glVertex( 0.0, 0.0, 0.0)
    #glColor3f(darkgreen[0], darkgreen[1], darkgreen[2])
    glColor3fv(lightblue)
    glVertex(0.0, yEnd, 0.0)
    glVertex(0.0,  0.0, 0.0)
    #glColor3f(blue[0], blue[1], blue[2])
    glColor3fv(lightblue)
    glVertex(0.0, 0.0, zEnd)
    glVertex(0.0, 0.0,  0.0)
    glEnd() #end draw lines
    glLineWidth(1.0)

    glPopMatrix() # end push matrix for drawing various lines in the origin and axes

    #start draw solid arrow heads  for  X , Y and Z axes
    glPushMatrix() 
    glDisable(GL_CULL_FACE)
    #glColor3fv(darkred)
    glColor3fv(lightblue)
    glTranslatef(xEnd, 0.0, 0.0)
    glRotatef(90, 0.0, 1.0, 0.0)

    glePolyCone([[0, 0, -1], [0, 0, 0], [0, 0, arrowHeight], [0, 0, arrowHeight+1]], None, [arrowBase, arrowBase, 0, 0])

    glPopMatrix()

    glPushMatrix()
    #glColor3f(darkgreen)
    glColor3fv(lightblue)
    glTranslatef(0.0, yEnd, 0.0)
    glRotatef(-90, 1.0, 0.0, 0.0)

    glePolyCone([[0, 0, -1], [0, 0, 0], [0, 0, arrowHeight], [0, 0, arrowHeight+1]], None, [arrowBase, arrowBase, 0, 0])

    glPopMatrix()

    glPushMatrix()
    glColor3fv(lightblue)
    glTranslatef(0.0,0.0,zEnd)

    glePolyCone([[0, 0, -1], [0, 0, 0], [0, 0, arrowHeight], [0, 0, arrowHeight+1]], None, [arrowBase, arrowBase, 0, 0])

    #Disable line stipple and Enable Depth test
    if dashEnabled:
        glLineStipple(1, 0xAAAA)
        glDisable(GL_LINE_STIPPLE)
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    gleSetNumSides(gleNumSides)
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPopMatrix() 
    #end draw solid arrow heads  for  X , Y and Z axes
    return

def drawDirectionArrow(color, tailPoint, arrowBasePoint, 
                       scale, flipDirection = False):
    '''Draw a directional arrow staring at <tailPoint>
	with an endpoint decided by the vector between 
	<arrowBasePoint> and <tailPoint> and the glpane scale <scale>
	'''

    vec = arrowBasePoint - tailPoint
    vec = scale*0.07*vec
    radius = vlen(vec)*0.07
    arrowBase =  radius*2.0
    arrowHeight =  arrowBase*2.0
    axis = norm(vec)

    scaledBasePoint = tailPoint + vlen(vec)*axis

    drawcylinder(color, tailPoint, scaledBasePoint, radius, capped = True)

    #start draw solid arrow heads
    glPushMatrix() 
    glColor3fv(color)
    glTranslatef(scaledBasePoint[0],scaledBasePoint[1], scaledBasePoint[2])

    if flipDirection:
        glRotatef(0,0.0,1.0,0.0)
    else:
        glRotatef(180,0.0,1.0,0.0)


    glePolyCone([[0, 0, -1], 
                 [0, 0, 0], 
                 [0, 0, arrowHeight], 
                 [0, 0, arrowHeight+1]], 
                 None, 
                 [arrowBase, arrowBase, 0, 0])

    glPopMatrix()


def findCell(pt, latticeType):
    """Return the cell which contains the point <pt> """
    if latticeType == 'DIAMOND':
        a = 0; cellX = cellY = cellZ = DiGridSp
    elif latticeType == 'LONSDALEITE':
        a = 1; cellX = XLen; cellY = YLen; cellZ = ZLen

    i = int(floor(pt[0]/cellX))
    j = int(floor(pt[1]/cellY))
    k = int(floor(pt[2]/cellZ))

    orig = V(i*cellX, j*cellY, k*cellZ)

    return orig, sp1

def genDiam(bblo, bbhi, latticeType):
    """Generate a list of possible atom positions within the area enclosed by (bblo, bbhi).
    <Return>: A list of unit cells"""
    if latticeType == 'DIAMOND':
        a = 0; cellX = cellY = cellZ = DiGridSp
    elif latticeType == 'LONSDALEITE':
        a = 1; cellX = XLen; cellY = YLen; cellZ = ZLen

    allCells = []    
    for i in range(int(floor(bblo[0]/cellX)),
                   int(ceil(bbhi[0]/cellX))):
        for j in range(int(floor(bblo[1]/cellY)),
                       int(ceil(bbhi[1]/cellY))):
            for k in range(int(floor(bblo[2]/cellZ)),
                           int(ceil(bbhi[2]/cellZ))):
                off = V(i*cellX, j*cellY, k*cellZ)
                if a == 0: allCells += [digrid + off]
                elif a ==1: allCells += [lonsEdges + off]
    return allCells  


def drawGrid(scale, center, latticeType):
    """Construct the grid model and show as position references for cookies.
    The model is build around "pov" and has size of 2*"scale" on each of the (x, y, z) directions.
    This should be optimized latter. For "scale = 200", it takes about 1479623 loops. ---Huaicai
    """
    glDisable(GL_LIGHTING)

    # bruce 041201:
    #   Quick fix to prevent "hang" from drawing too large a cookieMode grid
    # with our current cubic algorithm (bug 8). The constant 120.0 is still on
    # the large side in terms of responsiveness -- on a 1.8GHz iMac G5 it can
    # take many seconds to redraw the largest grid, or to update a selection
    # rectangle during a drag. I also tried 200.0 but that was way too large.
    # Since some users have slower machines, I'll be gentle and put 90.0 here.
    #   Someday we need to fix the alg to be quadratic by teaching this code
    # (and the cookie baker code too) about the eyespace clipping planes. 
    #   Once we support user prefs, this should be one of them (if the alg is
    # not fixed by then).

    MAX_GRID_SCALE = 90.0
    if scale > MAX_GRID_SCALE:
        scale = MAX_GRID_SCALE

    if latticeType == 'DIAMOND':
        cellX = cellY = cellZ = DiGridSp
    elif latticeType == 'LONSDALEITE':
        cellX = XLen; cellY = YLen; cellZ = ZLen

    bblo = center - scale
    bbhi = center + scale
    i1 = int(floor(bblo[0]/cellX))
    i2 = int(ceil(bbhi[0]/cellX))
    j1 = int(floor(bblo[1]/cellY))
    j2 = int(ceil(bbhi[1]/cellY))
    k1 = int(floor(bblo[2]/cellZ))
    k2 = int(ceil(bbhi[2]/cellZ))
    glPushMatrix()
    glTranslate(i1*cellX,  j1*cellY, k1*cellZ)
    for i in range(i1, i2):
        glPushMatrix()
        for j in range(j1, j2):
            glPushMatrix()
            for k in range(k1, k2):
                if latticeType == 'DIAMOND':
                    glCallList(diamondGridList)
                else:
                    glCallList(lonsGridList)
                glTranslate(0.0,  0.0, cellZ)
            glPopMatrix()
            glTranslate(0.0,  cellY, 0.0)
        glPopMatrix()
        glTranslate(cellX, 0.0, 0.0)
    glPopMatrix()
    glEnable(GL_LIGHTING)

    #drawCubeCell(V(1, 0, 0))
    return


def drawrectangle(pt1, pt2, rt, up, color):
    glColor3f(color[0], color[1], color[2])
    glDisable(GL_LIGHTING)
    c2 = pt1 + rt*Numeric.dot(rt,pt2-pt1)
    c3 = pt1 + up*Numeric.dot(up,pt2-pt1)
    glBegin(GL_LINE_LOOP)
    glVertex(pt1[0],pt1[1],pt1[2])
    glVertex(c2[0],c2[1],c2[2])
    glVertex(pt2[0],pt2[1],pt2[2])
    glVertex(c3[0],c3[1],c3[2])
    glEnd()
    glEnable(GL_LIGHTING)

#bruce & wware 060404: drawRubberBand apparently caused bug 1814 (Zoom Tool hanging some Macs, requiring power toggle)
# so it should not be used until debugged. Use drawrectangle instead. (For an example of how to translate between them,
# see ZoomMode.py rev 1.32 vs 1.31 in ViewCVS.) That bug was only repeatable on Bruce's & Will's iMacs G5.
#
# Bruce's speculations (not very definite; no evidence for them at all) about possible causes of the bug in drawRubberBand:
# - use of glVertex instead of glVertex3f or so??? This seems unlikely, since we have other uses of it,
#   but perhaps they work due to different arg types.
# - use of GL_LINE_LOOP within OpenGL xor mode, and bugs in some OpenGL drivers?? I didn't check whether cookieMode does this too.
##def drawRubberBand(pt1, pt2, c2, c3, color):
##    """Huaicai: depth test should be disabled to make the xor work """
##    glBegin(GL_LINE_LOOP)
##    glVertex(pt1[0],pt1[1],pt1[2])
##    glVertex(c2[0],c2[1],c2[2])
##    glVertex(pt2[0],pt2[1],pt2[2])
##    glVertex(c3[0],c3[1],c3[2])
##    glEnd()
##    return


# Wrote drawbrick for the Linear Motor.  Mark [2004-10-10]
def drawbrick(color, center, axis, l, h, w, opacity = 1.0):

    if len(color) == 3:
        color = (color[0], color[1], color[2], opacity)

    if opacity != 1.0:	
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  


    apply_material(color)
    glPushMatrix()
    glTranslatef(center[0], center[1], center[2])

    ##Huaicai 1/17/05: To avoid rotate around (0, 0, 0), which causes 
    ## display problem on some platforms
    angle = -acos(axis[2])*180.0/pi
    if (axis[2]*axis[2] >= 1.0):
        glRotate(angle, 0.0, 1.0, 0.0)
    else:
        glRotate(angle, axis[1], -axis[0], 0.0)



    glScale(h, w, l)
    glCallList(solidCubeList) #bruce 060302 revised the contents of solidCubeList as part of fixing bug 1595

    if opacity != 1.0:	
        glDisable(GL_BLEND)
        glDepthMask(GL_TRUE)

    glPopMatrix()
    return

def drawLineLoop(color,lines, width = 1):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glLineWidth(width)
    glBegin(GL_LINE_LOOP)
    for v in lines:
        glVertex3fv(v)
    glEnd()
    glEnable(GL_LIGHTING)  
    #reset the glLineWidth to 1
    if width!=1:
        glLineWidth(1)
    return


def drawlinelist(color,lines):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINES)
    for v in lines:
        glVertex3fv(v)
    glEnd()
    glEnable(GL_LIGHTING)
    return

cubeLines = A([[-1,-1,-1], [-1,-1, 1],
               [-1, 1,-1], [-1, 1, 1],
               [ 1,-1,-1], [ 1,-1, 1],
               [ 1, 1,-1], [ 1, 1, 1],

               [-1,-1,-1], [-1, 1,-1],
               [-1,-1, 1], [-1, 1, 1],
               [ 1,-1,-1], [ 1, 1,-1],
               [ 1,-1, 1], [ 1, 1, 1],

               [-1,-1,-1], [ 1,-1,-1],
               [-1,-1, 1], [ 1,-1, 1],
               [-1, 1,-1], [ 1, 1,-1],
               [-1, 1, 1], [ 1, 1, 1]])

def drawCubeCell(color):
    vs = [[sp0, sp0, sp0], [sp4, sp0, sp0], [sp4, sp4, sp0], [sp0, sp4, sp0],
          [sp0, sp0, sp4], [sp4, sp0, sp4], [sp4, sp4, sp4], [sp0, sp4, sp4]]

    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINE_LOOP)
    for ii in range(4):
        glVertex3fv(vs[ii])
    glEnd()

    glBegin(GL_LINE_LOOP)
    for ii in range(4, 8):
        glVertex3fv(vs[ii])
    glEnd()

    glBegin(GL_LINES)
    for ii in range(4):
        glVertex3fv(vs[ii])
        glVertex3fv(vs[ii+4])
    glEnd()

    glEnable(GL_LIGHTING) 
    return

def drawPlane(color, w, h, textureReady, opacity, SOLID=False, pickCheckOnly=False):
    '''Draw polygon with size of <w>*<h> and with color <color>. Optionally, it could be texuture mapped, translucent.
       @pickCheckOnly This is used to draw the geometry only, used for OpenGL pick selection purpose.'''
    vs = [[-0.5, 0.5, 0.0], [-0.5, -0.5, 0.0], [0.5, -0.5, 0.0], [0.5, 0.5, 0.0]]
    vt = [[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]    

    glDisable(GL_LIGHTING)
    glColor4fv(list(color) + [opacity])

    glPushMatrix()
    glScalef(w, h, 1.0)

    if SOLID:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glDisable(GL_CULL_FACE) 

    if not pickCheckOnly:
        glDepthMask(GL_FALSE) # This makes sure translucent object will not occlude another translucent object
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if textureReady:
            glEnable(GL_TEXTURE_2D)  

    glBegin(GL_QUADS)
    for ii in range(len(vs)):
        t = vt[ii]; v = vs[ii]
        if textureReady:
            glTexCoord2fv(t)
        glVertex3fv(v)
    glEnd()

    if not pickCheckOnly:
        if textureReady:
            glDisable(GL_TEXTURE_2D)

        glDisable(GL_BLEND)
        glDepthMask(GL_TRUE) 

    glEnable(GL_CULL_FACE)
    if not SOLID:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glPopMatrix()
    glEnable(GL_LIGHTING)
    return

def drawFullWindow(vtColors):
    """Draw gradient background color.
       <vtColors> is a 4 element list specifying colors for the  
       left-down, right-down, right-up, left-up window corners.
       To draw the full window, the modelview and projection should be set in identity.
       """
    from constants import GL_FAR_Z
    glDisable(GL_LIGHTING)

    glBegin(GL_QUADS)
    glColor3fv(vtColors[0])
    glVertex3f(-1, -1, GL_FAR_Z)
    glColor3fv(vtColors[1])            
    glVertex3f(1, -1, GL_FAR_Z)
    glColor3fv(vtColors[2])
    glVertex3f(1, 1, GL_FAR_Z)
    glColor3fv(vtColors[3])
    glVertex3f(-1, 1, GL_FAR_Z)
    glEnd()

    glEnable(GL_LIGHTING)
    return

def drawtext(text, color, origin, point_size, glpane):

    if not text:
        return
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    from PyQt4.Qt import QFont, QString, QColor
    font = QFont( QString("Helvetica"), point_size)
    #glpane.qglColor(QColor(75, 75, 75))
    from widgets import RGBf_to_QColor
    glpane.qglColor(RGBf_to_QColor(color))
    glpane.renderText(origin[0], origin[1], origin[2], QString(text), font)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    return

def drawcylinder_wireframe(color, end1, end2, radius): #bruce 060608
    "draw a wireframe cylinder (not too pretty, definitely could look nicer, but it works)"
    # display polys as their edges (see drawer.py's drawwirecube or Jig.draw for related code)
    # (probably we should instead create a suitable lines display list,
    #  or even use a wire-frame-like texture so various lengths work well)
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE) # this makes motors look too busy, but without it, they look too weird (which seems worse)
    try:
        drawcylinder(color, end1, end2, radius) ##k not sure if this color will end up controlling the edge color; we hope it will
    except:
        debug.print_compact_traceback("bug, ignored: ")
    # the following assumes that we are never called as part of a jig's drawing method,
    # or it will mess up drawing of the rest of the jig if it's disabled
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)
    glPolygonMode(GL_BACK, GL_FILL) # could probably use GL_FRONT_AND_BACK
    return

def drawsurface_wireframe(color, pos, radius, tm, nm): 
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE) 
    try:
        drawsurface(color, pos, radius, tm, nm) 
    except:
        debug.print_compact_traceback("bug, ignored: ")
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)
    glPolygonMode(GL_BACK, GL_FILL) 
    return

def renderSurface(surfaceEntities, surfaceNormals):
    ####@@@@ bruce 060927 comments:
    # - The color needs to come before the vertex. I fixed that, but left a debug_pref that can change it
    #   so you can see the effect of that bug before it was fixed. (Same for the normal, but it already did come before.)
    # - I suspect normals are not used (when nc > 0) due to lighting being off. But if it's on, colors are not used.
    #   I saw that problem before, and we had to use apply_material instead, to set color; I'm not sure why,
    #   it might just be due to specific OpenGL settings we make for other purposes. So I'll use drawer.apply_material(color)
    #   (again with a debug pref to control that).
    # The effect of the default debug_pref settings is that it now works properly with color -- but only for the 2nd chunk,
    # if you create two, and not at all if you create only one. I don't know why it doesn't work for the first chunk.
    (entityIndex, surfacePoints, surfaceColors) = surfaceEntities
    e0 = entityIndex[0]
    n = len(e0)
    nc = len(surfaceColors)
    if 1:
        ### bruce 060927 debug code; when done debugging, we can change them to constants & simplify the code that uses them.
        from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
        disable_lighting = debug_pref("surface: disable lighting?", Choice_boolean_False)
        if nc:
            color_first = debug_pref("surface: color before vertex?", Choice_boolean_True)
            use_apply_material = debug_pref("surface: use apply_material?", Choice_boolean_True)
    ## old code was equivalent to disable_lighting = (nc > 0)
    def use_color(color): #bruce 060927 split this out, so we can change how we apply color in a single place in the code
        if use_apply_material:
            apply_material(color) # This makes the colors visible even when lighting is enabled.
        else:
            glColor3fv(color) # Old code did this. These colors are only visible when lighting is not enabled.
        return
    def onevert(vertex_index): #bruce 060927 split this out, for code clarity, and so debug prefs are used in only one place
        glNormal3fv(surfaceNormals[vertex_index])
        if nc > 0 and color_first: use_color(surfaceColors[vertex_index]) # this needs to be done before glVertex3fv
        glVertex3fv(surfacePoints[vertex_index])
        if nc > 0 and not color_first: use_color(surfaceColors[vertex_index]) # old code did it here -- used wrong colors sometimes
        return
    ## if nc > 0 : glDisable(GL_LIGHTING)
    if disable_lighting: glDisable(GL_LIGHTING)
    if n == 3:
        glBegin(GL_TRIANGLES)
        for entity in entityIndex:
            onevert(entity[0])
            onevert(entity[1])
            onevert(entity[2])
        glEnd()
    else:	
        glBegin(GL_QUADS)
        for entity in entityIndex:
            onevert(entity[0])
            onevert(entity[1])
            onevert(entity[2])
            onevert(entity[3])
        glEnd()
    if disable_lighting: glEnable(GL_LIGHTING)
    return

# end
