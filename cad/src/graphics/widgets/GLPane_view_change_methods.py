# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_view_change_methods.py

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

I think Mark wrote most or all of these, in GLPane.py.

bruce 080912 split this out of class GLPane
"""

import time
import math

from Numeric import dot
from geometry.VQT import V, Q, norm, vlen

import foundation.env as env
from utilities.Log import orangemsg
from utilities.debug import print_compact_traceback

from utilities.prefs_constants import animateStandardViews_prefs_key
from utilities.prefs_constants import animateMaximumTime_prefs_key

MIN_REPAINT_TIME = 0.01 # minimum time to repaint (in seconds)

# ==

def typecheckViewArgs(q2, s2, p2, z2): #mark 060128
    """
    Typecheck the view arguments quat q2, scale s2, pov p2, and zoom factor z2
    used by GLPane.snapToView() and GLPane.animateToView().
    """
    assert isinstance(q2, Q)
    assert isinstance(s2, float)
    assert len(p2) == 3
    assert isinstance(p2[0], float)
    assert isinstance(p2[1], float)
    assert isinstance(p2[2], float)
    assert isinstance(z2, float)
    return

# ==

class GLPane_view_change_methods(object):
    """
    Private mixin superclass to provide view change methods to class GLPane,
    including view change animation methods, and some slot methods
    or direct submethods of those.

    @see: ops_view.py, which has UI slot methods that call some of these methods
    """
    # note: is_animating is visible as a public attr of the main class
    is_animating = False # mark 060404
        # Set to True while animating between views in animateToView()
        # so that update_selobj() in selectAtoms_GraphicsMode will not
        # hover highlight objects under the cursor during that time.

    _repaint_duration = MIN_REPAINT_TIME

    # == view toolbar helper methods

    # [bruce 050418 made these from corresponding methods in MWsemantics.py,
    #  which still exist but call these, perhaps after printing a history message.
    #  Also revised them for assembly/part split, i.e. per-part namedView attributes.]

    def setViewHome(self):
        """
        Change view to our model's home view (for glpane's current part).
        """
        self.animateToNamedView( self.part.homeView)

    def setViewFitToWindow(self, fast = False):
        """
        Change view so that the visible part of the entire model
        fits in the glpane.
        If <fast> is True, then snap to the view (i.e. don't animate).
        """
        # Recalculate center and bounding box for all the visible chunks in the current part.
        # The way a 3d bounding box is used to calculate the fit is not adequate. I consider this a bug, but I'm not sure
        # how to best use the BBox object to compute the proper fit. Should ask Bruce. This will do for now. Mark 060713.

        # BUG: only chunks are considered. See comment in bbox_for_viewing_model.
        # [bruce 070919 comment]

        bbox = self.assy.bbox_for_viewing_model()

        center, scale = self.center_and_scale_from_bbox( bbox, klugefactor = 0.75 )

        pov = V(-center[0], -center[1], -center[2])
        if fast:
            self.snapToView(self.quat, scale, pov, 1.0)
        else:
            self.animateToView(self.quat, scale, pov, 1.0)

    def setViewZoomToSelection(self, fast = False): #Ninad 60903
        """
        Change the view so that only selected atoms, chunks and Jigs fit in the GLPane. 
        (i.e. Zoom to the selection) If <fast> is True, then snap to the view
        """
        #ninad060905: 
        #This considers only selected atoms, movable jigs and chunks while doing fit to window. 
        #Zoom to selection ignores other immovable jigs. (it clearly tells this in a history msg)
        # For future:  Should work when a non movable jig is selected
        #Bugs due to use of Bbox remain as in fit to window.

        bbox = self.assy.bbox_for_viewing_selection()

        if bbox is None:
            env.history.message( orangemsg(
                " Zoom To Selection: No visible atoms , chunks or movable jigs selected" \
                " [Acceptable Jigs: Motors, Grid Plane and ESP Image]" ))
            # KLUGE: the proper content of this message depends on the behavior
            # of bbox_for_viewing_selection, which should be extended to cover more
            # kinds of objects.
            return

        center, scale = self.center_and_scale_from_bbox( bbox, klugefactor = 0.85 )
            #ninad060905 experimenting with the scale factor
            # [which was renamed to klugefactor after this comment was written].
            # I see no change with various values!

        pov = V(-center[0], -center[1], -center[2])
        if fast:
            self.snapToView(self.quat, scale, pov, 1.0)
        else:
            self.animateToView(self.quat, scale, pov, 1.0)
        return

    def setViewHomeToCurrent(self):
        """
        Set the Home view to the current view.
        """
        self.part.homeView.setToCurrentView(self)
        self.part.changed() # Mark [041215]

    def setViewRecenter(self, fast = False):
        """
        Recenter the current view around the origin of modeling space.
        """
        print "**in setViewRecenter"
        part = self.part
        part.computeBoundingBox()
        scale = (part.bbox.scale() * 0.75) + (vlen(part.center) * .5)
            # regarding the 0.75, it has the same role as the klugefactor
            # option of self.center_and_scale_from_bbox(). [bruce comment 070919]
        aspect = self.aspect
        if aspect < 1.0:
            scale /= aspect
        pov = V(0, 0, 0) 
        if fast:
            self.snapToView(self.quat, scale, pov, 1.0)
        else:
            self.animateToView(self.quat, scale, pov, 1.0)

    def setViewProjection(self, projection): # Added by Mark 050918.
        """
        Set projection, where 0 = Perspective and 1 = Orthographic.  It does not set the 
        prefs db value itself, since we don't want all user changes to projection to be stored
        in the prefs db, only the ones done from the Preferences dialog.
        """
        # Set the checkmark for the Ortho/Perspective menu item in the View menu.  
        # This needs to be done before comparing the value of self.ortho to projection
        # because self.ortho and the toggle state of the corresponding action may 
        # not be in sync at startup time. This fixes bug #996.
        # Mark 050924.

        if projection:
            self.win.setViewOrthoAction.setChecked(1)
        else:
            self.win.setViewPerspecAction.setChecked(1)

        if self.ortho == projection:
            return

        self.ortho = projection
        self.gl_update()

    def snapToNamedView(self, namedView):
        """
        Snap to the destination view L{namedView}.

        @param namedView: The view to snap to.
        @type  namedView: L{NamedView}
        """
        self.snapToView(namedView.quat, 
                        namedView.scale, 
                        namedView.pov, 
                        namedView.zoomFactor)

    def animateToNamedView(self, namedView, animate = True):
        """
        Animate to the destination view I{namedView}.

        @param namedView: The view to snap to.
        @type  namedView: L{NamedView}

        @param animate: If True, animate between views. If False, snap to
                        I{namedView}. If the user pref "Animate between views"
                        is unchecked, then this argument is ignored. 
        @type  animate: boolean
        """
        # Determine whether to snap (don't animate) to the destination view.
        if not animate or not env.prefs[animateStandardViews_prefs_key]:
            self.snapToNamedView(namedView)
            return
        self.animateToView(namedView.quat, 
                           namedView.scale, 
                           namedView.pov, 
                           namedView.zoomFactor, 
                           animate)
        return

    def snapToView(self, q2, s2, p2, z2, update_duration = False):
        """
        Snap to the destination view defined by
        quat q2, scale s2, pov p2, and zoom factor z2.
        """
        # Caller could easily pass these args in the wrong order.  Let's typecheck them.
        typecheckViewArgs(q2, s2, p2, z2)

        self.quat = Q(q2)
        self.pov = V(p2[0], p2[1], p2[2])
        self.zoomFactor = z2
        self.scale = s2

        if update_duration:
            self.gl_update_duration()
        else:
            self.gl_update()

    def rotateView(self, q2): 
        """
        Rotate current view to quat (viewpoint) q2
        """
        self.animateToView(q2, self.scale, self.pov, self.zoomFactor, animate = True)
        return

    # animateToView() uses "Normalized Linear Interpolation" 
    # and not "Spherical Linear Interpolation" (AKA slerp), 
    # which traces the same path as slerp but works much faster.
    # The advantages to this approach are explained in detail here:
    # http://number-none.com/product/Hacking%20Quaternions/
    def animateToView(self, q2, s2, p2, z2, animate = True):
        """
        Animate from the current view to the destination view defined by
        quat q2, scale s2, pov p2, and zoom factor z2.
        If animate is False *or* the user pref "Animate between views" is not selected, 
        then do not animate;  just snap to the destination view.
        """
        # Caller could easily pass these args in the wrong order.  Let's typecheck them.
        typecheckViewArgs(q2, s2, p2, z2)

        # Precaution. Don't animate if we're currently animating.
        if self.is_animating:
            return

        # Determine whether to snap (don't animate) to the destination view.
        if not animate or not env.prefs[animateStandardViews_prefs_key]:
            self.snapToView(q2, s2, p2, z2)
            return

        # Make copies of the current view parameters.
        q1 = Q(self.quat)
        s1 = self.scale
        p1 = V(self.pov[0], self.pov[1], self.pov[2])
        z1 = self.zoomFactor

        # Compute the normal vector for current and destination view rotation.
        wxyz1 = V(q1.w, q1.x, q1.y, q1.z)
        wxyz2 = V(q2.w, q2.x, q2.y, q2.z)

        # The rotation path may turn either the "short way" (less than 180) or the "long way" (more than 180).
        # Long paths can be prevented by negating one end (if the dot product is negative).
        if dot(wxyz1, wxyz2) < 0: 
            wxyz2 = V(-q2.w, -q2.x, -q2.y, -q2.z)

        # Compute the maximum number of frames for the maximum possible 
        # rotation (180 degrees) based on how long it takes to repaint one frame.
        self.gl_update_duration()
        max_frames = max(1, env.prefs[animateMaximumTime_prefs_key]/self._repaint_duration)

        # Compute the deltas for the quat, pov, scale and zoomFactor.
        deltaq = q2 - q1
        deltap = vlen(p2 - p1)
        deltas = abs(s2 - s1)
        deltaz = abs(z2 - z1)

        # Do nothing if there is no change b/w the current view to the new view.
        # Fixes bugs 1350 and 1170. mark 060124.
        if deltaq.angle + deltap + deltas + deltaz == 0: # deltaq.angle is always positive.
            return

        # Compute the rotation angle (in degrees) b/w the current and destination view.
        rot_angle = deltaq.angle * 180/math.pi # rotation delta (in degrees)
        if rot_angle > 180:
            rot_angle = 360 - rot_angle # go the short way

        # For each delta, compute the total number of frames each would 
        # require (by itself) for the animation sequence.
        ### REVIEW: LIKELY BUG: integer division in rot_angle/180 [bruce 080912 comment]
        rot_frames = int(rot_angle/180 * max_frames)
        pov_frames = int(deltap * .2) # .2 based on guess/testing. mark 060123
        scale_frames = int(deltas * .05) # .05 based on guess/testing. mark 060123
        zoom_frames = int(deltaz * .05) # Not tested. mark 060123

        # Using the data above, this formula computes the ideal number of frames
        # to use for the animation loop.  It attempts to keep animation speeds consistent.
        total_frames = int(
            min(max_frames,
                max(3, rot_frames, pov_frames, scale_frames, zoom_frames)))

        ##print "total_frames =", total_frames

        # Compute the increments for each view parameter to use in the animation loop.
        rot_inc = (wxyz2 - wxyz1) / total_frames
        scale_inc = (s2 - s1) / total_frames
        zoom_inc = (z2 - z1) / total_frames
        pov_inc = (p2 - p1) / total_frames

        # Disable standard view actions on toolbars/menus while animating.
        # This is a safety feature to keep the user from clicking another view 
        # animation action while this one is still running.
        self.win.enableViews(False)

        # 'is_animating' is checked in selectAtoms_GraphicsMode.update_selobj() to determine whether the 
        # GLPane is currently animating between views.  If True, then update_selobj() will 
        # not select any object under the cursor. mark 060404.
        self.is_animating = True

        try: #bruce 060404 for exception safety (desirable for both enableViews and is_animating)

            # Main animation loop, which doesn't draw the final frame of the loop.  
            # See comments below for explanation.
            for frame in range(1, total_frames): # Notice no +1 here.
                wxyz1 += rot_inc
                self.quat = Q(norm(wxyz1))
                self.pov += pov_inc
                self.zoomFactor += zoom_inc
                self.scale += scale_inc
                self.gl_update_duration()
                # Very desirable to adjust total_frames inside the loop to maintain
                # animation speed consistency. mark 060127.

            # The animation loop did not draw the last frame on purpose.  Instead,
            # we snap to the destination view.  This also eliminates the possibility
            # of any roundoff error in the increment values, which might result in a 
            # slightly wrong final viewpoint.
            self.is_animating = False 
                # piotr 080325: Moved the flag reset to here to make sure 
                # the last frame is redrawn the same way as it was before 
                # the animation has started (e.g. to show external bonds
                # if they were suppressed during the animation).
                # I'm not entirely sure if that is a safe solution.
                # The is_animating attribute is used to disable view and 
                # object renaming and I'm not sure if setting it "False"
                # early will not interfere with the renaming code.
            self.snapToView(q2, s2, p2, z2, update_duration = True)
                # snapToView() must call gl_update_duration() and not gl_update(), 
                # or we'll have an issue if total_frames ever ends up = 1. In that case,
                # self._repaint_duration would never get set again because gl_update_duration()
                # would never get called again. BTW,  gl_update_duration()  (as of 060127)
                # is only called in the main animation loop above or when a new part is loaded.
                # gl_update_duration() should be called at other times, too (i.e. when 
                # the display mode changes or something significant happens to the 
                # model or display mode that would impact the rendering duration),
                # or better yet, the number of frames should be adjusted in the 
                # main animation loop as it plays.  This is left as something for me to do
                # later (probably after A7). This verbose comment is left as a reminder
                # to myself about all this.  mark 060127.

        except:
            print_compact_traceback("bug: exception (ignored) during animateToView's loop: ")
            pass

        # Enable standard view actions on toolbars/menus.
        self.win.enableViews(True)

        # Finished animating.
        # piotr 080325: set it off again just to make sure it is off
        # if there was an exception in the animation loop 
        self.is_animating = False

    # ==
    
    def center_and_scale_from_bbox(self, bbox, klugefactor = 1.0):
        #bruce 070919 split this out of some other methods here.
        ### REVIEW: should this be a BBox method (taking aspect as an argument)?
        # Probably yes -- it uses self only for self.aspect.
        """
        Compute and return a center, and a value for self.scale,
        which are sufficient to show the contents which were used to
        construct bbox (a BBox object), taking self.aspect into account.
           But reduce its size by mutiplying it by klugefactor (typically 0.75
        or so, though the default value is 1.0 since anything less can make some
        bbox contents out of the view), as a kluge for the typical bbox corners
        being farther away than they need to be for most shapes of bbox
        contents. (KLUGE)
           (TODO: Ideally this should be fixed by computing bbox.scale()
        differently, e.g. doing it in the directions corresponding to glpane
        axes.)
        """
        center = bbox.center()

        scale = float( bbox.scale() * klugefactor) #bruce 050616 added float() as a precaution, probably not needed
            # appropriate height to show everything, for square or wide glpane [bruce 050616 comment]
        aspect = self.aspect
        if aspect < 1.0:
            # tall (narrow) glpane -- need to increase self.scale
            # (defined in terms of glpane height) so part bbox fits in width
            # [bruce 050616 comment]
            scale /= aspect
        return center, scale

    # ==

    def gl_update_duration(self, new_part = False):
        """
        Redraw GLPane and update the repaint duration variable <self._repaint_duration>
        used by animateToView() to compute the proper number of animation frames.
        Redraws the GLPane twice if <new_part> is True and only saves the repaint 
        duration of the second redraw.  This is needed in the case of drawing a newly opened part,
        which takes much longer to draw the first time than the second (or thereafter).
        """
        # The first redraw of a new part takes much longer than the second redraw.
        if new_part: 
            self.gl_update()
            env.call_qApp_processEvents() # Required!

        self._repaint_start_time = time.time()
        self.gl_update()
        env.call_qApp_processEvents() # This forces the GLPane to update before executing the next gl_update().
        self._repaint_end_time = time.time()

        self._repaint_duration =  max(MIN_REPAINT_TIME, self._repaint_end_time - self._repaint_start_time)

        # _last_few_repaint_times is currently unused. May need it later.  Mark 060116.
        # (bruce 080912: disabling it. if we revive it, something needs to initialize it to [].)
        ## self._last_few_repaint_times.append( self._repaint_duration)
        ## self._last_few_repaint_times = self._last_few_repaint_times[-5:] # keep at most the last five times

        ##if new_part:
        ##    print "new part, repaint duration = ", self._repaint_duration
        ##else:
        ##    print "repaint duration = ", self._repaint_duration

        return

    pass

# end

