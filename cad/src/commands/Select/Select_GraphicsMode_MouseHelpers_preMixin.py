# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Select_GraphicsMode_MouseHelpers_preMixin.py


Mixin class for the Select_basicGraphicsMode. The only purpose of creating this
mixin class was for easy understanding of the code in Select_basicGraphicsMode
As the name suggest, this mixin class overrides the Mouse helper Methods
(e.g. leftDown, objectLeftdown, objectSetUp etc) of the
'basicGraphicsMode' . This is a 'preMixin' class, meaning, it needs to be
inherited by the subclass 'Select_basicGraphicsMode' _before_ it inherits the
'basicGraphicsMode'

To be used as a Mixin class only for Select_basicGraphicsMode.

@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.


"""

import foundation.env as env
from model.bonds import Bond
from model.chem import Atom
from model.chunk import Chunk
from model.jigs import Jig
from utilities.debug import print_compact_stack
debug_update_selobj_calls = False # do not commit with true

from utilities.GlobalPreferences import DEBUG_BAREMOTION, DEBUG_BAREMOTION_VERBOSE

_count = 0

# ==

from command_support.GraphicsMode import commonGraphicsMode

class Select_GraphicsMode_MouseHelpers_preMixin(commonGraphicsMode):
    """
    Mixin class for the Select_basicGraphicsMode. The only purpose of creating this
    mixin class was for easy understanding of the code in Select_basicGraphicsMode
    As the name suggest, this mixin class overrides the Mouse helper Methods
    (e.g. leftDown, objectLeftdown, objectSetUp etc) of the
    'basicGraphicsMode' . This is a 'preMixin' class, meaning, it needs to be
    inherited by the subclass 'Select_basicGraphicsMode' _before_ it inherits the
    'basicGraphicsMode'

    To be used as a Mixin class only for Select_basicGraphicsMode.
    @see: B{Select_basicGraphicsMode}
    """
    #Define All Mouse related methods
    def bareMotion(self, event):
        """
        called for motion with no button down
        [should not be called otherwise -- call update_selatom
         or update_selobj directly instead]
        """
        # The mouse_exceeded_distance() conditional below is a
        # "hover highlighting" optimization.
        # It works by returning before calling update_selobj() if the mouse is
        # moving fast. This reduces unnecessary highlighting of objects whenever
        # the user moves the cursor quickly across the GLPane. In many cases,
        # this unnecessary highlighting degrades
        # interactive responsiveness and can also cause the user to select the
        # wrong objects (i.e. atoms), especially in large models.
        #
        # One problem with this approach (pointed out by Bruce) happens when the
        # user moves the
        # cursor quickly from one object and suddenly stops on another object,
        # expecting it (the 2nd object) to be highlighted. Since bareMotion()
        # is only called when the mouse is moving, and the distance between the
        # last two mouse move events is far, mouse_exceed_distance() will
        # return True. In that case, update_selobj() will not get called and the
        # object under the cursor  will never get highlighted unless the user
        # jiggles the mouse slightly. To address this issue, a GLpane timer was
        # implemented. The timer calls bareMotion() whenever it expires and the
        # cursor hasn't moved since the previous timer event. [But at most once
        # after the cursor stops, or something like that -- see the code.]
        # For more details, read the docstring [and code] for GLPane.timerEvent().
        # [probably by Mark, probably circa 060806]
        #
        # russ 080527: Fixed bug 2606.  After a zoom wheelEvent, prevent
        # skipping highlight selection due to mouse_exceeded_distance.
        if self.mouse_exceeded_distance(event, 1) and not self.o.wheelHighlight:
            if DEBUG_BAREMOTION_VERBOSE:
                #bruce 080129 re highlighting bug 2606 reported by Paul
                print "debug fyi: skipping %r.bareMotion since mouse travelled too far" % self
            return False

        self.update_selobj(event)
        # note: this routine no longer updates glpane.selatom. For that see
        # self.update_selatom().
        ###e someday, if new or prior selobj asks for it (by defining certain
        # methods), we'd tell it about this bareMotion and about changes in
        # selobj. [bruce 060726]
        return False # russ 080527

    #Left mouse related event handlers --


    # == LMB event handling methods ====================================

    # Important Terms: [mark 060205]
    #
    # "selection curve": the collection of line segments drawn by the cursor
    # when definingthe selection area.  These line segments become the selection
    # lasso when (and if) the selection rectangle disappears. When the selection
    # rectangle is still displayed,the selection curve consists of those line
    # segment that are drawn between opposite corners of the selection
    # rectangle. The line segments that define/draw the rectangle itself are not
    # part of the selection curve, however.Also, it is worth noting that the
    # line segments of the selection curve are also drawn just beyond the front
    # clipping plane. The variable <selCurve_List> contains the list
    # of points that draw the line segments of the selection curve.
    #
    # "selection area": determined by the selection curve, it is the area that
    # defines what
    # is picked (or unpicked).  The variable <selArea_List> contains the list of
    # points that define the selection area used to pick/unpick objects. The
    # points in  <selArea_List> lay in the plane parallel to the screen and pass
    # through the center of the view.
    #
    # "selection rectangle": the rectangular selection determined by the first
    # and last points of a selection curve.  These two points define the
    # opposite corners of the rectangle.
    #
    # "selection lasso": the lasso selection defined by all the points
    #(and line segements)in the selection curve.

    # == LMB down-click (button press) methods

    def leftShiftDown(self, event):
        self.leftDown(event)

    def leftCntlDown(self, event):
        self.leftDown(event)

    def leftDown(self, event):
        self.select_2d_region(event)

    # == LMB drag methods

    def leftShiftDrag(self, event):
        self.leftDrag(event)

    def leftCntlDrag(self, event):
        self.leftDrag(event)

    def leftDrag(self, event):
        self.continue_selection_curve(event)

    # == LMB up-click (button release) methods

    def leftShiftUp(self, event):
        self.leftUp(event)

    def leftCntlUp(self, event):
        self.leftUp(event)

    def leftUp(self, event):
        self.end_selection_curve(event)

    # == LMB double click method

    def leftDouble(self, event):
        pass

    # == END of LMB event handlers. ============================================

    # == START of Empty Space helper methods ===================================

    #& The Empty Space, Atom, Bond and Singlet helper methods should probably be
    #& moved to SelectAtoms_GraphicsMode.  I put them here because I think there is a
    #& good chance that we'll allow intermixing of atoms, chunks and jigs
    #&(and other stuff) in any mode. Mark 060220.

    def emptySpaceLeftDown(self, event):
        self.objectSetup(None)
        self.cursor_over_when_LMB_pressed = 'Empty Space'
        self.select_2d_region(event)
        return

    def emptySpaceLeftDrag(self, event):
        self.continue_selection_curve(event)
        return

    def emptySpaceLeftUp(self, event):
        self.end_selection_curve(event)
        return
    # == END of Empty Space helper methods =====================================

    # == START of object specific LMB helper methods ===========================
    def doObjectSpecificLeftDown(self, obj, event):
        """
        Call objectLeftDown methods depending on the object instance.
        @param obj: object under consideration
        @type  obj: instance
        @param event: Left down mouse event
        @type  event: QMouseEvent instance
        """
        if isinstance(obj, Chunk):
            self.chunkLeftDown(obj, event)
        if isinstance(obj, Atom) and obj.is_singlet():
            self.singletLeftDown(obj, event)# Cursor over a singlet
        elif isinstance(obj, Atom) and not obj.is_singlet():
            self.atomLeftDown(obj, event)   # Cursor over a real atom
        elif isinstance(obj, Bond) and not obj.is_open_bond():
            self.bondLeftDown(obj, event)   #Cursor over a bond.
        elif isinstance(obj, Jig):
            self.jigLeftDown(obj, event)    #Cursor over a jig.
        else:
            # Cursor is over something else other than an atom, singlet or bond.
            # (should be handled in caller)
            pass

    def doObjectSpecificLeftUp(self, obj, event):
        """
        Call objectLeftUp methods depending on the object instance.
        @param obj: object under consideration
        @type  obj: instance
        @param event: Left Up mouse event
        @type  event: QMouseEvent instance
        """

        #This flag initially gets set in selectMode.objectSetup. Then,
        #if the object is being dragged, the value is reset to False in
        #the object specific drag method  . FYI: The comment in
        #selectMode.objectSetup suggests the this flag should not be set in
        #class.leftDrag method. (but instead object specific left drag)
        #So lets set that flag up in the method
        #selectMode.doObjectSpecificLeftDrag. Note that this method is
        #overridden in subclasses, so make sure to either set that flag in
        #those methods or always call the superclass method at the beginning.
        # In case of SelectChunks_GraphicsMode, the 'objects' are
        # really the  selectedMovable. so it makes sense to set it in
        #SelectChunks_GraphicsMode.leftDragTranslation or call doObjectSpecificLeftDrag
        #somewhere -- Ninad 2007-11-15

        #UPDATE 2007-11-15:
        #The self.current_obj_clicked is not valid for  Singlets (bond
        #points) because singlet dragging and then doing left up actually forms
        #a bond. So It is important to continue down this method for that
        #condition even if self.current_obj_clicked is False. Otherwise bonds
        # won't be formed....Then should this check be done in each of the
        #objectLeftUp methods? But that would be too many methods in various
        #subclasses and it may cause bugs if someone forgets to add this check.

        if not self.current_obj_clicked:
            if isinstance(obj, Atom) and obj.is_singlet():
                pass
            else:
                return
        if isinstance(obj, Chunk):
            self.chunkLeftUp(obj, event)
        elif isinstance(obj, Atom):
            if obj.is_singlet(): # Bondpoint
                self.singletLeftUp(obj, event)
            else: # Real atom
                self.atomLeftUp(obj, event)
        elif isinstance(obj, Bond): # Bond
            self.bondLeftUp(obj, event)
        elif isinstance(obj, Jig): # Jig
            self.jigLeftUp(obj, event)

        else:
            pass

    def doObjectSpecificLeftDrag(self, obj, event):
        """
        Call objectLeftDrag methods depending on the object instance.
        Default implementation only sets flag self.current_obj_clicked to False.
        Subclasses should make sure to either set that flag in
        #those methods or always call the superclass method at the beginning.

        @param obj: object under consideration.
        @type  obj: instance
        @param event: Left drag mouse event
        @type  event: QMouseEvent instance
        @see: SelectAtoms_GraphicsMode.doObjectSpecificLeftDrag
        @see: self.doObjectSpecificLeftUp, self.objectSetup for comments
        """
        #current object is not clicked but is dragged. Important to set this
        #flag. See self.doObjectSpecificLeftUp for more comments
        self.current_obj_clicked = False


    def objectSetup(self, obj):
        ###e [should move this up, below generic left* methods --
        ##it's not just about atoms]
        # [this seems to be called (sometimes indirectly) by every leftDown
        # method, and by some methods in depmode that create objects and can
        # immediately drag them. Purpose is more general than just for a
        # literal "drag" --
        # I guess it's for many things that immediately-subsequent leftDrag or
        # leftUp or leftDouble might need to know obj to decide on. I think I'll
        #call it for all new drag_handlers too. [bruce 060728 comment]]
        self.current_obj = obj # [used by leftDrag and leftUp to decide what
                               #to do [bruce 060727 comment]]
        self.obj_doubleclicked = obj # [used by leftDouble and class-specific
                                     #leftDouble methods [bruce 060727 comment]]

        if obj is None:
            self.current_obj_clicked = False
        else:
            self.current_obj_clicked = True
                # [will be set back to False if obj is dragged, but only by
                # class-specific drag methods, not by leftDrag itself -- make
                # sure to consider doing that in drag_handler case too  ##@@@@@
                #  [bruce 060727 comment]]

            # we need to store something unique about this event;
            # we'd use serno or time if it had one..instead this _count will do.
            global _count
            _count = _count + 1
            self.current_obj_start = _count # used in transient_id argument
                                            #to env.history.message


    def atomSetup(self, a, event):
        """
        Subclasses should override this method
        Setup for a click, double-click or drag event for real atom <a>.
        @see: selectatomsMode.atomSetup where this method is overridden.
        """
        self.objectSetup(a)

    def atomLeftDown(self, a, event):
        """
        Subclasses should override this method.
        @param a: Instance of class Atom
        @type a: B{Atom}
        @param event: the QMouseEvent.
        @see: SelectAtoms_GraphicsMode.atomLeftDown
        """
        self.atomSetup(a, event)

    def atomLeftUp(self, a, event):
        """
        Subclasses should override this method. The default implementation does
        nothing.
        @param a: Instance of class Atom
        @type a: B{Atom}
        @param event: the QMouseEvent.
        @see: SelectAtoms_GraphicsMode.atomLeftUp
        """
        pass

    def atomLeftDouble(self):
        """
        Subclasses should override this method. The default implementation
        does nothing.

        Atom double click event handler for the left mouse button.
        """
        pass

    # == End of Atom selection and dragging helper methods

    # == Bond selection helper methods

    def bondLeftDown(self, b, event):
        # Bonds cannot be picked when highlighting is turned off.
        self.cursor_over_when_LMB_pressed = 'Bond'
        self.bondSetup(b)

    def bondSetup(self, b):
        """
        Setup for a click or double-click event for bond <b>. Bond dragging is
        not supported.
        """
        self.objectSetup(b)

    def bondLeftUp(self, b, event):
        """
        Subclasses should override this method. The default implementation does
        nothing.

        Bond <b> was clicked, so select or unselect its atoms or delete bond <b>
        based on the current modkey.
        - If no modkey is pressed, clear the selection and pick <b>'s two atoms.
        - If Shift is pressed, pick <b>'s two atoms, adding them to the current
          selection.
        - If Ctrl is pressed,  unpick <b>'s two atoms, removing them from
          the current selection.
        - If Shift+Control (Delete) is pressed, delete bond <b>.
        <event> is a LMB release event.
        """
        pass

    def bondDelete(self, event):
        """
        If the object under the cursor is a bond, delete it.

        @param event: A left mouse up event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        # see also: bond_utils.delete_bond

        #bruce 041130 in case no update_selatom happened yet
        self.update_selatom(event)
            # see warnings about update_selatom's delayed effect,
            # in its docstring or in leftDown. [bruce 050705 comment]
        selobj = self.o.selobj
        if isinstance( selobj, Bond) and not selobj.is_open_bond():
            _busted_strand_bond = False
            if selobj.isStrandBond():

                _busted_strand_bond = True
                msg = "breaking strand %s" % selobj.getStrandName()
            else:
                msg = "breaking bond %s" % selobj
            env.history.message_no_html(msg)
                # note: %r doesn't show bond type, but %s needs _no_html
                # since it contains "<-->" which looks like HTML.
            self.o.selobj = None
                # without this, the bond remains highlighted
                # even after it's broken (visible if it's toolong)
                ###e shouldn't we use set_selobj instead??
                ##[bruce 060726 question]
            x1, x2 = selobj.bust()
                # this fails to preserve the bond type on the open bonds
                # -- not sure if that's bad, but probably it is

            if 1:
                # Note: this should be removed once the dna updater becomes
                # turned on by default. (It will cause no harm, but will be a slowdown
                # since everything it does will be undone or redone differently
                # by the updater.) [bruce 080228 comment]

                # After bust() selobj.isStrandBond() is too fragile, so I set
                # <_busted_strand_bond> and test it instead. - Mark 2007-10-23.
                if _busted_strand_bond: # selobj.isStrandBond():
                    self.o.assy.makeStrandChunkFromBrokenStrand(x1, x2)

            self.set_cmdname('Delete Bond')
            self.o.assy.changed() #k needed?
            self.w.win_update() #k wouldn't gl_update be enough?
                                #[bruce 060726 question]


    def bondDrag(self, obj, event):
        """
        Subclasses should override this method
        @see: SelectAtoms_GraphicsMode.bondDrag
        """
        pass

    def bondLeftDouble(self):
        """
        Subclasses should override this method
        @see: SelectAtoms_GraphicsMode.bondLeftDouble
        """
        pass

    # == End of bond selection helper methods

    #== Chunk helper methods

    def chunkSetUp(self, a_chunk, event):
        """
        Chunk setup (called from self.chunkLeftDown()
        @see: SelectChunks_GraphicsMode.chunkLeftDown()
        @see: BuildDna_GraphicsMode.chunkLeftDown()
        @see:self.objectSetup()
        """

        self.objectSetup(a_chunk)

    def chunkLeftDown(self, a_chunk, event):
        """
        Overridden is subclasses. Default implementation does nothing.

        Depending on the modifier key(s) pressed, it does various operations on
        chunk..typically pick or unpick the chunk(s) or do nothing.

        If an object left down happens, the left down method of that object
        calls this method (chunkLeftDown) as it is the 'SelectChunks_GraphicsMode' which
        is supposed to select Chunk of the object clicked
        @param a_chunk: The chunk of the object clicked (example, if the  object
                      is an atom, then it is atom.molecule
        @type a_chunk: B{Chunk}
        @param event: MouseLeftDown event
        @see: self.atomLeftDown
        @see: self.chunkLeftUp

        @see: SelectChunks_GraphicsMode.chunkLeftDown()
        """
        pass

    def chunkLeftUp(self, a_chunk, event):
        """

        Overridden is subclasses. Default implementation does nothing.

        Depending on the modifier key(s) pressed, it does various operations on
        chunk. Example: if Shift and Control modkeys are pressed, it deletes the
        chunk
        @param a_chunk: The chunk of the object clicked (example, if the  object
                      is an atom, then it is atom.molecule
        @type a_chunk: B{Chunk}
        @param event: MouseLeftUp event
        @see: self.atomLeftUp
        @see: self.chunkLeftdown
        @see: SelectChunks_GraphicsMode.chunkLeftUp()
        """
        pass


    # == Singlet helper methods

    def singletLeftDown(self, s, event):
        self.cursor_over_when_LMB_pressed = 'Empty Space'
        self.select_2d_region(event)
        self.o.gl_update()
        # REVIEW (possible optim): can gl_update_highlight be extended to
        # cover this? [bruce 070626]
        return

    def singletSetup(self, s):
        pass

    def singletDrag(self, s, event):
        pass

    def singletLeftUp(self, s, event):
        pass

    def singletLeftDouble(self):
        """
        Singlet double click event handler for the left mouse button.
        """
        pass

    #Reference Geometry handler helper methods
    #@@ This and jig helper methods need to be combined. -- ninad 20070516
    def geometryLeftDown(self, geom, event):
        self.jigLeftDown(geom, event)

    def geometryLeftUp(self, geom, event):
        self.jigLeftUp(geom, event)

    def geometryLeftDrag(self, geom, event):
        geometry_NewPt = self.dragto( self.jig_MovePt, event)
        # Print status bar msg indicating the current move offset.
        if 1:
            self.moveOffset = geometry_NewPt - self.jig_StartPt
            msg = "Offset: [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.moveOffset[0],
                                                             self.moveOffset[1],
                                                             self.moveOffset[2])
            env.history.statusbar_msg(msg)

        offset = geometry_NewPt - self.jig_MovePt
        geom.move(offset)
        self.jig_MovePt = geometry_NewPt
        self.current_obj_clicked = False
        self.o.gl_update()

    def handleLeftDown(self, hdl, event):
        self.handle_MovePt = hdl.parent.getHandlePoint(hdl, event)
        self.handleSetUp(hdl)

    def handleLeftDrag(self, hdl, event):
        hdl.parent.resizeGeometry(hdl, event)
        handle_NewPt = hdl.parent.getHandlePoint(hdl, event)
        self.handle_MovePt = handle_NewPt
        self.current_obj_clicked = False
        self.o.gl_update()

    def handleLeftUp(self, hdl, event):
        pass

    def handleSetUp(self, hdl):
        self.objectSetup(hdl)

    # == Jig event handler helper methods

    def jigLeftDown(self, j, event):
        if not j.picked and self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane() # was unpickatoms, unpickparts
                                              #[bruce 060721]
            j.pick()
        if not j.picked and self.o.modkeys == 'Shift':
            j.pick()
        if j.picked:
            self.cursor_over_when_LMB_pressed = 'Picked Jig'
        else:
            self.cursor_over_when_LMB_pressed = 'Unpicked Jig'

        # Move section
        farQ_junk, self.jig_MovePt = self.dragstart_using_GL_DEPTH( event)
            #bruce 060316 replaced equivalent old code with this new method

        if 1:
            #bruce 060611 experiment, harmless, prototype of WidgetExpr-related
            # changes, might help Bauble; committed 060722
            # [see also leftClick, which will eventually supercede this,
            # and probably could already -- bruce 060725]
            method = getattr(j, 'clickedOn', None)
            if method and method(self.jig_MovePt):
                return

        self.jig_StartPt = self.jig_MovePt # Used in leftDrag() to compute move
                                           #offset during drag op.
        self.jigSetup(j)

    def jigSetup(self, j):
        """
        Setup for a click, double-click or drag event for jig <j>.
        """
        self.objectSetup(j)

    def jigLeftUp(self, j, event):
        """
        Jig <j> was clicked, so select, unselect or delete it based on the
        current modkey.
        - If no modkey is pressed, clear the selection and pick jig <j>.
        - If Shift is pressed, pick <j>, adding it to the current selection.
        - If Ctrl is pressed,  unpick <j>, removing it from the current
          selection.
        - If Shift+Control (Delete) is pressed, delete jig <j>.
        """

        self.deallocate_bc_in_use()

        if not self.current_obj_clicked:
            # Jig was dragged.  Nothing to do but return.
            self.set_cmdname('Move Jig')
            self.o.assy.changed()
            return

        if self.selection_locked():
            return

        nochange = False

        if self.o.modkeys is None:
            # isn't this redundant with jigLeftDown? [bruce 060721 question;
            #btw this method is very similar to atomLeftUp]
            self.o.assy.unpickall_in_GLPane() # was unpickatoms only
            #(but I think unpickall makes more sense) [bruce 060721]
            if j.picked:
                # bruce 060412 fix unreported bug: remove nochange = True,
                #in case atoms were just unpicked
                pass ## nochange = True
            else:
                j.pick()
                self.set_cmdname('Select Jig')

        elif self.o.modkeys == 'Shift':
            if j.picked:
                nochange = True
            else:
                j.pick()
                self.set_cmdname('Select Jig')

        elif self.o.modkeys == 'Control':
            if j.picked:
                j.unpick()
                self.set_cmdname('Unselect Jig')
                env.history.message("Unselected %r" % j.name)
                #bruce 060412 comment: I think a better term (in general) would
                #be "Deselect".
            else: # Already unpicked.
                nochange = True

        elif self.o.modkeys == 'Shift+Control':
            #fixed bug 1641. mark 060314. #bruce 060412 revised text
            env.history.message("Deleted %r" % j.name)
            # Build list of deleted jig's atoms before they are lost.
            self.atoms_of_last_deleted_jig.extend(j.atoms) #bruce 060412
                                                           #optimized this
            j.kill()
                #bruce 060412 wonders how j.kill() affects the idea of
                #double-clicking this same jig to delete its atoms too,
                # since the jig is gone by the time of the 2nd click.
                # See comments in jigLeftDouble for more info.
            self.set_cmdname('Delete Jig')
            self.w.win_update()
            return

        else:
            print_compact_stack('Invalid modkey = "' + str(self.o.modkeys) + '" ')
            return

        #call API method to do any additinal selection
        self.end_selection_from_GLPane()

        if nochange:
            return

        self.o.gl_update()

    def jigLeftDouble(self):
        """
        Jig <j> was double clicked, so select, unselect or delete its atoms
        based on the current modkey.
        - If no modkey is pressed, pick the jig's atoms.
        - If Shift is pressed, pick the jig's atoms, adding them to the current
          selection.
        - If Ctrl is pressed,  unpick the jig's atoms, removing them from the
          current selection.
        - If Shift+Control (Delete) is pressed, delete the jig's atoms.
        """
        #bruce 060412 thinks that the jig transdelete feature (delete the jig's
        #atoms on shift-control-dblclick)
        # might be more dangerous than useful:
        # - it might happen on a wireframe jig, like an Anchor, if user intended
        #   to transdelete on an atom instead;
        # - it might happen if user intended to delete jig and then delete an
        #   atom behind it (epecially since the jig
        #   becomes invisible after the first click), if two intended single
        #   clicks were interpreted as a double click;
        # - it seems rarely needed, so it could just as well be in the jig's
        #   context menu instead.
        # To mitigate this problem, I'll add a history message saying that it
        #   happened.
        # I'll also optimize some loops (by removing [:]) and fix bug 1816
        # (missing update).
        if self.o.modkeys == 'Control':
            for a in self.obj_doubleclicked.atoms:
                a.unpick()
        elif self.o.modkeys == 'Shift+Control':
            #bruce 060418 rewrote this, to fix bug 1816 and do other improvements
            # (though I think it should be removed, as explained above)
            atoms = self.atoms_of_last_deleted_jig # a list of atoms
            self.atoms_of_last_deleted_jig = [] # for safety
            if atoms:
                self.set_cmdname("Delete Jig's Atoms")
                    #bruce 060412. Should it be something else? 'Delete Atoms',
                    #'Delete Atoms of Jig', "Delete Jig's Atoms"
                    # Note, this presently ends up as a separate operation in the
                    # Undo stack from the first click deleting the jig, but in
                    #the future these ops might be merged in the Undo stack,
                    # and if they are, this command name should be changed to
                    # cover deleting both the jig and its atoms.
                env.history.message("Deleted jig's %d atoms" % len(atoms))
                    # needed since this could be done by accident, and in some
                    #cases could go unnoticed
                    # (count could be wrong if jig.kill() already killed some
                    # of the atoms for some reason; probably never happens)
                self.w.win_update() # fix bug 1816
                for a in atoms:
                    a.kill() ##e could be optimized using prekill
        else:
            for a in self.obj_doubleclicked.atoms:
                a.pick()
        self.o.gl_update() #bruce 060412 fix some possible unreported bugs
        return

    # == End of (most) Jig helper methods

    def selection_locked(self, msg = ''):
        """
        Returns whether the current selection is 'locked' . If True, no changes
        to the current selection are possible from glpane (i.e using mouse
        opearions) But user can still select the objects using MT or using
        toolbar options such as 'select all'.

        @param msg: optional string to include in statusbar text
        """
        isLocked = self.glpane.mouse_selection_lock_enabled
        if isLocked and msg:
            env.history.statusbar_msg("%s"% msg)

        return isLocked



    # == END of object specific LMB helper methods =============================
