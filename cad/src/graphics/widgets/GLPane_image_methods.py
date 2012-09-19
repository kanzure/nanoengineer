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
from OpenGL.GL import GL_CURRENT_RASTER_POSITION
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_FALSE, GL_TRUE
from OpenGL.GL import GL_LIGHTING, GL_TEXTURE_2D
from OpenGL.GL import GL_RGB, GL_RED, GL_RGBA
from OpenGL.GL import GL_DEPTH_COMPONENT
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import GL_UNSIGNED_INT, GL_FLOAT
from OpenGL.GL import glColorMask
from OpenGL.GL import glDisable
from OpenGL.GL import glDrawPixels, glDrawPixelsub, glDrawPixelsf
from OpenGL.GL import glEnable
from OpenGL.GL import glGetBooleanv, glGetFloatv
from OpenGL.GL import glRasterPos3f
from OpenGL.GL import glReadPixels, glReadPixelsf

from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import glClear


from OpenGL.GLU import gluUnProject

from PyQt4.QtOpenGL import QGLWidget

import foundation.env as env

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice_boolean_False

from utilities.Comparison import same_vals

import sys

# ==

##_GL_TYPE_FOR_DEPTH = GL_UNSIGNED_INT
_GL_TYPE_FOR_DEPTH = GL_FLOAT # makes no difference - HL still fails

## _GL_FORMAT_FOR_COLOR = GL_RGB
_GL_FORMAT_FOR_COLOR = GL_RGBA # this probably removes the crashes & visual errors for most width values

# ==

def _trim(width):
    """
    Reduce a width or height (in pixels) to a safe value (e.g. 0 mod 16).

    (This would not be needed if GL functions for images were used properly
    and had no bugs.)
    """
    return width # this seems to work when _GL_FORMAT_FOR_COLOR = GL_RGBA,
        # whereas this was needed when it was GL_RGB:
        ## # this fixed the C crash on resizing the main window
        ## # (which happened from increasing width, then redraw)
        ## return width - width % 16

# ==

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
        gl_format, gl_type = _GL_FORMAT_FOR_COLOR, GL_UNSIGNED_BYTE
            # these (but with GL_RGB) seem to be enough;
            # GL_RGBA, GL_FLOAT also work but look the same
        image = glReadPixels( width - subwidth,
                              height - subheight,
                              subwidth, subheight,
                              gl_format, gl_type )
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
                self._set_raster_pos(x, y)
                glDisable(GL_DEPTH_TEST) # otherwise it can be obscured by prior drawing into depth buffer
                # Note: doing more disables would speed up glDrawPixels,
                # but that doesn't matter unless we do it many times per frame.
                glDrawPixels(subwidth, subheight, gl_format, gl_type, image)
                glEnable(GL_DEPTH_TEST)
            pass
        return

    def _set_raster_pos(x, y): # staticmethod
        """
        """
        # If x or y is exactly 0, then numerical roundoff errors can make the raster position invalid.
        # Using 0.1 instead apparently fixes it, and causes no noticable image quality effect.
        # (Presumably they get rounded to integer window positions after the view volume clipping,
        #  though some effects I saw implied that they don't get rounded, so maybe 0.1 is close enough to 0.0.)
        # This only matters when GLPane size is 100x100 or less,
        # or when drawing this in lower left corner for debugging,
        # so we don't have to worry about whether it's perfect.
        # (The known perfect fix is to initialize both matrices, but we don't want to bother,
        #  or to worry about exceeding the projection matrix stack depth.)
        x1 = max(x, 0.1)
        y1 = max(y, 0.1)

        depth = 0.1 # this should not matter, as long as it's within the viewing volume
        x1, y1, z1 = gluUnProject(x1, y1, depth)
        glRasterPos3f(x1, y1, z1) # z1 does matter (when in perspective view), since this is a 3d position
            # Note: using glWindowPos would be simpler and better, but it's not defined
            # by the PyOpenGL I'm using. [bruce iMac G5 070626]
            ### UPDATE [bruce 081203]: glWindowPos2i *is* defined, at least on my newer Mac.
            # There are lots of variants, all suffix-typed with [23][dfis]{,v}.
            # I need to check whether it's defined on the older Macs too, then use it here. ####FIX

        if not glGetBooleanv(GL_CURRENT_RASTER_POSITION_VALID):
            # This was happening when we used x, y = exact 0,
            # and was causing the image to not get drawn sometimes (when mousewheel zoom was used).
            # It can still happen for extreme values of mousewheel zoom (close to the ones
            # which cause OpenGL exceptions), mostly only when pos = (0, 0) but not entirely.
            # Sometimes the actual drawing positions can get messed up then, too.
            # This doesn't matter much, but indicates that re-initing the matrices would be
            # a better solution if we could be sure the projection stack depth was sufficient
            # (or if we reset the standard projection when done, rather than using push/pop).
            print "bug: not glGetBooleanv(GL_CURRENT_RASTER_POSITION_VALID); pos =", x, y
                # if this happens, the subsequent effect is that glDrawPixels draws nothing
        else:
            # verify correct raster position
            px, py, pz, pw = glGetFloatv(GL_CURRENT_RASTER_POSITION)
            if not (0 <= px - x < 0.4) and (0 <= py - y < 0.4): # change to -0.4 < px - x ??
                print "LIKELY BUG: glGetFloatv(GL_CURRENT_RASTER_POSITION) = %s" % [px, py, pz, pw]
                # seems to be in window coord space, but with float values,
                # roughly [0.1, 0.1, 0.1, 1.0] but depends on viewpoint, error about 10**-5
            pass

        return
    _set_raster_pos = staticmethod(_set_raster_pos)

    # ==

    # known bugs with cached bg image [as of 080922 morn]:
    # - some update bugs listed below
    # - drawaxes (origin axes) end up as dotted line; fix: exclude them from bg image (in basicGM.draw())
    # - other special drawing in basicGM.draw
    # - Build Atoms region sel rubberband is not visible
    # - preventing crashes or visual image format errors required various kluges, incl _trim
    # - highlight is not working

    def _get_bg_image_comparison_data(self):
        """
        """
        data = (
            self.graphicsMode,
                # often too conservative, but not always
                # bug: some graphicsModes use prefs or PM settings to decide
                # how much of the model to display; this ignores those
                # bug: some GMs do extra drawing in .Draw; this ignores prefs etc that affect that
            self._fog_test_enable,
            self.displayMode, # display style
            self.part,
            self.part.assy.all_change_indicators(), # TODO: fix view change indicator for this to work fully
                # note: that's too conservative, since it notices changes in other parts (e.g. from Copy Selection)

            # KLUGE until view change indicator is fixed -- include view data
            # directly; should be ok indefinitely
            + self.quat, # this hit a bug in same_vals (C version), fixed by Eric M 080922 in samevalshelp.c rev 14311
            ## + self.quat.vec, # workaround for that bug (works)
            + self.pov, self.scale, self.zoomFactor,

            self.width,
            self.height,
            QGLWidget.width(self), # in case it disagrees with self.width
            QGLWidget.height(self),
            self._resize_counter, # redundant way to force new grab after resize
                # (tho it might be safer to completely disable the feature
                #  for a frame, after resize ### TRYIT)
            self.ortho,
           )
        return data

    _cached_bg_color_image = None
    _cached_bg_depth_image = None

    def _print_data(self):
        return "%d; %d %d == %#x %#x" % \
               (env.redraw_counter,
                self.width, self.height,
                self.width, self.height,)

    def _capture_saved_bg_image(self):
        """
        """
        # TODO: investigate better ways to do this, which don't involve the CPU.
        # For example, frame buffer objects, or "render to texture":
        # - by glCopyTexImage2D,
        #   http://nehe.gamedev.net/data/lessons/lesson.asp?lesson=36
        #   (which can do color -- I don't know about depth),
        # - or by more platform-specific ways, e.g. pbuffer.
        # [bruce 081002]

        print "_capture_saved_bg_image", self._print_data()
        sys.stdout.flush()

        if 1:
            from OpenGL.GL import glFlush, glFinish
            glFlush() # might well be needed, based on other code in NE1; not enough by itself
            glFinish() # try this too if needed
        w = _trim(self.width)
        h = _trim(self.height)

        # grab the color image part
        image = glReadPixels( 0, 0, w, h, _GL_FORMAT_FOR_COLOR, GL_UNSIGNED_BYTE )
        self._cached_bg_color_image = image

        # grab the depth part
        ## image = glReadPixels( 0, 0, w, h, GL_DEPTH_COMPONENT, _GL_TYPE_FOR_DEPTH )
        image = glReadPixelsf(0, 0, w, h, GL_DEPTH_COMPONENT) #####
        self._cached_bg_depth_image = image
        print "grabbed depth at 0,0:", image[0][0]######

        return

    def _draw_saved_bg_image(self):
        """
        """
        print "_draw_saved_bg_image", self._print_data()
        sys.stdout.flush()

        assert self._cached_bg_color_image is not None

        w = _trim(self.width)
        h = _trim(self.height)

        glDisable(GL_DEPTH_TEST) # probably a speedup
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D) # probably already the NE1 default (if so, doesn't matter here)
            # Note: doing more disables might well speed up glDrawPixels;
            # don't know whether that matters.

        color_image = self._cached_bg_color_image
        depth_image = self._cached_bg_depth_image

        # draw the color image part (review: does this also modify the depth buffer?)
        self._set_raster_pos(0, 0)
        if 0 and 'kluge - draw depth as color':
            glDrawPixels(w, h, GL_RED, _GL_TYPE_FOR_DEPTH, depth_image)
        else:
            glDrawPixels(w, h, _GL_FORMAT_FOR_COLOR, GL_UNSIGNED_BYTE, color_image)

        # draw the depth image part; ###BUG: this seems to replace all colors with blue... fixed below
        self._set_raster_pos(0, 0) # adding this makes the all-gray bug slightly less bad

        glClear(GL_DEPTH_BUFFER_BIT) # should not matter, but see whether it does #####

        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE) # don't draw color pixels -
            # fixes bug where this glDrawPixels replaced all colors with blue
            # (reference doc for glDrawPixels explains why - it makes fragments
            #  using current color and depths from image, draws them normally)
        print "depth_image[0][0] being written now:", depth_image[0][0] #####
            ## depth_image[0][0] being written now: 0.0632854178548

        ## glDrawPixels(w, h, GL_DEPTH_COMPONENT, _GL_TYPE_FOR_DEPTH, depth_image)
        # see if this works any better -- not sure which type to try:
        # types listed at http://pyopengl.sourceforge.net/documentation/ref/gl/drawpixels.html
        ## print glDrawPixels.__class__ ####
        glDrawPixelsf(GL_DEPTH_COMPONENT, depth_image) ## if it was PIL, could say .tostring("raw","R",0,-1))######

        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        if 1:####
            from OpenGL.GL import glFlush
            glFlush()######
        self._set_raster_pos(0, 0) # precaution (untested)

        if 1: # confirm if possible
            print "readback of depth at 0,0:", glReadPixels( 0, 0, 1, 1, GL_DEPTH_COMPONENT, _GL_TYPE_FOR_DEPTH )[0][0] ######
                ## BUG: readback of depth at 0,0: 1.0
##            import Numeric
##            print "min depth:" , Numeric.minimum( glReadPixels( 0, 0, w, h, GL_DEPTH_COMPONENT, _GL_TYPE_FOR_DEPTH ) ) #### 6 args required
##            ## ValueError: invalid number of arguments
            print

        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        # (but leave GL_TEXTURE_2D disabled)

        return

    pass

# end
