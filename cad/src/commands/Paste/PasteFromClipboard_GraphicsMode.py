# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 2008-08-04: Created by splitting PasteFromClipboard_Command class into command and 
GraphicsMode. 

TODO:
"""
from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode

import foundation.env as env
from utilities.Log import orangemsg, redmsg

_superclass = BuildAtoms_GraphicsMode
class PasteFromClipboard_GraphicsMode(BuildAtoms_GraphicsMode):
    
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
                       self.command.deposit_from_Clipboard_page(atom_or_pos) 
        deposited_obj = 'Chunk'

        self.o.selatom = None 

        if deposited_stuff:
            self.w.win_update()                
            status = self.ensure_visible( deposited_stuff, status) 
            env.history.message(status)
        else:
            env.history.message(orangemsg(status)) 

        return deposited_obj
    
    
    def transdepositPreviewedItem(self, singlet):
        """
        Trans-deposit the current object in the preview groupbox of the 
        property manager  on all singlets reachable through 
        any sequence of bonds to the singlet <singlet>.
        """

        # bruce 060412: fix bug 1677 (though this fix's modularity should be 
        # improved; perhaps it would be better to detect this error in 
        # deposit_from_MMKit).
        # See also other comments dated today about separate fixes of some 
        # parts of that bug.
        mmkit_part = self.command.MMKit_clipboard_part() # a Part or None
        if mmkit_part and self.o.assy.part is mmkit_part:
            env.history.message(redmsg("Can't transdeposit the MMKit's current"\
                                       " clipboard item onto itself."))
            return

        _superclass.transdepositPreviewedItem(self, singlet)


    

