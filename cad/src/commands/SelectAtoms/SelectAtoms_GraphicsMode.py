# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
SelectAtoms_GraphicsMode.py

The GraphicsMode part of the SelectAtoms_Command. It provides the  graphicsMode
object for its Command class. The GraphicsMode class defines anything related to
the *3D Graphics Area* --
For example:
- Anything related to graphics (Draw method),
- Mouse events
- Cursors,
- Key bindings or context menu


@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.


TODO:
- Items mentioned in Select_GraphicsMode.py
- Other items listed in Select_Command.py

History:
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from
                          the old class selectAtomsMode and moved the
                          GraphicsMode related methods into this class from
                          selectAtomsMode.py

"""

from analysis.ESP.ESPImage import ESPImage
from PyQt4.Qt import QMouseEvent

import foundation.env as env

from foundation.state_utils import transclose

from utilities import debug_flags

from geometry.VQT import V, Q, norm, vlen, ptonline
from model.chem import Atom
from model.jigs import Jig
from model.bonds import Bond
from model.elements import Singlet

from utilities.debug import print_compact_traceback, print_compact_stack

from foundation.Group import Group

from commands.Select.Select_GraphicsMode import DRAG_STICKINESS_LIMIT

from utilities.debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False

from utilities.prefs_constants import bondHighlightColor_prefs_key
from utilities.prefs_constants import bondpointHighlightColor_prefs_key
from utilities.prefs_constants import atomHighlightColor_prefs_key
from utilities.prefs_constants import deleteBondHighlightColor_prefs_key
from utilities.prefs_constants import deleteAtomHighlightColor_prefs_key
from utilities.prefs_constants import reshapeAtomsSelection_prefs_key

from utilities.constants import average_value

from utilities.Log import orangemsg

from commands.Select.Select_GraphicsMode import Select_basicGraphicsMode

_superclass = Select_basicGraphicsMode

class SelectAtoms_basicGraphicsMode(Select_basicGraphicsMode):
    """
    The GraphicsMode part of the SelectAtoms_Command. It provides the
    graphicsMode object for its Command class. The GraphicsMode class defines
    anything related to the 3D graphics area --
    For example:
    - Anything related to graphics (Draw method),
    - Mouse events, cursors (for use in graphics area),
    - Key bindings or context menu (for use in graphics area).

    @see: cad/doc/splitting_a_mode.py that gives a detailed explanation about
          how this is implemented.
    @see: B{SelectAtoms_GraphicsMode}
    @see: B{SelectAtoms_Command}, B{SelectAtoms_basicCommand},         
    @see: B{Select_basicGraphicsMode}
    """
    eCCBtab1 = [1, 2,
                5, 6, 7, 8, 9, 10,
                13, 14, 15, 16, 17, 18,
                32, 33, 34, 35, 36,
                51, 52, 53, 54]

    def __init__(self, glpane):
        """
        """
        _superclass.__init__(self, glpane)
        self.get_use_old_safe_drag_code() # ditto

    def Enter_GraphicsMode(self):
        """
        Things needed while entering the GraphicsMode (e.g. updating cursor,
        setting some attributes etc).
        This method is called in self.command.command_entered()
        @see: B{Select_basicGraphicsMode.Enter_GraphicsMode()}
        """

        _superclass.Enter_GraphicsMode(self) #also calls self.reset_drag_vars()
                                             #etc

        self.o.assy.permit_pick_atoms()
         # Reinitialize previously picked atoms (ppas).
        self.o.assy.ppa2 = self.o.assy.ppa3 = None
        self.o.selatom = None

    def getMovablesForLeftDragging(self):
        """
        Returns a list of movables that will be moved during this gaphics mode's
        left drag. In SelectChunks_GraphicsMode it is the selected movables
        in the assembly. However, some subclasses can override this method to
        provide a custom list of objects it wants to move during the left drag
        Example: In buildDna_GraphicsMode, it moving a dnaSegment axis chunk
        will move all the axischunk members of the dna segment and also
        its logical content chunks.
        @see: self._leftDrag_movables #attr
        @see: self._leftDown_preparation_for_dragging()
        @see: self.leftDragTranslation()
        @see:BuildDna_GraphicsMode.getMovablesForLeftDragging()
        @Note: Not implemented in SelectAtoms_GraphicsMode
        """
        movables = []
        return movables


    def reset_drag_vars(self):
        """
        Overrides L{Select_basicGraphicsMode.reset_drag_vars}
        """
        _superclass.reset_drag_vars(self)

        self.dragatoms = []
            # dragatoms is constructed in get_dragatoms_and_baggage() and
            # contains all  the selected atoms (except selected baggage atoms)
            # that are dragged around
            # as part of the current selection in drag_selected_atoms().
            # Selected atoms that are baggage are placed in self.baggage
            # along with non-selected baggage atoms connected to dragatoms.
            # See atomSetup() for more information.
            #bruce 060410 note: self.dragatoms is only set along with
            # self.baggage,and the atoms in these lists are only moved together
            # (in all cases involving self.dragatoms,
            #  though not in all cases involving self.baggage),
            # so it doesn't matter which atoms are in which lists
            # (in those cases),
            # and probably the code should be revised to use only the
            # self.dragatoms list (in those cases).
            #bruce 060410 optimization and change: when all atoms in existing
            # chunks are being dragged
            # (or if new chunks could be temporarily and transparently made for
            # which all their atoms were being dragged),
            # then we can take advantage of chunk display lists to get a big
            # speedup in dragging the atoms.
            # We do this by listing such chunks in self.dragchunks and excluding
            # their atoms from self.dragatoms and self.baggage.

        self.baggage = []
            # baggage contains singlets and/or monovalent atoms
            #(i.e. H, O(sp2), F, Cl, Br)
            # which are connected to a dragged atom and get dragged around with
            #it.Also, no atom which has baggage can also be baggage.

        self.nonbaggage = []
            # nonbaggage contains atoms which are bonded to a dragged atom but
            # are not dragged around with it. Their own baggage atoms are moved
            # when a single atom is dragged in atomDrag().

        self.dragchunks = []

        self.dragjigs = []
            # dragjigs is constructed in jigSetup() and contains all the
            # selected jigs that  are dragged around as part of the current
            # selection in jigDrag().

        self.drag_offset = V(0,0,0) #bruce 060316
            # default value of offset from object reference point
            # (e.g. atom center) to dragpoint (used by some drag methods)

        self.maybe_use_bc = False
            # whether to use the BorrowerChunk optimization for the current
            # drag (experimental) [bruce 060414]

        self.drag_multiple_atoms = False
            # set to True when we are dragging a movable unit of 2 or more
            # atoms.

        self.smooth_reshaping_drag = False
            # set to True when we're going to do a "smooth-reshaping drag" in
            # the current drag. [bruce 070412]

        self.only_highlight_singlets = False
            # When set to True, only singlets get highlighted when dragging a
            # singlet. (Note: the mechanism for that effect is that methods
            # in this class can return the highlight color as None to disable
            # highlighting for a particular selobj.)
            # depositMode.singletSetup() sets this to True while dragging a
            # singlet around.

        self.neighbors_of_last_deleted_atom = []
            # list of the real atom neighbors connected to a deleted atom.
            # Used by atomLeftDouble()
            # to find the connected atoms to a recently deleted atom when
            # double clicking with 'Shift+Control'
            # modifier keys pressed together.


    #==START Highlighting related methods================================

    def _getAtomHighlightColor(self, selobj):
        """
        Return the Atom highlight color to use for selobj
        which is the object under the mouse, or None to disable
        highlighting for that object.

        @note: ok to make use of self.only_highlight_singlets,
               and when it's set, self.current_obj. See code comments
               for details.

        @return: Highlight color to use for the object (Atom or Singlet), or None
        """
        assert isinstance(selobj, Atom)

        if selobj.is_singlet():
            return self._getSingletHighlightColor()
        else:
            # selobj is a real atom
            if self.only_highlight_singlets:
                # Above is True only when dragging a bondpoint (in Build mode)
                # (namely, we are dragging self.current_obj, a bondpoint).
                # Highlight this atom (selobj) if it has bondpoints
                # (but only if it's not the base atom of self.current_obj,
                #  to fix bug 1522 -- mark 060301).
                if selobj.singNeighbors():
                    if self.current_obj in selobj.singNeighbors():
                        # Do not highlight the atom that the current
                        # singlet (self.current_obj) belongs to.
                        return None
                    return env.prefs[atomHighlightColor_prefs_key]
                        # Possible bug: bruce 070413 seems to observe this not
                        # working except when the mouse goes over
                        # the end of a bond attached to that atom
                        # (which counts as the atom for highlighting),
                        # or when the atom is already highlighted.
                        # (Could it be the cursor going over the rubberband
                        #  line? Not always. But it might be intermittent.)
                else:
                    return None
            if self.o.modkeys == 'Shift+Control':
                return env.prefs[deleteAtomHighlightColor_prefs_key]
            else:
                return env.prefs[atomHighlightColor_prefs_key]

    def _getSingletHighlightColor(self):
        """
        Return the Singlet (bondpoint) highlight color.

        @return: Highlight color to use for any bondpoint (specific bondpoint is not passed)
        """
        # added highlight_singlets to fix bug 1540. mark 060220.
        if self.highlight_singlets:
            #bruce 060702 part of fixing bug 833 item 1
            likebond = self.command.isBondsToolActive()
            if likebond:
                # clicks in this tool-state modify the bond,
                # not the bondpoint, so let the color hint at that
                return env.prefs[bondHighlightColor_prefs_key]
            else:
                return env.prefs[bondpointHighlightColor_prefs_key]
        else:
            return None

    def _getBondHighlightColor(self, selobj):
        """
        Return the highlight color for selobj (a Bond),
        or None to disable highlighting for that object.

        @return: Highlight color to use for this bond (selobj), or None
        """
        assert isinstance(selobj, Bond)
        # Following might be an outdated or 'not useful anymore' comment.
        # Keeping it for now -- Ninad 2007-10-14

        #bruce 050822 experiment: debug_pref to control whether to highlight
        # bonds
        # (when False they'll still obscure other things -- need to see if
        # this works for Mark ###@@@)
        # ###@@@ PROBLEM with this implem: they still have a cmenu and
        #can be deleted by cmd-del (since still in selobj);
        # how would we *completely* turn this off? Need to see how
        # GLPane decides whether a drawn thing is highlightable --
        # maybe just by whether it can draw_with_abs_coords?
        # Maybe by whether it has a glname (not toggleable instantly)?
        # ... now i've modified GLPane to probably fix that...
        highlight_bonds = debug_pref("highlight bonds", Choice_boolean_True)
        if not highlight_bonds:
            return None
        ###@@@ use checkbox to control this; when false, return None
        if selobj.atom1.is_singlet() or selobj.atom2.is_singlet():
            # this should never happen, since singlet-bond is part of
            # singlet for selobj purposes [bruce 050708]
            print "bug: selobj is a bond to a bondpoint, should have " \
                  "borrowed glname from that bondpoint", selobj
            return None # precaution
        else:
            if self.only_highlight_singlets:
                return None
            if self.o.modkeys == 'Shift+Control':
                return env.prefs[deleteBondHighlightColor_prefs_key]
            else:
                return env.prefs[bondHighlightColor_prefs_key]


    #==END Highlighting related methods================================

    # == LMB event handling methods ====================================
    #
    # The following sections include all the LMB event handling methods for
    # this class. The section includes the following methods:
    #
    #   - LMB down-click (button press) methods
    #       leftShiftDown()
    #       leftCntlDown()
    #       leftDown()
    #
    #   - LMB drag methods
    #       leftShiftDrag()
    #       leftDrag()
    #
    #   - LMB up-click (button release) methods
    #       leftShiftUp()
    #       leftCntlUp()
    #       leftUp()
    #
    #   - LMB double-click method (only one)
    #       leftDouble()
    #
    # For more information about the LMB event handling scheme, go to
    # http://www.nanoengineer-1.net/ and click on the "Build Mode UI
    # Specification" link.

    # == LMB down-click (button press) methods


    def leftDown(self, event):
        """
        Event handler for all LMB press events.
        """
        # Note: the code of SelectAtoms_GraphicsMode and SelectChunks_GraphicsMode 
        # .leftDown methods  is very similar, so I'm removing the redundant 
        #comments the other one (SelectChunks_GraphicsMode); 
        #i.e. some of this method's comments
        # also apply to the same code in the same method in SelectChunks_GraphicsMode.
        # [bruce 071022]

        self.set_cmdname('BuildClick')
            # TODO: this should be set again later (during the same drag)
            # to a more specific command name.

        self.o.assy.permit_pick_atoms()
            # Fixes bug 1413, 1477, 1478 and 1479.  Mark 060218.
        self.reset_drag_vars()
        env.history.statusbar_msg(" ")
            # get rid of obsolete msg from bareMotion [bruce 050124; imperfect]

        self.LMB_press_event = QMouseEvent(event)
            # Make a copy of this event and save it.
            # We will need it later if we change our mind and start selecting
            # a 2D region in leftDrag(). Copying the event in this way is
            # necessary because Qt will overwrite <event> later (in leftDrag)
            # if we simply set self.LMB_press_event = event.  mark 060220.

        self.LMB_press_pt_xy = (event.pos().x(), event.pos().y())
            # <LMB_press_pt_xy> is the position of the mouse in window
            # coordinates when the LMB was pressed. Used in
            # mouse_within_stickiness_limit (called by leftDrag() and other
            # methods). We don't bother to vertically flip y using self.height
            # (as mousepoints does), since this is only used for drag distance
            # within single drags.

        obj = self.get_obj_under_cursor(event)
            # If highlighting is turned on, get_obj_under_cursor() returns
            # atoms, singlets, bonds, jigs, or anything that can be highlighted
            # and end up in glpane.selobj. [bruce revised this comment, 060725]
            # (It can also return a "background object" from testmode, as of
            # bruce 070322.)
            # If highlighting is turned off, get_obj_under_cursor() returns
            # atoms and singlets (not bonds or jigs).
            # [not sure if that's still true --
            # probably not. bruce 060725 addendum]

        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            return

        #bruce 060725 new feature. Any selobj can decide how clicks/drags
        # on it should behave, if it wants to. Normally this will not apply
        # to an Atom, Bond, or Jig, but there's no reason it couldn't in
        # theory (except that some code may check for those classes first,
        # before checking for selobj using this API).
        # WARNING: API is experimental and is very likely to be modified.
        # (But note that testmode and the exprs module do depend on it.)
        # For example, we're likely to tell it some modkeys, something
        # about this mode, the mousepoints, etc, and to respond more
        # fundamentally to whatever is returned.
        # (see also mouseover_statusbar_message, used in GLPane.set_selobj)
        method = getattr(obj, 'leftClick', None)
        if method:
            done = self.call_leftClick_method(method, obj, event)
            if done:
                return

        self.doObjectSpecificLeftDown(obj, event)

        self.w.win_update()
            #k (is this always desirable? note, a few cases above return
            # early just so they can skip it.)

        return # from SelectAtoms_GraphicsMode.leftDown

    def call_leftClick_method(self, method, obj, event):#bruce 071022 split this
                                                        #out
        """
        ###doc
        [return True if nothing more should be done to handle this event,
        False if it should be handled in the usual way]
        """
        gl_event_info = self.dragstart_using_GL_DEPTH( event, more_info = True)
        self._drag_handler_gl_event_info = gl_event_info
        farQ_junk, hitpoint, wX, wY, depth, farZ = gl_event_info
        del wX, wY, depth, farZ
        try:
            retval = method(hitpoint, event, self)
                ##e more args later -- mouseray? modkeys?
                # or use callbacks to get them?
                #bruce 061120 changed args from (hitpoint, self) to
                # (hitpoint, event, self) [where self is the mode object]
                # a new part of the drag_handler API is access by method to
                # self._drag_handler_gl_event_info [bruce 061206]
                #e (we might decide to change that to a dict so it's easily
                # extendable after that, or we might add more attrs
                # or methods of self which the method call is specifically
                # allowed to access as part of that API #e)
        except:
            print_compact_traceback("exception ignored "\
                                    "in %r.leftClick: " % (obj,))
            return True
        # If retval is None, the object just wanted to know about the click,
        # and now we handle it normally (including the usual special cases for
        # Atom, etc).
        # If retval is a drag handler (#doc), we let that object handle
        # everything about the drag. (Someday, all of our object/modkey-specific
        # code should be encapsulated into drag handlers.)
        # If retval is something else... not sure, so nevermind for now, just
        # assume it's a drag handler. ###@@@
        self.drag_handler = retval # needed even if this is None
            ##e should wrap with something which exception-protects all method
            # calls
        if self.drag_handler is not None:
            # We're using a drag_handler to override most of our behavior for
            # this drag.
            self.dragHandlerSetup(self.drag_handler, event)
                # does updates if needed
            return True
        return False

    # == LMB drag methods

    def leftDrag(self, event):
        """
        Event handler for all LMB+Drag events.
        """
        # Do not change the order of the following conditionals unless you know
        # what you're doing.  mark 060208.

        if self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            # [let this happen even for drag_handlers -- bruce 060728]
            return

        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            if self.drag_handler is not None:
##                print "possible bug (fyi): self.drag_handler is not None, "\
##                "but cursor_over_when_LMB_pressed == 'Empty Space'", \
##                      self.drag_handler #bruce 060728
                # bruce 070322: this is permitted now, and we let the
                # drag_handler handle it (for testmode & exprs module)...
                # however, I don't think this new feature will be made use of
                # yet, since testmode will instead sometimes override
                # get_obj_under_cursor to make it return a background object
                # rather than None, so this code will not set
                # cursor_over_when_LMB_pressed to 'Empty Space'.
                self.dragHandlerDrag(self.drag_handler, event)
                    # does updates if needed
            else:
                self.emptySpaceLeftDrag(event)
            return

        if self.o.modkeys is not None:
            # If a drag event has happened after the cursor was over an atom
            # and a modkey is pressed, do a 2D region selection as if the
            # atom were absent.
            # [let this happen even for drag_handlers -- bruce 060728]
            self.emptySpaceLeftDown(self.LMB_press_event)
            #bruce 060721 question: why don't we also do emptySpaceLeftDrag
            # at this point?
            return

        if self.drag_handler is not None:
            #bruce 060728
            self.dragHandlerDrag(self.drag_handler, event)
                # does updates if needed
            return

        obj = self.current_obj


        if obj is None: # Nothing dragged (or clicked); return.
            return

        self.doObjectSpecificLeftDrag(obj, event)

        # No gl_update() needed. Already taken care of.
        return

    def doObjectSpecificLeftDrag(self, object, event):
        """
        Call objectLeftDrag methods depending on the object instance.
        Overrides Select_basicGraphicsMode.doObjectSpecificLeftDrag

        @param object: object under consideration.
        @type  object: instance
        @param event: Left drag mouse event
        @type  event: QMouseEvent instance

        """
        #current object is not clicked but is dragged. Important to set this
        #flag. See Select_basicGraphicsMode.doObjectSpecificLeftUp for more
        # comments
        self.current_obj_clicked = False

        obj = object

        if isinstance(obj, Atom):
            if obj.is_singlet(): # Bondpoint
                self.singletDrag(obj, event)
            else: # Real atom
                self.atomDrag(obj, event)
        elif isinstance(obj, Bond): # Bond
            self.bondDrag(obj, event)
        elif isinstance(obj, Jig): # Jig
            self.jigDrag(obj, event)
        else: # Something else
            pass

    def posn_str(self, atm): #bruce 041123
        """
        Return the position of an atom
        as a string for use in our status messages.
        (Also works if given an atom's position vector itself -- kluge, sorry.)
        """
        try:
            x,y,z = atm.posn()
        except AttributeError:
            x,y,z = atm # kluge to accept either arg type
        return "(%.2f, %.2f, %.2f)" % (x,y,z)


    # == LMB up-click (button release) methods

    def leftUp(self, event):
        """
        Event handler for all LMB release events.
        """
        env.history.flush_saved_transients()

        if self.ignore_next_leftUp_event:
            # This event is the second leftUp of a double click, so ignore it.
            # [REVIEW: will resetting this flag here cause trouble for a triple
            #  click? I guess/hope not, since that also calls leftDouble and
            #  sets this. bruce comment 071022]
            self.ignore_next_leftUp_event = False
            self.update_selobj(event) # Fixes bug 1467. mark 060307.
            return

        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.emptySpaceLeftUp(event)
            return

        if self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            event = self.LMB_press_event
                # pretend the mouse didn't move -- this replaces our argument
                # event, for passing to *leftUp methods [bruce 060728 comment]

        if self.drag_handler:
            #bruce 060728
            # does updates if needed
            self.dragHandlerLeftUp(self.drag_handler, event)
            self.leftUp_reset_a_few_drag_vars() #k needed??
            return

        obj = self.current_obj

        if obj is None: # Nothing dragged (or clicked); return.
            return

        self.doObjectSpecificLeftUp(obj, event)

        self.leftUp_reset_a_few_drag_vars()
        #bruce 041130 comment: it forgets selatom, but doesn't repaint,
        # so selatom is still visible; then the next event will probably
        # set it again; all this seems ok for now, so I'll leave it alone.
        #bruce 041206: I changed my mind, since it seems dangerous to leave
        # it visible (seemingly active) but not active. So I'll repaint here.
        # In future we can consider first simulating a update_selatom at the
        # current location (to set selatom again, if appropriate), but it's
        # not clear this would be good, so *this* is what I won't do for now.
        #self.o.gl_update() #& Now handled in modkey*() methods. mark 060210.

        return # from SelectAtoms_GraphicsMode.leftUp

    def leftUp_reset_a_few_drag_vars(self):
        """
        reset a few drag vars at the end of leftUp --
        might not be safe to reset them all
        (e.g. if some are used by leftDouble)
        """
        #bruce 060728 split this out, guessed docstring
        self.baggage = []
        self.current_obj = None #bruce 041130 fix bug 230
            # later: i guess this attr had a different name then [bruce 060721]
        self.o.selatom = None #bruce 041208 for safety in case it's killed
        return

    # ===== START: Atom selection and dragging helper methods ==========

    drag_offset = V(0,0,0) # avoid tracebacks from lack of leftDown

    def atomSetup(self, a, event): #bruce 060316 added <event> argument,
                                   #for bug 1474
        """
        Setup for a click, double-click or drag event for real atom <a>.
        """
        #bruce 060316 set self.drag_offset to help fix bug 1474
        #(this should be moved into a method so singlets can call it too)--
        farQ, dragpoint = self.dragstart_using_GL_DEPTH( event)
        apos0 = a.posn()
        if farQ or vlen( dragpoint - apos0 ) > a.max_pixel_radius():
            # dragpoint is not realistic -- find a better one (using code
            #similar to innards of dragstart_using_GL_DEPTH)
            # [following comment appears to be obs, since +0.2 is no longer here
            #  [bruce 080605 comment]:]
            ###@@@ Note: + 0.2 is purely a guess (probably too big) --
            ###what it should be is a new method a.max_drawn_radius(),
            # which gives max distance from center of a drawn pixel, including
            #selatom, highlighting, wirespheres,
            # and maybe even the depth offset added by GLPane when it draws in
            # highlighted form (not sure, it might not draw
            # into depth buffer then...) Need to fix this sometime. Not high
            # priority, since it seems to work with 0.2,
            # and since higher than needed values would be basically ok anyway.
            #[bruce 060316]
            if env.debug(): # leave this in until we see it printed sometime
                print "debug: fyi: atomSetup dragpoint try1 was bad, %r "\
                      "for %r, reverting to ptonline" % (dragpoint, apos0)
            p1, p2 = self.o.mousepoints(event)
            dragpoint = ptonline(apos0, p1, norm(p2-p1))
            del p1,p2
        del farQ, event
        self.drag_offset = dragpoint - apos0 # some subclass drag methods can
                                             #use this with
                                             #self.dragto_with_offset()

        self.objectSetup(a)

        if len(self.o.assy.selatoms_list()) == 1:
            #bruce 060316 question: does it matter, in this case, whether <a>
            #is the single selected atom? is it always??
            self.baggage, self.nonbaggage = a.baggage_and_other_neighbors()
            self.drag_multiple_atoms = False
        else:
            #bruce 070412
            self.smooth_reshaping_drag = self.get_smooth_reshaping_drag()
            self.dragatoms, self.baggage, self.dragchunks = \
                self.get_dragatoms_and_baggage()
                # if no atoms in alist, dragatoms and baggage are empty lists,
                #which is good.
            self.drag_multiple_atoms = True
            self.maybe_use_bc = debug_pref("use bc to drag mult?",
                                           Choice_boolean_False) #bruce 060414

        # dragjigs contains all the selected jigs.
        self.dragjigs = self.o.assy.getSelectedJigs()

    def atomLeftDown(self, a, event):

        if not self.selection_locked():
            if not a.picked and self.o.modkeys is None:
                self.o.assy.unpickall_in_GLPane()
                a.pick()
            if not a.picked and self.o.modkeys == 'Shift':
                a.pick()

            if a.picked:
                self.cursor_over_when_LMB_pressed = 'Picked Atom'
            else:
                self.cursor_over_when_LMB_pressed = 'Unpicked Atom'

        self.atomSetup(a, event)

    def atomLeftUp(self, a, event): # Was atomClicked(). mark 060220.
        """
        Real atom <a> was clicked, so select, unselect or delete it based on
        the current modkey.
        - If no modkey is pressed, clear the selection and pick atom <a>.
        - If Shift is pressed, pick <a>, adding it to the current selection.
        - If Ctrl is pressed,  unpick <a>, removing it from the current
          selection.
        - If Shift+Control (Delete) is pressed, delete atom <a>.
        """

        if self.selection_locked():
            return

        self.deallocate_bc_in_use()

        if not self.current_obj_clicked:
            # Atom was dragged.  Nothing to do but return.
            if self.drag_multiple_atoms:
                self.set_cmdname('Move Atoms') #bruce 060412 added plural
                                               #variant
            else:
                self.set_cmdname('Move Atom')
            ##e note about command names: if jigs were moved too,
            ##"Move Selected Objects" might be better... [bruce 060412 comment]
            self.o.assy.changed() # mark 060227
            return

        nochange = False

        if self.o.modkeys is None:
            # isn't this redundant with the side effects in atomLeftDown??
            #[bruce 060721 question]
            self.o.assy.unpickall_in_GLPane() # was unpickatoms only;
                                              # I think unpickall makes more
                                              # sense [bruce 060721]
            if a.picked:
                nochange = True
                #bruce 060331 comment: nochange = True is wrong, since
                #the unpick might have changed something.
                # For some reason the gl_update occurs anyway, so I don't know
                # if this causes a real bug, so I didn't change it.
            else:
                a.pick()
                self.set_cmdname('Select Atom')
            env.history.message(a.getinfo())

        elif self.o.modkeys == 'Shift':
            if a.picked:
                nochange = True
            else:
                a.pick()
                self.set_cmdname('Select Atom')
            env.history.message(a.getinfo())

        elif self.o.modkeys == 'Control':
            if a.picked:
                a.unpick()
                self.set_cmdname('Unselect Atom')
                #bruce 060331 comment: I think a better term (in general)
                # would be "Deselect".
                #bruce 060331 bugfix: if filtering prevents the unpick,
                #don't print the message saying we unpicked it.
                # I also fixed the message to not use the internal jargon
                #'unpicked'.
                # I also added an orangemsg when filtering prevented
                #the unpick, as we have when it prevents a delete.
                if not a.picked:
                    # the unpick worked (was not filtered)
                    env.history.message("Deselected atom %r" % a)
                else:
                    msg = "Can't deselect atom %r due to selection filter."\
                        " Hit Escape to clear the filter." % (a)
                    env.history.message(orangemsg(msg))
            else: # Already unpicked.
                nochange = True

        elif self.o.modkeys == 'Shift+Control':
            result = self.delete_atom_and_baggage(event)
            env.history.message_no_html(result)
            self.set_cmdname('Delete Atom')
            return # delete_atom_and_baggage() calls win_update.

        else:
            print_compact_stack('Invalid modkey = "' + \
                                str(self.o.modkeys) + '" ')
            return

        if nochange: return
        self.o.gl_update()

    def atomLeftDouble(self): # mark 060308
        """
        Atom double click event handler for the left mouse button.
        """
        if self.selection_locked():
            return

        if self.o.modkeys == 'Control':
            self.o.assy.unselectConnected( [ self.obj_doubleclicked ] )
        elif self.o.modkeys == 'Shift+Control':
            self.o.assy.deleteConnected( self.neighbors_of_last_deleted_atom )
        else:
            self.o.assy.selectConnected( [ self.obj_doubleclicked ] )
        # the assy.xxxConnected routines do their own win_update or gl_update
        #as needed. [bruce 060412 comment]
        ##e set_cmdname would be useful here, conditioned on whether
        ##they did anything [bruce 060412 comment]
        return

    #===Drag related methods.
    def atomDrag(self, a, event):
        """
        Drag real atom <a> and any other selected atoms and/or jigs.
        @param event: is a drag event.
        """
        apos0 = a.posn()
        #bruce 060316 fixing bug 1474 --
        apos1 = self.dragto_with_offset(apos0, event, self.drag_offset )
        # xyz delta between new and current position of <a>.
        delta = apos1 - apos0


        if self.drag_multiple_atoms:
            self.drag_selected_atoms(delta)
        else:
            self.drag_selected_atom(a, delta) #bruce 060316 revised API
                                              #[##k could this case be handled
                                              # by the multiatom case??]

        self.drag_selected_jigs(delta)

        self.atomDragUpdate(a, apos0)
        return

    def atomDragUpdate(self, a, apos0):
        """
        Updates the GLPane and status bar message when dragging atom <a> around.
        <apos0> is the previous x,y,z position of <a>.
        """
        apos1 = a.posn()
        if apos1 - apos0:
            if debug_pref(
                #bruce 060316 made this optional, to see if it causes
                #lagging drags of C
                "show drag coords continuously",
                # non_debug needed for testing, for now [bruce comment]
                Choice_boolean_True, non_debug = True,
                prefs_key = "A7/Show Continuous Drag Coordinates"):

                msg = "dragged atom %r to %s" % (a, self.posn_str(a))
                this_drag_id = (self.current_obj_start, self.__class__.leftDrag)
                env.history.message(msg, transient_id = this_drag_id)
            self.current_obj_clicked = False # atom was dragged. mark 060125.
            self.o.gl_update()

    def drag_selected_atom(self, a, delta, computeBaggage = False): # bruce 060316 revised API for
                                            # uniformity and no redundant
                                            # dragto, re bug 1474
        """
        Drag real atom <a> by the xyz offset <delta>, adjusting its baggage
        atoms accordingly(how that's done depends on its other neighbor atoms).
        
        @param computeBaggage: If this is true, the baggage and non-baggage of
        the atom to be dragged will be computed in this method before dragging 
        the atom. Otherwise  it assumes that the baggage and non-baggage atoms 
        are up-to-date and are computed elsewhere , for example in 'atomSetUp'
        See a comment in the method that illustrates an example use. 
        @type recompueBaggage: boolean 
        @see: BuildAtomsPropertyManager._moveSelectedAtom()
        @see: SelectAtoms_Command.drag_selected_atom()  
        """
       
        apo = a.posn()
        ## delta = px - apo
        px = apo + delta
        
        #Example use of flag 'computeBaggage': If this method is called as a 
        #result of a value change in a UI element, the methods such as 
        #self.atomLeftDown or self.atomSetUp are not called. Those methods do 
        #the job of computing baggage etc. So a workaround is to instruct this 
        #method to recompute the baggage and non baggage before proceeding. 
        if computeBaggage:
            self.baggage, self.nonbaggage = a.baggage_and_other_neighbors()
        

        n = self.nonbaggage
            # n = real atoms bonded to <a> that are not singlets or
            # monovalent atoms.
            # they need to have their own baggage adjusted below.

        old = V(0,0,0)
        new = V(0,0,0)
            # old and new are used to compute the delta quat for the average
            # non-baggage bond [in a not-very-principled way,
            # which doesn't work well -- bruce 060629]
            # and apply it to <a>'s baggage

        for at in n:
            # Since adjBaggage() doesn't change at.posn(),
            #I switched the order for readability.
            # It is now more obvious that <old> and <new> have no impact
            # on at.adjBaggage().
            # mark 060202.
            at.adjBaggage(a, px) # Adjust the baggage of nonbaggage atoms.
            old += at.posn()-apo
            new += at.posn()-px

        # Handle baggage differently if <a> has nonbaggage atoms.
        if n: # If <a> has nonbaggage atoms, move and rotate its baggage atoms.
            # slight safety tweaks to old code, though we're about to add new
            #code to second-guess it [bruce 060629]
            old = norm(old) #k not sure if these norms make any difference
            new = norm(new)
            if old and new:
                q = Q(old,new)
                for at in self.baggage:
                    at.setposn(q.rot(at.posn()-apo)+px) # similar to adjBaggage,
                                                     #but also has a translation
            else:
                for at in self.baggage:
                    at.setposn(at.posn()+delta)
            #bruce 060629 for "bondpoint problem": treat that as an
            # initial guess --
            # now fix them better (below, after we've also moved <a> itself.)
        else: # If <a> has no nonbaggage atoms, just move each baggage atom
              # (no rotation).
            for at in self.baggage:
                at.setposn(at.posn()+delta)
        a.setposn(px)
        # [bruce 041108 writes:]
        # This a.setposn(px) can't be done before the at.adjBaggage(a, px)
        # in the loop before it, or adjBaggage (which compares a.posn() to
        # px) would think atom <a> was not moving.

        if n:
            #bruce 060629 for bondpoint problem
            a.reposition_baggage(self.baggage)
        return


    maybe_use_bc = False # precaution

    def drag_selected_atoms(self, offset):
        # WARNING: this (and quite a few other methods) is probably only called
        # (ultimately) from event handlers in SelectAtoms_GraphicsMode,
        # and probably uses some attrs of self that only exist in that mode.
        # [bruce 070412 comment]

        if self.maybe_use_bc and self.dragatoms and self.bc_in_use is None:
            #bruce 060414 move selatoms optimization (unfinished);
            # as of 060414 this never happens unless you set a debug_pref.
            # See long comment above for more info.
            bc = self.allocate_empty_borrowerchunk()
            self.bc_in_use = bc
            other_chunks, other_atoms = bc.take_atoms_from_list( self.dragatoms)
            self.dragatoms = other_atoms # usually []
            self.dragchunks.extend(other_chunks) # usually []
            self.dragchunks.append(bc)

        # Move dragatoms.
        for at in self.dragatoms:
            at.setposn(at.posn()+offset)

        # Move baggage (or slow atoms, in smooth-reshaping drag case)
        if not self.smooth_reshaping_drag:
            for at in self.baggage:
                at.setposn(at.posn() + offset)
        else:
            # kluge: in this case, the slow-moving atoms are the ones in
            # self.baggage.
            # We should probably rename self.baggage or not use the same
            # attribute for those.
            for at in self.baggage:
                f = self.offset_ratio(at, assert_slow = True)
                at.setposn(at.posn() + f * offset)

        # Move chunks. [bruce 060410 new feature, for optimizing moving of
        # selected atoms, re bugs 1828 / 1438]
        # Note, these might be chunks containing selected atoms (and no
        # unselected atoms, except baggage), not selected chunks.
        # All that matters is that we want to move them as a whole (as an
        # optimization of moving their atoms individually).
        # Note, as of 060414 one of them might be a BorrowerChunk.
        for ch in self.dragchunks:
            ch.move(offset)

        return
    # ===== END: Atom selection and dragging helper methods ==========

    #Various Drag related methods (some are experimental methods created
    #and maintained by Bruce.

    #@TODO: Bruce will be renaming/cleaningup method
    # OLD_get_dragatoms_and_baggage

    def get_dragatoms_and_baggage(self):
        """
        #doc... return dragatoms, baggage, dragchunks; look at
        self.smooth_reshaping_drag [nim];
        how atoms are divided between dragatoms & baggage is arbitrary and is
        not defined.
        [A rewrite of callers would either change them to treat those
        differently and change
        this to care how they're divided up (requiring a decision about
        selected baggage atoms),
        or remove self.baggage entirely.]
        """
        #bruce 060410 optimized this; it had a quadratic algorithm (part of the
        #cause of bugs 1828 / 1438), and other slownesses.
        # The old code was commented out for comparison [and later, 070412,
        # was removed].
        # [Since then, it was totally rewritten by bruce 070412.]
        #
        # Note: as of 060410, it looks like callers only care about the total
        # set of atoms in the two returned lists,
        # not about which atom is in which list, so the usefulness of having two
        # lists is questionable.
        # The old behavior was (by accident) that selected baggage atoms end up
        # only in the baggage list, not in dragatoms.
        # This was probably not intended but did not matter at the time.
        # The dragchunks optimization at the end [060410] changes this by
        # returning all atoms in dragatoms or dragchunks,
        # none in baggage. The new smooth reshaping feature [070412] may change
        # this again.

        if not self.smooth_reshaping_drag and self.get_use_old_safe_drag_code():
            # by default, for now: for safety, use the old drag code, if we're
            #not doing a smooth_reshaping_drag.
            # After FNANO I'll change the default for use_old_safe_drag_code
            # to False. [bruce 070413]
            return self.OLD_get_dragatoms_and_baggage()

        print "fyi: using experimental code for get_dragatoms_and_baggage;"\
              "smooth_reshaping_drag = %r" % self.smooth_reshaping_drag
            # Remove this print after FNANO when this code becomes standard,
            #at least for non-smooth_reshaping_drag case.
            # But consider changing the Undo cmdname, drag -> smooth drag or
            #reshaping drag. #e

        # rewrite, bruce 070412, for smooth reshaping and also for general
        # simplification:
        # [this comment and the partly redundant ones in the code will be
        # merged later]
        # - treat general case as smooth reshaping with different (trivial)
        # motion-function (though we'll optimize for that)
        # -- gather the same setup data either way. That will reduce
        # bug-differences between smooth reshaping and plain drags, and it might
        # help with other features in the future, like handling baggage better
        # when there are multiple selected atoms. - any baggage atom B has
        # exactly one neighbor S, and if that neighbor is selected(which is the
        # only time we might think of B as baggage here), we want B to move
        #   with S, regardless of smooth reshaping which might otherwise move
        #  them differently.
        #   This is true even if B itself is selected. So, for baggage atoms
        #  (even if selected) make a dict which points them to other selected
        # atoms. If we find cycles in that, those atoms must be closed for
        # selection (ie not indirectly bonded to unselected atoms, which is what
        # matters for smooth reshaping alg) or can be treated that way, so move
        # those atoms into a third dict for moving atoms which are not connected
        # to unmoving atoms.(These never participate in smooth reshaping
        # -- they always move
        #   with the drag.)
        # - the other atoms which move with the drag are the ones we find
        # later with N == N_max,
        #   and the other ones not bonded to unselected nonbaggage atoms,
        #   and all of them if
        #   we're not doing reshaping drag.
        # - then for all atoms which move with the drag (including some of
        #   the baggage,
        #   so rescan it to find those), we do the dragchunk optim;
        #   for the ones which move, but not with the drag, we store their
        #   motion-offset-ratio
        #   in a dict to be used during the drag (or maybe return it and let
        #   caller store it #k).
        #
        # - I think all the above can be simplified to the following:
        #   - expand selatoms to include baggage (then no need to remember
        #      which was which, since "monovalent" is good enough to mean
        #     "drag with neighbor", even for non-baggage)
        #   - point monovalent atoms in that set, whose neighbors are in it,
        #      to those neighbors(removing them from that set)
        #     (permitting cycles, which are always length 2)(during the drag,
        #      we'll move them with neighbors, then in future correct
        #      their posn for the motion of other atoms around those neighbors,
        #      as is now only done in single-atom dragging)
        #   - analyze remaining atoms in set for closeness (across bonds) to
        #     unselected atoms(permitting infinite dist == no connection to
        #     them)
        #   - then sort all the atoms into groups that move with the same
        #     offset, and find whole chunks in those groups (or at least in the
        #     group that moves precisely with the drag). (In future we'd use the
        #     whole-chunk and borrowerchunk optims (or equiv) for the
        #     slower-moving groups too. Even now, it'd be easy to use
        #     whole-chunk optim then, but only very rarely useful, so don't
        #     bother.)
        #
        # - finally, maybe done in another routine, selected movable jigs move
        #    in a way that depends on how
        #   their atoms move -- maybe their offset-ratio is the average of
        #   that of their atoms.

        # Ok, here we go:
        #   - expand selatoms to include baggage (then no need to remember
        #     which was which, since "monovalent" is good enough to mean
        #    "drag with neighbor", even for non-baggage)

        selatoms = self.o.assy.selatoms # maps atom.key -> atom
            # note: after this, we care only which atoms are in selatoms,
            # not whether they're selected --
            # in other words, you could pass some other dict in place of
            # selatoms if we modified the API for that,
            # and no code after this point would need to change.
        atoms_todo = dict(selatoms) # a copy which we'll modify in the
             # following loop,and later;
            # in general it contains all moving atoms we didn't yet decide how
            # to handle.
        monovalents = {} # maps a monvalent atom -> its neighbor,
                         #starting with baggage atoms we find
        boundary = {} # maps boundary atoms (selected, with unselected
                      #nonbaggage neighbor) to themselves
        ## unselected = {} # maps an unselected nonbaggage atom
        ##(next to one or more selected ones) to an arbitrary selected one
        for atom in selatoms.itervalues():
            baggage, nonbaggage = atom.baggage_and_other_neighbors()
            for b in baggage:
                monovalents[b] = atom # note: b (I mean b.key) might
                                      #also be in atoms_todo
            for n in nonbaggage:
                if n.key not in selatoms:
                    ## unselected[n] = atom
                    boundary[atom] = atom
                    break
            continue
        del selatoms
        # note: monovalents might overlap atoms_todo; we'll fix that later.
        # also it is not yet complete, we'll extend it later.

        #   - point monovalent atoms in that set (atoms_todo), whose neighbors
        #    are in it, to those neighbors
        #     (removing them from that set) (permitting cycles, which are
        #     always length 2 -- handled later ###DOIT)
        for atom in atoms_todo.itervalues():
            if len(atom.bonds) == 1:
                bond = atom.bonds[0]
                if bond.atom1.key in atoms_todo and bond.atom2.key in atoms_todo:
                    monovalents[atom] = bond.other(atom)
        for b in monovalents:
            atoms_todo.pop(b.key, None) # make sure b is not in atoms_todo,
                                        #if it ever was

        len_total = len(monovalents) + len(atoms_todo) # total number of atoms
                                                #considered, used in assertions

        #   - analyze remaining atoms in set (atoms_todo) for closeness
        # (across bonds) to unselected atoms
        #     (permitting infinite dist == no connection to them)
        # Do this by transclosing boundary across bonds to atoms in atoms_todo.
        layers = {} # will map N to set-of-atoms-with-N (using terminology of
                   #smooth-reshaping drag proposal)
        def collector( atom, dict1):
            """
            Add neighbors of atom which are in atoms_todo (which maps
            atom keys to atoms)to dict1 (which maps atoms to atoms).
            """
            for n in atom.neighbors():
                if n.key in atoms_todo:
                    dict1[n] = n
            return
        def layer_collector( counter, set):
            layers[counter] = set
            ## max_counter = counter # calling order is guaranteed by transclose
                # no good namespace to store this in -- grab it later
            return
        layers_union = transclose( boundary, collector, layer_collector)
        max_counter = len(layers)

        # Now layers_union is a subset of atoms_todo, and is the union of all
        # the layers; the other atoms in atoms_todo are the ones not connected
        # to unselected nonbaggage atoms.
        # And that's all moving atoms except the ones in monovalents.

        for atom in layers_union:
            atoms_todo.pop(atom.key) # this has KeyError if atom is not there,
                                    #which is a good check of the above alg.

        unconnected = {} # this will map atoms to themselves, which are not
            # connected to unselected atoms.
            # note that we can't say "it's atoms_todo", since that maps atom
            #keys to atoms.
            # (perhaps a mistake.)
        for atom in atoms_todo.itervalues():
            unconnected[atom] = atom
        ## del atoms_todo
            ## SyntaxError: can not delete variable 'atoms_todo' referenced
            ##in nested scope
            # not even if I promise I'll never use one of those references
            # again? (they're only in the local function defs above)
        atoms_todo = -1111 # error if used as a dict; recognizable/searchable
                           #value in a debugger

        assert len(monovalents) + len(layers_union) + len(unconnected) == \
               len_total
        assert len(layers_union) == sum(map(len, layers.values()))

        # Warning: most sets at this point map atoms to themselves, but
        # monovalents maps them to their neighbors
        # (which may or may not be monovalents).

        # Now sort all the atoms into groups that move with the same offset,
        # and find whole chunks
        # in those groups (or at least in the group that moves precisely
        # with the drag).
        # First, sort monovalents into unconnected ones (2-cycles, moved into
        # unconnected)and others (left in monovalents).

        cycs = {}
        for m in monovalents:
            if monovalents[m] in monovalents:
                assert monovalents[monovalents[m]] is m
                cycs[m] = m
                unconnected[m] = m
        for m in cycs:
            monovalents.pop(m)
        del cycs
        assert len(monovalents) + len(layers_union) + len(unconnected) == \
               len_total # again, now that we moved them around

        # Now handle the non-smooth_reshaping_drag case by expressing our
        # results from above
        # in terms of the smooth_reshaping_drag case.

        if not self.smooth_reshaping_drag:
            # throw away all the work we did above! (but help to catch bugs
            #in the above code, even so)
            unconnected.update(layers_union)
            for atom in monovalents:
                unconnected[atom] = atom
            assert len(unconnected) == len_total
            layers_union = {}
            layers = {}
            monovalents = {}
            max_counter = 0

        # Now we'll move unconnected and the highest layer (or layers?) with the
        # drag, move the other layers lesser amounts, and move monovalents with
        # their neighbors. Let's label all the atoms with their N, then pull
        # that back onto the monovalents, and add them to a layer or unconnected
        # as we do that, also adding a layer to unconnected if it moves the same
        # But the code is simpler if we move unconnected into the highest layer
        # instead of the other way around (noting that maybe max_counter == 0
        # and layers is empty). (unconnected can be empty too, but that is not
        # hard to handle.)

        labels = {}
        self.smooth_Max_N = max_counter # for use during the drag
        self.smooth_N_dict = labels # ditto (though we'll modify it below)

        if not max_counter:
            assert not layers
            layers[max_counter] = {}
        layers[max_counter].update(unconnected)
        del unconnected

        assert max_counter in layers
        for N, layer in layers.iteritems():
            assert N <= max_counter
            for atom in layer:
                labels[atom] = N
        N = layer = None
        del N, layer

        for m, n in monovalents.iteritems():
            where = labels[n]
            labels[m] = where
            layers[where][m] = m
        del monovalents

        # Now every atom is labelled and in a layer. Move the fast ones out,
        #keep the slower ones in layers.
        # (Note that labels itself is a dict of all the atoms, with their N
        #-- probably it could be our sole output
        #  except for the dragchunks optim. But we'll try to remain compatible
        #with the old API. Hmm, why not return
        #  the slow atoms in baggage and the fast ones in dragatoms/dragchunks?)

        fastatoms = layers.pop(max_counter)

        slowatoms = {}
        for layer in layers.itervalues():
            slowatoms.update(layer)
        layer = None
        del layer
        layers = -1112
        # slowatoms is not further used here, just returned

        assert len_total == len(fastatoms) + len(slowatoms)

        # Now find whole chunks in the group that moves precisely with the drag
        #(fastatoms).
        # This is a slightly modified version of:
        #bruce 060410 new code: optimize when all atoms in existing chunks are
        #being dragged.
        # (##e Soon we hope to extend this to all cases, by making new temporary
        # chunks to contain dragged atoms, invisibly to the user, taking steps
        #to not mess up existing chunks re their hotspot, display mode, etc.)
        atomsets = {} # id(mol) -> (dict from atom.key -> atom) for dragged
                      #atoms in that mol
        def doit(at):
            mol = at.molecule
            atoms = atomsets.setdefault(id(mol), {}) # dragged atoms which are
                                                     #in this mol, so far,
                                                     #as atom.key -> atom
            atoms[at.key] = at # atoms serves later to count them, to let us
                               #make fragments, and to identify the source mol
        for at in fastatoms:
            doit(at)
        dragatoms = []
        dragchunks = []
        for atomset in atomsets.itervalues():
            assert atomset
            mol = None # to detect bugs
            for key, at in atomset.iteritems():
                mol = at.molecule
                break # i.e. pick an arbitrary item... is there an easier way?
                      #is this way efficient?
            if len(mol.atoms) == len(atomset):
                # all mol's atoms are being dragged
                dragchunks.append(mol)
            else:
                # some but not all of mol's atoms are being dragged
                ##e soon we can optimize this case too by separating those
                ##atoms into a temporary chunk,
                # but for now, just drag them individually as before:
                dragatoms.extend(atomset.itervalues())
                    #k itervalues ok here? Should be, and seems to work ok.
                    #Faster than .values? Might be, in theory; not tested.
            continue

        assert len(fastatoms) == \
               len(dragatoms) + sum([len(chunk.atoms) for chunk in dragchunks])

        res = (dragatoms, slowatoms.values(), dragchunks) # these are all lists

        return res # from (NEW) get_dragatoms_and_baggage


    # By mark. later optimized and extended by bruce, 060410.
    # Still used 2007-11-15. [OLD_get_dragatoms_and_baggage]
    def OLD_get_dragatoms_and_baggage(self):
        """
        #doc... return dragatoms, baggage, dragchunks; look at
        self.smooth_reshaping_drag [nim];
        how atoms are divided between dragatoms & baggage is arbitrary and
        is not defined.
        [A rewrite of callers would either change them to treat those
        differently and change
        this to care how they're divided up (requiring a decision about
        selected baggage atoms),
        or remove self.baggage entirely.]
        """
        #bruce 060410 optimized this; it had a quadratic algorithm
        #(part of the cause of bugs 1828 / 1438), and other slownesses.
        # The old code was commented out for comparison
        #[and later, 070412, was removed].
        #
        # Note: as of 060410, it looks like callers only care about the total
        #set of atoms in the two returned lists, not about which atom is in
        # which list, so the usefulness of having two lists is questionable.
        # The old behavior was (by accident) that selected baggage atoms end up
        # only in the baggage list, not in dragatoms. This was probably not
        # intended but did not matter at the time. The dragchunks optimization
        # at the end [060410] changes this by returning all atoms in dragatoms
        # or dragchunks, none in baggage. The new smooth reshaping feature
        #[070412] may change this again.
        # WARNING: THIS IS NOT USED for smooth reshaping; see (non-OLD)
        #get_dragatoms_and_baggage for that.

        dragatoms = []
        baggage = []

        selatoms = self.o.assy.selatoms

        # Accumulate all the baggage from the selected atoms, which can include
        # selected atoms if a selected atom is another selected atom's baggage.
        # BTW, it is not possible for an atom to end up in self.baggage twice.

        for at in selatoms.itervalues():
            bag, nbag_junk = at.baggage_and_other_neighbors()
            baggage.extend(bag) # the baggage we'll keep.

        bagdict = dict([(at.key, None) for at in baggage])

        # dragatoms should contain all the selected atoms minus atoms that
        # are also baggage.
        # It is critical that dragatoms does not contain any baggage atoms or
        #they
        # will be moved twice in drag_selected_atoms(), so we remove them here.
        for key, at in selatoms.iteritems():
            if key not in bagdict: # no baggage atoms in dragatoms.
                dragatoms.append(at)

        # Accumulate all the nonbaggage bonded to the selected atoms.
        # We also need to keep a record of which selected atom belongs to
        # each nonbaggage atom.  This is not implemented yet, but will be needed
        # to get drag_selected_atoms() to work properly.  I'm commenting it out
        #for now.
        # mark 060202.
        ## [code removed, 070412]


        #bruce 060410 new code: optimize when all atoms in existing chunks
        #are being dragged.
        # (##e Soon we hope to extend this to all cases, by making new
        #temporary chunks to contain dragged atoms,
        #  invisibly to the user, taking steps to not mess up existing chunks re
        #their hotspot, display mode, etc.)
        atomsets = {} # id(mol) -> (dict from atom.key -> atom) for dragged
        #atoms in that mol
        def doit(at):
            mol = at.molecule
            atoms = atomsets.setdefault(id(mol), {}) # dragged atoms which are
                                                     #in this mol, so far, as
                                                     #atom.key -> atom
            atoms[at.key] = at # atoms serves later to count them, to let
                               #us make fragments, and to identify the source
                               #mol
        for at in dragatoms:
            doit(at)
        for at in baggage:
            doit(at)
        dragatoms = []
        baggage = [] # no longer used
        dragchunks = []
        for atomset in atomsets.itervalues():
            assert atomset
            mol = None # to detect bugs
            for key, at in atomset.iteritems():
                mol = at.molecule
                break # i.e. pick an arbitrary item... is there an easier way?
                      #is this way efficient?
            if len(mol.atoms) == len(atomset):
                # all mol's atoms are being dragged
                dragchunks.append(mol)
            else:
                # some but not all of mol's atoms are being dragged
                ##e soon we can optimize this case too by separating those atoms
                ##into a temporary chunk,
                # but for now, just drag them individually as before:
                dragatoms.extend(atomset.itervalues())
                    #k itervalues ok here? Should be, and seems to work ok.
                    #Faster than .values? Might be, in theory; not tested.
            continue

        return dragatoms, baggage, dragchunks  # return from
                                                #OLD_get_dragatoms_and_baggage;
                                                #this routine will be removed
                                                #later

    def offset_ratio(self, atom, assert_slow = False): #bruce 070412
        """
        When self.smooth_reshaping_drag, return the drag_offset_ratio for
        any atom (0 if we're not dragging it).
        """
        N = float(self.smooth_N_dict.get(atom, 0))
            # If found: from 1 to Max_N
        Max_N = self.smooth_Max_N # 0 or more (integer)
        if Max_N == 0:
            R = 0; f = 1
        else:
            R = (Max_N - N)/Max_N # ranges from just above 0 to just below 1,
                                  # in slow case, or can be exact 0 or 1 in
                                  # general
            f = (1-R**2)**2 # could be precomputed for each N, but that's
                            #probably not a big optim
        if assert_slow:
            assert 1 <= N < Max_N
            assert 0 < R < 1, "why is R == %r not strictly between 0 and 1?" \
                   "N = %r, Max_N = %r, atom = %r" % \
                   (R, N, Max_N, atom)
            assert 0 < f < 1
        else:
            assert 0 <= N <= Max_N
            assert 0 <= R <= 1
            assert 0 <= f <= 1
        return f


    #bruce 070525 shortened text (it made entire menu too wide)
    #@ Leaving this here before removing it. I'd like to discuss the proper
    #  way for this method should get the state of the "Reshape drag" checkbox
    #  in the "Build Atoms" Property Manager. --Mark 2008-04-06
    def get_smooth_reshaping_drag_OBSOLETE(self):
        res = debug_pref(
            "Drag reshapes selected atoms?",
            Choice_boolean_False,
            prefs_key = '_debug_pref_key:Drag reshapes selected atoms when \
            bonded to unselected atoms?',
            non_debug = True )
        return res

    def get_smooth_reshaping_drag(self):
        """
        Returns the state of the "Dragging reshapes selection" checkbox.

        @return: The state of the checkbox (True or False).
        @rtype:  boolean
        """
        return env.prefs[reshapeAtomsSelection_prefs_key]

    def get_use_old_safe_drag_code(self): #bruce 070413
        res = debug_pref("use old safe drag code, when not reshaping?",
                         Choice_boolean_True,
                             # asap, try changing this to False, and if all is well, remove the old code;
                             # but meanwhile, I'm removing non_debug [bruce 080416]
                         ## non_debug = True,
                         prefs_key = True )
        return res



    # ===== START: Bond selection, deletion and dragging helper methods =======


    def bondDrag(self, obj, event):
        # [bruce 060728 added obj arg, for uniformity; probably needed even more
        # in other Bond methods ##e]
        # If a LMB+Drag event has happened after selecting a bond in left*Down()
        # do a 2D region selection as if the bond were absent. This takes care
        # of both Shift and Control mod key cases.
        self.cursor_over_when_LMB_pressed = 'Empty Space'
        self.select_2d_region(self.LMB_press_event) # [i suspect this inlines
                                                    # something in another
                                                    # method -- bruce 060728]
        self.current_obj_clicked = False
        self.current_obj = None
        return


    def bondLeftDouble(self): # mark 060308.
        """
        Bond double click event handler for the left mouse button.
        """
        if self.o.modkeys == 'Control':
            self.o.assy.unselectConnected( [ self.obj_doubleclicked.atom1 ] )
        elif self.o.modkeys == 'Shift+Control':
            self.o.assy.deleteConnected( [ self.obj_doubleclicked.atom1,
                                           self.obj_doubleclicked.atom2 ] )
        else:
            self.o.assy.selectConnected( [ self.obj_doubleclicked.atom1 ] )
        # the assy.xxxConnected routines do their own win_update or gl_update
        #as needed. [bruce 060412 comment]
        return


    def bondLeftUp(self, b, event):
        """
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

        if self.selection_locked():
            return

        #& To do: check if anything changed (picked/unpicked) before
        #calling gl_update(). mark 060210.
        if self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane() # was unpickatoms() [bruce 060721]
            b.atom1.pick()
            b.atom2.pick()
            self.set_cmdname('Select Atoms')

        elif self.o.modkeys == 'Shift':
            b.atom1.pick()
            b.atom2.pick()
            self.set_cmdname('Select Atoms')
            #Bond class needs a getinfo() method to be called here. mark 060209.

        elif self.o.modkeys == 'Control':
            b.atom1.unpick()
            b.atom2.unpick()
            self.set_cmdname('Unselect Atoms')

        elif self.o.modkeys == 'Shift+Control':
            self.bondDelete(event)
                # <b> is the bond the cursor was over when the LMB was pressed.
                # use <event> to delete bond <b> to ensure that the cursor
                # is still over it.

        else:
            print_compact_stack('Invalid modkey = "' +
                                str(self.o.modkeys) + '" ')
            return

        self.o.gl_update()


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

    # ===== END: Bond selection and dragging helper methods ==========


    def jigSetup(self, j):
        """
        Setup for a click, double-click or drag event for jig <j>.
        """
        self.objectSetup(j)

        #bruce 070412
        self.smooth_reshaping_drag = self.get_smooth_reshaping_drag()

        self.dragatoms, self.baggage, self.dragchunks = \
            self.get_dragatoms_and_baggage()
            # if no atoms are selected, dragatoms and baggage
            #are empty lists, which is good.

        # dragjigs contains all the selected jigs.
        self.dragjigs = self.o.assy.getSelectedJigs()

    def drag_selected_jigs(self, offset):
        for j in self.dragjigs:
            if self.smooth_reshaping_drag:
                # figure out a modified offset by averaging the offset-ratio for
                #this jig's atoms
                ratio = average_value(map(self.offset_ratio, j.atoms),
                                      default = 1.0)
                offset = offset * ratio # not *=, since it's a mutable Numeric
                                        #array!
            j.move(offset)


    def jigDrag(self, j, event):
        """
        Drag jig <j> and any other selected jigs or atoms.
        <event> is a drag event.
        """
        #bruce 060316 commented out deltaMouse since it's not used in this
        #routine
          ##deltaMouse = V(event.pos().x() - self.o.MousePos[0],
          ##                self.o.MousePos[1] - event.pos().y(), 0.0)

        #bruce 060316 replaced old code with dragto (equivalent)
        jig_NewPt = self.dragto( self.jig_MovePt, event)

        # Print status bar msg indicating the current move offset.
        if 1:
            self.moveOffset = jig_NewPt - self.jig_StartPt
            msg = "Offset: [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.moveOffset[0],
                                                             self.moveOffset[1],
                                                             self.moveOffset[2])
            env.history.statusbar_msg(msg)

        offset = jig_NewPt - self.jig_MovePt

        self.drag_selected_atoms(offset)
        self.drag_selected_jigs(offset)

        self.jig_MovePt = jig_NewPt

        self.current_obj_clicked = False # jig was dragged.
        self.o.gl_update()

    # == LMB double-click method

    def leftDouble(self, event): # mark 060126.
        """
        Double click event handler for the left mouse button.

        @note: Also called for a triple click event.
        These can be distinguished using the flag
        self.glpane.tripleClick.
        """

        self.ignore_next_leftUp_event = True

        if isinstance(self.obj_doubleclicked, Atom):
            if self.obj_doubleclicked.is_singlet():
                self.singletLeftDouble()
                return
            else:
                self.atomLeftDouble()

        if isinstance(self.obj_doubleclicked, Bond):
            self.bondLeftDouble()

        if isinstance(self.obj_doubleclicked, Jig):
            self.jigLeftDouble()

    # == end of LMB event handler methods

    def update_cursor_for_no_MB(self):
        """
        Update the cursor for 'Select Atoms' mode (SelectAtoms_GraphicsMode)
        """
        ## print "SelectAtoms_GraphicsMode.update_cursor_for_no_MB(): button=",\
        ## self.o.button, ", modkeys=", self.o.modkeys

        if self.w.selection_filter_enabled:
            self.update_cursor_for_no_MB_selection_filter_enabled()
        else:
            self.update_cursor_for_no_MB_selection_filter_disabled()

    def update_cursor_for_no_MB_selection_filter_disabled(self):
        """
        Update the cursor for when the Selection Filter is disabled (default).
        """
        if self.o.modkeys is None:
            self.o.setCursor(self.w.SelectAtomsCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.SelectAtomsAddCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.SelectAtomsSubtractCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB():"\
                  "Invalid modkey = ", self.o.modkeys
        return

    def update_cursor_for_no_MB_selection_filter_enabled(self):
        """
        Update the cursor for when the Selection Filter is enabled.
        """
        if self.o.modkeys is None:
            self.o.setCursor(self.w.SelectAtomsFilterCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.SelectAtomsAddFilterCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.SelectAtomsSubtractFilterCursor)
        elif self.o.modkeys == 'Shift+Control':
            # Fixes bug 1604. mark 060303.
            self.o.setCursor(self.w.DeleteAtomsFilterCursor)
        else:
            print "Error in update_cursor_for_no_MB(): "\
                  "Invalid modkey = ", self.o.modkeys
        return

    def rightShiftDown(self, event):
        _superclass.rightShiftDown(self, event)
        self.o.setCursor(self.w.SelectAtomsCursor)

    def rightCntlDown(self, event):
        _superclass.rightCntlDown(self, event)
        self.o.setCursor(self.w.SelectAtomsCursor)

    def update_selatom(self,
                       event,
                       singOnly = False,
                       resort_to_prior = True):
        """
        Keep glpane.selatom up-to-date, as atom under mouse based on <event>;
        When <singOnly> is True, only keep singlets up-to-date.
        [not sure what that phrase means -- bruce 060726]

        Note: this method changes glpane.selatom but it
        never changes glpane.selobj. It is deprecated
        in favor of using update_selobj and glpane.selobj alone.

        When <resort_to_prior> is true (the default), then if
        selobj is not presently known, use the prior value;
        otherwise use None. (As of 071025 no callers change
        the default behavior.)

        Warning: glpane.selobj is not updated except by paintGL,
        and glpane.selatom is based on it, so after a mouse motion
        it will not become correct until after the next repaint.
        """
        #bruce 050124 split this out of bareMotion so options can vary
        #bruce 071025 revised docstring, removed msg_about_click option

        glpane = self.o
        if event is None:
            # event (and thus its x,y position) is not known
            # [bruce 050612 added this possibility]
            known = False
        else:
            known = self.update_selobj(event)
            # this might do gl_update (but the paintGL triggered by that
            # only happens later!),
            # and (when it does) might not know the correct obj...
            # so it returns True iff it did know the correct obj (or None) to
            #store into glpane.selobj, False if not.
        assert known in [False, True], \
               "known should be False or True, not %r" % (known,)

        # If not known, use None or use the prior one? This is up to the caller
        # since the best policy varies. Default is resort_to_prior = True since
        # some callers need this and I did not yet scan them all and fix them.
        # [bruce circa 050610]
        # Update: it might be that resort_to_prior = True is the only
        # correct value for any caller. Not sure. For now, leave in the code
        # for both ways. [bruce 071025]

        selobj = glpane.selobj

        if not known:
            if resort_to_prior:
                pass # stored one is what this says to use, and is what we'll
                     # use
                ## print "resort_to_prior using",glpane.selobj
                    # [this is rare, I guess since paintGL usually has time
                    #  to run after bareMotion before clicks]
            else:
                selobj = None
        oldselatom = glpane.selatom
        atm = selobj
        if not isinstance(atm, Atom):
            atm = None
        if atm is not None and (atm.element is Singlet or not singOnly):
            pass # we'll use this atm as the new selatom
        else:
            atm = None # otherwise we'll use None
        glpane.selatom = atm

        if glpane.selatom is not oldselatom:
            # update display (probably redundant with side effect of
            # update_selobj; ok if it is, and I'm not sure it always is #k)
            glpane.gl_update_highlight() # draws selatom too, since its chunk
            # is not hidden [comment might be obs, as of 050610]

        return # from update_selatom


    def update_selatom_and_selobj(self, event = None): #bruce 050705
        """
        update_selatom (or cause this to happen with next paintGL);
        return consistent pair (selatom, selobj);
        atom_debug warning if inconsistent
        """
        #e should either use this more widely, or do it in selatom itself,
        #or convert entirely to using only selobj.
        self.update_selatom( event) # bruce 050612 added this --
                                    #not needed before since bareMotion did it
                                    #(I guess).
            ##e It might be better to let set_selobj callback (NIM, but needed
            ##for sbar messages) keep it updated.
            #
            # See warnings about update_selatom's delayed effect, in its
            #docstring or in leftDown. [bruce 050705 comment]
        selatom = self.o.selatom
        selobj = self.o.selobj #bruce 050705 -- #e it might be better to use
                               #selobj alone (selatom should be derived from it)
        if selatom is not None:
            if selobj is not selatom:
                if debug_flags.atom_debug:
                    print "atom_debug: selobj %r not consistent with" \
                         "selatom %r -- using selobj = selatom" % (selobj,
                                                                   selatom)
                selobj = selatom # just for our return value, not changed in
                                 #GLPane (self.o)
        else:
            pass #e could check that selobj is reflected in selatom if an atom,
                 #but might as well let update_selatom do that,
                 #esp. since it behaves differently for singlets
        return selatom, selobj


    def get_real_atom_under_cursor(self, event):
        """
        If the object under the cursor is a real atom, return it.
        Otherwise, return None.
        """
        obj = self.get_obj_under_cursor(event)
        if isinstance(obj, Atom):
            if not obj.is_singlet():
                return obj
        return None


    def set_selection_filter(self, enabled):
        """
        Set/ Unset selection filter. Subclasses should override this
        @param: enabled: boolean that decides whether to turn
        selection filter on or off.
        """
        #REVIEW: Need to be in SelectAtoms_basicCommand class?
        pass

    def delete_atom_and_baggage(self, event):
        """
        If the object under the cursor is an atom, delete it and any baggage.
        Return the result of what happened.
        """
        a = self.get_real_atom_under_cursor(event)

        if a is None:
            return None

        if a.filtered(): # mark 060304.
            # note: bruce 060331 thinks refusing to delete filtered atoms,
            #as this does, is a bad UI design;
            # fo details, see longer comment on similar code in
            #delete_at_event (ops_select.py).
            # (Though when highlighting is disabled, it's arguable that this
            #is more desirable than bad -- conceivably.)
            #bruce 060331 adding orangemsg, since we should warn user we didn't
            #do what they asked.
            msg = "Cannot delete " + str(a) + " since it is being filtered."\
                " Hit Escape to clear the selection filter."
            env.history.message(orangemsg(msg))
            return None

        a.deleteBaggage()
        result = "deleted %r" % a
        self.neighbors_of_last_deleted_atom = a.realNeighbors()
        a.kill()
        self.o.selatom = None #bruce 041130 precaution
        self.o.assy.changed()
        self.w.win_update()
        return result

    pass

# ==

class SelectAtoms_GraphicsMode(SelectAtoms_basicGraphicsMode):
    """
    @see: Select_GraphicsMode
    """
    def __init__(self, command):
        self.command = command
        glpane = self.command.glpane
        SelectAtoms_basicGraphicsMode.__init__(self, glpane)
        return

    # (the rest would come from GraphicsMode if post-inheriting it worked,
    #  or we could split it out of GraphicsMode as a post-mixin to use there
    #  and here)

    def _get_commandSequencer(self):
        return self.command.commandSequencer

    commandSequencer = property( _get_commandSequencer)

    def set_cmdname(self, name):
        self.command.set_cmdname(name)
        return

    def _get_highlight_singlets(self):
        return self.command.highlight_singlets

    def _set_highlight_singlets(self, val):
        self.command.highlight_singlets = val

    highlight_singlets = property( _get_highlight_singlets,
                                   _set_highlight_singlets )

    pass

# end




