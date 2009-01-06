# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_text_and_color_methods.py - methods for GLPane related to
text rendering or backgroundColor/backgroundGradient

(Maybe it should be renamed GLPane_text_and_background_methods?)

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

bruce 080910 split this out of class GLPane
"""

from OpenGL.GL import glEnable
from OpenGL.GL import glDisable
from OpenGL.GL import GL_LIGHTING

from OpenGL.GL import glClear
from OpenGL.GL import glClearColor
from OpenGL.GL import GL_COLOR_BUFFER_BIT

from OpenGL.GL import glTexEnvf
from OpenGL.GL import GL_TEXTURE_ENV
from OpenGL.GL import GL_TEXTURE_ENV_MODE
from OpenGL.GL import GL_MODULATE

from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import glLoadIdentity

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix

from OpenGL.GLU import gluUnProject, gluProject


from graphics.drawing.drawers import drawFullWindow
          
from widgets.widget_helpers import RGBf_to_QColor

from PyQt4.Qt import QFontMetrics
from PyQt4.Qt import QFont, QString
from PyQt4.Qt import QPalette
from PyQt4.Qt import QColor

import foundation.env as env
from utilities.debug import print_compact_stack

from utilities.constants import black, white
from utilities.constants import getTextHaloColor

from utilities.constants import bgSOLID, bgBLUE_SKY, bgEVENING_SKY, bgSEAGREEN
from utilities.constants import bluesky, eveningsky, bg_seagreen
from utilities.constants import ave_colors, colors_differ_sufficiently

from utilities.prefs_constants import DarkBackgroundContrastColor_prefs_key
from utilities.prefs_constants import LightBackgroundContrastColor_prefs_key

from utilities.prefs_constants import backgroundColor_prefs_key
from utilities.prefs_constants import backgroundGradient_prefs_key

from utilities.prefs_constants import originAxisColor_prefs_key

assert bgSOLID == 0 # some code in GLPane depends on this

# ==

def _backgroundGradient_params(backgroundGradient, bgColor = None):
    """
    Given a backgroundGradient code (a small int of the kind
    stored in self.backgroundGradient), and if that is bgSOLID,
    a background color, return a 4-tuple of colors (for glpane corners)
    which it represents, and a boolean about whether to consider it "dark"
    for purposes such as cursor selection.
    """
    #bruce 080910 split this out of GLPane.standard_repaint_0;
    # ideally we'd turn this code into some sort of "background class"
    # with a subclass for solid and a few instances or singleton
    # subclasses for particular gradients, with the parameters
    # returned here (also fogColor) becoming attributes or methods.

    # for now only a few specific gradient backgrounds are supported

    if backgroundGradient == bgSOLID:
        assert bgColor is not None
        _bgGradient = (bgColor, bgColor, bgColor, bgColor)
        darkQ = not colors_differ_sufficiently(bgColor, black)
    elif backgroundGradient == bgBLUE_SKY:
        _bgGradient = bluesky
        darkQ = False
    elif backgroundGradient == bgEVENING_SKY:
        _bgGradient = eveningsky
        darkQ = True
    elif backgroundGradient == bgSEAGREEN:
        _bgGradient = bg_seagreen
        darkQ = False
    else:
        msg = "Warning: Unknown background gradient = %s. "\
            "Setting gradient to evening sky" % backgroundGradient
        print_compact_stack(msg + ": ")
        _bgGradient = eveningsky
        darkQ = True
    return _bgGradient, darkQ

# ==

class GLPane_text_and_color_methods(object):
    """
    private mixin for providing text- and color-related methods
    to class GLPane
    """
    def renderTextAtPosition(self,
                             position,
                             textString,
                             textColor = black,
                             textFont = None,
                             fontSize = 11,
                             ):
        """
        Renders the text at the specified position (x, y, z coordinates)
        @param position: The x, y, z coordinates of the object at which the 
        text needs to be rendered. 
        @type position: B{A}
        @param textString:  the text to be rendered at the specified position.
        @type textString : str
        @see: self.renderTextNearCursor() This method is different than that 
        method. That method uses QPoint (the current cursor position) to 
        render the text (thus needs integers x and y) whereas this method
        uses the actual object coordinates        
        @see: MultiplednaSegment_GraphicsMode._drawDnaRubberbandLine() [obsolete class name, what is correct one?]
        @see: QGLWidget.renderText()

        @TODO: refactor to move the common code in this method and
        self.renderTextNearCursor().
        """
        
        if textFont is not None:
            font = textFont
        else:
            font = self._getFontForTextNearCursor(fontSize = fontSize, 
                                                  isBold = True)
        x = position[0]
        y = position[1]
        z = position[2]

        glDisable(GL_LIGHTING)
        
        #Convert the object coordinates to the window coordinates.
        wX, wY, wZ = gluProject(x, y, z)
        
        halo_color = getTextHaloColor(textColor)
        
        offset_val = 1
        bg_z_offset = 0
        fg_z_offset = -1e-7

        render_positions = (( offset_val,  offset_val, bg_z_offset, halo_color), 
                            (-offset_val, -offset_val, bg_z_offset, halo_color), 
                            (-offset_val,  offset_val, bg_z_offset, halo_color), 
                            ( offset_val, -offset_val, bg_z_offset, halo_color),
                            (          0,           0, fg_z_offset, textColor))

        for dx, dy, dz, color in render_positions:
            x1, y1, z1 = gluUnProject(wX + dx, wY + dy, wZ + dz)

            self.qglColor(RGBf_to_QColor(color)) 
            self.renderText(x1, y1, z1,
                            QString(textString),
                            font)
##            self.qglClearColor(RGBf_to_QColor(color))
##            # question: is this related to glClearColor? [bruce 071214 question]
##            # -- yes [Ninad 2008-08-20]

        glEnable(GL_LIGHTING)        

    def renderTextNearCursor(self, 
                             textString, 
                             offset = 10, 
                             textColor = black,
                             fontSize = 11):
        """
        Renders text near the cursor position, on the top right side of the
        cursor (slightly above it).

        See example in DNA Line mode.

        @param textString: string
        @param offset: The offset that will be added to x and y values of the 
                       cursor position to get the base position of the text 
                       to be rendered. 

        @see: DnaLineMode.Draw
        @see: self._getFontForTextNearCursor()
        @see: self.renderTextAtPosition()
        """
        if not textString:
            return 

        #Extra precaution if the caller passes a junk value such as None
        #for the color
        if not isinstance(textColor, tuple) and isinstance(textColor, list):
            textColor = black

        pos = self.cursor().pos()  
        
        # x, y coordinates need to be in window coordinate system. 
        # See QGLWidget.mapToGlobal for more details.
        pos = self.mapFromGlobal(pos)

        # Important to turn off the lighting. Otherwise the text color would 
        # be dull and may also become even more light if some other object 
        # is rendered as a transparent object. Example in DNA Line mode, when the
        # second axis end sphere is rendered as a transparent sphere, it affects
        # the text rendering as well (if GL_LIGHTING is not disabled)
        # [-- Ninad 2007-12-03]
        glDisable(GL_LIGHTING)
        
        ############
        #Add 'stoppers' for the cursor text. Example: If the cursor is near the
        #extreme right hand corner of the 3D workspace, the following code 
        #ensures that all the text string is visible. It does this check for 
        #right(x) and top(for y) borders of the glpane. 
        
        xOffset = offset
        yOffset = offset
        #signForDX and signForDY are used by the code that draws the same 
        #text in the background (offset by 1 pixel in 4 directions) 
        signForDX = 1
        signForDY = 1
             
        xLimit = self.width - pos.x()
        
        #Note that at the top edge, y coord is 0
        yLimit = pos.y()
        
        textString = QString(textString)
        font = self._getFontForTextNearCursor(fontSize = fontSize,
                                              isBold = True)
        
        #Now determine the total x and y pixels used to render the text 
        #(add some tolerance to that number) 
        fm = QFontMetrics(font)
        xPixels = fm.width(textString) + 10
        yPixels = fm.height() + 10
 
        if xLimit < xPixels:
            xOffset = - (xPixels - xLimit)
            signForDX = -1
        
        if yLimit < yPixels:
            yOffset = - (yPixels - pos.y())
            signForDY = -1
                        
        x = pos.x() + xOffset
        y = pos.y() - yOffset
        
        offset_val = 1

        deltas_for_halo_color = (( offset_val,  offset_val), 
                                 (-offset_val, -offset_val), 
                                 (-offset_val,  offset_val), 
                                 ( offset_val, -offset_val))
        
        # halo color
        halo_color = getTextHaloColor(textColor)
        
        for dx, dy in deltas_for_halo_color: 
            self.qglColor(RGBf_to_QColor(halo_color)) 

            ### Note: self.renderText is QGLWidget.renderText method.
            self.renderText(x + dx*signForDX ,
                            y + dy*signForDY,
                            textString,
                            font)
##            self.qglClearColor(RGBf_to_QColor(halo_color))
##                # REVIEW: why is qglClearColor needed here? Why is it done *after* renderText?
##                # [bruce 081204 questions; same Qs for the other uses of qglClearColor in this file]

        # Note: It is necessary to set the font color, otherwise it may change!

        self.qglColor(RGBf_to_QColor(textColor))   
        x = pos.x() + xOffset
        y = pos.y() - yOffset

        self.renderText(x ,
                        y ,
                        textString,
                        font)
##        self.qglClearColor(RGBf_to_QColor(textColor))
##            # is qglClearColor related to glClearColor? [bruce 071214 question]
        glEnable(GL_LIGHTING)

    def _getFontForTextNearCursor(self, fontSize = 10, isBold = False):
        """
        Returns the font for text near the cursor. 
        @see: self.renderTextNearCursor
        """
        font = QFont("Arial", fontSize)
        font.setBold(isBold)              
        return font

    # == Background color helper methods. written and/or moved to GLPane by Mark 060814.

    def restoreDefaultBackground(self):
        """
        Restore the default background color and gradient (Sky Blue).
        Always do a gl_update.
        """
        env.prefs.restore_defaults([
            backgroundColor_prefs_key, 
            backgroundGradient_prefs_key, 
        ])

        self.setBackgroundColor(env.prefs[ backgroundColor_prefs_key ])
        self.setBackgroundGradient(env.prefs[ backgroundGradient_prefs_key ] )
        self.gl_update()

    def setBackgroundColor(self, color): # bruce 050105 new feature [bruce 050117 cleaned it up]
        """
        Set the background color and store it in the prefs db.

        @param color: r,g,b tuple with values between 0.0-1.0
        @type  color: tuple with 3 floats
        """
        self.backgroundColor = color
        env.prefs[ backgroundColor_prefs_key ] = color
        self.setBackgroundGradient(0)
        return

    def getBackgroundColor(self):
        """
        Returns the current background color.

        @return color: r,g,b tuple with values between 0.0-1.0
        @rtype  color: tuple with 3 floats
        """
        return self.backgroundColor

    def setBackgroundGradient(self, gradient): # mark 050808 new feature
        """
        Stores the background gradient prefs value in the prefs db.
        gradient can be either:
            0 - No gradient. The background color is a solid color.
            1 - the background gradient is set to the 'Blue Sky' gradient.
            2 - the background gradient is set to the 'Evening Sky' gradient.
            3 - the background gradient is set to the  'Sea Green' gradient.

        See GLPane.standard_repaint_0() to see how this is used when redrawing the glpane.
        """
        self.backgroundGradient = gradient
        env.prefs[ backgroundGradient_prefs_key ] = gradient
        self._updateOriginAxisColor()
        self._updateSpecialContrastColors()
        return
    
    def _updateOriginAxisColor(self):
        """
        [private]
        Update the color of the origin axis to a shade that 
        will contrast well with the background.
        """
        env.prefs.restore_defaults([originAxisColor_prefs_key])
        axisColor = env.prefs[originAxisColor_prefs_key]
        gradient = env.prefs[ backgroundGradient_prefs_key ]
        
        if gradient == bgSOLID:
            if not colors_differ_sufficiently(self.backgroundColor, axisColor):
                env.prefs[originAxisColor_prefs_key] = ave_colors( 0.5, axisColor, white)
        elif gradient == bgEVENING_SKY:
            env.prefs[originAxisColor_prefs_key] = ave_colors( 0.9, axisColor, white)
        return
    
    def _updateSpecialContrastColors(self): # [probably by Mark, circa 080710]
        """
        [private]
        Update the special contrast colors (used to draw lines, etc.) to a 
        shade that contrasts well with the current background.
        @see: get_background_contrast_color()
        """
        # REVIEW: the following is only legitimate since these prefs variables
        # are (I think) not actual user prefs, but just global state variables.
        # However, if that's true, they should not really be stored in the
        # prefs db. Furthermore, if we had multiple GLPanes with different
        # background colors, I think these variables would need to be
        # per-glpane, so really they ought to be GLPane instance variables.
        # [bruce 080711 comment]
        env.prefs.restore_defaults([DarkBackgroundContrastColor_prefs_key,
                                    LightBackgroundContrastColor_prefs_key])
        dark_color = env.prefs[DarkBackgroundContrastColor_prefs_key]  # black
        lite_color = env.prefs[LightBackgroundContrastColor_prefs_key] # white
        gradient = env.prefs[ backgroundGradient_prefs_key ]
        
        if gradient == bgSOLID:
            if not colors_differ_sufficiently(self.backgroundColor, dark_color):
                env.prefs[DarkBackgroundContrastColor_prefs_key] = ave_colors( 0.5, dark_color, white)
            if not colors_differ_sufficiently(self.backgroundColor, lite_color):
                env.prefs[LightBackgroundContrastColor_prefs_key] = ave_colors( 0.5, lite_color, black)
        elif gradient == bgEVENING_SKY:
            env.prefs[DarkBackgroundContrastColor_prefs_key] = ave_colors( 0.6, dark_color, white)
        return
    
    def get_background_contrast_color(self):
        """
        Return a color that contrasts well with the background color of the 
        3D workspace (self). 
        @see: MultipleDnaSegmentResize_GraphicsMode where it is used for rendering 
        text with a proper contrast. 
        @see: self._updateSpecialContrastColors()
        """
        #NOTE: This method mitigates bug 2927
        
        dark_color = env.prefs[DarkBackgroundContrastColor_prefs_key]  # black
        ##lite_color = env.prefs[LightBackgroundContrastColor_prefs_key] # white
        gradient = env.prefs[ backgroundGradient_prefs_key ]
        
        color = black
                
        if gradient == bgSOLID:
            if not colors_differ_sufficiently(self.backgroundColor, dark_color):
                color = ave_colors( 0.5, dark_color, white)            
        elif gradient == bgEVENING_SKY:
            color = ave_colors( 0.6, dark_color, white)
            
        return color

    # ==

    def _set_widget_erase_color(self): # revised, bruce 071011
        """
        Change this widget's erase color (seen only if it's resized,
        and only briefly -- it's independent of OpenGL clearColor) to
        self.backgroundColor. This is intended to minimize the visual
        effect of widget resizes which temporarily show the erase
        color. See comments in this method for caveats about that.
        """
        # Note: this was called in GLPane.update_after_new_graphicsMode
        # when the graphicsMode could determine the background color,
        # but that's no longer true, so it could probably
        # just be called at startup and whenever the background color is changed.
        # Try that sometime, it might be an optim. For now it continues
        # to be called from there. [bruce 071011, still true 080910]
        #
        # REVIEW: what is self.backgroundColor when we're using the new default
        # of "Blue Sky Gradient". For best effect here, what it ought to be
        # is the average or central bg color in that gradient. I think it's not,
        # which makes me wonder if this bugfix is still needed at all. [bruce 071011]
        #
        # Note: calling this fixed the bug in which the glpane or its edges
        # flickered to black during a main-window resize. [bruce 050408]
        #
        # Note: limited this to Mac [in caller], since it turns out that bug (which has
        # no bug number yet) was Mac-specific, but this change caused a new bug 530
        # on Windows. (Not sure about Linux.) See also bug 141 (black during
        # mode-change), related but different. [bruce 050413]
        #
        # Note: for graphicsModes with a translucent surface covering the screen
        # (i.e. Build Atoms water surface), it would be better to blend that surface
        # color with self.backgroundColor for passing to this method, to approximate
        # the effective background color. Alternatively, we could change how those
        # graphicsModes set up OpenGL clearcolor, so that their empty space areas
        # looked like self.backgroundColor.) [bruce 050615 comment]

        bgcolor = self.backgroundColor
        r = int(bgcolor[0]*255 + 0.5) # (same formula as in elementSelector.py)
        g = int(bgcolor[1]*255 + 0.5)
        b = int(bgcolor[2]*255 + 0.5)
        pal = QPalette()
        pal.setColor(self.backgroundRole(), QColor(r, g, b))
        self.setPalette(pal)
            # see Qt docs for this and for backgroundRole
        return

    # ==
    
    def is_background_dark(self): #bruce 080910 de-inlined this
        _bgGradient_junk, darkQ = _backgroundGradient_params(
                    self.backgroundGradient,
                    self.backgroundColor
         )
        return darkQ

    def background_gradient_corner_colors(self): #bruce 080910 de-inlined this
        _bgGradient, darkQ_junk = _backgroundGradient_params(
                    self.backgroundGradient,
                    self.backgroundColor
         )
        return _bgGradient

    def _init_background_from_prefs(self): #bruce 080910 de-inlined this
        self.backgroundColor = env.prefs[backgroundColor_prefs_key]
        self.backgroundGradient = env.prefs[backgroundGradient_prefs_key]
        return

    # ==

    def clear_and_draw_background(self, other_glClear_buffer_bits): #bruce 080910 de-inlined this
        """
        @param other_glClear_buffer_bits: whichever of GL_DEPTH_BUFFER_BIT |
                                          GL_STENCIL_BUFFER_BIT you want to
                                          pass to glClear, in addition to
                                          GL_COLOR_BUFFER_BIT, which we
                                          pass if needed
        """
        c = self.backgroundColor
            # note: self.backgroundGradient and self.backgroundColor
            # are used and maintained entirely in this mixin class, as of 080910
            # (unless other files access them as public attrs -- not reviewed)

        glClearColor(c[0], c[1], c[2], 0.0)
        self.fogColor = (c[0], c[1], c[2], 1.0) # piotr 080515        
        del c

        glClear(GL_COLOR_BUFFER_BIT | other_glClear_buffer_bits )
            # potential optims:
            # - if stencil clear is expensive, we could do it only when needed [bruce ca. 050615]
            # - if color clear is expensive, we needn't do it when self.backgroundGradient 

        self.kluge_reset_texture_mode_to_work_around_renderText_bug()
        
        if self.backgroundGradient:
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            _bgGradient = self.background_gradient_corner_colors()

            drawFullWindow(_bgGradient)
            # fogColor is an average of the gradient components
            # piotr 080515
            self.fogColor = \
                (0.25 * (_bgGradient[0][0] + _bgGradient[1][0] + _bgGradient[2][0] + _bgGradient[3][0]), \
                 0.25 * (_bgGradient[0][1] + _bgGradient[1][1] + _bgGradient[2][1] + _bgGradient[3][1]), \
                 0.25 * (_bgGradient[0][2] + _bgGradient[1][2] + _bgGradient[2][2] + _bgGradient[3][2]))
            
            # Note: it would be possible to optimize by not clearing the color buffer
            # when we'll call drawFullWindow, if we first cleared depth buffer (or got
            # drawFullWindow to ignore it and effectively clear it by writing its own
            # depths into it everywhere, if that's possible). [bruce 070913 comment]

        return
    
    def draw_solid_color_everywhere(self, color): #bruce 090105, for debugging
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        try:
            drawFullWindow([color, color, color, color])
        finally:
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
        
        return
    
    def kluge_reset_texture_mode_to_work_around_renderText_bug(self):
        """
        This helps work around a renderText bug in Qt 4.3.x (fixed in Qt 4.4.0).
        It should be called after anything which might set GL_TEXTURE_ENV_MODE
        to something other than GL_MODULATE (e.g. after drawing an ESP Image,
        or textures used in testmode), and before drawing the main model
        or when initializing the graphics context.
        """
        #bruce 081205 made this a separate method, called it from more places.
        # for more info, see:
        #    http://trolltech.com/developer/task-tracker/index_html?method=entry&id=183995
        #    http://trolltech.com/developer/changes/changes-4.4.0 (issue 183995)
        #    http://www.nanoengineer-1.net/mediawiki/index.php?title=Qt_bugs_in_renderText#glTexEnvf_turns_all_renderText_characters_into_solid_rectangles
        # In theory this should no longer be needed once we upgrade to Qt 4.4.0.
        #
        # piotr 080620 - fixed "white text" bug when using Qt 4.3.x
        # [by doing this inline in clear_and_draw_background] --
        # before rendering text, the texture mode should be set to GL_MODULATE
        # to reflect current color changes.
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    pass

# end
