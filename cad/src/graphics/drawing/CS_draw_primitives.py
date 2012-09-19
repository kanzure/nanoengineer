# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
CS_draw_primitives.py - Public entry points for ColorSorter drawing primitives.

These functions all call ColorSorter.schedule_* methods, which record object
data for sorting, including the object color and an eventual call on the
appropriate drawing worker function.

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Originated by Josh in drawer.py .

Various developers extended it since then, including Brad G (ColorSorter).

080311 piotr Added a "drawpolycone_multicolor" function for drawing polycone
tubes with per-vertex colors (necessary for DNA display style)

080420 piotr Solved highlighting and selection problems for multi-colored
objects (e.g. rainbow colored DNA structures).

080519 russ pulled the globals into a drawing_globals module and broke drawer.py
into 10 smaller chunks: glprefs.py setup_draw.py shape_vertices.py
ColorSorter.py CS_workers.py c_renderer.py CS_draw_primitives.py drawers.py
gl_lighting.py gl_buffers.py
"""

from OpenGL.GL import GL_BACK
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import GL_FILL
from OpenGL.GL import GL_FRONT
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LINE
from OpenGL.GL import glPolygonMode

from geometry.VQT import norm, vlen
import utilities.debug as debug # for debug.print_compact_traceback

from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.drawers import drawPoint
from graphics.drawing.gl_GLE import gleSetNumSides

def drawsphere(color, pos, radius, detailLevel,
               opacity = 1.0,
               testloop = 0
               ):
    """
    Schedule a sphere for rendering whenever ColorSorter thinks is appropriate.

    @param detailLevel: 0 (icosahedron), or 1 (4x as many triangles),
                        or 2 (16x as many triangles)
    @type detailLevel: int (0, 1, or 2)
    """
    ColorSorter.schedule_sphere(
        color,
        pos,
        radius,
        detailLevel, # see: _NUM_SPHERE_SIZES, len(drawing_globals.sphereList)
        opacity = opacity,
        testloop = testloop )

def drawwiresphere(color, pos, radius, detailLevel = 1):
    """
    Schedule a wireframe sphere for rendering whenever ColorSorter thinks is
    appropriate.
    """
    ColorSorter.schedule_wiresphere(color, pos, radius,
                                    detailLevel = detailLevel)

def drawcylinder(color, pos1, pos2, radius, capped = 0, opacity = 1.0):
    """
    Schedule a cylinder for rendering whenever ColorSorter thinks is
    appropriate.
    """
    if 1:
        #bruce 060304 optimization: don't draw zero-length or almost-zero-length
        # cylinders.  (This happens a lot, apparently for both long-bond
        # indicators and for open bonds.  The callers hitting this should be
        # fixed directly! That might provide a further optim by making a lot
        # more single bonds draw as single cylinders.)  The reason the
        # threshhold depends on capped is in case someone draws a very thin
        # cylinder as a way of drawing a disk. But they have to use some
        # positive length (or the direction would be undefined), so we still
        # won't permit zero-length then.
        cyllen = vlen(pos1 - pos2)
        if cyllen < (capped and 0.000000000001 or 0.0001):
            # Uncomment this to find the callers that ought to be optimized.
            #e optim or remove this test; until then it's commented out.
##            if env.debug():
##                print ("skipping drawcylinder since length is only %5g" %
##                       (cyllen,)), \
##                       ("  (color is (%0.2f, %0.2f, %0.2f))" %
##                        (color[0], color[1], color[2]))
            return
        pass
    ColorSorter.schedule_cylinder(color, pos1, pos2, radius,
                                  capped = capped, opacity = opacity)

def drawcylinder_wireframe(color, end1, end2, radius): #bruce 060608
    """
    Draw a wireframe cylinder (not too pretty, definitely could look nicer, but
    it works.)
    """
    # display polys as their edges (see drawer.py's drawwirecube or Jig.draw for
    # related code) (probably we should instead create a suitable lines display
    # list, or even use a wire-frame-like texture so various lengths work well)
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    # This makes motors look too busy, but without it, they look too weird
    # (which seems worse.)
    glDisable(GL_CULL_FACE)
    try:
        ##k Not sure if this color will end up controlling the edge color; we
        ## hope it will.
        drawcylinder(color, end1, end2, radius)
    except:
        debug.print_compact_traceback("bug, ignored: ")
    # The following assumes that we are never called as part of a jig's drawing
    # method, or it will mess up drawing of the rest of the jig if it's
    # disabled.
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)
    glPolygonMode(GL_BACK, GL_FILL) # could probably use GL_FRONT_AND_BACK
    return

def drawDirectionArrow(color,
                       tailPoint,
                       arrowBasePoint,
                       tailRadius,
                       scale,
                       tailRadiusLimits = (),
                       flipDirection = False,
                       opacity = 1.0,
                       numberOfSides = 20,
                       glpane = None,
                       scale_to_glpane = False
                       ):
    """
    Draw a directional arrow staring at <tailPoint> with an endpoint decided
    by the vector between <arrowBasePoint> and <tailPoint>
    and the glpane scale <scale>
    @param color : The arrow color
    @type  color: Array
    @param tailPoint: The point on the arrow tail where the arrow begins.
    @type   tailPoint: V
    @param arrowBasePoint: A point on the arrow where the arrow head begins(??
    @type  arrowBasePoint: V
    @param tailRadius: The radius of the arrow tail (cylinder radius
                       representing the arrow tail)
    @type  tailRaius: float
    @param opacity: The opacity decides the opacity (or transparent display)
                    of the rendered arrow. By default it is rendered as a solid
                    arrow. It varies between 0.0 to 1.0 ... 1.0 represents the
                    solid arrow renderring style
    @type opacity: float
    @param numberOfSides: The total number of sides for the arrow head
                        (a glePolycone) The default value if 20 (20 sided
                        polycone)
    @type  numberOfSides: int

    @param scale_to_glpane: If True, the arrow size will be determined by the
                            glpane scale.
    """
    #@See DnaSegment_ResizeHandle to see how the tailRadiusLimits
    #are defined. See also exprs.Arrow. Note that we are not using
    #argument 'scale' for this purpose because the
    if scale_to_glpane and glpane is not None:
        scaled_tailRadius = tailRadius*0.05*glpane.scale
        if tailRadiusLimits:
            min_tailRadius = tailRadiusLimits[0]
            max_tailRadius = tailRadiusLimits[1]
            if scaled_tailRadius < min_tailRadius:
                pass #use the provided tailRadius
            elif scaled_tailRadius > max_tailRadius:
                tailRadius = max_tailRadius
            else:
                tailRadius = scaled_tailRadius
        else:
            tailRadius = scaled_tailRadius



    vec = arrowBasePoint - tailPoint
    vec = scale*0.07*vec
    arrowBase =  tailRadius*3.0
    arrowHeight =  arrowBase*1.5
    axis = norm(vec)

    #as of 2008-03-03 scaledBasePoint is not used so commenting out.
    #(will be removed after more testing)
    ##scaledBasePoint = tailPoint + vlen(vec)*axis
    drawcylinder(color, tailPoint, arrowBasePoint, tailRadius, capped = True,
                 opacity = opacity)

    ##pos = scaledBasePoint
    pos = arrowBasePoint
    arrowRadius = arrowBase
    gleSetNumSides(numberOfSides)
    drawpolycone(color,
                 # Point array (the two endpoints not drawn.)
                 [[pos[0] - 1 * axis[0],
                   pos[1] - 1 * axis[1],
                   pos[2] - 1 * axis[2]],
                  [pos[0],# - axis[0],
                   pos[1], #- axis[1],
                   pos[2]], #- axis[2],
                  [pos[0] + arrowHeight * axis[0],
                   pos[1] + arrowHeight * axis[1],
                   pos[2] + arrowHeight * axis[2]],
                  [pos[0] + (arrowHeight + 1) * axis[0],
                   pos[1] + (arrowHeight + 1) * axis[1],
                   pos[2] + (arrowHeight + 1) * axis[2]]],
                 [arrowRadius, arrowRadius, 0, 0], # Radius array
                 opacity = opacity
                 )
    #reset the gle number of sides to the gle default of '20'
    gleSetNumSides(20)

def drawpolycone(color, pos_array, rad_array, opacity = 1.0):
    """Schedule a polycone for rendering whenever ColorSorter thinks is
    appropriate."""
    ColorSorter.schedule_polycone(color, pos_array, rad_array,
                                  opacity = opacity)

def drawpolycone_multicolor(color, pos_array, color_array, rad_array,
                            opacity = 1.0):
    """Schedule a polycone for rendering whenever ColorSorter thinks is
    appropriate. Accepts color_array for per-vertex coloring. """
    ColorSorter.schedule_polycone_multicolor(color, pos_array, color_array,
                                             rad_array, opacity = opacity)

def drawsurface(color, pos, radius, tm, nm):
    """
    Schedule a surface for rendering whenever ColorSorter thinks is
    appropriate.
    """
    ColorSorter.schedule_surface(color, pos, radius, tm, nm)

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

def drawline(color,
             endpt1,
             endpt2,
             dashEnabled = False,
             stipleFactor = 1,
             width = 1,
             isSmooth = False):
    """
    Draw a line from endpt1 to endpt2 in the given color.  Actually, schedule
    it for rendering whenever ColorSorter thinks is appropriate.

    @param endpt1: First endpoint.
    @type  endpt1: point

    @param endpt2: Second endpoint.
    @type  endpt2: point

    @param dashEnabled: If dashEnabled is True, it will be dashed.
    @type  dashEnabled: boolean

    @param stipleFactor: The stiple factor.
    @param stipleFactor: int

    @param width: The line width in pixels. The default is 1.
    @type  width: int or float

    @param isSmooth: Enables GL_LINE_SMOOTH. The default is False.
    @type  isSmooth: boolean

    @note: Whether the line is antialiased is determined by GL state variables
    which are not set in this function.

    @warning: Some callers pass dashEnabled as a positional argument rather
    than a named argument.
    """
    ColorSorter.schedule_line(color, endpt1, endpt2, dashEnabled,
                              stipleFactor, width, isSmooth)

def drawtriangle_strip(color, triangles, normals, colors):
    ColorSorter.schedule_triangle_strip(color, triangles, normals, colors)

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

def draw3DFlag(glpane,
              color,
              basePoint,
              cylRadius,
              cylHeight,
              direction = None,
              opacity = 1.0):
    """
    Draw a 3D flag with its base as a 'cylinder' and the head as a sphere.

    @param glpane: The GLPane object
    @type glpane: B{GLPane}

    @param color: color of the tag
    @type color: A

    @param basePoint: The base point of the tag
    @type basePoint: V

    @param cylRadius: Radius of the base cylinder  of the flag
    @type  cylRadius: float

    @param cylHeight: Height of the base cylinder of the flag
    @type  clyHeight: float

    @param direction: direction in which to draw the 3D flag. If this is not
                      spcified, it draws the flag using glpane.up
    @type direction: V  (or None)

    @param opacity: Flag opacity (a value bet 0.0 to 1.0)
    @type opacity: float
    """
    if direction is None:
        direction = glpane.up

    scale = glpane.scale

    height = cylHeight
    endPoint = basePoint + direction*height

    sphereRadius = cylHeight*0.7
    sphereCenter = endPoint + direction*0.8*sphereRadius
    SPHERE_DRAWLEVEL = 2

    drawcylinder(color,
                 basePoint,
                 endPoint,
                 cylRadius,
                 capped = True,
                 opacity = opacity)

    drawsphere(color,
               sphereCenter,
               sphereRadius,
               SPHERE_DRAWLEVEL,
               opacity = opacity)
    return

# end


