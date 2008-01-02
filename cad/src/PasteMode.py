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

from utilities.Log import orangemsg, redmsg
from chem          import Atom
from elements      import Singlet
from pastables     import is_pastable
from depositMode   import depositMode

from PastePropertyManager import PastePropertyManager

_superclass = depositMode

class PasteMode(depositMode):
    """
    PasteMode allows depositing clipboard items into the 3D workspace. 
    Its property manager lists the 'pastable' clipboard items and also shows the 
    current selected item in its 'Preview' box. User can return to previous mode 
    by hitting 'Escape' key  or pressing 'Done' button in the Paste mode. 
    """
    commandName = 'PASTE' 
    msg_commandName = "Paste Mode" 
    default_mode_status_text = "Mode: Paste"
    featurename = "Paste"

    command_can_be_suspended = True #bruce 071011, GUESS ### REVIEW whether correct when entering Zoom/Pan/Rotate
    
    #Don't resume previous mode (buggy if set to True)
    
    command_should_resume_prevMode = False #bruce 071011, to be revised (replaces need for customized Done method)
    
    #See Command.anyCommand for details about the following flag
    command_has_its_own_gui = True

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
        self.updateCommandToolbar(bool_entering = True)
        
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
        
        change_connect(self.exitModeAction, 
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
        self.updateCommandToolbar(bool_entering = False)
    
    def update_gui(self):
        """
        """
        _superclass.update_gui(self)
        self.resubscribe_to_clipboard_members_changed()
            
    def keyPress(self, key):
        """
        Handles the key press event in this mode. 
        @param key: Pressed keyboard key
        @type  key: U{L{enum Qt.Key} 
                    <http://doc.trolltech.com/4.2/qt.html#Key-enum>}
        """
        # Exit Paste mode.
        if key == Qt.Key_Escape: 
            self.Done(exit_using_done_or_cancel_button = False)
            # REVIEW: should we also do assy.selectNone? The lack of 'else' here
            # means we will, in superclass method. [bruce comment 071012]
        depositMode.keyPress(self, key) 
    
    def _init_flyoutActions(self):
        """
        Defines the actions to be added in the flyout toolbar of the 
        Command Explorer
        """
        
        depositMode._init_flyoutActions(self)        
        
        self.exitModeAction.setText("Exit Paste")
       
    
    def getFlyoutActionList(self):
        """ 
        Returns a tuple that contains mode spcific actionlists in the 
        added in the flyout toolbar of the mode. 
        
        @return: A tuple that contains 3 lists: subControlAreaActionList, 
               commandActionLists and allActionsList
        @rtype: tuple
        @see: L{CommandToolbar._createFlyoutToolBar} which calls this. 
        """
        
        subControlAreaActionList = []
        commandActionLists   = []
        allActionsList  = []
                
        subControlAreaActionList.append(self.exitModeAction)   
        
        lst = []
        commandActionLists.append(lst)      
        allActionsList.append(self.exitModeAction)
        
        params = (subControlAreaActionList, commandActionLists, allActionsList)
        
        return params

    def deposit_from_MMKit(self, atom_or_pos):
        """
        Deposit the clipboard item being previewed into the 3D workspace
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
        Deposit the clipboard item being previewed into the 3D workspace
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
    
    def MMKit_clipboard_part(self): #bruce 060412; implem is somewhat of a guess, based on the code of self.deposit_from_MMKit
        """
        If the MMKit is currently set to a clipboard item, return that item's Part, else return None.
        """
        if not self.pastable:
            return None
        return self.pastable.part
    
    def transdepositPreviewedItem(self, singlet):
        """
        Trans-deposit the current object in the preview groupbox of the 
        property manager  on all singlets reachable through 
        any sequence of bonds to the singlet <singlet>.
        """
       
        # bruce 060412: fix bug 1677 (though this fix's modularity should be improved;
        #  perhaps it would be better to detect this error in deposit_from_MMKit).
        # See also other comments dated today about separate fixes of some parts of that bug.
        mmkit_part = self.MMKit_clipboard_part() # a Part or None
        if mmkit_part and self.o.assy.part is mmkit_part:
            env.history.message(redmsg("Can't transdeposit the MMKit's current"\
                                       " clipboard item onto itself."))
            return
        
        _superclass.transdepositPreviewedItem(self, singlet)
    
    def resubscribe_to_clipboard_members_changed(self):
        try:
            ###@@@@ need this to avoid UnboundLocalError: local variable 'shelf' referenced before assignment
            # but that got swallowed the first time we entered mode!
            # but i can't figure out why, so neverind for now [bruce 050121]
            shelf = self.o.assy.shelf
            shelf.call_after_next_changed_members # does this method exist?
        except AttributeError:
            # this is normal, until I commit new code to Utility and model tree! [bruce 050121]
            pass
        except:#k should not be needed, but I'm not positive, in light of bug-mystery above
            raise
        else:
            shelf = self.o.assy.shelf
            func = self.clipboard_members_changed
            shelf.call_after_next_changed_members(func, only_if_new = True)
                # note reversed word order in method names (feature, not bug)
        return
    
    def clipboard_members_changed(self, clipboard): #bruce 050121
        """
        we'll subscribe this method to changes to shelf.members, if possible
        """
        if self.isCurrentCommand():
            self.UpdateDashboard()
                #e ideally we'd set an inval flag and call that later, but when?
                # For now, see if it works this way. (After all, the old code called
                # UpdateDashboard directly from certain Node or Group methods.)
            ## call this from update_gui (called by UpdateDashboard) instead,
            ## so it will happen the first time we're setting it up, too:
            ## self.resubscribe_to_clipboard_members_changed()
            self.propMgr.update_clipboard_items() 
            # Fixes bugs 1569, 1570, 1572 and 1573. mark 060306.
            # Note and bugfix, bruce 060412: doing this now was also causing 
            # traceback bugs 1726, 1629,
            # and the traceback part of bug 1677, and some related 
            #(perhaps unreported) bugs.
            # The problem was that this is called during pasteBond's addmol 
            #(due to its addchild), before it's finished,
            # at a time when the .part structure is invalid (since the added 
            # mol's .part has not yet been set).
            # To fix bugs 1726, 1629 and mitigate bug 1677, I revised the 
            # interface to MMKit.update_clipboard_items
            # (in the manner which was originally recommented in 
            #call_after_next_changed_members's docstring) 
            # so that it only sets a flag and updates (triggering an MMKit 
            # repaint event), deferring all UI effects to
            # the next MMKit event.
        return
    
    # paste the pastable object where the cursor is (at pos)
    # warning: some of the following comment is obsolete (read all of it for the details)
    # ###@@@ should clean up this comment and code
    # - bruce 041206 fix bug 222 by recentering it now --
    # in fact, even better, if there's a hotspot, put that at pos.
    # - bruce 050121 fixing bug in feature of putting hotspot on water
    # rather than center. I was going to remove it, since Ninad disliked it
    # and I can see problematic aspects of it; but I saw that it had a bug
    # of picking the "first singlet" if there were several (and no hotspot),
    # so I'll fix that bug first, and also call fix_bad_hotspot to work
    # around invalid hotspots if those can occur. If the feature still seems
    # objectionable after this, it can be removed (or made a nondefault preference).
    # ... bruce 050124: that feature bothers me, decided to remove it completely.
    def pasteFree(self, pos):
        self.update_pastable()
        pastable = self.pastable
            # as of 050316 addmol can change self.pastable!
            # (if we're operating in the same clipboard item it's stored in,
            #  and if adding numol makes that item no longer pastable.)
            # And someday the copy operation itself might auto-addmol, for some reason;
            # so to be safe, save pastable here before we change current part at all.
        
        chunk, status = self.o.assy.paste(pastable, pos)
        return chunk, status
    
    
    
    
   
