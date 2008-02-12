# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Draws the DNA ribbons where each strand is represented as a ribbon. DNA ribbons
are drawn as sine waves 

@author:    Mark
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
"""


from Numeric import pi
ONE_RADIAN = 180.0 / pi
HALF_PI  = pi/2.0
TWICE_PI = 2*pi

from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix
from OpenGL.GL import GL_BLEND
from OpenGL.GL import glBlendFunc
from OpenGL.GL import glColor4fv
from OpenGL.GL import glDepthMask
from OpenGL.GL import GL_FALSE
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_TRUE
from OpenGL.GL import glViewport
from OpenGL.GLU import gluOrtho2D
from OpenGL.GL import GL_SRC_ALPHA
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import glRectf
from OpenGL.GL import GL_PROJECTION
from drawer import drawline
from drawer import drawtext
from geometry.VQT import V
from constants import  lightgray, darkgray, black

import env
from prefs_constants import rulerColor_prefs_key
from prefs_constants import rulerOpacity_prefs_key


def drawRulers(glpane):
    """
    Draws a vertical ruler on the left side of the 3D graphics area.
    
    A 2D window (pixel) coordinate system is created locally, where:
    - The lower left corner is  (   0.0,    0.0, 0.0)
    - The upper right corner is ( width, height, 0.0)
    
    It doesn't matter what coordinate system you are in when you call this
    function, and the system will not be harmed, but it does use one level
    on each matrix stack, and it does set matrixmode to GL_MODELVIEW before
    returning.
    
    Still to do:
    - Transparent ruler and its tickmarks are obscured by the model (but not
      the labels). Fix this.
    - Once we're happy with the vertical ruler, add support for an (optional)
      horizontal ruler.
    
    @param glpane: the 3D graphics area.
    @type  glpane: L{GLPane)
    """
    
    width = glpane.width
    height = glpane.height
    scale = glpane.scale
    
    glViewport (0, 0, int(width), int(height) )
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity() # needed!
    gluOrtho2D(0.0, float(width), 0.0, float(height))
    
    # Turn off depth masking so anything under the cursor will still get picked.
    glDepthMask(GL_FALSE)
    
    ruler_color = env.prefs[rulerColor_prefs_key]
    ruler_opacity = env.prefs[rulerOpacity_prefs_key] # 0.7 is a good default.
    tickmark_color = darkgray
    text_color = black
    font_size = 8
    
    long_tick_len   = 15
    medium_tick_len = 10
    short_tick_len  = 5
    ruler_thickness = long_tick_len + 4
    
    # Set to False for left justified tickmarks
    tickmarks_right_justified = True 
    
    num_horz_ticks = int(scale * 2.0)
    tickmark_spacing = 0.5 / scale * height
    tickmark_spacing_multiplier = 1.0
    
    # Be careful if you changes these values.
    # Talk to Bruce about this section. Should I build some kind of hash/dict?
    # Mark 2008-02-07
    if scale <= 2.75:
        units_text = "A" # Angstroms
        units_format = "%2d"
        units_scale = 1.0
        unit_label_inc = 1
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
    elif scale <= 10.1:
        units_text = "A" # Angstroms
        units_format = "%2d"
        units_scale = 1.0
        unit_label_inc = 5
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
    elif scale <= 25.1:
        units_text = "nm" # nanometers
        units_format = "%-3.1f"
        units_scale = 0.1
        unit_label_inc = 5
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
    elif scale <= 51.0:
        units_text = "nm" # nanometers
        units_format = "%2d"
        units_scale = 0.1
        unit_label_inc = 10
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
    elif scale <= 101.0:
        units_text = "nm" # nanometers
        units_format = "%2d"
        units_scale = .5
        unit_label_inc = 2
        long_tickmark_inc = 10
        medium_tickmark_inc = 2
        num_horz_ticks = int(num_horz_ticks * 0.2)
        tickmark_spacing_multiplier = 5.0
    elif scale <= 501.0:
        units_text = "nm" # nanometers
        units_format = "%2d"
        units_scale = 1.0
        unit_label_inc = 5
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
        num_horz_ticks = int(num_horz_ticks * 0.1)
        tickmark_spacing_multiplier = 10.0
    elif scale <= 1001.0:
        units_text = "nm" # nanometers
        units_format = "%2d"
        units_scale = 1.0
        unit_label_inc = 10
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
        num_horz_ticks = int(num_horz_ticks * 0.1)
        tickmark_spacing_multiplier = 10.0
    elif scale <= 2505.0:
        units_text = "nm" # nanometers
        units_format = "%2d"
        units_scale = 2.0
        unit_label_inc = 10
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
        num_horz_ticks = int(num_horz_ticks * 0.05)
        tickmark_spacing_multiplier = 20.0
    elif scale <= 5005.0:
        units_text = "Um" # micrometers
        units_format = "%-3.1f"
        units_scale = 0.01
        unit_label_inc = 10
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
        num_horz_ticks = int(num_horz_ticks * 0.01)
        tickmark_spacing_multiplier = 100.0
    elif scale <= 15005.0:
        units_text = "Um" # micrometers
        units_format = "%-3.1f"
        units_scale = 0.1
        unit_label_inc = 1
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
        num_horz_ticks = int(num_horz_ticks * 0.001)
        tickmark_spacing_multiplier = 1000.0
    elif scale <= 25005.0:
        units_text = "Um" # micrometers
        units_format = "%-3.1f"
        units_scale = 0.1
        unit_label_inc = 5
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
        num_horz_ticks = int(num_horz_ticks * 0.001)
        tickmark_spacing_multiplier = 1000.0
    else:
        units_text = "Um" # micrometers
        units_format = "%2d"
        units_scale = 0.1
        unit_label_inc = 10
        long_tickmark_inc = 10
        medium_tickmark_inc = 5
        num_horz_ticks = int(num_horz_ticks * 0.001)
        tickmark_spacing_multiplier = 1000.0
    
    DEBUG = False
    if DEBUG:
        print "ticks=", num_horz_ticks, "tickmark_spacing=", tickmark_spacing, "scale=", scale
        print "units_scale=", units_scale, "unit_label_inc=", unit_label_inc
    
    # Draw semi-transparent ruler rectangle.
    if 1:
        glColor4fv(list(ruler_color) + [ruler_opacity])
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glRectf(0.0, 0.0, ruler_thickness, height)
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)
        
        # Draw vertical line along right edge of ruler.
        pt1 = V(ruler_thickness, 0.0, 0.0)
        pt2 = V(ruler_thickness, height, 0.0)
        drawline(tickmark_color, pt1, pt2)
        
        # Draw horizontal line along bottom edge of ruler.
        if 0:
            pt1 = V(  0.0, height - ruler_thickness, 0.0)
            pt2 = V(width, height - ruler_thickness, 0.0)
            drawline(tickmark_color, pt1, pt2)
    
    units_text_origin = V(2.0, height - ruler_thickness + 4.0, 0.0)
    
    # Draw unit of measurement in upper left corner (A or nm).
    drawtext(units_text, text_color, units_text_origin, font_size, glpane)
    
    # Initialize pt1 and pt2. They are both modified in the loop below.
    # Left/right justification needed if we decide to allow rules on left or 
    # right side of glpane.
    if tickmarks_right_justified:
        pt1 = V(ruler_thickness, height - ruler_thickness, 0.0)
        pt2 = pt1 + V(-ruler_thickness, 0.0, 0.0)
        long_tick_len   *= -1.0
        medium_tick_len *= -1.0
        short_tick_len  *= -1.0
        HORZ_UNITS_X_OFFSET =  -ruler_thickness
        HORZ_UNITS_Y_OFFSET =  -10.0
    else:
        pt1 = V(0.0, height - ruler_thickness, 0.0)
        pt2 = pt1 + V(ruler_thickness, 0.0, 0.0)
        HORZ_UNITS_X_OFFSET =  0
        HORZ_UNITS_Y_OFFSET =  -10.0
    
    # Save starting points. They are used by each iteration of the loop below.
    start_pt1 = pt1
    start_pt2 = pt2

    # Draw vertical ruler tickmarks, including numeric unit labels
    for tick_num in range(num_horz_ticks + 1):
        
        # pt1 and pt2 are modified by each iteration of the loop (below).
        drawline(tickmark_color, pt1, pt2)
        
        # Draw units number below long tickmarks.
        if not tick_num % unit_label_inc:
            units_num_origin = pt1 + V(HORZ_UNITS_X_OFFSET, HORZ_UNITS_Y_OFFSET, 0.0)
            units_num = units_format % (tick_num * units_scale)
            drawtext(units_num, text_color, units_num_origin, font_size, glpane)
            
        # Update tickmark endpoints for next tickmark.
        pt1 = \
            start_pt1 + \
            V(0.0, 
              -tickmark_spacing * tickmark_spacing_multiplier * (tick_num + 1),
              0.0)
        
        if not (tick_num + 1) % long_tickmark_inc:
            pt2 = pt1 + V(long_tick_len, 0.0, 0.0)
        elif not (tick_num + 1) % medium_tickmark_inc:
            pt2 = pt1 + V(medium_tick_len, 0.0, 0.0)
        else:
            pt2 = pt1 + V(short_tick_len, 0.0, 0.0)
    
    glDepthMask(GL_TRUE)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    return # from drawRulers

