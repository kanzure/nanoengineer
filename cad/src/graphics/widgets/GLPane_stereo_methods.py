# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_stereo_methods.py

@author: Piotr
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:

piotr 080515 and 080529 wrote these in GLPane.py

bruce 080912 split this into its own file
"""

import foundation.env as env

from utilities.prefs_constants import stereoViewMode_prefs_key
from utilities.prefs_constants import stereoViewSeparation_prefs_key
from utilities.prefs_constants import stereoViewAngle_prefs_key

from OpenGL.GL import GL_CLIP_PLANE5
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_TRANSFORM_BIT
from OpenGL.GL import GL_TRUE
from OpenGL.GL import glClear
from OpenGL.GL import glClipPlane
from OpenGL.GL import glColorMask
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glPopAttrib
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushAttrib
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glRotatef
from OpenGL.GL import glTranslatef


class GLPane_stereo_methods(object):
    """
    Private mixin superclass to provide stereo rendering support to class GLPane.
    The main class needs to call these methods at appropriate times
    and use some attributes we maintain in appropriate ways.
    For documentation see the method docstrings and code comments.
    
    All our attribute names and method names contain the string 'stereo',
    making them easy to find by text-searching the main class source code.
    """

    # note: instance variable default values are class assignments
    # in the main class, of stereo_enabled and a few other attrs.
    
    def set_stereo_enabled(self, enabled): #bruce 080911
        """
        Set whether stereo will be enabled during the next draw
        (and subsequent draws until this is set again).

        @note: this should only be called between draws. If it's called by
               Qt event handlers, that should guarantee this, since they
               are atomic with respect to paintGL and paintGL never does
               recursive event processing.
        """
        # future: if this could be called during paintGL, then we'd
        # need to reimplement it so that instead of setting self.stereo_enabled
        # directly, we'd set another attr which would be copied into it when
        # we call _update_stereo_settings at the start of the next paintGL.
        self.stereo_enabled = enabled
        if self.stereo_enabled:
            # have two images for the stereo rendering.
            # In some stereo_modes these are clipped left and right images;
            # in others they are drawn overlapping with different colormasks.
            # This is set up as needed by passing these values (as stereo_image)
            # to self._enable_stereo.
            self.stereo_images_to_draw = (-1, 1)
        else:
            # draw only once if stereo is disabled
            self.stereo_images_to_draw = (0,)
        return

    def stereo_image_hit_by_event(self, event): #bruce 080912 split this out
        """
        return a value for caller to store into self.current_stereo_image
        to indicate which stereo image the mouse press event was in:
        0 means stereo is disabled, or the two stereo images overlap
        (as opposed to being a left/right pair -- this is determined
         by self.stereo_mode)
        -1 means the left image (of a left/right pair) was clicked on
        +1 means the right image was clicked on
        """
        # piotr 080529 wrote this in GLPane
        current_stereo_image = 0
        if self.stereo_enabled:
            # if in side-by-side stereo
            if self.stereo_mode == 1 or \
               self.stereo_mode == 2:
                # find out which stereo image was clicked in
                if event.x() < self.width / 2:
                    current_stereo_image = -1
                else:
                    current_stereo_image = 1
        return current_stereo_image
    
    # stereo rendering methods [piotr 080515 added these, and their calling code]

    def _enable_stereo(self, stereo_image, preserve_colors = False, no_clipping = False):
        """
        Enables stereo rendering.        

        This should be called before entering a drawing phase
        and should be accompanied by a self._disable_stereo call
        after the drawing for that phase.
        
        These methods push a modelview matrix on the matrix stack
        and modify the matrix.

        @param stereo_image: Indicates which stereo image is being drawn
                             (-1 == left, 1 == right, 0 == stereo is disabled)
        
        @param preserve_colors: Disable color mask manipulations,
                                which normally occur in anaglyph mode.
                                (Also disable depth buffer clearing
                                 for 2nd image, which occurs then.)

        @param no_clipping: Disable clipping, which normally occurs in
                            side-by-side mode.
        """
        if not self.stereo_enabled:
            return

        glPushAttrib(GL_TRANSFORM_BIT)

        stereo_mode = self.stereo_mode
        stereo_separation = self.stereo_separation
        stereo_angle = self.stereo_angle

        # push the modelview matrix on the stack
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        separation = stereo_separation * self.scale
        angle = stereo_angle # might be modified below

        if stereo_mode <= 2:
            # side-by-side stereo mode
            # clip left or right image 
            # reset the modelview matrix

            if not no_clipping:
                glPushMatrix() # Note: this might look redundant with the
                    # glPushMatrix above, but removing it (and its glPopMatrix
                    # 10 lines below) causes a bug (no image visible).
                    # Guess: it's needed so the glLoadIdentity needed to set up
                    # the clipping plane just below has only a temporary effect.
                    # [bruce 080911 comment]
                glLoadIdentity()
                if stereo_image == -1:
                    clip_eq = (-1.0, 0.0, 0.0, 0.0)
                else:
                    clip_eq = ( 1.0, 0.0, 0.0, 0.0)
                # using GL_CLIP_PLANE5 for stereo clipping 
                glClipPlane(GL_CLIP_PLANE5, clip_eq)
                glEnable(GL_CLIP_PLANE5)
                glPopMatrix()

            # for cross-eyed mode, exchange left and right views
            if stereo_mode == 2:
                angle *= -1

            # translate images for side-by-side stereo
            glTranslatef(separation * stereo_image * self.right[0], 
                         separation * stereo_image * self.right[1], 
                         separation * stereo_image * self.right[2])

            # rotate the stereo image ("toe-in" method)
            glRotatef(angle * stereo_image,
                      self.up[0], 
                      self.up[1],
                      self.up[2])

        else:
            # Anaglyphs stereo mode - Red plus Blue, Cyan, or Green image.
            angle *= 0.5
            if not preserve_colors:
                if stereo_image == -1:
                    # red image
                    glColorMask(GL_TRUE, GL_FALSE, GL_FALSE, GL_TRUE)
                else:
                    # clear depth buffer to combine red/blue images
                    # REVIEW: this would cause bugs in the predraw_glselectdict code
                    # used for depth-testing selobj candidates. Maybe it does
                    # not happen then? The name of the flag 'preserve_colors'
                    # does not say anything about preserving depths.
                    # Anyway, it *does* happen then, so I think there is a bug.
                    # Also, remind me, what's the 4th arg to glColorMask?
                    # [bruce 080911 comment]
                    #
                    # piotr 080911 response: You are right. This technically
                    # causes a bug: the red image is not highlightable,
                    # but actually when using anaglyph glasses, the bug is not
                    # noticeable, as both red and blue images converge. 
                    # The bug becomes noticeable if user tries to highlight an
                    # object without wearing the anaglyph glasses.  
                    # At this point, I think we can either leave it as it is,
                    # or consider implementing anaglyph stereo by using 
                    # OpenGL alpha blending. 
                    # Also, I am not sure if highlighting problem is the only bug
                    # that is caused by clearing the GL_DEPTH_BUFFER_BIT.
                    glClear(GL_DEPTH_BUFFER_BIT)
                    if stereo_mode == 3:
                        # blue image
                        glColorMask(GL_FALSE, GL_FALSE, GL_TRUE, GL_TRUE)
                    elif stereo_mode == 4:
                        # cyan image
                        glColorMask(GL_FALSE, GL_TRUE, GL_TRUE, GL_TRUE)
                    elif stereo_mode == 5:
                        # green image
                        glColorMask(GL_FALSE, GL_TRUE, GL_FALSE, GL_TRUE)

            # rotate the stereo image ("toe-in" method)
            glRotatef(angle * stereo_image,
                      self.up[0], 
                      self.up[1],
                      self.up[2])
        return

    def _disable_stereo(self):
        """
        Disables stereo rendering.
        This method pops a modelview matrix from the matrix stack.
        """
        if not self.stereo_enabled:
            return
        
        if self.stereo_mode <= 2:
            # side-by-side stereo mode
            # make sure that the clipping plane is disabled
            glDisable(GL_CLIP_PLANE5)
        else: 
            # anaglyphs stereo mode
            # enable all colors
            glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE) 

        # restore the matrix
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glPopAttrib()

        return

    def _update_stereo_settings(self): #bruce 080911 (bugfix, see docstring)
        """
        set self.stereo_* attributes (mode, separation, angle)
        based on current user prefs values
        
        @note: this should be called just once per draw event, before
               anything might use these attributes, to make sure
               these settings remain constant throughout that event (perhaps not
               an issue since event handlers are atomic), and to ensure they remain
               correct relative to what was drawn in subsequent calls of
               mousePressEvent or mousepoints (necessary in case intervening
               user events modified the prefs values)
        """
        if self.stereo_enabled:
            # this code (by Piotr) must be kept in synch with the code
            # which sets the values of these prefs (in another module)
            self.stereo_mode = env.prefs[stereoViewMode_prefs_key]
            self.stereo_separation = 0.01 * env.prefs[stereoViewSeparation_prefs_key]
            self.stereo_angle = -0.1 * (env.prefs[stereoViewAngle_prefs_key] - 25)
        return

    pass

# end

