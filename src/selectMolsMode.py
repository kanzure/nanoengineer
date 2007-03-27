# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
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

- Ninad 070216 split this out of selectMode.py (in Qt4 branch)
- Ninad 070327 split this out of selectMode.py (in Qt3  branch)
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
            
    def init_gui(self):
        selectMode.init_gui(self)
        self.w.toolsSelectMoleculesAction.setOn(1) # toggle on the "Select Chunks" tools icon
        self.w.selectMolDashboard.show()
            
    def restore_gui(self):
        self.w.selectMolDashboard.hide()
        
    def leftDouble(self, event):
        '''Switch to Move Chunks Mode.  This will go away in A8. mark 060303.
        '''
        # Current plans are to merge Select Chunks and Move Chunks modes in A8.
        self.o.setMode('MODIFY')
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
            self.o.setCursor(self.w.SelectMolsCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.SelectMolsAddCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.SelectMolsSubtractCursor)
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

    pass # end of class selectMolsMode

# ==
