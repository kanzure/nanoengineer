# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
selectMolsMode.py 

$Id$


History:

Some things that need cleanup in this code [bruce 060721 comment]: ####@@@@

- redundant use of glRenderMode (see comment where that is used)

- drag algorithms for various object types and modifier keys are split over lots of methods
with lots of common but not identical code. For example, a set of atoms and jigs can be dragged
in the same way, by two different pieces of code depending on whether an atom or jig in the set
was clicked on. If this was cleaned up, so that objects clicked on would answer questions about
how to drag them, and if a drag_handler object was created to handle the drag (or the object itself
can act as one, if only it is dragged and if it knows how), the code would be clearer, some bugs
would be easier to fix, and some NFRs easier to implement. [bruce 060728 -- I'm adding drag_handlers
for use by new kinds of draggable or buttonlike things (only in selectAtoms mode and subclasses),
but not changing how old dragging code works.]

- Ninad 070216 split this out of selectMode.py 
"""

from PyQt4.Qt import QMouseEvent

import env

from modes import basicMode
from bonds import Bond
from chem import Atom
from selectMode import selectMode
from selectMode import DRAG_STICKINESS_LIMIT
from utilities.Log import orangemsg
from chunk import molecule

from debug import print_compact_stack
from debug import print_compact_traceback

from constants import yellow
from constants import orange

from VQT import V, vlen

import time

_superclass = selectMode

class selectMolsMode(selectMode):
    "Select Chunks mode"
    modename = 'SELECTMOLS'
    default_mode_status_text = "Mode: Select Chunks"

    def Enter(self): 
        basicMode.Enter(self)
        self.o.assy.selectChunksWithSelAtoms_noupdate() # josh 10/7 to avoid race in assy init     
        self.hover_highlighting_enabled = True

    def init_gui(self):
        _superclass.init_gui(self)
        self.w.toolsSelectMoleculesAction.setChecked(1) # toggle on the "Select Chunks" tools icon
        self.w.dashboardHolder.hide()
        #self.w.dashboardHolder.setWidget(self.w.selectMolDashboard)
        #self.w.selectMolDashboard.show()

    def restore_gui(self):
        self.w.toolsSelectMoleculesAction.setChecked(0) # toggle on the "Select Chunks" tools icon
        #self.w.selectMolDashboard.hide()

    def leftDouble(self, event):
        """
	Switch to Build Atoms mode when user double clicks on an object
	@note: pre Alpha9, it used to enter Move mode upon double clicking. 
	Since Alpha9, it enters Deposit mode if you double click on an object
	"""

        #@@@ ninad20070510 - based on discussion with Mark, don't enter deposit
        #mode when cursor is on empty space. (Otherwise, i.e. when its over an 
        #object, enter deposit mode.        
        #Following needs to be changed after implementation of objects like 
        #points, lines etc , which don't need deposit mode. 

        if self.cursor_over_when_LMB_pressed != 'Empty Space':
            self.commandSequencer.userEnterCommand('DEPOSIT')
        return

    def update_cursor_for_no_MB(self):
        '''Update the cursor for 'Select Chunks' mode (selectMolsMode).
        '''

        # print "selectMolsMode.update_cursor_for_no_MB(): button=",self.o.button,"modkeys=",self.o.modkeys

        if self.o.modkeys is None:
##            print "seeing modkeys is None",self.w.MolSelCursor #bruce 070628
##            self.o.gl_update()  #bruce 070628, didn't help
            self.o.setCursor(self.w.MolSelCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.MolSelAddCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.MolSelSubCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB(): Invalid modkey=", self.o.modkeys
        return

    def rightShiftDown(self, event):
        basicMode.rightShiftDown(self, event)

    def rightCntlDown(self, event):          
        basicMode.rightCntlDown(self, event)

    # moved here from modifyMode.  mark 060303.
    call_makeMenus_for_each_event = True #bruce 050914 enable dynamic context menus [fixes an unreported bug analogous to 971]

    # moved here from modifyMode.  mark 060303.
    def makeMenus(self): # mark 060303.

        self.Menu_spec = []

        if self.o.assy.selmols:
            # Menu items added when there are selected chunks.
            self.Menu_spec = [
                ('Change Color of Selected Chunks...', self.w.dispObjectColor),
                ('Reset Color of Selected Chunks', self.w.dispResetChunkColor),
                ('Reset Atoms Display of Selected Chunks', self.w.dispResetAtomsDisplay),
                ('Show Invisible Atoms of Selected Chunks', self.w.dispShowInvisAtoms),
                ('Hide Selected Chunks', self.o.assy.Hide),
            ]

        # Enable/Disable Jig Selection.
        # This is duplicated in selectMode.makeMenus() and depositMode.makeMenus().
        if self.o.jigSelectionEnabled:
            self.Menu_spec.extend( [('Enable Jig Selection',  self.toggleJigSelection, 'checked')])
        else:
            self.Menu_spec.extend( [('Enable Jig Selection',  self.toggleJigSelection, 'unchecked')])

        self.Menu_spec.extend( [
            # mark 060303. added the following:
            None,
            ('Change Background Color...', self.w.dispBGColor),
        ])

        self.debug_Menu_spec = [
            ('debug: invalidate selection', self.invalidate_selection),
            ('debug: update selection', self.update_selection),
        ]

    # moved here from modifyMode.  mark 060303.
    def invalidate_selection(self): #bruce 041115 (debugging method)
        "[debugging method] invalidate all aspects of selected atoms or mols"
        for mol in self.o.assy.selmols:
            print "already valid in mol %r: %r" % (mol, mol.invalid_attrs())
            mol.invalidate_everything()
        for atm in self.o.assy.selatoms.values():
            atm.invalidate_everything()

    # moved here from modifyMode.  mark 060303.
    def update_selection(self): #bruce 041115 (debugging method)
        """[debugging method] update all aspects of selected atoms or mols;
        no effect expected unless you invalidate them first
        """
        for atm in self.o.assy.selatoms.values():
            atm.update_everything()
        for mol in self.o.assy.selmols:
            mol.update_everything()
        return

    #Chunk selection helper methods. 

    def atomLeftDown(self, a, event):        
        m = a.molecule
        if not m.picked and self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane() # was unpickatoms and unpickparts [bruce 060721]
                # Note: a comment said that this was intended to unpick (among other things) jigs.
                # It will, since they are selectable in GLPane.
            m.pick()
            self.o.selobj =  None
        if not m.picked and self.o.modkeys == 'Shift':
            m.pick()
            self.o.selobj =  None

        if m.picked:
            self.cursor_over_when_LMB_pressed = 'Picked Chunk'
        else:
            self.cursor_over_when_LMB_pressed = 'Unpicked Chunk'

        self.w.win_update()


    def atomLeftUp(self, a, event):
        """
        Real atom <a> was clicked, so select, unselect or delete 
        ITS CHUNK  based on the current modkey.
        - If no modkey is pressed, clear the selection and pick atom's chunk 
          <m>.
        - If Shift is pressed, pick <m>, adding it to the current selection.
        - If Ctrl is pressed,  unpick <m>, removing it from the current 
          selection.
        - If Shift+Control (Delete) is pressed, delete atom <m>.
        """

        m = a.molecule

        self.deallocate_bc_in_use()

        if not self.current_obj_clicked:
            # Atom was dragged.  Nothing to do but return.
            if self.drag_multiple_atoms:
                self.set_cmdname('Move Atoms') #bruce 060412 added plural variant
            else:
                self.set_cmdname('Move Atom')
            ##e note about command names: if jigs were moved too, "Move Selected Objects" might be better... [bruce 060412 comment]
            self.o.assy.changed() # mark 060227
            return

        nochange = False

        if self.o.modkeys is None:
            # isn't this redundant with the side effects in atomLeftDown?? [bruce 060721 question]
            self.o.assy.unpickall_in_GLPane() # was unpickatoms only; I think unpickall makes more sense [bruce 060721]
            if m.picked:
                nochange = True
                #bruce 060331 comment: nochange = True is wrong, since the unpick might have changed something.
                # For some reason the gl_update occurs anyway, so I don't know if this causes a real bug, so I didn't change it.
            else:
                m.pick()
                self.set_cmdname('Select Atom')
            env.history.message(a.getinfo())

        elif self.o.modkeys == 'Shift':
            if m.picked: 
                nochange = True
            else:
                m.pick()
                self.set_cmdname('Select Atom')
            env.history.message(a.getinfo())

        elif self.o.modkeys == 'Control':
            if m.picked:
                m.unpick()
                self.set_cmdname('Unselect Atom') #bruce 060331 comment: I think a better term (in general) would be "Deselect".
                #bruce 060331 bugfix: if filtering prevents the unpick, don't print the message saying we unpicked it.
                # I also fixed the message to not use the internal jargon 'unpicked'.
                # I also added an orangemsg when filtering prevented the unpick, as we have when it prevents a delete.
                if not m.picked:
                    # the unpick worked (was not filtered)
                    env.history.message("Deselected atom %r" % a)
                else:
                    msg = "Can't deselect atom %r due to selection filter. " \
                        "Hit Escape to clear the filter." % a
                    env.history.message(orangemsg(msg))
            else: # Already unpicked.
                nochange = True

        elif self.o.modkeys == 'Shift+Control':
            result = self.delete_atom_and_baggage(event)
            env.history.message_no_html(result)
            self.set_cmdname('Delete Atom')
            return # delete_atom_and_baggage() calls win_update.

        else:
            print_compact_stack('Invalid modkey = "' + str(self.o.modkeys) + '" ')
            return

        if nochange: return
        self.o.gl_update()    

    def bondLeftDown(self, b, event):
        """Left down  on a Bond <b> , so select or unselect its chunk or 
        delete the bond <b>  based on the current modkey.
        - If no modkey is pressed, clear the selection and pick <b>'s chunk(s).
        - If Shift is pressed, pick <b>'s chunk(s) , adding them to the current 
          selection.
        - If Ctrl is pressed,  unpick <b>'s chunk(s), removing them from the 
          current selection.
        - If Shift+Control (Delete) is pressed, delete chunk(s) associated 
          with this bond <b>. <event> is a LMB release event.
        """

        self.cursor_over_when_LMB_pressed = 'Bond'
        self.bondSetup(b)

        chunk1 = b.atom1.molecule
        chunk2 = b.atom2.molecule

        if not (chunk1.picked or chunk2.picked) and self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane() # was unpickatoms() [bruce 060721]

            if chunk1 is chunk2:
                chunk1.pick()
            else:
                chunk1.pick()
                chunk2.pick()

            self.o.selobj =  None   
            self.set_cmdname('Select Chunks')

        if not (chunk1.picked or chunk2.picked) and self.o.modkeys == 'Shift':
            if chunk1 is chunk2:
                chunk1.pick()
            else:
                chunk1.pick()
                chunk2.pick()

            self.o.selobj =  None
            self.set_cmdname('Select Chunks')

        if chunk1.picked or chunk2.picked:
            self.cursor_over_when_LMB_pressed = 'Picked Chunk'
        else:
            self.cursor_over_when_LMB_pressed = 'Unpicked Chunk'


        self.o.gl_update()

    def bondLeftUp(self, b, event):

        chunk1 = b.atom1.molecule
        chunk2 = b.atom2.molecule

        if self.o.modkeys == 'Control':
            if chunk1 is chunk2:
                chunk1.unpick()
            else:
                chunk1.unpick()
                chunk2.unpick()

            self.o.selobj =  None
            self.set_cmdname('Unselect Chunks')

        if self.o.modkeys == 'Shift+Control':
            chunk1.kill()
            chunk2.kill()
            self.o.selobj =  None

        pass

    # == Singlet helper methods
    def singletLeftDown(self, s, event):
        self.atomLeftDown(s, event)
        return

    def singletLeftUp(self, s, event):
        self.atomLeftUp(s, event)
        return

    # == LMB down-click (button press) methods


    def leftDown(self, event):
        '''Event handler for all LMB press events.'''

        self.set_cmdname('ChunkClick') #e (this should be set again later (during the same drag) to a more specific command name)

        self.reset_drag_vars()
        env.history.statusbar_msg(" ") # get rid of obsolete msg from bareMotion [bruce 050124; imperfect #e]

        self.LMB_press_event = QMouseEvent(event) # Make a copy of this event and save it. 
            # We will need it later if we change our mind and start selecting a 2D region in leftDrag().
            # Copying the event in this way is necessary because Qt will overwrite <event> later (in 
            # leftDrag) if we simply set self.LMB_press_event = event.  mark 060220.

        #bruce 060315 replacing LMB_press_pt with LMB_press_pt_xy
        self.LMB_press_pt_xy = (event.pos().x(), event.pos().y())
            # <LMB_press_pt_xy> is the position of the mouse in window coordinates when the LMB was pressed.
            # Used in mouse_within_stickiness_limit (called by leftDrag() and other methods).
            # We don't bother to vertically flip y using self.height (as mousepoints does),
            # since this is only used for drag distance within single drags.

        self.pseudoMoveModeLeftDown(event) 

        obj = self.get_obj_under_cursor(event)
            # If highlighting is turned on, get_obj_under_cursor() returns atoms, singlets, bonds, jigs,
            # or anything that can be highlighted and end up in glpane.selobj. [bruce revised this comment, 060725]
            # If highlighting is turned off, get_obj_under_cursor() returns atoms and singlets (not bonds or jigs).
            # [not sure if that's still true -- probably not. bruce 060725 addendum]
        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            return

        if 1:
            #bruce 060725 new feature. Any selobj can decide how clicks/drags on it should behave, if it wants to.
            # Normally this will not apply to an Atom, Bond, or Jig, but there's no reason it couldn't in theory.
            # The API is experimental and is very likely to be modified, so don't depend on it yet.
            # For example, we're likely to tell it some modkeys, something about this mode, the mousepoints, etc,
            # and to respond more fundamentally to whatever is returned. ###@@@
            # (see also mouseover_statusbar_message, used in GLPane.set_selobj)
            method = getattr(obj, 'leftClick', None)
            if method:
                ## farQ_junk, hitpoint = self.dragstart_using_GL_DEPTH( event) ###k safe?
                gl_event_info = self.dragstart_using_GL_DEPTH( event, more_info = True) #bruce 061206 revised this, adding more_info
                self._drag_handler_gl_event_info = gl_event_info 
                farQ_junk, hitpoint, wX, wY, depth, farZ = gl_event_info
                del wX, wY, depth, farZ
                try:
                    retval = method(hitpoint, event, self) ##e more args later -- mouseray? modkeys? or use callbacks to get them?
                        #bruce 061120 changed args from (hitpoint, self) to (hitpoint, event, self) [where self is the mode object]
                        # a new part of the drag_handler API is access by method to self._drag_handler_gl_event_info [bruce 061206]
                        #e (we might decide to change that to a dict so it's easily extendable after that, or we might add more attrs
                        #   or methods of self which the method call is specifically allowed to access as part of that API #e)
                except:
                    print_compact_traceback("exception ignored in %r.leftClick: " % (obj,))
                    return # no update or other action here
                # If retval is None, the object just wanted to know about the click, and now we handle it normally
                # (including the usual special cases for Atom, etc).
                # If retval is a drag handler (#doc), we let that object handle everything about the drag.
                # (Someday, all of our object/modkey-specific code should be encapsulated into drag handlers.)
                # If retval is something else... not sure, so nevermind for now, just assume it's a drag handler. ###@@@
                self.drag_handler = retval # needed even if this is None
                    ##e should wrap with something which exception-protects all method calls
                if self.drag_handler is not None:
                    # We're using a drag_handler to override most of our behavior for this drag.
                    self.dragHandlerSetup(self.drag_handler, event) # does updates if needed
                    # don't do the rest of this method:
                    return

        self.doObjectSpecificLeftDown(obj, event)

        self.w.win_update() #k (is this always desirable? note, a few cases above return early just so they can skip it.)
        return # from selectMolsMode.leftDown


    def leftDrag(self, event):
        """ 
	Overrides leftdrag method of superclass.
	A) If the mouse cursor was on Empty space during left down, it draws 
	a selection curve 
	B) If it was on an object, it translates translates the selection 
	(free drag translate).This is called 'pseudo move mode' for convenience. 
	Note that NE1 still remains in the selectMolsMode while doing this. 
	It calls separate method for objects that implement drag handler API 

	@param  event: mouse left drag event
	@see : selectMode.leftDrag
	@see : selectMolsMode.pseudoMoveModeLeftDown
	@see : selectMolsMode.pseudoMoveModeLeftDrag

	"""

        #Copying some drag_handler checker code from selectAtomsMode (with some 
        # modifications)the comment below bu bruce070322 is just copied over 
        #as it is useful information --  Ninad20070601

        if self.cursor_over_when_LMB_pressed == 'Empty Space': 
            if self.drag_handler is not None:
##                print "possible bug (fyi): self.drag_handler is not None, but cursor_over_when_LMB_pressed == 'Empty Space'", \
##                      self.drag_handler #bruce 060728
                # bruce 070322: this is permitted now, and we let the drag_handler handle it (for testmode & exprs module)...
                # however, I don't think this new feature will be made use of yet, since testmode will instead sometimes
                # override get_obj_under_cursor to make it return a background object rather than None,
                # so this code will not set cursor_over_when_LMB_pressed to 'Empty Space'.
                self.dragHandlerDrag(self.drag_handler, event) # does updates if needed
            else:
                self.emptySpaceLeftDrag(event)            
            return

        if self.o.modkeys is not None:
            # If a drag event has happened after the cursor was over an atom and a modkey is pressed,
            # do a 2D region selection as if the atom were absent.
            # [let this happen even for drag_handlers -- bruce 060728]
            self.emptySpaceLeftDown(self.LMB_press_event)
            #bruce 060721 question: why don't we also do emptySpaceLeftDrag at this point?
            return

        if self.drag_handler is not None:
            movables = self.o.assy.getSelectedMovables()
            if movables:
                if self.drag_handler not in movables:
                    self.dragHandlerDrag(self.drag_handler, event) 
                    return
                elif len(movables)== 1:
                    self.dragHandlerDrag(self.drag_handler, event)
                    return                    

        if self.o.assy.getSelectedMovables():
            #Free Drag Translate the selected (movable) objects.
            self.pseudoMoveModeLeftDrag(event)


    def pseudoMoveModeLeftDown(self, event):
        """
	Initialize variables required for translating the selection during
	leftDrag method (pseudoMoveModeLeftDrag) . 
	@param event: Mouse left down event	
	@see : self.leftDown
	"""
        #pseudo move mode related initialization STARTS
        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0
        self.transDelta = 0 # X, Y or Z deltas for translate.
        self.moveOffset = [0.0, 0.0, 0.0] # X, Y and Z offset for move.

        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
        self.startpt = self.movingPoint # Used in leftDrag() to compute move offset during drag op.
        #pseudo move mode related initialization ENDS 
        return

    def pseudoMoveModeLeftDrag(self, event):
        """
	Translate the selected object(s) in the plane of the screen 
	following the mouse. This is a free drag translate.

        @param  event: mouse left drag event. 
	@see: self.leftDrag
	@see: modifyMode.leftDrag
	@note : This method uses some duplicate code (free drag translate code)
	from modifyMode.leftDrag 
        """

        if not self.picking:
            return

        if not self.o.assy.getSelectedMovables():
            return

        if self.movingPoint is None: 
            self.leftDown(event)         

        #Turn Off hover highlighting while translating the selection
        #This will be turned ON again in leftUp method. 
        self.hover_highlighting_enabled = False  

        # Move section
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)

        point = self.dragto( self.movingPoint, event) #bruce 060316 replaced old code with dragto (equivalent)

        # Print status bar msg indicating the current translation delta.	
        self.moveOffset = point - self.startpt # Fixed bug 929.  mark 060111
        msg = "Offset: [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.moveOffset[0],
                                                         self.moveOffset[1], 
                                                         self.moveOffset[2])
        env.history.statusbar_msg(msg)

        self.o.assy.movesel(point - self.movingPoint)
        self.movingPoint = point    
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()


    def leftUp(self, event):
        """
        Event handler for all LMB release events.
        """
        env.history.flush_saved_transients() # flush any transient message it saved up

        #Enable the highlighting which might be turned off during left drag 
        #@warning: When we add the chunk highlighting to the preferences, 
        #the following shuold set the user preferences value instead of 
        #setting this to 'True' -- ninad 20070720
        if not self.hover_highlighting_enabled:
            self.hover_highlighting_enabled = True

        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.emptySpaceLeftUp(event)
            return

        if self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            event = self.LMB_press_event
                # pretend the mouse didn't move -- this replaces our argument event,
                # for passing to *leftUp methods [bruce 060728 comment]

        obj = self.current_obj

        if obj is None: # Nothing dragged (or clicked); return.
            return

        self.doObjectSpecificLeftUp(obj, event)

        self.w.win_update()
        return # from selectMolsMode.leftUp

    def bareMotion(self, event): 
        """
        Overrides selectMode.bareMotion. Called for motion with no button down
        Should not be called otherwise, call update_selatom or 
	update_selobj directly instead.
        """

        # The value of self.timeAtLastWheelEvent is set in  
        # GraphicsMode.wheelEvent. 
        # This time is used to decide whether to highlight 
        #object under cursor. I.e. when user is scrolling the wheel to zoom in
        #or out, and at the same time the mouse moves slightly, we want to make 
        #sure that the object is not highlighted. The value of elapsed time
        #is selected as 2.0 seconds arbitrarily. Based on some tests, this value
        #seems OK. Following fixes bug 2536. Note, another fix would be to 
        #set self.hover_highlighting_enabled to False. But this fix looks more 
        #appropriate at the moment -- Ninad 2007-09-19
        if self.timeAtLastWheelEvent:
            timeSinceLastWheelEvent = time.clock() - self.timeAtLastWheelEvent	    
            if timeSinceLastWheelEvent < 2.0:		
                return 

        selectMode.bareMotion(self, event)

    def _getAtomHighlightColor(self, selobj):
        """
	Return the Atom highlight color 
	@return: Highlight color of the object (Atom or Singlet)
	The default implementation returns 'None' . Subclasses should override
	this method if they need atom highlight color.
	""" 
        return yellow

    def _getBondHighlightColor(self, selobj):
        """
	Return the Bond highlight color 
	@return: Highlight color of the object (Bond)
	The default implementation returns 'None' . Subclasses should override
	this method if they need bond highlight color.
	""" 
        return yellow

    def drawHighlightedObjectUnderMouse(self, glpane, selobj, hicolor):
        """
        [overrides superclass method]
        """
        # Ninad 070214 wrote this in GLPane; bruce 071008 moved it into 
        # selectMolsMode and slightly revised it. 
        skip_usual_selobj_highlighting = self.drawHighlightedChunk(glpane, 
                                                                   selobj, 
                                                                   hicolor)

            # Note: if subclasses don't like that, they should override 
            # drawHighlightedChunk to do nothing and return False. 
            # The prior code was equivalent to every subclass doing that. 
            # - [bruce 071008]
        if not skip_usual_selobj_highlighting:
            _superclass.drawHighlightedObjectUnderMouse(self, 
                                                        glpane, 
                                                        selobj, 
                                                        hicolor)
        return

    def drawHighlightedChunk(self, glpane, selobj, hicolor): 
        """
        Highlight the whole chunk to which 'selobj' belongs, using the 'hicolor'
        selobj = highlighted object 
        hicolor = highlight color

        @return: whether the caller should skip the usual selobj drawing
        (usually, this is just whether we drew something) (boolean)
        """
        # Ninad 070214 wrote this in GLPane; bruce 071008 moved it into 
        # selectMolsMode and slightly revised it (including, adding the return 
        # value).

        # Note: bool_fullBondLength represent whether full bond length to be
        # drawn it is used only in select Chunks mode while highlighting the 
        # whole chunk and when the atom display is Tubes display -- ninad 070214

        assert hicolor is not None #bruce 070919
        del self

        bool_fullBondLength = True

        if isinstance(selobj, molecule):
            print "I think this is never called "\
                  "(drawHighlightedChunk with selobj a Chunk)" #bruce 071008
            chunk = selobj
            for hiatom in chunk.atoms.itervalues():
                hiatom.draw_in_abs_coords(glpane, hicolor, 
                                          useSmallAtomRadius = True)
                for hibond in hiatom.bonds:
                    hibond.draw_in_abs_coords(glpane, hicolor,
                                              bool_fullBondLength)

            return False # not sure False is right, but it imitates 
                            # the prior code [bruce 071008]

        elif isinstance(selobj, Atom):
            chunk = selobj.molecule
            for hiatom in chunk.atoms.itervalues():
                hiatom.draw_in_abs_coords(glpane, hicolor, 
                                          useSmallAtomRadius = True)
                for hibond in hiatom.bonds:
                    hibond.draw_in_abs_coords(glpane, hicolor,
                                              bool_fullBondLength)
            return True

        elif isinstance(selobj, Bond):         
            hiatom1 = selobj.atom1
            hiatom2 = selobj.atom2                 
            chunk1 = hiatom1.molecule
            chunk2 = hiatom2.molecule

            if chunk1 is chunk2:
                for hiatom in chunk1.atoms.itervalues():
                    hiatom.draw_in_abs_coords(glpane, hicolor, 
                                              useSmallAtomRadius = True)
                    for hibond in hiatom.bonds:
                        hibond.draw_in_abs_coords(glpane, hicolor, 
                                                  bool_fullBondLength)
            else:
                for hiatom in chunk1.atoms.itervalues():
                    hiatom.draw_in_abs_coords(glpane, hicolor,
                                              useSmallAtomRadius = True)
                    for hibond in hiatom.bonds:
                        hibond.draw_in_abs_coords(glpane, hicolor,
                                                  bool_fullBondLength)
                for hiatom in chunk2.atoms.itervalues():
                    hiatom.draw_in_abs_coords(glpane, orange,
                                              useSmallAtomRadius = True)
                    for hibond in hiatom.bonds:
                        hibond.draw_in_abs_coords(glpane, orange,
                                                  bool_fullBondLength)
            return True

        return False # drew nothing

    pass # end of class selectMolsMode

# ==
