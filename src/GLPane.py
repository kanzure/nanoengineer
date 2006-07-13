# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
GLPane.py -- Atom's main model view, based on Qt's OpenGL widget.

Mostly written by Josh; partly revised by Bruce for mode code revision, 040922-24.
Revised by many other developers since then (and perhaps before).

$Id$

bruce 050913 used env.history in some places.
"""

## bruce 050408 removed several "import *" below
from qt import QFont, QWidget, QMessageBox
from qtgl import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLE import *
import math
from LinearAlgebra import *
from commands import *

import os,sys
import time
from VQT import *
import drawer
from shape import *
import re
from constants import *

from modifyMode import modifyMode
from cookieMode import cookieMode 
from extrudeMode import extrudeMode, revolveMode
from fusechunksMode import fusechunksMode
from selectMode import *
from depositMode import depositMode
from movieMode import movieMode
from zoomMode import zoomMode
from panMode import panMode
from rotateMode import rotateMode
from modes import modeMixin

import operator
import struct
##bruce 050413 removed: from povheader import povheader, povpoint

from fileIO import * #bruce 050414 comment: this might no longer be needed;
    # at least most symbols defined in fileIO (now moved to files_mmp)
    # don't occur in GLPane; but I didn't check for the few that are still
    # defined in fileIO.
from HistoryWidget import greenmsg, redmsg
from platform import fix_event_helper
import platform # for platform.atom_debug
from widgets import makemenu_helper
from debug import DebugMenuMixin, print_compact_traceback
import preferences
from prefs_constants import glpane_lights_prefs_key #bruce 051206
import env
from changes import SubUsageTrackingMixin


debug_lighting = False #bruce 050418

trans_feature = False ###@@@ bruce 050627 experimental code disabled for commit [DO NOT COMMIT with true]


paneno = 0
#  ... what a Pane ...

## normalGridLines = (0.0, 0.0, 0.6) # bruce 050410 removed this, and related code

pi2 = pi/2.0
pi3 = pi/3.0
pi4 = pi/4.0
xquats = [Q(1,0,0,0), Q(V(0,0,1),pi2), Q(V(0,0,1),pi), Q(V(0,0,1),-pi2),
          Q(V(0,0,1),pi4), Q(V(0,0,1),3*pi4),
          Q(V(0,0,1),-pi4), Q(V(0,0,1),-3*pi4)]
pquats = [Q(1,0,0,0), Q(V(0,1,0),pi2), Q(V(0,1,0),pi), Q(V(0,1,0),-pi2), 
          Q(V(1,0,0),pi2), Q(V(1,0,0),-pi2)]

quats100 = []
for q in pquats:
    for q1 in xquats:
        quats100 += [(q+q1, 0)]

rq = Q(V(0,1,0),pi2)
pquats = [Q(V(0,1,0),pi4), Q(V(0,1,0),3*pi4),
          Q(V(0,1,0),-pi4), Q(V(0,1,0),-3*pi4),
          Q(V(1,0,0),pi4), Q(V(1,0,0),3*pi4),
          Q(V(1,0,0),-pi4), Q(V(1,0,0),-3*pi4),
          rq+Q(V(1,0,0),pi4), rq+Q(V(1,0,0),3*pi4),
          rq+Q(V(1,0,0),-pi4), rq+Q(V(1,0,0),-3*pi4)]

quats110 = []
for q in pquats:
    for q1 in xquats:
        quats110 += [(q+q1, 1)]

cq = Q(V(1,0,0),0.615479708)
xquats = [Q(1,0,0,0), Q(V(0,0,1),pi3), Q(V(0,0,1),2*pi3), Q(V(0,0,1),pi),
          Q(V(0,0,1),-pi3), Q(V(0,0,1),-2*pi3)]
pquats = [Q(V(0,1,0),pi4), Q(V(0,1,0),3*pi4),
          Q(V(0,1,0),-pi4), Q(V(0,1,0),-3*pi4)]

quats111 = []
for q in pquats:
    for q1 in xquats:
        quats111 += [(q+cq+q1, 2), (q-cq+q1, 2)]

allQuats = quats100 + quats110 + quats111

MIN_REPAINT_TIME = 0.01 # minimum time to repaint (in seconds)

button = {0:None, 1:'LMB', 2:'RMB', 4:'MMB'} ###e NEEDS RENAME -- global variables need to be given more distinctive names
    # (but to rename it, someone has to search the entire program for places that might import it and use it,
    #  and preferably do it many weeks before a release so any rare bugs it causes might be found)
    # Also, the numeric constants need to be replaced by named constants from Qt (or at least from constants.py).

class GLPane(QGLWidget, modeMixin, DebugMenuMixin, SubUsageTrackingMixin):
    """Mouse input and graphics output in the main view window.
    """
    # Note: external code expects self.mode to always be a working
    # mode object, which has certain callable methods.  Our modes
    # themselves expect certain other attributes (like self.modetab)
    # to be present.  This is all set up and maintained by our mixin
    # class, modeMixin. [bruce 040922]
    #
    # [bruce 050112 adds: the reason the glpane is central to holding
    #  and switching a mode object might be that the mode object gets
    #  to process most mouse events on the glpane... but it might also
    #  be somewhat of a historical accident, since (esp. in the future)
    #  the mode might filter some other widgets' events too, esp. some
    #  of the operation buttons in the toolbars. Or, alternatively,
    #  modes might turn out to often apply to specific objects displayed
    #  in the glpane rather than to the pane as a whole. We'll see.
    #  For now, here it is.]

    # class constants (needed by modeMixin):
    mode_classes = [selectMolsMode, selectAtomsMode, modifyMode, depositMode,
                    cookieMode, extrudeMode, revolveMode, fusechunksMode,
                    movieMode, zoomMode, panMode, rotateMode]

    always_draw_hotspot = False #bruce 060627; not really needed, added for compatibility with ThumbView.py

    def __init__(self, assy, master=None, name=None, win=None):
        
        self.win = win

        modeMixin._init1(self)

        #bruce 050610 set gl format to request stencil buffer
        # (needed for mouseover-highlighting of objects of general shape in depositMode.bareMotion)
        glformat = QGLFormat()
        glformat.setStencil(True)
        
        QGLWidget.__init__(self, glformat, master, name)

        self.stencilbits = 0 # conservative guess, will be set to true value below
        
        if not self.format().stencil():
            # It's apparently too early to also test "or glGetInteger(GL_STENCIL_BITS) < 1" --
            # that glGet returns None even when the bits are actually there
            # (on my system this is 8 when tested later). Guess: this won't work until
            # the context is initialized.
            msg = ("Warning: your graphics hardware did not provide an OpenGL stencil buffer.\n"
                   "This will slow down some graphics operations.")
            ## env.history.message( regmsg( msg)) -- too early for that to work (need to fix that sometime, to queue the msg)
            print msg
            if platform.atom_debug:
                print "atom_debug: details of lack of stencil bits: " \
                      "self.format().stencil() = %r, glGetInteger(GL_STENCIL_BITS) = %r" % \
                      ( self.format().stencil() , glGetInteger(GL_STENCIL_BITS) )
                      # Warning: these values can be False, None -- I don't know why, since None is not an int!
                      # But see above for a guess. [bruce 050610]
            pass
        else:
            ## self.stencilbits = int( glGetInteger(GL_STENCIL_BITS) ) -- too early!
            self.stencilbits = 1 # conservative guess that if we got the buffer, it has at least one bitplane
                #e could probably be improved by testing this in initializeGL or paintGL (doesn't matter yet)
##            if platform.atom_debug:
##                print "atom_debug: glGetInteger(GL_STENCIL_BITS) = %r" % ( glGetInteger(GL_STENCIL_BITS) , )
            pass

        global paneno
        self.name = str(paneno)
        paneno += 1
        self.initialised = 0

        DebugMenuMixin._init1(self) # provides self.debug_event() [might provide or require more things too... #doc]

        self.trackball = Trackball(10,10)


        # [bruce 050419 new feature:]
        # The current Part to be displayed in this GLPane.
        # Logically this might not be the same as it's assy's current part, self.assy.part,
        # though in initial implem it will be the same except
        # when the part is changing... but the brief difference is important
        # since that's how the GLPane knows which previous part to store its
        # current view attributes in, before grabbing them from the new current part.
        # But some code might (incorrectly in principle, ok for now)
        # use self.assy.part when it should be using self.part.
        # The only thing we're sure self.part must be used for is to know in which
        # part the view attributes belong.
        self.part = None
        
        # Current view attributes (sometimes saved in or loaded from
        #  the currently displayed part or its mmp file):
        
        # rotation
        self.quat = Q(1, 0, 0, 0)
        # point of view (i.e. negative of center of view)
        self.pov = V(0.0, 0.0, 0.0)
        # half-height of window in Angstroms (gets reset by certain view-changing operations [bruce 050615 comment])
        self.scale = 10.0
        # zoom factor
        self.zoomFactor = 1.0


        # Other "current preference" attributes. ###e Maybe some of these should
        # also be part-specific and/or saved in the mmp file? [bruce 050418]

        # clipping planes, as percentage of distance from the eye
        self.near = 0.25 # After testing, this is much, much better.  Mark 060116. [Prior value was 0.66 -- bruce 060124 comment]
        self.far = 12.0  ##2.0, Huaicai: make this bigger, so models will be
                               ## more likely sitting within the view volume
        # start in perspective mode
        self.ortho = 0

        # Current coordinates of the mouse.
        self.MousePos = V(0,0)
 
        ##Huaicai 2/8/05: If this is true, redraw everything. It's better to split
        ##the paintGL() to several functions, so we may choose to draw 
        ##every thing, or only some thing that has been changed.
        self.redrawGL = True  
        
        # not selecting anything currently
        # [as of 050418 (and before), this is used in cookieMode and selectMode]
        self.shape = None

        self.setMouseTracking(True)

        # bruce 041220 let the GLPane have the keyboard focus, to fix bugs.
        # See comments above our keyPressEvent method.
        ###e I did not yet review  the choice of StrongFocus in the Qt docs,
        # just copied it from MWsemantics.
        self.setFocusPolicy(QWidget.StrongFocus)

##        self.singlet = None #bruce 060220 zapping this, seems to be old and to no longer be used
        self.selatom = None # josh 10/11/04 supports depositMode
        
        self.jigSelectionEnabled = True # mark 060312
        
        self.is_animating = False # mark 060404
            # Set to True while animating between views in animateToView() so 
            # that selectAtomsMode.update_selobj() will not select and highlight
            # objects under the cursor. mark 060404

        # [bruce 050608]
        self.glselect_dict = {} # only used within individual runs
            # see also env.obj_with_glselect_name
        
        self._last_few_repaint_times = []
            # repaint times will be appended to this,
            # but it will be trimmed to keep only the last 5 (or fewer) times
        self._repaint_duration = MIN_REPAINT_TIME

        ###### User Preference initialization ##############################
        
        # Get glpane related settings from prefs db.
        # Default values are set in "prefs_table" in prefs_constants.py.
        # Mark 050919.
        
        self.compassPosition = env.prefs[compassPosition_prefs_key]
        self.ortho = env.prefs[defaultProjection_prefs_key]
        # This updates the checkmark in the View menu. Fixes bug #996 Mark 050925.
        self.setViewProjection(self.ortho) 

        # default display form for objects in the window
        # even tho there is only one assembly to a window,
        # this is here in anticipation of being able to have
        # multiple windows on the same assembly
        self.display = env.prefs[defaultDisplayMode_prefs_key]
        self.win.dispbarLabel.setText( "Current Display: " + dispLabel[self.display] )
        
        ###### End of User Preference initialization ########################## 
        
        self.makeCurrent()
        
        drawer.setup()
        self.setAssy(assy) # leaves self.mode as nullmode, as of 050911

        self.loadLighting() #bruce 050311
            #bruce question 051212: why doesn't this prevent bug 1204 in use of lighting directions on startup?
        
        return # from GLPane.__init__        

    # self.part maintenance [bruce 050419]
    
    def set_part(self, part):
        """change our current part to the one given, and take on that part's view;
        ok if old or new part is None;
        note that when called on our current part,
        effect is to store our view into it
        (which might not actually be needed, but is fast enough and harmless)
        """
        if self.part is not part:
            self.gl_update() # we depend on this not doing the redraw until after we return
        self._close_part() # saves view into old part (if not None)
        self.part = part
        self._open_part() # loads view from new part (if not None)

    def forget_part(self, part):
        "[public] if you know about this part, forget about it (call this from dying parts)"
        if self.part is part:
            self.set_part(None)
        return

    def _close_part(self):
        "[private] save our current view into self.part [if not None] and forget about self.part"
        if self.part:
            self._saveLastViewIntoPart( self.part)
        self.part = None

    def _open_part(self):
        "[private] after something set self.part, load our current view from it"
        if self.part:
            self._setInitialViewFromPart( self.part)
        # else our current view doesn't matter
        return

    def saveLastView(self):
        "[public method] update the view of all parts you are displaying (presently only one or none) from your own view"
        if self.part:
            self._saveLastViewIntoPart( self.part)
    
    #bruce 050418 split the following Csys methods into two methods each,
    # so MWsemantics can share code with them. Also revised their docstrings,
    # and revised them for assembly/part split (i.e. per-part csys records),
    # and renamed them as needed to reflect that.
    
    def _setInitialViewFromPart(self, part):
        """Set the initial (or current) view used by this GLPane
        to the one stored in part.lastCsys, i.e. to part's "Last View".
        """
        # Huaicai 1/27/05: part of the code of this method comes
        # from original setAssy() method. This method can be called
        # after setAssy() has been called, for example, when opening
        # an mmp file. 
        
        self.snapToCsys( part.lastCsys)
    
    def _saveLastViewIntoPart(self, part):
        """Save the current view used by this GLPane into part.lastCsys,
        which (when this part's assy is later saved in an mmp file)
        will be saved as that part's "Last View".
        [As of 050418 this still only gets saved in the file for the main part]
        """
        # Huaicai 1/27/05: before mmp file saving, this method
        # should be called to save the last view user has, which will
        # be used as the initial view when it is opened again.
        self.saveViewInCsys( part.lastCsys)

    def saveViewInCsys(self, csys):
        "Save the current view used by this GLPane in the given Csys object."
        #e [bruce comment 050418: it would be good to verify csys has the right type,
        #   since almost any python object could be used here without any immediately
        #   detectable error. Maybe this should be a method in csys.]
        csys.quat = Q(self.quat)
        csys.scale = self.scale
        csys.pov = V(self.pov[0], self.pov[1], self.pov[2])
        csys.zoomFactor = self.zoomFactor

    # ==
    
    def setAssy(self, assy): #bruce 050911 revised this
        """[bruce comment 040922] This is called from self.__init__,
        and from MWSemantics.__clear when user asks to open a new
        file, etc.  Apparently, it is supposed to forget whatever is
        happening now, and reinitialize the entire GLPane.  However,
        it does nothing to cleanly leave the current mode, if any; my
        initial guess [040922 1035am] is that that's a bug.  (As of
        040922 I didn't yet try to fix that... only to emit a warning
        when it happens. Any fix requires modifying our callers.)  I
        also wonder if setAssy ought to do some of the other things
        now in __init__, e.g. setting some display prefs to their
        defaults.  Yet another bug (in how it's called now): user is
        evidently not given any chance to save unsaved changes, or get
        back to current state if the openfile fails... tho I'm not
        sure I'm right about that, since I didn't test it.
           Revised 050911: leaves self.mode as nullmode.
        """
        ##e should previous self.assy be destroyed, or at least made to no longer point to self? [bruce 051227 question]
        assy.o = self ###@@@ should only the part know the glpane?? or, only the mode itself? [bruce 050418 comment]
        self.assy = assy
        try:
            mainpart = assy.tree.part
            assert mainpart
        except:
            # I hope this never happens... but I don't know; if it does, reorder things?? [bruce 050418 comment]
            # [bruce 050428: I've never seen it that I noticed...]
            if platform.atom_debug:
                print "atom_debug: no mainpart yet in setAssy (ok during init); using a fake one"
            mainpart = Part(self) #bruce 050418 -- might be common during init; use this just for its lastCsys
            self._setInitialViewFromPart( mainpart)
        else:
            # [bruce 050428: this apparently always happens]
            self.set_part( mainpart)
        
        # defined in modeMixin [bruce 040922]; requires self.assy
        self._reinit_modes() # leaves mode as nullmode as of 050911

        return # from GLPane.setAssy

    # == view toolbar helper methods
    
    # [bruce 050418 made these from corresponding methods in MWsemantics.py,
    #  which still exist but call these, perhaps after printing a history message.
    #  Also revised them for assembly/part split, i.e. per-part csys attributes.]
    
    def setViewHome(self):
        "Change view to our model's home view (for glpane's current part)."
        self.animateToCsys( self.part.homeCsys)
        
    def setViewFitToWindow(self, fast=False):
        "Change view so that the entire model fits in the glpane. If <fast> is True, then snap to the view (i.e. don't animate)"
        # Recalculate center and bounding box for all the visible chunks in the current part.
        # The way a 3d bounding box is used to calculate the fit is not adequate. I consider this a bug, but I'm not sure
        # how to best use the BBox object to compute the proper fit. Should ask Bruce. This will do for now. Mark 060713.
        
        bbox = BBox()

        for mol in self.assy.molecules:
            if mol.hidden or mol.display == diINVISIBLE:
                continue
            bbox.merge(mol.bbox)
        
        center = bbox.center()

        scale = float( bbox.scale() * .75) #bruce 050616 added float() as a precaution, probably not needed
            # appropriate height to show everything, for square or wide glpane [bruce 050616 comment]
        aspect = float(self.width) / self.height
        if aspect < 1.0:
            # tall (narrow) glpane -- need to increase self.scale
            # (defined in terms of glpane height) so part bbox fits in width
            # [bruce 050616 comment]
            scale /= aspect
        pov = V(-center[0], -center[1], -center[2])
        if fast:
            self.snapToView(self.quat, scale, pov, 1.0)
        else:
            self.animateToView(self.quat, scale, pov, 1.0)

    def setViewHomeToCurrent(self):
        "Set the Home view to the current view."
        self.saveViewInCsys( self.part.homeCsys)
        self.part.changed() # Mark [041215]
        
    def setViewRecenter(self, fast=False):
        "Recenter the current view around the origin of modeling space."
        part = self.part
        part.computeBoundingBox()
        scale = (part.bbox.scale() * .75) + (vlen(part.center) * .5)
        aspect = float(self.width) / self.height
        if aspect < 1.0:
            scale /= aspect
        pov = V(0,0,0) 
        if fast:
            self.snapToView(self.quat, scale, pov, 1.0)
        else:
            self.animateToView(self.quat, scale, pov, 1.0)
        
    def setViewProjection(self, projection): # Added by Mark 050918.
        '''Set projection, where 0 = Perspective and 1 = Orthographic.  It does not set the 
        prefs db value itself, since we don't want all user changes to projection to be stored
        in the prefs db, only the ones done from the Preferences dialog.
        '''

        # Set the checkmark for the Ortho/Perspective menu item in the View menu.  
        # This needs to be done before comparing the value of self.ortho to projection
        # because self.ortho and the toggle state of the corresponding action may 
        # not be in sync at startup time. This fixes bug #996.
        # Mark 050924.
        if projection:
            self.win.setViewOrthoAction.setOn(1)
        else:
            self.win.setViewPerspecAction.setOn(1)
        
        if self.ortho == projection:
            return
            
        self.ortho = projection
        self.gl_update()
        
    def snapToCsys(self, csys):
        '''Snap to the destination view defined by csys.
        '''
        self.snapToView(csys.quat, csys.scale, csys.pov, csys.zoomFactor)
        
    def animateToCsys(self, csys, animate = True):
        '''Animate to the destination view defined by csys.
        If animate is False *or* the user pref "Animate between views" is not selected, 
        then do not animate;  just snap to the destination view.
        '''
        
        # Determine whether to snap (don't animate) to the destination view.
        if not animate or not env.prefs[animateStandardViews_prefs_key]:
            self.snapToCsys(csys)
            return
            
        self.animateToView(csys.quat, csys.scale, csys.pov, csys.zoomFactor, animate)

    def snapToView(self, q2, s2, p2, z2, update_duration = False):
        '''Snap to the destination view defined by
        quat q2, scale s2, pov p2, and zoom factor z2.
        '''
        
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
        "Rotate current view to quat (viewpoint) q2"
        
        self.animateToView(q2, self.scale, self.pov, self.zoomFactor, animate=True)
        return

    # animateToView() uses "Normalized Linear Interpolation" 
    # and not "Spherical Linear Interpolation" (AKA slerp), 
    # which traces the same path as slerp but works much faster.
    # The advantages to this approach are explained in detail here:
    # http://number-none.com/product/Hacking%20Quaternions/
    def animateToView(self, q2, s2, p2, z2, animate=True):
        '''Animate from the current view to the destination view defined by
        quat q2, scale s2, pov p2, and zoom factor z2.
        If animate is False *or* the user pref "Animate between views" is not selected, 
        then do not animate;  just snap to the destination view.
        '''
        
        # Caller could easily pass these args in the wrong order.  Let's typecheck them.
        typecheckViewArgs(q2, s2, p2, z2)
        
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
        rot_angle = deltaq.angle * 180/pi # rotation delta (in degrees)
        if rot_angle > 180:
            rot_angle = 360 - rot_angle # go the short way
        
        # For each delta, compute the total number of frames each would 
        # require (by itself) for the animation sequence.
        rot_frames = int(rot_angle/180 * max_frames)
        pov_frames = int(deltap * .2) # .2 based on guess/testing. mark 060123
        scale_frames = int(deltas * .05) # .05 based on guess/testing. mark 060123
        zoom_frames = int(deltaz * .05) # Not tested. mark 060123
        
        # Using the data above, this formula computes the ideal number of frames
        # to use for the animation loop.  It attempts to keep animation speeds consistent.
        total_frames = int( \
            min(max_frames, \
            max(3, rot_frames, pov_frames, scale_frames, zoom_frames)))
        
        #print "total_frames =", total_frames
        
        # Compute the increments for each view parameter to use in the animation loop.
        rot_inc = (wxyz2 - wxyz1) / total_frames
        scale_inc = (s2 - s1) / total_frames
        zoom_inc = (z2 - z1) / total_frames
        pov_inc = (p2 - p1) / total_frames
        
        # Disable standard view actions on toolbars/menus while animating.
        # This is a safety feature to keep the user from clicking another view 
        # animation action while this one is still running.
        self.win.enableViews(False)
        
        # 'is_animating' is checked in selectAtomsMode.update_selobj() to determine whether the 
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
        self.is_animating = False
    
    # == "callback methods" from modeMixin:

    def update_after_new_mode(self):
        """do whatever updates are needed after self.mode might have changed
        (ok if this is called more than needed, except it might be slower)
        """
        if self.selatom is not None: #bruce 050612 precaution (scheme could probably be cleaned up #e)
            if platform.atom_debug:
                print "atom_debug: update_after_new_mode storing None over self.selatom", self.selatom
            self.selatom = None
        if self.selobj is not None: #bruce 050612 bugfix; to try it, in Build drag selatom over Select Atoms toolbutton & press it
            if platform.atom_debug:
                print "atom_debug: update_after_new_mode storing None over self.selobj", self.selobj
            self.set_selobj(None)
        #bruce 050408: change widget's erase color (seen only if it's resized,
        # and only briefly -- unrelated to OpenGL clearColor) to current mode's
        # background color; this fixes the bug in which the glpane or its edges
        # flicker to black during a main-window resize.
        #bruce 050413: limit this to Mac, since it turns out that bug (which has
        # no bug number yet) was Mac-specific, but this change caused a new bug 530
        # on Windows. (Not sure about Linux.)
        # See also bug 141 (black during mode-change), related but different.
        if sys.platform == 'darwin':
            bgcolor = self.mode.backgroundColor
                ##e [bruce 050615 comment, moved here from a wrong location by bruce 050702:]
                # for modes with transparent surfaces covering screen, this ought to blend that in
                # (or we could change how they work so the blank areas looked like the specified bgcolor)
            r = int(bgcolor[0]*255 + 0.5) # (same formula as in elementSelector.py)
            g = int(bgcolor[1]*255 + 0.5)
            b = int(bgcolor[2]*255 + 0.5)
            self.setPaletteBackgroundColor(QColor(r, g, b))
                # see Qt docs for this and for backgroundMode
        
        #e also update tool-icon visual state in the toolbar?
        # bruce 041222 [comment revised 050408]:
        # changed this to a full update (not just a glpane update),
        # though technically the non-glpane part is the job of our caller rather than us,
        # and changed MWsemantics to make that safe during our __init__.
        self.win.win_update()

    # def setMode(self, modename) -- moved to modeMixin [bruce 040922]
    
    # ==

    # bruce 041220: handle keys in GLPane (see also setFocusPolicy, above).
    # Also call these from MWsemantics whenever it has the focus. This fixes
    # some key-focus-related bugs. We also wrap the Qt events with our own
    # type, to help fix Qt's Mac-specific Delete key bug (bug 93), and (in the
    # future) for other reasons. The fact that clicking in the GLPane now gives
    # it the focus (due to the setFocusPolicy, above) is also required to fully
    # fix bug 93.
    
    def keyPressEvent(self, e):
        #e future: also track these to match releases with presses, to fix
        # dialogs intercepting keyRelease? Maybe easier if they just pass it on.
        mc = env.begin_op("(keypress)") #bruce 060127
            # Note: we have to wrap press and release separately; later, we might pass them tags
            # to help the diffs connect up for merging
            # (same as in drags and maybe as in commands doing recursive event processing).
            # [bruce 060127]
        try:
            #print "GLPane.keyPressEvent(): self.in_drag=",self.in_drag
            if not self.in_drag:
                #bruce 060220 new code; should make it unnecessary (and incorrect)
                # for modes to track mod key press/release for cursor,
                # once update_modkeys calls a cursor updating routine
                but = e.stateAfter()
                self.update_modkeys(but)
            self.mode.keyPressEvent( atom_event(e) )
        finally:
            env.end_op(mc)
        return
        
    def keyReleaseEvent(self, e):
        mc = env.begin_op("(keyrelease)") #bruce 060127
        try:
            if not self.in_drag:
                #bruce 060220 new code; see comment in keyPressEvent
                but = e.stateAfter()
                self.update_modkeys(but)
            self.mode.keyReleaseEvent( atom_event(e) )
        finally:
            env.end_op(mc)
        return

    def warning(self, str, bother_user_with_dialog = 0, ensure_visible = 1):
        
        """[experimental method by bruce 040922]

            ###@@@ need to merge this with env.history.message
            or make a sibling method! [bruce 041223]
        
           Show a warning to the user, without interrupting them
           (i.e. not in a dialog) unless bother_user_with_dialog is
           true, or unless ensure_visible is true and there's no other
           way to be sure they'll see the message.  (If neither of
           these options is true, we might merely print the message to
           stdout.)

           In the future, this might go into a status bar in the
           window, if we can be sure it will remain visible long
           enough.  For now, that won't work, since some status bar
           messages I emit are vanishing almost instantly, and I can't
           yet predict which ones will do that.  Due to that problem
           and since the stdout/stderr output might be hidden from the
           user, ensure_visible implies bother_user_with_dialog for
           now.  (And when we change that, we have to figure out
           whether all the calls that no longer use dialogs are still
           ok.)

           In the future, all these messages will also probably get
           timestamped and recorded in a log file, in addition to
           whereever they're shown now.

           This is an experimental method, not yet uniformly used
           (most uses are in modes.py), and it's likely to be revised
           a few times in API as well as in implemention. [bruce
           040924]
        """
        
        use_status_bar = 0 # always 0, for now
        use_dialog = bother_user_with_dialog
        
        if ensure_visible:
            prefix = "WARNING"
            use_dialog = 1 ###e for now, and during debugging --
            ### status bar would be ok when we figure out how to
            ### guarantee it lasts
        else:
            prefix = "warning"
        str = str[0].upper() + str[1:] # capitalize the sentence
        msg = "%s: %s" % (prefix,str,)
        ###e add a timestamp prefix, at least for the printed one

        # always print it so there's a semi-permanent record they can refer to
        print msg 
        
        if use_status_bar: # do this first
            ## [this would work again as of 050107:] self.win.statusBar().message( msg)
            assert 0 # this never happens for now
        if use_dialog:
            # use this only when it's worth interrupting the user to make
            # sure they noticed the message.. see docstring for details
            ##e also linebreak it if it's very long? i might hope that some
            # arg to the messagebox could do this...
            QMessageBox.warning(self, prefix, msg) # args are title, content
        return
        
    # return space vectors corresponding to various directions
    # relative to the screen
    def __getattr__(self, name): # in class GLPane
        if name == 'lineOfSight':
            return self.quat.unrot(V(0,0,-1))
        elif name == 'right':
            return self.quat.unrot(V(1,0,0))
        elif name == 'left':
            return self.quat.unrot(V(-1,0,0))
        elif name == 'up':
            return self.quat.unrot(V(0,1,0))
        elif name == 'down':
            return self.quat.unrot(V(0,-1,0))
        elif name == 'out':
            return self.quat.unrot(V(0,0,1))
        else:
            raise AttributeError, 'GLPane has no "%s"' % name

    # == lighting methods [bruce 050311 rush order for Alpha4]
    
    def setLighting(self, lights, _guard_ = 6574833, gl_update = True): 
        """Set current lighting parameters as specified
        (using the format as described in the getLighting method docstring).
        This does not save them in the preferences file; for that see the saveLighting method.
        If option gl_update is False, then don't do a gl_update, let caller do that if they want to.
        """
        assert _guard_ == 6574833 # don't permit optional args to be specified positionally!!
        try:
            # check, standardize, and copy what the caller gave us for lights
            res = []
            lights = list(lights)
            assert len(lights) == 3
            for c,a,d,s,x,y,z,e in lights:
                # check values, give them standard types
                r = float(c[0])
                g = float(c[1])
                b = float(c[2])
                a = float(a)
                d = float(d)
                s = float(s)
                x = float(x)
                y = float(y)
                z = float(z)
                assert 0.0 <= r <= 1.0
                assert 0.0 <= g <= 1.0
                assert 0.0 <= b <= 1.0
                assert 0.0 <= a <= 1.0
                assert 0.0 <= d <= 1.0
                assert 0.0 <= s <= 1.0
                assert e in [0,1,True,False]
                e = not not e
                res.append( ((r,g,b),a,d,s,x,y,z,e) )
            lights = res
        except:
            print_compact_traceback("erroneous lights %r (ignored): " % lights)
            return
        self._lights = lights
        # set a flag so we'll set up the new lighting in the next paintGL call
        self.need_setup_lighting = True
        #e maybe arrange to later save the lighting in prefs... don't know if this belongs here
        # update GLPane unless caller wanted to do that itself
        if gl_update:
            self.gl_update()
        return

    def getLighting(self):
        """Return the current lighting parameters.
        [For now, these are a list of 3 tuples, one per light,
        each giving several floats and booleans
        (specific format is only documented in other methods or in their code).]
        """
        return list(self._lights)

    # default value of instance variable:
    # [bruce 051212 comment: not sure if this needs to be in sync with any other values;
    #  also not sure if this is used anymore, since __init__ sets _lights from prefs db via loadLighting.]
    _lights = drawer._default_lights

    _default_lights = _lights # this copy will never be changed

    need_setup_lighting = True # whether the next paintGL needs to call _setup_lighting

    _last_glprefs_data_used_by_lights = None #bruce 051212, replaces/generalizes _last_override_light_specular
    
    def _setup_lighting(self): # as of bruce 060415, this is mostly duplicated between GLPane (has comments) and ThumbView ###@@@
        """[private method]
        Set up lighting in the model (according to self._lights).
        [Called from both initializeGL and paintGL.]
        """
        glEnable(GL_NORMALIZE)
            # bruce comment 050311: I don't know if this relates to lighting or not
            # grantham 20051121: Yes, if NORMALIZE is not enabled (and normals
            # aren't unit length or the modelview matrix isn't just rotation)
            # then the lighting equation can produce unexpected results.  

        #bruce 050413 try to fix bug 507 in direction of lighting:
        ##k might be partly redundant now; not sure whether projection matrix needs to be modified here [bruce 051212]
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glprefs = None
            #e someday this could be an argument providing a different glprefs object
            # for local use in part of a scenegraph (if other code was also revised) [bruce 051212 comment]
        
        #bruce 051212 moved most code from this method into new function, setup_standard_lights
        drawer.setup_standard_lights( self._lights, glprefs)

        # record what glprefs data was used by that, for comparison to see when we need to call it again
        # (not needed for _lights since another system tells us when that changes)
        self._last_glprefs_data_used_by_lights = drawer.glprefs_data_used_by_setup_standard_lights(glprefs)
        return
    
    def saveLighting(self):
        "save the current lighting values in the standard preferences database"
        try:
            prefs = preferences.prefs_context()
            key = glpane_lights_prefs_key
            # we'll store everything in a single value at this key,
            # making it a dict of dicts so it's easy to add more lighting attrs (or lights) later
            # in an upward-compatible way.
            # [update, bruce 051206: it turned out that when we added lots of info it became
            #  not upward compatible, causing bug 1181 and making the only practical fix of that bug
            #  a change in this prefs key. In successive commits I moved this key to prefs_constants,
            #  then renamed it (variable and key string) to try to fix bug 1181. I would also like to find out
            #  what's up with our two redundant storings of light color in prefs db, ###@@@
            #  but I think bug 1181 can be fixed safely this way without my understanding that.]

            (((r0,g0,b0),a0,d0,s0,x0,y0,z0,e0), \
            ( (r1,g1,b1),a1,d1,s1,x1,y1,z1,e1), \
            ( (r2,g2,b2),a2,d2,s2,x2,y2,z2,e2)) = self._lights
             
            # now process it in a cleaner way
            val = {}
            for (i, (c,a,d,s,x,y,z,e)) in zip(range(3),self._lights):
                name = "light%d" % i
                params = dict( color = c, \
                                        ambient_intensity = a, \
                                        diffuse_intensity = d, \
                                        specular_intensity = s, \
                                        xpos = x, ypos = y, zpos = z, \
                                        enabled = e )
                val[name] = params
            # save the prefs to the database file
            prefs[key] = val
            # This was printing many redundant messages since this method is called 
            # many times while changing lighting parameters in the Preferences | Lighting dialog.
            # Mark 051125.
            #env.history.message( greenmsg( "Lighting preferences saved" ))
        except:
            print_compact_traceback("bug: exception in saveLighting (pref changes not saved): ")
            #e redmsg?
        return

    def loadLighting(self, gl_update = True):
        """load new lighting values from the standard preferences database, if possible;
        if correct values were loaded, start using them, and do gl_update unless option for that is False;
        return True if you loaded new values, False if that failed
        """
        try:
            prefs = preferences.prefs_context()
            key = glpane_lights_prefs_key
            try:
                val = prefs[key]
            except KeyError:
                # none were saved; not an error and not even worthy of a message
                # since this is called on startup and it's common for nothing to be saved.
                # Return with no changes.
                return False
            # At this point, you have a saved prefs val, and if this is wrong it's an error.        
            # val format is described (partly implicitly) in saveLighting method.
            res = [] # will become new argument to pass to self.setLighting method, if we succeed
            for name in ['light0','light1','light2']:
                params = val[name] # a dict of ambient, diffuse, specular, x, y, z, enabled
                color = params['color'] # light color (r,g,b)
                a = params['ambient_intensity'] # ambient intensity
                d = params['diffuse_intensity'] # diffuse intensity
                s = params['specular_intensity'] # specular intensity
                x = params['xpos'] # X position
                y = params['ypos'] # Y position
                z = params['zpos'] # Z position
                e = params['enabled'] # boolean

                res.append( (color,a,d,s,x,y,z,e) )
            self.setLighting( res, gl_update = gl_update)
            if debug_lighting:
                print "debug_lighting: fyi: Lighting preferences loaded"
            return True
        except:
            print_compact_traceback("bug: exception in loadLighting (current prefs not altered): ")
            #e redmsg?
            return False
        pass

    def restoreDefaultLighting(self, gl_update = True):
        "restore the default (built-in) lighting preferences (but don't save them)."
        
        # Restore light color prefs keys.
        env.prefs.restore_defaults([
            light1Color_prefs_key, 
            light2Color_prefs_key, 
            light3Color_prefs_key,
            ])
            
        self.setLighting( self._default_lights,  gl_update = gl_update )
        
        return True
    
    # ==
    
    def initializeGL(self):
        "#doc [called by Qt]"
        self.makeCurrent() # bruce comment 050311: probably not needed since Qt does it before calling this
        self._setup_lighting()
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        return

    #bruce 060220 changes related to supporting self.modkeys, self.in_drag.
    # These changes are unfinished in the following ways: ###@@@
    # - need to fix the known bugs in fix_event_helper, listed below
    # - update_modkeys needs to call some sort of self.mode.updateCursor routine
    # - then the modes which update the cursor for key press/release of modkeys need to stop doing that
    #   and instead just define that updateCursor routine properly
    # - ideally we'd capture mouseEnter and call both update_modkeys and the same updateCursor routine
    # - (and once the cursor works for drags between widgets, we might as well fix the statusbar text for that too)
    
    modkeys = None
    in_drag = False
    button = None
    
    def fix_event(self, but, when, target): #bruce 060220 added support for self.modkeys
        """[For most documentation, see fix_event_helper.
            We also set self.modkeys to replace the obsolete mode.modkey variable.
            This only works if we're called for all event types which want to look at that variable.]
        """
        but = fix_event_helper(self, but, when, target)
            # fix_event_helper has several known bugs as of 060220, including:
            # - target is not currently used, and it's not clear what it might be for
            # - it's overly bothered by dialogs that capture press and not release;
            # - maybe it can't be called for key events, but self.modkeys needs update then [might be fixed using in_drag #k];
            # - not sure it's always ok when user moves from one widget to another during a drag;
            # - confused if user releases two mouse buttons at different times to end a drag (thinks the first one ended it).
            # All these can be fixed straightforwardly when they become important enough. [bruce 060220]
        
        if when == 'release':
            self.in_drag = False
            self.button = None
            self.mode.update_cursor()
        else:
            olddrag = self.in_drag
            self.in_drag = but & (leftButton|midButton|rightButton)
                # you can also use this to see which mouse buttons are involved.
            if not olddrag:
                try:
                    # in_drag has values of 0 (None), 1 (LMB), 4 (MMB). or 2 (RMB) allowed here.
                    self.button = button[self.in_drag]
                except:
                    # To get here, two mouse buttons were pressed at the same time and one was 
                    # released (i.e. in-drag = 3, 5, 6). Leave self.button unchanged.
                    pass 
            
        self.update_modkeys(but)
            # need to call this when drag starts; ok to call it during drag too,
            # since retval is what came from fix_event
        return but

    def update_modkeys(self, but):
        """Call this whenever you have some modifier key flags from an event (as returned from fix_event,
        or found directly on the event as stateAfter in events not passed to fix_event).
        Exception: don't call it during a drag, except on values returned from fix_event, or bugs will occur.
        There is not yet a good way to follow this advice. This method and/or fix_event should provide one. ###e
           This method updates self.modkeys, setting it to None, 'Shift', 'Control' or 'Shift+Control'.
        (All uses of the obsolete mode.modkey variable should be replaced by this one.)
        """
        shift_control_flags = but & (shiftButton | cntlButton)
        oldmodkeys = self.modkeys
        if shift_control_flags == shiftButton:
            self.modkeys = 'Shift'
        elif shift_control_flags == cntlButton:
            self.modkeys = 'Control'
        elif shift_control_flags == (shiftButton | cntlButton):
            self.modkeys = 'Shift+Control'
        else:
            self.modkeys = None
        if self.modkeys != oldmodkeys:
            
            ## This would be a good place to tell the mode (self.mode) it might want to update the cursor,
            ## based on all state it knows about, including self.modkeys and what mouse is over,
            ## but it's not enough, since it doesn't cover mouseEnter (or mode Enter),
            ## where we need that even if modkeys didn't change. [bruce 060220]
            self.mode.update_cursor()
            
            if self.selobj and self.mode.hover_highlighting_enabled:
                if self.modkeys == 'Shift+Control' or oldmodkeys == 'Shift+Control':
                    # If something is highlighted under the cursor and we just pressed or released 
                    # "Shift+Control", repaint to update its correct highlight color.
                    self.gl_update()
        
        return

    def begin_select_cmd(self):
        # Warning: same named method exists in assembly, GLPane, and ops_select, with different implems.
        # More info in comments in assembly version. [bruce 051031]
        if self.assy:
            self.assy.begin_select_cmd()
        return

    def mouseDoubleClickEvent(self, event):
        # (note: mouseDoubleClickEvent and mousePressEvent share a lot of code)
        self.makeCurrent() #bruce 060129 precaution, presumably needed for same reasons as in mousePressEvent
        self.begin_select_cmd() #bruce 060129 bugfix (needed now that this can select atoms in depositMode)
        
        self.debug_event(event, 'mouseDoubleClickEvent')
        
        but = self.fix_event(event, 'press', self.mode)
        ## but = event.stateAfter()
        #k I'm guessing this event comes in place of a mousePressEvent;
        # need to test this, and especially whether a releaseEvent then comes
        # [bruce 040917 & 060124]
        ## print "Double clicked: ", but

        self.checkpoint_before_drag(event, but) #bruce 060323 for bug 1747 (caused by no Undo checkpoint for doubleclick)
            # Q. Why didn't that bug show up earlier??
            # A. guess: modelTree treeChanged signal, or (unlikely) GLPane paintGL, was providing a checkpoint
            # which made up for the 'checkpoint_after_drag' that this one makes happen (by setting self.__flag_and_begin_retval).
            # But I recently removed the checkpoint caused by treeChanged, and (unlikely cause) fiddled with code related to after_op.
            #   Now I'm thinking that checkpoint_after_drag should do one whether or not checkpoint_before_drag
            # was ever called. Maybe that would fix other bugs... but not cmenu op bugs like 1411 (or new ones the above-mentioned
            # change also caused), since in those, the checkpoint_before_drag happens, but the cmenu swallows up the
            # releaseEvent so the checkpoint_after_drag never has a chance to run. Instead, I'm fixing those by wrapping
            # most_of_paintGL in its own begin/end checkpoints, and (unlike the obs after_op) putting them after
            # env.postevent_updates (see its call to find them). But I might do the lone-releaseEvent checkpoint too. [bruce 060323]
            # Update, 060326: reverting the most_of_paintGL checkpointing, since it caused bug 1759 (more info there).

        if but & leftButton:
            self.mode.leftDouble(event)
        if but & midButton:
            self.mode.middleDouble(event)
        if but & rightButton:
            self.mode.rightDouble(event)

        return

    # == DUPLICATING checkpoint_before_drag and checkpoint_after_drag in TreeWidget.py -- should clean up ####@@@@ [bruce 060328]

    __pressEvent = None #bruce 060124 for Undo
    __flag_and_begin_retval = None

    def checkpoint_before_drag(self, event, but): #bruce 060124; split out of caller, 060126
        if but & (leftButton|midButton|rightButton):
            # Do undo_checkpoint_before_command if possible.
            #
            #bruce 060124 for Undo; will need cleanup of begin-end matching with help of fix_event;
            # also, should make redraw close the begin if no releaseEvent came by then (but don't
            #  forget about recursive event processing) [done in a different way in redraw, bruce 060323]
            if self.__pressEvent is not None and platform.atom_debug:
                # this happens whenever I put up a context menu in GLPane, so don't print it unless atom_debug ###@@@
                print "atom_debug: bug: pressEvent didn't get release:", self.__pressEvent
            self.__pressEvent = event
            self.__flag_and_begin_retval = None
            ##e we could simplify the following code using newer funcs external_begin_cmd_checkpoint etc in undo_manager
            if self.assy:
                begin_retval = self.assy.undo_checkpoint_before_command("(mouse)") # text was "(press)" before 060126 eve
                    # this command name should be replaced sometime during the command
                self.__flag_and_begin_retval = True, begin_retval
            pass
        return
    
    def mousePressEvent(self, event):
        """Dispatches mouse press events depending on shift and
        control key state.
        """
        # (note: mouseDoubleClickEvent and mousePressEvent share a lot of code)
        
        self.makeCurrent()
            ## Huaicai 2/25/05. This is to fix item 2 of bug 400: make this rendering context
            ## as current, otherwise, the first event will get wrong coordinates
        
        self.begin_select_cmd() #bruce 051031
        if self.debug_event(event, 'mousePressEvent', permit_debug_menu_popup = 1):
            #e would using fix_event here help to avoid those "release without press" messages,
            # or fix bugs from mouse motion? or should we set some other flag to skip subsequent
            # drag/release events until the next press? [bruce 060126 questions]
            return
        ## but = event.stateAfter()
        but = self.fix_event(event, 'press', self.mode)

        # (I hope fix_event makes sure at most one button flag remains; if not,
        #  following if/if/if should be given some elifs. ###k
        #  Note that same applies to mouseReleaseEvent; mouseMoveEvent already does if/elif.
        #  It'd be better to normalize it all in fix_event, though, in case user changes buttons
        #  without releasing them all, during the drag. Some old bug reports are about that. #e
        #  [bruce 060124-26 comment])
        
        ## print "Button pressed: ", but

        self.checkpoint_before_drag(event, but)
        
        if but & leftButton:
            if but & shiftButton:
                self.mode.leftShiftDown(event)
            elif but & cntlButton:
                self.mode.leftCntlDown(event)
            else:
                self.mode.leftDown(event)

        if but & midButton:
            if but & shiftButton and but & cntlButton: # mark 060228.
                self.mode.middleShiftCntlDown(event)
            elif but & shiftButton:
                self.mode.middleShiftDown(event)
            elif but & cntlButton:
                self.mode.middleCntlDown(event)
            else:
                self.mode.middleDown(event)

        if but & rightButton:
            if but & shiftButton:
                self.mode.rightShiftDown(event)
            elif but & cntlButton:
                self.mode.rightCntlDown(event)
            else:
                self.mode.rightDown(event)         

        return
    
    def mouseReleaseEvent(self, event):
        """#doc
        """
        self.debug_event(event, 'mouseReleaseEvent')
        ## but = event.state()
        but = self.fix_event(event, 'release', self.mode)
        ## print "Button released: ", but
        
        try:
            if but & leftButton:
                if but & shiftButton:
                    self.mode.leftShiftUp(event)
                elif but & cntlButton:
                    self.mode.leftCntlUp(event)
                else:
                    self.mode.leftUp(event)

            if but & midButton:
                if but & shiftButton and but & cntlButton: # mark 060228.
                    self.mode.middleShiftCntlUp(event)
                elif but & shiftButton:
                    self.mode.middleShiftUp(event)
                elif but & cntlButton:
                    self.mode.middleCntlUp(event)
                else:
                    self.mode.middleUp(event)

            if but & rightButton:
                if but & shiftButton:
                     self.mode.rightShiftUp(event)
                elif but & cntlButton:
                    self.mode.rightCntlUp(event)
                else:
                    self.mode.rightUp(event)
        except:
            print_compact_traceback("exception in mode's mouseReleaseEvent handler (bug, ignored): ") #bruce 060126
        
        self.checkpoint_after_drag(event) #bruce 060126 moved this later, to fix bug 1384, and split it out, for clarity
        return

    # == DUPLICATING checkpoint_before_drag and checkpoint_after_drag in TreeWidget.py -- should clean up ####@@@@ [bruce 060328]

    def checkpoint_after_drag(self, event): #bruce 060124; split out of caller, 060126 (and called it later, to fix bug 1384)
        """Do undo_checkpoint_after_command, if a prior press event did an undo_checkpoint_before_command to match.
        This should only be called *after* calling the mode-specific event handler for this event!
        """
        # (What if there's recursive event processing inside the event handler... when it's entered it'll end us, then begin us...
        #  so an end-checkpoint is still appropriate; not clear it should be passed same begin-retval -- most likely,
        #  the __attrs here should all be moved into env and used globally by all event handlers. I'll solve that when I get to
        #  the other forms of recursive event processing. #####@@@@@
        #  So for now, I'll assume recursive event processing never happens in the event handler
        #  (called just before this method is called) -- then the simplest
        #  scheme for this code is to do it all entirely after the mode's event handler (as done in this routine),
        #  rather than checking __attrs before the handlers and using the values afterwards. [bruce 060126])

        # Maybe we should simulate a pressEvent's checkpoint here, if there wasn't one, to fix hypothetical bugs from a
        # missing one. Seems like a good idea, but save it for later (maybe the next commit, maybe a bug report). [bruce 060323]
        
        if self.__pressEvent is not None: ####@@@@ and if no buttons are still pressed, according to fix_event?
            self.__pressEvent = None
            if self.__flag_and_begin_retval:
                flagjunk, begin_retval = self.__flag_and_begin_retval
                self.__flag_and_begin_retval = None
                if self.assy:
                    #k should always be true, and same assy as before
                    # (even for file-closing cmds? I bet not, but:
                    #  - unlikely as effect of a mouse-click or drag in GLPane;
                    #  - probably no harm from these checkpoints getting into different assys
                    #  But even so, when solution is developed (elsewhere, for toolbuttons), bring it here
                    #  or (better) put it into these checkpoint methods. ####@@@@)
                    self.assy.undo_checkpoint_after_command( begin_retval)
        return

    def mouseMoveEvent(self, event):
        """Dispatches mouse motion events depending on shift and
        control key state.
        """
        ## Huaicai 8/4/05. 
        self.makeCurrent()
        
        ##self.debug_event(event, 'mouseMoveEvent')
        ## but = event.state()
        but = self.fix_event(event, 'move', self.mode)
        
        if but & leftButton:
            if but & shiftButton:
                self.mode.leftShiftDrag(event)
            elif but & cntlButton:
                self.mode.leftCntlDrag(event)
            else:
                self.mode.leftDrag(event)

        elif but & midButton:
            if but & shiftButton and but & cntlButton: # mark 060228.
                self.mode.middleShiftCntlDrag(event)
            elif but & shiftButton:
                self.mode.middleShiftDrag(event)
            elif but & cntlButton:
                self.mode.middleCntlDrag(event)
            else:
                self.mode.middleDrag(event)

        elif but & rightButton:
            if but & shiftButton:
                self.mode.rightShiftDrag(event)
            elif but & cntlButton:
                self.mode.rightCntlDrag(event)
            else:
                self.mode.rightDrag(event)

        else:
            self.mode.bareMotion(event)
        return
    
    def wheelEvent(self, event):
        self.debug_event(event, 'wheelEvent')
        if not self.in_drag:
            but = event.state() # I think this event has no stateAfter() [bruce 060220]
            self.update_modkeys(but) #bruce 060220
        self.mode.Wheel(event) # mode bindings use modkeys from event; maybe this is ok?
            # Or would it be better to ignore this completely during a drag? [bruce 060220 questions]
        return

    def selectedJigTextPosition(self):
        return A(gluUnProject(5, 5, 0))

    def mousepoints(self, event, just_beyond = 0.0):
        """Returns a pair (tuple) of points (Numeric arrays of x,y,z)
        that lie under the mouse pointer at (or just beyond) the near clipping
        plane and in the plane of the center of view. Optional argument
        just_beyond = 0.0 tells how far beyond the near clipping plane
        the first point should lie. Before 041214 this was 0.01.
        """
        x = event.pos().x()
        y = self.height - event.pos().y()
        # bruce 041214 made just_beyond = 0.0 an optional argument,
        # rather than a hardcoded 0.01 (but put 0.01 into most callers)

        p1 = A(gluUnProject(x, y, just_beyond))
        p2 = A(gluUnProject(x, y, 1.0))

        los = self.lineOfSight
        
        k = dot(los, -self.pov - p1) / dot(los, p2 - p1)

        p2 = p1 + k*(p2-p1)
        return (p1, p2)

    def eyeball(self): #bruce 060219 ##e should call this to replace equivalent formulae in other places
        "Return the location of the eyeball in model coordinates."
        return self.quat.unrot(V(0,0,self.vdist)) - self.pov # note: self.vdist is (usually??) 6 * self.scale
        ##k need to review whether this is correct for tall aspect ratio GLPane

    def SaveMouse(self, event):
        """Extracts mouse position from event and saves it.
        (localizes the API-specific code for extracting the info)
        """
        self.MousePos = V(event.pos().x(), event.pos().y())

    def snapquat100(self):
        self.snapquat(quats100)

    def snapquat110(self):
        self.snapquat(quats110)

    def snapquat111(self):
        self.snapquat(quats111)

    def snap2trackball(self):
        return self.snapquat(allQuats)

    def snapquat(self, qlist):
        q1 = self.quat
        a=1.1
        what = 0
        for q2,n in qlist:
            a2 = vlen((q2-q1).axis)
            if a2 < a:
                a = a2
                q = q2
                what = n
        self.quat = Q(q)
        self.gl_update()
        return what

    def setDisplay(self, disp, default_display=False):
        '''Set the display mode of the GLPane, where:
            "disp" is the display mode, and
            "default_display" changes the header of the display status bar to either "Default Display" (True)
            or "Current Display (False, the default).
        '''
        
        # Fix to bug 800. Mark 050807
        if default_display:
            # Used when the user presses "Default Display" or changes the "Default Display"
            # in the preferences dialog.  
            header = "Default Display: " 
            self.mode.set_displayMode(diDEFAULT) # Fixes bug 1544. mark 060221.
        else:
            # Used for all other purposes.
            header = "Current Display: " 
            self.mode.set_displayMode(disp) # updates the prefs db.
            
        if disp == diDEFAULT:
            #disp = default_display_mode #bruce 041129 to fix bug 21
            prefs = preferences.prefs_context() #mark 050802 to fix bug 799
            disp = prefs.get(defaultDisplayMode_prefs_key, default_display_mode)
        #e someday: if self.display == disp, no actual change needed??
        # not sure if that holds for all init code, so being safe for now.
        self.display = disp
        ##Huaicai 3/29/05: Add the condition to fix bug 477
        if self.mode.modename == 'COOKIE':
            self.win.dispbarLabel.setText("    ")
        else:    
            #self.win.dispbarLabel.setText( "Default Display: " + dispLabel[disp] )
            self.win.dispbarLabel.setText( header + dispLabel[disp] )
        #bruce 050415: following should no longer be needed
        # (and it wasn't enough, anyway, since missed mols in non-current parts;
        #  see comments in chunk.py about today's bugfix in molecule.draw for
        #  bug 452 item 15)
        ## for mol in self.assy.molecules:
        ##     if mol.display == diDEFAULT: mol.changeapp(1)
        return

    def setZoomFactor(self, zFactor):
            self.zoomFactor = zFactor
    def getZoomFactor(self):
            return self.zoomFactor    
            
    def gl_update_duration(self, new_part=False):
        '''Redraw GLPane and update the repaint duration variable <self._repaint_duration>
        used by animateToView() to compute the proper number of animation frames.
        Redraws the GLPane twice if <new_part> is True and only saves the repaint 
        duration of the second redraw.  This is needed in the case of drawing a newly opened part,
        which takes much longer to draw the first time than the second (or thereafter).
        '''
        
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
        self._last_few_repaint_times.append( self._repaint_duration)
        self._last_few_repaint_times = self._last_few_repaint_times[-5:] # keep at most the last five times
        
        #if new_part:
        #    print "repaint duration = ", self._repaint_duration
        #print "repaint duration = ", self._repaint_duration
        
        return
        

    _needs_repaint = 1 #bruce 050516 experiment -- initial value is true
    
    def gl_update(self): #bruce 050127
        """External code should call this when it thinks the GLPane needs
        redrawing, rather than directly calling paintGL, unless it really
        knows it needs to wait until the redrawing has been finished
        (which should be very rare).
           Unlike calling paintGL directly (which can be very slow for
        large models, and redoes all its work each time it's called),
        this method is ok to call many times during the handling of one
        user event, since this will cause only one call of paintGL, after
        that user event handler has finished.
        """
        self._needs_repaint = 1 #bruce 050516 experiment
        # (To restore the pre-050127 behavior, it would be sufficient to
        # change the next line from "self.update()" to "self.paintGL()".)
        self.update()
            # QWidget.update() method -- ask Qt to call self.paintGL()
            # (via some sort of paintEvent to our superclass)
            # very soon after the current event handler returns
        return

    # default values for instance variables related to glSelectBuffer feature [bruce 050608]
    ## glselect = 0 # whether we're inside a glSelectBuffer call (not presently needed)
    glselect_wanted = 0 # whether the next paintGL should start with a glSelectBuffer call [bruce 050608]
    glselectBufferSize = 10000 # guess, probably overkill, seems to work, no other value was tried
    current_glselect = False #bruce 050616 #doc; might be approx. same as above commented-out "glselect" attr #k
    
    def paintGL(self): #bruce 050127 revised docstring to deprecate direct calls
        """[PRIVATE METHOD -- call gl_update instead!]
        The main screen-drawing function, called internally by Qt when our
        superclass needs to repaint. THIS SHOULD NO LONGER BE CALLED DIRECTLY
        BY EXTERNAL CODE -- CALL gl_update INSTEAD.
           Sets up point of view projection, position, angle.
        Calls draw member fns for everything in the screen.
        """
        # bruce comment 041220: besides our own calls of this function
        # [later: which no longer exist after 050127], it can
        # be called directly from the app.exec_loop() in atom.py; I'm not sure
        # exactly why or under what circumstances, but one case (on Mac) is when you
        # switch back into the app by clicking in the blank part of the model tree
        # (multiple repaints by different routes in that case),
        # or on the window's title bar (just one repaint); another case is when
        # you switch *out* of the app by clicking on some other app's window.
        # Guess: it's a special method name known to the superclass widget.
        # (Presumably the Qt docs spell this out... find out sometime! #k)

        env.after_op() #bruce 050908 [disabled in changes.py, sometime before 060323; probably obs as of 060323; see this date below]

        if not self.initialised: return

        #e Future: it might be good to set standard GL state, e.g. matrixmode, before checking self.redrawGL here,
        # in order to mitigate bugs in other code (re bug 727), but only if the current mode gets to
        # redefine what "standard GL state" means, since some modes which use this flag to avoid standard
        # repaints also maintain some GL state in nonstandard forms. [bruce 050707 comment]
        
        if not self.redrawGL: return

##        if not self._needs_repaint: #bruce 050516 experiment
##            # This probably happens fairly often when Qt calls paintGL but our own code
##            # didn't change anything and therefore didn't call gl_update.
##            # The plan is to return in this case, but until I'm sure that's safe
##            # (and/or know what else needs to be checked, like the GLPane widget size in case that changed),
##            # I'll just print a debug message about the missed chance for an optimization.
##            # (Removed message since it happens a lot, mainly when context menu is put up, window goes bg or fg, etc.
##            #  What we need is a debug pref to turn off repainting then, so we can see if it's needed on each platform.
##            #  Even if it is, we might optimize by somehow painting from the existing buffer
##            # without swapping or clearing it. ###@@@)
##            pass
####            if platform.atom_debug:
####                print_compact_stack("atom_debug: paintGL called with _needs_repaint false; needed?\n  ")

        env.redraw_counter += 1 #bruce 050825
        
        #bruce 050707 (for bond inference -- easiest place we can be sure to update bonds whenever needed)
        #bruce 050717 bugfix: always do this, not only when "self._needs_repaint"; otherwise,
        # after an atomtype change using Build's cmenu, the first redraw (caused by the cmenu going away, I guess)
        # doesn't do this, and then the bad bond (which this routine should have corrected, seeing the atomtype change)
        # gets into the display list, and then even though the bondtype change (set_v6) does invalidate the display list,
        # nothing triggers another gl_update, so the fixed bond is not drawn right away. I suppose set_v6 ought to do its own
        # gl_update, but for some reason I'm uncomfortable with that for now (and even if it did, this bugfix here is
        # probably also needed). And many analogous LL changers don't do that.
        env.post_event_updates( warn_if_needed = False)

#bruce 060326 zapping this, since it caused bug 1759, and I put in a better fix for bugs like 1411 since then
# (in the menu_spec processor in widgets.py). There might be reasons to revive this someday, and ways to avoid 1759 then,
# but it's hard and inefficient and not needed for now.
##        # Fix bugs from missing mouseReleases (like bug 1411) (provided they do a gl_update like that one does),
##        # from model changes during env.post_event_updates(), or from unexpected model changes during the following
##        # repaint, by surrounding this repaint with begin/end checkpoints. We might do the same thing in the model tree, too.
##        # [bruce 060323]
##        flag_and_begin_retval = None # different than (but analogous to) self.__flag_and_begin_retval
##        if self.assy:
##            begin_retval = self.assy.undo_checkpoint_before_command("(redraw)")
##                # this command name "(redraw)" won't be seen (I think) unless there are model changes during the redraw (a bug)
##            flag_and_begin_retval = True, begin_retval

        try:
            self.most_of_paintGL()
        except:
            print_compact_traceback("exception in most_of_paintGL ignored: ")

##        if flag_and_begin_retval:
##            flagjunk, begin_retval = flag_and_begin_retval
##            if self.assy:
##                #k should always be true, and same assy as before... (for more info see same comment elsewhere in this file)
##                self.assy.undo_checkpoint_after_command( begin_retval)

        return # from paintGL
    
    def most_of_paintGL(self): #bruce 060323 split this out of paintGL
        "Do most of what paintGL should do."
        # 20060224 Added fog_test_enable debug pref, can take out if fog is implemented fully.
        from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
        fog_test_enable = debug_pref("Use test fog?", Choice_boolean_False, non_debug = True)
            #e should remove non_debug = True before release!

        if fog_test_enable:
            drawer.setup_fog(125, 170, self.mode.backgroundColor)
            # this next line really should be just before rendering
            # the atomic model itself.  I dunno where that is.
            drawer.enable_fog()
        
        self._needs_repaint = 0 # do this now, even if we have an exception during the repaint

        #k not sure whether next two things are also needed in the split-out standard_repaint [bruce 050617]
        
        self._restore_modelview_stack_depth() #bruce 050608 moved this here (was after _setup_lighting ###k verify that)

        drawer._glprefs.update() #bruce 051126; kluge: have to do this before lighting *and* inside standard_repaint_0
        
        if self.need_setup_lighting \
          or self._last_glprefs_data_used_by_lights != drawer.glprefs_data_used_by_setup_standard_lights() \
          or debug_pref("always setup_lighting?", Choice_boolean_False):
            #bruce 060415 added debug_pref("always setup_lighting?"), in GLPane and ThumbView [KEEP DFLTS THE SAME!!];
            # using it makes specularity work on my iMac G4,
            # except for brief periods as you move mouse around to change selobj (also observed on G5, but less frequently I think).
            # BTW using this (on G4) has no effect on whether "new wirespheres" is needed to make wirespheres visible.
            #
            # (bruce 051126 added override_light_specular part of condition)
            # I don't know if it matters to avoid calling this every time...
            # in case it's slow, we'll only do it when it might have changed.
            self.need_setup_lighting = False # set to true again if setLighting is called
            self._setup_lighting()

        if trans_feature: # if we're top glpane and doing trans feature
            part = self.part #e correct? might worry if not same as self.assy.part
            if platform.atom_debug and part is not self.assy.part:
                print "atom_debug: glpane redraw sees different self.part %r and self.assy.part %r" % (self.part,self.assy.part)
            topnode = part.topnode
            try:
                import demo_trans
                reload(demo_trans)
                rendertop = demo_trans.translate(topnode, self)
            except:
                print_compact_traceback( "glpane redraw: ignoring exception in demo_trans (using untrans form): ")
                    #e improve if module missing, or don't commit
                self.standard_repaint()
            else:
                # rendertop is the actual nodes to draw... no, not enough, need the modified render loop too... ####e
                # or can that just be inserted into the nodes for use when you draw them? if so, they also need to encode the
                # standard render loop! ie a call of standard_repaint (and self's other attrs) need passing in. well we did pass self!
                # is that enough? if so, then right now, rather than std repaint we would just call rendertop.draw! (when no exc above)
                self.rendertop = rendertop # will be needed later for mouse-event processing, maybe more ###@@@
                rendertop.draw(self, self.display)
            pass
        else:
            self.standard_repaint()

        if fog_test_enable:
            # this next line really should be just after rendering
            # the atomic model itself.  I dunno where that is.
            drawer.disable_fog()

        glFlush()
        ##self.swapBuffers()  ##This is a redundant call, Huaicai 2/8/05
        
        return # from most_of_paintGL

    # ==
    
    special_topnode = None #bruce 050627 only used experimentally so far

    # The following behavior (in several methods herein) related to wants_gl_update
    # should probably also be done in ThumbViews
    # if they want to get properly updated when graphics prefs change. [bruce 050804 guess] ####@@@@
    
    wants_gl_update = True #bruce 050804
        # this is set to True after we redraw, and to False by the following method

    def wants_gl_update_was_True(self): #bruce 050804
        """Outside code should call this if it changes what our redraw would draw,
        and then sees self.wants_gl_update being true,
        if it might not otherwise call self.gl_update
        (which is also ok to do, but might be slower -- whether it's actually slower is not known).
           This can also be used as an invalidator for passing to self.end_tracking_usage().
        """
        self.wants_gl_update = False
        self.gl_update()
    
    def standard_repaint(self, special_topnode = None): #bruce 050617 split this out, added arg
        ###e not sure of name or exact role; might be called on proxy for subrect?
        """#doc... this trashes both gl matrices! caller must push them both if it needs the current ones.
        this routine sets its own matrixmode but depends on other gl state being standard when entered.
        """
        self.special_topnode = special_topnode # this will be detected by assy.draw()
        match_checking_code = self.begin_tracking_usage() #bruce 050806
        try:
            try:
                self.standard_repaint_0()
            except:
                print "exception in standard_repaint_0 (being reraised)"
                    # we're not restoring stack depths here, so this will mess up callers, so we'll reraise;
                    # so the caller will print a traceback, thus we don't need to print one here. [bruce 050806]
                raise
        finally:
            self.wants_gl_update = True #bruce 050804
            self.special_topnode = None #k or old one??
            self.end_tracking_usage( match_checking_code, self.wants_gl_update_was_True ) # same invalidator even if exception
        return

    def standard_repaint_0(self):
        drawer._glprefs.update() #bruce 051126 (so prefs changes do gl_update when needed)
            # (kluge: have to do this before lighting *and* inside standard_repaint_0)
        c = self.mode.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT )
            #e if stencil clear is expensive, we could optim and only do it when needed [bruce ca. 050615]

        # "Blue Sky" is the only gradient supported in A7.  Mark 05
        if self.mode.backgroundGradient:
            vtColors = (bluesky)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            drawer.drawFullWindow(vtColors)

        aspect = (self.width + 0.0)/(self.height + 0.0)
        vdist = 6.0 * self.scale
        self.vdist = vdist #bruce 050616 new feature (storing vdist in self), not yet used where it ought to be
        
        self._setup_modelview( vdist)
            #bruce 050608 moved modelview setup here, from just before the mode.Draw call

        # if GL_SELECT pass is needed (for hit test of objects with mouse), do it first.
        ###e note: if any objects moved since they were last rendered, this hit-test will still work (using their new posns),
        # but the later depth comparison (below) might not work right. See comments there for details.
        self.glselect_dict.clear()
            # this will be filled iff we do a gl_select draw,
            # then used only in the same paintGL call to alert some objects they might be the one

        if self.selobj is not None: #bruce 050702 part of fixing bug 716 (and possibly 715-5, though that's untested)
            try:
                # this 'try' might not be needed once the following method is fully implemented,
                # but it's good anyway for robustness
                if not self.mode.selobj_still_ok(self.selobj) or self.selobj_hicolor(self.selobj) is None:
                    #bruce 050822 added the selobj_hicolor test
                    self.set_selobj(None)
            except:
                # bug, but for now, don't disallow this selobj in this case
                # (message would be too verbose except for debug version)
                if platform.atom_debug:
                    print_compact_traceback("atom_debug: exception ignored: ")
                pass
            pass
        
        if self.glselect_wanted:
            wX, wY, self.targetdepth = self.glselect_wanted # wX,wY is the point to do the hit-test at
                # targetdepth is the depth buffer value to look for at that point, during ordinary drawing phase
                # (could also be used to set up clipping planes to further restrict hit-test, but this isn't yet done)
                # (Warning: targetdepth could in theory be out of date, if more events come between bareMotion
                #  and the one caused by its gl_update, whose paintGL is what's running now, and if those events
                #  move what's drawn. Maybe that could happen with mousewheel events or (someday) with keypresses
                #  having a graphical effect. Ideally we'd count intentional redraws, and disable this picking in that case.)
            self.wX, self.wY = wX,wY
            self.glselect_wanted = 0
            self.current_glselect = (wX,wY,3,3) #bruce 050615 for use by nodes which want to set up their own projection matrix
            self._setup_projection( aspect, vdist, glselect = self.current_glselect ) # option makes it use gluPickMatrix
                # replace 3,3 with 1,1? 5,5? not sure whether this will matter... in principle should have no effect except speed
            glSelectBuffer(self.glselectBufferSize)
            glRenderMode(GL_SELECT)
            glInitNames()
            ## glPushName(0) # this would be ignored if not in GL_SELECT mode, so do it after we enter that! [no longer needed]
            ## self.glselect = 1
            glMatrixMode(GL_MODELVIEW)
            try:
                self.mode.Draw() # should perhaps optim by skipping chunks based on bbox... don't know if that would help or hurt
                    # note: this might call some display lists which, when created, registered namestack names,
                    # so we need to still know those names!
            except:
                print_compact_traceback("exception in mode.Draw() during GL_SELECT; ignored; restoring modelview matrix: ")
                glMatrixMode(GL_MODELVIEW)
                self._setup_modelview( vdist) ###k correctness of this is unreviewed! ####@@@@
                # now it's important to continue, at least enough to restore other gl state
            self.current_glselect = False
            ###e On systems with no stencil buffer, I think we'd also need to draw selobj here in highlighted form
            # (in case that form is bigger than when it's not highlighted), or (easier & faster) just always pretend
            # it passes the hit test and add it to glselect_dict -- and, make sure to give it "first dibs" for being
            # the next selobj. I'll implement some of this now (untested when no stencil buffer) but not yet all. [bruce 050612]
            obj = self.selobj
            if obj is not None:
                self.glselect_dict[id(obj)] = obj
                    ###k unneeded, if the func that looks at this dict always tries selobj first
                    # (except for a kluge near "if self.glselect_dict", commented on below)
            ## self.glselect = 0
            glFlush()
            hit_records = list(glRenderMode(GL_RENDER))
            ## print "%d hits" % len(hit_records)
            for (near,far,names) in hit_records: # see example code, renderpass.py
                ## print "hit record: near,far,names:",near,far,names
                    # e.g. hit record: near,far,names: 1439181696 1453030144 (1638426L,)
                    # which proves that near/far are too far apart to give actual depth,
                    # in spite of the 1-pixel drawing window (presumably they're vertices
                    # taken from unclipped primitives, not clipped ones).
                if 1:
                    # partial workaround for bug 1527. This can be removed once that bug (in drawer.py)
                    # is properly fixed. This exists in two places -- GLPane.py and modes.py. [bruce 060217]
                    if names and names[-1] == 0:
                        print "%d(g) partial workaround for bug 1527: removing 0 from end of namestack:" % env.redraw_counter, names
                        names = names[:-1]
##                        if names:
##                            print " new last element maps to %r" % env.obj_with_glselect_name.get(names[-1])
                if names:
                    # for now, len is always 0 or 1, i think; if not, best to use only the last element...
                    # tho if we ever support "name/subname paths" we'll probably let first name interpret the remaining ones.
                    ###e in fact, when nodes change projection or viewport for kids, and/or share their kids, they need to
                    # put their own names on the stack, so we'll know how to redraw the kids, or which ones are meant when shared.
                    obj = env.obj_with_glselect_name.get(names[-1]) #k should always return an obj
                    if obj is None:
                        print "bug: obj_with_glselect_name returns None for name %r at end of namestack %r" % (names[-1],names)
                    self.glselect_dict[id(obj)] = obj # now these can be rerendered specially, at the end of mode.Draw
            #e maybe we should now sort glselect_dict by "hit priority" (for depth-tiebreaking), or at least put self.selobj first.
            # (or this could be done lower down, where it's used.)
            
        self._setup_projection( aspect, vdist)

        # In the glselect_wanted case, we now know (in glselect_dict) which objects draw any pixels at the mouse position,
        # but not which one is in front (the near/far info from GL_SELECT has too wide a range to tell us that).
        # So we have to get them to tell us their depth at that point (as it was last actually drawn
            ###@@@dothat for bugfix; also selobj first)
        # (and how it compares to the prior measured depth-buffer value there, as passed in glselect_wanted,
        #  if we want to avoid selecting something when it's obscured by non-selectable drawing in front of it).
        if self.glselect_dict:
            # kluge: this is always the case if self.glselect_wanted was set and self.selobj was set,
            # since selobj is always stored in glselect_dict then; if not for that, we might need to reset
            # selobj to None here for empty glselect_dict -- not sure, not fully analyzed. [bruce 050612]
            newpicked = self.preDraw_glselect_dict() # retval is new mouseover object, or None ###k verify
            ###e now tell this obj it's picked (for highlighting), which might affect how the main draw happens.
            # or, just store it so code knows it's there, and (later) overdraw it for highlighting.
            self.set_selobj( newpicked, "newpicked")
            ###e we'll probably need to notify some observers that selobj changed (if in fact it did). ###@@@
            ## env.history.statusbar_msg("%s" % newpicked) -- messed up by depmode "click to do x" msg
        
        # otherwise don't change prior selobj -- we have a separate system to set it back to None when needed
        # (which has to be implemented in the bareMotion routines of client modes -- would self.bareMotion be better? ###@@@ review)
        
        # draw according to mode
        glMatrixMode(GL_MODELVIEW) # this is assumed within Draw methods [bruce 050608 comment]
        self.mode.Draw()

        # highlight selobj if necessary -- we redraw it now (though it was part of
        # what was just drawn above) for two reasons:
        # - it might be in a display list in non-highlighted form (and if so, the above draw used that form);
        # - we need to draw it into the stencil buffer too, so mode.bareMotion can tell when mouse is still over it.
        if self.selobj is not None:
            # draw the selobj as highlighted, and make provisions for fast test
            # (by external code) of mouse still being over it (using stencil buffer)

            # first gather info needed to know what to do -- highlight color (and whether to draw that at all)
            # and whether object might be bigger when highlighted (affects whether depth write is needed now).
            hicolor = self.selobj_hicolor( self.selobj) #bruce 050822 revised this; ###@@@ should record it from earlier test above
            # if that is None, should we act as if selobj is not still_ok?
            # guess: yes, but related code needs review.
            # I think I've now effectively implemented this separately, next to the still_ok test above.
            # [bruce 050822 comment]
            if hicolor is None:
                if platform.atom_debug:
                    print "atom_debug: probable bug: self.selobj_hicolor( self.selobj) is None for %r" % self.selobj #bruce 050822
            highlight_might_be_bigger = True # True is always ok; someday we might let some objects tell us this can be False

            # color-writing is needed here, iff the mode asked for it, for this selobj.
            highlight_into_color = (hicolor is not None)

            if highlight_into_color:
                # depth-writing is needed here, if highlight might be drawn in front of not-yet-drawn transparent surfaces
                # (like Build mode water surface) -- otherwise they will look like they're in front of some of the highlighting
                # even though they're not. (In principle, the preDraw_glselect_dict call above needs to know whether this depth
                # writing occurred ###doc why. Probably we should store it into the object itself... ###@@@ review, then doit
                highlight_into_depth = highlight_might_be_bigger
            else:
                highlight_into_depth = False ###@@@ might also need to store 0 into obj...see discussion above

            if not highlight_into_depth:
                glDepthMask(GL_FALSE) # turn off depth writing (but not depth test)
            if not highlight_into_color:
                glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE) # don't draw color pixels
                        
            # Note: stencil buffer was cleared earlier in this paintGL call.
            glStencilFunc(GL_ALWAYS, 1, 1)
                # These args make sure stencil test always passes, so color is drawn if we want it to be,
                # and so we can tell whether depth test passes in glStencilOp (even if depth *writing* is disabled ###untested);
                # this also sets reference value of 1 for use by GL_REPLACE.
                # (Args are: func to say when drawing-test passes; ref value; comparison mask.
                #  Warning: Passing -1 for reference value, to get all 1's, does not work -- it makes ref value 0!)
            glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
                # turn on stencil-buffer writing based on depth test
                # (args are: what to do on fail, zfail, zpass (see OpenGL "red book" p. 468))
            glEnable(GL_STENCIL_TEST)
                # this enables both aspects of the test: effect on drawing, and use of stencil op (I think #k);
                # apparently they can't be enabled separately
            ##print glGetIntegerv( GL_STENCIL_REF)
            
            # Now "translate the world" slightly closer to the screen,
            # to ensure depth test passes for appropriate parts of highlight-drawing
            # even if roundoff errors would make it unreliable to just let equal depths pass the test.
            # The amount of translation is a guess (ideally it should be just enough to achieve the mentioned purpose).
            # (Note: In principle, this motion towards the screen needs to be accounted for when testing depths in
            #  preDraw_glselect_dict (and we might want to store it on the object itself as a reliable record of whether
            #  it happened and for which object). In practice, as long as the stencil optim works, this isn't needed,
            #  and it's not yet implemented. This is predicted to result in highlight flickering if no stencil bits are
            #  available. ###e should fix sometime, if that ever happens.)
            
            glMatrixMode(GL_PROJECTION) # prepare to "translate the world"
            glPushMatrix() # could avoid using another matrix-stack-level if necessary, by untranslating when done
            glTranslatef(0.0, 0.0, +0.01) # move the world a bit towards the screen
                # (this works, but someday verify sign is correct in theory #k)
            glMatrixMode(GL_MODELVIEW) # probably required!
            
            ####@@@@ TODO -- rename draw_in_abs_coords and make it imply highlighting so obj knows whether to get bigger
            # (note: having it always draw selatoms bigger, as if highlighted, as it does now, would probably be ok in hit-test,
            #  since false positives in hit test are ok, but this is not used in hit test; and it's probably wrong in depth-test
            #  of glselect_dict objs (where it *is* used), resulting in "premonition of bigger size" when hit test passed... ###bug);
            # make provisions elsewhere for objs "stuck as selobj" even if tests to retain that from stencil are not done
            # (and as optim, turn off stencil drawing then if you think it probably won't be needed after last draw you'll do)
            
            self.selobj.draw_in_abs_coords(self, hicolor or black) ###@@@ test having color writing disabled here, does stencil still happen??
            
            # restore gl state (but don't do unneeded OpenGL ops in case that speeds it up somehow)
            if not highlight_into_depth:
                glDepthMask(GL_TRUE)
            if not highlight_into_color:
                glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)                
            glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
                # no need to undo glStencilFunc state, I think -- whoever cares will set it up again
                # when they reenable stenciling.
            glDisable(GL_STENCIL_TEST)
            
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW) #k maybe not needed

        self.mode.Draw_after_highlighting() # e.g. draws water surface in Build mode

        ###@@@ move remaining items back into caller? sometimes yes sometimes no... need to make them more modular... [bruce 050617]
        
        # let parts (other than the main part) draw a text label, to warn
        # the user that the main part is not being shown [bruce 050408]
        try:
            self.part.draw_text_label(self)
        except:
            if platform.atom_debug:
                print_compact_traceback( "atom_debug: exception in self.part.draw_text_label(self): " )
            pass # if it happens at all, it'll happen too often to bother users with an error message
        
        # draw coordinate-orientation arrows at upper right corner of glpane
        if env.prefs[displayCompass_prefs_key]:
            self.drawcompass(aspect) #bruce 050608 moved this here, and rewrote it to behave then

        glMatrixMode(GL_MODELVIEW) #bruce 050707 precaution in case drawing code outside of paintGL forgets to do this
            # (see discussion in bug 727, which was caused by that)
            # (it might also be good to set mode-specific standard GL state before checking self.redrawGL in paintGL #e)

        return # from standard_repaint_0 (which is the central submethod of paintGL)
    
    def selobj_hicolor(self, obj): #bruce 050822 split this out
        """If obj was to be highlighted as selobj (whether or not it's presently self.selobj),
        what would its highlight color be?
        Or return None if obj should not be allowed as selobj.
        """
        try:
            hicolor = self.mode.selobj_highlight_color( obj) #e should implem noop version in basicMode [or maybe i did]
            # mode can decide whether selobj should be highlighted (return None if not), and if so, in what color
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: selobj_highlight_color exception for %r: " % obj)
            hicolor = None #bruce 050822 changed this from LEDon to None
        return hicolor
    
    selobj = None #bruce 050609

    def set_selobj(self, selobj, why = "why?"):
        if selobj is not self.selobj:
            #bruce 050702 partly address bug 715-3 (the presently-broken Build mode statusbar messages).
            # Temporary fix, since Build mode's messages are better and should be restored.
            if selobj is not None:
                try:
                    try:
                        #bruce 050806 let selobj control this
                        method = selobj.mouseover_statusbar_message # only defined for atoms, for now
                    except AttributeError:
                        msg = "%s" % (selobj,)
                    else:
                        msg = method()
                except:
                    msg = "<exception in selobj statusbar message code>"
            else:
                msg = " "
            env.history.statusbar_msg(msg)
        self.selobj = selobj
        #e notify some observers?
        return

    def preDraw_glselect_dict(self): #bruce 050609
        # We need to draw glselect_dict objects separately, so their drawing code runs now rather than in the past
        # (when some display list was being compiled), so they can notice they're in that dict.
        # We also draw them first, so that the nearest one (or one of them, if there's a tie)
        # is sure to update the depth buffer. (Then we clear it so that this drawing doesn't mess up
        # later drawing at the same depth.)
        # (If some mode with special drawing code wants to join this system, it should be refactored
        #  to store special nodes in the model which can be drawn in the standard way.)
        glMatrixMode(GL_MODELVIEW)
        glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE) # optimization -- don't draw color pixels (depth is all we need)
        newpicked = None # in case of errors, and to record found object
        # here we should sort the objs to check the ones we most want first (esp selobj)...
        #bruce 050702 try sorting this, see if it helps pick bonds rather than invis selatoms -- it seems to help.
        # This removes a bad side effect of today's earlier fix of bug 715-1.
        objects = self.glselect_dict.values()
        items = [] # (order, obj) pairs, for sorting objects
        for obj in objects:
            if obj is self.selobj:
                order = 0
            elif obj.__class__ is Bond:
                order = 1
            else:
                order = 2
            items.append((order, obj))
        items.sort()
        for orderjunk, obj in items:
            try:
                method = obj.draw_in_abs_coords
            except AttributeError:
                print "bug? ignored: %r has no draw_in_abs_coords method" % (obj,)
                print "   items are:", items
            else:
                try:
                    method(self, white) # draw depth info (color doesn't matter since we're not drawing pixels)
                        #bruce 050822 changed black to white in case some draw methods have boolean-test bugs for black (unlikely)
                        ###@@@ in principle, this needs bugfixes; in practice the bugs are tolerable in the short term
                        # (see longer discussion in other comments):
                        # - if no one reaches target depth, or more than one does, be smarter about what to do?
                        # - try current selobj first [this is done, as of 050702],
                        #   or give it priority in comparison - if it passes be sure to pick it
                        # - be sure to draw each obj in same way it was last drawn, esp if highlighted:
                        #    maybe drawn bigger (selatom)
                        #    moved towards screen
                    newpicked = self.check_target_depth( obj)
                        # returns obj or None -- not sure if that should be guaranteed [bruce 050822 comment]
                    if newpicked is not None:
                        break
                except:
                    print_compact_traceback("exception in %r.draw_in_abs_coords ignored: " % (obj,))
        ##e should check depth here to make sure it's near enough but not too near
        # (if too near, it means objects moved, and we should cancel this pick)
        glClear(GL_DEPTH_BUFFER_BIT) # prevent those predraws from messing up the subsequent main draws
        glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
        self.glselect_dict.clear() #k needed? even if not, seems safer this way.
            # do this now to avoid confusing the main draw methods,
            # in case they check this dict to decide whether they're
            # being called by draw_in_abs_coords
            # [which would be deprecated! but would work, not counting display lists.]
        #bruce 050822 new feature: objects which had no highlight color should not be allowed in self.selobj
        # (to make sure they can't be operated on without user intending this),
        # though they should still obscure other objects.
        if newpicked is not None:
            hicolor = self.selobj_hicolor( newpicked)
            if hicolor is None:
                newpicked = None
        else:
            #bruce 060217 debug code re bug 1527. Not sure only happens on a bug, so using atom_debug.
            # (But I couldn't yet cause this to be printed while testing that bug.)
            #bruce 060224 disabling it since it's happening all the time when hover-highlighting in Build
            # (though I didn't reanalyze my reasons for thinking it might be a bug, so I don't know if it's a real one or not).
            if 0 and platform.atom_debug:
                print "atom_debug: newpicked is None -- bug? items are:", items
        return newpicked # might be None in case of errors

    def check_target_depth(self, candidate): #bruce 050609; tolerance revised 050702
        """[private helper method]
           WARNING: docstring is obsolete -- no newpicked anymore, retval details differ: ###@@@
        Candidate is an object which drew at the mouse position during GL_SELECT drawing mode
        (using the given gl_select name), and which (1) has now noticed this, via its entry in self.glselect_dict
        (which was made when GL_SELECT mode was exited; as of 050609 this is in the same paintGL call as we're in now),
        and (2) has already drawn into the depth buffer during normal rendering (or an earlier rendering pass).
        (It doesn't matter whether it's already drawn into the color buffer when it calls this method.)
           We should read pixels from the depth buffer (after glFlush)
        to check whether it has just reached self.targetdepth at the appropriate point,
        which would mean candidate is the actual newly picked object.
           If so, record this fact and return True, else return False.
        We might quickly return False (checking nothing) if we already returned True in the same pass,
        or we might read pixels anyway for debugging or assertions.
           It's possible to read a depth even nearer than targetdepth, if the drawing passes round
        their coordinates differently (as the use of gluPickMatrix for GL_SELECT is likely to do),
        or if events between the initial targetdepth measurement and this redraw tell any model objects to move.
        Someday we should check for this.
        """
        glFlush()
        wX, wY = self.wX, self.wY
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        newdepth = wZ[0][0]
        targetdepth = self.targetdepth
        ####@@@@ here we could effectively move selobj forwards... warning: worry about scales of coord systems in doing that...
        # due to that issue it is probably be easier to fix this when drawing it, instead
        if newdepth <= targetdepth + 0.0001: # use fudge factor in case of roundoff errors
            # [bruce 050702: 0.000001 was not enough! 0.00003 or more was needed, to properly highlight some bonds
            #  which became too hard to highlight after today's initial fix of bug 715-1.]
            #e could check for newdepth being < targetdepth - 0.002 (error), but best
            # to just let caller do that (NIM), since we would often not catch this error anyway,
            # since we're turning into noop on first success
            # (no choice unless we re-cleared depth buffer now, which btw we could do... #e).
            ## print "target depth reached by",candidate,newdepth , targetdepth
            return candidate
                # caller should not call us again without clearing depth buffer,
                # otherwise we'll keep returning every object even if its true depth is too high
        ## print "target depth NOT reached by",candidate,newdepth , targetdepth
        return None

    def _restore_modelview_stack_depth(self): #bruce 050608 split this out
        "restore GL_MODELVIEW_STACK_DEPTH to 1, if necessary"
        #bruce 040923: I'd like to reset the OpenGL state
        # completely, here, incl the stack depths, to mitigate some
        # bugs. How??  Note that there might be some OpenGL init code
        # earlier which I'll have to not mess up. Incl displaylists in
        # drawer.setup.  What I ended up doing is just to measure the
        # stack depth and pop it 0 or more times to make the depth 1.
        #   BTW I don't know for sure whether this causes a significant speed
        # hit for some OpenGL implementations (esp. X windows)...
        # test sometime. #e
        glMatrixMode(GL_MODELVIEW)
        
        depth = glGetInteger(GL_MODELVIEW_STACK_DEPTH)
        # this is normally 1
        # (by experiment, qt-mac-free-3.3.3, Mac OS X 10.2.8...)
        if depth > 1:
            print "apparent bug: glGetInteger(GL_MODELVIEW_STACK_DEPTH) = %r in GLPane.paintGL" % depth
            print "workaround: pop it back to depth 1"
            while depth > 1:
                    depth -= 1
                    glPopMatrix()
            newdepth = glGetInteger(GL_MODELVIEW_STACK_DEPTH)
            if newdepth != 1:
                    print "hmm, after depth-1 pops we should have reached depth 1, but instead reached depth %r" % newdepth
            pass
        return

    def _setup_modelview(self, vdist): #bruce 050608 split this out; 050615 added explanatory comments
        "set up modelview coordinate system"
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef( 0.0, 0.0, - vdist)
            # [bruce comment 050615]
            # translate coords for drawing, away from eye (through screen and beyond it) by vdist;
            # this places origin at desired position in eyespace for "center of view" (and for center of trackball rotation).
            
            # bruce 041214 comment: some code assumes vdist is always 6.0 * self.scale
            # (e.g. eyeball computations, see bug 30), thus has bugs for aspect < 1.0.
            # We should have glpane attrs for aspect, w_scale, h_scale, eyeball,
            # clipping planes, etc, like we do now for right, up, etc. ###e

        q = self.quat 
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z) # rotate those coords by the trackball quat
        glTranslatef( self.pov[0], self.pov[1], self.pov[2]) # and translate them by -cov, to bring cov (center of view) to origin
        return

    def _setup_projection(self, aspect, vdist, glselect = False): #bruce 050608 split this out; 050615 revised docstring
        """Set up standard projection matrix contents using aspect, vdist, and some attributes of self.
        (Warning: leaves matrixmode as GL_PROJECTION.)
        Optional arg glselect should be False (default) or a 4-tuple (to prepare for GL_SELECT picking).
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        scalezoom = self.scale * self.zoomFactor #bruce 050608 used this to clarify following code
        near, far = self.near, self.far

        if glselect:
            x,y,w,h = glselect
            gluPickMatrix(
                    x,y,
                    w,h,
                    glGetIntegerv( GL_VIEWPORT ) #k is this arg needed? it might be the default...
            )
         
        if self.ortho:
            glOrtho( - scalezoom * aspect, scalezoom * aspect,
                     - scalezoom,          scalezoom,
                       vdist * near, vdist * far )
        else:
            glFrustum( - scalezoom * near * aspect, scalezoom * near * aspect,
                       - scalezoom * near,          scalezoom * near,
                         vdist * near, vdist * far)
        return

    def drawcompass(self, aspect):
        """Draw the "compass" (the perpendicular colored arrows showing orientation of model coordinates)
        in a corner of the GLPane specified by preference variables.
        No longer assumes a specific glMatrixMode, but sets it to GL_MODELVIEW on exit.
        No longer trashes either matrix, but does require enough GL_PROJECTION stack depth
        to do glPushMatrix on it (though the guaranteed depth for that stack is only 2).
        """
        #bruce 050608 improved behavior re GL state requirements and side effects; 050707 revised docstring accordingly.
        #mark 0510230 switched Y and Z colors.  Now X = red, Y = green, Z = blue, standard in all CAD programs.
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity() #k needed?
        
        # Set compass position using glOrtho
        if self.compassPosition == UPPER_RIGHT:
            glOrtho(-50*aspect, 5.5*aspect, -50, 5.5,  -5, 500) # Upper Right
        elif self.compassPosition == UPPER_LEFT:
            glOrtho(-5*aspect, 50.5*aspect, -50, 5.5,  -5, 500) # Upper Left
        elif self.compassPosition == LOWER_LEFT:
            glOrtho(-5*aspect, 50.5*aspect, -5, 50.5,  -5, 500) # Lower Left
        else:
            glOrtho(-50*aspect, 5.5*aspect, -5, 50.5,  -5, 500) # Lower Right
        
        q = self.quat
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)
        glEnable(GL_COLOR_MATERIAL)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDisable(GL_CULL_FACE)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # X Arrow (Red)      
        glePolyCone([[-1,0,0], [0,0,0], [4,0,0], [3,0,0], [5,0,0], [6,0,0]],
                    [[0,0,0], [1,0,0], [1,0,0], [.5,0,0], [.5,0,0], [0,0,0]],
                    [.3,.3,.3,.75,0,0])
        
        # Y Arrow (Green) 
        glePolyCone([[0,-1,0], [0,0,0], [0,4,0], [0,3,0], [0,5,0], [0,6,0]],
                    [[0,0,0], [0,.9,0], [0,.9,0], [0,.4,0], [0,.4,0], [0,0,0]],
                    [.3,.3,.3,.75,0,0])
        
        # Z Arrow (Blue)
        glePolyCone([[0,0,-1], [0,0,0], [0,0,4], [0,0,3], [0,0,5], [0,0,6]],
                    [[0,0,0], [0,0,1], [0,0,1], [0,0,.4], [0,0,.4], [0,0,0]],
                    [.3,.3,.3,.75,0,0])
                    
        glEnable(GL_CULL_FACE)
        glDisable(GL_COLOR_MATERIAL)
           
        ##Adding "X, Y, Z" text labels for Axis. By test, the following code will get
        # segmentation fault on Mandrake Linux 10.0 with libqt3-3.2.3-17mdk
        # or other 3.2.* versions, but works with libqt3-3.3.3-26mdk. Huaicai 1/15/05

        if env.prefs[displayCompassLabels_prefs_key]: ###sys.platform in ['darwin', 'win32']:
                glDisable(GL_LIGHTING)
                glDisable(GL_DEPTH_TEST)
                ## glPushMatrix()
                font = QFont( QString("Helvetica"), 12)
                self.qglColor(QColor(200, 75, 75)) # Dark Red
                self.renderText(5.3, 0.0, 0.0, QString("x"), font)
                self.qglColor(QColor(25, 100, 25)) # Dark Green
                self.renderText(0.0, 4.8, 0.0, QString("y"), font)
                self.qglColor(QColor(50, 50, 200)) # Dark Blue
                self.renderText(0.0, 0.0, 5.0, QString("z"), font)
                ## glPopMatrix()
                glEnable(GL_DEPTH_TEST)
                glEnable(GL_LIGHTING)

        #bruce 050707 switched order to leave ending matrixmode in standard state, GL_MODELVIEW
        # (though it doesn't matter for present calling code; see discussion in bug 727)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        return
           
    def resizeGL(self, width, height):
        """Called by QtGL when the drawing window is resized.
        """
        self.width = width
        self.height = height
           
	## glViewport(10, 15, (self.width-10)/2, (self.height-15)/3) # (guess: just an example of using a smaller viewport)
        glViewport(0, 0, self.width, self.height)
        if not self.initialised:
            self.initialised = 1
        self.trackball.rescale(width, height)
        self.gl_update()
        return
           
    def xdump(self):
        """for debugging"""
        print " pov: ", self.pov
        print " quat ", self.quat

    def __str__(self):
        return "<GLPane " + self.name + ">"

    def makemenu(self, menu_spec):
        # this overrides the one from DebugMenuMixin (with the same code), but that's ok,
        # since we want to be self-contained in case someone later removes that mixin class;
        # this method is called by our modes to make their context menus.
        # [bruce 050418 comment]
        return makemenu_helper(self, menu_spec)
    
    def debug_menu_items(self): #bruce 050515 experiment
        "overrides method from DebugMenuMixin"
        super = DebugMenuMixin
        usual = super.debug_menu_items(self)
            # list of (text, callable) pairs, None for separator
        ours = list(usual)
        try:
            # submenu for available custom modes [bruce 050515]
            #e should add special text to the item for current mode (if any) saying we'll reload it
            modemenu = []
            for modename, modefile in self.custom_mode_names_files():
                modemenu.append(( modename,
                                  lambda arg1 = None, arg2 = None, modename = modename, modefile = modefile:
                                    self.enter_custom_mode(modename, modefile) # not sure how many args are passed
                                ))
            if modemenu:
                ours.append(("custom modes", modemenu))
        except:
            print_compact_traceback("exception ignored: ")
        return ours

    def custom_mode_names_files(self):
        modes_dir = os.path.join( self.win.tmpFilePath, "Modes")
        if not os.path.isdir( modes_dir):
            return []
        res = []
        for file in os.listdir( modes_dir):
            if file.endswith('.py') and '-' not in file:
                modename, ext = os.path.splitext(file)
                modefile = os.path.join( modes_dir, file)
                res.append(( modename, modefile ))
        return res

    def enter_custom_mode( self, modename, modefile): #bruce 050515 experiment
        fn = modefile
        if not os.path.exists(fn):
            env.history.message("should never happen: file does not exist: [%s]" % fn)
            return
        dir, file = os.path.split(fn)
        base, ext = os.path.splitext(file)
        ## modename = base
        ###e need better way to import from this specific file!
        # (Like using an appropriate function in the import-related Python library module.)
        # This kluge is not protected against weird chars in base.
        if dir not in sys.path:
            sys.path.append(dir)
        exec("import %s as _module" % (base,)) ###e use the platform or debug func to limit this to GPL versions
        reload(_module)
        exec("from %s import %s as _modeclass" % (base,base))
        modeobj = _modeclass(self) # this should put it into self.modetab under the name defined in the mode module
        self.modetab[modename] = modeobj # also put it in under this name, if different [### will this cause bugs?]
        self.setMode(modename)
        return

    pass # end of class GLPane

def typecheckViewArgs(q2, s2, p2, z2): #mark 060128
    '''Typecheck the view arguments quat q2, scale s2, pov p2, and zoom factor z2
    used by GLPane.snapToView() and GLPane.animateToView().
    '''
    assert isinstance(q2, Q)
    assert isinstance(s2, float)
    assert len(p2) == 3
    assert isinstance(p2[0], float)
    assert isinstance(p2[1], float)
    assert isinstance(p2[2], float)
    assert isinstance(z2, float)
    return

# end
