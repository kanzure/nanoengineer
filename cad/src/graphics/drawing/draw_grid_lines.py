# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
draw_grid_lines.py - helper functions for drawing grid lines in OpenGL.

@version: $Id$

History:

someone wrote these in drawer.py

bruce 071030 split them into a separate module
to remove an import cycle.

TODO:

does drawer.drawGrid also belong here?
"""

# the imports from math vs. numpy are as discovered in existing code
# as of 2007/06/25 [when this was part of drawer.py].
from math import floor, ceil
from numpy import sqrt

from OpenGL.GL import glBegin
##from OpenGL.GL import GL_BLEND
##from OpenGL.GL import glBlendFunc
from OpenGL.GL import glCallList
from OpenGL.GL import glClipPlane
from OpenGL.GL import GL_CLIP_PLANE0
from OpenGL.GL import GL_CLIP_PLANE1
from OpenGL.GL import GL_CLIP_PLANE2
from OpenGL.GL import GL_CLIP_PLANE3
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import glEnd

from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LINES
from OpenGL.GL import GL_LINE_SMOOTH
from OpenGL.GL import glLineStipple
from OpenGL.GL import GL_LINE_STIPPLE

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix

from OpenGL.GL import GL_SRC_ALPHA
from OpenGL.GL import glTranslate
from OpenGL.GL import glVertex3f

from OpenGL.GL import glGenLists
from OpenGL.GL import GL_COMPILE
from OpenGL.GL import glNewList
from OpenGL.GL import GL_LINE_STRIP
from OpenGL.GL import glVertex3fv
from OpenGL.GL import glEndList
from OpenGL.GL import glColor3fv
from utilities.constants import PLANE_ORIGIN_LOWER_LEFT
from utilities.constants import PLANE_ORIGIN_LOWER_RIGHT
from utilities.constants import PLANE_ORIGIN_UPPER_LEFT
from utilities.constants import PLANE_ORIGIN_UPPER_RIGHT
from utilities.constants import LABELS_ALONG_ORIGIN, LABELS_ALONG_PLANE_EDGES
from graphics.drawing.drawers import drawtext
from geometry.VQT import V

from graphics.drawing.Font3D import Font3D

from utilities.prefs_constants import NO_LINE, SOLID_LINE
from utilities.prefs_constants import DASHED_LINE, DOTTED_LINE

SiCGridList = None # TODO: make this private

# SiC grid geometry. The number in parentheses is the point's index in
# the sic_vpdat list. This stuff is used to build an OpenGL display
# list, indexed by SiCGridList. The repeating drawing unit is the
# lines shown dotted here. The 1-6 line is omitted because it will be
# supplied by the unit below.
#
#              |
#  2*sic_yU  --+                   (3) . . . . . (4)
#              |                   .               .
#              |                  .                 .
#              |                 .                   .
#              |                .                     .
#              |               .                       .
#    sic_yU  -(0) . . . . . (2)                         (5)
#              |               .                       .
#              |                .                     .
#              |                 .                   .
#              |                  .                 .
#              |                   .               .
#         0  --+------+------|-----(1)-----|-----(6)-----|---
#              |             |             |             |
#              0          sic_uLen     2*sic_uLen    3*sic_uLen
#
sic_uLen = 1.8   # Si-C bond length (I think)
sic_yU = sic_uLen * sqrt(3.0) / 2
sic_vpdat = [[0.0 * sic_uLen, 1.0 * sic_yU, 0.0],
             [1.5 * sic_uLen, 0.0 * sic_yU, 0.0],
             [1.0 * sic_uLen, 1.0 * sic_yU, 0.0],
             [1.5 * sic_uLen, 2.0 * sic_yU, 0.0],
             [2.5 * sic_uLen, 2.0 * sic_yU, 0.0],
             [3.0 * sic_uLen, 1.0 * sic_yU, 0.0],
             [2.5 * sic_uLen, 0.0 * sic_yU, 0.0]]

def setup_draw_grid_lines(): 
    """
    This must be called in whichever GL display list context will be drawn in.
    
    See comment in drawer.setup_drawer about problems with calling this
    in more than one GL context. For now, it shouldn't be.
    """
    global SiCGridList
    SiCGridList = glGenLists(1)
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
    return

def drawGPGrid(glpane, color, line_type, w, h, uw, uh, up, right):
    """
    Draw grid lines for a Grid Plane.
    
    glpane = the glpane
    color = grid line and unit text color
    line_type is: 0=None, 1=Solid, 2=Dashed or 3=Dotted
    w = width
    h = height
    uw = width spacing between grid lines
    uh = height spacing between grid lines
    """
    
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
            print "drawGPGrid(): line_type '", line_type, \
                  "' is not valid.  Drawing dashed grid line."
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
    
    # Draw unit labels for gridlines (in nm).
    text_color = color
    
    import sys
    if sys.platform == "darwin":
        # WARNING: Anything smaller than 9 pt on Mac OS X results in 
        # un-rendered text. Not sure why. -- piotr 080616
        font_size = 9
    else:
        font_size = 8
        
    text_offset = 0.5 # Offset from edge of border, in Angstroms.
    
    
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 > -hh:
        y1 -= uh
        drawtext("%g" % (-y1 / 10.0), text_color,
                 V(hw + text_offset, y1, 0.0), font_size, glpane)
    drawtext("%g" % (-y1 / 10.0), text_color,
             V(hw + text_offset, y1, 0.0), font_size, glpane)

    y1 = 0
    while y1 < hh:
        drawtext("%g" % (-y1 / 10.0), text_color,
                 V(hw + text_offset, y1, 0.0), font_size, glpane)
        y1 += uh
    drawtext("%g" % (-y1 / 10.0), text_color,
             V(hw + text_offset, y1, 0.0), font_size, glpane)

    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 < hw:
        drawtext("%g" % (x1 / 10.0), text_color,
                 V(x1, hh + text_offset, 0.0), font_size, glpane)
        x1 += uw
    drawtext("%g" % (x1 / 10.0), text_color,
             V(x1, hh + text_offset, 0.0), font_size, glpane)

    x1 = 0
    while x1 > -hw:
        drawtext("%g" % (x1 / 10.0), text_color,
                 V(x1, hh + text_offset, 0.0), font_size, glpane)
        x1 -= uw
    drawtext("%g" % (x1 / 10.0), text_color,
             V(x1, hh + text_offset, 0.0), font_size, glpane)
    
    glEnable(GL_LIGHTING)
    return

def drawGPGridForPlane(glpane, color, line_type, w, h, uw, uh, up, right, 
                       displayLabels, originLocation, labelsDisplayStyle):
    """
    Draw grid lines for a Grid from Plane PM.
    
    glpane = the glpane
    color = grid line and unit text color
    line_type is: 0=None, 1=Solid, 2=Dashed, or 3=Dotted
    w = width
    h = height
    uw = width spacing between grid lines
    uh = height spacing between grid lines
    """
    
    if line_type == NO_LINE:
        return

    if uw > w: uw = w
    if uh > h: uh = h

    Z_OFF = 0.0 #0.001
    
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    
    hw = w/2.0; hh = h/2.0

    if line_type > 1:
        glEnable(GL_LINE_STIPPLE)
        if line_type == DASHED_LINE:
            glLineStipple (1, 0x00FF)  #  dashed
        elif line_type == DOTTED_LINE:
            glLineStipple (1, 0x0101)  #  dotted
        else:
            print "drawGPGrid(): line_type '", line_type,"' is not valid. ", \
                  "Drawing dashed grid line."
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
    
    # Draw unit labels for gridlines (in nm).
    text_color = color
    
    import sys
    if sys.platform == "darwin":
        # WARNING: Anything smaller than 9 pt on Mac OS X results in 
        # un-rendered text. Not sure why. -- piotr 080616
        font_size = 9
    else:
        font_size = 8
        
    text_offset = 0.3 # Offset from edge of border, in Angstroms.
    
    if displayLabels == True:
        if (originLocation == PLANE_ORIGIN_LOWER_LEFT and
            labelsDisplayStyle == LABELS_ALONG_ORIGIN):
            displayLabelsAlongOriginLowerLeft(h, w, hh, hw, uh, uw,
                text_offset, text_color, font_size, glpane)
        elif (originLocation == PLANE_ORIGIN_UPPER_LEFT and
              labelsDisplayStyle == LABELS_ALONG_ORIGIN):
            displayLabelsAlongOriginUpperLeft(h, w, hh, hw, uh, uw, 
                text_offset, text_color, font_size, glpane)
        elif (originLocation == PLANE_ORIGIN_UPPER_RIGHT and
              labelsDisplayStyle == LABELS_ALONG_ORIGIN):
            displayLabelsAlongOriginUpperRight(h, w, hh, hw, uh, uw, 
                text_offset, text_color,font_size, glpane)  
        elif (originLocation == PLANE_ORIGIN_LOWER_RIGHT and
              labelsDisplayStyle == LABELS_ALONG_ORIGIN):
            displayLabelsAlongOriginLowerRight(h, w, hh, hw, uh, uw, 
                text_offset, text_color, font_size, glpane)  
        elif (originLocation == PLANE_ORIGIN_LOWER_LEFT and
              labelsDisplayStyle == LABELS_ALONG_PLANE_EDGES):
            displayLabelsAlongPlaneEdgesLowerLeft(h, w, hh, hw, uh, uw, 
                text_offset, text_color, font_size, glpane)
        elif (originLocation == PLANE_ORIGIN_UPPER_LEFT and
              labelsDisplayStyle == LABELS_ALONG_PLANE_EDGES):
            displayLabelsAlongPlaneEdgesUpperLeft(h, w, hh, hw, uh, uw, 
                text_offset, text_color, font_size, glpane)  
        elif (originLocation == PLANE_ORIGIN_UPPER_RIGHT and
              labelsDisplayStyle == LABELS_ALONG_PLANE_EDGES):
            displayLabelsAlongPlaneEdgesUpperRight(h, w, hh, hw, uh, uw, 
                text_offset, text_color, font_size, glpane)  
        elif (originLocation == PLANE_ORIGIN_LOWER_RIGHT and
              labelsDisplayStyle == LABELS_ALONG_PLANE_EDGES):
            displayLabelsAlongPlaneEdgesLowerRight(h, w, hh, hw, uh, uw, 
                text_offset, text_color, font_size, glpane)  
        
    glEnable(GL_LIGHTING)
    return

# UM 20080617: Code for displaying labels depending on origin location
def displayLabelsAlongOriginLowerRight(h, w, hh, hw, uh, uw,
                  text_offset, text_color, font_size, glpane):
    """
    Display labels when origin is on the lower right corner.

    @param h: height of the plane
    @type h: float
    @param w: width of the plane
    @type w: float
    @param hh: half the height of the plane
    @type hh: float
    @param hw: half the width of the plane
    @type hw: float
    @param uh: spacing along height of the plane
    @type uh: float
    @param uw: spacing along width of the plane
    @type uw: float
    @param text_offset: offset for label 
    @type text_offset: float
    @param text_color: color of the text
    @type: text_colot: tuple
    @param font_size: size of the text font
    @type: font_size: float
    @param glpane: The 3D graphics area to draw it in.
    @type  glpane: L{GLPane}
    
    """
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 >= -h:
        drawtext("%g" % (-y1 / 10.0), text_color,
                 V(hw + text_offset, y1 + hh, 0.0), font_size, glpane)
        y1 -= uh  
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 >= -w:
        drawtext("%g" % (-x1 / 10.0), text_color,
                 V(x1 + hw, hh + 2 * text_offset, 0.0), font_size, glpane)
        x1 -= uw    
    return

def displayLabelsAlongOriginUpperLeft(h, w, hh, hw, uh, uw,
                 text_offset, text_color, font_size, glpane):
    """
    Display labels when origin is on the upper left corner.
    
    @param h: height of the plane
    @type h: float
    @param w: width of the plane
    @type w: float
    @param hh: half the height of the plane
    @type hh: float
    @param hw: half the width of the plane
    @type hw: float
    @param uh: spacing along height of the plane
    @type uh: float
    @param uw: spacing along width of the plane
    @type uw: float
    @param text_offset: offset for label 
    @type text_offset: float
    @param text_color: color of the text
    @type: text_colot: tuple
    @param font_size: size of the text font
    @type: font_size: float
    @param glpane: The 3D graphics area to draw it in.
    @type  glpane: L{GLPane}
    """
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 <= h:
        drawtext("%g" % (y1 / 10.0), text_color,
                 V(-hw - 3 * text_offset, y1 - hh, 0.0), font_size, glpane)
        y1 += uh  
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 <= w:
        drawtext("%g" % (x1 / 10.0), text_color,
                 V(x1 - hw, -hh - text_offset, 0.0), font_size, glpane)
        x1 += uw
    
    return

def displayLabelsAlongOriginLowerLeft(h, w, hh, hw, uh, uw,
                 text_offset, text_color, font_size, glpane):
 
    """
    Display labels when origin is on the lower left corner.
    
    @param h: height of the plane
    @type h: float
    @param w: width of the plane
    @type w: float
    @param hh: half the height of the plane
    @type hh: float
    @param hw: half the width of the plane
    @type hw: float
    @param uh: spacing along height of the plane
    @type uh: float
    @param uw: spacing along width of the plane
    @type uw: float
    @param text_offset: offset for label 
    @type text_offset: float
    @param text_color: color of the text
    @type: text_colot: tuple
    @param font_size: size of the text font
    @type: font_size: float
    @param glpane: The 3D graphics area to draw it in.
    @type  glpane: L{GLPane}
    """
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 >= -h:
        drawtext("%g" % (-y1 / 10.0), text_color,
                 V(-hw - 3 * text_offset, y1 + hh, 0.0), font_size, glpane)
        y1 -= uh  
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 <= w:
        drawtext("%g" % (x1 / 10.0), text_color,
                 V(x1 - hw, hh + 2 * text_offset, 0.0), font_size, glpane)
        x1 += uw    
    
    return

def displayLabelsAlongOriginUpperRight(h, w, hh, hw, uh, uw,
                  text_offset, text_color, font_size, glpane):
    """
    Display Labels when origin is on the upper right corner.
    
    @param h: height of the plane
    @type h: float
    @param w: width of the plane
    @type w: float
    @param hh: half the height of the plane
    @type hh: float
    @param hw: half the width of the plane
    @type hw: float
    @param uh: spacing along height of the plane
    @type uh: float
    @param uw: spacing along width of the plane
    @type uw: float
    @param text_offset: offset for label 
    @type text_offset: float
    @param text_color: color of the text
    @type: text_colot: tuple
    @param font_size: size of the text font
    @type: font_size: float
    @param glpane: The 3D graphics area to draw it in.
    @type  glpane: L{GLPane}
    """
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 <= h:
        drawtext("%g" % (y1 / 10.0), text_color,
                 V(hw + text_offset, y1 - hh, 0.0), font_size, glpane)
        y1 += uh  
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 >= -w:
        drawtext("%g" % (-x1 / 10.0), text_color,
                 V(x1 + hw, - hh - text_offset, 0.0), font_size, glpane)
        x1 -= uw
    return


def displayLabelsAlongPlaneEdgesLowerLeft(h, w ,hh, hw, uh, uw,
                     text_offset, text_color, font_size, glpane):
    """
    Display labels when origin is on the lower left corner.
    
    along all the plane edges
    @param h: height of the plane
    @type h: float
    @param w: width of the plane
    @type w: float
    @param hh: half the height of the plane
    @type hh: float
    @param hw: half the width of the plane
    @type hw: float
    @param uh: spacing along height of the plane
    @type uh: float
    @param uw: spacing along width of the plane
    @type uw: float
    @param text_offset: offset for label 
    @type text_offset: float
    @param text_color: color of the text
    @type: text_colot: tuple
    @param font_size: size of the text font
    @type: font_size: float
    @param glpane: The 3D graphics area to draw it in.
    @type  glpane: L{GLPane}
    """
    #Along the origin edges
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 >= -h:
        drawtext("%g" % (-y1 / 10.0), text_color,
                 V(-hw - 3 * text_offset, y1 + hh, 0.0), font_size, glpane)
        y1 -= uh  
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 <= w:
        drawtext("%g" % (x1 / 10.0), text_color,
                 V(x1 - hw, hh + 2 * text_offset, 0.0), font_size, glpane)
        x1 += uw 
    #Along the non origin edges
    
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 >= -h:
        drawtext("%g" % (-y1 / 10.0), text_color,
                 V(hw + 2 * text_offset, y1 + hh, 0.0), font_size, glpane)
        y1 -= uh  
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 <= w:
        drawtext("%g" % (x1 / 10.0), text_color,
                 V(x1 - hw, -hh - text_offset, 0.0), font_size, glpane)
        x1 += uw    
    return

def displayLabelsAlongPlaneEdgesUpperLeft(h, w, hh, hw, uh, uw, 
                     text_offset, text_color, font_size, glpane):
    """
    Display labels along plane edges when origin is on the upper left corner.
    
    @param h: height of the plane
    @type h: float
    @param w: width of the plane
    @type w: float
    @param hh: half the height of the plane
    @type hh: float
    @param hw: half the width of the plane
    @type hw: float
    @param uh: spacing along height of the plane
    @type uh: float
    @param uw: spacing along width of the plane
    @type uw: float
    @param text_offset: offset for label 
    @type text_offset: float
    @param text_color: color of the text
    @type: text_colot: tuple
    @param font_size: size of the text font
    @type: font_size: float
    @param glpane: The 3D graphics area to draw it in.
    @type  glpane: L{GLPane}
    """
    #Along origin edges
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 <= h:
        drawtext("%g" % (y1 / 10.0), text_color,
                 V(-hw - 3 * text_offset, y1-hh, 0.0), font_size, glpane)
        y1 += uh  
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 <= w:
        drawtext("%g" % (x1 / 10.0), text_color,
                 V(x1 - hw, -hh - text_offset, 0.0), font_size, glpane)
        x1 += uw
    #Along non origin edges
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 <= h:
        drawtext("%g" % (y1 / 10.0), text_color,
                 V(hw + 2 * text_offset, y1 - hh, 0.0), font_size, glpane)
        y1 += uh  
        
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 <= w:
        drawtext("%g" % (x1 / 10.0), text_color,
                 V(x1 - hw, hh + 2 * text_offset, 0.0), font_size, glpane)
        x1 += uw       
    return

def displayLabelsAlongPlaneEdgesLowerRight(h, w, hh, hw, uh, uw, 
                      text_offset, text_color, font_size, glpane):
    """
    Display labels along plane edges when origin is on the lower right corner
    @param h: height of the plane
    @type h: float
    @param w: width of the plane
    @type w: float
    @param hh: half the height of the plane
    @type hh: float
    @param hw: half the width of the plane
    @type hw: float
    @param uh: spacing along height of the plane
    @type uh: float
    @param uw: spacing along width of the plane
    @type uw: float
    @param text_offset: offset for label 
    @type text_offset: float
    @param text_color: color of the text
    @type: text_colot: tuple
    @param font_size: size of the text font
    @type: font_size: float
    @param glpane: The 3D graphics area to draw it in.
    @type  glpane: L{GLPane}
    """
    #Along origin edges
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 >= -h:
        drawtext("%g" % (-y1 / 10.0), text_color,
                 V(hw + 2 * text_offset, y1 + hh, 0.0), font_size, glpane)
        y1 -= uh  
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 >= -w:
        drawtext("%g" % (-x1 / 10.0), text_color,
                 V(x1 + hw, hh + 2 * text_offset, 0.0), font_size, glpane)
        x1 -= uw   
        
    #Along non origin edges  
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 >= -h:
        drawtext("%g" % (-y1 / 10.0), text_color,
                 V(-hw - 3 * text_offset, y1 + hh, 0.0), font_size, glpane)
        y1 -= uh  
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 >= -w:
        drawtext("%g" % (-x1 / 10.0), text_color,
                 V(x1 + hw, - hh - text_offset, 0.0), font_size, glpane)
        x1 -= uw    
    return

def displayLabelsAlongPlaneEdgesUpperRight(h, w, hh, hw, uh, uw, 
                      text_offset, text_color, font_size, glpane):
    """
    Display Labels along plane edges when origin is on the upper right corner
    @param h: height of the plane
    @type h: float
    @param w: width of the plane
    @type w: float
    @param hh: half the height of the plane
    @type hh: float
    @param hw: half the width of the plane
    @type hw: float
    @param uh: spacing along height of the plane
    @type uh: float
    @param uw: spacing along width of the plane
    @type uw: float
    @param text_offset: offset for label 
    @type text_offset: float
    @param text_color: color of the text
    @type: text_colot: tuple
    @param font_size: size of the text font
    @type: font_size: float
    @param glpane: The 3D graphics area to draw it in.
    @type  glpane: L{GLPane}
    """
    #Along origin edges
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 <= h:
        drawtext("%g" % (y1 / 10.0), text_color,
                 V(hw + text_offset, y1 - hh, 0.0), font_size, glpane)
        y1 += uh  
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 >= -w:
        drawtext("%g" % (-x1 / 10.0), text_color,
                 V(x1 + hw, - hh - text_offset, 0.0), font_size, glpane)
        x1 -= uw
        
    #Along non-origin edges
    # Draw unit text labels for horizontal lines (nm)
    y1 = 0
    while y1 <= h:
        drawtext("%g" % (y1 / 10.0), text_color,
                 V(-hw - 3 * text_offset, y1 - hh, 0.0), font_size, glpane)
        y1 += uh  
        
    # Draw unit text labels for vertical lines (nm).
    x1 = 0
    while x1 >= -w:
        drawtext("%g" % (-x1 / 10.0), text_color,
                 V(x1 + hw, hh + 2 * text_offset, 0.0), font_size, glpane)
        x1 -= uw       
    return

def drawSiCGrid(color, line_type, w, h, up, right):
    """
    Draw SiC grid.
    """
    
    if line_type == NO_LINE:
        return
    
    XLen = sic_uLen * 3.0
    YLen = sic_yU * 2.0
    hw = w/2.0; hh = h/2.0
    i1 = int(floor(-hw/XLen))
    i2 = int(ceil(hw/XLen))
    j1 = int(floor(-hh/YLen))
    j2 = int(ceil(hh/YLen))
    
    glDisable(GL_LIGHTING)
    glColor3fv(color)

    if line_type > 1:
        glEnable(GL_LINE_STIPPLE)
        if line_type == DASHED_LINE:
            glLineStipple (1, 0x00FF)  #  dashed
        elif line_type == DOTTED_LINE:
            glLineStipple (1, 0x0101)  #  dotted
        else:
            print "drawer.drawSiCGrid(): line_type '", line_type, \
                  "' is not valid.  Drawing dashed grid line."
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

    xpos, ypos = hw, 0.0
    f3d = Font3D(xpos=xpos, ypos=ypos, right=right, up=up,
                 rot90=False, glBegin=False)
    for j in range(j1, j2):
        yoff = j * YLen
        if -hh < yoff + ypos < hh:
            f3d.drawString("%-.4g" % yoff, color=color, yoff=yoff)

    xpos, ypos = 0.0, hh
    f3d = Font3D(xpos=xpos, ypos=ypos, right=right, up=up,
                 rot90=True, glBegin=False)
    for i in range(2*i1, 2*i2):
        yoff = i * (XLen/2)
        if -hw < yoff + xpos < hw:
            f3d.drawString("%-.4g" % yoff, color=color, yoff=yoff)
    
    glEnable(GL_LIGHTING)
    return

# end
