# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_image_methods.py

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 070626 wrote some of these in GLPane.py

bruce 080919 split this into its own file, added new methods & calling code
"""

from OpenGL.GL import GL_CURRENT_RASTER_POSITION_VALID
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_RGB
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import glDisable
from OpenGL.GL import glDrawPixels
from OpenGL.GL import glEnable
from OpenGL.GL import glGetBooleanv
from OpenGL.GL import glRasterPos3f
from OpenGL.GL import glReadPixels

from OpenGL.GLU import gluUnProject

import foundation.env as env

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice_boolean_False

class GLPane_image_methods(object):
    """
    Private mixin superclass to provide image capture/redraw support
    (and to use it in specific ways) for class GLPane_rendering_methods.
    """
    
    _conf_corner_bg_image_data = None

    def _draw_cc_test_images(self):
        """
        draw some test images related to the confirmation corner (if desired)
        """
        ccdp1 = debug_pref("Conf corner test: redraw at lower left",
                           Choice_boolean_False,
                           prefs_key = True)
        ccdp2 = debug_pref("Conf corner test: redraw in-place",
                           Choice_boolean_False,
                           prefs_key = True)
        
        if ccdp1 or ccdp2:
            self.grab_conf_corner_bg_image() #bruce 070626 (needs to be done before draw_overlay in caller)

        if ccdp1:
            self.draw_conf_corner_bg_image((0, 0))

        if ccdp2:
            self.draw_conf_corner_bg_image()

    def grab_conf_corner_bg_image(self): #bruce 070626
        """
        Grab an image of the top right corner, for use in confirmation corner
        optimizations which redraw it without redrawing everything.
        """
        width = self.width
        height = self.height
        subwidth = min(width, 100)
        subheight = min(height, 100)
        gl_format, gl_type = GL_RGB, GL_UNSIGNED_BYTE
            # these seem to be enough; GL_RGBA, GL_FLOAT also work but look the same
        image = glReadPixels( width - subwidth,
                              height - subheight,
                              subwidth, subheight,
                              gl_format, gl_type )
        if type(image) is not type("") and \
           not env.seen_before("conf_corner_bg_image of unexpected type"):
            print "fyi: grabbed conf_corner_bg_image of unexpected type %r:" % \
                  ( type(image), )

        self._conf_corner_bg_image_data = (subwidth, subheight,
                                           width, height,
                                           gl_format, gl_type, image)

            # Note: the following alternative form probably grabs a Numeric array, but I'm not sure
            # our current PyOpenGL (in release builds) supports those, so for now I'll stick with strings, as above.
            ## image2 = glReadPixelsf( width - subwidth, height - subheight, subwidth, subheight, GL_RGB)
            ## print "grabbed image2 (type %r):" % ( type(image2), ) # <type 'array'>

        return

    def draw_conf_corner_bg_image(self, pos = None): #bruce 070626 (pos argument is just for development & debugging)
        """
        Redraw the previously grabbed conf_corner_bg_image,
        in the same place from which it was grabbed,
        or in the specified place (lower left corner of pos, in OpenGL window coords).
        Note: this modifies the OpenGL raster position.
        """
        if not self._conf_corner_bg_image_data:
            print "self._conf_corner_bg_image_data not yet assigned"
        else:
            subwidth, subheight, width, height, gl_format, gl_type, image = self._conf_corner_bg_image_data
            if width != self.width or height != self.height:
                # I don't know if this can ever happen; if it can, caller might need
                # to detect this itself and do a full redraw.
                # (Or we might make this method return a boolean to indicate it.)
                print "can't draw self._conf_corner_bg_image_data -- glpane got resized" ###
            else:
                if pos is None:
                    pos = (width - subwidth, height - subheight)
                x, y = pos

                # If x or y is exactly 0, then numerical roundoff errors can make the raster position invalid.
                # Using 0.1 instead apparently fixes it, and causes no noticable image quality effect.
                # (Presumably they get rounded to integer window positions after the view volume clipping,
                #  though some effects I saw implied that they don't get rounded, so maybe 0.1 is close enough to 0.0.)
                # This only matters when GLPane size is 100x100 or less,
                # or when drawing this in lower left corner for debugging,
                # so we don't have to worry about whether it's perfect.
                # (The known perfect fix is to initialize both matrices, but we don't want to bother,
                #  or to worry about exceeding the projection matrix stack depth.)
                x = max(x, 0.1)
                y = max(y, 0.1)

                depth = 0.1 # this should not matter, as long as it's within the viewing volume
                x1, y1, z1 = gluUnProject(x, y, depth)
                glRasterPos3f(x1, y1, z1) # z1 does matter (when in perspective view), since this is a 3d position
                    # Note: using glWindowPos would be simpler and better, but it's not defined
                    # by the PyOpenGL I'm using. [bruce iMac G5 070626]

                if not glGetBooleanv(GL_CURRENT_RASTER_POSITION_VALID):
                    # This was happening when we used x, y = exact 0,
                    # and was causing the image to not get drawn sometimes (when mousewheel zoom was used).
                    # It can still happen for extreme values of mousewheel zoom (close to the ones
                    # which cause OpenGL exceptions), mostly only when pos = (0, 0) but not entirely.
                    # Sometimes the actual drawing positions can get messed up then, too.
                    # This doesn't matter much, but indicates that reiniting the matrices would be
                    # a better solution if we could be sure the projection stack depth was sufficient
                    # (or if we reset the standard projection when done, rather than using push/pop).
                    print "bug: not glGetBooleanv(GL_CURRENT_RASTER_POSITION_VALID); pos =", pos

                glDisable(GL_DEPTH_TEST) # otherwise it can be obscured by prior drawing into depth buffer
                # Note: doing more disables would speed up glDrawPixels,
                # but that doesn't matter unless we do it many times per frame.
                glDrawPixels(subwidth, subheight, gl_format, gl_type, image)
                glEnable(GL_DEPTH_TEST)
            pass
        return

    # ==
    
    def _get_bg_image_comparison_data(self):
        """
        """
        data = (
            self.graphicsMode,
                # often too conservative, but not always
                # bug: some graphicsModes use prefs or PM settings to decide
                # how much of the model to display; this ignores those
                # bug: some GMs do extra drawing in .Draw; this ignores prefs etc that affect that
            self._fog_enabled, #sp?
            self.display, # display style (sp? #k)
            self.part,
            self.part.assy.all_change_indicators(), # TODO: fix view change indicator for this to work fully
                # note: that's too conservative, since it notices changes in other parts (e.g. from Copy Selection)
            self.quat, self.pov, self.scale, self.zoomFactor, # KLUGE until that's done -- should be enough for now
            self.width,
            self.height,
           )
        return data

    def _draw_saved_bg_image(self):
        print "nim: _draw_saved_bg_image"

    def _capture_saved_bg_image(self):
        print "nim: _capture_saved_bg_image"

    pass

# end
