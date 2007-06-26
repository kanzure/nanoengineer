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



from modes import *
from HistoryWidget import orangemsg
from chunk import molecule
import env
from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice
from selectMode import *

class selectMolsMode(selectMode):
    "Select Chunks mode"
    modename = 'SELECTMOLS'
    default_mode_status_text = "Mode: Select Chunks"
    
    def Enter(self): 
        basicMode.Enter(self)
        self.o.assy.selectChunksWithSelAtoms_noupdate() # josh 10/7 to avoid race in assy init     
        self.hover_highlighting_enabled = True
                    
    def init_gui(self):
        selectMode.init_gui(self)
        #ninad 070929 Don't draw done cancel buttons in 'default mode' 
        #(which is proposed to be select chunks mode always in A9)
        self.w.toolsSelectMoleculesAction.setChecked(1) # toggle on the "Select Chunks" tools icon
        self.w.dashboardHolder.hide()
        #self.w.dashboardHolder.setWidget(self.w.selectMolDashboard)
        #self.w.selectMolDashboard.show()
    
    def restore_gui(self):
        self.w.toolsSelectMoleculesAction.setChecked(0) # toggle on the "Select Chunks" tools icon
        #self.w.selectMolDashboard.hide()
        
    def leftDouble(self, event):
        '''Switch to Build chunks mode'''
        #@@ninad070329  Till Alpha8, it used to Switch to Move Chunks Mode. 
        # for Alpha9, (pr pre Alpha9), it will enter Deposit mode 
        #this implementation might change in future.  We may decide to do nothing instead
        
        #@@@ninad 070329: Doubleclick in select mode changes to build mode but 
        #prints the following traceback : that needs to be fixed:
        #"exception in mode's mouseReleaseEvent handler (bug, ignored): exceptions.AttributeError: LMB_press_event
        #[GLPane.py:1515] [selectAtomsMode.py:721]"
        
        #### Current plans are to merge Select Chunks and Move Chunks modes in A8.
        ###self.o.setMode('MODIFY')
        
        #@@@ ninad20070510 - based on discussion with Mark, don't enter deposit
        #mode when cursor is on empty space. (Otherwise, i.e. when its over an 
        #object, enter deposit mode.        
        #Following needs to bechange after implementation of objects like 
        #points, lines etc , which don't need deposit mode. 
        
        if self.cursor_over_when_LMB_pressed != 'Empty Space':
            self.o.setMode('DEPOSIT')
        return
        
    def keyPress(self,key):
        '''keypress event handler for selectMolsMode.
        '''
        basicMode.keyPress(self, key)
                
    def keyRelease(self,key):
        '''keyrelease event handler for selectMolsMode.
        '''
            
        basicMode.keyRelease(self, key)
        
    def update_cursor_for_no_MB(self):
        '''Update the cursor for 'Select Chunks' mode (selectMolsMode).
        '''
        
        #print "selectMolsMode.update_cursor_for_no_MB(): button=",self.o.button
        
        if self.o.modkeys is None:
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
        '''Real atom <a> was clicked, so select, unselect or delete ITS CHUNK  based on the current modkey.
        - If no modkey is pressed, clear the selection and pick atom's chunk <m>.
        - If Shift is pressed, pick <m>, adding it to the current selection.
        - If Ctrl is pressed,  unpick <m>, removing it from the current selection.
        - If Shift+Control (Delete) is pressed, delete atom <m>.
        '''
        
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
                    env.history.message(orangemsg("Can't deselect atom %r due to selection filter. Hit Escape to clear the filter." % a))
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
        '''Left down  on a Bond <b> , so select or unselect its chunk or delete the bond <b> 
        based on the current modkey.
        - If no modkey is pressed, clear the selection and pick <b>'s chunk(s).
        - If Shift is pressed, pick <b>'s chunk(s) , adding them to the current selection.
        - If Ctrl is pressed,  unpick <b>'s chunk(s), removing them from the current selection.
        - If Shift+Control (Delete) is pressed, delete chunk(s) associated with this bond <b>.
        <event> is a LMB release event.
        '''
        
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

    def leftShiftDown(self, event):
        '''Event handler for Shift+LMB press.'''
        self.leftDown(event)
    
    def leftCntlDown(self, event):
        '''Event handler for Control+LMB press.'''
        self.leftDown(event)
    
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

        if isinstance(obj, Atom) and obj.is_singlet(): # Cursor over a singlet
            self.singletLeftDown(obj, event)
                # no win_update() needed. It's the responsibility of singletLeftDown to do it if needed.
            return
            
        elif isinstance(obj, Atom) and not obj.is_singlet(): # Cursor over a real atom
            self.atomLeftDown(obj, event)
        
        elif isinstance(obj, Bond) and not obj.is_open_bond(): # Cursor over a bond.
            self.bondLeftDown(obj, event)
        
        elif isinstance(obj, Jig): # Cursor over a jig.
            self.jigLeftDown(obj, event)
        
        else: # Cursor is over something else other than an atom, singlet or bond. 
            # The program never executes lines in this else statement since
            # get_obj_under_cursor() only returns atoms, singlets or bonds.
            # [perhaps no longer true, if it ever was -- bruce 060725]
            pass

        self.w.win_update() #k (is this always desirable? note, a few cases above return early just so they can skip it.)
        return # from selectMolsMode.leftDown

    
    def leftDrag(self, event):
        """ Overrides leftdrag method of select Mode. While left dragging
        if any movable object is selected, it enters 'move mode' called 'pseudo 
        move mode' for convenience. After releasing left mouse button 
        it returns to select chunks mode. The only observable effect for
        the end user is the pressed Move components action icon. 
        (which is intentional) """
        
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
                self.continue_selection_curve(event)             
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
            bool_goBackToMode = True
            self.o.setMode('MODIFY')  
            #@@ ninad 070302 Close the property manager. 
            #This works ok even for huge objects (i.e. there is no
            #'flashing' effect because property manager in move mode is initialized
            #in init_gui method instead of mode.enter
            # I wanted to set a flag here and use it in move mode's init_gui. 
            #but it didn't work. So trying this alternative. 
            self.o.mode.closePropertyManager()
            self.o.mode.setGoBackToMode(True, 'SELECTMOLS')             
            self.o.mode.leftDown(event)
        else:
            self.continue_selection_curve(event)      
    
    def leftCntlDrag(self, event):
        """ Overrides leftdrag method of select Mode. While left dragging
        if any movable object is selected, it enters 'move mode' called 'pseudo 
        move mode' for convenience. After releasing left mouse button 
        it returns to select chunks mode. The only observable effect for
        the end user is the pressed Move components action icon. 
        (which is intentional) """
        isCursorOnAnObject = self.o.selobj
        
        if self.o.assy.getSelectedMovables():
            bool_goBackToMode = True
            self.o.setMode('MODIFY')  
            #@@ ninad 070302 Close the property manager. 
            #This works ok even for huge objects (i.e. there is no
            #'flashing' effect because property manager in move mode is initialized
            #in init_gui method instead of mode.enter
            # I wanted to set a flag here and use it in move mode's init_gui. 
            #but it didn't work. So trying this alternative. 
            self.o.mode.closePropertyManager()
            self.o.mode.setGoBackToMode(True, 'SELECTMOLS')             
            self.o.mode.leftCntlDown(event)
        else:
            self.continue_selection_curve(event)  
        
            
    def leftUp(self, event):
        '''Event handler for all LMB release events.'''
        env.history.flush_saved_transients() # flush any transient message it saved up
         
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
            
        if isinstance(obj, Atom):
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
        
        return # from selectMolsMode.leftUp
            
    def bareMotion(self, event): 
        """SELECT CHUNKS MODE called for motion with no button down
        [should not be called otherwise -- call update_selatom or update_selobj directly instead]
        """
        
        if self.mouse_exceeded_distance(event, 1):
            return
        self.update_selobj(event) #ninad 20070214 to permit chunk highlighting
        return
    
    def selobj_highlight_color(self, selobj): #bruce 050612 added this to mode API
        """[mode API method] 
        If we'd like this selobj to be highlighted on mouseover
        (whenever it's stored in glpane.selobj), return the desired highlight color.
        If we'd prefer it not be highlighted (though it will still be stored
        in glpane.selobj and prevent any other objs it obscures from being stored there
        or highlighted), return None. (Warning: exceptions are ignored and cause the
        default highlight color to be used. #e should clean that up sometime)
        """
        #Ninad 070214 copied the  method of selectAtomsMode 
        #to this class(selectMolsMode) while working on Chunk Highlighting
        #code in select chunks mode. 
        #It needs further refinement. May be we should move this to selectMode class. 
        
                
        if not self.hover_highlighting_enabled:
            return None

        #####@@@@@ if self.drag_handler, we should probably let it override all this
        # (so it can highlight just the things it might let you DND its selobj to, for example),
        # even for Atom/Bondpoint/Bond/Jig, maybe even when not self.hover_highlighting_enabled. [bruce 060726 comment]
        
        if isinstance(selobj, Atom):
            return yellow
        elif isinstance(selobj, Bond):
            return yellow 
        elif isinstance(selobj, Jig): #bruce 050729 bugfix (for some bugs caused by Huaicai's jig-selection code)
            if not self.o.jigSelectionEnabled: #mark 060312.
                # jigSelectionEnabled set from GLPane context menu.
                return None
            if self.o.modkeys == 'Shift+Control': 
                return darkred
            else:
                return env.prefs[bondHighlightColor_prefs_key]
        else:
            if 1:
                # Let the object tell us its highlight color, if it's not one we have a special case for here
                # (and if no drag_handler told us instead (nim, above)).
                # Note: this color will be passed to selobj.draw_in_abs_coords when selobj is asked
                # to draw its highlight; but even if that method plans to ignore that color arg,
                # this method better return a real color (or at least not None or (maybe) anything false),
                # otherwise GLPane will decide it's not a valid selobj and not highlight it at all.
                # (And in that case, will a context menu work on it (if it wasn't nim for that kind of selobj)?
                #  I don't know.)
                # [bruce 060722 new feature; revised comment 060726]
                method = getattr(selobj, 'highlight_color_for_modkeys', None)
                if method:
                    clr = method(self.o.modkeys)
                    return method(self.o.modkeys)
                        # Note: this API might be revised; it only really makes sense if the mode created the selobj to fit its
                        # current way of using modkeys, perhaps including not only its code but its active-tool state.
                        #e Does it make sense to pass the drag_handler, even if we let it override this?
                        # Yes, since it might like to ask the object (so it needs an API to do that), or let the obj decide,
                        # based on properties of the drag_handler.
                        #e Does it make sense to pass the obj being dragged without a drag_handler?
                        # Yes, even more so. Not sure if that's always called the same thing, depending on its type.
                        # If not, we can probably just kluge it by self.this or self.that, if they all get reset each drag. ###@@@
            print "unexpected selobj class in mode.selobj_highlight_color:", selobj
            return black ## bruce 060726 blue -> black so the fact that it's an error is more obvious
        pass # end of selobj_highlight_color   
                
    def update_selobj(self, event): ###WARNING: this duplicates the same method in selectAtomsMode but has not been co-maintained. [bruce 070618 comment]
        """Keep glpane.selobj up-to-date, as object under mouse, or None
        (whether or not that kind of object should get highlighted).
           Return True if selobj is already updated when we return, or False if that will not happen until the next paintGL.
           Warning: if selobj needs to change, this routine does not change it (or even reset it to None);
        it only sets flags and does gl_update, so that paintGL will run soon and will update it properly,
        and will highlight it if desired ###@@@ how is that controlled? probably by some statevar in self, passed to gl flag?
           This means that old code which depends on selatom being up-to-date must do one of two things:
        - compute selatom from selobj, whenever it's needed;
        - hope that paintGL runs some callback in this mode when it changes selobj, which updates selatom
          and outputs whatever statusbar message is appropriate. ####@@@@ doit... this is not yet fully ok.
          
          For SELECT CHUNKS MODE 
        """
        
        #Ninad 070214 copied the  method of selectAtomsMode 
        #to this class(selectMolsMode) while working on Chunk Highlighting
        #code in select chunks mode. Also modified it to remove code releated to  'water'
        #in deposit mode. 
        
        #It needs further refinement. May be we should move this to selectMode class. 
        
        
        #e see also the options on update_selatom;
        # probably update_selatom should still exist, and call this, and provide those opts, and set selatom from this,
        # but see the docstring issues before doing this ####@@@@

        # bruce 050610 new comments for intended code (#e clean them up and make a docstring):
        # selobj might be None, or might be in stencil buffer.
        # Use that and depthbuffer to decide whether redraw is needed to look for a new one.
        # Details: if selobj none, depth far or under water is fine, any other depth means look for new selobj (set flag, glupdate).
        # if selobj not none, stencil 1 means still same selobj (if no stencil buffer, have to guess it's 0);
        # else depth far or underwater means it's now None (repaint needed to make that look right, but no hittest needed)
        # and another depth means set flag and do repaint (might get same selobj (if no stencil buffer or things moved)
        #   or none or new one, won't know yet, doesn't matter a lot, not sure we even need to reset it to none here first).
        # Only goals of this method: maybe glupdate, if so maybe first set flag, and maybe set selobj none, but prob not
        # (repaint sets new selobj, maybe highlights it).
        # [some code copied from modifyMode]
        
        if debug_update_selobj_calls:
            print_compact_stack("debug_update_selobj_calls: ")
        
        glpane = self.o
        
        # If animating or ZPRing (zooming/panning/rotating) with the MMB, do not hover highlight anything. 
        # For more info about <is_animating>, see GLPane.animateToView(). mark 060404.
        if self.o.is_animating or self.o.button == "MMB":
            return
        
        wX = event.pos().x()
        wY = glpane.height - event.pos().y()
        selobj = orig_selobj = glpane.selobj
        if selobj is not None:
            if glpane.stencilbits >= 1:
                # optimization: fast way to tell if we're still over the same object as last time
                # (warning: for now glpane.stencilbits is 1 even when true number of bits is higher; easy to fix when needed)
                stencilbit = glReadPixelsi(wX, wY, 1, 1, GL_STENCIL_INDEX)[0][0]
                    # Note: if there's no stencil buffer in this OpenGL context, this gets an invalid operation exception from OpenGL.
                    # And by default there isn't one -- it has to be asked for when the QGLWidget is initialized.
                # stencilbit tells whether the highlighted drawing of selobj got drawn at this point on the screen
                # (due to both the shape of selobj, and to the depth buffer contents when it was drawn)
            else:
                stencilbit = 0 # the correct value is "don't know"; 0 is conservative
                #e might collapse this code if stencilbit not used below;
                #e and/or might need to record whether we used this conservative value
            if stencilbit:
                return True # same selobj, no need for gl_update to change highlighting
        # We get here for no prior selobj,
        # or for a prior selobj that the mouse has moved off of the visible/highlighted part of,
        # or for a prior selobj when we don't know whether the mouse moved off of it or not
        # (due to lack of a stencil buffer, i.e. very limited graphics card or OpenGL implementation).
        #
        # We have to figure out selobj afresh from the mouse position (using depth buffer and/or GL_SELECT hit-testing).
        # It might be the same as before (if we have no stencil buffer, or if it got bigger or moved)
        # so don't set it to None for now (unless we're sure from the depth that it should end up being None) --
        # let it remain the old value until the new one (perhaps None) is computed during paintGL.
        #
        # Specifically, if this method can figure out the correct new setting of glpane.selobj (None or some object),
        # it should set it (###@@@ or call a setter? neither -- let end-code do this) and set new_selobj to that
        # (so code at method-end can repaint if new_selobj is different than orig_selobj);
        # and if not, it should set new_selobj to instructions for paintGL to find selobj (also handled by code at method-end).
        ###@@@ if we set it to None, and it wasn't before, we still have to redraw!
        ###@@@ ###e will need to fix bugs by resetting selobj when it moves or view changes etc (find same code as for selatom).
            
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)[0][0]
            # depth (range 0 to 1, 0 is nearest) of most recent drawing at this mouse position
        new_selobj_unknown = False
            # following code should either set this True or set new_selobj to correct new value (None or an object)
        if wZ >= GL_FAR_Z: ## Huaicai 8/17/05 for blue sky plane z value
            # far depth (this happens when no object is touched)
            new_selobj = None
        else:            
            new_selobj_unknown = True
                
        if new_selobj_unknown:
            # Only the next paintGL call can figure out the selobj (in general),
            # so set glpane.glselect_wanted to the command to do that and the necessary info for doing it.
            # Note: it might have been set before and not yet used;
            # if so, it's good to discard that old info, as we do.
            glpane.glselect_wanted = (wX, wY, wZ) # mouse pos, depth
                ###e and soon, instructions about whether to highlight selobj based on its type (as predicate on selobj)
                ###e should also include current count of number of times
                # glupdate was ever called because model looks different,
                # and inval these instrs if that happens again before they are used
                # (since in that case wZ is no longer correct)
            # don't change glpane.selobj (since it might not even need to change) (ok??#k) -- the next paintGL will do that --
            # UNLESS the current mode wants us to change it [new feature, bruce 061218, perhaps a temporary kluge, but helps
            #  avoid a logic bug in this code, experienced often in testmode due to its slow redraw]
            if hasattr(glpane.mode, 'UNKNOWN_SELOBJ'):
                glpane.selobj = getattr(glpane.mode, 'UNKNOWN_SELOBJ')
            glpane.gl_update_for_glselect()
        else:
            # it's known (to be a specific object or None)
            if new_selobj is not orig_selobj:                
                # this is the right test even if one or both of those is None.
                # (Note that we never figure out a specific new_selobj, above,
                #  except when it's None, but that might change someday
                #  and this code can already handle that.)
                glpane.set_selobj( new_selobj, "chunks mode")
                    #e use setter func, if anything needs to observe changes to this?
                    # or let paintGL notice the change (whether it or elseone does it) and report that?
                    # Probably it's better for paintGL to report it, so it doesn't happen too often or too soon!
                    # And in the glselect_wanted case, that's the only choice, so we needed code for that anyway.
                    # Conclusion: no external setter func is required; maybe glpane has an internal one and tracks prior value.
                glpane.gl_update_highlight() # this might or might not highlight that selobj ###e need to tell it how to decide??
        #####@@@@@ we'll need to do this in a callback when selobj is set:
        ## self.update_selatom(event, msg_about_click = True)
        return not new_selobj_unknown # from update_selobj
    
    def get_obj_under_cursor(self, event): 
        '''Return the object under the cursor.  Returns atoms, bonds, jigs.
        '''
        ### WARNING: this is slow, and redundant with highlighting -- only call it on mousedown or mouseup, never in move or drag.
        # [true as of 060726 and before; bruce 060726 comment]
        # It may be that it's not called when highlighting is on, and it has no excuse to be, but I suspect it is anyway.
        # [bruce 060726 comment]
        
        if self.hover_highlighting_enabled:
            
            #self.update_selatom(event) #bruce 041130 in case no update_selatom happened yet
            # update_selatom() updates self.o.selatom and self.o.selobj.
            # self.o.selatom is either a real atom or a singlet [or None].
            # self.o.selobj can be a bond, and is used in leftUp() to determine if a bond was selected.
            
            # Warning: if there was no GLPane repaint event (i.e. paintGL call) since the last bareMotion,
            # update_selatom can't make selobj/selatom correct until the next time paintGL runs.
            # Therefore, the present value might be out of date -- but it does correspond to whatever
            # highlighting is on the screen, so whatever it is should not be a surprise to the user,
            # so this is not too bad -- the user should wait for the highlighting to catch up to the mouse
            # motion before pressing the mouse. [bruce 050705 comment] [might be out of context, copied from other code]
        
            obj = self.o.selatom # a "highlighted" atom or singlet
            
            
            if obj is None and self.o.selobj:
                obj = self.o.selobj # a "highlighted" bond
                    # [or anything else, except Atom or Jig -- i.e. a general/drag_handler/Drawable seolobj [bruce 060728]]
 
                if env.debug():
                    # I want to know if either of these things occur -- I doubt they do, but I'm not sure about Jigs [bruce 060728]
                    if isinstance(obj, Atom):
                        print "debug fyi: likely bug: selobj is Atom but not in selatom: %r" % (obj,)
                    elif isinstance(obj, Jig):
                        print "debug fyi: selobj is a Jig in get_obj_under_cursor (comment is wrong), for %r" % (obj,)
                        # I suspect some jigs can occur here
                        # (and if not, we should put them here -- I know of no excuse for jig highlighting
                        #  to work differently than for anything else) [bruce 060721]
                    pass
            
            if obj is None: # a "highlighted" jig [i think this comment is misleading, it might really be nothing -- bruce 060726]
                obj = self.get_jig_under_cursor(event)
                if 0 and env.debug():
                    print "debug fyi: get_jig_under_cursor returns %r" % (obj,) # [bruce 060721] 
            pass
            
        else: # No hover highlighting
            self.water_enabled = None #@ should be removed completely
            obj = self.o.assy.findAtomUnderMouse(event, self.water_enabled, singlet_ok = True)
            # Note: findAtomUnderMouse() only returns atoms and singlets, not bonds or jigs.
            # This means that bonds can never be selected when highlighting is turned off.
            # [What about jigs? bruce question 060721]
        return obj
       
    
    def update_selatom(self, event, singOnly = False, msg_about_click = False, resort_to_prior = True):
        ### WARNING: this method is defined in two places, with mostly duplicated code. [bruce 070626 comment]
        '''Keep selatom up-to-date, as atom under mouse based on <event>; 
        When <singOnly> is True, only keep singlets up-to-date. [not sure what that phrase means -- bruce 060726]
        When <msg_about_click> is True, print a message on the statusbar about the LMB press.
        <resort_to_prior> is disabled. [that statement seems incorrect -- bruce 060726]
        ###@@@ correctness after rewrite not yet proven, due to delay until paintGL
        '''
        #bruce 050124 split this out of bareMotion so options can vary
        #bruce 050610 rewrote this
        #bruce 060726 comment: looks to me like docstring is wrong about resort_to_prior, and some comments are obs.
        # Note: it never changes glpane.selobj.
        glpane = self.o
        if event is None:
            # event (and thus its x,y position) is not known [bruce 050612 added this possibility]
            known = False
        else:
            known = self.update_selobj(event) # this might do gl_update (but the paintGL triggered by that only happens later!),
                # and (when it does) might not know the correct obj...
                # so it returns True iff it did know the correct obj (or None) to store into glpane.selobj, False if not.
        if known not in [False,True]:
            qt4info(known)
            known = not (not known)   # convert to boolean
        # If not known, use None or use the prior one? This is up to the caller
        # since the best policy varies. Default is resort_to_prior = True since some callers need this
        # and I did not yet scan them all and fix them. ####@@@@ do that
        
        selobj = glpane.selobj
        ## print "known %r, selobj %r" % (known, selobj) 
            
        if not known:
            if resort_to_prior: 
                pass # stored one is what this says to use, and is what we'll use
                ## print "resort_to_prior using",glpane.selobj
                    # [this is rare, I guess since paintGL usually has time to run after bareMotion before clicks]
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
        if msg_about_click: # [always do this, since many things can change what it should say]
            # come up with a status bar message about what we would paste now.
            # [bruce 050124 new feature, to mitigate current lack of model tree highlighting of pastable]
            msg = self.describe_leftDown_action( glpane.selatom)
            env.history.statusbar_msg( msg)
        if glpane.selatom is not oldselatom:
            # update display (probably redundant with side effect of update_selobj; ok if it is, and I'm not sure it always is #k)
            glpane.gl_update_highlight() # draws selatom too, since its chunk is not hidden [comment might be obs, as of 050610]
        
        return # from update_selatom
    
            
    pass # end of class selectMolsMode

# ==
