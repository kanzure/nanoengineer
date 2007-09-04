# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PasteMode.py

PasteMode allows depositing clipboard items into the 3D workspace. 
Its property manager lists the'pastable' clipboard items and also shows the 
current selected item in its 'Preview' box. User can return to previous mode by 
hitting 'Escape' key or pressing 'Done' button in the Paste mode. 
        
@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:
ninad 2007-08-29: Created. 
"""
from PyQt4.Qt import QWidgetAction
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt

import env
import changes

from Utility       import geticon
from HistoryWidget import orangemsg
from chem          import Atom
from chem          import Singlet
from depositMode   import is_pastable
from depositMode   import depositMode

from PastePropertyManager import PastePropertyManager

class PasteMode(depositMode):
    """
    PasteMode allows depositing clipboard items into the 3D workspace. 
    Its property manager lists the 'pastable' clipboard items and also shows the 
    current selected item in its 'Preview' box. User can return to previous mode 
    by hitting 'Escape' key  or pressing 'Done' button in the Paste mode. 
    """
    modename = 'PASTE' 
    msg_modename = "Paste Mode" 
    default_mode_status_text = "Mode: Paste"
    
    def __init__(self, glpane):
        """
        Constructor for the class PasteMode. PasteMode allows depositing 
        clipboard items into the 3D workspace. Its property manager lists the
        'pastable' clipboard items and also shows the current selected item 
        in its 'Preview' box. User can return to previous mode by hitting 
        'Escape' key  or pressing 'Done' button in the Paste mode. 
        @param glpane: GLPane object 
        @type  glpane: L{GLPane} 
        """
        depositMode.__init__(self, glpane)
    
      
    def init_gui(self):
        """
        Do changes to the GUI while entering this mode. This includes opening 
        the property manager, updating the command explorer , connecting widget 
        slots etc. 
        
        Called once each time the mode is entered; should be called only by code 
        in modes.py
        
        @see: L{self.restore_gui}
        """
        self.enable_gui_actions(False)
        self.dont_update_gui = True
        if not self.propMgr:
            self.propMgr = PastePropertyManager(self)
            changes.keep_forever(self.propMgr)
            
        self.propMgr.show()     
        
        self.connect_or_disconnect_signals(True)
        self.updateCommandManager(bool_entering = True)
        
        #Following is required to make sure that the 
        #clipboard groupbox in paste mode is updated 
        #(This is done by calling depositeMode.update_gui method 
        #Not only that, but the above mentioned method also defines 
        #self.pastable_list which is needed to paste items! This needs a 
        #separate code clean up in depositmode.py -- Ninad 20070827
        self.dont_update_gui = False
        
                
    def connect_or_disconnect_signals(self, isConnect): 
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
        
        change_connect(self.exitPasteAction, 
                       SIGNAL("triggered()"), 
                       self.w.toolsDone)
        
        self.propMgr.connect_or_disconnect_signals(isConnect)
        
    
    def restore_gui(self):
        """
        Do changes to the GUI while exiting this mode. This includes closing 
        this mode's property manager, updating the command explorer , 
        disconnecting widget slots etc. 
        @see: L{self.init_gui}
        """
        self.propMgr.close()
        self.connect_or_disconnect_signals(False)
        self.enable_gui_actions(True)
        self.updateCommandManager(bool_entering = False)
            
    def Done(self, new_mode = None):
        """
        Decides what to do after exiting the mode. If mode is left by clicking 
        on B{Done} button it will enter the previous mode the user was in. 
        
        @example: User invokes Paste mode while in 'Move' mode, and then 
        hits 'Done'button in the Paste mode, NE1 leaves Paste mode and enters 
        Move mode again . 
        If instead of Done button, user clicks on a button that invokes a different 
        mode , it enters the mode user asked for. 
        
        @param new_mode: New mode user wants to enter. (A value 'None' means the 
                         user didn't ask for any specific mode , so NE1 should 
                         enter the previous  mode (before the paste mode) the
                         user was in.
        @type  new_mode: L{basicMode} or None
        """
        resuming = False
        if new_mode is None:
            try:
                new_mode = self.o.prevMode
                resuming = True
            except:
                pass
        return depositMode.Done(self, new_mode, resuming = resuming) 

    def keyPress(self, key):
        """
        Handles the key press event in this mode. 
        @param key: Pressed keyboard key
        @type  key: U{L{enum Qt.Key} 
                    <http://doc.trolltech.com/4.2/qt.html#Key-enum>}
        """
        #Exit Paste mode.
        if key == Qt.Key_Escape: 
            self.Done()
        depositMode.keyPress(self, key) 
    
    def _init_flyoutActions(self):
        """
        Defines the actions to be added in the flyout toolbar of the c
        command explorer
        """
        #Note: calling depositMode._init_flyoutActions may not be needed, 
        #defining it for safety (till depositMode is further cleaned up)
        depositMode._init_flyoutActions(self)
        
        self.exitPasteAction = QWidgetAction(self.w)
        self.exitPasteAction.setText("Exit Paste")
        self.exitPasteAction.setIcon(geticon('ui/actions/Toolbars/Smart/Exit'))
        self.exitPasteAction.setCheckable(True)
        self.exitPasteAction.setChecked(True)
    
    def getFlyoutActionList(self):
        """ 
        Returns a tuple that contains mode spcific actionlists in the 
        added in the flyout toolbar of the mode. 
        
        @return: A tuple that contains 3 lists: subControlAreaActionList, 
               commandActionLists and allActionsList
        @rtype: tuple
        @see: L{CommandManager._createFlyoutToolBar} which calls this. 
        """
        
        subControlAreaActionList = []
        commandActionLists   = []
        allActionsList  = []
                
        subControlAreaActionList.append(self.exitPasteAction)   
        
        lst = []
        commandActionLists.append(lst)      
        allActionsList.append(self.exitPasteAction)
        
        params = (subControlAreaActionList, commandActionLists, allActionsList)
        
        return params

    def deposit_from_MMKit(self, atom_or_pos):
        """
        Deposit the clipboard item being previed into the 3D workspace
        Calls L{self.deposit_from_Clipboard_page}
        @attention: This method needs renaming. L{depositMode} still uses it 
        so simply overriden here. B{NEEDS CLEANUP}.
        @see: L{self.deposit_from_Clipboard_page}
        """
        
        if self.o.modkeys is None: # no Shift or Ctrl modifier key.
            self.o.assy.unpickall_in_GLPane()
            
        deposited_stuff, status = \
                       self.deposit_from_Clipboard_page(atom_or_pos) 
        deposited_obj = 'Chunk'
        
        self.o.selatom = None 
                    
        if deposited_stuff:
            self.w.win_update()                
            status = self.ensure_visible( deposited_stuff, status) 
            env.history.message(status)
        else:
            env.history.message(orangemsg(status)) 
        
        return deposited_obj
            
            
    def deposit_from_Clipboard_page(self, atom_or_pos):
        """
        Deposit the clipboard item being previed into the 3D workspace
        Called in L{self.deposit_from_MMKit}
        @attention: This method needs renaming. L{depositMode} still uses this 
        so simply overriden here. B{NEEDS CLEANUP}.
        @see: L{self.deposit_from_MMKit}        
        """     
        self.update_pastable()
        
        if isinstance(atom_or_pos, Atom):
            a = atom_or_pos
            if a.element is Singlet:
                if self.pastable: # bond clipboard object to the singlet
                    # do the following before <a> (the singlet) is killed
                    a0 = a.singlet_neighbor() 
                    chunk, desc = self.pasteBond(a)
                    if chunk:
                        status = "replaced bondpoint on %r with %s" % (a0, desc) 
                    else:
                        status = desc                       
                else:
                    #Nothing selected from the Clipboard to paste, so do nothing
                    status = "nothing selected to paste" #k correct??
                    chunk = None 
        else:
            if self.pastable: 
                # deposit into empty space at the cursor position
                chunk, status = self.pasteFree(atom_or_pos)
            else:
                # Nothing selected from the Clipboard to paste, so do nothing
                status = "Nothing selected to paste" 
                chunk = None 
      
        return chunk, status
    
    def update_pastable(self):
        """
        Update self.pastable based on current selected pastable 
        in the clipboard
        """
        members = self.o.assy.shelf.members[:]
        self.pastables_list = filter( is_pastable, members)
        
        try:
            cx = self.propMgr.clipboardGroupBox.currentRow()
            self.pastable = self.pastables_list[cx] 
        except: # various causes, mostly not errors
            self.pastable = None        
        return 
    
   