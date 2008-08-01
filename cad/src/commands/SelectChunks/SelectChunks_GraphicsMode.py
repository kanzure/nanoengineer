# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
SelectChunks_GraphicsMode.py

The GraphicsMode part of the SelectChunks_Command. It provides the  graphicsMode
object for its Command class. The GraphicsMode class defines anything related to
the *3D Graphics Area* --
For example:
- Anything related to graphics (Draw method),
- Mouse events
- Cursors,
- Key bindings or context menu


@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.


TODO:
- Items mentioned in Select_GraphicsMode.py
- Other items listed in Select_Command.py


History:
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from
                          the old class selectChunksMode and moved the
                          GraphicsMode related methods into this class from
                          selectChunksMode.py
"""

from PyQt4.Qt import QMouseEvent

import foundation.env as env

from model.bonds import Bond
from model.chem import Atom

from commands.Select.Select_GraphicsMode import DRAG_STICKINESS_LIMIT
from model.chunk import Chunk
from OpenGL.GL import glCallList
from utilities.debug import print_compact_traceback, print_compact_stack

from utilities.constants import orange, ave_colors, red
from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import mouseWheelTimeoutInterval_prefs_key

from utilities.debug_prefs import debug_pref, Choice_boolean_True
from utilities import debug_flags

from geometry.VQT import V, vlen

import time

from commands.Select.Select_GraphicsMode import Select_basicGraphicsMode

from utilities.GlobalPreferences import DEBUG_BAREMOTION

_superclass = Select_basicGraphicsMode

class SelectChunks_basicGraphicsMode(Select_basicGraphicsMode):
    """
    """
    #A list of movables that will be moved while dragging.
    #@seeself.getMovablesForLeftDragging()
    _leftDrag_movables = []
    
    

    def Enter_GraphicsMode(self):
        """
        Things needed while entering the GraphicsMode (e.g. updating cursor,
        setting some attributes etc).
        This method is called in self.command.Enter
        @see: B{SelectChunks_basicCommand.Enter}, B{basicCommand.Enter}
        """
        _superclass.Enter_GraphicsMode(self) #also calls self.reset_drag_vars()
                                             #etc

        self.o.assy.selectChunksWithSelAtoms_noupdate()
            # josh 10/7 to avoid race in assy init


    def leftDouble(self, event):
        """
        Handles LMB doubleclick event.
        @see:self.chunkLeftDouble()
        """

        self.ignore_next_leftUp_event = True

        if not self.obj_doubleclicked:
            return

        #this is a temporary fix for NFR bug 2569. 'Selectconnected chunks not
        #implemented yet
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            return

        chunk = None

        #Select neighboring DnaSegments
        if isinstance(self.obj_doubleclicked, Chunk):
            chunk = self.obj_doubleclicked
        elif isinstance(self.obj_doubleclicked, Atom):
            chunk = self.obj_doubleclicked.molecule
        elif isinstance(self.obj_doubleclicked, Bond):
            atm1 = self.obj_doubleclicked.atom1
            atm2 = self.obj_doubleclicked.atom2
            #@TODO" For now (2008-04-11, it considers only the chunk of a single
            #atom (and not atm2.molecule)
            chunk = atm1.molecule
        if chunk:
            self.chunkLeftDouble(chunk, event)

        return

    def chunkLeftDouble(self, chunk, event):
        """
        Select the connected chunks
        Note: For Rattlesnake, the implementation is limited for DnaStrands and
        DnaSegment. See the following methods to know what it selects/ deselects
        @see: ops_select_Mixin.expandDnaComponentSelection()
        @see: ops_select_Mixin.contractDnaComponentSelection()
        @see: ops_select_Mixin._expandDnaStrandSelection()
        @see:ops_select_Mixin._contractDnaStrandSelection()
        @see: ops_select_Mixin._contractDnaSegmentSelection()
        @see: DnaStrand.get_DnaStrandChunks_sharing_basepairs()
        @see: DnaSegment.get_DnaSegments_reachable_thru_crossovers()
        @see: NFR bug 2749 for details.
        """

        if self.selection_locked():
            return

        if not isinstance(chunk, Chunk):
            return

        if chunk.isNullChunk():
            #The chunk might have got deleted (during first leftUp operation
            #before it calls leftDouble-- Reason: it might have got deleted
            #during first leftUp of a Shift + Control  double click.
            #When the chunk is killed, its treated as a _nullMol_Chunk before
            #the next update. For rattlesnake release, we don't support
            #delete connected on chunks so return from the left double.
            return


        dnaStrandOrSegment = chunk.parent_node_of_class(self.win.assy.DnaStrandOrSegment)

        if dnaStrandOrSegment:
            if self.o.modkeys == 'Control':
                self.win.assy.contractDnaComponentSelection(dnaStrandOrSegment)
            elif self.o.modkeys == 'Shift+Control':
                #Deleting conneced dna components not supported for Rattlesnake
                #release
                pass
            else:
                self.win.assy.expandDnaComponentSelection(dnaStrandOrSegment)
        else:
            #Selecting / deselecting / deleting connected regular chunks is not
            #supported for Rattlesnke release
            if self.o.modkeys == 'Control':
                pass
                ##self.o.assy.unselectConnected( [ chunk ] )
            elif self.o.modkeys == 'Shift+Control':
                #Deleting conneced chunks not supported for Rattlesnake
                #release
                pass
            else:
                pass
                ##self.o.assy.selectConnected( [ chunk ] )

        return


    def selectConnectedChunks(self):
        """
        TODO: Not implemented yet. Need to define a method in ops_select to
        do this
        """
        pass

    def rightShiftDown(self, event):
        _superclass.rightShiftDown(self, event)

    def rightCntlDown(self, event):
        _superclass.rightCntlDown(self, event)


    # Chunk selection helper methods.
    def atomLeftDown(self, a, event):
        """
        Left down on an atom or a singlet(bondpoint)
        @param a: Atom or singlet
        @type  a: Atom or singlet
        @param event: QMouseLeftDown event
        """
        m = a.molecule
        #chunkLeftDown in turn calls self.objectSetUp()..
        self.chunkLeftDown(m, event)


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
        #Don't know if deallocate_bc_in_use is needed. Keeping the old code.
        self.deallocate_bc_in_use()
        self.chunkLeftUp(m, event)

    def chunkLeftDown(self, a_chunk, event):
        """
        Depending on the modifier key(s) pressed, it does various operations on
        chunk..typically pick or unpick the chunk(s) or do nothing.

        If an object left down happens, the left down method of that object
        calls this method (chunkLeftDown) as it is the 'selectMolsMode' which
        is supposed to select Chunk of the object clicked
        @param a_chunk: The chunk of the object clicked (example, if the  object
                      is an atom, then it is atom.molecule
        @type a_chunk: B{Chunk}
        @param event: MouseLeftDown event
        @see: self.atomLeftDown
        @see: BuildDna_GraphicsMode.chunkLeftDown() (overrides this method)
        @see: self.chunkSetUp()

        """
        #Don't select anything if the selection is locked.
        #see self.selection_locked() for more comments.
        if self.selection_locked():
            return

        assert isinstance(a_chunk, Chunk)

        m = a_chunk

        #@REVIEW: The following code that checks if its a dna segment or strand
        #etc is probably not needed because now we have implemented the API
        #method self.end_selection_from_GLPane() (which is also called in this
        #method.) Needs cleanup -- Ninad 2008-04-17

        if self._is_dnaGroup_highlighting_enabled():
            #If this graphicsmode highlights the whole DnaGroup,
            #pick that whole dna group when leftDown event occurs.
            dnaGroup = a_chunk.getDnaGroup()
            if dnaGroup is not None:
                m = dnaGroup
        else:
            #Fixed bug 2661 (see also similar code in self.chunkLeftUp() )
            #Select the whole parent DnaStrand or DnaSegment group (used when Dna
            # updater is enabled) instead of the chunk.
            #Note that this will be effective only in graphics modes where the
            #whole DnaGroup highlighting is disabled. (i.e. where the
            #highlighting of individual strands and segments is allowed)
            #-- Ninad 2008-03-14
            strandOrSegment = a_chunk.parent_node_of_class(
                self.win.assy.DnaStrandOrSegment)
            if 0:
                print "debug fyi: chunk %r .picked %r is in DnaStrandOrSegment %r .picked %r" % \
                  (a_chunk, a_chunk.picked,
                   strandOrSegment, strandOrSegment.picked) ###### @@@@@@ bruce 080430 debug code
                        ##### for 'rapid click selects subset of strand chunks' bug
            if strandOrSegment is not None:
                m = strandOrSegment

        if not m.picked and self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane()
            m.pick()
            self.o.selobj = None
        elif not m.picked and self.o.modkeys == 'Shift':
            m.pick()
            self.o.selobj = None
        elif self.o.modkeys == 'Control':
            if m.picked:
                m.unpick()
            self.o.selobj = None
        else:
            pass

        if m.picked:
            self.cursor_over_when_LMB_pressed = 'Picked Chunk'
        else:
            self.cursor_over_when_LMB_pressed = 'Unpicked Chunk'

        self.chunkSetUp(m, event)

        #Fixes bug because of which Nanotube segment is not selected from the
        #MT if the correspoinding chunk is selected from GLPane.
        #This was fixed AFTER Rattlesnake rc2  See also similar changes in
        #self.chunkLeftUp and self.bondLeftDown etc -- Ninad 2008-04-17
        self.end_selection_from_GLPane()


        self.w.win_update()

    def chunkLeftUp(self, a_chunk, event):
        """
        Depending on the modifier key(s) pressed, it does various operations on
        chunk. Example: if Shift and Control modkeys are pressed, it deletes the
        chunk
        @param a_chunk: The chunk of the object clicked (example, if the  object
                      is an atom, then it is atom.molecule
        @type a_chunk: B{Chunk}
        @param event: MouseLeftUp event
        @see: self.atomLeftUp()
        @see: self.chunkLeftDown()
        @see: self.leftShiftCntlUp()
        """
        #Note: The following check is already done in
        #selectMode.doObjectspecificLeftUp.
        #self.chunkLeftUp method should never be called if
        #self.current_obj_clicked is False. The check below is added just
        #to be on a safer side and prints a warning.
        #UPDATE 2008-03-03: This warning is harmless. In certain situations,
        #(e.g. leftup on a bondPoint etc), this method is invoked.
        #although it is a bug, its harmless because we do proper check here.
        #So print a warning message if ATOM_DEBUG flag is enabled.

        if not self.current_obj_clicked:
            if debug_flags.atom_debug:
                print_compact_stack("Note: self.current_obj_clicked is False "
                "and still selectMolsMode.chunkLeftUp is called. Make sure to "
                "call selectMode.objectSpecificLeftUp before calling "
                "selectMolsMode.chunkLeftUp: ")
            return

        #Don't select anything if the selection is locked.
        #see self.selection_locked() for more comments.
        if self.selection_locked():
            return

        assert isinstance(a_chunk, Chunk)

        m = a_chunk

        #@REVIEW: The following code that checks if its a dna segment or strand
        #etc is probably not needed because now we have implemented the API
        #method self.end_selection_from_GLPane() (which is also called in this
        #method.) Needs cleanup -- Ninad 2008-04-17

        if self._is_dnaGroup_highlighting_enabled():
            #If this graphicsmode highlights the whole DnaGroup,
            #pick that whole dna group when leftDown event occurs.
            dnaGroup = a_chunk.getDnaGroup()
            if dnaGroup is not None:
                m = dnaGroup
        else:
            #Fixed bug 2661 (see also similar code in self.chunkLeftDown() )
            #Select the whole parent DnaStrand or DnaSegment group (used when Dna
            # updater is enabled) instead of the chunk.
            #Note that this will be effective only in graphics modes where the
            #whole DnaGroup highlighting is disabled. (i.e. where the
            #highlighting of individual strands and segments is allowed)
            #-- Ninad 2008-03-14
            strandOrSegment = a_chunk.parent_node_of_class(self.win.assy.DnaStrandOrSegment)
            if strandOrSegment is not None:
                m = strandOrSegment

        if self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane()
            m.pick()
        elif self.o.modkeys == 'Shift+Control':
            #REVIEW/ TODO: leftShiftCntl* need to be an API method
            parentNodesOfObjUnderMouse = [m]
            self.leftShiftCntlUp(event,
                                 parentNodesOfObjUnderMouse = parentNodesOfObjUnderMouse)

        #Fixes bug because of which Nanotube segment is not selected from the
        #MT if the correspoinding chunk is selected from GLPane.
        #REVIEW: Should we do the following only when self.o.modkeys is None?
        #probably not. Some basic tests indicate that the fix is also good
        #for shift + control deleting the segment from the GLPane. This was fixed
        #AFTER Rattlesnake rc2  See also similar changes in  self.chunkLeftDown
        #and self.bondLeftDown -- Ninad 2008-04-17
        self.end_selection_from_GLPane()

        self.w.win_update()

    def leftShiftCntlUp(self, event, parentNodesOfObjUnderMouse = ()):
        """
        Do operations when Shift + control left up event occurs
        (As of 2008-05-02, this is now only implemented for and called from
        self.chunkLeftUp())

        @param parentNodesOfObjUnderMouse: Parent chunk, of which, the object
                under mouse is a part of.or some other node such as a
                DnaStrand Or DnaSegment etc which the user probably wants to
                operate on.

        @see: self.chunkLeftUp()
        @see: self._do_leftShiftCntlUp_delete_operations()
        """
        #TODO: This is a new method written on 2008-05-02 , especially to permit
        #some custom deleting in BuildDna graphicsMode (a subclass of this
        #class) . This method should also consider other possibilities
        #such as 'what if the object under mouse is a Jig or something else'
        #there is some code that already exists which needs to use this new
        #method (and this method needs to take care of that) . -- Ninad
        print "parentNodesOfObjUnderMouse =", parentNodesOfObjUnderMouse
        obj = self.get_obj_under_cursor(event)
        self._do_leftShiftCntlUp_delete_operations(
            event,
            obj,
            parentNodesOfObjUnderMouse = parentNodesOfObjUnderMouse)

        self.o.selobj =  None

    def _do_leftShiftCntlUp_delete_operations(self,
                                              event,
                                              objUnderMouse,
                                              parentNodesOfObjUnderMouse = ()):
        """
        Overridden in subclasses, default implementation just deletes the
        parent node of the object under cursor (provides as an argument)

        @param parentNodesOfObjUnderMouse: Tuple containing the
                parent chunk(s), of which, the object
                under mouse  is a part of,  or, some other node such as a
                DnaStrand Or DnaSegment etc which the user probably wants to
                operate on.
        @type: Tuple

        @see: self.chunkLeftUp()
        @see: self.leftShiftCntlUp() which calls this method.

        @see: BuildDna_GraphicsMode._do_leftShiftCntlUp_delete_operations()
        """
        obj = objUnderMouse
        if obj is self.o.selobj:
            if parentNodesOfObjUnderMouse:
                try:
                    for node in parentNodesOfObjUnderMouse:
                        node.kill()
                except:
                    print_compact_traceback(
                        "Error deleting objects %r" % parentNodesOfObjUnderMouse)


    def bondLeftDown(self, b, event):
        """
        Left down  on a Bond <b> , so select or unselect its chunk or
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

        if self.selection_locked():
            return

        chunk1 = b.atom1.molecule
        chunk2 = b.atom2.molecule
        self.set_cmdname('Select Chunks')

        if chunk1 is chunk2:
            self.chunkLeftDown(chunk1, event)
            return

        if self._is_dnaGroup_highlighting_enabled():
            dnaGroup1 = chunk1.getDnaGroup()
            dnaGroup2 = chunk2.getDnaGroup()

            if dnaGroup1 is not None and dnaGroup1 is dnaGroup2:
                self.chunkLeftDown(chunk1, event)
                return

            if dnaGroup1 is not None:
                chunk1 = dnaGroup1

            if dnaGroup2 is not None:
                chunk2 = dnaGroup2
        else:
            #@TODO Fixes part of bug 2749. Method needs refactoring
            #-- Ninad 2008-04-07
            dnaStrandOrSegment1 = chunk1.parent_node_of_class(
                self.win.assy.DnaStrandOrSegment)
            dnaStrandOrSegment2 = chunk2.parent_node_of_class(
                self.win.assy.DnaStrandOrSegment)

            if dnaStrandOrSegment1 is not None and \
               dnaStrandOrSegment1 is dnaStrandOrSegment2:
                self.chunkLeftDown(chunk1, event)
                return

            if dnaStrandOrSegment1 is not None:
                chunk1 = dnaStrandOrSegment1

            if dnaStrandOrSegment2 is not None:
                chunk2 = dnaStrandOrSegment2

        if self.o.modkeys is None:
            if chunk1.picked and chunk2.picked:
                pass
            else:
                self.o.assy.unpickall_in_GLPane()
                if not chunk1.picked:
                    chunk1.pick()
                if not chunk2.picked:
                    chunk2.pick()
            self.o.selobj = None
        elif self.o.modkeys == 'Shift':
            if not chunk1.picked:
                chunk1.pick()
            if not chunk2.picked:
                chunk2.pick()
            self.o.selobj = None
        elif self.o.modkeys == 'Control':
            chunk1.unpick()
            chunk2.unpick()
            self.set_cmdname('Unselect Chunks')
            self.o.selobj = None
        else:
            pass

        if chunk1.picked or chunk2.picked:
            self.cursor_over_when_LMB_pressed = 'Picked Chunk'
        else:
            self.cursor_over_when_LMB_pressed = 'Unpicked Chunk'

        #Fixes bug because of which Nanotube segment is not selected from the
        #MT if the correspoinding chunk is selected from GLPane.
        #This was fixed AFTER Rattlesnake rc2  See also similar changes in
        #self.chunkLeftUp and self.bondLeftUp etc -- Ninad 2008-04-17
        self.end_selection_from_GLPane()

        self.w.win_update()

    def bondLeftUp(self, b, event):

        #Note: The following check is already done in
        #selectMode.doObjectspecificLeftUp.
        #self.chunkLeftUp method should never be called if
        #self.current_obj_clicked is False. The check below is added just
        #to be on a safer side and prints a warning.
        if not self.current_obj_clicked:
            print_compact_stack("Note: self.current_obj_clicked is False "
            "and still selectMolsMode.bondLeftUp is called. Make sure to "
            "call selectMode.objectSpecificLeftUp before calling "
            "selectMolsMode.bondLeftUp: ")
            return

        if self.selection_locked():
            return

        chunk1 = b.atom1.molecule
        chunk2 = b.atom2.molecule

        if chunk1 is chunk2:
            self.chunkLeftUp(chunk1, event)
            return

        if self._is_dnaGroup_highlighting_enabled():
            dnaGroup1 = chunk1.getDnaGroup()
            dnaGroup2 = chunk2.getDnaGroup()

            if dnaGroup1 is not None and dnaGroup1 is dnaGroup2:
                self.chunkLeftDown(chunk1, event)
                return

            if dnaGroup1 is not None:
                chunk1 = dnaGroup1

            if dnaGroup2 is not None:
                chunk2 = dnaGroup2
        else:
            #@TODO Fixes part of bug 2749. Method needs refactoring
            #-- Ninad 2008-04-07
            dnaStrandOrSegment1 = chunk1.parent_node_of_class(
                self.win.assy.DnaStrandOrSegment)
            dnaStrandOrSegment2 = chunk2.parent_node_of_class(
                self.win.assy.DnaStrandOrSegment)

            if dnaStrandOrSegment1 is not None and \
               dnaStrandOrSegment1 is dnaStrandOrSegment2:
                if self.o.modkeys != 'Shift+Control':
                    self.chunkLeftDown(chunk1, event)
                else:
                    self.leftShiftCntlUp(event,
                                         parentNodesOfObjUnderMouse = (chunk1))
                return


            if dnaStrandOrSegment1 is not None:
                chunk1 = dnaStrandOrSegment1

            if dnaStrandOrSegment2 is not None:
                chunk2 = dnaStrandOrSegment2

            pass

        if self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane()
            chunk1.pick()
            chunk2.pick()
            self.o.selobj = None
        elif self.o.modkeys == 'Shift+Control':
            self.leftShiftCntlUp(event,
                                 parentNodesOfObjUnderMouse = (chunk1, chunk2))


        #call API method to do any special selection (e.g. select the whole
        #DnaStrand if all its chunks are selected)
        self.end_selection_from_GLPane()

    # == Singlet helper methods
    def singletLeftDown(self, s, event):
        self.atomLeftDown(s, event)
        return

    def singletLeftUp(self, s, event):
        self.atomLeftUp(s, event)
        return

    # == LMB down-click (button press) methods


    def leftDown(self, event):
        """
        Event handler for all LMB press events.
        """
        # Note: the code of selectAtomsMode and selectMolsMode .leftDown methods
        # is very similar, so I'm removing the redundant comments from
        # this one (selectMolsMode); see selectAtomsMode to find them.
        # [bruce 071022]

        self.set_cmdname('ChunkClick')
            # TODO: this should be set again later (during the same drag)
            # to a more specific command name.

        self.reset_drag_vars()
        env.history.statusbar_msg(" ")

        self.LMB_press_event = QMouseEvent(event)

        self.LMB_press_pt_xy = (event.pos().x(), event.pos().y())

        obj = self.get_obj_under_cursor(event)
        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            return

        method = getattr(obj, 'leftClick', None)
        if method:
            # This looks identical to the code from selectAtomsMode.leftDown
            # which I just split into a separate method call_leftClick_method,
            # so I will shortly move that into our common superclass and
            # call it here instead of duplicating that code.
            #[bruce 071022 comment]
            gl_event_info = self.dragstart_using_GL_DEPTH( event,
                                                           more_info = True)
            self._drag_handler_gl_event_info = gl_event_info
            farQ_junk, hitpoint, wX, wY, depth, farZ = gl_event_info
            del wX, wY, depth, farZ
            try:
                retval = method(hitpoint, event, self)
            except:
                print_compact_traceback("exception ignored "\
                                        "in %r.leftClick: " % (obj,))
                return
            self.drag_handler = retval # needed even if this is None
            if self.drag_handler is not None:
                #the psuedoMoveMode left down might still be needed even when
                #drag handler is not None
                #(especially to get the self._leftDrag_movables)
                self._leftDown_preparation_for_dragging(obj, event)
                self.dragHandlerSetup(self.drag_handler, event)
                return

        self.doObjectSpecificLeftDown(obj, event)

        if self.glpane.modkeys is None:
            self._leftDown_preparation_for_dragging(obj, event)

        self.w.win_update()

        return # from selectMolsMode.leftDown


    def leftDrag(self, event):
        """
        Overrides leftdrag method of superclass.
        A) If the mouse cursor was on Empty space during left down, it draws
           a selection curve
        B) If it was on an object, it translates translates the selection
          (free drag translate). This is called 'pseudo move mode'
          for convenience.

        Note that NE1 still remains in the selectMolsMode while doing this.
        It calls separate method for objects that implement drag handler API

        @param  event: mouse left drag event
        @see : selectMode.leftDrag
        @see : selectMolsMode._leftDown_preparation_for_dragging
        @see : selectMolsMode.leftDragTranslation

        """

        if self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            return

        self.current_obj_clicked = False

        # Copying some drag_handler checker code from selectAtomsMode (with some
        # modifications) -- Ninad20070601
        # [bruce 071022 removed some comments redundant with the
        #  leftDrag method of selectAtomsMode]


        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            if self.drag_handler is not None:
                self.dragHandlerDrag(self.drag_handler, event)
                    # does updates if needed
            else:
                self.emptySpaceLeftDrag(event)
            return

        if self.o.modkeys is not None:
            # If a drag event has happened after the cursor was over an atom
            # and a modkey is pressed, do a 2D region selection as if the
            # atom were absent.
            self.emptySpaceLeftDown(self.LMB_press_event)
            #bruce 060721 question: why don't we also do emptySpaceLeftDrag
            # at this point?
            return

        if self.drag_handler is not None:
            movables = self._leftDrag_movables
            if movables:
                if self.drag_handler not in movables:
                    self.dragHandlerDrag(self.drag_handler, event)
                    return
                elif len(movables) == 1:
                    self.dragHandlerDrag(self.drag_handler, event)
                    return

        #Free Drag Translate the selected (movable) objects.
        self.leftDragTranslation(event)


    def _leftDown_preparation_for_dragging(self, objectUnderMouse, event):
        """
        Initialize variables required for translating the selection during
        leftDrag method (leftDragTranslation) .
        @param event: Mouse left down event
        @param objectUnderMouse: Object under the mouse during left down event.
        @see : self.leftDown()
        @see: self.getMovablesForLeftDragging()
        """
        #pseudo move mode related initialization STARTS
        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0
        self.transDelta = 0 # X, Y or Z deltas for translate.
        self.moveOffset = [0.0, 0.0, 0.0] # X, Y and Z offset for move.

        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
        self.startpt = self.movingPoint
            # Used in leftDrag() to compute move offset during drag op.

        self._leftDrag_movables = [] #Just for safety. This is already reset
        #in self.reset_drag_vars()
        #pseudo move mode related initialization ENDS

        #Defin the left drag movables. These will be computed once only in
        #the leftDown (and not each time duruing the leftDrag)
        self._leftDrag_movables = self.getMovablesForLeftDragging()
        return

    def leftDragTranslation(self, event):
        """
        Translate the selected object(s) in the plane of the screen
        following the mouse. This is a free drag translate.

        @param  event: mouse left drag event.
        @see: self.leftDrag
        @see: modifyMode.leftDrag
        #@see: self.getMovablesForLeftDragging()
        @note : This method uses some duplicate code (free drag translate code)
        from modifyMode.leftDrag

        """
        self._leftDragFreeTranslation(event)

    def _leftDragFreeTranslation(self, event):
        """
        @see : self.leftDrag()
        @see: self._leftDragFreeTranslation()
        @see: self._leftDragConstrainedTranslation()
        """
        if not self.picking:
            return

        if not self._leftDrag_movables:
            return

        if self.movingPoint is None:
            self.leftDown(event)

        # Turn Off hover highlighting while translating the selection
        # This will be turned ON again in leftUp method.
        # [update, bruce 071121: it looks like it's turned back on
        #  in bareMotion instead.]
        ##self.hover_highlighting_enabled = False
        self._supress_highlighting = True

        # This flag is required in various leftUp methods. It helps them
        # decide what to do upon left up. The flag value is set in
        # selectMode.objectSetup, selectMode.objectLeftDrag.
        # See those comments. Found a bit confusing but enough documentation
        # exists so ok
        self.current_obj_clicked = False

        # Move section
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)

        point = self.dragto( self.movingPoint, event)

        # Print status bar msg indicating the current translation delta.
        self.moveOffset = point - self.startpt # Fixed bug 929.  mark 060111
        msg = "Offset: [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.moveOffset[0],
                                                         self.moveOffset[1],
                                                         self.moveOffset[2])
        env.history.statusbar_msg(msg)

        offset = point - self.movingPoint
        self.win.assy.translateSpecifiedMovables(offset,
                                                 self._leftDrag_movables)

        self.movingPoint = point
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()

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


        #Enable the highlighting which might be turned off during left drag
        #@warning: When we add the chunk highlighting to the preferences,
        #the following should set the user preferences value instead of
        #setting this to 'True' -- ninad 20070720
        ##if not self.hover_highlighting_enabled:
            ##self.hover_highlighting_enabled = True

        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.emptySpaceLeftUp(event)
            return

        if self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            event = self.LMB_press_event
                # pretend the mouse didn't move -- this replaces our argument
                # event, for passing to *leftUp methods [bruce 060728 comment]

        obj = self.current_obj


        if obj is None: # Nothing dragged (or clicked); return.
            return

        #For drag handler API such as the one used in exprs.Highlightable
        #or in class ResizeHandle
        if self.drag_handler:
            self.dragHandlerLeftUp(self.drag_handler, event)
            self.leftUp_reset_a_few_drag_vars()

        self.doObjectSpecificLeftUp(obj, event)

        self.w.win_update()
        return # from selectMolsMode.leftUp

    def reset_drag_vars(self):
        """
        @see: SelectGraphicsMode.reset_drag_vars() for documentation
        """
        _superclass.reset_drag_vars(self)
        #Clear the list of movables (to be moved while left dragging selection)
        #@see: self.psudoMoveModeLeftDown()
        self._leftDrag_movables = []

    def leftUp_reset_a_few_drag_vars(self):
        """
        reset a few drag vars at the end of leftUp --
        might not be safe to reset them all
        (e.g. if some are used by leftDouble)
        """
        self.current_obj = None #bruce 041130 fix bug 230
            # later: i guess this attr had a different name then [bruce 060721]
        self.o.selatom = None #bruce 041208 for safety in case it's killed
        self._leftDrag_movables = []
        return

    def bareMotion(self, event):
        """
        Overrides selectMode.bareMotion. Called for motion with no button down
        Should not be called otherwise, call update_selatom or
        update_selobj directly instead.
        """
        #The value of self.timeAtLastWheelEvent is set in
        #GraphicsMode.wheelEvent.
        #This time is used to decide whether to highlight the object
        #under the cursor. I.e. when user is scrolling the wheel to zoom in
        #or out, and at the same time the mouse moves slightly, we want to make
        #sure that the object is not highlighted. The value of elapsed time
        #is selected as 2.0 seconds arbitrarily. Based on some tests, this value
        #seems OK. Following fixes bug 2536. Note, another fix would be to
        #set self.hover_highlighting_enabled to False. But this fix looks more
        #appropriate at the moment -- Ninad 2007-09-19
        #
        # Note: I think 2.0 is too long -- this should probably be more like 0.5.
        # But I will not change this immediately, since I am fixing two other
        # contributing causes to bug 2606, and I want to see their effects one
        # at a time. @@@@@
        # [bruce 080129 comment]
        #
        # update, bruce 080130: change time.clock -> time.time to fix one cause
        # of bug 2606. Explanation: time.clock is documented as returning
        # "either real time or CPU time", and at least on the Macs I tested,
        # it returns something that grows much more slowly than real time,
        # especially on the faster Mac of the two (like cpu time would do).
        # That is probably one of two or three bugs adding together to cause the
        # highlighting suppression bug 2606 reported by Paul -- the others are
        # the large timeout value of 2.0, and (predicted from the code, not yet
        # fully tested) that this timeout condition can discard not only a real
        # bareMotion event, but a fake zero-motion event intended to make sure
        # highlighting occurs after large mouse motions disabled it, which is
        # sent exactly once after motion stops (even if this timeout is still
        # running). I am fixing these one at a time to see their individual
        # effects. @@@@@
        #
        # update: Mark 2008-05-26. Added user pref to set timeout interval
        # from the Preferences dialog. The default = 0.5 seconds, which is
        # much better than 2.0.
        #
        # russ 080527: Fix Bug 2606 (highlighting not turned on after wheel event.)
        # Return value to caller tells whether the bareMotion event was discarded.
        #
        if self.timeAtLastWheelEvent:
            time_since_wheel_event = time.time() - self.timeAtLastWheelEvent
            if time_since_wheel_event < env.prefs[mouseWheelTimeoutInterval_prefs_key]:
                if DEBUG_BAREMOTION:
                    #bruce 080129 re highlighting bug 2606 reported by Paul
                    print "debug fyi: ignoring %r.bareMotion since time_since_wheel_event is only %r " % \
                          (self, time_since_wheel_event)
                return True

        #Turn the highlighting back on if it was supressed during, 
        #for example, leftDrag
        if self._supress_highlighting:
            self._supress_highlighting = False

        _superclass.bareMotion(self, event)

        return False

    def update_cursor_for_no_MB(self):
        """
        Update the cursor for Select mode (Default implementation).
        """

        # print "selectMolsMode.update_cursor_for_no_MB(): button=",\
        #  self.o.button,"modkeys=",self.o.modkeys

        if self.o.modkeys is None:
            ##print "seeing modkeys is None",self.w.SelectArrowCursor #bruce 070628
            ##self.o.gl_update()  #bruce 070628, didn't help
            self.o.setCursor(self.w.SelectArrowCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.SelectArrowAddCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.SelectArrowSubtractCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB(): " \
                  "Invalid modkey=", self.o.modkeys
        return

    def drawHighlightedChunk(self, glpane, selobj, hicolor, hicolor2):
        """
        Highlight the whole chunk to which 'selobj' belongs, using the 'hicolor'.
        If selobj is an external bond, highlight both its atoms' chunks,
        one in hicolor and one in hicolor2 (which chunk is which is arbitrary,
        for now). (External bonds connecting those two chunks will get drawn
        in hicolor.)

        @param selobj: the atom or bond (or other object) under the mouse

        @param hicolor: highlight color for selobj's chunk

        @param hicolor2: highlight color for selobj's "other chunk", if any

        @return: whether the caller should skip the usual selobj drawing
                 (usually, this is just whether we drew something)
        @rtype: boolean
        @see: self._get_objects_to_highlight()
        @see: self._is_dnaGroup_highlighting_enabled()
        @see : self.drawHighlightedObjectUnderMouse()
        """
        # Ninad 070214 wrote this in GLPane; bruce 071008 moved it into
        # selectMolsMode and slightly revised it (including, adding the return
        # value).
        # Bruce 080217 formalized hicolor2 as an arg (was hardcoded orange).
        assert hicolor is not None #bruce 070919
        assert hicolor2 is not None

        something_drawn_highlighted = False

        #dictionary of objects to highlight.
        highlightObjectDict =  self._get_objects_to_highlight(selobj,
                                                              hicolor,
                                                              hicolor2)

        #We could have even used simple lists here. one for objects to be
        #highlighted and one for highlight colors. Easy to change to that
        #implementation if we need to.

        for obj, color in highlightObjectDict.iteritems():
            #obj = object to be drawn highlighted
            #color = highlight color
            if hasattr( obj, 'draw_highlighted'):
                obj.draw_highlighted(self.glpane, color)
                something_drawn_highlighted = True

        return  something_drawn_highlighted

    def _get_objects_to_highlight(self, selobj, hiColor1, hiColor2):
        """
        Returns a python dictionary with objects to be drawn highlighted as its
        keys and highlight color as their corresponding values.

        The object to be highlighted is determined based the current graphics
        mode using the glpane.selobj. The subclasses can override this method to
        return objects to be highlighted in that particular graphics mode.
        @param selobj: GLPane.selobj (object under cursoe which can be registered
                       as a GLPane.selobj
        @param hiColor1 : highlight color 1
        @paramhiColor2: alternative highlight color. Example: If there are two
                        chunks that need to be highlighted, one chunk gets
                        hiColor1 and other gets hiColor2.

        @TODO:
        - may be hiColors should be in a list to make it more general
        @return: dictionary of objects to be highlighted.
        @rtype: dict
        @see: self._is_dnaGroup_highlighting_enabled()
        @see: self.drawHighlightedChunk()
        @see : self.drawHighlightedObjectUnderMouse()
        """

        #Create a dictionary of objects to be drawn highlighted.
        #(object_to_highlight, highlight_color) will
        objectDict = {}

        chunkList = []
        colorList = []

        #Note: Make sure to check if its a 'DnaStrand' or a 'DnaSegment' so that
        #its draw_highlighted method gets called when applicable. There could be
        #several such things in the future. so need to think of a better way to
        #do it.
        #@TODO Following also fixes part of bug 2749. Method needs refactoring
        #-- Ninad 2008-04-07
        if isinstance(selobj, Chunk):
            dnaStrandOrSegment = selobj.parent_node_of_class(
                self.win.assy.DnaStrandOrSegment)

            if dnaStrandOrSegment:
                chunkList = [dnaStrandOrSegment]
            else:
                chunkList = [selobj]
            colorList = [hiColor1]
        elif isinstance(selobj, Atom):
            dnaStrandOrSegment = selobj.molecule.parent_node_of_class(
                self.win.assy.DnaStrandOrSegment)

            if dnaStrandOrSegment:
                chunkList = [dnaStrandOrSegment]
            else:
                chunkList = [selobj.molecule]
            colorList = [hiColor1]
        elif isinstance(selobj, Bond):
            chunk1 = selobj.atom1.molecule
            chunk2 = selobj.atom2.molecule
            if chunk1 is chunk2:
                dnaStrandOrSegment = chunk1.parent_node_of_class(
                    self.win.assy.DnaStrandOrSegment)

                if dnaStrandOrSegment:
                    chunkList = [dnaStrandOrSegment]
                else:
                    chunkList = [chunk1]
                colorList = [hiColor1]
            else:
                for c in [chunk1, chunk2]:
                    dnaStrandOrSegment = c.parent_node_of_class(
                        self.win.assy.DnaStrandOrSegment)
                    if dnaStrandOrSegment:
                        chunkList.append(dnaStrandOrSegment)
                    else:
                        chunkList.append(c)
                colorList = [hiColor1, hiColor2]

        if self._is_dnaGroup_highlighting_enabled():
            for c in chunkList:
                i = chunkList.index(c)
                dnaGroup = c.getDnaGroup()
                if dnaGroup is not None:
                    if not objectDict.has_key(dnaGroup):
                        objectDict[dnaGroup] = colorList[i]
                else:
                    objectDict[c] = colorList[i]
        else:
            for c in chunkList:
                i = chunkList.index(c)
                objectDict[c] = colorList[i]

        return objectDict

    def _is_dnaGroup_highlighting_enabled(self):
        """
        NOTE: TO BE DEPRECATED: 2008-04-07 onwards, the whole DnaGroup will never be highlighted
        So this flag will always returns True in this class and in subclasses
        See bug Bug 2749 for implementation change details. post FNANO, this
        method and its calls can be removed (provided implementation doesn't
        change). Returning 'False' is as good as not using this feature in the
        UI so no problem.

        Returns a boolean that decides whether to highlight the whole
        DnaGroup or just the chunk of the glpane.selobj.
        Example: In default mode (SelectChunks_graphicsMode) if the cursor is
        over an atom or a bond which belongs to a DnaGroup, the whole
        DnaGroup is highlighted. But if you are in buildDna mode, the
        individual strand and axis chunks will be highlighted in this case.
        Therefore, subclasses of SelectChunks_graphicsMode should override this
        method to enable or disable the DnaGroup highlighting. (the Default
        implementation returns True)
        @see: self._get_objects_to_highlight()
        @see: self.drawHighlightedChunk()
        @see : self.drawHighlightedObjectUnderMouse()
        """
        return False

    def drawHighlightedObjectUnderMouse(self, glpane, selobj, hicolor):
        """
        [overrides superclass method]
        @see: self._get_objects_to_highlight()
        @see: self.drawHighlightedChunk()


        """
        # Ninad 070214 wrote this in GLPane; bruce 071008 moved it into
        # selectMolsMode and slightly revised it.
        ## hicolor2 = orange # intended to visually differ from hicolor
        HHColor = env.prefs[hoverHighlightingColor_prefs_key]
        hicolor2 = ave_colors(0.5, HHColor, orange)
            #bruce 080217 revision to hicolor2 (since orange is a warning color)
        skip_usual_selobj_highlighting = self.drawHighlightedChunk(glpane,
                                                                   selobj,
                                                                   hicolor,
                                                                   hicolor2)
            # Note: if subclasses don't want that call, they should override
            # drawHighlightedChunk to do nothing and return False.
            # The prior code was equivalent to every subclass doing that.
            # - [bruce 071008]
        if not skip_usual_selobj_highlighting:
            _superclass.drawHighlightedObjectUnderMouse(self,
                                                        glpane,
                                                        selobj,
                                                        hicolor)
        return

    def _getAtomHighlightColor(self, selobj):
        """
        Return the Atom highlight color
        @return: Highlight color of the object (Atom or Singlet)
        The default implementation returns 'None' . Subclasses should override
        this method if they need atom highlight color.
        """
        if self.o.modkeys == 'Shift+Control':
            return red

        return env.prefs[hoverHighlightingColor_prefs_key]


    def _getBondHighlightColor(self, selobj):
        """
        Return the Bond highlight color
        @return: Highlight color of the object (Bond)
        The default implementation returns 'None' . Subclasses should override
        this method if they need bond highlight color.
        """
        if self.o.modkeys == 'Shift+Control':
            return red

        return env.prefs[hoverHighlightingColor_prefs_key]

class SelectChunks_GraphicsMode(SelectChunks_basicGraphicsMode):
    """
    """
    def __init__(self, command):
        self.command = command
        glpane = self.command.glpane
        SelectChunks_basicGraphicsMode.__init__(self, glpane)
        return

    # (the rest would come from GraphicsMode if post-inheriting it worked,
    #  or we could split it out of GraphicsMode as a post-mixin to use there
    #  and here)

    def _get_commandSequencer(self):
        return self.command.commandSequencer

    commandSequencer = property(_get_commandSequencer)

    def set_cmdname(self, name):
        self.command.set_cmdname(name)
        return

    def _get_hover_highlighting_enabled(self):
        return self.command.hover_highlighting_enabled

    def _set_hover_highlighting_enabled(self, val):
        self.command.hover_highlighting_enabled = val

    hover_highlighting_enabled = property(_get_hover_highlighting_enabled,
                                          _set_hover_highlighting_enabled)


