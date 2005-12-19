# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
drawer.py

OpenGL drawing utilities.

$Id$
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GLUT as glut
import math
from VQT import *
from constants import DIAMOND_BOND_LENGTH, white
import env #bruce 051126
from prefs_constants import material_specular_highlights_prefs_key, \
        material_specular_shininess_prefs_key, \
        material_specular_finish_prefs_key, \
        material_specular_brightness_prefs_key #mark 051205. names revised
import debug #bruce 051212, for debug.print_compact_traceback

# the golden ratio
phi=(1.0+sqrt(5.0))/2.0
vert=norm(V(phi,0,1))
a=vert[0]
b=vert[1]
c=vert[2]

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
        a=tri[0]
        b=tri[1]
        c=tri[2]
        a1=norm(A(tri[0]))
        b1=norm(A(tri[1]))
        c1=norm(A(tri[2]))
        d=tuple(norm(a1+b1))
        e=tuple(norm(b1+c1))
        f=tuple(norm(c1+a1))
        return subdivide((a,d,f), deep-1) + subdivide((d,e,f), deep-1) +\
               subdivide((d,b,e), deep-1) + subdivide((f,e,c), deep-1)
    else: return [tri]

## Get the specific detail level of triangles approximation of a sphere 
def getSphereTriangles(level):
        ocdec=[]
        for i in icosix:
            ocdec+=subdivide((icosa[i[0]],icosa[i[1]],icosa[i[2]]),level)
        return ocdec

# generate two circles in space as 13-gons,
# one rotated half a segment with respect to the other
# these are used as cylinder ends
slices=13
circ1=map((lambda n: n*2.0*pi/slices), range(slices+1))
circ2=map((lambda a: a+pi/slices), circ1)
drum0=map((lambda a: (cos(a), sin(a), 0.0)), circ1)
drum1=map((lambda a: (cos(a), sin(a), 1.0)), circ2)
drum1n=map((lambda a: (cos(a), sin(a), 0.0)), circ2)

# grantham 20051213 I finally decided the look of the oddly twisted
# cylinder bonds was not pretty enough, so I made a "drum2" which is just
# drum0 with a 1.0 Z coordinate, a la drum1.
drum2=map((lambda a: (cos(a), sin(a), 1.0)), circ1)

# This edge list zips up the "top" vertex and normal and then
# the "bottom" vertex and normal.
# Thus each tuple in the sequence would be (vtop, ntop, vbot, nbot) [grantham 20051213]
# (bruce 051215 simplified the python usage in a way which should create the same list.)
cylinderEdges = zip(drum0, drum0, drum2, drum0)

circle=zip(drum0[:-1],drum0[1:],drum1[:-1]) +\
       zip(drum1[:-1],drum0[1:],drum1[1:])
circlen=zip(drum0[:-1],drum0[1:],drum1n[:-1]) +\
        zip(drum1n[:-1],drum0[1:],drum1n[1:])

cap0n=(0.0, 0.0, -1.0)
cap1n=(0.0, 0.0, 1.0)
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
rotSignList = linearLineList = linearArrowList = circleList = lonsGridList = SiCGridList = None

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
        return
    def materialprefs_summary(self): #bruce 051126
        """Return a Python data object summarizing our prefs which affect chunk display lists,
        so that memoized display lists should become invalid (due to changes in this object)
        if and only if this value becomes different.
        """
        res = (self.enable_specular_highlights,)
        if self.enable_specular_highlights:
            res = res + ( self.specular_shininess, self.specular_whiteness, self.specular_brightness)
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
                (white, 0.1, 0.5, 0.5, 0, 0, 100, False))
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

def get_gl_info_string():

    """Return a string containing some useful information about the
    OpenGL implementation."""
    # grantham 20051129

    gl_info_string = ''

    gl_info_string += 'GL_VENDOR : "%s"\n' % glGetString(GL_VENDOR)
    gl_info_string += 'GL_VERSION : "%s"\n' % glGetString(GL_VERSION)
    gl_info_string += 'GL_RENDERER : "%s"\n' % glGetString(GL_RENDERER)
    gl_info_string += 'GL_EXTENSIONS : "%s"\n' % glGetString(GL_EXTENSIONS)

    if False:
        # Give a practical indication of how much video memory is available.
        # Should also do this with VBOs.

        # I'm pretty sure this code is right, but PyOpenGL seg faults in
        # glAreTexturesResident, so it's disabled until I can figure that
        # out.

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

	glDisable(GL_TEXTURE_2D)
	glDeleteTextures(tex_names)

	gl_info_string += "Could create %d 512x512 RGBA resident textures\n", tex_count
    return gl_info_string

class ColorSorter:

    """
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
    _glnames = []       # internal record of GL name stack

    def pushName(glname):
        """Record the current pushed GL name.  This will probably mutate a little
        into doing the GL name push as well, for clarity and encapsulation.
        """
        ColorSorter._glnames.append(glname)

    pushName = staticmethod(pushName)


    def popName():
        """Record a pop of the GL name.  This will probably mutate a little
        into doing the GL pop as well, for clarity and encapsulation.
        """
        del ColorSorter._glnames[-1]

    popName = staticmethod(popName)


    def _printstats():
        """Internal function for developers to call to print stats on number of
        sorted and immediately-called objects"""
        print "Since previous 'stats', %d sorted, %d immediate: " % (ColorSorter._sorted, ColorSorter._immediate)
        ColorSorter._sorted = 0
        ColorSorter._immediate = 0

    _printstats = staticmethod(_printstats)


    def _add_to_sorter(color, func, params):
        """Internal function that stores 'scheduled' operations for a later
        sort, between a start/finish"""
        ColorSorter._sorted += 1
        color = tuple(color)
        if not ColorSorter.sorted_by_color.has_key(color):
            ColorSorter.sorted_by_color[color] = []
        if len(ColorSorter._glnames) > 0:
            name = ColorSorter._glnames[-1]
        else:
            name = None
        ColorSorter.sorted_by_color[color].append((func, params, name))

    _add_to_sorter = staticmethod(_add_to_sorter)


    def _invoke_immediately(color, func, params):
        """Internal function that invokes 'scheduled' operations right now,
        outside a start/finish."""
        ColorSorter._immediate += 1
        apply_material(color)
        func(params)

    _invoke_immediately = staticmethod(_invoke_immediately)


    # schedule is a code object; call it with a color, function, and
    # param tuple
    schedule = _invoke_immediately

    def start():
        """Start sorting - objects provided to "schedule" will be stored
        for a sort at the time "finish" is called."""
        assert not ColorSorter.sorting, "Called ColorSorter.start but already sorting?!"
        ColorSorter.sorting = True
        ColorSorter.sorted_by_color = {}
        ColorSorter.schedule = staticmethod(ColorSorter._add_to_sorter)

    start = staticmethod(start)


    def finish():
        """Finish sorting - objects recorded since "start" will
        be sorted and invoked now."""
        color_groups = len(ColorSorter.sorted_by_color)
        objects_drawn = 0
        for color, funcs in ColorSorter.sorted_by_color.iteritems():
            apply_material(color)
            for func, params, name in funcs:
                objects_drawn += 1
                if name is not None:
                    glPushName(name)
                func(params)
                if name is not None:
                    glPopName()
        ColorSorter.schedule = staticmethod(ColorSorter._invoke_immediately)
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

    lonsEdges = [ # 2 outward vertical edges for layer 1
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
                     
    return lonsEdges 

#Some variables for Graphite lattice
gUx = 1.228; gUy = 0.709; gZLen = 1.674
gXLen = 2*gUx; gYLen = 4*gUy

def _makeGraphiteCell(zIndex):
    """Data structure to construct a Graphite lattice cell"""
    gVp = [[-gUx, -gUy, 0.0],   [0.0, 0.0, 0.0],        [gUx, -gUy, 0.0],
              [-gUx, 3*gUy, 0.0], [0.0, 2*gUy, 0.0],  [gUx, 3*gUy, 0.0],
              [gUx, 5*gUy, 0.0]
         ]

    grpEdges = [ 
                      [gVp[0], gVp[1]], [gVp[1], lVp[2]],
                      ##Not finished yet. We need double bond to do this??
                    ]
                     
    return lonsEdges 


##Some varaible defined for SiC Grid
sic_sqt3_2 = sqrt(3.0)/2.0; sic_uLen = 1.8; sic_yU = sic_uLen * sic_sqt3_2; sic_hLen = sic_uLen/2.0
sic_vpdat = [[0.0, sic_yU, 0.0], [sic_uLen+sic_hLen, 0.0, 0.0], [sic_uLen, sic_yU, 0.0],
             [sic_uLen+sic_hLen, sic_yU*2, 0.0], [2*sic_uLen+sic_hLen, sic_yU*2.0, 0.0],
             [3*sic_uLen, sic_yU, 0.0], [2*sic_uLen+sic_hLen, 0.0, 0.0]]
    

def setup():
    global CylList, diamondGridList, CapList, CubeList, solidCubeList
    global sphereList, rotSignList, linearLineList, linearArrowList
    global circleList, lonsGridList, lonsEdges, lineCubeList, SiCGridList

    listbase = glGenLists(numSphereSizes + 21)

    for i in range(numSphereSizes):
        sphereList += [listbase+i]
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


    CylList = listbase+numSphereSizes
    glNewList(CylList, GL_COMPILE)
    glBegin(GL_TRIANGLE_STRIP)
    for (vtop, ntop, vbot, nbot) in cylinderEdges:
        glNormal3fv(nbot)
        glVertex3fv(vbot)
        glNormal3fv(ntop)
        glVertex3fv(vtop)
    glEnd()
    glEndList()

    CapList = CylList + 1
    glNewList(CapList, GL_COMPILE)
    glNormal3fv(cap0n)
    glBegin(GL_POLYGON)
    for p in drum0:
        glVertex3fv(p)
    glEnd()
    glNormal3fv(cap1n)
    glBegin(GL_POLYGON)
    for p in drum1:
        glVertex3fv(p)
    glEnd()
    glEndList()

    diamondGridList = CapList + 1
    glNewList(diamondGridList, GL_COMPILE)
    glBegin(GL_LINES)
    for p in digrid:
        glVertex(p[0])
        glVertex(p[1])
    glEnd()
    glEndList()
    
    lonsGridList = diamondGridList + 1
    lonsEdges = _makeLonsCell()
    glNewList(lonsGridList, GL_COMPILE)
    glBegin(GL_LINES)
    for p in lonsEdges:
        glVertex(p[0])
        glVertex(p[1])
    glEnd()
    glEndList()

    CubeList = lonsGridList + 1
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
    
    solidCubeList = CubeList + 1
    glNewList(solidCubeList, GL_COMPILE)
    glBegin(GL_QUADS)
    for i in xrange(len(cubeIndices)):
        for j in xrange(4) :    
                nTuple = tuple(cubeNormals[cubeIndices[i][j]])
                vTuple = tuple(cubeVertices[cubeIndices[i][j]])
                glNormal3fv(nTuple)
                glVertex3fv(vTuple)
    glEnd()
    glEndList()                

    rotSignList = solidCubeList + 1
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

    linearArrowList = rotSignList + 1
    glNewList(linearArrowList, GL_COMPILE)
    glBegin(GL_TRIANGLES)
    for v in linearArrowVertices:
        glVertex3f(v[0], v[1], v[2])
    glEnd()
    glEndList()

    linearLineList = linearArrowList + 1
    glNewList(linearLineList, GL_COMPILE)
    glEnable(GL_LINE_SMOOTH)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, -halfHeight)
    glVertex3f(0.0, 0.0, halfHeight)
    glEnd()
    glDisable(GL_LINE_SMOOTH)
    glEndList()
    
    circleList = linearLineList + 1 #glGenLists(1)
    glNewList(circleList, GL_COMPILE)
    glBegin(GL_LINE_LOOP)
    for ii in range(60):
        x = cos(ii*2.0*pi/60)
        y = sin(ii*2.0*pi/60)
        glVertex3f(x, y, 0.0)
    glEnd()    
    glEndList()
    
    cvIndices = [0,1, 2,3, 4,5, 6,7, 0,3, 1,2, 5,6, 4,7, 0,4, 1,5, 2,6, 3,7]
    lineCubeList = circleList + 1
    glNewList(lineCubeList, GL_COMPILE)
    glBegin(GL_LINES)
    for i in cvIndices:
        glVertex3fv(tuple(cubeVertices[i]))
    glEnd()    
    glEndList()
    
    
    SiCGridList = lineCubeList + 1
    glNewList(SiCGridList, GL_COMPILE)
    glBegin(GL_LINES)
    glVertex3fv(sic_vpdat[0])
    glVertex3fv(sic_vpdat[2])
    glEnd()
    
    glBegin(GL_LINE_STRIP)
    for v in sic_vpdat[1:]:
        glVertex3fv(v)
    glEnd()
    glEndList()
        
    #initTexture('C:\\Huaicai\\atom\\temp\\newSample.png', 128,128)
    return
    
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
    glScale(radius,radius,vlen(vec))

    glLineWidth(2.0)
    glDisable(GL_LIGHTING)
    glCallList(rotSignList)
    glEnable(GL_LIGHTING)
    glLineWidth(1.0)

    glPopMatrix()
    return

def drawsphere_worker(params):
    """Draw a sphere.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see above)"""

    (pos, radius, detailLevel) = params
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    glCallList(sphereList[detailLevel])
    glPopMatrix()
    return

def drawsphere(color, pos, radius, detailLevel):
    """Schedule a sphere for rendering whenever ColorSorter thinks is
    appropriate."""
    ColorSorter.schedule(color, drawsphere_worker, (pos, radius, detailLevel))

def drawwiresphere(color, pos, radius, detailLevel=1):
    glColor3fv(color)
    glDisable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_LINE)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    glCallList(sphereList[detailLevel])
    glEnable(GL_LIGHTING)
    glPopMatrix()
    glPolygonMode(GL_FRONT, GL_FILL)
    return

def drawcylinder_worker(params):
    """Draw a cylinder.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see above)"""

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
  
    glScale(radius,radius,vlen(vec))
    glCallList(CylList)
    if capped: glCallList(CapList)

    glPopMatrix()

    return

def drawcylinder(color, pos1, pos2, radius, capped=0):
    """Schedule a cylinder for rendering whenever ColorSorter thinks is
    appropriate."""
    ColorSorter.schedule(color, drawcylinder_worker, (pos1, pos2, radius, capped))

def drawline(color, pos1, pos2, dashEnabled = False, width = 1):
    """Draw a line from pos1 to pos2 of the given color.
    If dashEnabled is True, it will be dashed.
    If width is not 1, it should be an int or float (more than 0)
    and the line will have that width, in pixels.
    (Whether the line is antialiased is determined by GL state variables
     which are not set by this code.)
    """
    # WARNING: some callers pass dashEnabled as a positional argument rather than a named argument.
    # [bruce 050831 added docstring, this comment, and the width argument.]
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    if dashEnabled: 
        glLineStipple(1, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
    if width != 1:
        glLineWidth(width)
    glBegin(GL_LINES)
    glVertex(pos1[0], pos1[1], pos1[2])
    glVertex(pos2[0], pos2[1], pos2[2])
    glEnd()
    if width != 1:
        glLineWidth(1.0) # restore default state
    if dashEnabled: 
        glDisable(GL_LINE_STIPPLE)
    glEnable(GL_LIGHTING)
    return

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
    global CubeList, lineCubeList
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
    global CubeList
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

def drawaxes(n,point,coloraxes=False):
    from constants import blue, red, darkgreen
    glPushMatrix()
    glTranslate(point[0], point[1], point[2])
    glDisable(GL_LIGHTING)
    if coloraxes: glColor3f(red[0], red[1], red[2])
    else: glColor3f(darkgreen[0], darkgreen[1], darkgreen[2])
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
    glEnable(GL_LIGHTING)
    glPopMatrix()
    return

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
    
def getGridCellPoints(pt, latticeType): 
    grid=A([[sp0, sp0, sp0], [sp1, sp1, sp1], [sp2, sp2, sp0], [sp3, sp3, sp1], 
        [sp4, sp4, sp0], [sp2, sp0, sp2], [sp3, sp1, sp3], [sp4, sp2, sp2],
        [sp0, sp2, sp2], [sp1, sp3, sp3], [sp2, sp4, sp2], [sp4, sp0, sp4], 
        [sp2, sp2, sp4], [sp0, sp4, sp4]])
    
    cubeCorner = [[sp0, sp0, sp0], [sp4, sp0, sp0], [sp4, sp4, sp0], [sp0, sp4, sp0],
                            [sp0, sp0, sp4], [sp4, sp0, sp4], [sp4, sp4, sp4], [sp0, sp4, sp4]]
    
    if latticeType == 'DIAMOND':
        a = 0; cellX = cellY = cellZ = DiGridSp
    elif latticeType == 'LONSDALEITE':
        a = 1; cellX = XLen; cellY = YLen; cellZ = ZLen       
    i = int(floor(pt[0]/cellX))
    j = int(floor(pt[1]/cellY))
    k = int(floor(pt[2]/cellZ))
    
    orig = V(i*cellX, j*cellY, k*cellZ)
    
    return orig + grid 
    
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
    c2 = pt1 + rt*dot(rt,pt2-pt1)
    c3 = pt1 + up*dot(up,pt2-pt1)
    glBegin(GL_LINE_LOOP)
    glVertex(pt1[0],pt1[1],pt1[2])
    glVertex(c2[0],c2[1],c2[2])
    glVertex(pt2[0],pt2[1],pt2[2])
    glVertex(c3[0],c3[1],c3[2])
    glEnd()
    glEnable(GL_LIGHTING)

def drawRubberBand(pt1, pt2, c2, c3, color):
    """Huaicai: depth test should be disabled to make the xor work """
    glBegin(GL_LINE_LOOP)
    glVertex(pt1[0],pt1[1],pt1[2])
    glVertex(c2[0],c2[1],c2[2])
    glVertex(pt2[0],pt2[1],pt2[2])
    glVertex(c3[0],c3[1],c3[2])
    glEnd()
    return
       

# Wrote drawbrick for the Linear Motor.  Mark [2004-10-10]
def drawbrick(color, center, axis, l, h, w):
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
    glut.glutSolidCube(1.0)
    #glCallList(solidCubeList)
    glPopMatrix()
    return

def drawLineLoop(color,lines):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINE_LOOP)
    for v in lines:
        glVertex3fv(v)
    glEnd()
    glEnable(GL_LIGHTING)    
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

# mat mult by rowvector list and max/min reduce to find extrema
D = sqrt(2.0)/2.0
T = sqrt(3.0)/3.0
#              0  1  2  3   4  5   6  7   8  9  10  11  12
#             13 14 15 16  17 18  19 20  21 22  23  24  25
polyXmat = A([[1, 0, 0, D,  D, D,  D,  0,   0, T,  T,  T,  T],
                       [0, 1, 0, D, -D, 0,   0,  D,  D, T,  T, -T, -T],
                       [0, 0, 1, 0,  0,  D, -D,  D, -D, T, -T,  T, -T]])

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
    

def drawLonsdaleiteGrid(scale, center):
    """This function is obsolete. Call dragGrid() and pass approriate parameter to draw the Lonsdaleite Lattice """
    glDisable(GL_LIGHTING)
    
    bblo = center- scale
    bbhi = center + scale
    i1 =  int(floor(bblo[0]/XLen))
    i2 = int(ceil(bbhi[0]/XLen))
    j1 = int(floor(bblo[1]/YLen))
    j2 = int(ceil(bbhi[1]/YLen))
    k1 = int(floor(bblo[2]/ZLen))
    k2 = int(ceil(bbhi[2]/ZLen))
    glPushMatrix()
    glTranslate(i1*XLen,  j1*YLen, k1*ZLen)
    for i in range(i1, i2):
        glPushMatrix()
        for j in range(j1, j2):
            glPushMatrix()
            for k in range(k1, k2):
                glCallList(lonsGridList)
                glTranslate(0.0,  0.0, ZLen)
            glPopMatrix()
            glTranslate(0.0,  YLen, 0.0)
        glPopMatrix()
        glTranslate(XLen, 0.0, 0.0)
    glPopMatrix()
    glEnable(GL_LIGHTING)        
    return
    
###Huaicai: test function    
def drawDiamondCubic(color):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINES)
    for jj in range(5):
         for kk in range(5):
              glVertex3f(sp0, sp1*jj, sp1*kk)
              glVertex3f(sp4, sp1*jj, sp1*kk)
    
    for jj in range(5):
         for ii in range(5):
              glVertex3f(sp1*ii, sp1*jj, sp0)
              glVertex3f(sp1*ii, sp1*jj, sp4)
    
    for kk in range(5):
         for ii in range(5):
              glVertex3f(sp1*ii, sp0, sp1*kk)
              glVertex3f(sp1*ii, sp4, sp1*kk)
              
    glEnd()
    glEnable(GL_LIGHTING)
    return

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
            
def drawGPGrid(color, line_type, w, h, uw, uh):
    '''Draw grid lines for a Grid Plane, where:
    color = grid line color
    line_type is: 0=None, 1=Solid, 2=Dashed" or 3=Dotted
    w = width
    h = height
    uw = width spacing between grid lines
    uh = height spacing between grid lines
    '''
    
    from prefs_constants import NO_LINE, SOLID_LINE, DASHED_LINE, DOTTED_LINE
    
    if line_type == NO_LINE:
        return

    if uw > w: uw = w
    if uh > h: uh = h
    
    Z_OFF = 0.0 #0.001
    
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    
    hw = w/2.0; hh = h/2.0

    #glEnable(GL_LINE_SMOOTH)
    #glEnable(GL_BLEND)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE)#_MINUS_SRC_ALPHA)
    
    if line_type > 1:
        glEnable(GL_LINE_STIPPLE)
        if line_type == DASHED_LINE:
            glLineStipple (1, 0x00FF)  #  dashed
        elif line_type == DOTTED_LINE:
            glLineStipple (1, 0x0101)  #  dotted
        else:
            print "drawer.drawGPGrid(): line_type '", line_type,"' is not valid.  Drawing dashed grid line."
            glLineStipple (1, 0x00FF)  #  dashed
    
    glBegin(GL_LINES)
    
    #Draw horizontal lines
    y1 = 0
    while y1 > -hh:
        glVertex3f(-hw, y1, Z_OFF)
        glVertex3f(hw, y1, Z_OFF)
    
        y1 -= uh
    
    y1 = 0
    while y1 < hh:
        glVertex3f(-hw, y1, Z_OFF)
        glVertex3f(hw, y1, Z_OFF)
    
        y1 += uh
    
    #Draw vertical lines    
    x1 = 0
    while x1 < hw:        
        glVertex3f(x1, hh, Z_OFF)
        glVertex3f(x1, -hh, Z_OFF)
    
        x1 += uw
    
    x1 = 0
    while x1 > -hw:        
        glVertex3f(x1, hh, Z_OFF)
        glVertex3f(x1, -hh, Z_OFF)
    
        x1 -= uw
    
    glEnd()
    
    if line_type > 1:
        glDisable (GL_LINE_STIPPLE)
    
    #glDisable(GL_LINE_SMOOTH)
    #glDisable(GL_BLEND)
    
    glEnable(GL_LIGHTING)
    return

def drawSiCGrid(color, line_type, w, h):
    '''Draw SiC grid. '''
    from prefs_constants import NO_LINE, SOLID_LINE, DASHED_LINE, DOTTED_LINE
    
    if line_type == NO_LINE:
        return
    
    XLen = sic_uLen * 3.0
    YLen = sic_yU * 2.0
    hw = w/2.0; hh = h/2.0
    xx = (-hw, hw)
    yy = (-hh, hh)
    i1 = int(floor(xx[0]/XLen))
    i2 = int(ceil(xx[1]/XLen))
    j1 = int(floor(xx[0]/YLen))
    j2 = int(ceil(xx[1]/YLen))
    
    glDisable(GL_LIGHTING)
    glColor3fv(color)

    if line_type > 1:
        glEnable(GL_LINE_STIPPLE)
        if line_type == DASHED_LINE:
            glLineStipple (1, 0x00FF)  #  dashed
        elif line_type == DOTTED_LINE:
            glLineStipple (1, 0x0101)  #  dotted
        else:
            print "drawer.drawGPGrid(): line_type '", line_type,"' is not valid.  Drawing dashed grid line."
            glLineStipple (1, 0x00FF)  #  dashed
    
    glClipPlane(GL_CLIP_PLANE0, (1.0, 0.0, 0.0, hw))
    glClipPlane(GL_CLIP_PLANE1, (-1.0, 0.0, 0.0, hw))
    glClipPlane(GL_CLIP_PLANE2, (0.0, 1.0, 0.0, hh))
    glClipPlane(GL_CLIP_PLANE3, (0.0, -1.0, 0.0, hh))
    glEnable(GL_CLIP_PLANE0)
    glEnable(GL_CLIP_PLANE1)
    glEnable(GL_CLIP_PLANE2)
    glEnable(GL_CLIP_PLANE3)
     
    glPushMatrix()
    glTranslate(i1*XLen,  j1*YLen, 0.0)
    for i in range(i1, i2):
        glPushMatrix()
        for j in range(j1, j2):
            glCallList(SiCGridList)
            glTranslate(0.0, YLen, 0.0)
        glPopMatrix()
        glTranslate(XLen, 0.0, 0.0)
    glPopMatrix()
    
    glDisable(GL_CLIP_PLANE0)
    glDisable(GL_CLIP_PLANE1)
    glDisable(GL_CLIP_PLANE2)
    glDisable(GL_CLIP_PLANE3)
    
    if line_type > 1:
        glDisable (GL_LINE_STIPPLE)
    
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
    
def drawtext(text, color, pt, size, glpane):

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    from qt import QFont, QString, QColor
    font = QFont( QString("Helvetica"), size)
    #glpane.qglColor(QColor(75, 75, 75))
    from widgets import RGBf_to_QColor
    glpane.qglColor(RGBf_to_QColor(color))
    glpane.renderText(pt[0], pt[1], pt[2], QString(text), font)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    return

#end
