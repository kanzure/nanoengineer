# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
"""
import foundation.env as env
from utilities.Log import orangemsg

from commands.Paste.PasteFromClipboard_GraphicsMode import PasteFromClipboard_GraphicsMode

class PartLibrary_GraphicsMode(PasteFromClipboard_GraphicsMode):
    
    def deposit_from_MMKit(self, atom_or_pos):
        """
        Deposit the library part being previewed into the 3D workspace
        Calls L{self.deposit_from_Library_page}

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

        @attention: This method needs renaming. L{BuildAtoms_Command} still uses it 
        so simply overriden here. B{NEEDS CLEANUP}.
        @see: L{self.deposit_from_Library_page} 

        """
        deposited_stuff, status = self.command.deposit_from_Library_page(atom_or_pos)
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