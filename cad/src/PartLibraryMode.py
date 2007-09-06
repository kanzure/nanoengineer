#Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
PartLibraryMode.py 

Class PartLibraryMode allows depositing parts from the partlib into the 3D 
workspace.Its property manager shows the current selected part in its 'Preview' 
box. The part can be deposited by doubleclicking on empty space in 3D workspace 
or if it has a hotspot, it can be deposited on a bondpoint of an existing model.  
User can return to previous mode by hitting  'Escape' key or pressing 'Done' 
button in the Part Library mode.

@author: Bruce, Huaicai, Mark, Ninad
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:
The Partlib existed as a tab in the MMKit of Build Atoms Mode. (MMKit has been 
deprecated since 2007-08-29.) Now it has its own temporary mode. 

ninad 2007-09-06: Created. Split out some methods originally in depositMode.py 
                  to this file. 

"""
import changes
import env

from HistoryWidget import orangemsg
from icon_utilities import geticon

from chem import Atom
from chem import Singlet

from PasteMode              import PasteMode
from PartLibPropertyManager import PartLibPropertyManager

class PartLibraryMode(PasteMode):
    """
    The PartLibraryMode allows depositing parts from the partlib into the 3D 
    workspace. Its property manager shows the current selected part in its 
    'Preview' box. The part can be deposited by doubleclicking on empty space 
    in 3D workspace or if it has a hotspot, it can be deposited on a bondpoint 
    of an existing model.  User can return to previous mode by hitting  'Escape' 
    key or pressing 'Done' button in this mode. 
    """
    modename = 'PARTLIB'
    msg_modename = "Part Library" 
    default_mode_status_text = "Part Library"
    
    def __init__(self, glpane):
        """
        Constructor for the class PartLibraryMode. This mode allows 
        depositing parts from the partlib into the 3D workspace. Its property 
        manager shows the current selected part in its 'Preview' box. The part 
        can be deposited by doubleclicking on empty space in 3D workspace or if
        it has a hotspot, it can be deposited on a bondpoint of an existing 
        model.  User can return to previous mode by hitting  'Escape' key  
        or pressing 'Done' button in the Part Library mode. 
        
        @param glpane: GLPane object 
        @type  glpane: L{GLPane} 
        
        @see: L{PasteMode} , L{depositMode}
        """
        PasteMode.__init__(self, glpane)
    
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
            self.propMgr = PartLibPropertyManager(self)
            changes.keep_forever(self.propMgr)
            
        self.propMgr.show()     
        
        self.connect_or_disconnect_signals(True)
        self.updateCommandManager(bool_entering = True)
        
        self.dont_update_gui = False
        
    def _init_flyoutActions(self):
        """
        Defines the actions to be added in the flyout toolbar of the 
        Command Explorer
        """
        PasteMode._init_flyoutActions(self)
        self.exitModeAction.setText("Exit Partlib")
            
    def deposit_from_MMKit(self, atom_or_pos):
        """
        Deposit the library part being previewed into the 3D workspace
        Calls L{self.deposit_from_Clipboard_page}
        
        @param atom_or_pos: If user clicks on a bondpoint in 3D workspace,
                            this is that bondpoint. NE1 will try to bond the 
                            part to this bondpoint, by Part's hotspot(if exists)
                            If user double clicks on empty space, this gives 
                            the coordinates at that point. This data is then 
                            used to deposit the item.
        @type atom_or_pos: Array (vector) of coordinates or L{Atom}
        
        @return: (deposited_stuff, status_msg_text) Object deposited in the 3 D 
                workspace. (Deposits the selected  part as a 'Group'. The status
                message text tells whether the Part got deposited.
        @rtype: (L{Group} , str)
        
        @attention: This method needs renaming. L{depositMode} still uses it 
        so simply overriden here. B{NEEDS CLEANUP}.
        @see: L{self.deposit_from_Library_page} 
        
        """
        deposited_stuff, status = self.deposit_from_Library_page(atom_or_pos)
        deposited_obj = 'Part'
        if deposited_stuff and self.pickit():
            for d in deposited_stuff[:]:
                d.pickatoms() 
                
        if deposited_stuff:
            self.w.win_update()                
            status = self.ensure_visible( deposited_stuff, status) 
            env.history.message(status)
        else:
            env.history.message(orangemsg(status)) 
        
        return deposited_obj
    
    def deposit_from_Library_page(self, atom_or_pos): 
        """
        Deposit a copy of the selected part from the Property Manager.
               
        @param atom_or_pos: If user clicks on a bondpoint in 3D workspace,
                            this is that bondpoint. NE1 will try to bond the 
                            part to this bondpoint, by Part's hotspot(if exists)
                            If user double clicks on empty space, this gives 
                            the coordinates at that point. This data is then 
                            used to deposit the item.
        @type atom_or_pos: Array (vector) of coordinates or L{Atom}
        
        @return: (deposited_stuff, status_msg_text) Object deposited in the 3 D 
                workspace. (Deposits the selected  part as a 'Group'. The status
                message text tells whether the Part got deposited.
        @rtype: (L{Group} , str)
        """
        #Needs cleanup. Copying old code from depositMode.py -- ninad 2007-09-06
        
        newPart, hotSpot = self.propMgr.getPastablePart()
        
        if not newPart: # Make sure a part is selected in the MMKit Library.
            # Whenever the MMKit is closed with the 'Library' page open,
            # MMKit.closeEvent() will change the current page to 'Atoms'.
            # This ensures that this condition never happens if the MMKit is 
            # closed.
            # Mark 051213.
           
            return False, "No library part has been selected to paste." 
        
        if isinstance(atom_or_pos, Atom):
            a = atom_or_pos
            if a.element is Singlet:
                if hotSpot : # bond the part to the singlet.
                    return self._depositLibraryPart(newPart, hotSpot, a)                 
                else: # part doesn't have hotspot.
                    #if newPart.has_singlets(): # need a method like this so we 
                    # can provide more descriptive msgs.
                    #    msg = "To bond this part, you must pick a hotspot by \
                    #           left-clicking on a bondpoint  of the library \
                    #           part in the Modeling Kit's 3D thumbview."
                    #else:
                    #    msg = "The library part cannot be bonded because it \
                    #           has no bondpoints."
                    
                    msg = "The library part cannot be bonded because either " \
                           "it has no bondpoints"\
                            " or its hotspot hasn't been specified"
                    
                    return False, msg # nothing deposited
            else: 
                # atom_or_pos was an atom, but wasn't a singlet.  Do nothing.
                return False, "internal error: can't deposit onto a real atom" \ 
                              " %r" % a
        
        else:
            # deposit into empty space at the cursor position
            #bruce 051227 note: looks like subr repeats these conds;
            #are they needed here?
            return self._depositLibraryPart(newPart, hotSpot, atom_or_pos) 
        
        assert 0, "notreached"
    
    