# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
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
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.


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

import env

from modes import basicMode
from bonds import Bond
from chem import Atom

from Select_GraphicsMode import DRAG_STICKINESS_LIMIT
from chunk import Chunk 
from debug import print_compact_traceback, print_compact_stack
from constants import orange

from constants import yellow

from VQT import V, vlen

import time

from Select_Command import Select_Command

from Select_GraphicsMode import Select_basicGraphicsMode


_superclass = Select_basicGraphicsMode

class SelectChunks_basicGraphicsMode(Select_basicGraphicsMode):
    """
    """
    
    def Enter_GraphicsMode(self):
        """
        Things needed while entering the GraphicsMode (e.g. updating cursor, 
        setting some attributes etc). 
        This method is called in self.command.Enter
        @see: B{SelectChunks_basicCommand.Enter}, B{basicCommand.Enter}
        """
        _superclass.Enter_GraphicsMode(self)        
        self.o.assy.selectChunksWithSelAtoms_noupdate()
            # josh 10/7 to avoid race in assy init          
    
    def leftDouble(self, event):
        """
	Select connected chunks
	"""
        #this is a temporary fix for NFR bug 2569. 'Selectconnected chunks not
        #implemented yet
        if self.cursor_over_when_LMB_pressed != 'Empty Space':
            self.selectConnectedChunks()
        return

    def rightShiftDown(self, event):
        basicMode.rightShiftDown(self, event)

    def rightCntlDown(self, event):          
        basicMode.rightCntlDown(self, event)

    # Chunk selection helper methods. 
    def atomLeftDown(self, a, event):  
        """
        Left down on an atom or a singlet(bondpoint)
        @param a: Atom or singlet
        @type  a: Atom or singlet
        @param event: QMouseLeftDown event
        """
        m = a.molecule
        self.chunkLeftDown(m, event)
        
        #calling atom setup is needed as it calls 'objectSetup' , which in turn 
        #sets an appropriate flag for leftUp methods 
        self.atomSetup(a, event)
    
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
        @see: self.chunkLeftDown
        """
        m = a_chunk
        
        assert isinstance(m, Chunk)
                
        if not m.picked and self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane()
            m.pick()
            self.o.selobj =  None
        elif not m.picked and self.o.modkeys == 'Shift':
            m.pick()
            self.o.selobj =  None
        elif self.o.modkeys == 'Control':
            if m.picked:
                m.unpick()
            self.o.selobj =  None
        else:
            pass
        
        if m.picked:
            self.cursor_over_when_LMB_pressed = 'Picked Chunk'
        else:
            self.cursor_over_when_LMB_pressed = 'Unpicked Chunk'
        
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
        @see: self.atomLeftUp
        @see: self.chunkLeftDown
        
        """
        #Note: The following check is already done in 
        #selectMode.doObjectspecificLeftUp. 
        #self.chunkLeftUp method should never be called if
        #self.current_obj_clicked is False. The check below is added just 
        #to be on a safer side and prints a warning.
        if not self.current_obj_clicked:
            print_compact_stack("Note: self.current_obj_clicked is False "
            "and still selectMolsMode.chunkLeftUp is called. Make sure to "
            "call selectMode.objectSpecificLeftUp before calling "
            "selectMolsMode.chunkLeftUp: ")
            return
        
        m = a_chunk
                
        assert isinstance(m, Chunk)    
        
        if self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane()
            m.pick()          
        elif self.o.modkeys == 'Shift+Control':
            obj = self.get_obj_under_cursor(event)
            if obj is self.o.selobj:
                m.kill()                
            self.o.selobj =  None             
        
        self.w.win_update()

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

        chunk1 = b.atom1.molecule
        chunk2 = b.atom2.molecule
        self.set_cmdname('Select Chunks')
        
        if chunk1 is chunk2:
            self.chunkLeftDown(chunk1, event)
            return
        
        if self.o.modkeys is None:
            if chunk1.picked and chunk2.picked:
                pass
            else:
                self.o.assy.unpickall_in_GLPane()
                if not chunk1.picked:
                    chunk1.pick()     
                if not chunk2.picked:
                    chunk2.pick()                
            self.o.selobj =  None  
        elif self.o.modkeys == 'Shift':
            if not chunk1.picked:
                chunk1.pick()     
            if not chunk2.picked:
                chunk2.pick() 
            self.o.selobj =  None 
        elif self.o.modkeys == 'Control':
            chunk1.unpick()            
            chunk2.unpick()
            self.set_cmdname('Unselect Chunks')
            self.o.selobj =  None 
        else:
            pass

        if chunk1.picked or chunk2.picked:
            self.cursor_over_when_LMB_pressed = 'Picked Chunk'
        else:
            self.cursor_over_when_LMB_pressed = 'Unpicked Chunk'

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
        
        chunk1 = b.atom1.molecule
        chunk2 = b.atom2.molecule  
        
        if chunk1 is chunk2:
            self.chunkLeftUp(chunk1, event)
            return
        
        if self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane()
            chunk1.pick() 
            chunk2.pick()  
            self.o.selobj =  None
        elif self.o.modkeys == 'Shift+Control':         
            chunk1.kill()
            chunk2.kill()
            self.o.selobj =  None

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

        self.pseudoMoveModeLeftDown(event) 

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
                self.dragHandlerSetup(self.drag_handler, event) 
                return

        self.doObjectSpecificLeftDown(obj, event)

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
	@see : selectMolsMode.pseudoMoveModeLeftDown
	@see : selectMolsMode.pseudoMoveModeLeftDrag

	"""

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
            movables = self.o.assy.getSelectedMovables()
            if movables:
                if self.drag_handler not in movables:
                    self.dragHandlerDrag(self.drag_handler, event) 
                    return
                elif len(movables) == 1:
                    self.dragHandlerDrag(self.drag_handler, event)
                    return                    

        if self.o.assy.getSelectedMovables():
            # TODO: optim by computing this only once, before the prior 'if'
            # [bruce 071022 suggestion]
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
        self.startpt = self.movingPoint
            # Used in leftDrag() to compute move offset during drag op.
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
            
        # Turn Off hover highlighting while translating the selection
        # This will be turned ON again in leftUp method.
        # [update, bruce 071121: it looks like it's turned back on
        #  in bareMotion instead.]
        self.hover_highlighting_enabled = False  
        
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

        self.o.assy.movesel(point - self.movingPoint)
        self.movingPoint = point    
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()


    def leftUp(self, event):
        """
        Event handler for all LMB release events.
        """
        env.history.flush_saved_transients()

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
        
        if not self.hover_highlighting_enabled:
            self.hover_highlighting_enabled = True
        
        _superclass.bareMotion(self, event)
        
    
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

        if isinstance(selobj, Chunk):
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

        
