# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
ThumbView.py - a simpler OpenGL widget, similar to GLPane
(which unfortunately has a lot of duplicated but partly modified
code copied from GLPane)

@author: Huaicai
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""

from Numeric import dot

from OpenGL.GL import GL_NORMALIZE
from OpenGL.GL import glEnable
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import glClearColor
from OpenGL.GL import GL_COLOR_BUFFER_BIT
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import glClear
from OpenGL.GL import GL_STENCIL_INDEX
from OpenGL.GL import glReadPixelsi
from OpenGL.GL import GL_DEPTH_COMPONENT
from OpenGL.GL import glReadPixelsf
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glSelectBuffer
from OpenGL.GL import GL_SELECT
from OpenGL.GL import glRenderMode
from OpenGL.GL import glInitNames
from OpenGL.GL import GL_CLIP_PLANE0
from OpenGL.GL import glClipPlane
from OpenGL.GL import GL_RENDER
from OpenGL.GL import glFlush
from OpenGL.GL import GL_STENCIL_BUFFER_BIT
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_ALWAYS
from OpenGL.GL import glStencilFunc
from OpenGL.GL import GL_REPLACE
from OpenGL.GL import GL_TRUE
from OpenGL.GL import glDepthMask
from OpenGL.GL import GL_KEEP
from OpenGL.GL import glStencilOp
from OpenGL.GL import GL_STENCIL_TEST
from OpenGL.GL import glDisable
from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glDepthFunc
from OpenGL.GL import GL_LEQUAL

from OpenGL.GLU import gluUnProject

from PyQt4.Qt import Qt

from geometry.VQT import V, Q, A
from graphics.drawing.drawers import drawFullWindow
from graphics.drawing.gl_lighting import _default_lights
from graphics.drawing.gl_lighting import setup_standard_lights
from model.assembly import Assembly
import foundation.env as env
from utilities import debug_flags


from utilities.debug import print_compact_traceback

from utilities.constants import diTrueCPK
from utilities.constants import gray
from utilities.constants import bluesky, eveningsky, bg_seagreen, bgEVENING_SKY, bgSEAGREEN
from utilities.constants import GL_FAR_Z
from utilities.prefs_constants import bondpointHighlightColor_prefs_key
from utilities.prefs_constants import backgroundGradient_prefs_key
from utilities.prefs_constants import backgroundColor_prefs_key

from foundation.Group import Group
from model.chem import Atom
from model.elements import Singlet
from model.chunk import Chunk

from operations.pastables import find_hotspot_for_pasting

from graphics.widgets.GLPane_minimal import GLPane_minimal
from platform_dependent.PlatformDependent import fix_event_helper

class ThumbView(GLPane_minimal):
    """
    A simple version of OpenGL widget, which can be used to show a simple
    thumb view of models when loading models or color changing.
    General rules for multiple QGLWidget uses: make sure the rendering context
    is current. Remember makeCurrent() will be called implicitly before any
    initializeGL, resizeGL, paintGL virtual functions call. Ideally, this class
    should coordinate with class GLPane in some ways.
    """
    # Note: classes GLPane and ThumbView share lots of code,
    # which ought to be merged into their common superclass GLPane_minimal
    # [bruce 070914 comment; since then some of it has been merged, some
    #  still needs to be] [I merged a bunch more now -- bruce 080912]

    # class constants and/or default values of instance variables [not sure which are which]

    SIZE_FOR_glSelectBuffer = 500
        # different value from that in GLPane_minimal
        # [I don't know whether this matters -- bruce 071003 comment]

    shareWidget = None #bruce 051212
    always_draw_hotspot = False #bruce 060627

    _always_remake_during_movies = True #bruce 090224

    # default values of subclass-specific constants

    permit_draw_bond_letters = False #bruce 071023, overrides superclass

    def __init__(self, parent, name, shareWidget):
        """
        Constructs an instance of a Thumbview.
        """

        useStencilBuffer = False

        GLPane_minimal.__init__(self, parent, shareWidget, useStencilBuffer)

        self.elementMode = None

        #@@@Add the QGLWidget to the parentwidget's grid layout. This is done
        #here for improving the loading speed. Needs further optimization and
        #a better place to put this code if possible. -- Ninad 20070827
        try:
            parent.gridLayout.addWidget(self, 0, 0, 1, 1)
        except:
            print_compact_traceback("bug: Preview Pane's parent widget doesn't" \
            " have a layout. Preview Pane not added to the layout.")
            pass

        self.picking = False

        self.selectedObj = None

        #This enables the mouse bareMotion() event
        self.setMouseTracking(True)

        # clipping planes, as percentage of distance from the eye
        self.near = 0.66
        self.far = 2.0
        # start in perspective mode
        self.ortho = False #True

        self.scale # make sure superclass set this [bruce 080219]

        # default color and gradient values.
        self.backgroundColor = env.prefs[backgroundColor_prefs_key]
        self.backgroundGradient = env.prefs[ backgroundGradient_prefs_key ]


    def drawModel(self):
        """
        This is an abstract method for drawing self's "model".

        [subclasses which need to draw anything must override this method]
        """
        pass

    def _drawModel_using_DrawingSets(self): #bruce 090219
        """
        """
        def func():
            self.drawModel()
        self._call_func_that_draws_model( func,
                                          drawing_phase = 'main' )
        return

    def drawSelected(self, obj):
        """
        Draw the selected object.

        [subclasses can override this method]
        """
        pass

    def _drawSelected_using_DrawingSets(self, obj): #bruce 090219
        """
        """
        def func():
            self.drawSelected(obj)
        self._call_func_that_draws_model( func,
                                          drawing_phase = 'selobj',
                                          whole_model = False )
            ### REVIEW: should we use _call_func_that_draws_objects instead?
            # That requires passing a part which contains obj,
            # and I don't know for sure whether there is one, or how to find it
            # in all cases. Guess: this is desirable, but not yet essential.
            # [bruce 090219 comment]
        return

    def _get_assy(self): #bruce 080220
        """
        Return the assy which contains all objects we are drawing
        (or None if this is not possible).

        [subclasses must override this method]
        """
        return None

    def __get_assy(self): #bruce 080220
        # this glue method is a necessary kluge so that the following property
        # for self.assy will use a subclass's overridden version of _get_assy
        return self._get_assy()

    assy = property(__get_assy) #bruce 080220, for per-assy glname dict

    def _setup_lighting(self):
        """
        [private method]
        Set up lighting in the model.
        [Called from both initializeGL and paintGL.]
        """
        # note: there is some duplicated code in this method
        # in GLPane_lighting_methods (has more comments) and ThumbView,
        # but also significant differences. Should refactor sometime.
        # [bruce 060415/080912 comment]

        glEnable(GL_NORMALIZE)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        #bruce 060415 moved following from ThumbView.initializeGL to this split-out method...
        #bruce 051212 revised lighting code to share prefs and common code with GLPane
        # (to fix bug 1200 and mitigate bugs 475 and 1158;
        #  fully fixing those would require updating lighting in all ThumbView widgets
        #  whenever lighting prefs change, including making .update calls on them,
        #  and is not planned for near future since it's easy enough to close & reopen them)
        try:
            lights = self.shareWidget._lights #bruce 060415 shareWidget --> self.shareWidget; presumably always failed before that
                ###@@@ will this fix some bugs about common lighting prefs??
        except:
            lights = _default_lights

        setup_standard_lights( lights, self.glprefs)
        return

    def resetView(self):
        """
        Reset the view.

        Subclass can override this method with different <scale>, so call
        this version in the overridden version.
        """
        self.pov = V(0.0, 0.0, 0.0)
        self.quat = Q(1, 0, 0, 0)

    def setBackgroundColor(self, color, gradient):
        """
        Set the background  to 'color' or 'gradient' (Sky Blue).
        """
        self.backgroundColor = color

        # Ninad and I discussed this and decided that the background should always be set to skyblue.
        # This issue has to do with Build mode's water surface introducing inconsistencies
        # with the thumbview background color whenever Build mode's bg color is solid.
        # Change to "if 0:" to have the thubview background match the current mode background.
        # This fixes bug 1229.  Mark 060116
        if 1:
            self.backgroundGradient = env.prefs[ backgroundGradient_prefs_key ]
        else:
            self.backgroundGradient = gradient

    def paintGL(self):
        """
        Called by QtGL when redrawing is needed. For every redraw, color &
        depth butter are cleared, view projection are reset, view location &
        orientation are also reset.
        """
        if not self.initialised:
            return

        self._call_whatever_waits_for_gl_context_current() #bruce 071103

        glDepthFunc( GL_LEQUAL)

        self.setDepthRange_setup_from_debug_pref()
        self.setDepthRange_Normal()

        from utilities.debug_prefs import debug_pref, Choice_boolean_False
        if debug_pref("always setup_lighting?", Choice_boolean_False):
            #bruce 060415 added debug_pref("always setup_lighting?"), in GLPane and ThumbView [KEEP DFLTS THE SAME!!];
            # see comments in GLPane_lighting_methods
            self._setup_lighting() #bruce 060415 added this call

        self.backgroundColor = env.prefs[backgroundColor_prefs_key]
        c = self.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        del c
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.backgroundGradient = env.prefs[ backgroundGradient_prefs_key ]
        if self.backgroundGradient:

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Setting to blue sky (default), but might change to something else
            _bgGradient = bluesky
            if self.backgroundGradient == bgEVENING_SKY:
                _bgGradient = eveningsky
            if self.backgroundGradient == bgSEAGREEN:
                _bgGradient = bg_seagreen

            drawFullWindow(_bgGradient)# gradient color

        self._setup_projection()

        self._setup_modelview()
##        glMatrixMode(GL_MODELVIEW)
##        glLoadIdentity()
##        glTranslatef(0.0, 0.0, - self.vdist)
##        q = self.quat
##        glRotatef(q.angle * 180.0 / math.pi, q.x, q.y, q.z)
##        glTranslatef(self.pov[0], self.pov[1], self.pov[2])

        if self.model_is_valid():
            #bruce 080117 [testing this at start of paintGL to skip most of it]:
            # precaution (perhaps a bugfix); see similar code in GLPane.
            #
            # update, bruce 080220: this may have caused a bug by making this
            # not draw a blank-background graphics area when it has no model.
            # E.g. the partlib has no model when first entered.
            # Fixing this by only not drawing the model itself in that case [UNTESTED].
            # (The GLPane always has a model, so has no similar issue.)
            #
            # I'm not moving the coordinate transforms into this if statement,
            # since I don't know if they might be depended on by non-paintGL
            # drawing (e.g. for highlighting, which btw is called "selection"
            # in some method names and comments in this file). [bruce 080220]
            self._drawModel_using_DrawingSets()

    def mousePressEvent(self, event):
        """
        Dispatches mouse press events depending on shift and
        control key state.
        """
        ## Huaicai 2/25/05. This is to fix item 2 of bug 400: make this rendering context
        ## as current, otherwise, the first event will get wrong coordinates
        self.makeCurrent()

        buttons, modifiers = event.buttons(), event.modifiers()
        #print "Button pressed: ", but

        if 1:
            #bruce 060328 kluge fix of undo part of bug 1775 (overkill, but should be ok) (part 1 of 2)
            import foundation.undo_manager as undo_manager
            main_assy = env.mainwindow().assy
            self.__begin_retval = undo_manager.external_begin_cmd_checkpoint(main_assy, cmdname = "(mmkit)")

        if buttons & Qt.LeftButton:
            if modifiers & Qt.ShiftModifier:
                pass # self.graphicsMode.leftShiftDown(event)
            elif modifiers & Qt.ControlModifier:
                pass # self.graphicsMode.leftCntlDown(event)
            else:
                self.leftDown(event)

        if buttons & Qt.MidButton:
            if modifiers & Qt.ShiftModifier:
                pass # self.graphicsMode.middleShiftDown(event)
            elif modifiers & Qt.ControlModifier:
                pass # self.graphicsMode.middleCntlDown(event)
            else:
                self.middleDown(event)

        if buttons & Qt.RightButton:
            if modifiers & Qt.ShiftModifier:
                pass # self.graphicsMode.rightShiftDown(event)
            elif modifiers & Qt.ControlModifier:
                pass # self.graphicsMode.rightCntlDown(event)
            else:
                pass # self.rightDown(event)

    __begin_retval = None

    def mouseReleaseEvent(self, event):
        """
        Only used to detect the end of a freehand selection curve.
        """
        buttons, modifiers = event.buttons(), event.modifiers()

        #print "Button released: ", but

        if buttons & Qt.LeftButton:
            if modifiers & Qt.ShiftModifier:
                pass # self.leftShiftUp(event)
            elif modifiers & Qt.ControlModifier:
                pass # self.leftCntlUp(event)
            else:
                self.leftUp(event)

        if buttons & Qt.MidButton:
            if modifiers & Qt.ShiftModifier:
                pass # self.graphicsMode.middleShiftUp(event)
            elif modifiers & Qt.ControlModifier:
                pass # self.graphicsMode.middleCntlUp(event)
            else:
                self.middleUp(event)

        if buttons & Qt.RightButton:
            if modifiers & Qt.ShiftModifier:
                pass # self.rightShiftUp(event)
            elif modifiers & Qt.ControlModifier:
                pass # self.rightCntlUp(event)
            else:
                pass # self.rightUp(event)

        if 1:
            #bruce 060328 kluge fix of undo part of bug 1775 (part 2 of 2)
            import foundation.undo_manager as undo_manager
            main_assy = env.mainwindow().assy
            undo_manager.external_end_cmd_checkpoint(main_assy, self.__begin_retval)

        return

    def mouseMoveEvent(self, event):
        """
        Dispatches mouse motion events depending on shift and
        control key state.
        """
        ##self.debug_event(event, 'mouseMoveEvent')
        buttons, modifiers = event.buttons(), event.modifiers()

        if buttons & Qt.LeftButton:
            if modifiers & Qt.ShiftModifier:
                pass # self.leftShiftDrag(event)
            elif modifiers & Qt.ControlModifier:
                pass # self.leftCntlDrag(event)
            else:
                pass # self.leftDrag(event)

        elif buttons & Qt.MidButton:
            if modifiers & Qt.ShiftModifier:
                pass # self.middleShiftDrag(event)
            elif modifiers & Qt.ControlModifier:
                pass # self.middleCntlDrag(event)
            else:
                self.middleDrag(event)

        elif buttons & Qt.RightButton:
            if modifiers & Qt.ShiftModifier:
                pass # self.rightShiftDrag(event)
            elif modifiers & Qt.ControlModifier:
                pass # self.rightCntlDrag(event)
            else:
                pass # self.rightDrag(event)

        else:
            #Huaicai: To fix bugs related to multiple rendering contexts existed in our application.
            # See comments in mousePressEvent() for more detail.
            self.makeCurrent()
            self.bareMotion(event)

    def wheelEvent(self, event):
        buttons, modifiers = event.buttons(), event.modifiers()

        # The following copies some code from basicMode.Wheel, but not yet the call of rescale_around_point,
        # since that is not implemented in this class; it ought to be made a method of a new common superclass
        # of this class and GLPane (and there are quite a few methods of GLPane about which that can be said,
        # some redundantly implemented here and some not).
        # [bruce 060829 comment]
        #
        # update [bruce 070402 comment]:
        # sharing that code would now be a bit more complicated (but is still desirable),
        # since GLPane.rescale_around_point is now best called by basicMode.rescale_around_point_re_user_prefs.
        # The real lesson is that even ThumbViews ought to use some kind of "graphicsMode" (like full-fledged modes,
        # even if some aspects of them would not be used), to handle mouse bindings. But this is likely to be
        # nontrivial since full-fledged modes might have extra behavior that's inappropriate but hard to
        # turn off. So if we decide to make ThumbView zoom compatible with that of the main graphics area,
        # the easiest quick way is just to copy and modify rescale_around_point_re_user_prefs and basicMode.Wheel
        # into this class.

        dScale = 1.0/1200.0
        if modifiers & Qt.ShiftModifier:
            dScale *= 0.5
        if modifiers & Qt.ControlModifier:
            dScale *= 2.0
        self.scale *= 1.0 + dScale * event.delta()
            ### BUG: The scale variable needs to set a limit; otherwise, it will
            # set self.near = self.far = 0.0 because of machine precision,
            # which will cause OpenGL Error. [Huaicai 10/18/04]
            # NOTE: this bug may have been fixed in other defs of wheelEvent.
            # TODO: review, and fix it here too (or, better, use common code).
            # See also the longer comment above in this method.
            # [bruce 080917 addendum]
        self.updateGL()
        return

    def bareMotion(self, event):
        wX = event.pos().x()
        wY = self.height - event.pos().y()

        if self.selectedObj is not None:
            stencilbit = glReadPixelsi(wX, wY, 1, 1, GL_STENCIL_INDEX)[0][0]
            if stencilbit: # If it's the same highlighting object, no display change needed.
                return

        self.updateGL()

        self.selectedObj = self.select(wX, wY)
        self.highlightSelected(self.selectedObj)

        return False # russ 080527

    def leftDown(self, event):
        pass

    def leftUp(self, event):
        pass

    def middleDown(self, event):
        pos = event.pos()
        self.trackball.start(pos.x(), pos.y())
        self.picking = True
        return

    def middleDrag(self, event):
        if self.picking:
            pos = event.pos()
            q = self.trackball.update(pos.x(), pos.y())
            self.quat += q
            self.updateGL()
        return

    def middleUp(self, event):
        self.picking = False
        return

    def select(self, wX, wY):
        """
        Use the OpenGL picking/selection to select any object. Return the
        selected object, otherwise, return None. Restore projection and
        modelview matrices before returning.
        """
        ### NOTE: this code is similar to (and was copied and modified from)
        # GLPane_highlighting_methods.do_glselect_if_wanted, but also differs
        # in significant ways (too much to make it worth merging, unless we
        # decide to merge the differing algorithms as well). It's one of
        # several instances of hit-test code that calls glRenderMode.
        # [bruce 060721/080917 comment]
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        gz = wZ[0][0]

        if gz >= GL_FAR_Z: # Empty space was clicked
            return None

        pxyz = A(gluUnProject(wX, wY, gz))
        pn = self.out
        pxyz -= 0.0002 * pn
            # Note: if this runs before the model is drawn, this can have an
            # exception "OverflowError: math range error", presumably because
            # appropriate state for gluUnProject was not set up. That doesn't
            # normally happen but can happen due to bugs (no known open bugs
            # of that kind).
            # Sometimes our drawing area can become "stuck at gray",
            # and when that happens, the same exception can occur from this line.
            # Could it be that too many accidental mousewheel scrolls occurred
            # and made the scale unreasonable? (To mitigate, we should prevent
            # those from doing anything unless we have a valid model, and also
            # reset that scale when loading a new model (latter is probably
            # already done, but I didn't check). See also the comments
            # in def wheelEvent.) [bruce 080220 comment]
        dp = - dot(pxyz, pn)

        # Save projection matrix before it's changed.
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()

        current_glselect = (wX, wY, 1, 1)
        self._setup_projection(glselect = current_glselect)

        glSelectBuffer(self.SIZE_FOR_glSelectBuffer)
        glRenderMode(GL_SELECT)
        glInitNames()
        glMatrixMode(GL_MODELVIEW)
        # Save model view matrix before it's changed.
        glPushMatrix()

        # Draw model using glRenderMode(GL_SELECT) as set up above
        try:
            glClipPlane(GL_CLIP_PLANE0, (pn[0], pn[1], pn[2], dp))
            glEnable(GL_CLIP_PLANE0)
            self._drawModel_using_DrawingSets()
        except:
            #bruce 080917 fixed predicted bugs in this except clause (untested)
            print_compact_traceback("exception in ThumbView._drawModel_using_DrawingSets() during GL_SELECT; ignored; restoring matrices: ")
            glDisable(GL_CLIP_PLANE0)
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()
            glRenderMode(GL_RENDER)
            return None
        else:
            glDisable(GL_CLIP_PLANE0)
            # Restore model/view matrix
            glPopMatrix()

        # Restore projection matrix and set matrix mode to Model/View
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glFlush()

        hit_records = list(glRenderMode(GL_RENDER))
        ## print "%d hits" % len(hit_records)
        for (near, far, names) in hit_records:
            ## print "hit record: near, far, names:", near, far, names
            # note from testing: near/far are too far apart to give actual depth,
            # in spite of the 1-pixel drawing window (presumably they're vertices
            # taken from unclipped primitives, not clipped ones).
            ### REVIEW: this just returns the first candidate object found.
            # The clip plane may restrict the set of candidates well enough to
            # make sure that's the right one, but this is untested and unreviewed.
            # (And it's just my guess that that was Huaicai's intention in
            #  setting up clipping, since it's not documented. I'm guessing that
            #  the plane is just behind the hitpoint, but haven't confirmed this.)
            # [bruce 080917 comment]
            if names:
                name = names[-1]
                assy = self.assy
                obj = assy and assy.object_for_glselect_name(name)
                    #k should always return an obj
                return obj
        return None # from ThumbView.select

    def highlightSelected(self, obj):
        # TODO: merge with GLPane (from which this was copied and modified)
        """
        Highlight the selected object <obj>. In the mean time, we do stencil test to
        update stencil buffer, so it can be used to quickly test if pick is still
        on the same <obj> as last test.
        """
        if not obj:
            return
        if not isinstance(obj, Atom) or (obj.element is not Singlet):
            return

        self._preHighlight()

        self._drawSelected_using_DrawingSets(obj)

        self._endHighlight()

        glFlush()
        self.swapBuffers()
        return

    def _preHighlight(self): ### TODO: rename; move into GLPane_minimal, use in GLPane.py
        """
        Change OpenGL settings to prepare for highlighting.
        """
        self.makeCurrent()
        glClear(GL_STENCIL_BUFFER_BIT)

        glDepthMask(GL_FALSE) # turn off depth writing (but not depth test)
        ## glDisable(GL_DEPTH_TEST)
        glStencilFunc(GL_ALWAYS, 1, 1)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        glEnable(GL_STENCIL_TEST)

        self.setDepthRange_Highlighting()

        glMatrixMode(GL_MODELVIEW)
        return

    def _endHighlight(self):
        """
        Restore OpenGL settings changed by _preHighlight to standard values.
        """
        glDepthMask(GL_TRUE)
        ## glEnable(GL_DEPTH_TEST)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
        glDisable(GL_STENCIL_TEST)

        self.setDepthRange_Normal()

        glMatrixMode(GL_MODELVIEW)
        return

    def saveLastView(self): #bruce 060627 for compatibility with GLPane (for sake of assy.update_parts)
        pass

    def forget_part(self, part): #bruce 060627 for compatibility with GLPane (for sake of chunk.kill)
        pass

    pass # end of class ThumbView

# ==

class ElementView(ThumbView):
    """
    Element graphical display class.
    """
    # note: as of 080403 this is only used by elementColors.py and elementSelector.py
    def __init__(self, parent, name, shareWidget = None):
        ThumbView.__init__(self, parent, name, shareWidget)
        self.scale = 2.0 #5.0 ## the possible largest rvdw of all elements
        self.pos = V(0.0, 0.0, 0.0)
        self.mol = None

        ## Dummy attributes. A kludge, just try to make other code
        ##  think it looks like a glpane object.
        self.displayMode = 0
        self.selatom = None

    def resetView(self, scale = 2.0):
        """
        Reset current view.
        """
        ThumbView.resetView(self)
        self.scale = scale

    def drawModel(self):
        """
        The method for element drawing.
        """
        if self.mol:
            self.mol.draw(self, None)

    def model_is_valid(self): #bruce 080117
        """
        whether our model is currently valid for drawing
        [overrides GLPane_minimal method]
        """
        return self.mol and self.mol.assy.assy_valid

    def _get_assy(self):
        """
        [overrides ThumbView method]
        """
        return self.mol and self.mol.assy

    def refreshDisplay(self, elm, dispMode = diTrueCPK):
        """
        Display the new element or the same element but new display mode.
        """
        self.makeCurrent()
        self.mol = self.constructModel(elm, self.pos, dispMode)
        self.updateGL()

    def updateColorDisplay(self, elm, dispMode = diTrueCPK):
        """
        Display the new element or the same element but new display mode.
        """
        self.makeCurrent()
        self.mol = self.constructModel(elm, self.pos, dispMode)
        self.updateGL()


    def constructModel(self, elm, pos, dispMode):
        """
        This is to try to repeat what 'make_Atom_and_bondpoints()' method does,
        but hope to remove some stuff not needed here.
        The main purpose is to build the geometry model for element display.

        @param elm: An object of class Elem
        @param elm: L{Elem}

        @param dispMode: the display mode of the atom
        @type  dispMode: int

        @return: the Chunk which contains the geometry model.
        @rtype: L{Chunk}
        """
        assy = Assembly(None, run_updaters = False)
        assy.set_glpane(self) # sets .o and .glpane
        mol = Chunk(assy, 'dummy')
        atm = Atom(elm.symbol, pos, mol)
        atm.display = dispMode
        ## bruce 050510 comment: this is approximately how you should change the atom type (e.g. to sp2) for this new atom:
        ## atm.set_atomtype_but_dont_revise_singlets('sp2')
        ## see also atm.element.atomtypes -> a list of available atomtype objects for that element
        ## (which can be passed to set_atomtype_but_dont_revise_singlets)
        atm.make_bondpoints_when_no_bonds()
        return mol

    def drawSelected(self, obj):
        """
        Override the parent version. Specific drawing code for the object.
        """
        if isinstance(obj, Atom) and (obj.element is Singlet):
            obj.draw_in_abs_coords(self, env.prefs[bondpointHighlightColor_prefs_key])

    pass # end of class ElementView

class MMKitView(ThumbView):
    """
    Currently used as the GLWidget for the graphical display and manipulation
    for element/clipboard/part. Initial attempt was to subclass this for each
    of above type models, but find trouble to dynamically change the GLWidget
    when changing tab page.
    """
    # note: as of 080403 this is constructed only by PM_PreviewGroupBox.py
    # and required (assert isinstance(self.elementViewer, MMKitView)) by
    # PM_Clipboard.py, PM_MolecularModelingKit.py, and PM_PartLib.py.
    # I think that means it is used for MMKit atoms, PasteFromClipboard_Command clipboard,
    # and PartLib parts. [bruce 080403 comment]
    always_draw_hotspot = True
        #bruce 060627 to help with bug 2028
        # (replaces a horribe kluge in old code which broke a fix to that bug)

    def __init__(self, parent, name, shareWidget = None):
        ThumbView.__init__(self, parent, name, shareWidget)
        self.scale = 2.0
        self.pos = V(0.0, 0.0, 0.0)
        self.model = None

        ## Dummy attributes. A kludge, just try to make other code
        ##  think it looks like a glpane object.
        self.displayMode = 0
        self.selatom = None

        self.hotspotAtom = None #The current hotspot singlet for the part
        self.lastHotspotChunk = None # The previous chunk of the hotspot for the part

        hybrid_type_name = None
        elementMode = True  #Used to differentiate elment page versus clipboard/part page

    def drawModel(self):
        """
        The method for element drawing.
        """
        if self.model:
            if isinstance(self.model, Chunk) or \
               isinstance(self.model, Group):
                self.model.draw(self, None)
            else: ## Assembly
                self.model.draw(self)
        return

    def model_is_valid(self): #bruce 080117, revised 080220, 080913
        """
        whether our model is currently valid for drawing
        [overrides GLPane_minimal method]
        """
        return self.assy and self.assy.assy_valid

    def _get_assy(self): #bruce 080220
        """
        [overrides ThumbView method]
        """
        if self.model:
            if isinstance(self.model, Chunk) or \
               isinstance(self.model, Group):
                assy = self.model.assy
                    # Note: assy can be None, if the dna updater kills a bare Ax,
                    # since its chunk is then killed and its .assy set to None.
                    # But the following is too verbose to be useful; also it
                    # seemingly happens even for Ss3 (why??).
                    # Todo: check if it's due to Ax (ok to not print it here)
                    # or to something we didn't expect (needs print so as not
                    # to risk hiding other bugs).
                ## if res is None:
                ##     print "dna updater fyi: in model_is_valid: " \
                ##        "%r.model %r has .assy None" % \
                ##        (self, self.model)
                return assy
            else: ## self.model is an Assembly
                return self.model
        return None

    def refreshDisplay(self, elm, dispMode = diTrueCPK):
        """
        Display the new element or the same element but new display mode.
        """
        self.makeCurrent()
        self.model = self.constructModel(elm, self.pos, dispMode)
        self.updateGL()

    def changeHybridType(self, name):
        self.hybrid_type_name = name

    def resetView(self):
        """
        Reset current view.
        """
        ThumbView.resetView(self)
        self.scale = 2.0

    def drawSelected(self, obj):
        """
        Override the parent version. Specific drawing code for the object.
        """
        if isinstance(obj, Atom) and (obj.element is Singlet):
            obj.draw_in_abs_coords(self, env.prefs[bondpointHighlightColor_prefs_key])
        return

    def constructModel(self, elm, pos, dispMode):
        """
        This is to try to repeat what 'make_Atom_and_bondpoints()' method does,
        but hope to remove some stuff not needed here.
        The main purpose is to build the geometry model for element display.

        @param elm: An object of class Elem
        @param elm: L{Elem}

        @param dispMode: the display mode of the atom
        @type  dispMode: int

        @return: the Chunk which contains the geometry model.
        @rtype: L{Chunk}
        """
        assy = Assembly(None, run_updaters = False)
        assy.set_glpane(self) # sets .o and .glpane
        mol = Chunk(assy, 'dummy')
        atm = Atom(elm.symbol, pos, mol)
        atm.display = dispMode
        ## bruce 050510 comment: this is approximately how you should change the atom type (e.g. to sp2) for this new atom:
        if self.hybrid_type_name:
            atm.set_atomtype_but_dont_revise_singlets(self.hybrid_type_name)
        ## see also atm.element.atomtypes -> a list of available atomtype objects for that element
        ## (which can be passed to set_atomtype_but_dont_revise_singlets)
        atm.make_bondpoints_when_no_bonds()

        self.elementMode = True
        return mol

    def leftDown(self, event):
        """
        When in clipboard mode, set hotspot if a Singlet is highlighted.
        """
        if self.elementMode: return

        obj = self.selectedObj
        if isinstance(obj, Atom) and (obj.element is Singlet):
            mol = obj.molecule
            if not mol is self.lastHotspotChunk:
                if self.lastHotspotChunk: # Unset previous hotspot [bruce 060629 fix bug 1974 -- only if in same part]
                    if mol.part is self.lastHotspotChunk.part and mol.part is not None:
                        # Old and new hotspot chunks are in same part. Unset old hotspot,
                        # so as to encourage there to be only one per Part.
                        #   This should happen when you try to make more than one hotspot in one
                        # library part or clipboard item, using the MMKit to make both.
                        #   It might make more sense for more general code in Part to prevent
                        # more than one hotspot per part... but we have never decided whether
                        # that would be a good feature. (I have long suspected that hotspots
                        # should be replaced by some sort of jig, to give more control....)
                        #   I don't know if this case can ever happen as of now, since multichunk
                        # clipboard items aren't shown in MMKit -- whether it can happen now
                        # depends on whether any multichunk library parts have bondpoints on
                        # more than one chunk. [bruce 060629]
                        if env.debug() and self.lastHotspotChunk.hotspot: #bruce 060629 re bug 1974
                            print "debug: unsetting hotspot of %r (was %r)" % \
                                  (self.lastHotspotChunk, self.lastHotspotChunk.hotspot)
                        self.lastHotspotChunk.set_hotspot(None)
                    else:
                        # Don't unset hotspot in this case (doing so was causing bug 1974).
                        if env.debug() and self.lastHotspotChunk.hotspot:
                            print "debug: NOT unsetting hotspot of %r" % (self.lastHotspotChunk, )
                        pass
                self.lastHotspotChunk = mol
                    # [as of 060629, the only purpose of this is to permit the above code to unset it in some cases]

            mol.set_hotspot(obj)

            if 1:
                #bruce 060328 fix gl_update part of bug 1775 (the code looks like that was a bug forever, don't know for sure)
                main_glpane = env.mainwindow().glpane
                if mol.part is main_glpane.part:
                    main_glpane.gl_update()

            self.hotspotAtom = obj
            self.updateGL()
        return

    def gl_update(self): #bruce 070502 bugfix (can be called when ESPImage jigs appear in a partlib part)
        self.updateGL() #k guess at correct/safe thing to do
        return

    def gl_update_highlight(self): #bruce 070626 precaution (not sure if any code will call this)
        self.gl_update()
        return

    def gl_update_for_glselect(self): #bruce 070626 precaution (not sure if any code will call this)
        self.gl_update()
        return

    def updateModel(self, newObj):
        """
        Set new chunk or Assembly for display.
        """
        self.model = newObj

        #Reset hotspot related stuff for a new Assembly
        if isinstance(newObj, Assembly):
            self._find_and_set_hotSpotAtom_in_new_model(newObj)

        self._fitInWindow()
        self.elementMode = False
        self.updateGL()

    def _find_and_set_hotSpotAtom_in_new_model(self, newModel):
        """
        If the model being viewed in the thumbView window already has a hotspot,
        set it as self.hotSpotAtom (which then will be used by client code)

        @see: self.updateModel
        @Note that , in self.leftDown, we can actually temporarily change the
        the hotspot for the partlib model. But then if you view another part and
        go back to this model, the hotspot will be reset to the one that already
        exists in the model (or None if one doesn't exist)
        """
        assert isinstance(newModel, Assembly)
        chunkList = []
        def func(node):
            if isinstance(node, Chunk):
                chunkList.append(node)
        newModel.part.topnode.apply2all(func)


        ok = False
        if len(chunkList) == 1:
            ok, hotspot_or_whynot = find_hotspot_for_pasting(chunkList[0])
        elif len(chunkList) > 1:
            for chunk in chunkList:
                ok, hotspot_or_whynot = find_hotspot_for_pasting(chunk)
                if ok:
                    break
        if ok:
            self.hotspotAtom = hotspot_or_whynot
            self.lastHotspotChunk = self.hotspotAtom.molecule
        else:
            self.hotspotAtom = None
            self.lastHotspotChunk = None
        return

    def setDisplay(self, disp):
        self.displayMode = disp
        return

    def _fitInWindow(self):
        if not self.model:
            return

        self.quat = Q(1, 0, 0, 0)

        if isinstance(self.model, Chunk):
            self.model._recompute_bbox()
            bbox = self.model.bbox
        else: ## Assembly
            part = self.model.part
            bbox = part.bbox
        self.scale = bbox.scale()

        # guess: the following is a KLUGE for width and height
        # being the names of Qt superclass methods
        # but also being assigned to ints by our own code.
        # I don't know why it could ever be needed, since resizeGL
        # sets them -- maybe this can be called before that ever is??
        # [bruce 080912 comment]
        if isinstance(self.width, int):
            width = self.width
        else:
            width = float(self.width())
        if isinstance(self.height, int):
            height = self.height
        else:
            height = float(self.height())

        aspect = width / height
            # REVIEW: likely bug: integer division is possible [bruce 080912 comment]

        ##aspect = float(self.width) / self.height
        if aspect < 1.0:
            self.scale /= aspect
        center = bbox.center()
        self.pov = V(-center[0], -center[1], -center[2])

    pass # end of class MMKitView

# end
