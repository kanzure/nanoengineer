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
HALF_PI  = pi / 2.0
TWICE_PI = 2 * pi

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
from prefs_constants import displayVertRuler_prefs_key
from prefs_constants import displayHorzRuler_prefs_key
from prefs_constants import rulerPosition_prefs_key
from prefs_constants import rulerColor_prefs_key
from prefs_constants import rulerOpacity_prefs_key

# These must match the order items appear in the ruler "Position" combobox
# in the preferences dialog.
LOWER_LEFT = 0
UPPER_LEFT = 1
LOWER_RIGHT = 2
UPPER_RIGHT = 3

def drawRulers(glpane):
    """
    Draws a set of vertical and horizontal rulers in the 3D graphics area.
    
    A 2D window (pixel) coordinate system is created locally, where:
    - The lower left corner is  (   0.0,    0.0, 0.0)
    - The upper right corner is ( width, height, 0.0)
    
    This schematic shows the 2D window coodinate system with the rulers 
    positioned in the lower left corner (their default position).
    
                                                             (width, height)
                                                              /
                  +---+--------------------------------------+
                  |   |                                      |
                  | v |                                      |
                  | e |                                      |
                  | r |                                      |
                  | t |                                      |
                  | i |                                      |
                  | c |                                      |
                  | a |  ruler_start_pt                      |
                  | l | (hr_thickness, vr_thickness, 0.0)    |
                  |   |/                                     |
                  +---+--------------------------------------+
                  | A |              horizontal              |
                  +---+--------------------------------------+
                 / 
     ruler_origin
    (0.0, 0.0, 0.0)
             
    It doesn't matter what coordinate system you are in when you call this
    function, and the system will not be harmed, but it does use one level
    on each matrix stack, and it does set matrixmode to GL_MODELVIEW before
    returning.
    
    Still to do:
    - For optimization and cleaner code, convert into a class called "Guides".
      Doing so will improve redraw performance since ruler and tick mark 
      parameters will only be recomputed when necessary and not every time the
      rulers are redrawn (which is the case now). Discuss this plan with Bruce.
    - Add support for 2D gridlines.
    - Allow user to control ruler thickness, font size, tick mark color, etc.
      via user preferences. (nice to have)
    - Center unit text in origin square (using QFontMetrics class to do this).
    - Transparent ruler and its tick marks are obscured by the model (but not
      the ruler unit labels). This is a "nice to have" fix.
    
    @param glpane: the 3D graphics area.
    @type  glpane: L{GLPane)
    
    @note: There is a pref key called I{displayRulers_prefs_key} that is set
    from the "View > Rulers" menu item. It is used in this function's sole
    caller (GLPane.standard_repaint_0()) to determine whether to draw any
    ruler(s). It is not used here.
    """
    
    display_vr = env.prefs[displayVertRuler_prefs_key]
    display_hr = env.prefs[displayHorzRuler_prefs_key]
    ruler_position = env.prefs[rulerPosition_prefs_key]
    ruler_color = env.prefs[rulerColor_prefs_key]
    ruler_opacity = env.prefs[rulerOpacity_prefs_key]
    
    width = glpane.width
    height = glpane.height
    scale = glpane.scale
    aspect = glpane.aspect
    
    # Set up 2D (window) coordinate system.
    glViewport (0, 0, int(width), int(height) )
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity() # needed!
    gluOrtho2D(0.0, float(width), 0.0, float(height))
    
    # Turn off depth masking so anything behind the ruler will still get picked.
    glDepthMask(GL_FALSE)
    
    num_horz_ticks = int(scale * 2.0)
    num_vert_ticks = int(num_horz_ticks * aspect) + 1
    tickmark_spacing = 0.5 / scale * height
    tickmark_spacing_multiplier = 1.0
    
    # This section computes the the tick mark drawing parameters based on the
    # scale of the 3D graphics area. Be careful if you changes these values.
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
    
    
    tickmark_color = darkgray
    text_color = black
    font_size = 7
    
    # Computer ruler width based on font size, which should be a user pref for 
    # far-sighted users that need larger unit text in rulers. Mark 2008-02-20
    ruler_thickness = 15.0 
    
    vr_thickness = ruler_thickness
    hr_thickness = ruler_thickness
    
    vr_long_tick_len   = vr_thickness * 0.75
    vr_medium_tick_len = vr_thickness * 0.5
    vr_short_tick_len  = vr_thickness * 0.25
    
    hr_long_tick_len   = vr_thickness * 0.75
    hr_medium_tick_len = vr_thickness * 0.5
    hr_short_tick_len  = vr_thickness * 0.25
    
    if ruler_position == LOWER_LEFT:
        ruler_origin = V(0.0, 0.0, 0.0)
        units_text_origin = V(3.0, 5.0, 0.0)
        
        ruler_start_pt = ruler_origin \
                       + V(vr_thickness, hr_thickness, 0.0)
        
        origin_square_pt1 = V(0.0, 0.0, 0.0)
        origin_square_pt2 = V(vr_thickness, hr_thickness, 0.0)
        
        # VR vars.
        vr_rect_pt1 = V(0.0, hr_thickness, 0.0)
        vr_rect_pt2 = V(vr_thickness, height, 0.0)
        
        vr_line_pt1 = V(vr_thickness, 0.0, 0.0)
        vr_line_pt2 = V(vr_thickness, height, 0.0)
        
        vr_long_tick_len   *= -1.0
        vr_medium_tick_len *= -1.0
        vr_short_tick_len  *= -1.0
        
        vr_units_x_offset =  -vr_thickness
        vr_units_y_offset =  3.0
        
        vr_tickmark_spacing = tickmark_spacing
        
        # HR vars.
        hr_rect_pt1 = V(vr_thickness, 0.0, 0.0)
        hr_rect_pt2 = V(width, hr_thickness, 0.0)
        
        hr_line_pt1 = V(0.0, hr_thickness, 0.0)
        hr_line_pt2 = V(width, hr_thickness, 0.0)
        
        hr_long_tick_len   *= -1.0
        hr_medium_tick_len *= -1.0
        hr_short_tick_len  *= -1.0
        
        hr_units_x_offset =  3.0
        hr_units_y_offset =  -hr_thickness * 0.8
    
        hr_tickmark_spacing = tickmark_spacing
        
    elif ruler_position == UPPER_LEFT:
        hr_thickness *= -1 # Note: Thickness is a negative value.
        
        ruler_origin = V(0.0, height, 0.0)
        units_text_origin = ruler_origin \
                          + V(3.0, hr_thickness + 4.0, 0.0)
        
        ruler_start_pt = ruler_origin \
                       + V(vr_thickness, hr_thickness, 0.0)
        
        origin_square_pt1 = V(0.0, height + hr_thickness, 0.0)
        origin_square_pt2 = V(vr_thickness, height, 0.0)
        
        # VR vars.
        vr_rect_pt1 = V(0.0, 0.0, 0.0)
        vr_rect_pt2 = V(vr_thickness, height + hr_thickness, 0.0)
        
        vr_line_pt1 = V(vr_thickness, 0.0, 0.0)
        vr_line_pt2 = V(vr_thickness, height, 0.0)
        
        vr_long_tick_len   *= -1.0
        vr_medium_tick_len *= -1.0
        vr_short_tick_len  *= -1.0
        
        vr_units_x_offset =  -vr_thickness
        vr_units_y_offset =  -10.0
        
        # HR vars.
        hr_rect_pt1 = V(vr_thickness, height + hr_thickness, 0.0)
        hr_rect_pt2 = V(width, height, 0.0)
        
        hr_line_pt1 = V(0, height + hr_thickness, 0.0)
        hr_line_pt2 = V(width, height + hr_thickness, 0.0)
        
        hr_units_x_offset =  3.0
        hr_units_y_offset =  -hr_thickness * 0.5
        
        vr_tickmark_spacing = -tickmark_spacing
        hr_tickmark_spacing =  tickmark_spacing

    elif ruler_position == LOWER_RIGHT:
        ruler_origin = V(width, 0.0, 0.0)
        vr_thickness *= -1 # Note: Thickness is a negative value.
        units_text_origin = ruler_origin + V(vr_thickness + 3.0, 2.0, 0.0)
        
        ruler_start_pt = ruler_origin \
                       + V(vr_thickness, hr_thickness, 0.0)
        
        origin_square_pt1 = V(width + vr_thickness, 0.0, 0.0)
        origin_square_pt2 = V(width, hr_thickness, 0.0)
        
        # VR vars.
        vr_rect_pt1 = V(width + vr_thickness, hr_thickness, 0.0)
        vr_rect_pt2 = V(width, height, 0.0)
        
        vr_line_pt1 = V(width + vr_thickness, 0.0, 0.0)
        vr_line_pt2 = V(width + vr_thickness, height, 0.0)
        
        vr_units_x_offset =  3.0 #@ Need way to right justify unit text!
        vr_units_y_offset =  3.0
        
        vr_tickmark_spacing = tickmark_spacing
        
        # HR vars.
        hr_rect_pt1 = V(0.0, 0.0, 0.0)
        hr_rect_pt2 = V(width + vr_thickness, hr_thickness, 0.0)
        
        hr_line_pt1 = V(0.0, hr_thickness, 0.0)
        hr_line_pt2 = V(width, hr_thickness, 0.0)
        
        hr_long_tick_len   *= -1.0
        hr_medium_tick_len *= -1.0
        hr_short_tick_len  *= -1.0
        
        hr_units_x_offset =  -15.0 #@ Need way to right justify unit text!
        hr_units_y_offset =  -hr_thickness * 0.8
    
        hr_tickmark_spacing = -tickmark_spacing
        
    elif ruler_position == UPPER_RIGHT:
        ruler_origin = V(width, height, 0.0)
        vr_thickness *= -1 # Note: Thickness is a negative value.
        hr_thickness *= -1 # Note: Thickness is a negative value.
        units_text_origin = ruler_origin + V(vr_thickness * 0.8, hr_thickness * 0.8, 0.0)
        
        ruler_start_pt = ruler_origin \
                       + V(vr_thickness, hr_thickness, 0.0)
        
        origin_square_pt1 = V(width + vr_thickness, height + hr_thickness, 0.0)
        origin_square_pt2 = V(width, height, 0.0)
        
        # VR vars.
        vr_rect_pt1 = V(width + vr_thickness, 0.0, 0.0)
        vr_rect_pt2 = V(width, height + hr_thickness, 0.0)
        
        vr_line_pt1 = V(width + vr_thickness,    0.0, 0.0)
        vr_line_pt2 = V(width + vr_thickness, height, 0.0)
        
        vr_units_x_offset =  3.0 #@ Need way to right justify unit text!
        vr_units_y_offset =  -10.0
        
        vr_tickmark_spacing = -tickmark_spacing
        
        # HR vars.
        hr_rect_pt1 = V(0.0, height + hr_thickness, 0.0)
        hr_rect_pt2 = V(width + vr_thickness, height, 0.0)
        
        hr_line_pt1 = V(  0.0, height + hr_thickness, 0.0)
        hr_line_pt2 = V(width, height + hr_thickness, 0.0)
        
        hr_units_x_offset =  -15.0 #@ Need way to right justify unit text!
        hr_units_y_offset =  -hr_thickness * 0.5
    
        hr_tickmark_spacing = -tickmark_spacing
    
    else:
        msg = "bug: Illegal ruler position value (must be 0-3). Current value"\
                                "is %d. Ignoring." % ruler_position
        print_compact_stack(msg)
        return 
    
    # Draw v/h ruler rectangles in the user defined color and opacity.
    glColor4fv(list(ruler_color) + [ruler_opacity])
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glRectf(origin_square_pt1[0], origin_square_pt1[1], 
            origin_square_pt2[0], origin_square_pt2[1]) # Origin square
    if display_vr:
        glRectf(vr_rect_pt1[0], vr_rect_pt1[1], 
                vr_rect_pt2[0], vr_rect_pt2[1]) # Vertical ruler
    if display_hr:
        glRectf(hr_rect_pt1[0], hr_rect_pt1[1], 
                hr_rect_pt2[0], hr_rect_pt2[1]) # Horizontal ruler
    glEnable(GL_LIGHTING)
    glDisable(GL_BLEND)
    
    # Draw unit of measurement in corner (A or nm).
    drawtext(units_text, text_color, units_text_origin, font_size, glpane)

    # Draw vertical ruler line(s) and tick marks ###############################
    
    if display_vr:
    
        # Draw vertical line along right/left edge of ruler.
        drawline(tickmark_color, vr_line_pt1, vr_line_pt2)
        
        # Initialize pt1 and pt2, the tick mark endpoints. The first tick mark
        # will span the entire width of the ruler,  which serves as a divider
        # b/w the unit of measure text (i.e. A or nm) and the rest of the ruler.
        pt1 = ruler_start_pt
        pt2 = ruler_start_pt + V(-vr_thickness, 0.0, 0.0)
        
        # Draw vertical ruler tickmarks, including numeric unit labels
        for tick_num in range(num_horz_ticks + 1):
            
            # pt1 and pt2 are modified by each iteration of the loop (below).
            drawline(tickmark_color, pt1, pt2)
            
            # Draw units number beside long tickmarks.
            if not tick_num % unit_label_inc:
                units_num_origin = pt1 \
                                 + V(vr_units_x_offset, 
                                     vr_units_y_offset, 
                                     0.0)
                units_num = units_format % (tick_num * units_scale)
                drawtext(units_num, text_color, units_num_origin, font_size, glpane)
                
            # Update tickmark endpoints for next tickmark.
            pt1 = ruler_start_pt + \
                V(0.0, 
                  vr_tickmark_spacing * tickmark_spacing_multiplier * (tick_num + 1),
                  0.0)
            
            if not (tick_num + 1) % long_tickmark_inc:
                pt2 = pt1 + V(vr_long_tick_len, 0.0, 0.0)
            elif not (tick_num + 1) % medium_tickmark_inc:
                pt2 = pt1 + V(vr_medium_tick_len, 0.0, 0.0)
            else:
                pt2 = pt1 + V(vr_short_tick_len, 0.0, 0.0)
    
        # End vertical ruler
    
    # Draw horizontal ruler line(s) and tick marks #############################
    
    if display_hr:
        # Draw horizontal line along top/bottom edge of ruler.
        drawline(tickmark_color, hr_line_pt1, hr_line_pt2)
        
        # Initialize pt1 and pt2, the tick mark endpoints. The first tick mark
        # will span the entire width of the ruler,  which serves as a divider
        # b/w the unit of measure text (i.e. A or nm) and the rest of the ruler.
        pt1 = ruler_start_pt
        pt2 = ruler_start_pt + V(0.0, -hr_thickness, 0.0) 
    
        # Draw horizontal ruler (with vertical) tickmarks, including its
        # numeric unit labels
        for tick_num in range(num_vert_ticks + 1):
            
            # pt1 and pt2 are modified by each iteration of the loop (below).
            drawline(tickmark_color, pt1, pt2)
            
            # Draw units number beside long tickmarks.
            if not tick_num % unit_label_inc:
                units_num_origin = pt1 \
                                 + V(hr_units_x_offset, 
                                     hr_units_y_offset, 
                                     0.0)
                units_num = units_format % (tick_num * units_scale)
                drawtext(units_num, text_color, units_num_origin, font_size, glpane)
                
            # Update tickmark endpoints for next tickmark.
            pt1 = \
                ruler_start_pt + \
                V(hr_tickmark_spacing * tickmark_spacing_multiplier * (tick_num + 1),
                  0.0,
                  0.0)
            
            if not (tick_num + 1) % long_tickmark_inc:
                pt2 = pt1 + V(0.0, hr_long_tick_len, 0.0)
            elif not (tick_num + 1) % medium_tickmark_inc:
                pt2 = pt1 + V(0.0, hr_medium_tick_len, 0.0)
            else:
                pt2 = pt1 + V(0.0, hr_short_tick_len, 0.0)
        
        # End horizontal ruler
    
    # Restore OpenGL state.
    glDepthMask(GL_TRUE)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    return # from drawRulers

